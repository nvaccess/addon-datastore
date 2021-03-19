@echo off
rem validate <file.json>
pip install wheel
call "%~dp0\venvUtils\venvCmd.bat" py "%~dp0\_validate\validate.py" %1
  if ERRORLEVEL 1 exit 1