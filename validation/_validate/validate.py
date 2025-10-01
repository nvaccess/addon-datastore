# Copyright (C) 2021-2025 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import argparse
from collections.abc import Generator
from glob import glob
import json
import os
import re
from typing import Any, cast
import urllib.request

from jsonschema import validate, exceptions

from .addonManifest import AddonManifest, ApiVersionT
from .manifestLoader import getAddonManifest, TEMP_DIR
from .majorMinorPatch import MajorMinorPatch
from .sha256 import sha256_checksum


JSON_SCHEMA = os.path.join(os.path.dirname(__file__), "addonVersion_schema.json")
JsonObjT = dict[str, Any]


ValidationErrorGenerator = Generator[str, None, None]


def getAddonMetadata(filename: str) -> JsonObjT:
	"""Loads addon submission metadata json file and returns as object.
	Raises if the metadata does not conform to the schema.
	"""
	with open(filename, encoding="utf-8") as f:
		data: JsonObjT = json.load(f)
	validateJson(data)
	return data


def getExistingVersions(verFilename: str) -> list[str]:
	"""Loads API versions file and returns list of versions formatted as strings."""
	with open(verFilename, encoding="utf-8") as f:
		data: list[JsonObjT] = json.load(f)
	return [_formatVersionString(version["apiVer"].values()) for version in data]


def getExistingStableVersions(verFilename: str) -> list[str]:
	"""Loads API versions file and returns list of stable versions formatted as strings."""
	with open(verFilename, encoding="utf-8") as f:
		data: list[JsonObjT] = json.load(f)
	return [
		_formatVersionString(version["apiVer"].values())
		for version in data
		if not version.get("experimental", False)
	]


def validateJson(data: JsonObjT) -> None:
	"""Ensure that the loaded metadata conforms to the schema.
	Raise error if not
	"""
	with open(JSON_SCHEMA, encoding="utf-8") as f:
		schema = json.load(f)
	try:
		validate(instance=data, schema=schema)
	except exceptions.ValidationError as err:
		raise err


def checkDownloadUrlFormat(url: str) -> ValidationErrorGenerator:
	"""Check for common errors with download URL string.
	It must be a:
	- HTTPS URL
	- Pointing to a '.nvda-addon' file.
	Raise on failure
	"""
	if not url.startswith("https://"):
		yield "Add-on download url must start with https://"
	if not url.endswith(".nvda-addon"):
		yield "Add-on download url must end with .nvda-addon"


def downloadAddon(url: str, destPath: str) -> ValidationErrorGenerator:
	"""Download the addon file, save as destPath
	Raise on failure.
	"""
	DOWNLOAD_BLOCK_SIZE = 8192  # 8 kb
	remote = urllib.request.urlopen(url)
	if remote.code != 200:
		yield "Download of addon failed"
		raise RuntimeError(f"Unable to download from {url}, HTTP response status code: {remote.code}")
	size = int(remote.headers["content-length"])
	with open(destPath, "wb") as local:
		read = 0
		chunk = DOWNLOAD_BLOCK_SIZE
		while True:
			remainingSize = size - read
			if remainingSize < chunk:
				chunk = remainingSize
			block = remote.read(chunk)
			if not block:
				break
			read += len(block)
			local.write(block)
	return


def checkSha256(addonPath: str, expectedSha: str) -> ValidationErrorGenerator:
	"""Calculate the hash (SHA256) of the *.nvda-addon
	Return an error if it does not match the expected.
	"""
	with open(addonPath, "rb") as f:
		sha256Addon = sha256_checksum(f)
	if sha256Addon.upper() != expectedSha.upper():
		yield f"Sha256 of .nvda-addon at URL is: {sha256Addon}"


def checkSummaryMatchesDisplayName(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	"""The submission Name must match the *.nvda-addon manifest summary field."""
	summary = cast(str, manifest["summary"])
	if summary != submission["displayName"]:
		yield (
			f"Submission 'displayName' must be set to '{summary}' in json file."
			f" Instead got: '{submission['displayName']}'"
		)


def checkDescriptionMatches(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	"""The submission description must match the *.nvda-addon manifest description field."""
	description = cast(str, manifest["description"])
	if description != submission["description"]:
		yield (
			f"Submission 'description' must be set to '{description}' in json file."
			f" Instead got: '{submission['description']}'"
		)


def checkUrlMatchesHomepage(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	"""The submission homepage must match the *.nvda-addon manifest url field."""
	manifestUrl = manifest.get("url")  # type: ignore[reportUnknownMemberType]
	if manifestUrl == "None":
		# The config default is None which is parsed by configobj as a string not a NoneType
		manifestUrl = None
	if manifestUrl != submission.get("homepage"):
		yield (
			f"Submission 'homepage' must be set to '{manifest.get('url')}' "  # type: ignore[reportUnknownMemberType]
			f"in json file instead of {submission.get('homepage')}"
		)


def checkAddonId(
	manifest: AddonManifest,
	submissionFilePath: str,
	submission: JsonObjT,
) -> ValidationErrorGenerator:
	"""The submitted json file must be placed in a folder matching the *.nvda-addon manifest name field."""
	expectedName = cast(str, manifest["name"])
	idInPath = os.path.basename(os.path.dirname(submissionFilePath))
	if expectedName != idInPath:
		yield (f"Submitted json file must be placed in a folder matching the addonId/name '{expectedName}'")
	if expectedName != submission["addonId"]:
		yield (
			"Submission data 'addonId' field does not match 'name' field in addon manifest:"
			f" {expectedName} vs {submission['addonId']}"
		)
	if not re.match(r"^[A-Za-z][A-Za-z0-9\-_]*[A-Za-z0-9]$", expectedName):
		yield (
			"Submission data 'addonId' field does not match the expected format:"
			" must start and end with a letter, and contain only letters,"
			" numbers, underscores, and hyphens. "
			f"ID: {submission['addonId']}"
		)


VERSION_PARSE = re.compile(r"^(\d+)(?:$|(?:\.(\d+)$)|(?:\.(\d+)\.(\d+)$))")


def parseVersionStr(ver: str) -> dict[str, int]:
	matches = VERSION_PARSE.match(ver)
	if not matches:
		return {
			"major": 0,
			"minor": 0,
			"patch": 0,
		}

	groups = list(x for x in matches.groups() if x)
	groups.extend([0, 0])  # ensure there are enough elements (smallest match is a single value)
	version = {
		"major": int(groups[0]),
		"minor": int(groups[1]),
		"patch": int(groups[2]),
	}

	return version


def _formatVersionString(versionValues: ApiVersionT) -> str:
	return ".".join(str(x) for x in versionValues)


def checkSubmissionFilenameMatchesVersionNumber(
	submissionFilePath: str,
	submission: JsonObjT,
) -> ValidationErrorGenerator:
	versionFromPath: str = os.path.splitext(os.path.basename(submissionFilePath))[0]
	versionNumber: dict[str, int] = submission["addonVersionNumber"]
	formattedVersionNumber = _formatVersionString(cast(ApiVersionT, tuple(versionNumber.values())))
	if versionFromPath != formattedVersionNumber:
		# yield f"Submitted json file should be named '{formattedVersionNumber}.json'"
		yield (
			"Submission filename and versionNumber mismatch error:"
			f" addonVersionNumber: {formattedVersionNumber}"
			f" version from submission filename: {versionFromPath}"
			f" expected submission filename: {formattedVersionNumber}.json"
		)


def checkParsedVersionNameMatchesVersionNumber(submission: JsonObjT) -> ValidationErrorGenerator:
	versionNumber: dict[str, int] = submission["addonVersionNumber"]
	versionName: str = submission["addonVersionName"]
	parsedVersion = parseVersionStr(versionName)
	if parsedVersion != versionNumber:
		yield (
			"Warning: submission data 'addonVersionName' and 'addonVersionNumber' mismatch."
			f"  Unable to parse: {versionName} and match with {_formatVersionString(cast(ApiVersionT, tuple(versionNumber.values())))}"
		)


def checkManifestVersionMatchesVersionName(
	manifest: AddonManifest,
	submission: JsonObjT,
) -> ValidationErrorGenerator:
	manifestVersion: str = cast(str, manifest["version"])
	addonVersionName: str = submission["addonVersionName"]
	if manifestVersion != addonVersionName:
		yield (
			"Submission data 'addonVersionName' field does not match 'version' field in"
			f" addon manifest: {manifestVersion} vs addonVersionName: {addonVersionName}"
		)


def checkMinNVDAVersionMatches(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	manifestMinimumNVDAVersion = MajorMinorPatch(*cast(ApiVersionT, manifest["minimumNVDAVersion"]))
	minNVDAVersion = MajorMinorPatch(**submission["minNVDAVersion"])
	if manifestMinimumNVDAVersion != minNVDAVersion:
		yield (
			"Submission data 'minNVDAVersion' field does not match 'minNVDAVersion' field in"
			f" addon manifest: {manifestMinimumNVDAVersion} vs minNVDAVersion: {minNVDAVersion}"
		)


def checkLastTestedNVDAVersionMatches(
	manifest: AddonManifest,
	submission: JsonObjT,
) -> ValidationErrorGenerator:
	manifestLastTestedNVDAVersion = MajorMinorPatch(*cast(ApiVersionT, manifest["lastTestedNVDAVersion"]))
	lastTestedVersion = MajorMinorPatch(**submission["lastTestedVersion"])
	if manifestLastTestedNVDAVersion != lastTestedVersion:
		yield (
			"Submission data 'lastTestedVersion' field does not match 'lastTestedNVDAVersion' field in"
			f" addon manifest: {manifestLastTestedNVDAVersion} vs lastTestedVersion: {lastTestedVersion}"
		)


def checkLastTestedVersionExist(submission: JsonObjT, verFilename: str) -> ValidationErrorGenerator:
	lastTestedVersion: dict[str, int] = submission["lastTestedVersion"]
	formattedLastTestedVersion: str = _formatVersionString(cast(ApiVersionT, lastTestedVersion.values()))
	if formattedLastTestedVersion not in getExistingVersions(verFilename):
		yield f"Last tested version error: {formattedLastTestedVersion} doesn't exist"

	elif submission["channel"] == "stable" and formattedLastTestedVersion not in getExistingStableVersions(
		verFilename,
	):
		yield (
			f"Last tested version error: {formattedLastTestedVersion} is not stable yet. "
			+ "Please submit add-on using the beta or dev channel."
		)


def checkMinRequiredVersionExist(submission: JsonObjT, verFilename: str) -> ValidationErrorGenerator:
	minRequiredVersion: dict[str, int] = submission["minNVDAVersion"]
	formattedMinRequiredVersion: str = _formatVersionString(cast(ApiVersionT, minRequiredVersion.values()))
	if formattedMinRequiredVersion not in getExistingVersions(verFilename):
		yield f"Minimum required version error: {formattedMinRequiredVersion} doesn't exist"

	elif submission["channel"] == "stable" and formattedMinRequiredVersion not in getExistingStableVersions(
		verFilename,
	):
		yield (
			f"Minimum required version error: {formattedMinRequiredVersion} is not stable yet. "
			+ "Please submit add-on using the beta or dev channel."
		)


def checkVersions(
	manifest: AddonManifest,
	submissionFilePath: str,
	submission: JsonObjT,
) -> ValidationErrorGenerator:
	"""Check submitted json file name matches the *.nvda-addon manifest name field."""
	yield from checkSubmissionFilenameMatchesVersionNumber(submissionFilePath, submission)
	yield from checkManifestVersionMatchesVersionName(manifest, submission)
	yield from checkParsedVersionNameMatchesVersionNumber(submission)


def validateSubmission(submissionFilePath: str, verFilename: str) -> ValidationErrorGenerator:
	try:
		submissionData = getAddonMetadata(filename=submissionFilePath)

		if submissionData.get("legacy"):
			# Legacy add-ons do not need a valid manifest or metadata
			return None

		urlErrors = list(checkDownloadUrlFormat(submissionData["URL"]))
		if urlErrors:
			# if there are errors in the URL validation can not continue
			yield from urlErrors
			raise ValueError(submissionData["URL"])

		addonDestPath = os.path.join(TEMP_DIR, "addon.nvda-addon")
		if os.path.exists(addonDestPath):
			os.remove(addonDestPath)
		yield from downloadAddon(url=submissionData["URL"], destPath=addonDestPath)

		checksumErrors = list(checkSha256(addonDestPath, expectedSha=submissionData["sha256"]))
		if checksumErrors:
			yield from checksumErrors

		yield from checkLastTestedVersionExist(submissionData, verFilename)
		yield from checkMinRequiredVersionExist(submissionData, verFilename)

		manifest = getAddonManifest(addonDestPath)
		yield from checkSummaryMatchesDisplayName(manifest, submissionData)
		yield from checkDescriptionMatches(manifest, submissionData)
		yield from checkUrlMatchesHomepage(manifest, submissionData)
		yield from checkAddonId(manifest, submissionFilePath, submissionData)
		yield from checkMinNVDAVersionMatches(manifest, submissionData)
		yield from checkLastTestedNVDAVersionMatches(manifest, submissionData)
		yield from checkVersions(manifest, submissionFilePath, submissionData)

	except Exception as e:
		yield f"Fatal error, unable to continue: {e}"


def outputErrors(addonFileName: str, errors: list[str], errorFilePath: str | None = None):
	if len(errors) > 0:
		print("\r\n".join(errors))
		if errorFilePath:
			with open(errorFilePath, "a", encoding="utf-8") as errorFile:
				errorFile.write(f"Validation Errors for {addonFileName}:\n- " + "\n- ".join(errors) + "\n\n")


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--dry-run",
		action="store_true",
		default=False,
		help="Ensures the correct arguments are passed, doesn't run checks, exists with success.",
	)
	parser.add_argument(
		dest="filePathGlob",
		help="The json (.json) files containing add-on metadata. e.g. addons/*/*.json.",
	)
	parser.add_argument(
		dest="APIVersions",
		help="The JSON file containing valid NVDA API versions.",
	)
	parser.add_argument(
		"--output",
		dest="errorOutputFile",
		help="The text file to output errors from the validation, if any.",
		default=None,
	)

	args = parser.parse_args()
	addonFiles: list[str] = glob(args.filePathGlob)
	verFilename: str = args.APIVersions
	errorOutputFile: str = args.errorOutputFile
	if errorOutputFile and os.path.exists(errorOutputFile):
		os.remove(errorOutputFile)

	if not args.dry_run:
		anyErrors = False
		for filename in addonFiles:
			print(f"Validating {filename}")
			errors = list(validateSubmission(filename, verFilename))
			if errors:
				anyErrors = True
				outputErrors(filename, errors, errorOutputFile)
		if anyErrors:
			print(f"Validation errors for {args.filePathGlob} in {errorOutputFile}")
			raise ValueError(f"Validation errors for {args.filePathGlob} in {errorOutputFile}")
		else:
			print(f"No validation errors for {args.filePathGlob}")


if __name__ == "__main__":
	main()
