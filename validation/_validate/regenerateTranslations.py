# Copyright (C) 2023-2025 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import argparse
import glob
import json
from urllib.request import urlretrieve

from .manifestLoader import getAddonManifest, getAddonManifestLocalizations


def regenerateJsonFile(filePath: str, errorFilePath: str | None) -> None:
	with open(filePath, encoding="utf-8") as f:
		addonData = json.load(f)
	if addonData.get("legacy"):
		return
	addonData["translations"] = []
	addonFilePath, _ = urlretrieve(addonData["URL"])
	manifest = getAddonManifest(addonFilePath)
	if manifest.errors:
		if errorFilePath:
			with open(errorFilePath, "w") as errorFile:
				errorFile.write(f"Validation Errors:\n{manifest.errors}")
		return

	for langCode, manifest in getAddonManifestLocalizations(manifest):
		addonData["translations"].append(
			{
				"language": langCode,
				"displayName": manifest["summary"],
				"description": manifest["description"],
			},
		)

	with open(filePath, "wt", encoding="utf-8") as f:
		json.dump(addonData, f, indent="\t", ensure_ascii=False)
	print(f"Wrote json file: {filePath}")


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--dir",
		dest="parentDir",
		help="Parent directory to regenerate the JSON files inside.",
		required=True,
	)
	parser.add_argument(
		"--output",
		dest="errorOutputFile",
		help="The text file to output errors from the validation, if any.",
		default=None,
	)
	args = parser.parse_args()
	errorFilePath: str | None = args.errorOutputFile
	for addonJsonFile in glob.glob(f"{args.parentDir}/**/*.json"):
		regenerateJsonFile(addonJsonFile, errorFilePath)


if __name__ == "__main__":
	main()
