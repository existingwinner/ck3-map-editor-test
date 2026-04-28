# CK3 MapEditor - Proof of Concept

Редактор карт для Crusader Kings 3 на Python с использованием PyQt6.

## 🚀 Быстрый Старт

### Установка

```bash
cd ck3_mapeditor_poc
pip install -r requirements.txt
```

### Запуск

```bash
python main.py
```

Или с тестовыми данными:

```bash
python main.py --test
```

## 📋 Возможности

### Инструменты Редактирования
- **Brush** (B) - Рисование кистью с настраиваемым размером
- **Bucket Fill** (F) - Заливка области одним цветом (flood fill)
- **Color Picker** (I) - Выбор цвета с изображения

### Навигация
- **Zoom In/Out** - Ctrl + Mouse Wheel или Ctrl++ / Ctrl+-
- **Pan** - Средняя кнопка мыши + Drag
- **Fit to Window** - Ctrl + 0

### Окна
- **Editor** - Окно редактирования
- **Preview** - Превью с игровыми элементами (границы провинций)
- **Detach** - Открепить окно в отдельное (View → Detach)

### Preview Modes
- **Raw View** - Чистое изображение без наложений
- **Game View** - С границами провинций (черные линии)

### Undo/Redo
- **Undo** - Ctrl+Z (до 20 шагов)
- **Redo** - Ctrl+Y

## 📁 Структура Проекта

```
ck3_mapeditor_poc/
├── main.py                    # Точка входа
├── requirements.txt           # Зависимости
├── README.md                  # Этот файл
│
├── src/                       # Исходный код
│   ├── __init__.py
│   ├── editor_window.py       # Окно редактора
│   ├── preview_window.py      # Окно превью
│   ├── main_window.py         # Главное окно
│   │
│   ├── tools/                 # Инструменты
│   │   ├── __init__.py
│   │   ├── base_tool.py
│   │   ├── brush_tool.py
│   │   ├── bucket_tool.py
│   │   └── picker_tool.py
│   │
│   ├── core/                  # Основные компоненты
│   │   ├── __init__.py
│   │   ├── image_manager.py
│   │   ├── province_analyzer.py
│   │   └── definitions_parser.py
│   │
│   └── ui/                    # UI компоненты
│       ├── __init__.py
│       ├── toolbar.py
│       └── property_panel.py
│
├── game_data/                 # ← СЮДА КЛАСТЬ ФАЙЛЫ ИЗ ИГРЫ
│   └── map_data/
│       ├── provinces.png      # Скопируйте из игры
│       ├── definitions.csv    # Скопируйте из игры
│       ├── heightmap.png      # Опционально
│       └── rivers.png         # Опционально
│
└── test_data/                 # Тестовые данные
    ├── test_provinces.png     # Тестовая карта 256x256
    ├── test_heightmap.png
    └── test_definitions.csv
```

## 🎮 Как Использовать с Реальными Файлами CK3

### Шаг 1: Найти Файлы Игры

**Стандартный путь CK3:**

**Windows:**
```
C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game\
```

**Linux:**
```
~/.steam/steam/steamapps/common/Crusader Kings III/game/
```

**Mac:**
```
~/Library/Application Support/Steam/steamapps/common/Crusader Kings III/game/
```

### Шаг 2: Скопировать Файлы в Проект

Скопируйте следующие файлы из игры:

| Файл | Из игры | В проект |
|------|---------|----------|
| **provinces.png** | `game/gfx/map/terrain/provinces.png` | `game_data/map_data/provinces.png` |
| **definitions.csv** | `game/map_data/definition.csv` | `game_data/map_data/definitions.csv` |
| **heightmap.png** | `game/gfx/map/terrain/heightmap.png` | `game_data/map_data/heightmap.png` |
| **rivers.png** | `game/gfx/map/terrain/rivers.png` | `game_data/map_data/rivers.png` |

### Шаг 3: Запустить Редактор

```bash
python main.py
```

### Шаг 4: Открыть Файлы в Редакторе

1. **File → Open provinces.png** → выберите `game_data/map_data/provinces.png`
2. **File → Load definitions.csv** → выберите `game_data/map_data/definitions.csv`
3. Теперь можно редактировать и видеть превью!

## ⚠️ Важные Замечания

**ВСЕГДА сохраняйте изменения в новую папку, НЕ перезаписывайте оригинальные файлы игры!**

```
File → Save As... → game_data/map_data/provinces_modified.png
```

Потом замените файл в игре (сделайте бэкап оригинала!):
```
game/gfx/map/terrain/provinces.png ← замените на provinces_modified.png
```

## 🔧 Горячие Клавиши

| Клавиша | Действие |
|---------|----------|
| B | Brush Tool |
| F | Bucket Fill |
| I | Color Picker |
| Ctrl+O | Open provinces.png |
| Ctrl+L | Load definitions.csv |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save As... |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl++ | Zoom In |
| Ctrl+- | Zoom Out |
| Ctrl+0 | Fit to Window |
| Ctrl+Q | Exit |

## 🐛 Troubleshooting

**Q: Превью не показывает границы провинций**  
A: Убедитесь, что загружен definitions.csv (File → Load definitions.csv)

**Q: Цвета провинций отображаются неправильно**  
A: Убедитесь, что provinces.png в формате RGB (не RGBA)

**Q: Редактор тормозит на больших картах**  
A: Для карт >8192px используйте Zoom для работы с участками

**Q: Ошибка при запуске**  
A: Убедитесь, что все зависимости установлены: `pip install -r requirements.txt`

## 📝 Технические Детали

### Формат definitions.csv

CK3 использует формат CSV с разделителем `;`:

```csv
province;red;green;blue;name;x
1;255;0;0;c_vestisland;x
2;0;255;0;c_akureyri;x
```

Поля:
- `province` - ID провинции
- `red`, `green`, `blue` - RGB цвет (0-255)
- `name` - Название провинции
- `x` - Заглушка (обычно "x")

### Алгоритм Flood Fill (Bucket)

Используется 4-connectivity алгоритм:
1. Запомнить исходный цвет в точке клика
2. Создать очередь с начальной точкой
3. Пока очередь не пуста:
   - Взять точку из очереди
   - Если цвет = исходный → заменить на новый
   - Добавить соседей (верх, низ, лево, право) в очередь

### Обнаружение Границ

Границы обнаруживаются сравнением каждого пикселя с соседями:
- Если цвет пикселя отличается от правого или нижнего соседа → это граница
- Границы отображаются черными линиями (RGB: 0,0,0)

## 📄 Лицензия

Proof-of-Concept проект для демонстрации технических возможностей.

## 🙏 Благодарности

- **Paradox Interactive** - за Crusader Kings 3
- **PyQt6** - GUI фреймворк
- **Pillow** - работа с изображениями
- **NumPy** - обработка массивов
