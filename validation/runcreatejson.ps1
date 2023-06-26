# create json from manifest <dir file.json>
$ErrorActionPreference = "Stop";
& "$PSScriptRoot\venvUtils\venvCmd" "$PSScriptRoot\_validate\createJson.py" $args
