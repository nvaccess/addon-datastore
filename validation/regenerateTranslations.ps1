# Regenerate translations for files in dir
$ErrorActionPreference = "Stop";
& "$PSScriptRoot\venvUtils\venvCmd" "$PSScriptRoot\_validate\regenerateTranslations.py" $args
