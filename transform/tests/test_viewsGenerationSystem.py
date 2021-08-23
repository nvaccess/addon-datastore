# Copyright (C) 2021 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

"""
Runs the dataView generation system on test data.
Confirms the end result data is as expected.
Runs a number of specific checks for scenarios within the test data.
"""
import json
import glob
import os
import unittest

TEST_DATASET_0_DIR = "./tests/test_data_input/addonSet0"
TEST_DATASET_1_DIR = "./tests/test_data_input/addonSet1"
TEST_DATASET_0_EXPECTED_DIR = "./tests/test_data_results/addonSet0"
TEST_DATASET_1_EXPECTED_DIR = "./tests/test_data_results/addonSet1"
TEST_OUTPUT_DIR = "./tests/test_output"
VIEWS_GLOB = "/**/**/*.json"


class TestTransformation(unittest.TestCase):
	@classmethod
	def _execute_transformation(cls, inputPath: str, outputPath: str = TEST_OUTPUT_DIR):
		pass

	def setUp(self):
		"""
		Runs the transformation.
		"""
		self._execute_transformation(TEST_DATASET_0_DIR)

	def tearDown(self):
		"""
		Removes and empties the test_output directory
		"""
		os.remove(TEST_OUTPUT_DIR)

	def _check_expected_addons_added(self, expectedResultsPath: str):
		"""
		Checks that all the data and files in expectedResultsPath match the test output directory.
		"""
		testOutputFiles = set(glob.glob(TEST_OUTPUT_DIR + VIEWS_GLOB))
		expectedFiles = set(glob.glob(expectedResultsPath + VIEWS_GLOB))
		self.assertEqual(testOutputFiles, expectedFiles)
		for outputFilename in testOutputFiles:
			expectedFilename = outputFilename.replace(TEST_OUTPUT_DIR, expectedResultsPath)
			with open(outputFilename, "r") as outputFile:
				outputFileJson = json.loads(outputFile)
			with open(expectedFilename, "r") as expectedFile:
				expectedResultsJson = json.loads(expectedFile)
			self.assertEqual(expectedResultsJson, outputFileJson)

	def test_expected_addons_added(self):
		"""
		Confirms the initial transformation was successful.
		"""
		self._check_expected_addons_added(TEST_DATASET_0_EXPECTED_DIR)

	def test_expected_addons_updated(self):
		"""
		Confirms that a subsequent transformation is successful, and the first transformation results are
		overwritten.
		"""
		self._check_expected_addons_added(TEST_DATASET_0_EXPECTED_DIR)
		self._execute_transformation(TEST_DATASET_1_DIR)
		self._check_expected_addons_added(TEST_DATASET_1_EXPECTED_DIR)

	def test_removed_addon(self):
		"""
		Confirms that an addon that was expected to be removed after a subsequent transformation is removed.
		"""
		REMOVED_ADDON_GLOB = TEST_OUTPUT_DIR + "/**/ipsum/*.json"
		EMPTY_SET = set()
		self.assertNotEqual(set(glob.glob(REMOVED_ADDON_GLOB)), EMPTY_SET)
		self._execute_transformation(TEST_DATASET_1_DIR)
		self.assertEqual(set(glob.glob(REMOVED_ADDON_GLOB)), EMPTY_SET)

	def test_addon_version_downgraded(self):
		"""
		Confirms that a removed new addon version downgrades an older version.
		"""
		NEWER_ADDON_GLOB = TEST_OUTPUT_DIR + "/**/bar/1.1.1.json"
		OLDER_ADDON_GLOB = TEST_OUTPUT_DIR + "/**/bar/0.9.json"
		EMPTY_SET = set()
		initialOldVersionUsages = set(glob.glob(OLDER_ADDON_GLOB))
		initialUsages = set(glob.glob(NEWER_ADDON_GLOB))
		self.assertGreater(initialUsages, EMPTY_SET)
		self._execute_transformation(TEST_DATASET_1_DIR)
		self.assertEqual(set(glob.glob(NEWER_ADDON_GLOB)), EMPTY_SET)
		self.assertEqual(len(glob.glob(OLDER_ADDON_GLOB)), len(initialOldVersionUsages) + len(initialUsages))

	def test_outdated_addon_not_transformed(self):
		"""
		Confirms that an old addon version that has been fully replaced for all NVDA versions is not used.
		"""
		REPLACED_ADDON_GLOB = TEST_OUTPUT_DIR + "/**/fake/13.0.json"
		EMPTY_SET = set()
		self.assertNotEqual(set(glob.glob(REPLACED_ADDON_GLOB)), EMPTY_SET)
		self._execute_transformation(TEST_DATASET_1_DIR)
		self.assertEqual(set(glob.glob(REPLACED_ADDON_GLOB)), EMPTY_SET)
