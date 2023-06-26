# validate <file.json>
$ErrorActionPreference = "Stop";
& "$PSScriptRoot\venvUtils\venvCmd" "$PSScriptRoot\_validate\validate.py" $args
