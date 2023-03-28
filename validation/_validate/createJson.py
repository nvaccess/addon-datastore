#!/usr/bin/env python

# Copyright (C) 2022-2023 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html
import dataclasses
import json
import argparse
import os
import sys

import typing

sys.path.append(os.path.dirname(__file__))  # To allow this module to be run as a script by runcreatejson.bat
# E402 module level import not at top of file
from addonManifest import AddonManifest  # noqa:E402
from manifestLoader import getAddonManifest  # noqa:E402
from majorMinorPatch import MajorMinorPatch  # noqa:E402
import sha256  # noqa:E402
del sys.path[-1]


def getSha256(addonPath: str) -> str:
	with open(addonPath, "rb") as f:
		sha256Addon = sha256.sha256_checksum(f)
	return sha256Addon


def generateJsonFile(
		addonPath: str,
		parentDir: str,
		channel: str,
		publisher: str,
		sourceUrl: str,
		url: str,
		licenseName: str,
		licenseUrl: typing.Optional[str],
) -> None:
	manifest = getAddonManifest(addonPath)
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

	with open(filePath, "wt") as f:
		json.dump(data, f, indent="\t")
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
	return typing.cast(os.PathLike, filePath)


def _createDictMatchingJsonSchema(
		manifest: AddonManifest,
		sha: str,
		channel: str,
		publisher: str,
		sourceUrl: str,
		url: str,
		licenseName: str,
		licenseUrl: typing.Optional[str],
) -> typing.Dict[str, str]:
	return {  # see _validate/addonVersion_schema.json
		"addonId": manifest["name"],
		"displayName": manifest["summary"],
		"URL": url,
		"description": manifest["description"],
		"sha256": sha,
		# Optional field
		"homepage": manifest.get("url"),
		"addonVersionName": manifest["version"],
		"addonVersionNumber": dataclasses.asdict(
			MajorMinorPatch.getFromStr(manifest["version"])
		),
		"minNVDAVersion": dataclasses.asdict(
			MajorMinorPatch.getFromStr(manifest["minimumNVDAVersion"])
		),
		"lastTestedVersion": dataclasses.asdict(
			MajorMinorPatch.getFromStr(manifest["lastTestedNVDAVersion"])
		),
		"channel": channel,
		"publisher": publisher,
		"sourceURL": sourceUrl,
		"license": licenseName,
		"licenseURL": licenseUrl,
	}


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
	generateJsonFile(
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


if __name__ == '__main__':
	main()
