# this script ensures the NVDA build system Python virtual environment is created and up to date,
# and then activates it.
# this script should be used only in the case where many commands will be executed within the environment and the shell will be eventually thrown away. 
# E.g. an Appveyor build.
py -3.8-32 "$PSScriptRoot\ensureVenv.py"
if ($LASTEXITCODE -eq 1) {exit 1}
. "$PSScriptRoot\..\.venv\scripts\activate.ps1"
Set-Variable NVDA_VENV $ENV:VIRTUAL_ENV
