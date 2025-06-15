@echo off
:: filepath: c:\Dev\csm-attendance-system\run_app.bat
echo ========================================
echo CSM Attendance System - Startup Script
echo ========================================
echo.

:: Check if Python is installed
echo [INFO] Checking for Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python not found. Attempting to install Python...
    
    :: Download and install Python using PowerShell
    echo [INFO] Downloading Python installer...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python_installer.exe'}"
    
    if not exist "python_installer.exe" (
        echo [ERROR] Failed to download Python installer. Please install Python manually from https://www.python.org/
        pause
        exit /b 1
    )
    
    echo [INFO] Installing Python... This may take a few minutes.
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Clean up installer
    del python_installer.exe
    
    :: Refresh environment variables
    echo [INFO] Refreshing environment variables...
    call refreshenv >nul 2>&1
    
    :: Check if Python is now available
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python installation failed or Python is not in PATH. Please restart your command prompt or computer and try again.
        echo Alternatively, install Python manually from https://www.python.org/
        pause
        exit /b 1
    )
    
    echo [INFO] Python installed successfully.
) else (
    echo [INFO] Python found.
)

:: Display Python version
for /f "tokens=*" %%i in ('python --version') do echo [INFO] Using %%i

:: Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Virtual environment not found. Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Please ensure Python is installed and accessible.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully.
) else (
    echo [INFO] Virtual environment found.
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
echo [INFO] Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Please check your internet connection and requirements.txt file.
    pause
    exit /b 1
)

:: Check if main.py exists
if not exist "src\main.py" (
    echo [ERROR] main.py not found in src directory. Please ensure the file exists.
    pause
    exit /b 1
)

:: Check if test database exists
if not exist "src\test_database.csv" (
    echo [WARNING] test_database.csv not found in src directory. The application may not work properly.
    echo Please ensure the database file exists before running the application.
    pause
)

:: Navigate to src directory and run the application
echo [INFO] Starting CSM Attendance System...
echo.
cd src
python main.py

:: Return to original directory
cd ..

echo.
echo [INFO] Application closed.
pause