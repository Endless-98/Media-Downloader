from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class Segment:
    def __init__(self, name: str, start: int, end: int, color: QColor):
        self.name = name
        self.start = start
        self.end = end
        self.color = color


class Timeline(QWidget):
    segment_changed = pyqtSignal(int, int, int)
    segment_selected = pyqtSignal(int)
    
    COLORS = [
        QColor("#e94560"), QColor("#4ecca3"), QColor("#7b68ee"),
        QColor("#ff9f43"), QColor("#00cec9"), QColor("#fd79a8"),
    ]
    
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(80)
        self.setMouseTracking(True)
        
        self._duration = 1000
        self._position = 0
        self._segments: list[Segment] = []
        self._selected_segment = -1
        self._dragging = None
        self._hover_handle = None
    
    def set_duration(self, duration_ms: int):
        self._duration = max(duration_ms, 1)
        self.update()
    
    def set_position(self, position_ms: int):
        self._position = position_ms
        self.update()
    
    def add_segment(self, name: str, start: int, end: int) -> int:
        color = self.COLORS[len(self._segments) % len(self.COLORS)]
        self._segments.append(Segment(name, start, end, color))
        self._selected_segment = len(self._segments) - 1
        self.update()
        return self._selected_segment
    
    def remove_segment(self, index: int):
        if 0 <= index < len(self._segments):
            self._segments.pop(index)
            if self._selected_segment >= len(self._segments):
                self._selected_segment = len(self._segments) - 1
            self.update()
    
    def get_segment(self, index: int) -> tuple[str, int, int]:
        if 0 <= index < len(self._segments):
            seg = self._segments[index]
            return seg.name, seg.start, seg.end
        return "", 0, 0
    
    def update_segment_name(self, index: int, name: str):
        if 0 <= index < len(self._segments):
            self._segments[index].name = name
            self.update()
    
    def get_segments(self) -> list[tuple[str, int, int]]:
        return [(s.name, s.start, s.end) for s in self._segments]
    
    def clear_segments(self):
        self._segments.clear()
        self._selected_segment = -1
        self.update()
    
    def select_segment(self, index: int):
        self._selected_segment = index
        self.update()
    
    def _pos_to_time(self, x: int) -> int:
        margin = 10
        width = self.width() - 2 * margin
        return int((x - margin) / width * self._duration)
    
    def _time_to_pos(self, time_ms: int) -> int:
        margin = 10
        width = self.width() - 2 * margin
        return int(time_ms / self._duration * width + margin)
    
    def _get_handle_at(self, x: int, y: int):
        if y < 30 or y > 60:
            return None
        for i, seg in enumerate(self._segments):
            start_x = self._time_to_pos(seg.start)
            end_x = self._time_to_pos(seg.end)
            if abs(x - start_x) < 8:
                return (i, "start")
            if abs(x - end_x) < 8:
                return (i, "end")
        return None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self._get_handle_at(event.pos().x(), event.pos().y())
            if handle:
                self._dragging = handle
                self._selected_segment = handle[0]
                self.segment_selected.emit(handle[0])
            else:
                for i, seg in enumerate(self._segments):
                    start_x = self._time_to_pos(seg.start)
                    end_x = self._time_to_pos(seg.end)
                    if start_x <= event.pos().x() <= end_x and 30 <= event.pos().y() <= 60:
                        self._selected_segment = i
                        self.segment_selected.emit(i)
                        break
            self.update()
    
    def mouseMoveEvent(self, event):
        if self._dragging:
            idx, handle = self._dragging
            time = max(0, min(self._pos_to_time(event.pos().x()), self._duration))
            seg = self._segments[idx]
            
            if handle == "start" and time < seg.end - 100:
                seg.start = time
            elif handle == "end" and time > seg.start + 100:
                seg.end = time
            
            self.segment_changed.emit(idx, seg.start, seg.end)
            self.update()
        else:
            handle = self._get_handle_at(event.pos().x(), event.pos().y())
            if handle != self._hover_handle:
                self._hover_handle = handle
                self.setCursor(
                    Qt.CursorShape.SizeHorCursor if handle else Qt.CursorShape.ArrowCursor
                )
    
    def mouseReleaseEvent(self, event):
        self._dragging = None
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor("#16213e"))
        
        track_rect = QRectF(10, 30, self.width() - 20, 30)
        painter.fillRect(track_rect, QColor("#0f3460"))
        
        for i, seg in enumerate(self._segments):
            x1 = self._time_to_pos(seg.start)
            x2 = self._time_to_pos(seg.end)
            rect = QRectF(x1, 32, x2 - x1, 26)
            
            color = seg.color
            if i == self._selected_segment:
                painter.setPen(QPen(QColor("#fff"), 2))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                color = QColor(seg.color.red(), seg.color.green(), seg.color.blue(), 180)
            
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(rect, 3, 3)
            
            painter.setPen(QColor("#fff"))
            font = QFont()
            font.setPointSize(9)
            painter.setFont(font)
            text_rect = rect.adjusted(4, 0, -4, 0)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, seg.name)
        
        pos_x = self._time_to_pos(self._position)
        painter.setPen(QPen(QColor("#fff"), 2))
        painter.drawLine(int(pos_x), 25, int(pos_x), 65)
        
        painter.setPen(QColor("#8a8aaa"))
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        
        for i in range(5):
            time_ms = int(self._duration * i / 4)
            x = self._time_to_pos(time_ms)
            painter.drawLine(int(x), 65, int(x), 70)
            painter.drawText(int(x) - 20, 78, 40, 15, Qt.AlignmentFlag.AlignCenter, 
                           self._format_time(time_ms))
    
    def _format_time(self, ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
