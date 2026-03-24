# Copyright (C) 2021 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from src.transform.datastructures import Addon, MajorMinorPatch


def MockAddon() -> Addon:
	"""Mocks the creation of an Addon. Specific required data for testing should be overwritten.
	An instance of a dataclass, e.g. Addon, can't be created without providing all the required fields.
	This strategy is based on the discussion here: https://bugs.python.org/issue36580
	"""
	return Addon(
		addonId="mock-addon",
		addonVersion=MajorMinorPatch(0, 0, 0),
		pathToData="mock-path",
		channel="stable",
		minNvdaAPIVersion=MajorMinorPatch(0, 0, 0),
		lastTestedVersion=MajorMinorPatch(0, 0, 0),
		translations=[],
	)
