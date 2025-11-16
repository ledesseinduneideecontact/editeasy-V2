@echo off
echo ========================================
echo AI Video Editor - Starting...
echo ========================================
echo.

REM Check if FFmpeg is installed
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] FFmpeg is not installed!
    echo Please install FFmpeg from https://ffmpeg.org/download.html
    pause
    exit /b 1
)
echo [OK] FFmpeg found

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)
echo [OK] Python found

REM Install backend dependencies
if not exist "backend\node_modules" (
    echo.
    echo Installing backend dependencies...
    cd backend
    call npm install
    cd ..
)

REM Setup Python virtual environment
if not exist "ai-processor\venv" (
    echo.
    echo Setting up Python virtual environment...
    cd ai-processor
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    deactivate
    cd ..
)

REM Create necessary directories
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "temp" mkdir temp

REM Create .env if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file from .env.example...
    copy .env.example .env >nul
    echo [OK] .env file created
)

echo.
echo ========================================
echo Starting services...
echo ========================================
echo.

REM Start AI Processor
echo Starting AI Processor...
cd ai-processor
start "AI Processor" cmd /k "venv\Scripts\activate.bat && python app.py"
cd ..

REM Wait for AI service
timeout /t 3 /nobreak >nul

REM Start Backend
echo Starting Backend...
cd backend
start "Backend Server" cmd /k "node server.js"
cd ..

REM Wait for backend
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Application started successfully!
echo ========================================
echo.
echo Access the application at: http://localhost:3000
echo.
echo Press any key to open in browser...
pause >nul
start http://localhost:3000
