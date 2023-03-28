#!/usr/bin/env python

# Copyright (C) 2021 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html


import sys
import os
import re
import urllib.request
import typing
import argparse
import json
from jsonschema import validate, exceptions

sys.path.append(os.path.dirname(__file__))  # To allow this module to be run as a script by runValidate.bat
# E402 module level import not at top of file
import sha256  # noqa:E402
from addonManifest import AddonManifest   # noqa:E402
from manifestLoader import getAddonManifest, TEMP_DIR  # noqa:E402
from majorMinorPatch import MajorMinorPatch  # noqa:E402
del sys.path[-1]


JSON_SCHEMA = os.path.join(os.path.dirname(__file__), "addonVersion_schema.json")
JsonObjT = typing.Dict[str, typing.Any]


ValidationErrorGenerator = typing.Generator[str, None, None]


def getAddonMetadata(filename: str) -> JsonObjT:
	"""Loads addon submission metadata json file and returns as object.
	Raises if the metadata does not conform to the schema.
	"""
	with open(filename) as f:
		data: JsonObjT = json.load(f)
	_validateJson(data)
	return data


def getExistingVersions(verFilename: str) -> typing.List[str]:
	"""Loads API versions file and returns list of versions formatted as strings.
	"""
	with open(verFilename) as f:
		data: JsonObjT = json.load(f)
	return [_formatVersionString(version["apiVer"].values()) for version in data]


def _validateJson(data: JsonObjT) -> None:
	""" Ensure that the loaded metadata conforms to the schema.
	Raise error if not
	"""
	with open(JSON_SCHEMA) as f:
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
		sha256Addon = sha256.sha256_checksum(f)
	if sha256Addon.upper() != expectedSha.upper():
		yield f"Sha256 of .nvda-addon at URL is: {sha256Addon}"


def checkSummaryMatchesDisplayName(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	""" The submission Name must match the *.nvda-addon manifest summary field.
	"""
	summary = manifest["summary"]
	if summary != submission["displayName"]:
		yield (
			f"Submission 'displayName' must be set to '{summary}' in json file."
			f" Instead got: '{submission['displayName']}'"
		)


def checkDescriptionMatches(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	""" The submission description must match the *.nvda-addon manifest description field."""
	description = manifest["description"]
	if description != submission["description"]:
		yield (
			f"Submission 'description' must be set to '{description}' in json file."
			f" Instead got: '{submission['description']}'"
		)


def checkUrlMatchesHomepage(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	""" The submission homepage must match the *.nvda-addon manifest url field.
	"""
	if manifest.get("url") != submission.get("homepage"):
		yield f"Submission 'homepage' must be set to '{manifest.get('url')}' " \
		f"in json file instead of {submission.get('homepage')}"


def checkAddonId(
		manifest: AddonManifest,
		submissionFilePath: str,
		submission: JsonObjT,
) -> ValidationErrorGenerator:
	"""  The submitted json file must be placed in a folder matching the *.nvda-addon manifest name field.
	"""
	expectedName = manifest["name"]
	idInPath = os.path.basename(os.path.dirname(submissionFilePath))
	if expectedName != idInPath:
		yield (
			"Submitted json file must be placed in a folder matching"
			f" the addonId/name '{expectedName}'"
		)
	if expectedName != submission['addonId']:
		yield (
			"Submission data 'addonId' field does not match 'name' field in addon manifest:"
			f" {expectedName} vs {submission['addonId']}"
		)


VERSION_PARSE = re.compile(r"^(\d+)(?:$|(?:\.(\d+)$)|(?:\.(\d+)\.(\d+)$))")


def parseVersionStr(ver: str) -> typing.Dict[str, int]:

	matches = VERSION_PARSE.match(ver)
	if not matches:
		return {
			"major": 0,
			"minor": 0,
			"patch": 0
		}

	groups = list(x for x in matches.groups() if x)
	groups.extend([0, 0])  # ensure there are enough elements (smallest match is a single value)
	version = {
		"major": int(groups[0]),
		"minor": int(groups[1]),
		"patch": int(groups[2])
	}

	return version


def _formatVersionString(versionValues: typing.Iterable) -> str:
	versionValues = list(versionValues)
	assert 1 < len(versionValues) < 4
	return ".".join(
		str(x) for x in versionValues
	)


def checkSubmissionFilenameMatchesVersionNumber(
		submissionFilePath: str,
		submission: JsonObjT,
) -> ValidationErrorGenerator:
	versionFromPath: str = os.path.splitext(os.path.basename(submissionFilePath))[0]
	versionNumber: JsonObjT = submission['addonVersionNumber']
	formattedVersionNumber = _formatVersionString(versionNumber.values())
	if versionFromPath != formattedVersionNumber:
		# yield f"Submitted json file should be named '{formattedVersionNumber}.json'"
		yield (
			"Submission filename and versionNumber mismatch error:"
			f" versionNumberField: {formattedVersionNumber}"
			f" version from submission filename: {versionFromPath}"
			f" expected submission filename: {formattedVersionNumber}.json"
		)


def checkParsedVersionNameMatchesVersionNumber(
		submission: JsonObjT
) -> ValidationErrorGenerator:
	versionNumber: JsonObjT = submission['addonVersionNumber']
	versionName: str = submission['addonVersionName']
	parsedVersion = parseVersionStr(versionName)
	if parsedVersion != versionNumber:
		yield (
			"Warning: submission data 'addonVersionName' and 'addonVersionNumber' mismatch."
			f"  Unable to parse: {versionName} and match with {_formatVersionString(versionNumber.values())}"
		)


def checkManifestVersionMatchesVersionName(
		manifest: AddonManifest,
		submission: JsonObjT
) -> ValidationErrorGenerator:
	manifestVersion: str = manifest["version"]
	addonVersionName: str = submission["addonVersionName"]
	if manifestVersion != addonVersionName:
		yield (
			"Submission data 'addonVersionName' field does not match 'version' field in"
			f" addon manifest: {manifestVersion} vs addonVersionName: {addonVersionName}"
		)


def checkMinNVDAVersionMatches(
		manifest: AddonManifest,
		submission: JsonObjT
) -> ValidationErrorGenerator:
	manifestMinimumNVDAVersion = MajorMinorPatch.getFromStr(manifest["minimumNVDAVersion"])
	minNVDAVersion = MajorMinorPatch(**submission["minNVDAVersion"])
	if manifestMinimumNVDAVersion != minNVDAVersion:
		yield (
			"Submission data 'minNVDAVersion' field does not match 'minNVDAVersion' field in"
			f" addon manifest: {manifestMinimumNVDAVersion} vs minNVDAVersion: {minNVDAVersion}"
		)


def checkLastTestedNVDAVersionMatches(
		manifest: AddonManifest,
		submission: JsonObjT
) -> ValidationErrorGenerator:
	manifestLastTestedNVDAVersion = MajorMinorPatch.getFromStr(manifest["lastTestedNVDAVersion"])
	lastTestedVersion = MajorMinorPatch(**submission["lastTestedVersion"])
	if manifestLastTestedNVDAVersion != lastTestedVersion:
		yield (
			"Submission data 'lastTestedVersion' field does not match 'lastTestedNVDAVersion' field in"
			f" addon manifest: {manifestLastTestedNVDAVersion} vs lastTestedVersion: {lastTestedVersion}"
		)


def checkLastTestedVersionExist(submission: JsonObjT, verFilename: str) -> ValidationErrorGenerator:
	lastTestedVersion: JsonObjT = submission['lastTestedVersion']
	formattedLastTestedVersion: str = _formatVersionString(lastTestedVersion.values())
	if formattedLastTestedVersion not in getExistingVersions(verFilename):
		yield f"Last tested version error: {formattedLastTestedVersion} doesn't exist"


def checkMinRequiredVersionExist(submission: JsonObjT, verFilename: str) -> ValidationErrorGenerator:
	minRequiredVersion: JsonObjT = submission["minNVDAVersion"]
	formattedMinRequiredVersion: str = _formatVersionString(minRequiredVersion.values())
	if formattedMinRequiredVersion not in getExistingVersions(verFilename):
		yield f"Minimum required version error: {formattedMinRequiredVersion} doesn't exist"


def checkVersions(
		manifest: AddonManifest,
		submissionFilePath: str,
		submission: JsonObjT
) -> ValidationErrorGenerator:
	"""Check submitted json file name matches the *.nvda-addon manifest name field.
	"""
	yield from checkSubmissionFilenameMatchesVersionNumber(
		submissionFilePath,
		submission
	)
	yield from checkManifestVersionMatchesVersionName(manifest, submission)
	yield from checkParsedVersionNameMatchesVersionNumber(submission)


def validateSubmission(submissionFilePath: str, verFilename: str) -> ValidationErrorGenerator:
	try:
		submissionData = getAddonMetadata(filename=submissionFilePath)
		print("Submission JSON validated with schema.")

		urlErrors = list(checkDownloadUrlFormat(submissionData["URL"]))
		if urlErrors:
			# if there are errors in the URL validation can not continue
			yield from urlErrors
			raise ValueError(submissionData["URL"])
		print("Addon URL passes format requirements")

		addonDestPath = os.path.join(TEMP_DIR, "addon.nvda-addon")
		yield from downloadAddon(url=submissionData["URL"], destPath=addonDestPath)
		print("Addon downloaded successfully")

		checksumErrors = list(checkSha256(addonDestPath, expectedSha=submissionData["sha256"]))
		if checksumErrors:
			yield from checksumErrors
		else:
			print("Sha256 matches")

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


def outputResult(errors: ValidationErrorGenerator, errorFilePath: typing.Optional[str] = None):
	errors = list(errors)
	if len(errors) > 0:
		print("\r\n".join(errors))
		if errorFilePath:
			with open(errorFilePath, "w") as errorFile:
				errorFile.write("Validation Errors:\n- " + "\n- ".join(errors))
		raise ValueError("Submission not valid")
	print("Congratulations: manifest, metadata and file path are valid")


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--dry-run",
		action="store_true",
		default=False,
		help="Ensures the correct arguments are passed, doesn't run checks, exists with success."
	)
	parser.add_argument(
		dest="file",
		help="The json (.json) file containing add-on metadata."
	)
	parser.add_argument(
		dest="APIVersions",
		help="The JSON file containing valid NVDA API versions."
	)
	parser.add_argument(
		dest="errorOutputFile",
		help="The text file to output errors from the validation, if any.",
		default=None,
	)

	args = parser.parse_args()
	filename = args.file
	verFilename = args.APIVersions
	errorOutputFile = args.errorOutputFile

	if not args.dry_run:
		errors = validateSubmission(filename, verFilename)
		outputResult(errors, errorOutputFile)


if __name__ == '__main__':
	main()
