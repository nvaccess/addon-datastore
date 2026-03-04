# Copyright (C) 2021 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from src.transform.datastructures import MajorMinorPatch
import unittest


class TestMajorMinorPatch(unittest.TestCase):
	def test_compare(self):
		"""Test comparing versions"""
		self.assertLess(MajorMinorPatch(13, 2), MajorMinorPatch(13, 2, 1))
		self.assertGreater(MajorMinorPatch(3, 2, 1), MajorMinorPatch(1, 2, 3))

	def test_patch_optional(self):
		"""Test that the patch number is optional and 0 by default"""
		self.assertEqual(MajorMinorPatch(13, 2, 0), MajorMinorPatch(13, 2))

	def test_toStr(self):
		"""Test converting versions to string"""
		self.assertEqual(str(MajorMinorPatch(1, 3, 4)), "1.3.4")
		self.assertEqual(str(MajorMinorPatch(13, 2, 0)), "13.2.0")
	
	def test_toStr_patch_optional(self):
		"""Confirm that versions as string always include the patch number, 0 by default.
		
		Even if the patch isn't specified, it should be included
		so that the output is consistent - e.g. /views/2021.1.3/stable.json"""
		self.assertEqual(str(MajorMinorPatch(13, 2)), "13.2.0")
	
	def test_fromDict(self):
		"""Test creating versions from dictionaries"""
		self.assertEqual(MajorMinorPatch(2, 3, 4), MajorMinorPatch(**{
			"major": 2,
			"minor": 3,
			"patch": 4,
		}))
		self.assertEqual(MajorMinorPatch(2, 3, 0), MajorMinorPatch(**{
			"major": 2,
			"minor": 3,
			"patch": 0,
		}))

	def test_fromDict_patch_optional(self):
		"""Test creating versions from dictionaries where the patch is not supplied"""
		self.assertEqual(MajorMinorPatch(2, 3, 0), MajorMinorPatch(**{
			"major": 2,
			"minor": 3,
		}))

	def test_fromDict_throws(self):
		"""Test creating versions from invalid dictionaries"""
		with self.assertRaises(TypeError):
			MajorMinorPatch(**{
				"patch": 2,
				"minor": 2,
			})
		with self.assertRaises(TypeError):
			MajorMinorPatch(**{
				"major": 2,
				"patch": 2,
			})
