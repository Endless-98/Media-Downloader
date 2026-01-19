"""Path utilities for cross-platform app data directories."""
import sys
import os
from pathlib import Path


def get_app_data_dir() -> Path:
    """
    Get the appropriate application data directory for the current platform.
    
    Windows: %LOCALAPPDATA%/MediaDownloader
    Linux/Mac: ~/.local/share/MediaDownloader
    """
    if sys.platform == "win32":
        # Use Windows AppData/Local
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        app_dir = base / "MediaDownloader"
    else:
        # Use XDG standard on Linux/Mac
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        app_dir = base / "MediaDownloader"
    
    return app_dir


def get_downloads_dir() -> Path:
    """Get the directory where downloaded videos are stored."""
    downloads_dir = get_app_data_dir() / "Downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    return downloads_dir


def get_logs_dir() -> Path:
    """Get the directory where log files are stored."""
    logs_dir = get_app_data_dir() / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_exports_dir() -> Path:
    """
    Get the default directory for exported segments.
    Uses the user's Documents/MediaDownloader folder for easy access.
    """
    if sys.platform == "win32":
        # Use Documents folder on Windows
        docs = Path.home() / "Documents"
    else:
        # Use XDG Documents or fallback to home
        docs = Path(os.environ.get("XDG_DOCUMENTS_DIR", Path.home() / "Documents"))
    
    # Create MediaDownloader subfolder in Documents
    exports_dir = docs / "MediaDownloader"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir
