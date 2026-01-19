# Logging & Debugging Guide

## Overview

The Media Downloader app includes comprehensive logging for debugging, troubleshooting, and understanding application behavior. Logs are written to both the console and disk files automatically.

## Log Locations

### Linux/Mac
```
~/.media_downloader/logs/app_YYYYMMDD_HHMMSS.log
```

### Windows
```
C:\Users\YourUsername\.media_downloader\logs\app_YYYYMMDD_HHMMSS.log
```

Each run of the application creates a new timestamped log file for easy tracking across sessions.

## Log Levels

- **DEBUG** - Detailed diagnostic information (file paths, command arguments, system checks)
- **INFO** - General application flow and major operations
- **WARNING** - Potentially problematic situations (missing optional components)
- **ERROR** - Error conditions with full exception tracebacks

## What Gets Logged

### Application Startup
```
============================================================
Media Downloader Starting
============================================================
Python: 3.10.12 (main, Jan  8 2026, 06:52:19) [GCC 11.4.0]
FFmpeg Path: /usr/bin/ffmpeg
PyQt6 Application initialized
```

### Video Download
```
Starting download: https://www.youtube.com/watch?v=...
Output template: /home/user/.media_downloader/downloads/%(title)s.%(ext)s
Download progress: 25.3%
Download finished: /home/user/.media_downloader/downloads/Video Title.mp4
```

### Media Processing
```
Getting duration for: /home/user/video.mp4
Duration: 125000ms
Exporting audio: segment_name.wav (5000ms - 15000ms)
FFmpeg command: ffmpeg -y -ss 00:00:05.000 -i /home/user/video.mp4 ...
Audio exported successfully: /home/user/segment_name.wav
```

### Error Scenarios
```
ERROR - File not found: /nonexistent/file.mp4
ERROR - ffprobe failed: No such file or directory
ERROR - Download failed: Video not available in your country
ERROR - Failed to parse duration output: [stderr output]
```

## Viewing Logs

### Real-time Console Output
When running the app from terminal, logs appear in real-time:
```bash
cd /home/endless/Portfolio/MediaDownloader
source venv/bin/activate
python src/main.py
```

### View Latest Log File
```bash
# Linux/Mac
tail -f ~/.media_downloader/logs/app_*.log

# Windows PowerShell
Get-Content $env:USERPROFILE\.media_downloader\logs\app_*.log -Tail 20 -Wait
```

### Search for Specific Issues
```bash
# Find all errors
grep ERROR ~/.media_downloader/logs/app_*.log

# Find download attempts
grep "Starting download" ~/.media_downloader/logs/app_*.log

# Find FFmpeg issues
grep -i ffmpeg ~/.media_downloader/logs/app_*.log
```

## Common Issues & Log Examples

### Issue: "Could not open media. FFmpeg error"
**What to check in logs:**
```
Getting duration for: /path/to/file.mp4
ffprobe error: No such file or directory
```
**Solution:** File doesn't exist or isn't readable. Check the path in the log.

### Issue: Download fails
**What to check in logs:**
```
Starting download: [URL]
Download failed: [error message]
```
**Common causes:** Invalid URL, no internet connection, video unavailable, region restrictions.

### Issue: Export produces no output
**What to check in logs:**
```
Exporting 3 segments (audio_only=False)
Exporting segment 1/3: Segment 1
FFmpeg command: ffmpeg -y -ss ...
FFmpeg error: [error message]
```
**Solution:** Check FFmpeg error message in logs to identify the issue.

### Issue: FFmpeg not found
**What to check in logs:**
```
FFmpeg not found in common locations, will use 'ffmpeg' from PATH
```
**Solution:** Install FFmpeg and add to PATH, or copy executable to app folder.

## Enabling More Detailed Logging

To capture additional debug information, you can modify `src/core/logger.py`:

```python
# Change the console handler level to DEBUG for more verbose output
console_handler.setLevel(logging.DEBUG)  # Changed from logging.INFO
```

Then restart the app to see all DEBUG-level messages on console.

## Log File Cleanup

Log files accumulate over time. To manage disk space:

```bash
# Delete logs older than 30 days
find ~/.media_downloader/logs -name "*.log" -mtime +30 -delete

# Keep only the last 10 logs
ls -t ~/.media_downloader/logs/app_*.log | tail -n +11 | xargs rm
```

## Example: Debugging a Download Issue

1. **Start the app and attempt download:**
   ```bash
   python src/main.py
   ```
   (Paste URL and click Download)

2. **Check the log file:**
   ```bash
   tail ~/.media_downloader/logs/app_*.log
   ```

3. **Look for the actual error:**
   ```
   Starting download: https://www.youtube.com/watch?v=abc123
   Download failed: Video is private
   ```

4. **Act on the information:** The video is private, so you need a valid URL.

## Example: Debugging an Export Issue

1. **Load video and create segments in UI**

2. **Check logs when export fails:**
   ```bash
   grep -A 5 "Exporting" ~/.media_downloader/logs/app_*.log
   ```

3. **Look for detailed FFmpeg error:**
   ```
   Exporting audio: my_segment.wav (0ms - 5000ms)
   FFmpeg command: ffmpeg -y -ss 00:00:00.000 -i /home/user/video.mp4 ...
   FFmpeg error: Encoder (aac) not found for output stream #0:1
   ```

4. **Resolve:** Install missing audio codec or use different format.

## Development Logging Tips

If you're adding new features:

```python
from core.logger import get_logger

logger = get_logger(__name__)

# In your function
logger.info(f"Processing video: {file_path}")
logger.debug(f"Video duration: {duration_ms}ms")
logger.warning(f"Audio codec not optimal: {codec}")
logger.error(f"Failed to process: {error}", exc_info=True)
```

The `exc_info=True` parameter automatically includes the full traceback, which is valuable for debugging exceptions.

## Log Format

Each log line follows this format:
```
TIMESTAMP - MODULE_NAME - LEVEL - MESSAGE
2026-01-18 18:06:43 - core.downloader - INFO - Starting download: https://...
```

- **TIMESTAMP**: When the event occurred (YYYY-MM-DD HH:MM:SS)
- **MODULE_NAME**: Which part of the code (e.g., core.downloader, ui.main_window)
- **LEVEL**: Severity (DEBUG, INFO, WARNING, ERROR)
- **MESSAGE**: What happened with relevant details
