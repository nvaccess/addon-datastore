#!/usr/bin/env python

# Copyright (C) 2022 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import json
import argparse
from dataclasses import dataclass
import os
import sys
sys.path.append(os.path.dirname(__file__))  # To allow this module to be run as a script by runcreatejson.bat
# E402 module level import not at top of file
from manifestLoader import getAddonManifest  # noqa:E402
import sha256  # noqa:E402
del sys.path[-1]

VALID_JSON = os.path.join(
	os.path.dirname(__file__), "..", "_tests", "testData", "addons", "fake", "13.0.0.json"
)


@dataclass
class Version:
	major: int = 0
	minor: int = 0
	patch: int = 0


def getSha256(addonPath: str) -> str:
	with open(addonPath, "rb") as f:
		sha256Addon = sha256.sha256_checksum(f)
	return sha256Addon


def getVersionNumber(ver: str) -> Version:
	version = Version()
	verParts = ver.split(".")
	verLen = len(verParts)
	if verLen < 2 or verLen > 3:
		raise ValueError("Version not valid")
	version.major = int(verParts[0])
	version.minor = int(verParts[1])
	if len(verParts) > 2:
		version.patch = int(verParts[2])
	return version


def getFullQualifiedName(version: Version) -> str:
	versionParts = [
		str(version.major),
		str(version.minor),
		str(version.patch)
	]
	stringVersion = ".".join(versionParts)
	return stringVersion


def generateJsonFile(
		addonPath: str, parentDir: str, channel: str,
		publisher: str, sourceUrl: str, url: str
) -> None:
	manifest = getAddonManifest(addonPath)
	shaVal = getSha256(addonPath)
	addonId = manifest["name"]
	addonDisplayName = manifest["summary"]
	addonDescription = manifest["description"]
	addonHomepage = manifest["url"]
	addonVersionNumber = manifest["version"]
	addonMinVersion = manifest["minimumNVDAVersion"]
	addonLastTestedVersion = manifest["lastTestedNVDAVersion"]
	with open(VALID_JSON, "r") as f:
		data = json.load(f)
	del data["sha256-comment"]
	data["addonId"] = addonId
	data["displayName"] = addonDisplayName
	data["description"] = addonDescription
	data["URL"] = url
	data["homepage"] = addonHomepage
	data["addonVersionName"] = addonVersionNumber
	versionNumber = getVersionNumber(addonVersionNumber)
	filename = f"{getFullQualifiedName(versionNumber)}.json"
	data["addonVersionNumber"]["major"] = versionNumber.major
	data["addonVersionNumber"]["minor"] = versionNumber.minor
	data["addonVersionNumber"]["patch"] = versionNumber.patch
	minVersion = getVersionNumber(addonMinVersion)
	data["minNVDAVersion"]["major"] = minVersion.major
	data["minNVDAVersion"]["minor"] = minVersion.minor
	data["minNVDAVersion"]["patch"] = minVersion.patch
	lastTestedVersion = getVersionNumber(addonLastTestedVersion)
	data["lastTestedVersion"]["major"] = lastTestedVersion.major
	data["lastTestedVersion"]["minor"] = lastTestedVersion.minor
	data["lastTestedVersion"]["patch"] = lastTestedVersion.patch
	data["sha256"] = shaVal
	data["channel"] = channel
	data["publisher"] = publisher
	data["sourceURL"] = sourceUrl
	addonDir = os.path.join(parentDir, addonId)
	if not os.path.isdir(addonDir):
		os.makedirs(addonDir)
	filePath = os.path.join(addonDir, filename)
	with open(filePath, "wt") as f:
		json.dump(data, f, indent="\t")
	print(f"Json file is in {dir}/{filename}.")


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		dest="file",
		help="The add-on (nvda-addon) file to create json from manifest."
	)
	parser.add_argument(
		dest="parentDir",
		help="Parent directory to store the json file."
	)
	parser.add_argument(
		dest="channel",
		help="The channel for this release."
	)
	parser.add_argument(
		dest="publisher",
		help="The publisher for this submission."
	)
	parser.add_argument(
		dest="sourceUrl",
		help="The URL to review source code."
	)
	parser.add_argument(
		dest="url",
		help="URL to download the add-on."
	)
	args = parser.parse_args()
	filename = args.file
	parentDir = args.parentDir
	channel = args.channel
	publisher = args.publisher
	sourceUrl = args.sourceUrl
	url = args.url
	generateJsonFile(filename, parentDir, channel, publisher, sourceUrl, url)


if __name__ == '__main__':
	main()
