@echo off
cd /d "%~dp0"

call .venv\Scripts\activate.bat
set PYTHONPATH=src

python -m carlo_bot.main --send
