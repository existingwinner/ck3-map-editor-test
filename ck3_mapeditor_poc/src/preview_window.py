"""
PreviewWindow - Окно превью с игровыми элементами

Функционал:
- Отображение текущего состояния карты
- Наложение границ провинций
- Tooltip с Province ID при наведении
- Подсветка провинции при клике
- Режимы отображения (Raw / Game View / Terrain)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QLabel, QToolTip
)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
import numpy as np
from typing import Optional, Tuple, Dict

from .core.definitions_parser import DefinitionsParser
from .core.province_analyzer import ProvinceAnalyzer


class PreviewGraphicsView(QGraphicsView):
    """Графическое представление для превью"""
    
    province_hovered = pyqtSignal(int, int, tuple)  # x, y, rgb
    province_clicked = pyqtSignal(int, int, tuple)  # x, y, rgb
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
    
    def mouseMoveEvent(self, event):
        """Обработка перемещения мыши для tooltip"""
        pos = event.position().toPoint()
        scene_pos = self.mapToScene(pos)
        
        if hasattr(self, 'image_item') and self.image_item:
            pixmap = self.image_item.pixmap()
            x = int(scene_pos.x())
            y = int(scene_pos.y())
            
            if 0 <= x < pixmap.width() and 0 <= y < pixmap.height():
                # Получить цвет пикселя из изображения
                if hasattr(self, 'source_image') and self.source_image is not None:
                    h, w = self.source_image.shape[:2]
                    if 0 <= x < w and 0 <= y < h:
                        rgb = tuple(self.source_image[y, x])
                        self.province_hovered.emit(x, y, rgb)
        
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        """Обработка клика мыши"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            scene_pos = self.mapToScene(pos)
            
            if hasattr(self, 'image_item') and self.image_item:
                pixmap = self.image_item.pixmap()
                x = int(scene_pos.x())
                y = int(scene_pos.y())
                
                if 0 <= x < pixmap.width() and 0 <= y < pixmap.height():
                    if hasattr(self, 'source_image') and self.source_image is not None:
                        h, w = self.source_image.shape[:2]
                        if 0 <= x < w and 0 <= y < h:
                            rgb = tuple(self.source_image[y, x])
                            self.province_clicked.emit(x, y, rgb)
        
        super().mousePressEvent(event)


class PreviewWindow(QWidget):
    """Окно превью с игровыми элементами"""
    
    # Сигналы
    province_selected = pyqtSignal(int)  # Province ID выбран
    image_updated = pyqtSignal()  # Изображение обновлено
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Game Preview")
        
        self.image: Optional[np.ndarray] = None
        self.definitions: Dict = {}
        self.view_mode: str = "game_view"  # raw / game_view / terrain
        
        # Визуальные элементы
        self.show_borders: bool = True
        self.show_ids: bool = True
        self.selected_province_id: Optional[int] = None
        self.highlighted_rgb: Optional[Tuple[int, int, int]] = None
        
        # Компоненты
        self.definitions_parser = DefinitionsParser()
        self.province_analyzer = ProvinceAnalyzer()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Настроить UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Графическое представление
        self.graphics_view = PreviewGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        
        layout.addWidget(self.graphics_view)
        
        self.setLayout(layout)
        
        # Подключить сигналы
        self.graphics_view.province_hovered.connect(self._on_province_hovered)
        self.graphics_view.province_clicked.connect(self._on_province_clicked)
    
    def update_image(self, image: np.ndarray):
        """Обновить изображение от редактора"""
        self.image = image.copy()
        self.source_image = image.copy()
        self.province_analyzer.set_image(self.image)
        self._render()
        self.image_updated.emit()
    
    def load_definitions(self, csv_path: str):
        """Загрузить definitions.csv"""
        self.definitions = self.definitions_parser.parse(csv_path)
    
    def set_view_mode(self, mode: str):
        """Установить режим отображения"""
        self.view_mode = mode
        self._render()
    
    def toggle_borders(self, show: bool):
        """Включить/выключить отображение границ"""
        self.show_borders = show
        self._render()
    
    def toggle_ids(self, show: bool):
        """Включить/выключить отображение ID"""
        self.show_ids = show
        self._render()
    
    def get_province_at_pixel(self, x: int, y: int) -> Optional[int]:
        """Получить Province ID по координатам"""
        if self.image is None:
            return None
        
        h, w = self.image.shape[:2]
        if not (0 <= x < w and 0 <= y < h):
            return None
        
        rgb = tuple(self.image[y, x])
        info = self.definitions.get(rgb)
        
        return info['id'] if info else None
    
    def highlight_province(self, rgb: Tuple[int, int, int]):
        """Подсветить провинцию"""
        self.highlighted_rgb = rgb
        self._render()
    
    def clear_highlight(self):
        """Снять подсветку"""
        self.highlighted_rgb = None
        self._render()
    
    def _render(self):
        """Отрендерить изображение с наложениями"""
        if self.image is None:
            return
        
        if self.view_mode == "raw":
            self._render_raw()
        elif self.view_mode == "game_view":
            self._render_game_view()
        elif self.view_mode == "terrain":
            self._render_terrain()
    
    def _render_raw(self):
        """Отрендерить чистое изображение без наложений"""
        self._display_image(self.image)
    
    def _render_game_view(self):
        """
        Отрендерить Game View с наложениями:
        1. Базовое изображение
        2. Границы провинций (черные линии)
        3. Province ID (опционально)
        """
        # Создать копию для рендеринга
        render_image = self.image.copy()
        
        if self.show_borders:
            # Найти и нарисовать границы
            borders = self.province_analyzer.detect_borders(self.image)
            
            # Нарисовать черные линии на границах
            h, w = borders.shape
            for y in range(h):
                for x in range(w):
                    if borders[y, x] == 255:
                        render_image[y, x] = [0, 0, 0]
        
        # Если есть подсветка, добавить её
        if self.highlighted_rgb:
            mask = np.all(self.image == self.highlighted_rgb, axis=2)
            # Полупрозрачная желтая подсветка
            render_image[mask] = (render_image[mask] * 0.7 + np.array([255, 255, 0]) * 0.3).astype(np.uint8)
        
        self._display_image(render_image)
    
    def _render_terrain(self):
        """Отрендерить с обозначением типов террейна"""
        # Для прототипа просто показываем обычное изображение
        # В полной версии здесь будет наложение типов террейна
        self._render_game_view()
    
    def _display_image(self, image: np.ndarray):
        """Отобразить изображение на сцене"""
        # Конвертировать numpy array в QImage
        h, w, ch = image.shape
        bytes_per_line = ch * w
        
        qimage = QImage(
            image.data,
            w, h, bytes_per_line,
            QImage.Format.Format_RGB888
        )
        
        # Создать pixmap
        pixmap = QPixmap.fromImage(qimage)
        
        # Очистить сцену и добавить новое изображение
        self.graphics_scene.clear()
        self.graphics_view.image_item = self.graphics_scene.addPixmap(pixmap)
        
        # Сохранить ссылку на исходное изображение для tooltip
        self.graphics_view.source_image = self.image
    
    def _on_province_hovered(self, x: int, y: int, rgb: Tuple[int, int, int]):
        """Обработать наведение на провинцию"""
        info = self.definitions.get(rgb)
        
        if info:
            tooltip = f"Province ID: {info['id']}\nName: {info['name']}\nColor: {rgb}"
        else:
            tooltip = f"Color: {rgb}\n(Unknown province)"
        
        # Показать tooltip
        QToolTip.showText(self.graphics_view.mapToGlobal(QPoint(x, y)), tooltip)
    
    def _on_province_clicked(self, x: int, y: int, rgb: Tuple[int, int, int]):
        """Обработать клик по провинции"""
        info = self.definitions.get(rgb)
        
        if info:
            self.selected_province_id = info['id']
            self.province_selected.emit(info['id'])
            self.highlight_province(rgb)
    
    def get_current_image(self) -> Optional[np.ndarray]:
        """Получить текущее изображение"""
        return self.image.copy() if self.image is not None else None
