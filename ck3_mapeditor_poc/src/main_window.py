"""
MainWindow - Главное окно приложения с MDI

Функционал:
- Меню File/Edit/View/Tools
- Toolbar с инструментами
- MDI Area для Editor и Preview
- Возможность открепления окон
"""

from PyQt6.QtWidgets import (
    QMainWindow, QMdiArea, QMdiSubWindow, QApplication,
    QMenuBar, QMenu, QAction, QToolBar, QWidget, QVBoxLayout,
    QHBoxLayout, QSplitter, QLabel, QMessageBox
)
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal

import numpy as np
from typing import Optional, List, Tuple

from .editor_window import EditorWindow
from .preview_window import PreviewWindow
from .ui.toolbar import Toolbar
from .ui.property_panel import PropertyPanel
from .core.definitions_parser import DefinitionsParser


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("CK3 MapEditor - Proof of Concept")
        self.setMinimumSize(1200, 800)
        
        # Окна
        self.editor_window = EditorWindow()
        self.preview_window = PreviewWindow()
        self.property_panel = PropertyPanel()
        
        # Detached windows storage
        self.detached_windows: List[Tuple[QMainWindow, QWidget]] = []
        
        # Definitions parser
        self.definitions_parser = DefinitionsParser()
        
        self._setup_ui()
        self._create_menus()
        self._connect_signals()
    
    def _setup_ui(self):
        """Настроить UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        self.main_toolbar = Toolbar()
        main_layout.addWidget(self.main_toolbar)
        
        # Splitter for editor/preview and property panel
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Editor and Preview
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Editor subwindow
        self.editor_subwindow = QMdiSubWindow()
        self.editor_subwindow.setWidget(self.editor_window)
        self.editor_subwindow.setWindowTitle("Editor")
        
        # Preview subwindow
        self.preview_subwindow = QMdiSubWindow()
        self.preview_subwindow.setWidget(self.preview_window)
        self.preview_subwindow.setWindowTitle("Game Preview")
        
        # Add to left splitter
        left_container = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.editor_window)
        left_layout.addWidget(self.preview_window)
        left_container.setLayout(left_layout)
        
        splitter.addWidget(left_container)
        splitter.addWidget(self.property_panel)
        
        # Set splitter sizes
        splitter.setSizes([800, 200])
        
        main_layout.addWidget(splitter)
        
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _create_menus(self):
        """Создать меню"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        open_provinces_action = QAction("Open provinces.png", self)
        open_provinces_action.setShortcut("Ctrl+O")
        open_provinces_action.triggered.connect(self.open_provinces)
        file_menu.addAction(open_provinces_action)
        
        load_definitions_action = QAction("Load definitions.csv", self)
        load_definitions_action.setShortcut("Ctrl+L")
        load_definitions_action.triggered.connect(self.load_definitions)
        file_menu.addAction(load_definitions_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.editor_window.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.editor_window.redo)
        edit_menu.addAction(redo_action)
        
        # View Menu
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.editor_window.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.editor_window.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        fit_action = QAction("Fit to Window", self)
        fit_action.setShortcut("Ctrl+0")
        fit_action.triggered.connect(self.editor_window.fit_to_window)
        view_menu.addAction(fit_action)
        
        view_menu.addSeparator()
        
        raw_view_action = QAction("Raw View", self)
        raw_view_action.triggered.connect(lambda: self.preview_window.set_view_mode("raw"))
        view_menu.addAction(raw_view_action)
        
        game_view_action = QAction("Game View", self)
        game_view_action.triggered.connect(lambda: self.preview_window.set_view_mode("game_view"))
        view_menu.addAction(game_view_action)
        
        view_menu.addSeparator()
        
        detach_editor_action = QAction("Detach Editor", self)
        detach_editor_action.triggered.connect(self.detach_editor)
        view_menu.addAction(detach_editor_action)
        
        detach_preview_action = QAction("Detach Preview", self)
        detach_preview_action.triggered.connect(self.detach_preview)
        view_menu.addAction(detach_preview_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        
        brush_action = QAction("Brush (B)", self)
        brush_action.setShortcut("B")
        brush_action.triggered.connect(lambda: self.main_toolbar.set_current_tool("brush"))
        tools_menu.addAction(brush_action)
        
        bucket_action = QAction("Bucket Fill (F)", self)
        bucket_action.setShortcut("F")
        bucket_action.triggered.connect(lambda: self.main_toolbar.set_current_tool("bucket"))
        tools_menu.addAction(bucket_action)
        
        picker_action = QAction("Color Picker (I)", self)
        picker_action.setShortcut("I")
        picker_action.triggered.connect(lambda: self.main_toolbar.set_current_tool("picker"))
        tools_menu.addAction(picker_action)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """Подключить сигналы"""
        # Editor -> Preview synchronization
        self.editor_window.image_changed.connect(self.preview_window.update_image)
        
        # Toolbar signals
        self.main_toolbar.tool_changed.connect(self.editor_window.set_tool)
        self.main_toolbar.color_changed.connect(self.editor_window.set_color)
        self.main_toolbar.brush_size_changed.connect(self.editor_window.set_brush_size)
        self.main_toolbar.zoom_changed.connect(self._on_zoom_changed)
        
        # Preview signals
        self.preview_window.province_selected.connect(self._on_province_selected)
        
        # Editor pixel selected
        self.editor_window.pixel_selected.connect(self._on_pixel_selected)
    
    def open_provinces(self):
        """Открыть provinces.png"""
        from PyQt6.QtWidgets import QFileDialog
        
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open provinces.png",
            "",
            "PNG Files (*.png);;All Files (*)"
        )
        
        if filepath:
            try:
                self.editor_window.load_image(filepath)
                self.statusBar().showMessage(f"Loaded: {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {e}")
    
    def load_definitions(self):
        """Загрузить definitions.csv"""
        from PyQt6.QtWidgets import QFileDialog
        
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Load definitions.csv",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if filepath:
            try:
                self.preview_window.load_definitions(filepath)
                count = self.preview_window.definitions_parser.get_province_count()
                self.statusBar().showMessage(f"Loaded definitions: {count} provinces")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load definitions: {e}")
    
    def save(self):
        """Сохранить изменения"""
        if self.editor_window.current_image is None:
            return
        
        try:
            from PIL import Image
            
            pil_image = Image.fromarray(self.editor_window.current_image, mode='RGB')
            
            # Сохранить в test_data по умолчанию
            filepath = "test_data/provinces_modified.png"
            pil_image.save(filepath, format='PNG')
            
            self.statusBar().showMessage(f"Saved: {filepath}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")
    
    def save_as(self):
        """Сохранить как..."""
        from PyQt6.QtWidgets import QFileDialog
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            "",
            "PNG Files (*.png);;All Files (*)"
        )
        
        if filepath:
            if not filepath.endswith('.png'):
                filepath += '.png'
            
            if self.editor_window.save_image(filepath):
                self.statusBar().showMessage(f"Saved: {filepath}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save image")
    
    def detach_editor(self):
        """Открепить окно редактора"""
        self._detach_window(self.editor_window, "Editor")
    
    def detach_preview(self):
        """Открепить окно превью"""
        self._detach_window(self.preview_window, "Game Preview")
    
    def _detach_window(self, widget: QWidget, title: str):
        """Открепить виджет в отдельное окно"""
        # Скрыть в главном окне
        widget.hide()
        
        # Создать отдельное окно
        detached = QMainWindow()
        detached.setCentralWidget(widget)
        detached.setWindowTitle(title)
        detached.resize(800, 600)
        
        # Показать
        detached.show()
        
        # Сохранить ссылку
        self.detached_windows.append((detached, widget))
    
    def _on_zoom_changed(self, zoom_level: float):
        """Обработать изменение зума"""
        self.main_toolbar.update_zoom_label(zoom_level)
    
    def _on_province_selected(self, province_id: int):
        """Обработать выбор провинции"""
        info = self.preview_window.definitions_parser.get_province_by_rgb(
            self.preview_window.highlighted_rgb
        )
        
        if info:
            h, w = self.preview_window.image.shape[:2]
            area = self.preview_window.province_analyzer.get_province_area(
                w // 2, h // 2, self.preview_window.image
            )
            
            self.property_panel.update_properties(
                province_id=info['id'],
                name=info['name'],
                rgb=info['rgb'],
                area=area
            )
    
    def _on_pixel_selected(self, x: int, y: int):
        """Обработать выбор пикселя в редакторе"""
        if self.editor_window.current_image is not None:
            rgb = tuple(self.editor_window.current_image[y, x])
            info = self.preview_window.definitions_parser.get_province_by_rgb(rgb)
            
            if info:
                self.property_panel.update_properties(
                    province_id=info['id'],
                    name=info['name'],
                    rgb=rgb,
                    coords=(x, y)
                )
            else:
                self.property_panel.update_properties(
                    rgb=rgb,
                    coords=(x, y)
                )
    
    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(
            self,
            "About CK3 MapEditor",
            "CK3 MapEditor - Proof of Concept\n\n"
            "A simple map editor for Crusader Kings 3.\n\n"
            "Features:\n"
            "- Edit provinces.png files\n"
            "- Brush, Bucket Fill, Color Picker tools\n"
            "- Live preview with province borders\n"
            "- Undo/Redo support\n\n"
            "Version: 0.1.0"
        )
