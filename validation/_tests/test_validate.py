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

	def tearDown(self):
		self.data = None
		self.manifest = None

	def test_getAddonMetadata(self):
		self.assertEqual(validate.getAddonMetadata(JSON_FILE), self.data)

	def test_validateJson(self):
		self.assertTrue(validate.validateJson(self.data))

	def test_validateSha256(self):
		self.assertTrue(validate.validateSha256(MANIFEST_FILE, self.data))

	def test_validateManifest(self):
		self.assertTrue(validate.validateManifest(self.manifest, self.data, JSON_FILE))
