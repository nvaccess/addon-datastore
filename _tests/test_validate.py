import unittest
import os
import json
from _tools import validate
from . import SOURCE_DIR
from jsonschema import exceptions

TEMPLATE_FILE = os.path.join(SOURCE_DIR, "_tools", "21.02.json")
JSONSCHEMA = validate.JSON_SCHEMA


def getTemplateData():
	with open(TEMPLATE_FILE) as f:
		data = json.load(f)
	return data

class TestValidate(unittest.TestCase):

	def setUp(self):
		self.data = getTemplateData()

	def tearDown(self):
		self.data = None

	def test_validateJson(self):
		data = self.data
		data["description"] = 20
		assert(validate.ValidateJson(self.data))

