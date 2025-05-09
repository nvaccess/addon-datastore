#!/usr/bin/env python

# Copyright (C) 2022-2025 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from time import gmtime, mktime
import dataclasses
import json
import argparse
import os
import sys
import zipfile

from typing import (
	Dict,
	Optional,
	cast,
)

sys.path.append(os.path.dirname(__file__))  # To allow this module to be run as a script by runcreatejson.bat
# E402 module level import not at top of file
from addonManifest import AddonManifest  # noqa:E402
from manifestLoader import getAddonManifest, getAddonManifestLocalizations  # noqa:E402
from majorMinorPatch import MajorMinorPatch  # noqa:E402
import sha256  # noqa:E402
del sys.path[-1]


def getSha256(addonPath: str) -> str:
	with open(addonPath, "rb") as f:
		sha256Addon = sha256.sha256_checksum(f)
	return sha256Addon


def getCurrentTime() -> int:
	return int(mktime(gmtime()) * 1000)  # Milliseconds


def generateJsonFile(
		manifest: AddonManifest,
		addonPath: str,
		parentDir: str,
		channel: str,
		publisher: str,
		sourceUrl: str,
		url: str,
		licenseName: str,
		licenseUrl: Optional[str],
) -> None:
	data = _createDictMatchingJsonSchema(
		manifest=manifest,
		sha=getSha256(addonPath),
		channel=channel,
		publisher=publisher,
		sourceUrl=sourceUrl,
		url=url,
		licenseName=licenseName,
		licenseUrl=licenseUrl,
	)

	filePath = buildOutputFilePath(data, parentDir)

	with open(filePath, "wt", encoding="utf-8") as f:
		json.dump(data, f, indent="\t", ensure_ascii=False)
	print(f"Wrote json file: {filePath}")


def buildOutputFilePath(data, parentDir) -> os.PathLike:
	addonDir = os.path.join(parentDir, data["addonId"])
	versionNumber = MajorMinorPatch(**data["addonVersionNumber"])
	canonicalVersionString = ".".join(
		(str(i) for i in dataclasses.astuple(versionNumber))
	)
	if not os.path.isdir(addonDir):
		os.makedirs(addonDir)
	filePath = os.path.join(addonDir, f'{canonicalVersionString}.json')
	return cast(os.PathLike, filePath)


def _createDictMatchingJsonSchema(
		manifest: AddonManifest,
		sha: str,
		channel: str,
		publisher: str,
		sourceUrl: str,
		url: str,
		licenseName: str,
		licenseUrl: Optional[str],
) -> Dict[str, str]:
	"""Refer to _validate/addonVersion_schema.json"""
	try:
		addonVersionNumber = MajorMinorPatch.getFromStr(manifest["version"])
	except ValueError as e:
		raise ValueError(f"Manifest version invalid {addonVersionNumber}") from e

	try:
		addonData = {
			"addonId": manifest["name"],
			"displayName": manifest["summary"],
			"URL": url,
			"description": manifest["description"],
			"sha256": sha,
			"addonVersionName": manifest["version"],
			"addonVersionNumber": dataclasses.asdict(addonVersionNumber),
			"minNVDAVersion": dataclasses.asdict(
				MajorMinorPatch(*manifest["minimumNVDAVersion"])
			),
			"lastTestedVersion": dataclasses.asdict(
				MajorMinorPatch(*manifest["lastTestedNVDAVersion"])
			),
			"channel": channel,
			"publisher": publisher,
			"sourceURL": sourceUrl,
			"license": licenseName,
		}
	except KeyError as e:
		raise KeyError(f"Manifest missing required key '{e.args[0]}'.") from e

	# Add optional fields
	homepage = manifest.get("url")
	if homepage and homepage != 'None':
		# The config default is None
		# which is parsed by configobj as a string not a NoneType
		addonData["homepage"] = homepage
	if licenseUrl:
		addonData["licenseURL"] = licenseUrl
	addonData["submissionTime"] = getCurrentTime()

	addonData["translations"] = []
	for langCode, manifest in getAddonManifestLocalizations(manifest):
		try:
			addonData["translations"].append(
				{
					"language": langCode,
					"displayName": manifest["summary"],
					"description": manifest["description"],
				}
			)
		except KeyError as e:
			raise KeyError(f"Translation for {langCode} missing required key '{e.args[0]}'.") from e

	return addonData


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-f",
		dest="file",
		help="The add-on (nvda-addon) file to create json from manifest.",
		required=True,
	)
	parser.add_argument(
		"--dir",
		dest="parentDir",
		help="Parent directory to store the json file.",
		required=True,
	)
	parser.add_argument(
		"--output",
		dest="errorOutputFile",
		help="The text file to output errors from the validation, if any.",
		default=None,
	)
	parser.add_argument(
		"--channel",
		dest="channel",
		help="The channel for this release.",
		required=True,
	)
	parser.add_argument(
		"--publisher",
		dest="publisher",
		help="The publisher for this submission.",
		required=True,
	)
	parser.add_argument(
		"--sourceUrl",
		dest="sourceUrl",
		help="The URL to review source code.",
		required=True,
	)
	parser.add_argument(
		"--url",
		dest="url",
		help="URL to download the add-on.",
		required=True,
	)
	parser.add_argument(
		"--licName",
		dest="licenseName",
		help="Name of the license used with the add-on. E.G. 'GPL v2'",
		required=True,
	)
	parser.add_argument(
		"--licUrl",
		dest="licenseUrl",
		help="URL to read the license in full. E.G. 'https://www.gnu.org/licenses/gpl-2.0.html'",
		default=None,
		required=False,
	)
	args = parser.parse_args()
	errorFilePath: Optional[str] = args.errorOutputFile

	try:
		manifest = getAddonManifest(args.file)
	except zipfile.BadZipFile as e:
		if errorFilePath:
			with open(errorFilePath, "w") as errorFile:
				errorFile.write(f"Validation Errors:\n{e}")
		raise

	if manifest.errors:
		if errorFilePath:
			with open(errorFilePath, "w") as errorFile:
				errorFile.write(f"Validation Errors:\n{manifest.errors}")
		raise ValueError(f"Invalid manifest file: {manifest.errors}")

	try:
		generateJsonFile(
			manifest=manifest,
			addonPath=args.file,
			parentDir=args.parentDir,
			channel=args.channel,
			publisher=args.publisher,
			sourceUrl=args.sourceUrl,
			url=args.url,
			licenseName=args.licenseName,
			# Convert the case --licUrl='' to --licUrl=None
			licenseUrl=args.licenseUrl if args.licenseUrl else None,
		)
	except Exception as e:
		if manifest.errors:
			if errorFilePath:
				with open(errorFilePath, "w") as errorFile:
					errorFile.write(f"Validation Errors:\n{manifest.errors}")
			raise ValueError(f"Invalid manifest file: {manifest.errors}")
		else:
			if errorFilePath:
				with open(errorFilePath, "w") as errorFile:
					errorFile.write(f"Validation Errors:\n{e}")
			raise


if __name__ == '__main__':
	main()
