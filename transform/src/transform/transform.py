# Copyright (C) 2021-2023 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

import glob
import json
import logging
from pathlib import Path
from typing import (
	Dict,
	Iterable,
	Set,
	Tuple,
)
from .datastructures import (
	Addon,
	generateAddonChannelDict,
	MajorMinorPatch,
	VersionCompatibility,
	WriteableAddons
)
from src.validate.validate import (
	ValidationError,
	validateJson,
	JSONSchemaPaths,
)

log = logging.getLogger()


def _isAddonCompatible(addon: Addon, nvdaAPIVersion: VersionCompatibility) -> bool:
	"""
	Confirms that the addon has been tested with an API version that the nvdaAPIVersion is compatible with.
	"""
	return (
		nvdaAPIVersion.backCompatTo <= addon.lastTestedVersion
		and addon.minNvdaAPIVersion <= nvdaAPIVersion.apiVer
	)


def _isAddonNewer(addons: Dict[str, Addon], addon: Addon) -> bool:
	"""
	Confirms that a given addon is newer than the most recent version of that addon in the addons dict.
	"""
	_addonVersionNotAlreadyAdded(addons, addon)
	return addon.addonId not in addons or addon.addonVersion > addons[addon.addonId].addonVersion


def _addonVersionNotAlreadyAdded(addons: Dict[str, Addon], addon: Addon) -> True:
	"""
	Throws an exception if an addon with that version has already been added to addons.
	"""
	if addon.addonId in addons and addon.addonVersion == addons[addon.addonId].addonVersion:
		raise ValueError(f"Addon {addon.addonId} {addon.addonVersion} already added to addons dictionary")
	return True


def getSupportedLanguages(addons: WriteableAddons) -> Set[str]:
	supportedLanguages: Set[str] = set()
	for apiVersion in addons:
		for channel in addons[apiVersion]:
			for addonId in addons[apiVersion][channel]:
				supportedLanguages.update({t["language"] for t in addons[apiVersion][channel][addonId].translations})
	return supportedLanguages


def getLatestAddons(addons: Iterable[Addon], nvdaAPIVersions: Tuple[VersionCompatibility]) -> WriteableAddons:
	"""
	Given a set of addons and NVDA versions, create a dictionary mapping each nvdaAPIVersion and channel
	to the newest compatible addon.
	"""
	uniqueApiVersions = set(nvdaAPIVersion.apiVer for nvdaAPIVersion in nvdaAPIVersions)
	latestAddons: WriteableAddons = dict(
		(nvdaAPIVersion, generateAddonChannelDict())
		for nvdaAPIVersion in uniqueApiVersions
	)
	for addon in addons:
		for nvdaAPIVersion in nvdaAPIVersions:
			addonsForVersionChannel = latestAddons[nvdaAPIVersion.apiVer][addon.channel]
			if (
				_isAddonCompatible(addon, nvdaAPIVersion)
				and _isAddonNewer(addonsForVersionChannel, addon)
			):
				addonsForVersionChannel[addon.addonId] = addon
				log.error(f"added {addon.addonId} {addon.addonVersion}")
			else:
				log.error(f"ignoring {addon.addonId} {addon.addonVersion}")
	return latestAddons


def writeAddons(addonDir: str, addons: WriteableAddons, supportedLanguages: Set[str]) -> None:
	"""
	Given a unique mapping of (nvdaAPIVersion, channel) -> addon, write the addons to file.
	Throws a ValidationError and exits if writeable data does not match expected schema.
	"""
	writtenLatestAddonForChannel: Set[str] = set()
	for nvdaAPIVersion in sorted(addons.keys(), reverse=True):
		# To generate the 'latest view',
		# check each api version, starting with the latest.
		# For a given 'latest' addon write path,
		# store the path when the path is first encountered.
		# This ensures the latest path is returned.
		for channel in addons[nvdaAPIVersion]:
			for addonName in addons[nvdaAPIVersion][channel]:
				addon = addons[nvdaAPIVersion][channel][addonName]
				addonWritePath = f"{addonDir}/en/{str(nvdaAPIVersion)}/{addonName}"
				with open(addon.pathToData, "r") as oldAddonFile:
					addonData: Dict = json.load(oldAddonFile)
					if "translations" in addonData:
						del addonData["translations"]
				Path(addonWritePath).mkdir(parents=True, exist_ok=True)
				with open(f"{addonWritePath}/{channel}.json", "w") as newAddonFile:
					validateJson(addonData, JSONSchemaPaths.ADDON_DATA)
					json.dump(addonData, newAddonFile)

				latestAddonWritePath = f"{addonDir}/en/latest/{addonName}"
				Path(latestAddonWritePath).mkdir(parents=True, exist_ok=True)
				# paths are case insensitive
				# Identical add-on IDs may have different casing
				# due to legacy add-on submissions.
				# This can be removed when old submissions are given updated casing.
				caseInsensitiveLatestAddonForChannel = f"{addonName.lower()}-{channel}"
				addLatest = caseInsensitiveLatestAddonForChannel not in writtenLatestAddonForChannel
				if addLatest:
					log.error(f"Latest version: {addonName} {channel} {nvdaAPIVersion}")
					writtenLatestAddonForChannel.add(caseInsensitiveLatestAddonForChannel)
					with open(f"{latestAddonWritePath}/{channel}.json", "w") as latestAddonFile:
						json.dump(addonData, latestAddonFile)

				addonTranslations = {t["language"]: t for t in addon.translations}
				translatedAddonData = addonData.copy()
				for lang in supportedLanguages:
					addonWritePath = f"{addonDir}/{lang}/{str(nvdaAPIVersion)}/{addonName}"
					if lang in addonTranslations:
						# update with translated version
						translatedAddonData["displayName"] = addonTranslations[lang]["displayName"]
						translatedAddonData["description"] = addonTranslations[lang]["description"]
					else:
						# update with english
						translatedAddonData["displayName"] = addonData["displayName"]
						translatedAddonData["description"] = addonData["description"]
					Path(addonWritePath).mkdir(parents=True, exist_ok=True)
					with open(f"{addonWritePath}/{channel}.json", "w") as newAddonFile:
						validateJson(translatedAddonData, JSONSchemaPaths.ADDON_DATA)
						json.dump(translatedAddonData, newAddonFile)
					if addLatest:
						latestAddonWritePath = f"{addonDir}/{lang}/latest/{addonName}"
						Path(latestAddonWritePath).mkdir(parents=True, exist_ok=True)
						with open(f"{latestAddonWritePath}/{channel}.json", "w") as newAddonFile:
							validateJson(translatedAddonData, JSONSchemaPaths.ADDON_DATA)
							json.dump(translatedAddonData, newAddonFile)


def readAddons(addonDir: str) -> Iterable[Addon]:
	"""
	Read addons from a directory and capture required data for processing.
	Works as a generator to minimize memory usage, as such, each use of iteration should call readAddons.
	Skips addons and logs errors if the naming schema or json schema do not match what is expected.
	"""
	for fileName in glob.glob(f"{addonDir}/**/*.json"):
		with open(fileName, "r") as addonFile:
			addonData = json.load(addonFile)
		try:
			validateJson(addonData, JSONSchemaPaths.ADDON_DATA)
		except ValidationError as e:
			log.error(f"{fileName} doesn't match schema: {e}")
			continue
		yield Addon(
			addonId=addonData["addonId"],
			addonVersion=MajorMinorPatch(**addonData["addonVersionNumber"]),
			pathToData=fileName,
			channel=addonData["channel"],
			minNvdaAPIVersion=MajorMinorPatch(**addonData["minNVDAVersion"]),
			lastTestedVersion=MajorMinorPatch(**addonData["lastTestedVersion"]),
			translations=addonData.get("translations", []),
		)


def readnvdaAPIVersionInfo(pathToFile: str) -> Tuple[VersionCompatibility]:
	"""
	Reads and captures NVDA version information from file.
	"""
	with open(pathToFile, "r") as nvdaAPIVersionFile:
		nvdaAPIVersionData = json.load(nvdaAPIVersionFile)
	validateJson(nvdaAPIVersionData, JSONSchemaPaths.NVDA_VERSIONS)
	return tuple(
		VersionCompatibility(
			apiVer=MajorMinorPatch(**version["apiVer"]),
			backCompatTo=MajorMinorPatch(**version["backCompatTo"]),
		) for version in nvdaAPIVersionData
	)


def runTransformation(nvdaAPIVersionsPath: str, sourceDir: str, outputDir: str) -> None:
	"""
	Performs the transformation of addon data described in the readme.
	Takes addon data found in sourceDir that fits the schema and writes the transformed data to outputDir.
	Uses the NVDA API Versions found in nvdaAPIVersionsPath.
	"""
	# Make sure the directory doesn't already exist so data isn't overwritten
	Path(outputDir).mkdir(parents=True, exist_ok=False)
	nvdaAPIVersionInfo = readnvdaAPIVersionInfo(nvdaAPIVersionsPath)
	latestAddons = getLatestAddons(readAddons(sourceDir), nvdaAPIVersionInfo)
	supportedLanguages = getSupportedLanguages(latestAddons)
	writeAddons(outputDir, latestAddons, supportedLanguages)
