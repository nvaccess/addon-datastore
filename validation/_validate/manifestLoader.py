# Copyright (C) 2022 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from glob import glob
import os
import pathlib
import shutil
from typing import Generator, Tuple
import zipfile
from addonManifest import AddonManifest
import tempfile
TEMP_DIR = tempfile.gettempdir()


def getAddonManifest(addonPath: str) -> AddonManifest:
	""" Extract manifest.ini from *.nvda-addon and parse.
	Raise on error.
	"""
	extractDir = os.path.join(TEMP_DIR, "tempAddon")
	if pathlib.Path(extractDir).exists():
		shutil.rmtree(extractDir)
	pathlib.Path(extractDir).mkdir()
	with zipfile.ZipFile(addonPath, "r") as z:
		for info in z.infolist():
			z.extract(info, extractDir)
	filePath = os.path.join(extractDir, "manifest.ini")
	try:
		manifest = AddonManifest(filePath)
		return manifest
	except Exception as err:
		raise err


def getAddonManifestLocalizations(
		manifest: AddonManifest
) -> Generator[Tuple[str, AddonManifest], None, None]:
	""" Extract data from translated manifest.ini from *.nvda-addon and parse.
	Raise on error.
	"""
	if manifest.filename is None:
		# Ignore during tests
		return
	addonFolder = pathlib.Path(manifest.filename).parent.absolute().as_posix()
	filePaths = os.path.join(addonFolder, "locale", "*", "manifest.ini")
	for translationFile in glob(filePaths):
		languageCode = pathlib.Path(translationFile).parent.name
		try:
			translatedManifest = AddonManifest(translationFile)
			yield normalizeLanguage(languageCode), translatedManifest
		except Exception:
			print(f"Error in {translationFile}")


def normalizeLanguage(lang: str) -> str:
	"""
	Normalizes a language-dialect string  into a standard form we can deal with.
	Converts any dash to underline, and makes sure that language is lowercase and dialect is uppercase.
	Based on NVDA`s `languageHandler` module.
	:param lang: A language code.
	:return: A normalized language code.
	"""
	lang = lang.replace("-", "_")
	ld = lang.split("_")
	ld[0] = ld[0].lower()
	if len(ld) >= 2:
		ld[1] = ld[1].upper()
	return "_".join(ld)
