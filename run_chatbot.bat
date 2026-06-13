@echo off
title Chatbot Launcher
cd /d "%~dp0"
echo Activating virtual environment...
call "iisc env\Scripts\activate.bat"
echo Starting chatbot...
python bot.py
pause
