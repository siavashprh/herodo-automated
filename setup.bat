@echo off
REM Setup script for Herodo Automated (Windows)

echo Setting up Herodo Automated...

REM Check if python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To use the pipeline:
echo   1. Activate the virtual environment: venv\Scripts\activate
echo   2. Run: python -m src.main "Your Wikipedia Article"
echo.

pause


