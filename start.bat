@echo off
echo CodeGraph Quick Start
echo ==========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3 is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo [OK] Python found
echo [OK] Node.js found
echo.

REM Setup backend
echo Setting up backend...
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo [OK] Backend setup complete!
echo.

REM Setup frontend
echo Setting up frontend...
cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo Installing Node dependencies - this will take a few minutes...
    call npm install
    
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

echo [OK] Frontend setup complete!
echo.

REM Start services
echo Starting CodeGraph...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Close both windows to stop the application.
echo.

REM Start backend
cd /d "%~dp0backend"
start "CodeGraph Backend" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend
cd /d "%~dp0frontend"
start "CodeGraph Frontend" cmd /k "npm start"

echo.
echo [OK] CodeGraph is starting in separate windows...
echo.
pause