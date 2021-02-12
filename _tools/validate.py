#!/usr/bin/env python

# Copyright (C) 2020 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import hashlib
import argparse
import typing
import os
import json
from jsonschema import validate
#: The read size for each chunk read from the file, prevents memory overuse with large files.
JSON_SCHEMA = os.path.join(os.path.dirname(__file__), "addonVersion_schema.json")

def validateJson(jsonFile):
	with open(JSON_SCHEMA) as f:
		schema = json.load(f)
	with open(jsonFile) as f:
		data = json.load(f)
	try:
		validate(instance=data, schema=schema)
		print("Add-on metadata is valid")
	except jsonschema.exceptions.ValidationError as err:
		print(err)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		dest="file",
		help="The json (.json) file containing add-on metadata."
	)
	args = parser.parse_args()
	validateJson(args.file)

if __name__ == '__main__':
	main()
