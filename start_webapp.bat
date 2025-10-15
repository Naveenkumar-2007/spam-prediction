@echo off
REM ============================================
REM Spam Detector Web App Launcher
REM ============================================

echo.
echo ============================================
echo    SMS Spam Detector - Web Application
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Flask not found. Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if model exists
if not exist "artifacts\best_model.h5" (
    echo.
    echo [WARNING] Model file not found!
    echo You need to train the model first.
    echo.
    echo Run this command to train:
    echo    python run_pipeline.py
    echo.
    set /p choice="Do you want to train the model now? (y/n): "
    if /i "%choice%"=="y" (
        echo.
        echo Training model... This may take a few minutes...
        python run_pipeline.py
        if %errorlevel% neq 0 (
            echo [ERROR] Model training failed
            pause
            exit /b 1
        )
    ) else (
        echo Please train the model before running the web app
        pause
        exit /b 1
    )
)

REM Start the Flask application
echo.
echo Starting Flask web application...
echo.
echo ============================================
echo  Opening in browser: http://127.0.0.1:5000
echo ============================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Wait a moment then open browser
start "" http://127.0.0.1:5000

REM Run Flask app
python app.py

pause
