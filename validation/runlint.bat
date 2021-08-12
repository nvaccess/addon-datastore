@echo off
rem lint Python files
call "%~dp0\venvUtils\venvCmd.bat" flake8 _validate _tests --count --show-source --statistics --tee
