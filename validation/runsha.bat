@echo off
rem print sha256 of a Python file
call py "%~dp0\_validate\sha256.py" %1
