"""
Toolbar - Панель инструментов

Содержит кнопки для переключения между инструментами
"""

from PyQt6.QtWidgets import (
    QToolBar, QComboBox, QLabel, QWidget, QHBoxLayout,
    QSpinBox, QPushButton, QColorDialog
)
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtCore import Qt, pyqtSignal


class Toolbar(QToolBar):
    """Панель инструментов редактора"""
    
    # Сигналы
    tool_changed = pyqtSignal(str)  # Название инструмента
    color_changed = pyqtSignal(int, int, int)  # RGB цвет
    brush_size_changed = pyqtSignal(int)  # Размер кисти
    zoom_changed = pyqtSignal(int)  # Направление зума (-1 или 1)
    fit_requested = pyqtSignal()  # Запрос на fit to window
    
    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        
        self.setMovable(True)
        self.current_color = (255, 0, 0)  # Red по умолчанию
        self.current_brush_size = 5
        
        self._setup_tools()
        self._setup_color_picker()
        self._setup_brush_size()
        self._setup_zoom_controls()
    
    def _setup_tools(self):
        """Настроить кнопки инструментов"""
        
        # Brush Tool
        self.brush_action = QAction("🖌️ Brush", self)
        self.brush_action.setShortcut("B")
        self.brush_action.setToolTip("Brush Tool (B) - Рисование кистью")
        self.brush_action.setCheckable(True)
        self.brush_action.triggered.connect(lambda: self._on_tool_selected("brush"))
        self.addAction(self.brush_action)
        
        # Bucket Tool
        self.bucket_action = QAction("🪣 Bucket", self)
        self.bucket_action.setShortcut("F")
        self.bucket_action.setToolTip("Bucket Fill (F) - Заливка области")
        self.bucket_action.setCheckable(True)
        self.bucket_action.triggered.connect(lambda: self._on_tool_selected("bucket"))
        self.addAction(self.bucket_action)
        
        # Picker Tool
        self.picker_action = QAction("💉 Picker", self)
        self.picker_action.setShortcut("I")
        self.picker_action.setToolTip("Color Picker (I) - Выбор цвета")
        self.picker_action.setCheckable(True)
        self.picker_action.triggered.connect(lambda: self._on_tool_selected("picker"))
        self.addAction(self.picker_action)
        
        # Separator
        self.addSeparator()
        
        # Выбрать Brush по умолчанию
        self.brush_action.setChecked(True)
    
    def _setup_color_picker(self):
        """Настроить выбор цвета"""
        
        self.addSeparator()
        
        # Label
        color_label = QLabel("Color:")
        self.addWidget(color_label)
        
        # Кнопка выбора цвета
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 25)
        self.color_button.setStyleSheet(f"background-color: rgb{self.current_color};")
        self.color_button.setToolTip("Click to change color")
        self.color_button.clicked.connect(self._on_color_button_clicked)
        self.addWidget(self.color_button)
    
    def _setup_brush_size(self):
        """Настроить размер кисти"""
        
        self.addSeparator()
        
        # Label
        size_label = QLabel("Brush Size:")
        self.addWidget(size_label)
        
        # Spinbox для размера
        self.brush_size_spinbox = QSpinBox()
        self.brush_size_spinbox.setRange(1, 50)
        self.brush_size_spinbox.setValue(self.current_brush_size)
        self.brush_size_spinbox.setFixedWidth(60)
        self.brush_size_spinbox.valueChanged.connect(self._on_brush_size_changed)
        self.addWidget(self.brush_size_spinbox)
    
    def _setup_zoom_controls(self):
        """Настроить управление зумом"""
        
        self.addSeparator()
        
        # Zoom Out
        zoom_out_action = QAction("🔍-", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.setToolTip("Zoom Out (Ctrl+-)")
        zoom_out_action.triggered.connect(lambda: self.zoom_changed.emit(-1))
        self.addAction(zoom_out_action)
        
        # Zoom Level Label
        self.zoom_label = QLabel("100%")
        self.addWidget(self.zoom_label)
        
        # Zoom In
        zoom_in_action = QAction("🔍+", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.setToolTip("Zoom In (Ctrl++)")
        zoom_in_action.triggered.connect(lambda: self.zoom_changed.emit(1))
        self.addAction(zoom_in_action)
        
        # Fit to Window
        fit_action = QAction("Fit", self)
        fit_action.setShortcut("Ctrl+0")
        fit_action.setToolTip("Fit to Window (Ctrl+0)")
        fit_action.triggered.connect(lambda: self.fit_requested.emit())
        self.addAction(fit_action)
    
    def _on_tool_selected(self, tool_name: str):
        """Обработать выбор инструмента"""
        # Сбросить все кнопки
        self.brush_action.setChecked(False)
        self.bucket_action.setChecked(False)
        self.picker_action.setChecked(False)
        
        # Установить выбранную кнопку
        if tool_name == "brush":
            self.brush_action.setChecked(True)
        elif tool_name == "bucket":
            self.bucket_action.setChecked(True)
        elif tool_name == "picker":
            self.picker_action.setChecked(True)
        
        # Отправить сигнал
        self.tool_changed.emit(tool_name)
    
    def _on_color_button_clicked(self):
        """Открыть диалог выбора цвета"""
        from PyQt6.QtWidgets import QColorDialog
        
        current_qcolor = QColorDialog.getColor()
        
        if current_qcolor.isValid():
            self.current_color = (
                current_qcolor.red(),
                current_qcolor.green(),
                current_qcolor.blue()
            )
            
            # Обновить кнопку
            r, g, b = self.current_color
            self.color_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
            
            # Отправить сигнал
            self.color_changed.emit(r, g, b)
    
    def _on_brush_size_changed(self, value: int):
        """Обработать изменение размера кисти"""
        self.current_brush_size = value
        self.brush_size_changed.emit(value)
    
    def set_current_tool(self, tool_name: str):
        """Установить текущий инструмент программно"""
        if tool_name == "brush":
            self.brush_action.setChecked(True)
            self._on_tool_selected("brush")
        elif tool_name == "bucket":
            self.bucket_action.setChecked(True)
            self._on_tool_selected("bucket")
        elif tool_name == "picker":
            self.picker_action.setChecked(True)
            self._on_tool_selected("picker")
    
    def set_color(self, r: int, g: int, b: int):
        """Установить текущий цвет программно"""
        self.current_color = (r, g, b)
        self.color_button.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
    
    def update_zoom_label(self, zoom_level: float):
        """Обновить отображение уровня зума"""
        self.zoom_label.setText(f"{int(zoom_level * 100)}%")
