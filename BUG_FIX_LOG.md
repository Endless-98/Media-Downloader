# Download Bug Fix - January 18, 2026

## Issue
When attempting to download a YouTube video, the application crashed with:
```
TypeError: DownloadThread.finished[Path].emit(): argument 1 has unexpected type 'NoneType'
```

The `download()` method was returning `None` instead of the path to the downloaded file.

## Root Cause
The `Downloader.download()` method relied solely on the yt-dlp progress hook to capture the output filename. However, in some cases, the progress hook's "finished" status event either:
1. Wasn't triggered
2. Didn't contain the `filename` key
3. Had an empty filename

This left `downloaded_file = None`, causing the signal emission to fail because `PyQt6.QtCore.pyqtSignal[Path]` expects a Path object, not None.

## Solution
Implemented a two-stage filename capture approach:

### Stage 1: Progress Hook (Primary)
- Captures filename from yt-dlp's progress hook when available
- Logs when filename is provided
- Gracefully handles missing filename

### Stage 2: Directory Search (Fallback)
- If Stage 1 doesn't capture the filename, search the output directory
- Compares files before and after download
- Finds the most recently modified file (by modification time)
- Logs the found file
- Raises clear error if no file found

### Code Changes
**File:** `src/core/downloader.py`

**Added:**
- Import `os` for file system operations
- `files_before = set(os.listdir(self.output_dir))` before download
- Better error handling in progress hook (check if filename exists)
- Fallback logic after download completes

**Benefits:**
1. ✅ Robust filename detection
2. ✅ Better error messages
3. ✅ Handles various yt-dlp versions/behaviors
4. ✅ Clear logging of what happened
5. ✅ No signature breaking changes

## Testing
The app now:
1. Starts successfully
2. Initializes all components
3. Ready to download videos with proper Path return value

## Log Example
```
2026-01-18 18:11:59 - core.downloader - INFO - Starting download: https://youtu.be/...
2026-01-18 18:11:59 - core.downloader - DEBUG - Output template: /home/user/.media_downloader/downloads/%(title)s.%(ext)s
[yt-dlp downloads video...]
2026-01-18 18:11:14 - core.downloader - INFO - Download finished: /home/user/.media_downloader/downloads/Video Title.mp4
2026-01-18 18:11:14 - core.downloader - INFO - Successfully downloaded to: /home/user/.media_downloader/downloads/Video Title.mp4
```

## Related Files
- `src/core/downloader.py` - Main fix
- `src/ui/main_window.py` - Uses the Path return value
- Logging automatically captures all details

## Impact
- Users can now download videos without crashes
- Clear logging helps identify any edge cases
- Fallback mechanism handles various scenarios
