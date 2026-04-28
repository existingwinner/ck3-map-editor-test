"""
ImageManager - Управление изображениями

Отвечает за:
- Загрузку PNG файлов через Pillow
- Конвертацию в numpy array
- Сохранение изменений
"""

import numpy as np
from PIL import Image
from typing import Optional, Tuple


class ImageManager:
    """Менеджер для работы с изображениями карт"""
    
    def __init__(self):
        self.image: Optional[np.ndarray] = None
        self.original_image: Optional[np.ndarray] = None
        self.filepath: Optional[str] = None
    
    def load_image(self, filepath: str) -> np.ndarray:
        """
        Загрузить изображение из файла
        
        Args:
            filepath: Путь к PNG файлу
            
        Returns:
            numpy array с изображением (H, W, 3) RGB
            
        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл не является корректным PNG
        """
        try:
            # Открыть изображение через Pillow
            pil_image = Image.open(filepath)
            
            # Конвертировать в RGB (на случай RGBA или других форматов)
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Конвертировать в numpy array
            self.image = np.array(pil_image, dtype=np.uint8)
            self.original_image = self.image.copy()
            self.filepath = filepath
            
            return self.image
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {filepath}")
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")
    
    def save_image(self, filepath: str) -> bool:
        """
        Сохранить текущее изображение в файл
        
        Args:
            filepath: Путь для сохранения
            
        Returns:
            True если успешно, False иначе
        """
        if self.image is None:
            return False
        
        try:
            # Конвертировать numpy array обратно в PIL Image
            pil_image = Image.fromarray(self.image, mode='RGB')
            
            # Сохранить как PNG
            pil_image.save(filepath, format='PNG')
            
            return True
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def get_image_copy(self) -> Optional[np.ndarray]:
        """
        Получить копию текущего изображения
        
        Returns:
            Копия numpy array или None если изображение не загружено
        """
        if self.image is None:
            return None
        return self.image.copy()
    
    def get_pixel(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """
        Получить цвет пикселя по координатам
        
        Args:
            x: X координата
            y: Y координата
            
        Returns:
            Кортеж (R, G, B) или None если вне границ
        """
        if self.image is None:
            return None
        
        h, w = self.image.shape[:2]
        
        if not (0 <= x < w and 0 <= y < h):
            return None
        
        return tuple(self.image[y, x])
    
    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
        """
        Установить цвет пикселя
        
        Args:
            x: X координата
            y: Y координата
            color: Кортеж (R, G, B)
        """
        if self.image is None:
            return
        
        h, w = self.image.shape[:2]
        
        if 0 <= x < w and 0 <= y < h:
            self.image[y, x] = color
    
    def get_dimensions(self) -> Optional[Tuple[int, int]]:
        """
        Получить размеры изображения
        
        Returns:
            Кортеж (width, height) или None
        """
        if self.image is None:
            return None
        
        h, w = self.image.shape[:2]
        return (w, h)
    
    def reset_to_original(self):
        """Сбросить изображение к оригинальной версии"""
        if self.original_image is not None:
            self.image = self.original_image.copy()
