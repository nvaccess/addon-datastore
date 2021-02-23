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


def getAddonMetadata(filename):
	with open(filename) as f:
		data = json.load(f)
	return data

def getJsonschemaErrors(data):
	errors = []
	with open(JSON_SCHEMA) as f:
		schema = json.load(f)
	try:
		validate(instance=data, schema=schema)
	except exceptions.ValidationError as err:
		errors.append(err)
	finally:
		return errors

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

def getSha256Errors(destPath, data):
	errors = []
	with open(destPath, "rb") as f:
		sha256Addon = sha256.sha256_checksum(f)
	if sha256Addon != data["sha256"]:
		errors.append(f"sha256 must be set to {sha256Addon} in json file")
	return errors

def _getAddonManifest(destPath):
	expandedPath = os.path.join(TEMP_DIR, "nvda-addon")
	with zipfile.ZipFile(destPath, "r") as z:
		for info in z.infolist():
			z.extract(info, expandedPath)
	filePath = os.path.join(expandedPath, "manifest.ini")
	manifest = AddonManifest(filePath)
	return manifest

def getSummaryErrors(manifest, data):
	errors = []
	summary = manifest["summary"]
	if summary != data["name"]:
		errors.append(f"name must be set to {summary} in json file")
	return errors

def getDescriptionErrors(manifest, data):
	errors = []
	description = manifest["description"]
	if description != data["description"]:
		errors.append("description must be set to {description} in json file")
	return errors

def getUrlErrors(manifest, data):
	errors = []
	url = manifest["url"]
	if url != data["homepage"]:
		errors.append(f"homepage must be set to {url} in json file")
	return errors

def getNameErrors(manifest, filename):
	errors = []
	name = manifest["name"]
	if name != os.path.basename(os.path.dirname(filename)):
		errors.append(f"json file must be placed in {name} folder")
	return errors

def getVersionErrors(manifest, filename):
	errors = []
	version = manifest["version"]
	if version != os.path.splitext(os.path.basename(filename))[0]:
		errors.append(f"jsonfile should be named {version}.json")
	return errors


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		dest="file",
		help="The json (.json) file containing add-on metadata."
	)
	args = parser.parse_args()
	filename = args.file
	data = getAddonMetadata(filename=filename)
	getJsonschemaErrors(data=data)
	url = data["URL"]
	destPath = _downloadAddon(url=url)
	getSha256Errors(destPath=destPath, data=data)
	manifest = _getAddonManifest(destPath=destPath)
	getSummaryErrors(manifest=manifest, data=data)
	getDescriptionErrors(manifest=manifest, data=data)
	getUrlErrors(manifest=manifest, data=data)
	getNameErrors(manifest=manifest, filename=filename)
	getVersionErrors(manifest=manifest, filename=filename)
if __name__ == '__main__':
	main()
