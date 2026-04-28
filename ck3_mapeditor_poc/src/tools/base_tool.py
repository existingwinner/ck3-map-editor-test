"""
Base Tool - Базовый класс для инструментов
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
import numpy as np


class Tool(ABC):
    """Базовый класс для всех инструментов редактирования"""
    
    def __init__(self, name: str, shortcut: str = ""):
        self.name = name
        self.shortcut = shortcut
        self.color: Tuple[int, int, int] = (255, 0, 0)  # Default red
        self.brush_size: int = 1
    
    @abstractmethod
    def use(self, image: np.ndarray, x: int, y: int) -> bool:
        """
        Применить инструмент к изображению
        
        Args:
            image: Изображение для редактирования
            x: X координата
            y: Y координата
            
        Returns:
            True если изображение было изменено
        """
        pass
    
    def set_color(self, color: Tuple[int, int, int]):
        """Установить цвет инструмента"""
        self.color = color
    
    def set_brush_size(self, size: int):
        """Установить размер кисти"""
        self.brush_size = max(1, size)
    
    def get_cursor(self) -> str:
        """Получить тип курсора для инструмента"""
        return "cross"
