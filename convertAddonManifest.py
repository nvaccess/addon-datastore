"""
Setup:
pip install requests configobj

Usage:
python convertAddonManifest.py [addonId] [stable|beta|dev] [addonUrl]
"""

import hashlib
from io import StringIO
import json
import os
import pathlib
import sys
import tempfile
from time import sleep
import traceback
from typing import (
	Any,
	Dict,
	NamedTuple,
	Tuple,
)
from zipfile import ZipFile, BadZipFile

import configobj
from requests import get


manifestSpec = configobj.ConfigObj(StringIO(
"""
# NVDA Add-on Manifest configuration specification
# Add-on unique name
name = string()

# short  summary (label) of the add-on to show to users.
summary = string()

# Long description with further information and instructions
description = string(default=None)

# Name of the author or entity that created the add-on
author = string()

# Version of the add-on. Should preferably in some standard format such as x.y.z
version = string()

# The minimum required NVDA version for this add-on to work correctly.
# Should be less than or equal to lastTestedNVDAVersion
minimumNVDAVersion = apiVersion(default="0.0.0")

# Must be greater than or equal to minimumNVDAVersion
lastTestedNVDAVersion = apiVersion(default="0.0.0")

# URL for more information about the add-on. New versions and such.
url= string(default=None)

# Name of default documentation file for the add-on.
docFileName = string(default=None)

# NOTE: apiVersion:
# EG: 2019.1.0 or 0.0.0
# Must have 3 integers separated by dots.
# The first integer must be a Year (4 characters)
# "0.0.0" is also valid.
# The final integer can be left out, and in that case will default to 0. E.g. 2019.1

"""))


class MajorMinorPatch(NamedTuple):
	major: int
	minor: int
	patch: int = 0

	def __str__(self) -> str:
		return f"{self.major}.{self.minor}.{self.patch}"


def createNewAddonJSON(addonId: str, channel: str, url: str, sha256: str, manifest: Dict[str, str]) -> Dict[str, Any]:
	if "minimumNVDAVersion" in manifest and not manifest["minimumNVDAVersion"] == "None":
		minimumNVDAVersionInts = [int(x) for x in manifest["minimumNVDAVersion"].split(".")]
		minimumNVDAVersion = MajorMinorPatch(*minimumNVDAVersionInts)
	else:
		minimumNVDAVersion = MajorMinorPatch(0, 0, 0)

	if "lastTestedNVDAVersion" in manifest:
		lastTestedNVDAVersionInts = [int(x) for x in manifest["lastTestedNVDAVersion"].split(".")]
		lastTestedNVDAVersion = MajorMinorPatch(*lastTestedNVDAVersionInts)
	else:
		lastTestedNVDAVersion = MajorMinorPatch(0, 0, 0)

	if lastTestedNVDAVersion > MajorMinorPatch(2023, 1, 0):
		print("Setting lastTestedNVDAVersion version to 2023.1.0")
		lastTestedNVDAVersion = MajorMinorPatch(2023, 1, 0)
	elif lastTestedNVDAVersion < MajorMinorPatch(2019, 3, 0):
		print("Setting lastTestedNVDAVersion version to 0.0.0")
		lastTestedNVDAVersion = MajorMinorPatch(0, 0, 0)

	if minimumNVDAVersion > MajorMinorPatch(2023, 1, 0):
		print("Setting minimumNVDAVersion version to 2023.1.0")
		minimumNVDAVersion = MajorMinorPatch(2023, 1, 0)
	elif minimumNVDAVersion < MajorMinorPatch(2019, 3, 0):
		print("Setting minimumNVDAVersion version to 0.0.0")
		minimumNVDAVersion = MajorMinorPatch(0, 0, 0)

	try:
		addonVersionStr = manifest["version"]
		if "-dev" in addonVersionStr:
			addonVersionStr = addonVersionStr.replace("-dev", "")
			if channel != "dev":
				print(f"addon version str for {addonId} contains dev but channel is not dev")

		if "dev" in addonVersionStr:
			addonVersionStr = addonVersionStr.replace("dev", "")
			if channel != "dev":
				print(f"addon version str for {addonId} contains dev but channel is not dev")

		if ":" in addonVersionStr:
			addonVersionStr = addonVersionStr.split(":")[0]

		addonVersionInts = [int(x) for x in addonVersionStr.split(".")]
		if len(addonVersionInts) == 1:
			addonVersionInts.append(0)
		addonVersionNumber = MajorMinorPatch(*addonVersionInts)
	except:
		print(f"Error parsing version: {manifest['version']}")
		addonVersionNumber = MajorMinorPatch(0, 0, 0)


	return {
		"displayName": manifest['summary'],
		"publisher": manifest["author"],
		"description": manifest["description"],
		"homepage": manifest.get("url"),
		"addonId": addonId,
		"addonVersionName": manifest["version"],
		"addonVersionNumber": addonVersionNumber._asdict(),
		"minNVDAVersion": minimumNVDAVersion._asdict(),
		"lastTestedVersion": lastTestedNVDAVersion._asdict(),
		"channel": channel,
		"URL": url,
		"sha256": sha256,
		"sourceURL": manifest.get("url", default=""),
		"license": "unknown",
		"licenseURL": None,
	}


def downloadAddonManifest(url: str) -> Tuple[configobj.ConfigObj, str]:
	response = get(url, headers={
		"Accept": "*/*",
		"User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
		}
	)

	with tempfile.TemporaryFile() as outfile:
		outfile.write(response.content)

		try:
			with ZipFile(outfile, 'r') as zipFile:
				with zipFile.open("manifest.ini", "r") as manifestFile:
					config = configobj.ConfigObj(manifestFile, configspec=manifestSpec)
		except BadZipFile:
			sleep(1)
			print(f"failed get {url}, trying again")
			return downloadAddonManifest(url)

		sha256Hash = hashlib.sha256(outfile.read()).hexdigest()

	return config, sha256Hash


def fetchAndTransformLegacyAddons(addonId: str, channel: str, url: str):
	newAddonPaths = set()
	addonManifest = None
	try:
		addonManifest, sha256 = downloadAddonManifest(url)
		newAddonJson = createNewAddonJSON(addonId, channel, url, sha256, addonManifest)
		print("Fetched: ", addonId, newAddonJson['addonVersionName'], newAddonJson["channel"])
		newAddonFolder = os.path.join(".", "addons", addonId.replace("-dev", ""))
		pathlib.Path(newAddonFolder).mkdir(parents=True, exist_ok=True)

		while True:
			# handle when a dev and stable version collide with the same version number
			addonVersionNumber = MajorMinorPatch(**newAddonJson['addonVersionNumber'])
			newAddonPath = os.path.join(newAddonFolder, f"{str(addonVersionNumber)}.json")
			if newAddonPath in newAddonPaths:
				print(f"Collision with version path {addonId} {newAddonPath}")
				with open(newAddonPath, "r") as newAddonFile:
					existingCopyOfAddon = json.load(newAddonFile)

				if existingCopyOfAddon["channel"] != newAddonJson["channel"]:
					newAddonJson["addonVersionNumber"]["patch"] += 1
					print(
						f"Channels are different, increasing patch version number for {addonId} {newAddonJson['channel']}"
						f" from {str(MajorMinorPatch(**newAddonJson['addonVersionNumber']))} to {str(addonVersionNumber)}"
					)
			else:
				break

		try:
			pathlib.Path(newAddonPath).touch(exist_ok=False)
			newAddonPaths.add(newAddonPath)
		except OSError as e:
			print(f"Error: {e} file exists {newAddonPath}")
			raise
		with open(newAddonPath, "w") as newAddonFile:
			json.dump(newAddonJson, newAddonFile, indent="\t")

	except Exception as error:
		print(f"Error {error}: {url} {addonManifest}")
		print(traceback.format_exc())


if __name__ == "__main__":
	fetchAndTransformLegacyAddons(*sys.argv[1:])

