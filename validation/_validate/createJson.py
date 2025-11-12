# Copyright (C) 2022-2025 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from time import gmtime, mktime
import dataclasses
import json
import argparse
import os
from typing import cast
import zipfile

from .addonManifest import AddonManifest, ApiVersionT
from .manifestLoader import getAddonManifest, getAddonManifestLocalizations
from .majorMinorPatch import MajorMinorPatch
from .sha256 import sha256_checksum
from .validate import parseConfigValue


@dataclasses.dataclass
class AddonData:
	addonId: str
	displayName: str
	URL: str
	description: str
	sha256: str
	addonVersionName: str
	addonVersionNumber: dict[str, int]
	minNVDAVersion: dict[str, int]
	lastTestedVersion: dict[str, int]
	channel: str
	publisher: str
	sourceURL: str
	license: str
	homepage: str | None
	changelog: str | None
	licenseURL: str | None
	submissionTime: int
	translations: list[dict[str, str]]


def getSha256(addonPath: str) -> str:
	with open(addonPath, "rb") as f:
		sha256Addon = sha256_checksum(f)
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
	licenseUrl: str | None,
) -> None:
	data = _createDataclassMatchingJsonSchema(
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
		json.dump(
			dataclasses.asdict(
				data,
				# The JSON schema does not permit null values, but does contain optional keys.
				# We have already ensured that all required keys are present in the metadata,
				# So we can safely delete all keys whose value is None as optional.
				dict_factory=lambda args: dict(filter(lambda item: item[1] is not None, args)),
			),
			f,
			indent="\t",
			ensure_ascii=False,
		)
	print(f"Wrote json file: {filePath}")


def buildOutputFilePath(data: AddonData, parentDir: str) -> os.PathLike[str]:
	addonDir = os.path.join(parentDir, data.addonId)
	versionNumber = MajorMinorPatch(**data.addonVersionNumber)
	canonicalVersionString = ".".join((str(i) for i in dataclasses.astuple(versionNumber)))
	if not os.path.isdir(addonDir):
		os.makedirs(addonDir)
	filePath = os.path.join(addonDir, f"{canonicalVersionString}.json")
	return cast(os.PathLike[str], filePath)


def _createDataclassMatchingJsonSchema(
	manifest: AddonManifest,
	sha: str,
	channel: str,
	publisher: str,
	sourceUrl: str,
	url: str,
	licenseName: str,
	licenseUrl: str | None,
) -> AddonData:
	"""Refer to _validate/addonVersion_schema.json"""
	try:
		addonVersionNumber = MajorMinorPatch.getFromStr(cast(str, manifest["version"]))
	except ValueError as e:
		raise ValueError(f"Manifest version invalid {manifest['version']}") from e

	for key in ("name", "summary", "description", "minimumNVDAVersion", "lastTestedNVDAVersion", "version"):
		if key not in manifest:
			raise KeyError(f"Manifest missing required key '{key}'.")

	# Add optional fields
	homepage: str | None = parseConfigValue(manifest, "url")
	changelog: str | None = parseConfigValue(manifest, "changelog")
	translations: list[dict[str, str]] = []
	for langCode, translatedManifest in getAddonManifestLocalizations(manifest):
		# Add optional translated changelog.
		translatedChangelog: str | None = parseConfigValue(translatedManifest, "changelog")

		try:
			translation: dict[str, str] = {
				"language": langCode,
				"displayName": cast(str, translatedManifest["summary"]),
				"description": cast(str, translatedManifest["description"]),
			}
			if translatedChangelog is not None:
				translation["changelog"] = translatedChangelog
			translations.append(translation)
		except KeyError as e:
			raise KeyError(f"Translation for {langCode} missing required key '{e.args[0]}'.") from e

	addonData = AddonData(
		addonId=cast(str, manifest["name"]),
		displayName=cast(str, manifest["summary"]),
		URL=url,
		description=cast(str, manifest["description"]),
		sha256=sha,
		addonVersionName=cast(str, manifest["version"]),
		addonVersionNumber=dataclasses.asdict(addonVersionNumber),
		minNVDAVersion=dataclasses.asdict(MajorMinorPatch(*cast(tuple[int], manifest["minimumNVDAVersion"]))),
		lastTestedVersion=dataclasses.asdict(
			MajorMinorPatch(*cast(ApiVersionT, manifest["lastTestedNVDAVersion"])),
		),
		channel=channel,
		publisher=publisher,
		sourceURL=sourceUrl,
		license=licenseName,
		homepage=homepage,
		changelog=changelog,
		licenseURL=licenseUrl,
		submissionTime=getCurrentTime(),
		translations=translations,
	)

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
	errorFilePath: str | None = args.errorOutputFile

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


if __name__ == "__main__":
	main()
