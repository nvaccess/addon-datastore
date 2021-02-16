import unittest
import os
import json
from _tools import validate

class TestValidate(unittest.TestCase):

	def setUp(self):
		self.jsonschema = validate.JSON_SCHEMA
		self.template = os.path.join(SOURCE_DIR, "_tools", "21.02.json")
		self.data = json.load(self.template)

	def tearDown(self):
		self.jsonschema = None
		self.template = None
		self.data = None

	def test_getAddonMetadata(self):
		data = validate.getAddonMetadata(self.template)
		self.assertTrue(isinstance(data, dict))
