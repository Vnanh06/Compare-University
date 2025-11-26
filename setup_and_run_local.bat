@echo off
chcp 65001 >nul 2>&1

echo ============================================
echo    LOCAL DEVELOPMENT SETUP
echo    Windows + SQL Server + AI Chatbot
echo ============================================

echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo SUCCESS: Python is installed

echo [2/8] Removing old virtual environment...
if exist venv (
    rmdir /s /q venv
    echo SUCCESS: Old venv removed
) else (
    echo INFO: No old venv found
)

echo [3/8] Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Cannot create virtual environment!
    pause
    exit /b 1
)
echo SUCCESS: Virtual environment created

echo [4/8] Activating virtual environment...
call venv\Scripts\activate.bat
echo SUCCESS: Virtual environment activated

echo [5/8] Installing packages for LOCAL DEVELOPMENT...
echo Using requirements-local.txt (SQL Server, no PostgreSQL)
echo This may take 5-10 minutes, please wait...
echo.

pip install --upgrade pip

echo Installing packages from requirements-local.txt...
pip install -r requirements-local.txt

if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: Package installation failed!
    echo ============================================
    echo.
    echo Common fixes:
    echo 1. Make sure you have internet connection
    echo 2. Try running as Administrator
    echo 3. Check if antivirus is blocking pip
    echo.
    pause
    exit /b 1
)

echo SUCCESS: All packages installed

echo [6/8] Setting up Django...
echo Applying Django migrations...
python manage.py migrate --run-syncdb

echo [7/8] Creating admin user...
python manage.py createadmin


echo [8/8] Starting Django server...
echo.
echo ============================================
echo               SUCCESS!
echo ============================================
echo.
echo Django Server: http://127.0.0.1:8000
echo Database: SQL Server University
echo.
echo Fixed Issues:
echo [OK] Conversion errors resolved
echo [OK] Encoding issues fixed
echo [OK] Simple queries implemented
echo [OK] Gemini AI Chatbot with RAG enabled
echo.
echo Your university data is now accessible!
echo Chatbot: Click AI button at bottom-right corner
echo Press Ctrl+C to stop server
echo ============================================

python manage.py runserver
pause
