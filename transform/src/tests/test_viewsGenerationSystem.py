# Copyright (C) 2021-2026 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

"""
Runs the dataView generation system on test data.
Creates a number of specific scenarios for running the transformation.
"""

from dataclasses import dataclass
from enum import Enum
import json
import glob
from logging import getLogger
import os
from pathlib import Path
import re
import shutil
import textwrap
from src.transform.datastructures import MajorMinorPatch
import subprocess
import unittest

log = getLogger()

versionNumRegex = re.compile(r"([0-9]+)\.([0-9]+)\.([0-9]+)")

TRANSFORM_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class DATA_DIR(str, Enum):
	ROOT = os.path.join(os.path.dirname(__file__), "test_data")
	INPUT = os.path.join(ROOT, "input")
	OUTPUT = os.path.join(ROOT, "output")
	nvdaAPIVersionsPath = os.path.join(TRANSFORM_ROOT, "nvdaAPIVersions.json")


@dataclass
class InputAddonVersion:
	path: str
	addonDataBlob: str


@dataclass
class ExpectedAddonVersion:
	path: str
	addonVersion: str
	targetPath: str | None = None


def addonJson(path: str, channel: str, *, required: str, tested: str) -> InputAddonVersion:
	"""
	path should be of the form: `addonName/addonVersionString.json`, eg `nvdaOcr/13.1.0.json`
	All version strings should be of the form major.minor.patch.

	required is the minNVDAVersion as a version string
	tested is the lastTestedVersion as a version string
	"""
	pathRegex = re.compile(r"^(?P<addonId>[A-Za-z0-9]+)/(?P<version>[0-9]+\.[0-9]+\.[0-9]+)\.json$")
	pathMatch = pathRegex.match(path)
	if pathMatch is None:
		raise ValueError(f"Invalid addon path format: {path}")
	addonId = pathMatch.group("addonId")
	addonVersionStr = pathMatch.group("version")

	addonVersion = versionNumRegex.match(addonVersionStr)
	minVersion = versionNumRegex.match(required)
	testedVersion = versionNumRegex.match(tested)
	if addonVersion is None:
		raise ValueError(f"Invalid addon version format: {addonVersionStr}")
	if minVersion is None:
		raise ValueError(f"Invalid required version format: {required}")
	if testedVersion is None:
		raise ValueError(f"Invalid tested version format: {tested}")

	return InputAddonVersion(
		path,
		f'''
	{{
		"addonId": "{addonId}",
		"channel": "{channel}",
		"addonVersionNumber": {{
			"major": {addonVersion.group(1)},
			"minor": {addonVersion.group(2)},
			"patch": {addonVersion.group(3)}
		}},
		"minNVDAVersion": {{
			"major": {minVersion.group(1)},
			"minor": {minVersion.group(2)},
			"patch": {minVersion.group(3)}
		}},
		"lastTestedVersion": {{
			"major": {testedVersion.group(1)},
			"minor": {testedVersion.group(2)},
			"patch": {testedVersion.group(3)}
		}}
	}}\n''',
	)


def write_addons(*addons: InputAddonVersion):
	"""Write mock addon data to the input directory.
	Arguments should be tuples of the form (path, addonDataBlob)"""
	for addon in addons:
		addonWritePath = os.path.join(DATA_DIR.INPUT.value, addon.path)
		Path(os.path.dirname(addonWritePath)).mkdir(parents=True, exist_ok=True)
		with open(addonWritePath, "w") as addonFile:
			addonFile.write(addon.addonDataBlob)


class TestTransformation(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		"""Empty the test data before the start of tests"""
		if Path(DATA_DIR.ROOT.value).exists():
			shutil.rmtree(DATA_DIR.ROOT.value)

	def tearDown(self):
		"""Empty the test data after each test"""
		if Path(DATA_DIR.ROOT.value).exists():
			shutil.rmtree(DATA_DIR.ROOT.value)

	def runTransformation(self, *, expectFailure: bool = False) -> subprocess.CompletedProcess[bytes]:
		"""
		Runs the transformation.
		When expectFailure is False, raises AssertionError with rich diagnostics on failure.
		When expectFailure is True, raises CalledProcessError on failure.
		"""
		command = (
			f"python -m src.transform {DATA_DIR.nvdaAPIVersionsPath.value}"
			f" {DATA_DIR.INPUT.value} {DATA_DIR.OUTPUT.value}"
		)
		transformProcess = subprocess.run(
			command,
			shell=True,
			cwd=TRANSFORM_ROOT,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)
		if transformProcess.returncode != 0:
			stdout = (transformProcess.stdout or b"").decode("utf-8", errors="replace")
			stderr = (transformProcess.stderr or b"").decode("utf-8", errors="replace")
			debugContext = textwrap.dedent(
				f"""

				--- transform subprocess debug ---
				exitCode: {transformProcess.returncode}
				cwd: {TRANSFORM_ROOT}
				command: {command}
				nvdaAPIVersionsPath: {DATA_DIR.nvdaAPIVersionsPath.value}
				inputPath: {DATA_DIR.INPUT.value}
				outputPath: {DATA_DIR.OUTPUT.value}
				stdout:
				{stdout}
				stderr:
				{stderr}
				--- end transform subprocess debug ---
				""",
			)
			if expectFailure:
				raise subprocess.CalledProcessError(
					transformProcess.returncode,
					command,
					output=transformProcess.stdout,
					stderr=transformProcess.stderr,
				)
			raise AssertionError(debugContext)
		return transformProcess

	def test_transform_empty(self):
		"""Confirms an empty transformation exits with a zero exit code (successful)."""
		self.runTransformation()

	def test_transform_successfully(self):
		"""Confirms a transformation of a single addon exits with a zero exit code (successful)."""
		write_addons(addonJson("foo/0.1.1.json", "stable", required="2020.1.0", tested="2020.1.0"))
		self.runTransformation()

	def test_throw_error_on_nonempty_output_folder(self):
		"""Confirms using an existing output directory throws an error"""
		# Make the folder before transform
		Path(DATA_DIR.OUTPUT.value).mkdir(parents=True, exist_ok=True)
		with self.assertRaises(subprocess.CalledProcessError) as transformError:
			self.runTransformation(expectFailure=True)

		doubleEscapedDir = DATA_DIR.OUTPUT.value.replace(
			"\\",
			"\\\\",
		)  # stderr escapes all the backslashes twice
		self.assertIn(
			"FileExistsError: [WinError 183] Cannot create a file when that file already exists: "
			f"'{doubleEscapedDir}'",
			# requires that runTransformation and child processes log errors to stderr
			transformError.exception.stderr.decode("utf-8"),
		)

	def _assertAddonDataWritten(self, *expectedAddons: ExpectedAddonVersion):
		"""Confirms that an addon is written to a path and the file contains an expected version.
		Arguments should be tuples of the form (expectedPathToAddon, expectedAddonVersionStr)"""
		self.assertEqual(
			len(glob.glob(f"{DATA_DIR.OUTPUT.value}/**/**.json", recursive=True)),
			len(expectedAddons),
		)
		for expectedAddon in expectedAddons:
			fullPathToAddon = os.path.join(DATA_DIR.OUTPUT.value, expectedAddon.path)
			self.assertTrue(Path(fullPathToAddon).exists())
			if expectedAddon.targetPath is not None:
				targetPath = os.path.join(DATA_DIR.OUTPUT.value, expectedAddon.targetPath)
				self.assertTrue(os.path.islink(fullPathToAddon))
				self.assertEqual(
					os.path.normpath(os.path.realpath(fullPathToAddon)),
					os.path.normpath(os.path.realpath(targetPath)),
				)
			with open(fullPathToAddon, "r") as expectedAddonFile:
				addonData = json.load(expectedAddonFile)
			addonVersion = MajorMinorPatch(**addonData["addonVersionNumber"])
			self.assertEqual(expectedAddon.addonVersion, str(addonVersion))

	def test_output_file_structure_matches_expected(self):
		"""Confirms that a transform of multiple addon versions is written as expected.
		Cases include:
		  - Multiple addons
		  - Multiple NVDA API versions
		  - A beta addon
		  - A newer version of an addon which overrides an older version for the same NVDA API version
		"""
		write_addons(
			addonJson("oldNewAddon/2.1.0.json", "stable", required="2020.2.0", tested="2020.3.0"),
			addonJson("oldNewAddon/13.0.0.json", "stable", required="2020.3.0", tested="2020.4.0"),
			addonJson("betaStableAddon/0.0.1.json", "stable", required="2020.4.0", tested="2020.4.0"),
			addonJson("betaStableAddon/0.0.2.json", "beta", required="2020.4.0", tested="2020.4.0"),
		)
		self.runTransformation()
		self._assertAddonDataWritten(
			ExpectedAddonVersion("addons/oldNewAddon/2.1.0/en.json", "2.1.0"),
			ExpectedAddonVersion("addons/oldNewAddon/13.0.0/en.json", "13.0.0"),
			ExpectedAddonVersion("addons/betaStableAddon/0.0.1/en.json", "0.0.1"),
			ExpectedAddonVersion("addons/betaStableAddon/0.0.2/en.json", "0.0.2"),
			ExpectedAddonVersion(
				"views/en/2020.2.0/oldNewAddon/stable.json",
				"2.1.0",
				targetPath="addons/oldNewAddon/2.1.0/en.json",
			),
			ExpectedAddonVersion(
				"views/en/2020.3.0/oldNewAddon/stable.json",
				"13.0.0",
				targetPath="addons/oldNewAddon/13.0.0/en.json",
			),
			ExpectedAddonVersion(
				"views/en/2020.4.0/oldNewAddon/stable.json",
				"13.0.0",
				targetPath="addons/oldNewAddon/13.0.0/en.json",
			),
			ExpectedAddonVersion(
				"views/en/2020.4.0/betaStableAddon/stable.json",
				"0.0.1",
				targetPath="addons/betaStableAddon/0.0.1/en.json",
			),
			ExpectedAddonVersion(
				"views/en/2020.4.0/betaStableAddon/beta.json",
				"0.0.2",
				targetPath="addons/betaStableAddon/0.0.2/en.json",
			),
			ExpectedAddonVersion(
				"views/en/latest/betaStableAddon/beta.json",
				"0.0.2",
				targetPath="addons/betaStableAddon/0.0.2/en.json",
			),
			ExpectedAddonVersion(
				"views/en/latest/betaStableAddon/stable.json",
				"0.0.1",
				targetPath="addons/betaStableAddon/0.0.1/en.json",
			),
			ExpectedAddonVersion(
				"views/en/latest/oldNewAddon/stable.json",
				"13.0.0",
				targetPath="addons/oldNewAddon/13.0.0/en.json",
			),
		)

	def test_translation_view_symlink_points_to_translated_addon_data(self):
		"""Confirms language-specific views symlink to translated addon data files."""
		write_addons(
			InputAddonVersion(
				"UIANotificationSwitch/2026.1.0.json",
				"""
{
	"addonId": "UIANotificationSwitch",
	"displayName": "UIA Notification Switch",
	"description": "English description",
	"channel": "stable",
	"addonVersionNumber": {
		"major": 2026,
		"minor": 1,
		"patch": 0
	},
	"minNVDAVersion": {
		"major": 2019,
		"minor": 1,
		"patch": 0
	},
	"lastTestedVersion": {
		"major": 2019,
		"minor": 1,
		"patch": 0
	},
	"translations": [
		{
			"language": "ar",
			"displayName": "مفتاح إشعارات UIA",
			"description": "وصف عربي"
		}
	]
}
""",
			),
		)
		self.runTransformation()
		self._assertAddonDataWritten(
			ExpectedAddonVersion("addons/UIANotificationSwitch/2026.1.0/en.json", "2026.1.0"),
			ExpectedAddonVersion("addons/UIANotificationSwitch/2026.1.0/ar.json", "2026.1.0"),
			ExpectedAddonVersion(
				"views/ar/2019.1.0/UIANotificationSwitch/stable.json",
				"2026.1.0",
				targetPath="addons/UIANotificationSwitch/2026.1.0/ar.json",
			),
		)
