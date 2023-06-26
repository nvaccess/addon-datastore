# this script executes the single given command and arguments inside the NVDA build system's Python virtual environment.
# It activates the environment, creating / updating it first if necessary,
# then executes the command,
# and then finally deactivates the environment.

# This script also supports running in an already fully activated NVDA Python environment.
# If this is detected, the command is executed directly instead.

if ("$ENV:VIRTUAL_ENV" -ne "") {
	if ("$NVDA_VENV" -ne "$ENV:VIRTUAL_ENV") {
		Write-Output "Warning: Detected a custom Python virtual environment. "
		Write-Output "It is recommended to run all NVDA build system commands outside of any existing Python virtual environment, unless you really know what you are doing."
	}
	Write-Output "directly calling $($args[0]) $($args[1])"
	. "$ENV:VIRTUAL_ENV/Scripts/python.exe" @args
	exit $LASTEXITCODE
}


Write-Output "Ensuring NVDA Python virtual environment"
. $PSScriptRoot/ensureAndActivate.ps1
if ($LASTEXITCODE -eq 1) {exit 1}
Write-Output "calling $($args[0]) $($args[1])"
. "$ENV:VIRTUAL_ENV/Scripts/python.exe" @args
Write-Output "Deactivating NVDA Python virtual environment"
deactivate
