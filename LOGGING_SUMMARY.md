# Logging Implementation Summary

## What Was Added

Comprehensive logging has been integrated throughout the application to help you understand what's happening and debug issues.

## Key Features

✅ **Dual Output:**
- Console output for real-time feedback
- Disk files for permanent records

✅ **Structured Logging:**
- Module-specific loggers (one per component)
- Clear timestamps and severity levels
- Full exception tracebacks on errors

✅ **Coverage:**
- Application startup and initialization
- YouTube download progress and completion
- Media file processing and FFmpeg commands
- UI interactions and state changes
- Error conditions with detailed diagnostics

## Log Files

Location: `~/.media_downloader/logs/`

Files are named: `app_YYYYMMDD_HHMMSS.log`

Each application run creates its own timestamped log file.

## Example Log Entry

```
2026-01-18 18:06:43 - core.downloader - INFO - Starting download: https://www.youtube.com/watch?v=abc123
```

Components:
- **Timestamp**: When it happened
- **Module**: Which component (`core.downloader`, `ui.main_window`, etc.)
- **Level**: Severity (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- **Message**: What happened with relevant context

## What Gets Logged

### On Startup
```
Python version
FFmpeg availability and path
Component initialization
Configuration
```

### During Download
```
URL being downloaded
Output directory
Progress percentages
Completion status
Any errors or warnings
```

### During Media Processing
```
File paths being processed
Segment information
FFmpeg commands being executed
Processing status and completion
Audio/video quality settings
```

### On Errors
```
Full exception type and message
Stack trace with file names and line numbers
Context about what was being done
Suggestions for resolution (where applicable)
```

## Finding Issues

The app logs provide enough information to identify:

1. **Missing dependencies**: FFmpeg not found, Python modules missing
2. **File access issues**: File not found, permission denied, disk full
3. **Invalid input**: Bad URLs, unsupported formats, corrupted files
4. **Processing failures**: FFmpeg errors, encoding issues, timeout problems
5. **UI problems**: Widget initialization, signal/slot issues

## Where to Start When Something Goes Wrong

1. **Check the latest log file:**
   ```bash
   tail ~/.media_downloader/logs/app_*.log
   ```

2. **Look for ERROR entries:**
   ```bash
   grep ERROR ~/.media_downloader/logs/app_*.log
   ```

3. **Search for the specific operation:**
   ```bash
   grep "download\|export\|loading" ~/.media_downloader/logs/app_*.log
   ```

## Log Levels

- **DEBUG**: Detailed technical information (file paths, configurations, internal state)
- **INFO**: Major operations and state changes (download started, video loaded, export complete)
- **WARNING**: Potentially problematic but non-fatal (missing optional components, suboptimal settings)
- **ERROR**: Failures that require user action (file not found, encoding failed, FFmpeg crashed)

## Future Enhancements

The logging system is designed to be expanded. You can:
- Add logs to new features easily
- Filter logs by module or level
- Export logs for crash reports
- Monitor app behavior in production

## Questions or Issues?

Check [LOGGING.md](LOGGING.md) for comprehensive debugging guidance with examples of common issues and their solutions.
