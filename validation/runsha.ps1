# print sha256 of a Python file
$ErrorActionPreference = "Stop";
& "$PSScriptRoot\venvUtils\venvCmd" "$PSScriptRoot\_validate\sha256.py" $args
