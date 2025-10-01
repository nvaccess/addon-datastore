# Copyright (C) 2022-2025 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from io import StringIO, TextIOBase
from typing import Any, cast

from configobj import ConfigObj
from configobj.validate import Validator, ValidateError

from .majorMinorPatch import MajorMinorPatch

ApiVersionT = tuple[int, int, int]  # major, minor, patch


class AddonManifest(ConfigObj):
	"""From the NVDA addonHandler module. Should be kept in sync.
	Add-on manifest file. It contains metadata about an NVDA add-on package."""

	configspec = ConfigObj(
		StringIO(
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

		""",
		),
	)

	def __init__(self, input: str | TextIOBase, translatedInput: str | None = None):
		"""
		Constructs an :class:`AddonManifest` instance from manifest string data.

		:param input: data to read the manifest information. Can be a filename or a file-like object.
		:param translatedInput: translated manifest input
		"""
		super().__init__(  # type: ignore[reportUnknownMemberType]
			input,
			configspec=self.configspec,
			encoding="utf-8",
			default_encoding="utf-8",
		)
		self._errors: str | None = None
		validator = Validator({"apiVersion": validate_apiVersionString})
		result = self.validate(validator, copy=True, preserve_errors=True)  # type: ignore[reportUnknownMemberType]
		if result is not True:
			self._errors = result
		elif self._validateApiVersionRange() is not True:
			self._errors = "Constraint not met: minimumNVDAVersion ({}) <= lastTestedNVDAVersion ({})".format(
				cast(ApiVersionT, self.get("minimumNVDAVersion")),  # type: ignore[reportUnknownMemberType]
				cast(ApiVersionT, self.get("lastTestedNVDAVersion")),  # type: ignore[reportUnknownMemberType]
			)
		self._translatedConfig = None
		if translatedInput is not None:
			self._translatedConfig = ConfigObj(translatedInput, encoding="utf-8", default_encoding="utf-8")
			for key in ("summary", "description"):
				val: str = self._translatedConfig.get(key)  # type: ignore[reportUnknownMemberType]
				if val:
					self[key] = val

	@property
	def errors(self) -> str | None:
		return self._errors

	def _validateApiVersionRange(self) -> bool:
		lastTested = cast(ApiVersionT, self.get("lastTestedNVDAVersion"))  # type: ignore[reportUnknownMemberType]
		minRequiredVersion = cast(ApiVersionT, self.get("minimumNVDAVersion"))  # type: ignore[reportUnknownMemberType]
		return minRequiredVersion <= lastTested


def validate_apiVersionString(value: str | Any) -> ApiVersionT:
	"""From the NVDA addonHandler module. Should be kept in sync."""
	if not value or value == "None":
		return (0, 0, 0)
	if not isinstance(value, str):
		raise ValidateError(
			"Expected an apiVersion in the form of a string. "
			f"e.g. '2019.1.0' instead of {value} (type {type(value)})",
		)
	try:
		versionParsed = MajorMinorPatch.getFromStr(value)
		return (versionParsed.major, versionParsed.minor, versionParsed.patch)
	except ValueError as e:
		raise ValidateError('"{}" is not a valid API Version string: {}'.format(value, e))
