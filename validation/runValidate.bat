@echo off
rem install wheel to avoid warnings
call pip install wheel
rem validate <file.json>
call "%~dp0\venvUtils\venvCmd.bat" py "%~dp0\_validate\validate.py" %1
