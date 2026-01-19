@echo off
echo Building Media Downloader for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Build the executable
echo.
echo Building executable...
pyinstaller --clean MediaDownloader.spec

echo.
echo Build complete! Executable is in dist\MediaDownloader.exe
echo.
echo NOTE: FFmpeg must be installed and in PATH for video processing.
echo Download from: https://ffmpeg.org/download.html
echo.
pause
