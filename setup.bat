@echo off
REM Setup script for GenAI Document Assistant (Windows)

echo ===================================
echo GenAI Document Assistant Setup
echo ===================================

REM Check Python version
echo Checking Python version...
python --version

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

REM Create necessary directories
echo Creating directories...
if not exist "data\chroma" mkdir data\chroma
if not exist "temp_uploads" mkdir temp_uploads

REM Copy environment template
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo WARNING: Edit .env and add your LLM_API_KEY
    echo.
) else (
    echo .env file already exists
)

echo.
echo ===================================
echo Setup complete!
echo ===================================
echo.
echo Next steps:
echo 1. Edit .env and add your LLM_API_KEY
echo 2. Activate virtual environment: venv\Scripts\activate.bat
echo 3. Run API: run_api.bat
echo 4. Run UI (in new terminal): run_ui.bat
echo.

pause
