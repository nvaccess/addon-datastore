# Copyright (C) 2021 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from copy import deepcopy

from src.transform.datastructures import MajorMinorPatch, VersionCompatibility
from src.transform.transform import getLatestAddons, _isAddonCompatible
from src.tests.generateData import MockAddon
import unittest

V_2020_1 = MajorMinorPatch(2020, 1)
V_2020_2 = MajorMinorPatch(2020, 2)
V_2020_3 = MajorMinorPatch(2020, 3)
V_2021_1 = MajorMinorPatch(2021, 1)
V_2021_1_1 = MajorMinorPatch(2021, 1, 1)
V_2021_2 = MajorMinorPatch(2021, 2)
V_2022_1 = MajorMinorPatch(2022, 1)
nvdaAPIVersion2020_2 = VersionCompatibility(V_2020_2, V_2020_1)
nvdaAPIVersion2020_3 = VersionCompatibility(V_2020_3, V_2020_1)
nvdaAPIVersion2021_1 = VersionCompatibility(V_2021_1, V_2021_1)
nvdaAPIVersion2021_2 = VersionCompatibility(V_2021_2, V_2021_1)
nvdaAPIVersion2022_1 = VersionCompatibility(V_2022_1, V_2022_1)


class Test_isAddonCompatible(unittest.TestCase):
	def test_valid_with_api(self):
		"""Confirm an addon is compatible with a fully tested API"""
		addon = MockAddon()
		addon.minNvdaAPIVersion = V_2020_1
		addon.lastTestedVersion = V_2020_2
		self.assertTrue(_isAddonCompatible(addon, nvdaAPIVersion2020_2))

	def test_valid_with_backwards_compatible_api(self):
		"""Confirm an addon is compatible with a backwards compatible API"""
		addon = MockAddon()
		addon.minNvdaAPIVersion = V_2020_1
		addon.lastTestedVersion = V_2020_2
		self.assertTrue(_isAddonCompatible(addon, nvdaAPIVersion2020_3))

	def test_not_valid_because_breaking_api(self):
		"""Confirm an addon is not compatible with a breaking API"""
		addon = MockAddon()
		addon.minNvdaAPIVersion = V_2020_1
		addon.lastTestedVersion = V_2020_2
		self.assertFalse(_isAddonCompatible(addon, nvdaAPIVersion2021_1))

	def test_not_valid_because_old_api(self):
		"""Confirm an addon is not compatible with an old API"""
		addon = MockAddon()
		addon.minNvdaAPIVersion = V_2021_1
		addon.lastTestedVersion = V_2021_2
		self.assertFalse(_isAddonCompatible(addon, nvdaAPIVersion2020_3))


class Test_getLatestAddons(unittest.TestCase):
	def test_beta_stable(self):
		"""Ensure addons are added to the correct channels"""
		nvdaAPIVersions = (nvdaAPIVersion2020_2,)
		betaAddon = MockAddon()
		betaAddon.minNvdaAPIVersion = V_2020_1
		betaAddon.lastTestedVersion = V_2020_2
		betaAddon.channel = "beta"
		betaAddon.pathToData = "beta-path"  # unique identifier for addon metadata version
		betaAddon.addonVersion = MajorMinorPatch(0, 2, 1)
		stableAddon = deepcopy(betaAddon)
		stableAddon.channel = "stable"
		stableAddon.pathToData = "stable-path"  # unique identifier for addon metadata version
		self.assertDictEqual(getLatestAddons([betaAddon, stableAddon], nvdaAPIVersions), {
			V_2020_2: {"beta": {betaAddon.addonId: betaAddon}, "stable": {stableAddon.addonId: stableAddon}},
		})

	def test_addon_order_irrelevant(self):
		"""
		Confirm that the order of addons supplied does not effect the output.

		getLatestAddons checks addons in order, and we want to ensure the addon dictionary is updated to
		maintain the newest addon for a version+channel.
		"""
		nvdaAPIVersions = (nvdaAPIVersion2020_3,)
		oldAddon = MockAddon()
		oldAddon.addonId = "foo"
		oldAddon.minNvdaAPIVersion = V_2020_3
		oldAddon.lastTestedVersion = V_2020_3
		oldAddon.channel = "stable"
		oldAddon.pathToData = "old-path"
		oldAddon.addonVersion = MajorMinorPatch(0, 1)

		newAddon = deepcopy(oldAddon)
		newAddon.addonVersion = MajorMinorPatch(0, 3)
		newAddon.pathToData = "new-path"

		self.assertDictEqual(
			getLatestAddons([oldAddon, newAddon], nvdaAPIVersions),
			getLatestAddons([newAddon, oldAddon], nvdaAPIVersions)
		)

	def test_nvdaAPIVersions_order_irrelevant(self):
		"""
		Confirm that the order of API versions supplied does not effect the output.
		"""
		addon = MockAddon()
		addon.addonId = "foo"
		addon.minNvdaAPIVersion = V_2020_2
		addon.lastTestedVersion = V_2020_3
		addon.channel = "stable"
		addon.pathToData = "old-path"
		addon.addonVersion = MajorMinorPatch(0, 1)

		self.assertDictEqual(
			getLatestAddons([addon], (nvdaAPIVersion2020_3, nvdaAPIVersion2020_2)),
			getLatestAddons([addon], (nvdaAPIVersion2020_2, nvdaAPIVersion2020_3))
		)

	def test_is_backCompatTo(self):
		"""Confirm that an addon is only added if it is backwards compatible"""
		nvdaAPIVersions = (nvdaAPIVersion2021_1, nvdaAPIVersion2021_2, nvdaAPIVersion2022_1)
		addon = MockAddon()
		addon.minNvdaAPIVersion = V_2021_1
		addon.lastTestedVersion = V_2021_2
		addon.channel = "stable"
		self.assertDictEqual(getLatestAddons([addon], nvdaAPIVersions), {
			# nvdaAPIVersion.backCompatTo < addon.lastTestedVersion
			V_2021_1: {"stable": {addon.addonId: addon}, "beta": {}},

			# nvdaAPIVersion.backCompatTo == addon.lastTestedVersion
			V_2021_2: {"stable": {addon.addonId: addon}, "beta": {}},

			# nvdaAPIVersion.backCompatTo > addon.lastTestedVersion
			V_2022_1: {"stable": {}, "beta": {}},
		})

	def test_same_addon_version_throws(self):
		"""Test that two addons with the same version throws an error"""
		nvdaAPIVersions = (nvdaAPIVersion2020_2, )
		addon = MockAddon()
		addon.addonId = "foo"
		addon.minNvdaAPIVersion = V_2020_2
		addon.lastTestedVersion = V_2020_2
		addon.channel = "stable"
		addon.addonVersion = MajorMinorPatch(0, 1)
		addonCopy = deepcopy(addon)
		with self.assertRaises(ValueError):
			getLatestAddons([addon, addonCopy], nvdaAPIVersions)

	def test_is_compatible(self):
		"""Confirm that an addon is only added if it is compatible with the API"""
		nvdaAPIVersions = (nvdaAPIVersion2020_3, nvdaAPIVersion2021_1, nvdaAPIVersion2021_2)
		addon = MockAddon()
		addon.minNvdaAPIVersion = V_2021_1
		addon.lastTestedVersion = V_2021_2
		addon.channel = "stable"
		self.assertDictEqual(getLatestAddons([addon], nvdaAPIVersions), {
			# addon.minNvdaAPIVersion > nvdaAPIVersion.apiVer
			V_2020_3: {"stable": {}, "beta": {}},

			# addon.minNvdaAPIVersion == nvdaAPIVersion.apiVer
			V_2021_1: {"stable": {addon.addonId: addon}, "beta": {}},

			# addon.minNvdaAPIVersion < nvdaAPIVersion.apiVer
			V_2021_2: {"stable": {addon.addonId: addon}, "beta": {}},
		})
