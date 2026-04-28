"""
PickerTool - Инструмент выбора цвета (Color Picker)

Позволяет выбрать цвет с изображения для текущего инструмента
"""

import numpy as np
from typing import Tuple, Optional
from .base_tool import Tool


class PickerTool(Tool):
    """Инструмент выбора цвета с изображения (пипетка)"""
    
    def __init__(self):
        super().__init__("Color Picker", "I")
        self.picked_color: Optional[Tuple[int, int, int]] = None
    
    def use(self, image: np.ndarray, x: int, y: int) -> bool:
        """
        Выбрать цвет из изображения
        
        Args:
            image: Изображение для выбора цвета
            x: X координата
            y: Y координата
            
        Returns:
            True если цвет был успешно выбран
        """
        h, w = image.shape[:2]
        
        # Проверить границы
        if not (0 <= x < w and 0 <= y < h):
            return False
        
        # Получить цвет пикселя
        self.picked_color = tuple(image[y, x])
        
        return True
    
    def get_picked_color(self) -> Optional[Tuple[int, int, int]]:
        """Получить выбранный цвет"""
        return self.picked_color
    
    def get_cursor(self) -> str:
        """Курсор в виде пипетки"""
        return "cross"
