#!/usr/bin/env bash

set -euo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

validationUnitTestsPath="$here/validation/tests"
transformUnitTestsPath="$here/transform/src/tests"
testOutput="$here/testOutput"

mkdir -p "$testOutput"

uv run --group unit-tests --directory "$here" -m xmlrunner discover -b -s "$validationUnitTestsPath" -t "$here" --output-file "$testOutput/validationUnitTests.xml" "$@"
uv run --group unit-tests --directory "$here" -m xmlrunner discover -b -s "$transformUnitTestsPath" -t "$here" --output-file "$testOutput/transformUnitTests.xml" "$@"
