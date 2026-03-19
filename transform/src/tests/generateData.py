# Copyright (C) 2021 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from src.transform.datastructures import Addon
from unittest.mock import create_autospec, Mock


def MockAddon() -> Addon:
	"""Mocks the creation of an Addon. Specific required data for testing should be overwritten.
	An instance of a dataclass, e.g. Addon, can't be created without providing all the required fields.
	This strategy is based on the discussion here: https://bugs.python.org/issue36580
	"""
	return Mock(spec=create_autospec(Addon))()
