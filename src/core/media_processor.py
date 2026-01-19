import subprocess
import shutil
import sys
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)


def get_bundled_path() -> Path:
    """Get the path to bundled resources (for PyInstaller builds)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent.parent.parent


@dataclass
class Segment:
    name: str
    start_ms: int
    end_ms: int


class MediaProcessor:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        logger.info(f"MediaProcessor initialized. FFmpeg path: {self.ffmpeg_path}")
    
    def _find_ffmpeg(self) -> str:
        # First check if bundled with the app (PyInstaller)
        if getattr(sys, 'frozen', False):
            bundled_ffmpeg = Path(sys._MEIPASS) / "ffmpeg.exe"
            if bundled_ffmpeg.exists():
                logger.debug(f"Found bundled ffmpeg: {bundled_ffmpeg}")
                return str(bundled_ffmpeg)
            # Also check same directory as executable
            exe_dir = Path(sys.executable).parent
            exe_ffmpeg = exe_dir / "ffmpeg.exe"
            if exe_ffmpeg.exists():
                logger.debug(f"Found ffmpeg next to exe: {exe_ffmpeg}")
                return str(exe_ffmpeg)
        
        # Check PATH
        path = shutil.which("ffmpeg")
        if path:
            logger.debug(f"Found ffmpeg in PATH: {path}")
            return path
        
        logger.debug("FFmpeg not in PATH, checking common locations...")
        common_paths = [
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
            Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
            Path.home() / "ffmpeg" / "bin" / "ffmpeg.exe",
            Path("/usr/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
        ]
        for p in common_paths:
            if p.exists():
                logger.debug(f"Found ffmpeg at: {p}")
                return str(p)
        logger.warning("FFmpeg not found in common locations, will use 'ffmpeg' from PATH")
        return "ffmpeg"
    
    def _ms_to_timestamp(self, ms: int) -> str:
        seconds = ms // 1000
        millis = ms % 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def get_duration_ms(self, file_path: Path) -> int:
        logger.debug(f"Getting duration for: {file_path}")
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ffprobe = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
        cmd = [
            ffprobe, "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
        ]
        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"ffprobe error: {result.stderr}")
            raise RuntimeError(f"ffprobe failed: {result.stderr}")
        
        try:
            duration_ms = int(float(result.stdout.strip()) * 1000)
            logger.debug(f"Duration: {duration_ms}ms")
            return duration_ms
        except ValueError as e:
            logger.error(f"Failed to parse duration output: {result.stdout}")
            raise
    
    def export_video(
        self,
        source: Path,
        output: Path,
        start_ms: int,
        end_ms: int,
        progress_callback: Optional[callable] = None
    ) -> Path:
        logger.info(f"Exporting video: {output.name} ({start_ms}ms - {end_ms}ms)")
        
        if not source.exists():
            logger.error(f"Source file not found: {source}")
            raise FileNotFoundError(f"Source file not found: {source}")
        
        output.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            self.ffmpeg_path, "-y",
            "-ss", self._ms_to_timestamp(start_ms),
            "-i", str(source),
            "-t", self._ms_to_timestamp(end_ms - start_ms),
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac",
            str(output)
        ]
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise RuntimeError(f"Video export failed: {result.stderr}")
            logger.info(f"Video exported successfully: {output}")
            return output
        except Exception as e:
            logger.error(f"Video export failed: {e}", exc_info=True)
            raise
    
    def export_audio(
        self,
        source: Path,
        output: Path,
        start_ms: int,
        end_ms: int,
        progress_callback: Optional[callable] = None
    ) -> Path:
        logger.info(f"Exporting audio: {output.name} ({start_ms}ms - {end_ms}ms)")
        
        if not source.exists():
            logger.error(f"Source file not found: {source}")
            raise FileNotFoundError(f"Source file not found: {source}")
        
        output.parent.mkdir(parents=True, exist_ok=True)
        wav_output = output.with_suffix(".wav")
        cmd = [
            self.ffmpeg_path, "-y",
            "-ss", self._ms_to_timestamp(start_ms),
            "-i", str(source),
            "-t", self._ms_to_timestamp(end_ms - start_ms),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            str(wav_output)
        ]
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise RuntimeError(f"Audio export failed: {result.stderr}")
            logger.info(f"Audio exported successfully: {wav_output}")
            return wav_output
        except Exception as e:
            logger.error(f"Audio export failed: {e}", exc_info=True)
            raise
    
    def export_segments(
        self,
        source: Path,
        output_dir: Path,
        segments: list[Segment],
        audio_only: bool = False,
        progress_callback: Optional[callable] = None
    ) -> list[Path]:
        logger.info(f"Exporting {len(segments)} segments (audio_only={audio_only})")
        output_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        
        for i, seg in enumerate(segments):
            logger.debug(f"Exporting segment {i+1}/{len(segments)}: {seg.name}")
            if progress_callback:
                progress_callback((i + 1) / len(segments), f"Exporting: {seg.name}")
            
            ext = ".wav" if audio_only else ".mp4"
            output_path = output_dir / f"{seg.name}{ext}"
            
            try:
                if audio_only:
                    self.export_audio(source, output_path, seg.start_ms, seg.end_ms)
                else:
                    self.export_video(source, output_path, seg.start_ms, seg.end_ms)
                outputs.append(output_path)
            except Exception as e:
                logger.error(f"Failed to export segment {seg.name}: {e}", exc_info=True)
                raise
        
        logger.info(f"Successfully exported {len(outputs)} segments")
        return outputs
