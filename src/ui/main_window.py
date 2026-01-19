from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLineEdit, QLabel, QProgressBar,
    QFileDialog, QMessageBox, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ui.styles import STYLESHEET
from ui.video_player import VideoPlayer
from ui.timeline import Timeline
from ui.segment_panel import SegmentPanel
from core.downloader import Downloader
from core.media_processor import MediaProcessor, Segment
from core.logger import get_logger
from core.paths import get_downloads_dir, get_exports_dir

logger = get_logger(__name__)


class DownloadThread(QThread):
    progress = pyqtSignal(float, str)
    finished = pyqtSignal(Path)
    error = pyqtSignal(str)
    
    def __init__(self, downloader: Downloader, url: str):
        super().__init__()
        self.downloader = downloader
        self.url = url
        logger.debug(f"DownloadThread created for: {url}")
    
    def run(self):
        try:
            logger.info("DownloadThread: Starting download")
            file_path = self.downloader.download(
                self.url, 
                lambda p, s: self.progress.emit(p, s)
            )
            logger.info(f"DownloadThread: Download complete: {file_path}")
            self.finished.emit(file_path)
        except Exception as e:
            logger.error(f"DownloadThread error: {e}", exc_info=True)
            self.error.emit(str(e))


class ExportThread(QThread):
    progress = pyqtSignal(float, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, processor: MediaProcessor, source: Path, 
                 output_dir: Path, segments: list[Segment], audio_only: bool):
        super().__init__()
        self.processor = processor
        self.source = source
        self.output_dir = output_dir
        self.segments = segments
        self.audio_only = audio_only
        logger.debug(f"ExportThread created. Source: {source}, Segments: {len(segments)}")
    
    def run(self):
        try:
            logger.info("ExportThread: Starting export")
            outputs = self.processor.export_segments(
                self.source, self.output_dir, self.segments,
                self.audio_only, lambda p, s: self.progress.emit(p, s)
            )
            logger.info(f"ExportThread: Export complete. Outputs: {len(outputs)}")
            self.finished.emit(outputs)
        except Exception as e:
            logger.error(f"ExportThread error: {e}", exc_info=True)
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("MainWindow: Initializing")
        self.setWindowTitle("Media Downloader")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(STYLESHEET)
        
        download_dir = get_downloads_dir()
        logger.info(f"Download directory: {download_dir}")
        self.downloader = Downloader(download_dir)
        
        self.processor = MediaProcessor()
        self.current_file: Path = None
        self.download_thread = None
        self.export_thread = None
        
        self._setup_ui()
        self._connect_signals()
        logger.info("MainWindow: Ready")
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        header = QHBoxLayout()
        title = QLabel("Media Downloader")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        
        self.load_btn = QPushButton("Load File")
        self.load_btn.setObjectName("secondaryBtn")
        self.load_btn.clicked.connect(self._load_file)
        header.addWidget(self.load_btn)
        layout.addLayout(header)
        
        url_layout = QHBoxLayout()
        url_layout.setSpacing(10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL...")
        url_layout.addWidget(self.url_input, 1)
        
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self._start_download)
        url_layout.addWidget(self.download_btn)
        
        layout.addLayout(url_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        self.status_label.setObjectName("subtitle")
        self.status_label.hide()
        layout.addWidget(self.status_label)
        
        content = QHBoxLayout()
        content.setSpacing(16)
        
        editor_layout = QVBoxLayout()
        editor_layout.setSpacing(12)
        
        self.player = VideoPlayer()
        editor_layout.addWidget(self.player, 1)
        
        self.timeline = Timeline()
        editor_layout.addWidget(self.timeline)
        
        content.addLayout(editor_layout, 1)
        
        self.segment_panel = SegmentPanel()
        content.addWidget(self.segment_panel)
        
        layout.addLayout(content, 1)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #0f3460;")
        layout.addWidget(separator)
        
        export_layout = QHBoxLayout()
        export_layout.setSpacing(12)
        
        self.audio_only = QCheckBox("Audio Only (.wav)")
        export_layout.addWidget(self.audio_only)
        
        export_layout.addStretch()
        
        self.export_btn = QPushButton("Export Segments")
        self.export_btn.clicked.connect(self._export_segments)
        export_layout.addWidget(self.export_btn)
        
        layout.addLayout(export_layout)
    
    def _connect_signals(self):
        self.player.position_changed.connect(self.timeline.set_position)
        self.player.duration_changed.connect(self.timeline.set_duration)
        
        self.segment_panel.add_segment.connect(self._add_segment)
        self.segment_panel.remove_segment.connect(self._remove_segment)
        self.segment_panel.segment_selected.connect(self._on_segment_selected)
        self.segment_panel.name_changed.connect(self._on_name_changed)
        self.segment_panel.set_start.connect(self._set_segment_start)
        self.segment_panel.set_end.connect(self._set_segment_end)
        
        self.timeline.segment_selected.connect(self._on_timeline_segment_selected)
        self.timeline.segment_changed.connect(self._on_segment_bounds_changed)
    
    def _start_download(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.show()
        
        self.download_thread = DownloadThread(self.downloader, url)
        self.download_thread.progress.connect(self._on_download_progress)
        self.download_thread.finished.connect(self._on_download_finished)
        self.download_thread.error.connect(self._on_download_error)
        self.download_thread.start()
    
    def _on_download_progress(self, progress: float, status: str):
        self.progress_bar.setValue(int(progress * 100))
        self.status_label.setText(status)
    
    def _on_download_finished(self, file_path: Path):
        self.download_btn.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText(f"Downloaded to: {file_path.parent}\\{file_path.name}")
        logger.info(f"Download complete, auto-loading video: {file_path}")
        self._load_video(file_path)
    
    def _on_download_error(self, error: str):
        self.download_btn.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.hide()
        QMessageBox.critical(self, "Download Error", error)
    
    def _load_file(self):
        # Start in downloads directory where videos are saved
        start_dir = get_downloads_dir()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video", str(start_dir),
            "Video Files (*.mp4 *.mkv *.webm *.avi);;All Files (*)"
        )
        if file_path:
            self._load_video(Path(file_path))
    
    def _load_video(self, file_path: Path):
        logger.info(f"Loading video: {file_path}")
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            QMessageBox.critical(self, "Error", f"File not found: {file_path}")
            return
        
        try:
            self.current_file = file_path
            self.player.load(file_path)
            self.timeline.clear_segments()
            self.segment_panel.clear_segments()
            self.status_label.setText(f"Loaded: {file_path.name}")
            self.status_label.show()
            logger.info(f"Video loaded successfully: {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to load video: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load video: {e}")
    
    def _add_segment(self):
        if not self.current_file:
            return
        
        duration = self.player.get_duration()
        position = self.player.get_position()
        
        segments = self.timeline.get_segments()
        name = f"Segment {len(segments) + 1}"
        
        end = min(position + 10000, duration)
        start = position
        
        self.timeline.add_segment(name, start, end)
        self.segment_panel.add_segment_item(name, start, end)
        self.segment_panel.set_segment_name(name)
    
    def _remove_segment(self, index: int):
        self.timeline.remove_segment(index)
        self.segment_panel.remove_segment_item(index)
    
    def _on_segment_selected(self, index: int):
        self.timeline.select_segment(index)
        if index >= 0:
            name, start, end = self.timeline.get_segment(index)
            self.segment_panel.set_segment_name(name)
    
    def _on_timeline_segment_selected(self, index: int):
        self.segment_panel.select_segment(index)
        if index >= 0:
            name, start, end = self.timeline.get_segment(index)
            self.segment_panel.set_segment_name(name)
    
    def _on_name_changed(self, index: int, name: str):
        self.timeline.update_segment_name(index, name)
        _, start, end = self.timeline.get_segment(index)
        self.segment_panel.update_segment_item(index, name, start, end)
    
    def _on_segment_bounds_changed(self, index: int, start: int, end: int):
        name, _, _ = self.timeline.get_segment(index)
        self.segment_panel.update_segment_item(index, name, start, end)
    
    def _set_segment_start(self):
        segments = self.timeline.get_segments()
        if not segments:
            return
        idx = self.segment_panel.segment_list.currentRow()
        if idx < 0:
            return
        
        position = self.player.get_position()
        name, _, end = self.timeline.get_segment(idx)
        if position < end - 100:
            self.timeline._segments[idx].start = position
            self.timeline.update()
            self.segment_panel.update_segment_item(idx, name, position, end)
    
    def _set_segment_end(self):
        segments = self.timeline.get_segments()
        if not segments:
            return
        idx = self.segment_panel.segment_list.currentRow()
        if idx < 0:
            return
        
        position = self.player.get_position()
        name, start, _ = self.timeline.get_segment(idx)
        if position > start + 100:
            self.timeline._segments[idx].end = position
            self.timeline.update()
            self.segment_panel.update_segment_item(idx, name, start, position)
    
    def _export_segments(self):
        segments_data = self.timeline.get_segments()
        if not segments_data or not self.current_file:
            QMessageBox.warning(self, "Export", "No segments to export.")
            return
        
        # Default to Documents/MediaDownloader for easy access
        default_export_dir = get_exports_dir()
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select Export Folder", str(default_export_dir)
        )
        if not output_dir:
            return
        
        segments = [
            Segment(name=s[0], start_ms=s[1], end_ms=s[2]) 
            for s in segments_data
        ]
        
        self.export_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.show()
        
        self.export_thread = ExportThread(
            self.processor, self.current_file, Path(output_dir),
            segments, self.audio_only.isChecked()
        )
        self.export_thread.progress.connect(self._on_download_progress)
        self.export_thread.finished.connect(self._on_export_finished)
        self.export_thread.error.connect(self._on_export_error)
        self.export_thread.start()
    
    def _on_export_finished(self, outputs: list):
        self.export_btn.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText(f"Exported {len(outputs)} segment(s)")
        QMessageBox.information(
            self, "Export Complete", 
            f"Successfully exported {len(outputs)} segment(s)."
        )
    
    def _on_export_error(self, error: str):
        self.export_btn.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.hide()
        QMessageBox.critical(self, "Export Error", error)
