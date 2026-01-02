@echo off
echo ========================================
echo    The Last Critic - Health Check
echo ========================================
echo.

echo [1/3] Checking Backend Health...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ❌ Backend is not responding at http://localhost:8000
    echo    Make sure the backend is running
) else (
    echo ✅ Backend is healthy at http://localhost:8000
)

echo.
echo [2/3] Checking Frontend...
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ❌ Frontend is not responding at http://localhost:3000
    echo    Make sure the frontend is running
) else (
    echo ✅ Frontend is accessible at http://localhost:3000
)

echo.
echo [3/3] Testing API Endpoints...
curl -s http://localhost:8000/api/movies?limit=1 >nul 2>&1
if errorlevel 1 (
    echo ❌ Movies API is not working
) else (
    echo ✅ Movies API is working
)

echo.
echo ========================================
echo Health Check Complete!
echo.
echo If all services are healthy, open:
echo http://localhost:3000
echo ========================================
echo.
pause