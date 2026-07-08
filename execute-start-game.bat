@echo off
cd /d "%~dp0"
python files\protect_assets.py
python files\start.py
