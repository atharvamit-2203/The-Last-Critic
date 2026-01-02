@echo off
echo ========================================
echo  The Last Critic - Setup Verification
echo ========================================
echo.

set "error_count=0"

echo [1/8] Checking project structure...
if exist "backend\main.py" (
    echo ✅ Backend main.py found
) else (
    echo ❌ Backend main.py missing
    set /a error_count+=1
)

if exist "frontend\package.json" (
    echo ✅ Frontend package.json found
) else (
    echo ❌ Frontend package.json missing
    set /a error_count+=1
)

echo.
echo [2/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found - Please install Python 3.8+
    set /a error_count+=1
) else (
    echo ✅ Python is installed
)

echo.
echo [3/8] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found - Please install Node.js 18+
    set /a error_count+=1
) else (
    echo ✅ Node.js is installed
)

echo.
echo [4/8] Checking backend dependencies...
if exist "backend\requirements.txt" (
    echo ✅ Backend requirements.txt found
) else (
    echo ❌ Backend requirements.txt missing
    set /a error_count+=1
)

echo.
echo [5/8] Checking frontend dependencies...
if exist "frontend\package.json" (
    echo ✅ Frontend package.json found
) else (
    echo ❌ Frontend package.json missing
    set /a error_count+=1
)

echo.
echo [6/8] Checking environment files...
if exist "backend\.env" (
    echo ✅ Backend .env found
) else (
    echo ⚠️  Backend .env missing (will use defaults)
)

if exist "frontend\.env.local" (
    echo ✅ Frontend .env.local found
) else (
    echo ⚠️  Frontend .env.local missing (will use defaults)
)

echo.
echo [7/8] Checking movie database...
if exist "backend\data\movies.csv" (
    echo ✅ Movie database CSV found
) else (
    echo ❌ Movie database CSV missing
    set /a error_count+=1
)

if exist "backend\data\additional_movies.py" (
    echo ✅ Additional movies database found
) else (
    echo ❌ Additional movies database missing
    set /a error_count+=1
)

echo.
echo [8/8] Checking startup scripts...
if exist "start-the-last-critic.bat" (
    echo ✅ Startup script found
) else (
    echo ❌ Startup script missing
    set /a error_count+=1
)

echo.
echo ========================================
if %error_count% equ 0 (
    echo 🎉 VERIFICATION PASSED!
    echo.
    echo The Last Critic is ready to run!
    echo.
    echo To start the application:
    echo 1. Double-click "start-the-last-critic.bat"
    echo 2. Wait for services to start
    echo 3. Open http://localhost:3000
    echo.
    echo For health checks, run "health-check.bat"
) else (
    echo ❌ VERIFICATION FAILED!
    echo.
    echo Found %error_count% error(s). Please fix them before running.
    echo.
    echo Common fixes:
    echo - Install Python 3.8+ from python.org
    echo - Install Node.js 18+ from nodejs.org
    echo - Ensure all files are properly extracted
)
echo ========================================
echo.
pause