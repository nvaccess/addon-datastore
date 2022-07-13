# Copyright (C) 2022 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import os
import zipfile
from addonManifest import AddonManifest
import tempfile
TEMP_DIR = tempfile.gettempdir()


def getAddonManifest(addonPath: str) -> AddonManifest:
	""" Extract manifest.ini from *.nvda-addon and parse.
	Raise on error.
	"""
	expandedPath = os.path.join(TEMP_DIR, "nvda-addon")
	with zipfile.ZipFile(addonPath, "r") as z:
		for info in z.infolist():
			z.extract(info, expandedPath)
	filePath = os.path.join(expandedPath, "manifest.ini")
	try:
		manifest = AddonManifest(filePath)
		return manifest
	except Exception as err:
		raise err
