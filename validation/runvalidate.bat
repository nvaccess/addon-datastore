@echo off
rem install wheel to avoid warnings
call python -m pip install wheel
rem validate <file.json>
call "%~dp0\venvUtils\venvCmd.bat" py "%~dp0\_validate\validate.py" %1
