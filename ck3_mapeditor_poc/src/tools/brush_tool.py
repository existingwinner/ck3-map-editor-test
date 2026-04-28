"""
BrushTool - Инструмент кисти для рисования

Позволяет рисовать пикселями выбранного цвета
"""

import numpy as np
from typing import Tuple
from .base_tool import Tool


class BrushTool(Tool):
    """Инструмент кисти для свободного рисования"""
    
    def __init__(self):
        super().__init__("Brush", "B")
        self.brush_size = 5  # Размер кисти по умолчанию
    
    def use(self, image: np.ndarray, x: int, y: int) -> bool:
        """
        Нарисовать кистью на изображении
        
        Рисует круглую область заданного размера
        
        Args:
            image: Изображение для редактирования
            x: X координата центра кисти
            y: Y координата центра кисти
            
        Returns:
            True если изображение было изменено
        """
        h, w = image.shape[:2]
        radius = self.brush_size // 2
        
        changed = False
        
        # Рисовать круглую кисть
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Проверить попадание в круг
                if dx * dx + dy * dy <= radius * radius:
                    nx, ny = x + dx, y + dy
                    
                    # Проверить границы изображения
                    if 0 <= nx < w and 0 <= ny < h:
                        # Установить цвет пикселя
                        if not np.array_equal(image[ny, nx], self.color):
                            image[ny, nx] = self.color
                            changed = True
        
        return changed
    
    def get_cursor(self) -> str:
        """Курсор в виде круга для кисти"""
        return "cross"
