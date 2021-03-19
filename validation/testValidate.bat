@echo off
rem validate <clipContentsDesigner\13.0.json>

call "%~dp0\venvUtils\venvCmd.bat" py "%~dp0\_validate\validate.py %dp0\clipContentsDesigner\13.0.json"