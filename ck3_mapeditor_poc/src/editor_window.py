"""
EditorWindow - Окно редактирования изображений

Функционал:
- Отображение provinces.png
- Инструменты рисования (brush, bucket, eraser)
- Zoom: от 25% до 1600%
- Pan: drag с зажатой средней кнопкой мыши
- Grid: опциональная сетка для точности
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, 
    QGraphicsPixmapItem, QApplication
)
from PyQt6.QtGui import QPixmap, QImage, QCursor, QColor, QPainter
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
import numpy as np
from typing import Optional, Tuple

from .tools.brush_tool import BrushTool
from .tools.bucket_tool import BucketTool
from .tools.picker_tool import PickerTool
from .tools.base_tool import Tool


class EditorGraphicsView(QGraphicsView):
    """Графическое представление для редактора с поддержкой зума и панорамирования"""
    
    # Сигналы
    pixel_clicked = pyqtSignal(int, int)  # x, y координаты пикселя
    pixel_dragged = pyqtSignal(int, int)  # При перетаскивании с ЛКМ
    zoom_changed = pyqtSignal(float)  # Новый уровень зума
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Настройки отображения
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Зум
        self.zoom_level = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 16.0
        
        # Панорамирование
        self._panning = False
        self._pan_start = QPoint()
        
        # Рисование
        self._drawing = False
        self.last_pos = None
        
        # Сцена
        self.image_item: Optional[QGraphicsPixmapItem] = None
    
    def wheelEvent(self, event):
        """Обработка колеса мыши для зума"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Ctrl + колесо = зум
            delta = event.angleDelta().y()
            
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            
            event.accept()
        else:
            super().wheelEvent(event)
    
    def mousePressEvent(self, event):
        """Обработка нажатия кнопок мыши"""
        pos = event.position().toPoint()
        
        if event.button() == Qt.MouseButton.MiddleButton:
            # Средняя кнопка = панорамирование
            self._panning = True
            self._pan_start = pos
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        
        elif event.button() == Qt.MouseButton.LeftButton:
            # Левая кнопка = рисование/выбор
            self._drawing = True
            scene_pos = self.mapToScene(pos)
            
            if self.image_item and self.image_item.contains(scene_pos):
                # Получить координаты пикселя
                pixmap = self.image_item.pixmap()
                x = int(scene_pos.x())
                y = int(scene_pos.y())
                
                if 0 <= x < pixmap.width() and 0 <= y < pixmap.height():
                    self.pixel_clicked.emit(x, y)
                    self.last_pos = (x, y)
            
            event.accept()
        
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Обработка перемещения мыши"""
        pos = event.position().toPoint()
        
        if self._panning:
            # Панорамирование
            delta = pos - self._pan_start
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self._pan_start = pos
            event.accept()
        
        elif self._drawing and self.last_pos:
            # Рисование при перетаскивании
            scene_pos = self.mapToScene(pos)
            pixmap = self.image_item.pixmap() if self.image_item else None
            
            if pixmap:
                x = int(scene_pos.x())
                y = int(scene_pos.y())
                
                if 0 <= x < pixmap.width() and 0 <= y < pixmap.height():
                    self.pixel_dragged.emit(x, y)
                    self.last_pos = (x, y)
            
            event.accept()
        
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания кнопок мыши"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        
        elif event.button() == Qt.MouseButton.LeftButton:
            self._drawing = False
            self.last_pos = None
            event.accept()
        
        else:
            super().mouseReleaseEvent(event)
    
    def zoom_in(self):
        """Увеличить масштаб"""
        self._set_zoom(self.zoom_level * 1.2)
    
    def zoom_out(self):
        """Уменьшить масштаб"""
        self._set_zoom(self.zoom_level / 1.2)
    
    def _set_zoom(self, new_zoom: float):
        """Установить новый масштаб"""
        old_zoom = self.zoom_level
        
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        if self.zoom_level != old_zoom:
            scale_factor = self.zoom_level / old_zoom
            self.scale(scale_factor, scale_factor)
            self.zoom_changed.emit(self.zoom_level)
    
    def fit_to_scene(self):
        """Подогнать изображение под размер окна"""
        if self.scene() and not self.scene().items():
            return
        
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
        # Вычислить текущий зум
        if self.sceneRect().width() > 0:
            self.zoom_level = self.viewport().width() / self.sceneRect().width()
            self.zoom_changed.emit(self.zoom_level)


class EditorWindow(QWidget):
    """Окно редактирования изображений"""
    
    # Сигналы для синхронизации с превью
    image_changed = pyqtSignal(np.ndarray)  # При изменении изображения
    pixel_selected = pyqtSignal(int, int)   # При клике на пиксель
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Editor")
        
        # Текущее изображение (numpy array)
        self.current_image: Optional[np.ndarray] = None
        
        # История для Undo/Redo
        self.history: list = []
        self.history_index: int = 0
        self.max_history = 20
        
        # Текущий инструмент
        self.current_tool: Tool = BrushTool()
        self.tools = {
            'brush': BrushTool(),
            'bucket': BucketTool(),
            'picker': PickerTool()
        }
        
        # Параметры отображения
        self.zoom_level: float = 1.0
        self.pan_offset: Tuple[int, int] = (0, 0)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Настроить UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Графическое представление
        self.graphics_view = EditorGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        
        layout.addWidget(self.graphics_view)
        
        self.setLayout(layout)
    
    def _connect_signals(self):
        """Подключить сигналы"""
        self.graphics_view.pixel_clicked.connect(self._on_pixel_clicked)
        self.graphics_view.pixel_dragged.connect(self._on_pixel_dragged)
        self.graphics_view.zoom_changed.connect(self._on_zoom_changed)
    
    def load_image(self, filepath: str):
        """Загрузить изображение для редактирования"""
        try:
            from PIL import Image
            
            # Открыть изображение
            pil_image = Image.open(filepath)
            
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Конвертировать в numpy
            self.current_image = np.array(pil_image, dtype=np.uint8)
            
            # Сохранить в историю
            self._save_to_history()
            
            # Отобразить
            self._update_display()
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def load_from_array(self, image: np.ndarray):
        """Загрузить изображение из numpy array"""
        self.current_image = image.copy()
        self._save_to_history()
        self._update_display()
    
    def save_image(self, filepath: str) -> bool:
        """Сохранить изменения"""
        if self.current_image is None:
            return False
        
        try:
            from PIL import Image
            
            pil_image = Image.fromarray(self.current_image, mode='RGB')
            pil_image.save(filepath, format='PNG')
            
            return True
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def undo(self):
        """Отменить последнее действие"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self._update_display()
            self.image_changed.emit(self.current_image)
    
    def redo(self):
        """Вернуть отмененное действие"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self._update_display()
            self.image_changed.emit(self.current_image)
    
    def set_tool(self, tool_name: str):
        """Сменить инструмент"""
        if tool_name in self.tools:
            self.current_tool = self.tools[tool_name]
    
    def set_color(self, r: int, g: int, b: int):
        """Установить цвет для инструментов"""
        for tool in self.tools.values():
            tool.set_color((r, g, b))
    
    def set_brush_size(self, size: int):
        """Установить размер кисти"""
        if 'brush' in self.tools:
            self.tools['brush'].set_brush_size(size)
    
    def zoom_in(self):
        """Увеличить масштаб"""
        self.graphics_view.zoom_in()
    
    def zoom_out(self):
        """Уменьшить масштаб"""
        self.graphics_view.zoom_out()
    
    def fit_to_window(self):
        """Подогнать под окно"""
        self.graphics_view.fit_to_scene()
    
    def _save_to_history(self):
        """Сохранить текущее состояние в историю"""
        if self.current_image is None:
            return
        
        # Удалить всё после текущей позиции (если были undo)
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Добавить текущее состояние
        self.history.append(self.current_image.copy())
        
        # Ограничить размер истории
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.history_index += 1
    
    def _update_display(self):
        """Обновить отображение изображения"""
        if self.current_image is None:
            return
        
        # Конвертировать numpy array в QImage
        h, w, ch = self.current_image.shape
        bytes_per_line = ch * w
        
        qimage = QImage(
            self.current_image.data,
            w, h, bytes_per_line,
            QImage.Format.Format_RGB888
        )
        
        # Создать pixmap
        pixmap = QPixmap.fromImage(qimage)
        
        # Очистить сцену и добавить новое изображение
        self.graphics_scene.clear()
        self.graphics_view.image_item = self.graphics_scene.addPixmap(pixmap)
    
    def _on_pixel_clicked(self, x: int, y: int):
        """Обработать клик по пикселю"""
        if self.current_image is None:
            return
        
        # Использовать инструмент
        changed = self.current_tool.use(self.current_image, x, y)
        
        # Если это picker, применить выбранный цвет к другим инструментам
        if isinstance(self.current_tool, PickerTool):
            picked_color = self.current_tool.get_picked_color()
            if picked_color:
                self.set_color(*picked_color)
        
        if changed:
            self._save_to_history()
            self._update_display()
            self.image_changed.emit(self.current_image)
        
        self.pixel_selected.emit(x, y)
    
    def _on_pixel_dragged(self, x: int, y: int):
        """Обработать перетаскивание по пикселям (для кисти)"""
        if self.current_image is None:
            return
        
        # Применять инструмент только для brush
        if isinstance(self.current_tool, BrushTool):
            changed = self.current_tool.use(self.current_image, x, y)
            
            if changed:
                self._update_display()
                # Не сохранять в историю каждый пиксель, только при отпускании
    
    def _on_zoom_changed(self, zoom_level: float):
        """Обработать изменение зума"""
        self.zoom_level = zoom_level
    
    def get_current_image(self) -> Optional[np.ndarray]:
        """Получить текущее изображение"""
        return self.current_image.copy() if self.current_image is not None else None
