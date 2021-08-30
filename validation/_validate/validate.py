#!/usr/bin/env python

# Copyright (C) 2021 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import argparse
import enum
import os
import re
import tempfile
import typing
import zipfile
import json
import urllib.request
from jsonschema import validate, exceptions

import sys
# To allow this module to be run as a script by runValidate.bat
sys.path.append(os.path.dirname(__file__))
# E402 module level import not at top of file
import sha256  # noqa:E402
from addonManifest import AddonManifest   # noqa:E402
del sys.path[-1]


JSON_SCHEMA = os.path.join(os.path.dirname(__file__), "addonVersion_schema.json")
TEMP_DIR = tempfile.gettempdir()

JsonObjT = typing.Dict[str, typing.Any]


@enum.unique
class ValidationErrorMessage(enum.Enum):
	URL_MISSING_HTTPS = "Add-on download url must start with https://"
	URL_MISSING_ADDON_EXT = "Add-on download url must end with .nvda-addon"
	URL_DOWNLOAD_ERROR = "Download of addon failed"
	CHECKSUM_FAILURE = "Sha256 of .nvda-addon at URL is: {}"
	NAME = "Submission 'displayName' must be set to '{}' in json file. Instead got: '{}'"
	DESC = "Submission 'description' must be set to '{}' in json file. Instead got: '{}'"
	VERSION = "Addon version in submission data does not match manifest value: {}"
	HOMEPAGE = "Submission 'homepage' must be set to '{}' in json file"
	SUBMISSION_DIR_ADDON_NAME = "Submitted json file must be placed in {} folder."
	SUBMISSION_DIR_ADDON_VER = "Submitted json file should be named {}.json"


ValidationErrorGenerator = typing.Generator[str, None, None]


def getAddonMetadata(filename: str) -> JsonObjT:
	"""Loads addon submission metadata json file and returns as object.
	Raises if the metadata does not conform to the schema.
	"""
	with open(filename) as f:
		data: JsonObjT = json.load(f)
	_validateJson(data)
	return data


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
		yield ValidationErrorMessage.URL_MISSING_HTTPS.value
	if not url.endswith(".nvda-addon"):
		yield ValidationErrorMessage.URL_MISSING_ADDON_EXT.value


def downloadAddon(url: str, destPath: str) -> ValidationErrorGenerator:
	"""Download the addon file, save as destPath
	Raise on failure.
	"""
	DOWNLOAD_BLOCK_SIZE = 8192  # 8 kb
	remote = urllib.request.urlopen(url)
	if remote.code != 200:
		yield ValidationErrorMessage.URL_DOWNLOAD_ERROR.value
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
		yield ValidationErrorMessage.CHECKSUM_FAILURE.value.format(sha256Addon)


def getAddonManifest(addonPath: str) -> AddonManifest:
	""" Extract manifest.ini from *.nvda-addon and parse.
	Raise on error.
	"""
	expandedPath = os.path.join(TEMP_DIR, "nvda-addon")
	with zipfile.ZipFile(addonPath, "r") as z:
		for info in z.infolist():
			z.extract(info, expandedPath)
	filePath = os.path.join(expandedPath, "manifest.ini")
	try:
		manifest = AddonManifest(filePath)
		return manifest
	except Exception as err:
		raise err


def checkSummaryMatchesDisplayName(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	""" The submission Name must match the *.nvda-addon manifest summary field.
	"""
	summary = manifest["summary"]
	if summary != submission["displayName"]:
		yield ValidationErrorMessage.NAME.value.format(summary, submission["displayName"])


def checkDescriptionMatches(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	""" The submission description must match the *.nvda-addon manifest description field."""
	description = manifest["description"]
	if description != submission["description"]:
		yield ValidationErrorMessage.DESC.value.format(description, submission["description"])


def checkUrlMatchesHomepage(manifest: AddonManifest, submission: JsonObjT) -> ValidationErrorGenerator:
	""" The submission homepage must match the *.nvda-addon manifest url field.
	"""
	if manifest["url"] != submission["homepage"]:
		yield ValidationErrorMessage.HOMEPAGE.value.format(manifest['url'])


def checkAddonId(
		manifest: AddonManifest,
		submissionFilePath: str,
		submission: JsonObjT,
) -> ValidationErrorGenerator:
	"""  The submitted json file must be placed in a folder matching the *.nvda-addon manifest name field.
	"""
	if manifest["name"] != os.path.basename(os.path.dirname(submissionFilePath)):
		yield ValidationErrorMessage.SUBMISSION_DIR_ADDON_NAME.value.format(manifest['name'])


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


def checkVersions(
		manifest: AddonManifest,
		submissionFilePath: str,
		submission: JsonObjT
) -> ValidationErrorGenerator:
	"""Check submitted json file name matches the *.nvda-addon manifest name field.
	"""
	if manifest['version'] != os.path.splitext(os.path.basename(submissionFilePath))[0]:
		yield ValidationErrorMessage.SUBMISSION_DIR_ADDON_VER.value.format(manifest['version'])

	if parseVersionStr(manifest['version']) != submission['addonVersion']:
		yield ValidationErrorMessage.VERSION.value.format(manifest['version'])


def validateSubmission(submissionFilePath: str) -> ValidationErrorGenerator:
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

		manifest = getAddonManifest(addonDestPath)
		yield from checkSummaryMatchesDisplayName(manifest, submissionData)
		yield from checkDescriptionMatches(manifest, submissionData)
		yield from checkUrlMatchesHomepage(manifest, submissionData)
		yield from checkAddonId(manifest, submissionFilePath, submissionData)
		yield from checkVersions(manifest, submissionFilePath, submissionData)

	except Exception as e:
		yield f"Fatal error, unable to continue: {e}"


def outputResult(errors: ValidationErrorGenerator):
	errors = list(errors)
	if len(errors) > 0:
		print("\r\n".join(errors))
		raise ValueError("Submission not valid")
	print("Congratulations: manifest, metadata and file path are valid")


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--dry-run",
		action="store_true",
		default=False,
	)
	parser.add_argument(
		dest="file",
		help="The json (.json) file containing add-on metadata."
	)

	args = parser.parse_args()
	filename = args.file

	if not args.dry_run:
		errors = validateSubmission(filename)
	else:
		errors = iter(())
	outputResult(errors)


if __name__ == '__main__':
	main()
