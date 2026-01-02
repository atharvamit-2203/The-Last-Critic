@echo off
echo ========================================
echo    Starting The Last Critic
echo    Your final word on what to watch
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)
echo ✓ Python is installed

echo.
echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)
echo ✓ Node.js is installed

echo.
echo [3/4] Starting Backend (FastAPI)...
cd backend
start "The Last Critic - Backend" cmd /k "python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python main.py"

echo.
echo [4/4] Starting Frontend (Next.js)...
cd ..\frontend
start "The Last Critic - Frontend" cmd /k "npm install && npm run dev"

echo.
echo ========================================
echo The Last Critic is starting up!
echo.
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo API Documentation: http://localhost:8000/docs
echo.
echo Wait for both services to start, then open:
echo http://localhost:3000
echo ========================================
echo.
echo Press any key to exit this window...
pause >nul