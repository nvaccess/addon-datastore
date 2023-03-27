# Copyright (C) 2022-2023 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import unittest

from _validate.majorMinorPatch import MajorMinorPatch


class Test_getVersionNumber(unittest.TestCase):
	def test_tripleDigitVersion_isValid(self):
		""" Canonical version (major, minor, patch) expected.
		"""
		versionNumber = MajorMinorPatch.getFromStr("1.2.3")
		self.assertEqual(versionNumber.major, 1)
		self.assertEqual(versionNumber.minor, 2)
		self.assertEqual(versionNumber.patch, 3)

	def test_doubleDigitVersion_isValid(self):
		"""patch is optional, assumed to be zero.
		"""
		versionNumber = MajorMinorPatch.getFromStr("1.02")
		self.assertEqual(versionNumber.major, 1)
		self.assertEqual(versionNumber.minor, 2)
		self.assertEqual(versionNumber.patch, 0)

	def test_singleDigitVersion_raises(self):
		with self.assertRaises(ValueError, msg="Single digit version numbers are expected to be an error."):
			MajorMinorPatch.getFromStr("1")

	def test_tooManyValues_raises(self):
		with self.assertRaises(ValueError, msg="More than three parts is expected as an error."):
			MajorMinorPatch.getFromStr("1.2.3.4")

	def test_versionWithNonDigit(self):
		with self.assertRaises(
			ValueError,
			msg="Non-digit chars in version number expected as an error."):
			MajorMinorPatch.getFromStr("1.2.3a")
