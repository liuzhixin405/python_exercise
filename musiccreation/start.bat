@echo off
echo ========================================
echo         FeedMusic Project Startup Script
echo ========================================
echo.

echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please install Python 3.8+
    pause
    exit /b 1
)

echo Checking Node.js environment...
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found, please install Node.js 16+
    pause
    exit /b 1
)

echo Environment check completed!
echo.

echo Starting backend services...
cd backend
echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Warning: Dependency installation may have issues, but continuing...
)

echo Starting Flask backend service...
start "FeedMusic Backend" python app.py

echo Waiting for backend service to start...
timeout /t 5 /nobreak >nul

echo Starting admin panel...
start "FeedMusic Admin" python run_admin.py

echo Waiting for admin panel to start...
timeout /t 3 /nobreak >nul

echo Starting frontend service...
cd ../frontend
echo Installing Node.js dependencies...
call npm install
if errorlevel 1 (
    echo Warning: Dependency installation may have issues, but continuing...
)

echo Starting React frontend service...
start "FeedMusic Frontend" cmd /k "npm start"

echo.
echo ========================================
echo           Services Started Successfully!
echo ========================================
echo Backend API: http://localhost:5000
echo Admin Panel: http://localhost:5001
echo Frontend App: http://localhost:3000
echo.
echo Press any key to close this window...
echo Note: Services will continue running in background
pause >nul 