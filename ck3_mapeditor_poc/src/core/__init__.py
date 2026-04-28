"""
Core module - основные компоненты редактора
"""

from .image_manager import ImageManager
from .province_analyzer import ProvinceAnalyzer
from .definitions_parser import DefinitionsParser

__all__ = ['ImageManager', 'ProvinceAnalyzer', 'DefinitionsParser']
