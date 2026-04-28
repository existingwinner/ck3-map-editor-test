#!/usr/bin/env python3
"""
CK3 MapEditor - Proof of Concept
Точка входа приложения

Запуск:
    python main.py

Или с тестовыми данными:
    python main.py --test
"""

import sys
import os

# Добавить src в path для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow


def main():
    """Главная функция запуска приложения"""
    
    # Создать QApplication
    app = QApplication(sys.argv)
    
    # Настроить стиль приложения
    app.setStyle("Fusion")
    
    # Создать главное окно
    window = MainWindow()
    window.show()
    
    # Загрузить тестовые данные если указано
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        load_test_data(window)
    
    # Запустить event loop
    sys.exit(app.exec())


def load_test_data(window):
    """Загрузить тестовые данные для демонстрации"""
    import os
    
    test_dir = os.path.join(os.path.dirname(__file__), "test_data")
    
    # Загрузить тестовое изображение
    test_image = os.path.join(test_dir, "test_provinces.png")
    if os.path.exists(test_image):
        window.editor_window.load_image(test_image)
        print(f"Loaded test image: {test_image}")
    
    # Загрузить тестовые определения
    test_definitions = os.path.join(test_dir, "test_definitions.csv")
    if os.path.exists(test_definitions):
        window.preview_window.load_definitions(test_definitions)
        print(f"Loaded test definitions: {test_definitions}")


if __name__ == "__main__":
    main()
