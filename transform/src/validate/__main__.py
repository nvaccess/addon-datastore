# Copyright (C) 2021 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import argparse
import json
from .validate import validateJson

"""Validate json data file
Usage: python -m src.validate {pathToSchema} {pathToDataFile}
"""

parser = argparse.ArgumentParser()
parser.add_argument(
	dest="pathToSchema",
	help="path to the jsonschema file"
)
parser.add_argument(
	dest="pathToDataFile",
	help="The json (.json) file containing the file to be validated using the schema file"
)

args = parser.parse_args()
with open(args.pathToDataFile, "r") as jsonDataFile:
	jsonData = json.load(jsonDataFile)
validateJson(jsonData, args.pathToSchema)
