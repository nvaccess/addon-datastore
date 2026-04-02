@echo off
set hereOrig=%~dp0
set here=%hereOrig%
if #%hereOrig:~-1%# == #\# set here=%hereOrig:~0,-1%
set validationUnitTestsPath=%here%\validation\tests
set transformUnitTestsPath=%here%\transform\src\tests
set testOutput=%here%\testOutput
md %testOutput%

call uv run --group unit-tests --directory "%here%" -m xmlrunner discover -b -s "%validationUnitTestsPath%" -t "%here%" --output-file "%testOutput%\validationUnitTests.xml" %*
call uv run --group unit-tests --directory "%here%" -m xmlrunner discover -b -s "%transformUnitTestsPath%" -t "%here%" --output-file "%testOutput%\transformUnitTests.xml" %*
