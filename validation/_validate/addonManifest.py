#!/usr/bin/env python

# Copyright (C) 2022-2023 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import os
import sys
from typing import (
	Optional,
	TextIO,
	Tuple,
)
from io import StringIO

from configobj import ConfigObj
from configobj.validate import Validator, ValidateError

sys.path.append(os.path.dirname(__file__))
# E402 module level import not at top of file
from majorMinorPatch import MajorMinorPatch  # noqa:E402
del sys.path[-1]


class AddonManifest(ConfigObj):
	"""From the NVDA addonHandler module. Should be kept in sync.
	Add-on manifest file. It contains metadata about an NVDA add-on package. """
	configspec = ConfigObj(StringIO(
		"""
		# NVDA Add-on Manifest configuration specification
		# Add-on unique name
		# Suggested convention is lowerCamelCase.
		name = string()

		# short summary (label) of the add-on to show to users.
		summary = string()

		# Long description with further information and instructions
		description = string(default=None)

		# Name of the author or entity that created the add-on
		author = string()

		# Version of the add-on.
		# Suggested convention is <major>.<minor>.<patch> format.
		version = string()

		# The minimum required NVDA version for this add-on to work correctly.
		# Should be less than or equal to lastTestedNVDAVersion
		minimumNVDAVersion = apiVersion(default="0.0.0")

		# Must be greater than or equal to minimumNVDAVersion
		lastTestedNVDAVersion = apiVersion(default="0.0.0")

		# URL for more information about the add-on, e.g. a homepage.
		# Should begin with https://
		url = string(default=None)

		# Name of default documentation file for the add-on.
		docFileName = string(default=None)

		# NOTE: apiVersion:
		# EG: 2019.1.0 or 0.0.0
		# Must have 3 integers separated by dots.
		# The first integer must be a Year (4 characters)
		# "0.0.0" is also valid.
		# The final integer can be left out, and in that case will default to 0. E.g. 2019.1

		"""
	))

	def __init__(self, input: TextIO, translatedInput: Optional[TextIO] = None):
		""" Constructs an L{AddonManifest} instance from manifest string data
		@param input: data to read the manifest information
		@param translatedInput: translated manifest input
		"""
		super().__init__(
			input,
			configspec=self.configspec,
			encoding='utf-8',
			default_encoding='utf-8',
		)
		self._errors: Optional[str] = None
		val = Validator({"apiVersion": validate_apiVersionString})
		result = self.validate(val, copy=True, preserve_errors=True)
		if result is not True:
			self._errors = result
		elif self._validateApiVersionRange() is not True:
			self._errors = "Constraint not met: minimumNVDAVersion ({}) <= lastTestedNVDAVersion ({})".format(
				self.get("minimumNVDAVersion"),
				self.get("lastTestedNVDAVersion")
			)
		self._translatedConfig = None
		if translatedInput is not None:
			self._translatedConfig = ConfigObj(translatedInput, encoding='utf-8', default_encoding='utf-8')
			for key in ('summary', 'description'):
				val = self._translatedConfig.get(key)
				if val:
					self[key] = val

	@property
	def errors(self) -> str:
		return self._errors

	def _validateApiVersionRange(self) -> bool:
		lastTested = self.get("lastTestedNVDAVersion")
		minRequiredVersion = self.get("minimumNVDAVersion")
		return minRequiredVersion <= lastTested


def validate_apiVersionString(value: str) -> Tuple[int, int, int]:
	"""From the NVDA addonHandler module. Should be kept in sync."""
	if not value or value == "None":
		return (0, 0, 0)
	if not isinstance(value, str):
		raise ValidateError(
			"Expected an apiVersion in the form of a string. "
			f"e.g. '2019.1.0' instead of {value} (type {type(value)})"
		)
	try:
		versionParsed = MajorMinorPatch.getFromStr(value)
		return (versionParsed.major, versionParsed.minor, versionParsed.patch)
	except ValueError as e:
		raise ValidateError('"{}" is not a valid API Version string: {}'.format(value, e))
