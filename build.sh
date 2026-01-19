#!/bin/bash

echo "Building Media Downloader..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Build the executable
echo
echo "Building executable..."
pyinstaller --clean MediaDownloader.spec

echo
echo "Build complete! Executable is in dist/MediaDownloader"
echo
echo "NOTE: FFmpeg must be installed for video processing."
echo "Install with: sudo apt install ffmpeg"
