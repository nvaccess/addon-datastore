@echo off
REM create json from manifest <dir file.json>
set hereOrig=%~dp0
set here=%hereOrig%
if #%hereOrig:~-1%# == #\# set here=%hereOrig:~0,-1%
set unitTestsPath=%here%\tests
set testOutput=%here%\testOutput
md %testOutput%

call uv run --directory "%here%" python -m _validate.createJson %*
