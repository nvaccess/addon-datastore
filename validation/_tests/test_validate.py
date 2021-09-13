#!/usr/bin/env python

# Copyright (C) 2021 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import unittest
from unittest.mock import patch
import os
import json
from jsonschema import exceptions
from _validate import validate, addonManifest


VALID_ADDON_ID = "fake"
VALID_ADDON_VER = '13.0'

JSON_SCHEMA = validate.JSON_SCHEMA
TOP_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_DIR = os.path.dirname(TOP_DIR)
TEST_DATA_PATH = os.path.join(SOURCE_DIR, '_tests', 'testData')
ADDON_PACKAGE = os.path.join(TEST_DATA_PATH, f'{VALID_ADDON_ID}.nvda-addon')
ADDON_SUBMISSIONS_DIR = os.path.join(TEST_DATA_PATH, 'addons')
VALID_SUBMISSION_JSON_FILE = os.path.join(ADDON_SUBMISSIONS_DIR, VALID_ADDON_ID, f'{VALID_ADDON_VER}.json')
MANIFEST_FILE = os.path.join(TEST_DATA_PATH, 'manifest.ini')


def getValidAddonSubmission() -> validate.JsonObjT:
	with open(VALID_SUBMISSION_JSON_FILE) as f:
		submission = json.load(f)
	return submission


def getAddonManifest():
	with open(MANIFEST_FILE) as f:
		manifest = addonManifest.AddonManifest(f)
	return manifest


class Validate_general(unittest.TestCase):
	def setUp(self):
		self.submissionData = getValidAddonSubmission()
		self.manifest = getAddonManifest()

	def tearDown(self):
		self.submissionData = None
		self.manifest = None

	def test_validateJson_SchemaNonConformance_Raises(self):
		self.submissionData["description"] = 3  # should be a string
		with self.assertRaises(exceptions.ValidationError):
			validate._validateJson(self.submissionData)


class Validate_checkDownloadUrlFormat(unittest.TestCase):
	"""Tests for the checkDownloadUrlFormat function
	"""
	def test_validExampleURL(self):
		url = (
			"https://github.com/nvdaes/clipContentsDesigner/releases/download/13.0/"
			"clipContentsDesigner-13.0.nvda-addon"
		)
		errors = list(
			validate.checkDownloadUrlFormat(url)
		)
		self.assertEqual(errors, [])

	def test_minimalRequirementsURL(self):
		url = "https://something.nvda-addon"
		errors = list(
			validate.checkDownloadUrlFormat(url)
		)
		self.assertEqual(errors, [])

	def test_missingHTTPS(self):
		url = "http://something.nvda-addon"
		errors = list(
			validate.checkDownloadUrlFormat(url)
		)
		self.assertEqual(
			errors,
			[validate.ValidationErrorMessage.URL_MISSING_HTTPS.value]
		)

	def test_missingExt(self):
		url = "https://example.com"
		errors = list(
			validate.checkDownloadUrlFormat(url)
		)
		self.assertEqual(
			errors,
			[validate.ValidationErrorMessage.URL_MISSING_ADDON_EXT.value]
		)

	def test_missingHTTPsAndExt(self):
		url = "http://example.com"
		errors = list(
			validate.checkDownloadUrlFormat(url)
		)
		self.assertEqual(
			errors,
			[
				validate.ValidationErrorMessage.URL_MISSING_HTTPS.value,
				validate.ValidationErrorMessage.URL_MISSING_ADDON_EXT.value,
			]
		)


class Validate_checkSha256(unittest.TestCase):
	"""Tests for the checkSha256 function
	"""
	validSha = "12ABBF6BAC89FC24602245F4B8B750BCF2B72AFDF2DF54A0B07467FF4983F872"

	def test_valid(self):
		errors = validate.checkSha256(
			ADDON_PACKAGE,
			expectedSha=self.validSha.upper()
		)
		self.assertEqual(list(errors), [])

		errors = validate.checkSha256(
			ADDON_PACKAGE,
			expectedSha=self.validSha.lower()
		)
		self.assertEqual(list(errors), [])

	def test_invalid(self):
		errors = validate.checkSha256(
			# just do a SHA for the manifest file so we don't need to include the whole *.nvda-addon file
			ADDON_PACKAGE,
			expectedSha='abc'
		)
		errors = list(errors)
		expectedErrorMessage = validate.ValidationErrorMessage.CHECKSUM_FAILURE.value
		actualSha = self.validSha.lower()
		self.assertEqual(
			errors,
			[expectedErrorMessage.format(actualSha)]
		)


class Validate_checkSummaryMatchesDisplayName(unittest.TestCase):
	def setUp(self):
		self.submissionData = getValidAddonSubmission()
		self.manifest = getAddonManifest()

	def tearDown(self):
		self.submissionData = None
		self.manifest = None

	def test_valid(self):
		errors = list(
			validate.checkSummaryMatchesDisplayName(self.manifest, self.submissionData)
		)
		self.assertEqual(errors, [])

	def test_invalid(self):
		badDisplayName = "bad display Name"
		self.submissionData["displayName"] = badDisplayName
		errors = list(
			validate.checkSummaryMatchesDisplayName(self.manifest, self.submissionData)
		)
		expectedErrorMessage = validate.ValidationErrorMessage.NAME.value
		self.assertEqual(
			errors,
			[expectedErrorMessage.format(self.manifest["summary"], badDisplayName)]
		)


class Validate_checkDescriptionMatches(unittest.TestCase):
	def setUp(self):
		self.submissionData = getValidAddonSubmission()
		self.manifest = getAddonManifest()

	def tearDown(self):
		self.submissionData = None
		self.manifest = None

	def test_valid(self):
		errors = list(
			validate.checkDescriptionMatches(self.manifest, self.submissionData)
		)
		self.assertEqual(errors, [])

	def test_invalid(self):
		badDesc = "bad description"
		self.submissionData["description"] = badDesc
		errors = list(
			validate.checkDescriptionMatches(self.manifest, self.submissionData)
		)
		expectedErrorMessage = validate.ValidationErrorMessage.DESC.value
		self.assertEqual(
			errors,
			[expectedErrorMessage.format(self.manifest["description"], badDesc)]
		)


class Validate_checkAddonId(unittest.TestCase):
	"""
		Manifest 'name' considered source of truth for addonID
		Must match:
		- Submission file name '<addonID>/<version>.json'
		- `addonId` within the submission JSON data
	"""
	def setUp(self):
		self.submissionData = getValidAddonSubmission()
		self.manifest = getAddonManifest()

	def tearDown(self):
		self.submissionData = None
		self.manifest = None

	def test_valid(self):
		"""No error when manifest 'name', submission file path, and submission contents all agree.
		"""
		errors = list(
			validate.checkAddonId(self.manifest, VALID_SUBMISSION_JSON_FILE, self.submissionData)
		)
		self.assertEqual(errors, [])

	def test_invalidPath(self):
		""" Error when submission path does not include correct addon ID
		"""
		filename = os.path.join(TOP_DIR, "invalid")
		errors = list(
			validate.checkAddonId(self.manifest, filename, self.submissionData)
		)
		expectedErrorMessage = validate.ValidationErrorMessage.SUBMISSION_DIR_ADDON_NAME.value
		self.assertEqual(
			errors,
			[expectedErrorMessage.format(self.manifest['name'])]
		)

	def test_invalidJSONData(self):
		""" Error when submission does not include correct addonId
		"""
		invalidID = "invalid"
		self.submissionData['addonId'] = invalidID
		errors = list(
			validate.checkAddonId(self.manifest, VALID_SUBMISSION_JSON_FILE, self.submissionData)
		)
		expectedErrorMessage = validate.ValidationErrorMessage.ID.value
		self.assertEqual(
			[expectedErrorMessage.format(VALID_ADDON_ID, invalidID)],
			errors
		)

	def test_invalidJSONDataAndPath(self):
		""" Error when submission does not include correct addonId and file path does not include the addonID
		"""
		expectedAddonId = "valid"
		self.manifest['name'] = expectedAddonId
		errors = list(
			validate.checkAddonId(self.manifest, VALID_SUBMISSION_JSON_FILE, self.submissionData)
		)
		pathMessage = validate.ValidationErrorMessage.SUBMISSION_DIR_ADDON_NAME.value
		addonIdMessage = validate.ValidationErrorMessage.ID.value
		self.assertEqual(
			[
				pathMessage.format(expectedAddonId),
				addonIdMessage.format(expectedAddonId, "fake"),
			],
			errors
		)


class validate_checkVersions(unittest.TestCase):
	"""Tests for the checkVersions function.

		Manifest considered source of truth.
		Must match:
		- Submission file name '<addonID>/<version>.json'
		- `addonVersionField` within the submission JSON data
	"""
	def setUp(self):
		self.submissionData = getValidAddonSubmission()
		self.manifest = getAddonManifest()
		self.fileName = ""

	def tearDown(self):
		self.submissionData = None
		self.manifest = None

	def test_valid(self):
		"""No error when manifest version, submission file name, and submission contents all agree.
		"""

		errors = list(
			validate.checkVersions(self.manifest, VALID_SUBMISSION_JSON_FILE, self.submissionData)
		)
		self.assertEqual(errors, [])

	def test_invalidFilename(self):
		""" Error expected when fileName does not match manifest version
		"""
		filename = os.path.join(ADDON_SUBMISSIONS_DIR, VALID_ADDON_ID, "12.2.json")
		errors = list(
			validate.checkVersions(self.manifest, filename, self.submissionData)
		)
		expectedVersion = self.manifest['version']
		expectedErrorMessage = validate.ValidationErrorMessage.SUBMISSION_DIR_ADDON_VER.value
		self.assertEqual(
			errors,
			[expectedErrorMessage.format(expectedVersion)]
		)

	def test_JsonDoesntMatchManifest(self):
		""" Error expected when JSON data 'addonVersion' does not match manifest version.
		"""
		self.submissionData['addonVersionNumber'] = {
			"major": 12,
			"minor": 2,
			"patch": 0
		}
		submissionPath = os.path.join(ADDON_SUBMISSIONS_DIR, VALID_ADDON_ID, f'{VALID_ADDON_VER}.json')
		expectedVersion = self.manifest['version']
		errors = list(
			validate.checkVersions(self.manifest, submissionPath, self.submissionData)
		)
		expectedErrorMessage = validate.ValidationErrorMessage.VERSION.value
		self.assertEqual(
			[expectedErrorMessage.format(expectedVersion, "12.2.0")],
			errors
		)

	def test_invalidJSONDataAndFileName(self):
		""" Error expected when JSON data 'addonVersion' does not match manifest version.
		"""
		# update the manifest version so that both the submission file name, and it's contents are considered
		# invalid.
		expectedVersion = "13.2.1"
		self.manifest['version'] = expectedVersion
		errors = list(
			validate.checkVersions(self.manifest, VALID_SUBMISSION_JSON_FILE, self.submissionData)
		)

		fileNameError = validate.ValidationErrorMessage.SUBMISSION_DIR_ADDON_VER.value
		versionError = validate.ValidationErrorMessage.VERSION.value

		self.assertEqual(
			errors,
			[
				fileNameError.format(expectedVersion),
				versionError.format(expectedVersion, "13.0.0")
			]
		)


class Validate_outputResult(unittest.TestCase):

	def test_output_errorRaises(self):
		singleErrorGen = ("error string" for _ in range(1))
		with self.assertRaises(ValueError):
			validate.outputResult(singleErrorGen)

	def test_output_noError(self):
		noErrorGen = ("error string" for _ in range(0))
		validate.outputResult(noErrorGen)


class Validate_End2End(unittest.TestCase):

	class OpenUrlResult:
		def __init__(self, readFunc):
			self.read = readFunc
			self.code = 200
			self.headers = {
				"content-length": os.path.getsize(ADDON_PACKAGE)
			}

	def setUp(self) -> None:
		self.addonReader = open(ADDON_PACKAGE, 'rb')
		self.urlOpenResult = self.OpenUrlResult(self.addonReader.read)

	def tearDown(self) -> None:
		self.addonReader.close()

	@patch('_validate.validate.urllib.request.urlopen')
	def test_success(self, mock_urlopen):
		"""Run validate on a known good file.
		"""
		mock_urlopen.return_value = self.urlOpenResult
		errors = list(
			validate.validateSubmission(VALID_SUBMISSION_JSON_FILE)
		)
		self.assertEqual(list(errors), [])

	@patch('_validate.validate.urllib.request.urlopen')
	def test_downloadFailure(self, mock_urlopen):
		"""Unable to download addon
		"""
		self.urlOpenResult.code = 404  # add-on not found
		mock_urlopen.return_value = self.urlOpenResult
		errors = list(
			validate.validateSubmission(VALID_SUBMISSION_JSON_FILE)
		)
		self.assertEqual(
			list(errors),
			[
				'Download of addon failed',
				'Fatal error, unable to continue: Unable to download from '
				# note this the mocked urlopen function actually fetches from ADDON_PACKAGE
				'https://github.com/'
				'nvdaes/clipContentsDesigner/releases/download/13.0/'
				'clipContentsDesigner-13.0.nvda-addon, '
				'HTTP response status code: 404'
			]
		)


class ParseVersionString(unittest.TestCase):

	def test_single(self):
		self.assertEqual(
			{
				"major": 24,
				"minor": 0,
				"patch": 0,
			},
			validate.parseVersionStr("24")
		)

	def test_double(self):
		self.assertEqual(
			{
				"major": 24,
				"minor": 6,
				"patch": 0,
			},
			validate.parseVersionStr("24.6")
		)

	def test_triple(self):
		self.assertEqual(
			{
				"major": 24,
				"minor": 6,
				"patch": 1,
			},
			validate.parseVersionStr("24.6.1")
		)


class VersionRegex(unittest.TestCase):

	def test_versionMajorMinorPatch_valid(self):
		ver = "23.5.1"
		matches = validate.VERSION_PARSE.match(ver)
		self.assertTrue(matches)
		groups = list(x for x in matches.groups() if x)
		self.assertEqual(
			['23', '5', '1'],
			groups
		)

	def test_versionMajorMinor_valid(self):
		ver = "6.0"
		matches = validate.VERSION_PARSE.match(ver)
		self.assertTrue(matches)
		groups = list(x for x in matches.groups() if x)
		self.assertEqual(
			['6', '0'],
			groups
		)

	def test_versionMajor_valid(self):
		ver = "1"
		matches = validate.VERSION_PARSE.match(ver)
		self.assertTrue(matches)
		groups = list(x for x in matches.groups() if x)
		self.assertEqual(
			['1'],
			groups
		)

	def test_NonDotSep_invalid(self):
		ver = f"{3},{2},{1}"
		matches = validate.VERSION_PARSE.match(ver)
		self.assertFalse(matches)
