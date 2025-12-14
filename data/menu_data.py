# data/menu_data.py
import json
import os
from config import BUILTIN_CATEGORIES, BUILTIN_SUBCATEGORIES

def load_categories():
    """Загрузка категорий - встроенные + кастомные из JSON"""
    builtin_categories = BUILTIN_CATEGORIES.copy()
    
    # Загрузка кастомных категорий из JSON
    config_path = os.path.join(os.path.dirname(__file__), 'categories.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            custom_categories = json.load(f)
            print(f"Loaded {len(custom_categories)} custom categories from categories.json")
            
            # Объединяем встроенные и кастомные категории
            all_categories = builtin_categories + custom_categories
            print(f"Total categories: {len(all_categories)}")
            return all_categories
            
    except FileNotFoundError:
        print("No custom categories.json found, using built-in categories only")
        return builtin_categories
    except json.JSONDecodeError as e:
        print(f"Error parsing categories.json: {e}, using built-in categories only")
        return builtin_categories

def load_subcategories():
    """Загрузка подкатегорий - встроенные + кастомные из JSON"""
    all_subcategories = BUILTIN_SUBCATEGORIES.copy()
    
    # Загрузка кастомных подкатегорий из JSON
    config_path = os.path.join(os.path.dirname(__file__), 'subcategories.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            custom_subcategories = json.load(f)
            print(f"Loaded {len(custom_subcategories)} custom subcategories from subcategories.json")
            
            # Объединяем встроенные и кастомные подкатегории
            all_subcategories.update(custom_subcategories)
            print(f"Total subcategories: {len(all_subcategories)}")
            
    except FileNotFoundError:
        print("No custom subcategories.json found, using built-in subcategories only")
    except json.JSONDecodeError as e:
        print(f"Error parsing subcategories.json: {e}, using built-in subcategories only")
    
    return all_subcategories

def load_options():
    """Загрузка опций из JSON файла с группировкой по подкатегориям"""
    config_path = os.path.join(os.path.dirname(__file__), 'options.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Преобразуем структуру: подкатегория -> список опций
            options_by_subcategory = {}
            for option_name, option_data in data.items():
                subcategory = option_data.get("subcategory")
                if subcategory:
                    if subcategory not in options_by_subcategory:
                        options_by_subcategory[subcategory] = []
                    options_by_subcategory[subcategory].append(option_name)
            
            print(f"Loaded {len(data)} options for {len(options_by_subcategory)} subcategories from options.json")
            return data, options_by_subcategory
            
    except FileNotFoundError:
        print(f"Warning: options.json not found, using default data")
        return get_options_fallback()
    except json.JSONDecodeError as e:
        print(f"Error parsing options.json: {e}, using default data")
        return get_options_fallback()

def build_category_structure(categories_data, subcategories_data):
    """Построение структуры категорий с подкатегориями"""
    result_categories = []
    
    # Группируем подкатегории по категориям
    subcategories_by_category = {}
    for sub_name, sub_data in subcategories_data.items():
        category_name = sub_data.get("category")
        if category_name:
            if category_name not in subcategories_by_category:
                subcategories_by_category[category_name] = []
            subcategories_by_category[category_name].append(sub_name)
    
    for category in categories_data:
        category_name = category["name"]
        category_copy = category.copy()
        
        # Добавляем подкатегории для этой категории
        category_copy["subcategories"] = subcategories_by_category.get(category_name, [])
        
        result_categories.append(category_copy)
    
    return result_categories

# Основные функции загрузки
def get_categories_with_subs():
    """Основная функция для получения категорий с подкатегориями"""
    categories_data = load_categories()
    subcategories_data = load_subcategories()
    return build_category_structure(categories_data, subcategories_data)

def get_subcategories_data():
    """Получение данных подкатегорий"""
    return load_subcategories()

def get_options_data():
    """Получение данных опций"""
    return load_options()

# Для обратной совместимости
def load_categories_old():
    return get_categories_with_subs()

def load_subcategories_old():
    return get_subcategories_data()

def load_options_old():
    options_data, _ = get_options_data()
    return options_data

# Резервные данные
def get_options_fallback():
    """Резервные данные опций"""
    options_data = {
        "Date & Time": {
            "subcategory": "System Settings",
            "icon": "datetime.png",
            "command": "datetime_setup.exe"
        },
        "Language": {
            "subcategory": "System Settings", 
            "icon": "language.png",
            "command": "language_setup.exe"
        }
    }
    options_by_subcategory = {
        "System Settings": ["Date & Time", "Language"]
    }
    return options_data, options_by_subcategory