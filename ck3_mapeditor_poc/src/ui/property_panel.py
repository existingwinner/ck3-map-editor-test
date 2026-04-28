"""
PropertyPanel - Панель свойств провинции

Отображает информацию о выбранной провинции
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from typing import Optional, Tuple


class PropertyPanel(QFrame):
    """Панель для отображения свойств провинции"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMinimumWidth(200)
        
        self._setup_ui()
        self._clear_properties()
    
    def _setup_ui(self):
        """Настроить UI панели"""
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок
        title = QLabel("Province Properties")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Информация о провинции
        self.id_label = QLabel("ID: -")
        layout.addWidget(self.id_label)
        
        self.name_label = QLabel("Name: -")
        layout.addWidget(self.name_label)
        
        self.color_label = QLabel("Color: -")
        layout.addWidget(self.color_label)
        
        # Цветовой образец
        self.color_sample = QLabel()
        self.color_sample.setFixedSize(50, 30)
        self.color_sample.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.color_sample.setStyleSheet("background-color: gray; border: 1px solid black;")
        layout.addWidget(self.color_sample)
        
        self.coords_label = QLabel("Coordinates: -")
        layout.addWidget(self.coords_label)
        
        self.area_label = QLabel("Area: -")
        layout.addWidget(self.area_label)
        
        # Stretch чтобы прижать всё вверх
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _clear_properties(self):
        """Очистить все свойства"""
        self.id_label.setText("ID: -")
        self.name_label.setText("Name: -")
        self.color_label.setText("Color: -")
        self.coords_label.setText("Coordinates: -")
        self.area_label.setText("Area: -")
        self.color_sample.setStyleSheet("background-color: gray; border: 1px solid black;")
    
    def update_properties(self, province_id: Optional[int] = None,
                         name: Optional[str] = None,
                         rgb: Optional[Tuple[int, int, int]] = None,
                         coords: Optional[Tuple[int, int]] = None,
                         area: Optional[int] = None):
        """
        Обновить отображаемые свойства
        
        Args:
            province_id: ID провинции
            name: Название провинции
            rgb: RGB цвет
            coords: Координаты (x, y)
            area: Площадь в пикселях
        """
        if province_id is not None:
            self.id_label.setText(f"ID: {province_id}")
        
        if name is not None:
            self.name_label.setText(f"Name: {name}")
        
        if rgb is not None:
            r, g, b = rgb
            self.color_label.setText(f"Color: ({r}, {g}, {b})")
            self.color_sample.setStyleSheet(
                f"background-color: rgb({r}, {g}, {b}); border: 1px solid black;"
            )
        
        if coords is not None:
            x, y = coords
            self.coords_label.setText(f"Coordinates: ({x}, {y})")
        
        if area is not None:
            self.area_label.setText(f"Area: {area} px")
    
    def clear(self):
        """Очистить панель"""
        self._clear_properties()
