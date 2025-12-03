@echo off
ECHO Activating virtual environment...
CALL venv\Scripts\activate.bat

ECHO Launching Gemini client with test parameters...
python -m src.monitors.gemini_client --api-key AIzaSyBjDGtyntnQrMxPLZNiIGe3nZ6urQeb63s --num-messages 3

ECHO Client process finished.
pause
