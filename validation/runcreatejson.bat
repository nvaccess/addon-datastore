@echo off
rem create json from manifest <dir file.json>
call "%~dp0\venvUtils\venvCmd.bat" py "%~dp0\_validate\createJson.py" %*
