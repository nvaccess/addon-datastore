#!/usr/bin/env python

# Copyright (C) 2020 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import argparse
import typing
import os
import sys
import json
import urllib.request
from jsonschema import validate, exceptions

sys.path.append(os.path.dirname(__file__))
import sha256
del sys.path[-1]

JSON_SCHEMA = os.path.join(os.path.dirname(__file__), "addonVersion_schema.json")
DOWNLOAD_BLOCK_SIZE = 8192 # 8 kb

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
	except exceptions.ValidationError as err:
		print(f"Add-on metadata is not valid: {err}")

def downloadAddon(url):
	assert url.startswith("https"), "add-on url should start with https"
	assert url.endswith(".nvda-addon"), "add-on url should ends with .nvda-addon"
	destPath = os.path.join(os.path.dirname(__file__), url.split("/")[-1])
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

def validateSha256(destPath, data):
	with open(destPath, "rb") as f:
		sha256Addon = sha256.sha256_checksum(f)
		assert sha256Addon == data["sha256"], f"Please, set sha256 to {sha256Addon} in json file"


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
	destPath = downloadAddon(url=url)
	validateSha256(destPath=destPath, data=data)

if __name__ == '__main__':
	main()
