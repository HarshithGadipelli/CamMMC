@echo off
echo ===================================================
echo Setting up and running the application...
echo ===================================================

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in the PATH. Please install Python and try again.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Run the application
echo Starting the application...
python app.py

REM Deactivate when done
deactivate
pause
