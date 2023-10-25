@echo off

set MayaVersion=2024

set MayaPy="%ProgramFiles%\Autodesk\Maya%MayaVersion%\bin\mayapy.exe"

:: pip upgrade
%MayaPy% -m pip install -U pip

:: install site-packages
::%MayaPy% -m pip install -U openai keyboard tenacity -t %UserProfile%\Documents\maya\%MayaVersion%\scripts\site-packages
%MayaPy% -m pip install -U openai[datalib] keyboard tenacity -t %UserProfile%\Documents\maya\%MayaVersion%\scripts\site-packages