"""
BucketTool - Инструмент заливки (Flood Fill)

Заливает область одного цвета новым цветом
"""

import numpy as np
from typing import Tuple, Set
from collections import deque
from .base_tool import Tool


class BucketTool(Tool):
    """Инструмент заливки области (flood fill)"""
    
    def __init__(self):
        super().__init__("Bucket Fill", "F")
    
    def use(self, image: np.ndarray, x: int, y: int) -> bool:
        """
        Залить область одного цвета новым цветом
        
        Алгоритм:
        1. Запомнить исходный цвет в точке (x, y)
        2. Создать очередь: queue = [(x, y)]
        3. Пока queue не пуста:
           - Взять точку из очереди
           - Если цвет = исходный → заменить на новый
           - Добавить соседей (4-connectivity) в очередь
        
        Args:
            image: Изображение для редактирования
            x: X координата точки для заливки
            y: Y координата точки для заливки
            
        Returns:
            True если изображение было изменено
        """
        h, w = image.shape[:2]
        
        # Проверить границы
        if not (0 <= x < w and 0 <= y < h):
            return False
        
        target_color = tuple(image[y, x])
        new_color = self.color
        
        # Не заливать если цвета одинаковые
        if target_color == new_color:
            return False
        
        # Flood fill алгоритм
        visited = set()
        queue = deque([(x, y)])
        changed = False
        
        while queue:
            cx, cy = queue.popleft()
            
            if (cx, cy) in visited:
                continue
            
            if not (0 <= cx < w and 0 <= cy < h):
                continue
            
            current_pixel_color = tuple(image[cy, cx])
            
            if current_pixel_color != target_color:
                continue
            
            visited.add((cx, cy))
            
            # Заменить цвет пикселя
            image[cy, cx] = new_color
            changed = True
            
            # Добавить соседей (4-connectivity)
            queue.append((cx + 1, cy))
            queue.append((cx - 1, cy))
            queue.append((cx, cy + 1))
            queue.append((cx, cy - 1))
        
        return changed
    
    def get_cursor(self) -> str:
        """Курсор в виде ведра для заливки"""
        return "cross"
