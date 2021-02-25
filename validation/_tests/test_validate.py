#!/usr/bin/env python

# Copyright (C) 2021 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import unittest
import os
import json
from jsonschema import exceptions
from _validate import validate, addonManifest


JSON_SCHEMA = validate.JSON_SCHEMA
TOP_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.dirname(TOP_DIR)
ADDON_PATH = os.path.join(SOURCE_DIR, "clipContentsDesigner")
JSON_FILE = os.path.join(ADDON_PATH, "13.0.json")
MANIFEST_FILE = os.path.join(ADDON_PATH, "manifest.ini")


def getAddonData():
	with open(JSON_FILE) as f:
		data = json.load(f)
	return data

def getAddonManifest():
	with open(MANIFEST_FILE) as f:
		manifest = addonManifest.AddonManifest(f)
	return manifest

class TestValidate(unittest.TestCase):

	def setUp(self):
		self.data = getAddonData()
		self.manifest = getAddonManifest()
		self.badValue = "Test"

	def tearDown(self):
		self.data = None
		self.manifest = None
		self.badValue = None

	def test_getAddonMetadata(self):
		self.assertEqual(validate.getAddonMetadata(JSON_FILE), self.data)

	def test_validateJson(self):
		validate.validateJson(self.data)
		self.badValue = 3
		self.data["description"] = self.badValue
		with self.assertRaises(exceptions.ValidationError):
			validate.validateJson(self.data)

	def test_getDownloadUrlErrors(self):
		url = self.data["URL"]
		errors = validate.getDownloadUrlErrors(url)
		self.assertEqual(len(errors), 0)
		url = self.badValue
		errors = validate.getDownloadUrlErrors(url)
		self.assertEqual(len(errors), 2)
		url = "https://" + self.badValue
		errors = validate.getDownloadUrlErrors(url)
		self.assertEqual(len(errors), 1)
		url = self.badValue + ".nvda-addon"
		errors = validate.getDownloadUrlErrors(url)
		self.assertEqual(len(errors), 1)

	def test_getSha256Errors(self):
		errors = validate.getSha256Errors(MANIFEST_FILE, self.data)
		self.assertEqual(len(errors), 0)
		self.data["sha256"] = self.badValue
		errors = validate.getSha256Errors(MANIFEST_FILE, self.data)
		self.assertNotEqual(len(errors), 0)

	def test_getSummaryErrors(self):
		errors = validate.getSummaryErrors(self.manifest, self.data)
		self.assertEqual(len(errors), 0)
		self.data["name"] = self.badValue
		errors = validate.getSummaryErrors(self.manifest, self.data)
		self.assertNotEqual(len(errors), 0)

	def test_getDescriptionErrors(self):
		errors = validate.getDescriptionErrors(self.manifest, self.data)
		self.assertEqual(len(errors), 0)
		self.data["description"] = self.badValue
		errors = validate.getDescriptionErrors(self.manifest, self.data)
		self.assertNotEqual(len(errors), 0)

	def test_getNameErrors(self):
		errors = validate.getNameErrors(self.manifest, JSON_FILE)
		self.assertEqual(len(errors), 0)
		filename = os.path.join(TOP_DIR, self.badValue)
		errors = validate.getNameErrors(self.manifest, filename)
		self.assertNotEqual(len(errors), 0)

	def test_getVersionErrors(self):
		errors = validate.getVersionErrors(self.manifest, JSON_FILE)
		self.assertEqual(len(errors), 0)
		filename = os.path.join(ADDON_PATH, self.badValue)
		errors = validate.getVersionErrors(self.manifest, filename)
		self.assertNotEqual(len(errors), 0)

