"""
ProvinceAnalyzer - Анализ провинций на карте

Отвечает за:
- Обнаружение границ между провинциями
- Поиск пикселей принадлежащих провинции
- Статистика провинций
"""

import numpy as np
from typing import Tuple, Optional, Set, List
from collections import deque


class ProvinceAnalyzer:
    """Анализатор провинций для работы с картой"""
    
    def __init__(self):
        self.image: Optional[np.ndarray] = None
    
    def set_image(self, image: np.ndarray):
        """Установить изображение для анализа"""
        self.image = image
    
    def detect_borders(self, image: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Найти границы между провинциями
        
        Алгоритм:
        1. Сравнить каждый пиксель с соседями (4-connectivity)
        2. Если RGB отличается → граница
        3. Вернуть маску границ
        
        Args:
            image: Изображение для анализа (или использовать текущее)
            
        Returns:
            Маска границ (0 = не граница, 255 = граница)
        """
        if image is None:
            image = self.image
        
        if image is None:
            return np.array([], dtype=np.uint8)
        
        h, w = image.shape[:2]
        borders = np.zeros((h, w), dtype=np.uint8)
        
        # Сравнить каждый пиксель с правым и нижним соседом
        for y in range(h - 1):
            for x in range(w - 1):
                current = tuple(image[y, x])
                right = tuple(image[y, x + 1])
                down = tuple(image[y + 1, x])
                
                # Если соседний пиксель другого цвета → граница
                if current != right or current != down:
                    borders[y, x] = 255
        
        # Обработать последний ряд и колонку
        borders[h-1, :] = 255  # Нижний край
        borders[:, w-1] = 255  # Правый край
        
        return borders
    
    def get_province_pixels(self, x: int, y: int, 
                           image: Optional[np.ndarray] = None) -> Set[Tuple[int, int]]:
        """
        Получить все пиксели принадлежащие той же провинции
        
        Использует flood fill алгоритм для нахождения всех пикселей
        одного цвета
        
        Args:
            x: Начальная X координата
            y: Начальная Y координата
            image: Изображение для анализа
            
        Returns:
            Множество координат (x, y) всех пикселей провинции
        """
        if image is None:
            image = self.image
        
        if image is None:
            return set()
        
        h, w = image.shape[:2]
        
        if not (0 <= x < w and 0 <= y < h):
            return set()
        
        target_color = tuple(image[y, x])
        
        # Flood fill алгоритм
        visited = set()
        queue = deque([(x, y)])
        
        while queue:
            cx, cy = queue.popleft()
            
            if (cx, cy) in visited:
                continue
            
            if not (0 <= cx < w and 0 <= cy < h):
                continue
            
            if tuple(image[cy, cx]) != target_color:
                continue
            
            visited.add((cx, cy))
            
            # Добавить соседей (4-connectivity)
            queue.append((cx + 1, cy))
            queue.append((cx - 1, cy))
            queue.append((cx, cy + 1))
            queue.append((cx, cy - 1))
        
        return visited
    
    def get_province_color(self, x: int, y: int, 
                          image: Optional[np.ndarray] = None) -> Optional[Tuple[int, int, int]]:
        """
        Получить цвет провинции в указанной точке
        
        Args:
            x: X координата
            y: Y координата
            image: Изображение для анализа
            
        Returns:
            RGB кортеж или None
        """
        if image is None:
            image = self.image
        
        if image is None:
            return None
        
        h, w = image.shape[:2]
        
        if not (0 <= x < w and 0 <= cy < h):
            return None
        
        return tuple(image[y, x])
    
    def count_unique_colors(self, image: Optional[np.ndarray] = None) -> int:
        """
        Подсчитать количество уникальных цветов (провинций) на карте
        
        Args:
            image: Изображение для анализа
            
        Returns:
            Количество уникальных цветов
        """
        if image is None:
            image = self.image
        
        if image is None:
            return 0
        
        # Reshape to (w*h, 3) и найти уникальные строки
        pixels = image.reshape(-1, 3)
        unique_colors = np.unique(pixels, axis=0)
        
        return len(unique_colors)
    
    def get_province_area(self, x: int, y: int, 
                         image: Optional[np.ndarray] = None) -> int:
        """
        Получить площадь провинции в пикселях
        
        Args:
            x: X координата внутри провинции
            y: Y координата внутри провинции
            image: Изображение для анализа
            
        Returns:
            Площадь в пикселях
        """
        pixels = self.get_province_pixels(x, y, image)
        return len(pixels)
    
    def find_province_center(self, x: int, y: int,
                            image: Optional[np.ndarray] = None) -> Optional[Tuple[int, int]]:
        """
        Найти центр провинции (центроид)
        
        Args:
            x: X координата внутри провинции
            y: Y координата внутри провинции
            image: Изображение для анализа
            
        Returns:
            Координаты центра (x, y) или None
        """
        pixels = self.get_province_pixels(x, y, image)
        
        if not pixels:
            return None
        
        # Вычислить среднее значение координат
        sum_x = sum(p[0] for p in pixels)
        sum_y = sum(p[1] for p in pixels)
        count = len(pixels)
        
        return (sum_x // count, sum_y // count)
    
    def get_neighbors(self, x: int, y: int,
                     image: Optional[np.ndarray] = None) -> Set[Tuple[int, int, int]]:
        """
        Получить цвета соседних провинций
        
        Args:
            x: X координата
            y: Y координата
            image: Изображение для анализа
            
        Returns:
            Множество RGB цветов соседних провинций
        """
        if image is None:
            image = self.image
        
        if image is None:
            return set()
        
        h, w = image.shape[:2]
        current_color = tuple(image[y, x])
        neighbors = set()
        
        # Проверить все пиксели на границе провинции
        province_pixels = self.get_province_pixels(x, y, image)
        
        for px, py in province_pixels:
            # Проверить соседей каждого пикселя
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = px + dx, py + dy
                
                if 0 <= nx < w and 0 <= ny < h:
                    neighbor_color = tuple(image[ny, nx])
                    
                    if neighbor_color != current_color:
                        neighbors.add(neighbor_color)
        
        return neighbors
