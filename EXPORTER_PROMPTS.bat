@echo off
cd /d "%~dp0"
py -c "from pathlib import Path; from kolor_studio_core import export_prompts; print(export_prompts(Path('projet')))"
if errorlevel 1 pause
