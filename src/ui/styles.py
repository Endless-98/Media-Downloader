STYLESHEET = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    color: #eaeaea;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QLineEdit {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 10px 14px;
    color: #eaeaea;
    font-size: 14px;
}

QLineEdit:focus {
    border-color: #e94560;
}

QPushButton {
    background-color: #e94560;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    color: white;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #ff6b6b;
}

QPushButton:pressed {
    background-color: #c73e54;
}

QPushButton:disabled {
    background-color: #4a4a6a;
    color: #8a8a8a;
}

QPushButton#secondaryBtn {
    background-color: #0f3460;
}

QPushButton#secondaryBtn:hover {
    background-color: #16213e;
}

QProgressBar {
    background-color: #16213e;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #e94560;
    border-radius: 4px;
}

QSlider::groove:horizontal {
    background: #16213e;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #e94560;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::sub-page:horizontal {
    background: #e94560;
    border-radius: 3px;
}

QListWidget {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #e94560;
}

QListWidget::item:hover {
    background-color: #0f3460;
}

QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #e94560;
}

QLabel#subtitle {
    font-size: 12px;
    color: #8a8aaa;
}

QGroupBox {
    border: 2px solid #0f3460;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #e94560;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #0f3460;
    background-color: #16213e;
}

QCheckBox::indicator:checked {
    background-color: #e94560;
    border-color: #e94560;
}

QScrollBar:vertical {
    background: #16213e;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""
