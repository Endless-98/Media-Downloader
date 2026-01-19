import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.logger import setup_logging, get_logger
from ui.main_window import MainWindow

logger = get_logger(__name__)


def main():
    setup_logging()
    logger.info("="*60)
    logger.info("Media Downloader Starting")
    logger.info("="*60)
    logger.info(f"Python: {sys.version}")
    logger.info(f"FFmpeg Path: {os.popen('which ffmpeg').read().strip() or 'Not found in PATH'}")
    
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        app = QApplication(sys.argv)
        app.setApplicationName("Media Downloader")
        app.setStyle("Fusion")
        
        logger.info("PyQt6 Application initialized")
        
        window = MainWindow()
        window.show()
        logger.info("Main window displayed")
        
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
