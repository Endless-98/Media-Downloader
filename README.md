# Media Downloader

A clean, modern desktop app for downloading YouTube videos and extracting/trimming segments.

## Features

- **Download YouTube Videos** - Paste a URL and download in best quality
- **Video Preview** - Built-in video player with playback controls
- **Segment Editor** - Create multiple named segments with visual timeline
- **Easy Trimming** - Drag handles or use "Set Start/End" buttons
- **Flexible Export** - Export as video (.mp4) or audio (.wav)
- **Batch Export** - Export all segments at once with custom names

## Quick Start (Windows)

**Option 1: Download Pre-built Release**
1. Go to [Releases](../../releases) and download `MediaDownloader.exe`
2. Double-click to run - no installation needed!

**Option 2: Build via GitHub Actions**
1. Push this repo to GitHub
2. Go to Actions → "Build Windows Executable" → Run workflow
3. Download the artifact `MediaDownloader-Windows.zip`
4. Extract and run `MediaDownloader.exe`

The Windows build includes FFmpeg bundled - **no additional software required**.

## Building Locally

### Windows (Local Build)

```batch
build.bat
```

Note: Local Windows builds require FFmpeg installed. The GitHub Actions build bundles FFmpeg automatically.

### Linux

```bash
sudo apt install ffmpeg
chmod +x build.sh
./build.sh
```

### Development

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python src/main.py
```

## Usage

1. **Download a Video:**
   - Paste a YouTube URL in the input field
   - Click "Download"
   - Video is automatically loaded when download completes
   - Downloaded videos are saved to `%LOCALAPPDATA%\MediaDownloader\Downloads` (Windows) or `~/.local/share/MediaDownloader/Downloads` (Linux)

2. **Load Existing File:**
   - Click "Load File" to browse and open a local video
   - File browser starts in your downloads folder for convenience

3. **Create Segments:**
   - Click "+ Add" to create a segment at current position
   - Drag the segment handles on the timeline to adjust
   - Or use "Set Start" / "Set End" at the current playhead position
   - Edit the segment name in the text field

4. **Export:**
   - Check "Audio Only (.wav)" if you only want audio
   - Click "Export Segments"
   - Default export location: `Documents\MediaDownloader` (easy to find!)
   - All segments will be exported with their names

## File Locations

**Windows:**
- Downloads: `%LOCALAPPDATA%\MediaDownloader\Downloads` (e.g., `C:\Users\YourName\AppData\Local\MediaDownloader\Downloads`)
- Exports: `Documents\MediaDownloader`
- Logs: `%LOCALAPPDATA%\MediaDownloader\Logs`

**Linux:**
- Downloads: `~/.local/share/MediaDownloader/Downloads`
- Exports: `~/Documents/MediaDownloader`
- Logs: `~/.local/share/MediaDownloader/Logs`

## Debugging & Logs

The app creates detailed logs for all operations. See [LOGGING.md](LOGGING.md) for:
- Where to find logs
- What information is logged
- How to troubleshoot common issues
- Viewing and searching logs

## Project Structure

```
MediaDownloader/
├── src/
│   ├── main.py              # Entry point
│   ├── core/
│   │   ├── downloader.py    # YouTube download logic
│   │   └── media_processor.py # FFmpeg trimming/conversion
│   └── ui/
│       ├── main_window.py   # Main application window
│       ├── video_player.py  # Video playback widget
│       ├── timeline.py      # Visual timeline with segments
│       ├── segment_panel.py # Segment list and controls
│       └── styles.py        # UI stylesheet
├── requirements.txt
├── MediaDownloader.spec     # PyInstaller config
├── build.bat               # Windows build script
└── build.sh                # Linux build script
```

## Extending

The modular architecture makes it easy to add features:

- **New sources:** Add downloaders in `core/` following the `Downloader` pattern
- **Export formats:** Extend `MediaProcessor` with new format methods
- **UI features:** Components are separated in `ui/` for easy modification

## License

MIT
