# Copyright (C) 2023-2026 NV Access Limited, Noelia Ruiz Martínez
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import argparse
import glob
import json
from urllib.request import urlretrieve
from dataclasses import asdict

from .manifestLoader import getAddonManifest
from .validate import checkSha256
from .createJson import createDataclassMatchingJsonSchema


def regenerateJsonFile(filePath: str, errorFilePath: str | None) -> None:
	with open(filePath, encoding="utf-8") as f:
		addonData = json.load(f)
	if addonData.get("legacy"):
		return
	addonFilePath, _ = urlretrieve(addonData["URL"])
	addonSha = addonData["sha256"]
	checksumErrors = list(checkSha256(addonFilePath, addonSha))
	if checksumErrors:
		if errorFilePath:
			with open(errorFilePath, "a") as errorFile:
				errorFile.write(f"Validation errors:\n{'\n'.join(checksumErrors)}")
		return
	manifest = getAddonManifest(addonFilePath)
	if manifest.errors:
		if errorFilePath:
			with open(errorFilePath, "a") as errorFile:
				errorFile.write(f"Validation Errors:\n{manifest.errors}")
		return
	regeneratedData = createDataclassMatchingJsonSchema(
		manifest,
		addonSha,
		addonData["channel"],
		addonData["publisher"],
		addonData["sourceURL"],
		addonData["URL"],
		addonData["license"],
		addonData["licenseURL"],
	)
	submissionTime = addonData.get("submissionTime")
	regeneratedAddonData = asdict(
		regeneratedData,
		# The JSON schema does not permit null values, but does contain optional keys.
		# We have already ensured that all required keys are present in the metadata,
		# So we can safely delete all keys whose value is None as optional.
		dict_factory=lambda args: dict(filter(lambda item: item[1] is not None, args)),
	)
	if submissionTime:
		regeneratedAddonData["submissionTime"] = submissionTime
	with open(filePath, "wt", encoding="utf-8") as f:
		json.dump(regeneratedAddonData, f, indent="\t", ensure_ascii=False)
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
