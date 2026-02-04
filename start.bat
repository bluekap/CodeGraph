@echo off
setlocal enabledelayedexpansion

echo CodeGraph Quick Start
echo ==========================
echo.

REM Set script directory as root
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 1. Check for Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed. Please install Git from https://git-scm.com/
    pause
    exit /b 1
)
echo [OK] Git found.

REM 2. Check for Python 3.10+
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.10+ is required. 
    echo Current version:
    python --version
    pause
    exit /b 1
)
echo [OK] Python 3.10+ found.

REM 3. Check for Node.js 18+
node -e "const v = process.version.slice(1).split('.')[0]; process.exit(v >= 18 ? 0 : 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js 18+ is required.
    echo Current version:
    node --version
    pause
    exit /b 1
)
echo [OK] Node.js 18+ found.

REM 4. Check for Port Conflicts
set "PORT_8000_BUSY="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do set "PORT_8000_BUSY=%%a"
if defined PORT_8000_BUSY (
    echo [ERROR] Port 8000 is already in use (Backend target). Please close the application using it.
    pause
    exit /b 1
)

set "PORT_3000_BUSY="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do set "PORT_3000_BUSY=%%a"
if defined PORT_3000_BUSY (
    echo [ERROR] Port 3000 is already in use (Frontend target). Please close the application using it.
    pause
    exit /b 1
)
echo [OK] Ports 8000 and 3000 are available.
echo.

REM --- Setup Backend ---
echo [STEP] Setting up backend...
cd /d "%SCRIPT_DIR%backend"
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv || (echo [ERROR] Failed to create venv & pause & exit /b 1)
)

call venv\Scripts\activate.bat || (echo [ERROR] Failed to activate venv & pause & exit /b 1)
echo [INFO] Installing/Updating Python dependencies...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt || (echo [ERROR] Failed to install backend dependencies & pause & exit /b 1)

echo [OK] Backend setup complete!
echo.

REM --- Setup Frontend ---
echo [STEP] Setting up frontend...
cd /d "%SCRIPT_DIR%frontend"
if not exist "node_modules" (
    echo [INFO] Installing Node dependencies (this may take a few minutes)...
    call npm install || (echo [ERROR] npm install failed & pause & exit /b 1)
)

echo [OK] Frontend setup complete!
echo.

REM --- Launching ---
echo [STEP] Launching CodeGraph...
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo [TIP] Keep this window open. Close the backend/frontend windows to stop.
echo.

REM Start backend
cd /d "%SCRIPT_DIR%backend"
start "CodeGraph Backend" /min cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

REM Wait for backend
echo [INFO] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

REM Start frontend
cd /d "%SCRIPT_DIR%frontend"
start "CodeGraph Frontend" cmd /k "npm start"

echo.
echo [OK] CodeGraph is up and running!
echo.
pause