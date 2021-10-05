# Copyright (C) 2021 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from enum import Enum
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import os
import typing


JsonObjT = typing.Dict[str, typing.Any]


class JSONSchemaPaths(str, Enum):
	ADDON_DATA = os.path.join(os.path.dirname(__file__), "addon_data.schema.json")
	NVDA_VERSIONS = os.path.join(os.path.dirname(__file__), "nvdaAPIVersions.schema.json")


def validateJson(data: JsonObjT, schemaPath: str) -> None:
	""" Ensure that the loaded metadata conforms to the schema.
	Raise error if not.
	"""
	with open(schemaPath) as f:
		schema = json.load(f)
	try:
		validate(instance=data, schema=schema)
	except ValidationError as err:
		raise err
