from pathlib import Path
from typing import Callable, Optional
import yt_dlp
import os
from .logger import get_logger

logger = get_logger(__name__)


class Downloader:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloader initialized with output dir: {self.output_dir}")
    
    def download(
        self,
        url: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Path:
        logger.info(f"Starting download: {url}")
        output_template = str(self.output_dir / "%(title)s.%(ext)s")
        logger.debug(f"Output template: {output_template}")
        logger.debug(f"Output directory: {self.output_dir}")
        logger.debug(f"Output directory exists: {self.output_dir.exists()}")
        
        downloaded_file = None
        files_before = set(os.listdir(self.output_dir)) if self.output_dir.exists() else set()
        logger.debug(f"Files before download: {files_before}")
        
        def progress_hook(d):
            nonlocal downloaded_file
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    percent = (downloaded / total) * 100
                    logger.debug(f"Download progress: {percent:.1f}%")
                    if progress_callback:
                        progress_callback(downloaded / total, "Downloading...")
            elif d["status"] == "finished":
                if "filename" in d and d["filename"]:
                    downloaded_file = Path(d["filename"])
                    logger.info(f"Download finished (from hook): {downloaded_file}")
                else:
                    logger.debug("Progress hook finished but no filename provided")
                if progress_callback:
                    progress_callback(1.0, "Processing...")
            elif d["status"] == "error":
                logger.error(f"yt-dlp error in hook: {d.get('info_dict', {}).get('exception')}")
        
        opts = {
            "format": "best",
            "outtmpl": output_template,
            "progress_hooks": [progress_hook],
            "quiet": False,
            "no_warnings": False,
        }
        
        try:
            logger.debug(f"yt-dlp options: format={opts['format']}, outtmpl={opts['outtmpl']}")
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.download([url])
                logger.debug(f"yt-dlp download returned: {info}")
            
            # Check directory contents after download
            files_after = set(os.listdir(self.output_dir)) if self.output_dir.exists() else set()
            logger.debug(f"Files after download: {files_after}")
            
            if downloaded_file is None:
                logger.debug("Filename not captured from hook, searching output directory")
                new_files = files_after - files_before
                logger.debug(f"New files detected: {new_files}")
                
                if new_files:
                    newest_file = max(
                        [self.output_dir / f for f in new_files],
                        key=lambda p: p.stat().st_mtime
                    )
                    downloaded_file = newest_file
                    logger.info(f"Found downloaded file: {downloaded_file}")
                else:
                    logger.error(f"No new files found. Before: {files_before}, After: {files_after}")
                    logger.error(f"Output directory contents: {list(self.output_dir.iterdir())}")
                    raise RuntimeError("Download completed but output file not found")
            
            logger.info(f"Successfully downloaded to: {downloaded_file}")
            return downloaded_file
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"yt-dlp download error: {e}")
            logger.error("This may be due to: geo-blocking, age restriction, video unavailable, or network issues")
            raise RuntimeError(f"Failed to download video: {str(e)}")
        except Exception as e:
            logger.error(f"Download failed: {e}", exc_info=True)
            raise
    
    def get_video_info(self, url: str) -> dict:
        logger.debug(f"Fetching video info: {url}")
        opts = {"quiet": True, "no_warnings": True, "extract_flat": False}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                logger.debug(f"Video info: title={info.get('title')}, duration={info.get('duration')}s")
                return info
        except Exception as e:
            logger.error(f"Failed to fetch video info: {e}", exc_info=True)
            raise
