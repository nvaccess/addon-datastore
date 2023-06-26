# lint Python files
$ErrorActionPreference = "Stop";
& "$PSScriptRoot\venvUtils\venvCmd" -m flake8 _validate _tests --count --show-source --statistics --tee
