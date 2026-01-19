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
        
        # Track the final filename (after all post-processing)
        final_file = None
        files_before = set(os.listdir(self.output_dir)) if self.output_dir.exists() else set()
        logger.debug(f"Files before download: {files_before}")
        
        def progress_hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                if total > 0:
                    percent = (downloaded / total) * 100
                    logger.debug(f"Download progress: {percent:.1f}%")
                    if progress_callback:
                        progress_callback(downloaded / total, "Downloading...")
            elif d["status"] == "finished":
                logger.debug(f"Download phase finished: {d.get('filename', 'unknown')}")
                if progress_callback:
                    progress_callback(0.9, "Processing...")
            elif d["status"] == "error":
                logger.error(f"yt-dlp error in hook: {d.get('info_dict', {}).get('exception')}")
        
        def postprocessor_hook(d):
            nonlocal final_file
            # Capture the final filename after all post-processing (including merging)
            if d["status"] == "finished":
                if "info_dict" in d:
                    # Get the final filepath from info_dict
                    filepath = d["info_dict"].get("filepath")
                    if filepath:
                        final_file = Path(filepath)
                        logger.info(f"Post-processor finished, final file: {final_file}")
                if progress_callback:
                    progress_callback(1.0, "Complete!")
        
        opts = {
            # Format selection with multiple fallbacks
            # Priority: mp4 video+audio combo → best mp4 → best overall
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best",
            "outtmpl": output_template,
            "progress_hooks": [progress_hook],
            "postprocessor_hooks": [postprocessor_hook],
            # Merge to mp4 format
            "merge_output_format": "mp4",
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
            logger.debug(f"Final file from postprocessor hook: {final_file}")
            
            # Determine the actual downloaded file
            downloaded_file = None
            
            # First priority: use the postprocessor hook result if it exists
            if final_file and final_file.exists():
                downloaded_file = final_file
                logger.info(f"Using file from postprocessor hook: {downloaded_file}")
            else:
                # Fallback: find new files in directory
                logger.debug("Searching output directory for new files")
                new_files = files_after - files_before
                # Filter out partial/temp files
                new_files = {f for f in new_files if not f.endswith(('.part', '.ytdl', '.temp'))}
                logger.debug(f"New files detected: {new_files}")
                
                if new_files:
                    # Find the newest video file (prefer mp4)
                    video_extensions = ('.mp4', '.mkv', '.webm', '.avi')
                    video_files = [f for f in new_files if f.lower().endswith(video_extensions)]
                    
                    if video_files:
                        newest_file = max(
                            [self.output_dir / f for f in video_files],
                            key=lambda p: p.stat().st_mtime
                        )
                    else:
                        newest_file = max(
                            [self.output_dir / f for f in new_files],
                            key=lambda p: p.stat().st_mtime
                        )
                    downloaded_file = newest_file
                    logger.info(f"Found downloaded file via directory scan: {downloaded_file}")
                else:
                    logger.error(f"No new files found. Before: {files_before}, After: {files_after}")
                    logger.error(f"Output directory contents: {list(self.output_dir.iterdir())}")
                    raise RuntimeError("Download completed but output file not found")
            
            # Verify file exists and is not empty
            if not downloaded_file.exists():
                raise RuntimeError(f"Downloaded file does not exist: {downloaded_file}")
            
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
