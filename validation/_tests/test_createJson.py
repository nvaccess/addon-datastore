#!/usr/bin/env python

# Copyright (C) 2022-2024 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import unittest
import os
import shutil
import json
from _validate import (
	createJson,
	addonManifest,
	manifestLoader
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


def getAddonManifest():
	with open(MANIFEST_FILE, encoding="utf-8") as f:
		manifest = addonManifest.AddonManifest(f)
	return manifest


class IntegrationTestCreateJson(unittest.TestCase):
	""" Integration tests.
	- The JSON file is created (written to the filesystem).
	- The output is then loaded and checked for correctness.
	"""
	def setUp(self):
		self.outputDir = os.path.join(OUTPUT_DATA_PATH, "createJsonOutput")
		self.maxDiff = None  # Permit unittest.TestCase (base class) to calculate diffs of any lengths.
		if os.path.isdir(self.outputDir):
			shutil.rmtree(self.outputDir)

	def test_contentsMatchesExampleFile(self):
		# Values used must match the manifest files:
		# - '_tests / testData / manifest.ini'
		# - '_tests/testData/fake.nvda-addon' (unzip)
		manifest = getAddonManifest()
		createJson.generateJsonFile(
			manifest,
			ADDON_PACKAGE,
			self.outputDir,
			channel="stable",
			publisher="Name of addon author or organisation",
			sourceUrl="https://github.com/nvaccess/dont/use/this/address",
			url="https://github.com/nvaccess/dont/use/this/address/fake.nvda-addon",
			licenseName="GPL v2",
			licenseUrl="https://www.gnu.org/licenses/gpl-2.0.html",
		)
		actualJsonPath = os.path.join(self.outputDir, "fake", "13.0.0.json")
		self.assertTrue(
			os.path.isfile(actualJsonPath),
			f"Failed to create json file: {actualJsonPath}"
		)
		self._assertJsonFilesEqual(actualJsonPath=actualJsonPath, expectedJsonPath=VALID_JSON)

	def _assertJsonFilesEqual(self, actualJsonPath: str, expectedJsonPath: str):

		# Not equal, how are they different?
		with open(VALID_JSON, encoding="utf-8") as expectedFile:
			expectedJson = json.load(expectedFile)
			del expectedJson["sha256-comment"]  # remove explanatory comment
		with open(actualJsonPath, encoding="utf-8") as actualFile:
			actualJson = json.load(actualFile)
			del actualJson["submissionTime"]  # remove submission time

		self.assertDictEqual(actualJson, expectedJson)


class Test_buildOutputFilePath(unittest.TestCase):
	def setUp(self) -> None:
		self.outputDir = os.path.join(OUTPUT_DATA_PATH, "test_buildOutputFilePath")
		if os.path.isdir(self.outputDir):
			shutil.rmtree(self.outputDir)

	def test_validVersion(self):
		outputFilePath = createJson.buildOutputFilePath(
			data={
				"addonId": "testId",
				"addonVersionNumber": {
					"major": 1,
					"minor": 2,
					"patch": 0,
				}
			},
			parentDir=self.outputDir
		)

		dir, filename = os.path.split(outputFilePath)
		self.assertTrue(os.path.isdir(dir), msg="Directory must exist.")
		self.assertEqual(
			filename,
			"1.2.0.json",
			msg="Name of the output file should be named based on version number"
		)


class Test_normalizeLanguage(unittest.TestCase):
	"""Set of unit tests for `manifestLoader.normalizeLanguage`."""

	def test_normalization_no_country_info(self):
		"""Makes sure that if no country info is provided language is normalized to lower case."""
		self.assertEqual("en", manifestLoader.normalizeLanguage("en"))
		self.assertEqual("en", manifestLoader.normalizeLanguage("EN"))
		self.assertEqual("kmr", manifestLoader.normalizeLanguage("kmr"))

	def test_underscore_used_as_separator_after_normalization(self):
		"""Ensures that underscore is used to separate country info from language.
		Also implicitly test the fact that country code is converted to upper case."""
		self.assertEqual("pt_BR", manifestLoader.normalizeLanguage("pt_BR"))
		self.assertEqual("pt_BR", manifestLoader.normalizeLanguage("pt-BR"))
