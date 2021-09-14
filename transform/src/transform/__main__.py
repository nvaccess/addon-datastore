# Copyright (C) 2021 NV Access Limited
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

"""
Usage: python -m transform {nvdaVersionsPath} {inputPath} {outputPath} [logLevel]
"""
import argparse
import logging
import sys
from .transform import runTransformation

log = logging.getLogger()

parser = argparse.ArgumentParser()
parser.add_argument(
	dest="nvdaVersionsPath",
	help="The path to the NVDAVersions.json, see README for full usage."
)
parser.add_argument(
	dest="sourceDir",
	help="The input directory, see README for full usage."
)
parser.add_argument(
	dest="outputDir",
	help="The output directory, see README for full usage."
)
parser.add_argument(
	"--loglevel",
	required=False,
	help=f"The loglevel, one of {logging._nameToLevel}",
	dest="loglevel",
	default=logging.WARNING,
)
args = parser.parse_args()

handler = logging.StreamHandler(sys.stdout)  # always log to stdout
log.setLevel(args.loglevel)
log.addHandler(handler)
runTransformation(args.nvdaVersionsPath, args.sourceDir, args.outputDir)
