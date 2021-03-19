@echo off
rem validate <file.json>

call "%~dp0\venvUtils\venvCmd.bat" py "%~dp0\_validate\validate.py" %1
  if ERRORLEVEL 1 exit /b %ERRORLEVEL%
