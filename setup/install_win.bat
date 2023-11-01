@echo off

set MayaPy="%ProgramFiles%\Autodesk\Maya%MayaVersion%\bin\mayapy.exe"

:: pip upgrade
%MayaPy% -m pip install -U pip

:: install site-packages
%MayaPy% -m pip install -U -r %~dp0\requirements.txt -t %UserProfile%\Documents\maya\%MayaVersion%\scripts\site-packages