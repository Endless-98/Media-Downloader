from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, pyqtSignal, QUrl


class VideoPlayer(QWidget):
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self._duration = 0
        self._setup_ui()
        self._setup_player()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.video_widget.setStyleSheet("background-color: #000;")
        layout.addWidget(self.video_widget, 1)
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_btn)
        
        self.time_label = QLabel("00:00")
        self.time_label.setFixedWidth(50)
        controls_layout.addWidget(self.time_label)
        
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.sliderMoved.connect(self._seek)
        self.seek_slider.sliderPressed.connect(self._on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self._on_slider_released)
        controls_layout.addWidget(self.seek_slider, 1)
        
        self.duration_label = QLabel("00:00")
        self.duration_label.setFixedWidth(50)
        controls_layout.addWidget(self.duration_label)
        
        layout.addLayout(controls_layout)
    
    def _setup_player(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)
        
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        
        self._slider_held = False
    
    def load(self, file_path: Path):
        self.player.setSource(QUrl.fromLocalFile(str(file_path)))
        self.player.pause()
    
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()
    
    def seek_to(self, position_ms: int):
        self.player.setPosition(position_ms)
    
    def get_position(self) -> int:
        return self.player.position()
    
    def get_duration(self) -> int:
        return self._duration
    
    def _seek(self, position: int):
        self.player.setPosition(position)
    
    def _on_slider_pressed(self):
        self._slider_held = True
    
    def _on_slider_released(self):
        self._slider_held = False
    
    def _on_position_changed(self, position: int):
        if not self._slider_held:
            self.seek_slider.setValue(position)
        self.time_label.setText(self._format_time(position))
        self.position_changed.emit(position)
    
    def _on_duration_changed(self, duration: int):
        self._duration = duration
        self.seek_slider.setRange(0, duration)
        self.duration_label.setText(self._format_time(duration))
        self.duration_changed.emit(duration)
    
    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")
    
    def _format_time(self, ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
