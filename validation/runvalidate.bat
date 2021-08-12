@echo off
rem validate <file.json>
call "%~dp0\venvUtils\venvCmd.bat" py "%~dp0\_validate\validate.py" %*
