#!/usr/bin/env python

# Copyright (C) 2021 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import argparse
import os
import sys
import tempfile
import zipfile
import json
import urllib.request
from jsonschema import validate, exceptions

sys.path.append(os.path.dirname(__file__))
import sha256
from addonManifest import AddonManifest
del sys.path[-1]


JSON_SCHEMA = os.path.join(os.path.dirname(__file__), "addonVersion_schema.json")
DOWNLOAD_BLOCK_SIZE = 8192 # 8 kb
TEMP_DIR = tempfile.gettempdir()

def getAddonMetadata(jsonFile):
	with open(jsonFile) as f:
		data = json.load(f)
		return data

def validateJson(data):
	with open(JSON_SCHEMA) as f:
		schema = json.load(f)
	try:
		validate(instance=data, schema=schema)
		print("Add-on metadata matches json schema")
		return True
	except exceptions.ValidationError as err:
		print(f"Add-on metadata is not valid: {err}")
		return False

def _downloadAddon(url):
	assert url.startswith("https"), "add-on url should start with https"
	assert url.endswith(".nvda-addon"), "add-on url should ends with .nvda-addon"
	destPath = os.path.join(TEMP_DIR, "addon.nvda-addon")
	remote = urllib.request.urlopen(url)
	if remote.code != 200:
		raise RuntimeError("Download failed with code %d" % remote.code)
	size = int(remote.headers["content-length"])
	with open(destPath, "wb") as local:
		read = 0
		chunk=DOWNLOAD_BLOCK_SIZE
		while True:
			if size -read <chunk:
				chunk =size -read
			block = remote.read(chunk)
			if not block:
				break
			read += len(block)
			local.write(block)
	return destPath

jsonContentErrors = []

def validateSha256(destPath, data):
	with open(destPath, "rb") as f:
		sha256Addon = sha256.sha256_checksum(f)
		if sha256Addon != data["sha256"]:
			jsonContentErrors.append(f"Please, set sha256 to {sha256Addon} in json file")
			return False	
		return True

def _getAddonManifest(destPath):
	expandedPath = os.path.join(TEMP_DIR, "nvda-addon")
	with zipfile.ZipFile(destPath, "r") as z:
		for info in z.infolist():
			z.extract(info, expandedPath)
	filePath = os.path.join(expandedPath, "manifest.ini")
	manifest = AddonManifest(filePath)
	return manifest

def validateJsonContent(manifest, data, filename):
	summary = manifest["summary"]
	if summary != data["name"]:
		jsonContentErrors.append(f"Please, set name to {summary} in json file")
	description = manifest["description"]
	if description != data["description"]:
		jsonContentErrors.append("Please, set description to {description} in json file")
	url = manifest["url"]
	if url != data["homepage"]:
		jsonContentErrors.append(f"Please, set homepage to {url} in json file")
	name = manifest["name"]
	if name != os.path.basename(os.path.dirname(filename)):
		jsonContentErrors.append(f"Please, place jsonfile in {name} folder")
	version = manifest["version"]
	if version != os.path.splitext(os.path.basename(filename))[0]:
		jsonContentErrors.append(f"Please, rename jsonfile to {version}.json")
	if len(jsonContentErrors) >= 1:
		print(jsonContentErrors.join("\r\n"))
		return False
	print("Add-on metadata matches manifest")
	return True


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		dest="file",
		help="The json (.json) file containing add-on metadata."
	)
	args = parser.parse_args()
	data = getAddonMetadata(args.file)
	validateJson(data=data)
	url = data["URL"]
	destPath = _downloadAddon(url=url)
	validateSha256(destPath=destPath, data=data)
	manifest = _getAddonManifest(destPath=destPath)
	validateJsonContent(manifest=manifest, data=data, filename=args.file)

if __name__ == '__main__':
	main()
