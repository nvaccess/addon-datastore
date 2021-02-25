#!/usr/bin/env python

import unittest
import os
import json
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

	def test_getDownloadUrlErrors(self):
		url = self.data["URL"]
		errors = validate.getDownloadUrlErrors(url)
		self.assertEqual(len(errors), 0)
		url = self.badValue
		errors = validate.getDownloadUrlErrors(url
		self.assertNotEqual(len(errors), 0)

	def test_getSummaryErrors(self
		errors = validate.getSummaryErrors(self.manifest, self.data)
		self.assertEqual(len(errors), 0)
		data = self.data
		data["name"] = self.badValue
		errors = validate.getSummaryErrors(self.manifest, data)
		self.assertNotEqual(len(errors), 0)

	def test_getDescriptionErrors(self
		errors = validate.getDescriptionErrors(self.manifest, self.data)
		self.assertEqual(len(errors), 0)
		data = self.data
		data["description"] = self.badValue
		errors = validate.getDescriptionErrors(self.manifest, data)
		self.assertNotEqual(len(errors), 0)

