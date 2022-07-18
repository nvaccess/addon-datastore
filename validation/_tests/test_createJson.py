#!/usr/bin/env python

# Copyright (C) 2022 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import unittest
import os
import shutil
import json
from _validate import (
	createJson,
	addonManifest
)

TOP_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_DIR = os.path.dirname(TOP_DIR)
INPUT_DATA_PATH = os.path.join(SOURCE_DIR, '_tests', 'testData')
VALID_JSON = os.path.join(
	INPUT_DATA_PATH,
	"addons",
	"fake",
	"13.0.0.json"
)  # json file available in testData/fake
ADDON_PACKAGE = os.path.join(INPUT_DATA_PATH, 'fake.nvda-addon')
MANIFEST_FILE = os.path.join(INPUT_DATA_PATH, 'manifest.ini')
ADDON_CHANNEL = "testChannel"
ADDON_PUBLISHER = "testPublisher"
ADDON_SOURCE_URL = "https://example.com/"

OUTPUT_DATA_PATH = os.path.join(SOURCE_DIR, '_tests', 'testOutput')
OUTPUT_DIR = os.path.join(OUTPUT_DATA_PATH, "createJsonOutput")


def getAddonManifest():
	with open(MANIFEST_FILE) as f:
		manifest = addonManifest.AddonManifest(f)
	return manifest


class IntegrationTestCreateJson(unittest.TestCase):
	""" Integration tests.
	- The JSON file is created (written to the filesystem).
	- The output is then loaded and checked for correctness.
	"""
	def setUp(self):
		self.maxDiff = None
		if os.path.isdir(OUTPUT_DIR):
			shutil.rmtree(OUTPUT_DIR)

	def test_contentsMatchesExampleFile(self):
		# Values used must match the manifest files:
		# - '_tests / testData / manifest.ini'
		# - '_tests/testData/fake.nvda-addon' (unzip)
		createJson.generateJsonFile(
			ADDON_PACKAGE,
			OUTPUT_DIR,
			channel="stable",
			publisher="Name of addon author or organisation",
			sourceUrl="https://github.com/nvaccess/dont/use/this/address",
			url="https://github.com/nvaccess/dont/use/this/address/fake.nvda-addon",
			licenseName="GPL v2",
			licenseUrl="https://www.gnu.org/licenses/gpl-2.0.html",
		)
		actualJsonPath = os.path.join(OUTPUT_DIR, "fake", "13.0.0.json")
		self.assertTrue(
			os.path.isfile(actualJsonPath),
			f"Failed to create json file: {actualJsonPath}"
		)
		self._assertJsonFilesEqual(actualJsonPath=actualJsonPath, expectedJsonPath=VALID_JSON)

	def _assertJsonFilesEqual(self, actualJsonPath: str, expectedJsonPath: str):

		# Not equal, how are they different?
		with open(VALID_JSON) as expectedFile:
			expectedJson = json.load(expectedFile)
			del expectedJson["sha256-comment"]  # remove explanatory comment
		with open(actualJsonPath) as actualFile:
			actualJson = json.load(actualFile)

		self.assertDictEqual(actualJson, expectedJson)

#
# class CreateJson(unittest.TestCase):
#
# 	def test_validId(self):
# 		submissionId = self.createdSubmission["addonId"]
# 		name = self.manifest["name"]
# 		self.assertEqual(submissionId, name, f"addonId in json file should be {name}")
#
# 	def test_validDisPlayName(self):
# 		submissionDisplayName = self.createdSubmission["displayName"]
# 		summary = self.manifest["summary"]
# 		self.assertEqual(submissionDisplayName, summary, f"displayName in json file should be {summary}")
#
# 	def test_validDescription(self):
# 		submissionDescription = self.createdSubmission["description"]
# 		description = self.manifest["description"]
# 		self.assertEqual(submissionDescription, description, f"description in json file should be {description}")
#
# 	def test_validVersionName(self):
# 		submissionVersionName = self.createdSubmission["addonVersionName"]
# 		version = self.manifest["version"]
# 		self.assertEqual(submissionVersionName, version, f"addonVersionName in json file should be {version}")
#
# 	def test_validHomepage(self):
# 		submissionHomepage = self.createdSubmission["homepage"]
# 		url = self.manifest["url"]
# 		self.assertEqual(submissionHomepage, url, f"homepage in json file should be {url}")
#
# 	def test_validSha256(self):
# 		submissionSha256 = self.createdSubmission["sha256"]
# 		sha256 = createJson.getSha256(ADDON_PACKAGE)
# 		self.assertEqual(submissionSha256, sha256, f"sha256 in json file should be {sha256}")
#
# 	def test_validChannel(self):
# 		submissionChannel = self.createdSubmission["channel"]
# 		self.assertEqual(submissionChannel, ADDON_CHANNEL, f"channel in json file should be {ADDON_CHANNEL}")
#
# 	def test_validPublisher(self):
# 		submissionPublisher = self.createdSubmission["publisher"]
# 		self.assertEqual(
# 			submissionPublisher, ADDON_PUBLISHER, f"publisher in json file should be {ADDON_PUBLISHER}"
# 		)
#
# 	def test_validSourceUrl(self):
# 		submissionSourceUrl = self.createdSubmission["sourceURL"]
# 		self.assertEqual(
# 			submissionSourceUrl, ADDON_SOURCE_URL, f"sourceURL in json file should be {ADDON_SOURCE_URL}"
# 		)
#
# 	def test_validDownloadUrl(self):
# 		submissionDownloadUrl = self.createdSubmission["URL"]
# 		self.assertEqual(
# 			submissionDownloadUrl, ADDON_DOWNLOAD_URL, f"URL in json file should be {ADDON_DOWNLOAD_URL}"
# 		)
#
# 	def test_validVersionNumber(self):
# 		addonVersionNumber = self.createdSubmission["addonVersionNumber"]
# 		versionNumber = createJson.getVersionNumber(self.manifest["version"])
# 		expectedVersionNumber = {
# 			"major": versionNumber.major,
# 			"minor": versionNumber.minor,
# 			"patch": versionNumber.patch
# 		}
# 		self.assertDictEqual(
# 			addonVersionNumber, expectedVersionNumber,
# 			f"addonVersionNumber in json file  should be {expectedVersionNumber}"
# 		)
#
# 	def test_validVersionNumber_date(self):
# 		self.assertEqual(
# 			createJson.getVersionNumber("2022.07.10"),
# 			createJson.Version(
# 				major=2022,
# 				minor=7,
# 				patch=10
# 			)
# 		)
#
# 	def test_validMinVersion(self):
# 		minVersion = self.createdSubmission["minNVDAVersion"]
# 		versionNumber = createJson.getVersionNumber(self.manifest["minimumNVDAVersion"])
# 		expectedVersionNumber = {
# 			"major": versionNumber.major,
# 			"minor": versionNumber.minor,
# 			"patch": versionNumber.patch
# 		}
# 		self.assertDictEqual(
# 			minVersion, expectedVersionNumber, f"minNVDAVersion in json file  should be {expectedVersionNumber}"
# 		)
#
# 	def test_validLastTestedVersion(self):
# 		lastTestedVersion = self.createdSubmission["lastTestedVersion"]
# 		versionNumber = createJson.getVersionNumber(self.manifest["lastTestedNVDAVersion"])
# 		expectedVersionNumber = {
# 			"major": versionNumber.major,
# 			"minor": versionNumber.minor,
# 			"patch": versionNumber.patch
# 		}
# 		self.assertDictEqual(
# 			lastTestedVersion, expectedVersionNumber,
# 			f"lastTestedVersion in json file  should be {expectedVersionNumber}"
# 		)
#
# 	def test_validLicense(self):
# 		submissionLicense = self.createdSubmission["license"]
# 		validLicense = self.validSubmission["license"]
# 		self.assertEqual(submissionLicense, validLicense, f"license in json file should be {validLicense}")
#
# 	def test_validLicenseUrl(self):
# 		submissionLicenseUrl = self.createdSubmission["licenseURL"]
# 		validLicenseUrl = self.validSubmission["licenseURL"]
# 		self.assertEqual(
# 			submissionLicenseUrl, validLicenseUrl,
# 			f"licenseURL in json file should be {validLicenseUrl}"
# 		)
#
# 	def deletedSha256Comment(self):
# 		self.assertNone(
# 			self.createdSubmission.get("sha256-comment"), "sha256-comment should be deleted from json file"
# 		)
#
#
# class Valid_VersionNumber(unittest.TestCase):
# 	def setUp(self):
# 		self.singleDigitVersion = "1"
# 		self.doubleDigitVersion = "1.02"
# 		self.tripleDigitVersion = "1.2.3"
# 		self.longVersion = "1.2.3.4"
# 		self.versionWithNonDigit = "1.2.3a"
# 		self.versionNumber = createJson.Version(1, 2, 0)
#
# 	def tearDown(self):
# 		self.singleDigitVersion = None
# 		self.doubleDigitVersion = None
# 		self.tripleDigitVersion = None
# 		self.longVersion = None
# 		self.versionWithNonDigit = None
# 		self.versionNumber = None
#
# 	def test_singleDigitVersion(self):
# 		with self.assertRaises(ValueError):
# 			createJson.getVersionNumber(self.singleDigitVersion)
#
# 	def test_doubleDigitVersion(self):
# 		versionNumber = createJson.getVersionNumber(self.doubleDigitVersion)
# 		self.assertEqual(versionNumber.major, 1)
# 		self.assertEqual(versionNumber.minor, 2)
# 		self.assertEqual(versionNumber.patch, 0)
#
# 	def test_TripleDigitVersion(self):
# 		versionNumber = createJson.getVersionNumber(self.tripleDigitVersion)
# 		self.assertEqual(versionNumber.major, 1)
# 		self.assertEqual(versionNumber.minor, 2)
# 		self.assertEqual(versionNumber.patch, 3)
#
# 	def test_LongVersion(self):
# 		with self.assertRaises(ValueError):
# 			createJson.getVersionNumber(self.longVersion)
#
# 	def test_versionWithNonDigit(self):
# 		with self.assertRaises(ValueError):
# 			createJson.getVersionNumber(self.versionWithNonDigit)
#
# 	def test_fullQualifiedName(self):
# 		fullQualifiedName = createJson.getFullQualifiedName(self.versionNumber)
# 		self.assertEqual(fullQualifiedName, "1.2.0", "Full qualified name should be 1.2.0")
