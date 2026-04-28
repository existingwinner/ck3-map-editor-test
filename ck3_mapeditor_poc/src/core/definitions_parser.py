"""
DefinitionsParser - Парсинг definitions.csv

Формат CSV файла CK3:
province;red;green;blue;name;x
1;255;0;0;c_vestisland;x
2;0;255;0;c_akureyri;x
"""

import csv
from typing import Dict, Tuple, Optional
from pathlib import Path


class DefinitionsParser:
    """
    Парсер definitions.csv для маппинга RGB → Province ID
    
    Attributes:
        definitions: Словарь {RGB: province_info}
    """
    
    def __init__(self):
        self.definitions: Dict[Tuple[int, int, int], Dict] = {}
    
    def parse(self, csv_path: str) -> Dict[Tuple[int, int, int], Dict]:
        """
        Парсить definitions.csv файл
        
        Args:
            csv_path: Путь к файлу definitions.csv
            
        Returns:
            Словарь вида:
            {
                (255, 0, 0): {
                    'id': 1,
                    'name': 'c_vestisland',
                    'rgb': (255, 0, 0)
                },
                ...
            }
        """
        self.definitions = {}
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                # CK3 использует ; как разделитель
                reader = csv.DictReader(f, delimiter=';')
                
                for row in reader:
                    try:
                        province_id = int(row.get('province', 0))
                        r = int(row.get('red', 0))
                        g = int(row.get('green', 0))
                        b = int(row.get('blue', 0))
                        name = row.get('name', '')
                        
                        rgb = (r, g, b)
                        
                        self.definitions[rgb] = {
                            'id': province_id,
                            'name': name,
                            'rgb': rgb
                        }
                        
                    except (ValueError, KeyError) as e:
                        # Пропустить некорректные строки
                        print(f"Warning: Skipping invalid row: {row}, error: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: definitions.csv not found at {csv_path}")
        except Exception as e:
            print(f"Error parsing definitions.csv: {e}")
        
        return self.definitions
    
    def get_province_by_rgb(self, rgb: Tuple[int, int, int]) -> Optional[Dict]:
        """
        Получить информацию о провинции по RGB цвету
        
        Args:
            rgb: Кортеж (R, G, B)
            
        Returns:
            Информация о провинции или None
        """
        return self.definitions.get(rgb)
    
    def get_province_id(self, rgb: Tuple[int, int, int]) -> Optional[int]:
        """
        Получить ID провинции по RGB цвету
        
        Args:
            rgb: Кортеж (R, G, B)
            
        Returns:
            ID провинции или None
        """
        info = self.get_province_by_rgb(rgb)
        return info['id'] if info else None
    
    def get_province_name(self, rgb: Tuple[int, int, int]) -> Optional[str]:
        """
        Получить название провинции по RGB цвету
        
        Args:
            rgb: Кортеж (R, G, B)
            
        Returns:
            Название провинции или None
        """
        info = self.get_province_by_rgb(rgb)
        return info['name'] if info else None
    
    def get_next_available_rgb(self) -> Tuple[int, int, int]:
        """
        Сгенерировать следующий доступный RGB цвет для новой провинции
        
        Returns:
            Кортеж (R, G, B) который еще не используется
        """
        # Простая стратегия: перебрать цвета пока не найдем свободный
        used_colors = set(self.definitions.keys())
        
        # Начать с последнего ID + 1
        max_id = max((info['id'] for info in self.definitions.values()), default=0)
        new_id = max_id + 1
        
        # Генерировать цвет на основе ID (простая хеш-функция)
        # Это гарантирует уникальный цвет для каждой провинции
        r = (new_id * 73) % 256
        g = (new_id * 151) % 256
        b = (new_id * 223) % 256
        
        rgb = (r, g, b)
        
        # Если цвет уже занят, искать следующий
        while rgb in used_colors:
            new_id += 1
            r = (new_id * 73) % 256
            g = (new_id * 151) % 256
            b = (new_id * 223) % 256
            rgb = (r, g, b)
        
        return rgb
    
    def add_province(self, province_id: int, name: str, rgb: Tuple[int, int, int]):
        """
        Добавить новую провинцию в определения
        
        Args:
            province_id: ID провинции
            name: Название провинции
            rgb: RGB цвет
        """
        self.definitions[rgb] = {
            'id': province_id,
            'name': name,
            'rgb': rgb
        }
    
    def get_all_provinces(self) -> list:
        """
        Получить список всех провинций
        
        Returns:
            Список словарей с информацией о провинциях
        """
        return list(self.definitions.values())
    
    def get_province_count(self) -> int:
        """Получить количество провинций"""
        return len(self.definitions)
