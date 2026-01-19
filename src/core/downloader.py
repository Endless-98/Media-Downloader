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
            # Format selection with multiple fallbacks
            # Priority: mp4 video+audio combo → best mp4 → best overall
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best",
            "outtmpl": output_template,
            "progress_hooks": [progress_hook],
            "quiet": False,
            "no_warnings": False,
            # Increase socket timeout for slow/unreliable connections
            "socket_timeout": 30,
            # Retry failed fragments
            "retries": 3,
            "fragment_retries": 3,
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
            
            # Verify file is not empty
            if downloaded_file.exists():
                file_size = downloaded_file.stat().st_size
                logger.info(f"Downloaded file size: {file_size} bytes")
                
                if file_size == 0:
                    logger.error(f"Downloaded file is empty: {downloaded_file}")
                    downloaded_file.unlink()  # Delete empty file
                    raise RuntimeError(
                        "Downloaded file is empty. This usually means:\n"
                        "- Video is geo-blocked\n"
                        "- Content is age-restricted\n"
                        "- Video is temporarily unavailable\n"
                        "- Network connection was interrupted\n\n"
                        "Try a different video or check your internet connection."
                    )
            else:
                raise RuntimeError(f"Downloaded file no longer exists: {downloaded_file}")
            
            logger.info(f"Successfully downloaded to: {downloaded_file}")
            return downloaded_file
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            logger.error(f"yt-dlp download error: {error_msg}")
            
            # Provide helpful error messages based on error type
            if "empty" in error_msg.lower():
                raise RuntimeError(
                    "Download produced an empty file. This usually means:\n"
                    "- Video is geo-blocked or restricted\n"
                    "- Video requires authentication\n"
                    "- Video is temporarily unavailable\n"
                    "- Network connection was interrupted\n\n"
                    "Try a different video or check your internet connection."
                )
            elif "age" in error_msg.lower() or "restricted" in error_msg.lower():
                raise RuntimeError(f"Video is age-restricted or restricted: {error_msg}")
            elif "not found" in error_msg.lower() or "no such file" in error_msg.lower():
                raise RuntimeError(f"Video not found or no longer available: {error_msg}")
            else:
                raise RuntimeError(f"Failed to download video: {error_msg}")
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
