from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QLineEdit, QLabel, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal


class SegmentPanel(QWidget):
    add_segment = pyqtSignal()
    remove_segment = pyqtSignal(int)
    segment_selected = pyqtSignal(int)
    name_changed = pyqtSignal(int, str)
    set_start = pyqtSignal()
    set_end = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(280)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        header = QLabel("Segments")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #e94560;")
        layout.addWidget(header)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        
        self.add_btn = QPushButton("+ Add")
        self.add_btn.clicked.connect(self.add_segment.emit)
        btn_layout.addWidget(self.add_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setObjectName("secondaryBtn")
        self.remove_btn.clicked.connect(self._on_remove)
        btn_layout.addWidget(self.remove_btn)
        
        layout.addLayout(btn_layout)
        
        self.segment_list = QListWidget()
        self.segment_list.currentRowChanged.connect(self._on_selection_changed)
        layout.addWidget(self.segment_list, 1)
        
        edit_label = QLabel("Segment Name:")
        edit_label.setStyleSheet("font-size: 12px; color: #8a8aaa;")
        layout.addWidget(edit_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter name...")
        self.name_edit.textChanged.connect(self._on_name_changed)
        layout.addWidget(self.name_edit)
        
        marker_layout = QHBoxLayout()
        marker_layout.setSpacing(6)
        
        self.start_btn = QPushButton("Set Start")
        self.start_btn.setObjectName("secondaryBtn")
        self.start_btn.clicked.connect(self.set_start.emit)
        marker_layout.addWidget(self.start_btn)
        
        self.end_btn = QPushButton("Set End")
        self.end_btn.setObjectName("secondaryBtn")
        self.end_btn.clicked.connect(self.set_end.emit)
        marker_layout.addWidget(self.end_btn)
        
        layout.addLayout(marker_layout)
    
    def add_segment_item(self, name: str, start_ms: int, end_ms: int):
        time_str = f"{self._format_time(start_ms)} - {self._format_time(end_ms)}"
        item = QListWidgetItem(f"{name}\n{time_str}")
        self.segment_list.addItem(item)
        self.segment_list.setCurrentRow(self.segment_list.count() - 1)
    
    def update_segment_item(self, index: int, name: str, start_ms: int, end_ms: int):
        if 0 <= index < self.segment_list.count():
            time_str = f"{self._format_time(start_ms)} - {self._format_time(end_ms)}"
            self.segment_list.item(index).setText(f"{name}\n{time_str}")
    
    def remove_segment_item(self, index: int):
        if 0 <= index < self.segment_list.count():
            self.segment_list.takeItem(index)
    
    def clear_segments(self):
        self.segment_list.clear()
        self.name_edit.clear()
    
    def select_segment(self, index: int):
        self.segment_list.blockSignals(True)
        self.segment_list.setCurrentRow(index)
        self.segment_list.blockSignals(False)
    
    def set_segment_name(self, name: str):
        self.name_edit.blockSignals(True)
        self.name_edit.setText(name)
        self.name_edit.blockSignals(False)
    
    def _on_selection_changed(self, row: int):
        self.segment_selected.emit(row)
    
    def _on_remove(self):
        row = self.segment_list.currentRow()
        if row >= 0:
            self.remove_segment.emit(row)
    
    def _on_name_changed(self, text: str):
        row = self.segment_list.currentRow()
        if row >= 0:
            self.name_changed.emit(row, text)
    
    def _format_time(self, ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
