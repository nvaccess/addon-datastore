# Copyright (C) 2023 Noelia Ruiz Martínez, NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

from dataclasses import dataclass


@dataclass
class MajorMinorPatch:
	major: int = 0
	minor: int = 0
	patch: int = 0

	@classmethod
	def getFromStr(cls, version: str) -> "MajorMinorPatch":
		versionParts = version.split(".")
		versionLen = len(versionParts)
		if versionLen < 2 or versionLen > 3:
			raise ValueError(f"Version string not valid: {version}")
		return cls(
			major=int(versionParts[0]),
			minor=int(versionParts[1]),
			patch=0 if len(versionParts) == 2 else int(versionParts[2])
		)

	def __str__(self) -> str:
		return f"{self.major}.{self.minor}.{self.patch}"
