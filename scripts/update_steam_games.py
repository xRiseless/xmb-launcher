#!/usr/bin/env python3
"""
Скрипт для парсинга игр Steam и обновления конфигурации XMB интерфейса
Обновленная версия для новой структуры конфигов
"""

import os
import json
import sys
import subprocess
from pathlib import Path

try:
    import vdf
    VDF_AVAILABLE = True
except ImportError:
    VDF_AVAILABLE = False
    print("Warning: vdf library not available. Install with: pip install vdf")

# Добавляем путь к корневой директории проекта для импорта модулей
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_steam_library_paths():
    """Получение путей к библиотекам Steam"""
    steam_paths = []
    
    # Windows пути
    if os.name == 'nt':
        # Основная установка Steam
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        steam_path = os.path.join(program_files, 'Steam')
        if os.path.exists(steam_path):
            steam_paths.append(steam_path)
        
        # Steam в Program Files (x86)
        program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        steam_path_x86 = os.path.join(program_files_x86, 'Steam')
        if os.path.exists(steam_path_x86) and steam_path_x86 not in steam_paths:
            steam_paths.append(steam_path_x86)
        
        # Steam в Games
        games = os.environ.get('Games', 'C:\\Games')
        steam_path = os.path.join(games, 'Steam')
        if os.path.exists(steam_path):
            steam_paths.append(steam_path)
        
        # Пользовательская установка Steam
        user_profile = os.environ.get('USERPROFILE', '')
        if user_profile:
            custom_steam = os.path.join(user_profile, 'Steam')
            if os.path.exists(custom_steam) and custom_steam not in steam_paths:
                steam_paths.append(custom_steam)
    
    # Linux пути
    elif os.name == 'posix':
        home = os.path.expanduser('~')
        steam_path = os.path.join(home, '.steam', 'steam')
        if os.path.exists(steam_path):
            steam_paths.append(steam_path)
        
        flatpak_steam = os.path.join(home, '.var', 'app', 'com.valvesoftware.Steam', '.steam', 'steam')
        if os.path.exists(flatpak_steam) and flatpak_steam not in steam_paths:
            steam_paths.append(flatpak_steam)
    
    return steam_paths

def parse_steam_libraries(steam_path):
    """Парсинг библиотек Steam из libraryfolders.vdf"""
    libraries = [os.path.join(steam_path, 'steamapps')]
    
    libraryfolders_path = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
    if os.path.exists(libraryfolders_path):
        try:
            with open(libraryfolders_path, 'r', encoding='utf-8') as f:
                if VDF_AVAILABLE:
                    data = vdf.load(f)
                    # Обрабатываем структуру libraryfolders.vdf
                    if 'libraryfolders' in data:
                        for key, folder_data in data['libraryfolders'].items():
                            if key.isdigit():  # Это номер библиотеки, а не мета-данные
                                path = folder_data.get('path', '')
                                if path and os.path.exists(path):
                                    lib_steamapps = os.path.join(path, 'steamapps')
                                    if os.path.exists(lib_steamapps):
                                        libraries.append(lib_steamapps)
                else:
                    # Резервный парсинг без библиотеки vdf
                    content = f.read()
                    lines = content.split('\n')
                    for line in lines:
                        if '"path"' in line:
                            parts = line.split('"')
                            if len(parts) >= 4:
                                lib_path = parts[3]
                                lib_steamapps = os.path.join(lib_path, 'steamapps')
                                if os.path.exists(lib_steamapps):
                                    libraries.append(lib_steamapps)
        except Exception as e:
            print(f"Error parsing libraryfolders.vdf: {e}")
    
    return libraries

def get_steam_games(steamapps_paths):
    """Получение списка игр Steam из acf файлов с устранением дубликатов"""
    games_dict = {}  # Используем словарь для устранения дубликатов по appid
    
    for steamapps in steamapps_paths:
        if not os.path.exists(steamapps):
            continue
            
        print(f"Scanning library: {steamapps}")
        
        # Ищем все .acf файлы
        acf_files = [f for f in os.listdir(steamapps) if f.endswith('.acf') and f.startswith('appmanifest_')]
        print(f"Found {len(acf_files)} ACF files")
        
        for file in acf_files:
            acf_path = os.path.join(steamapps, file)
            try:
                game_data = parse_acf_file(acf_path)
                if game_data and is_real_game(game_data):
                    appid = game_data['appid']
                    
                    # Проверяем, есть ли уже игра с таким appid
                    if appid not in games_dict:
                        games_dict[appid] = game_data
                        print(f"  ✓ {game_data['name']} (AppID: {appid})")
                    else:
                        print(f"  ⚠ {game_data['name']} (AppID: {appid}) - duplicate, skipping")
                        
                elif game_data:
                    print(f"  ✗ {game_data['name']} (filtered out)")
            except Exception as e:
                print(f"  Error parsing {file}: {e}")
    
    # Возвращаем список уникальных игр
    return list(games_dict.values())

def parse_acf_file(acf_path):
    """Парсинг ACF файла игры Steam с использованием vdf библиотеки"""
    try:
        if VDF_AVAILABLE:
            with open(acf_path, 'r', encoding='utf-8') as f:
                data = vdf.load(f)
            
            if 'AppState' in data:
                app_data = data['AppState']
                return {
                    'name': app_data.get('name', ''),
                    'appid': app_data.get('appid', ''),
                    'installdir': app_data.get('installdir', '')
                }
        else:
            # Резервный парсинг без vdf
            with open(acf_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            game_data = {}
            lines = content.split('\n')
            
            for i in range(len(lines)):
                line = lines[i].strip()
                
                if line.startswith('"name"'):
                    # Следующие 1-2 строки содержат значение
                    for j in range(i+1, min(i+3, len(lines))):
                        value_line = lines[j].strip()
                        if value_line and not value_line.startswith('"') and not value_line.startswith('{') and not value_line.startswith('}'):
                            game_data['name'] = value_line.strip('"')
                            break
                
                elif line.startswith('"appid"'):
                    for j in range(i+1, min(i+3, len(lines))):
                        value_line = lines[j].strip()
                        if value_line and not value_line.startswith('"') and not value_line.startswith('{') and not value_line.startswith('}'):
                            game_data['appid'] = value_line.strip('"')
                            break
                
                elif line.startswith('"installdir"'):
                    for j in range(i+1, min(i+3, len(lines))):
                        value_line = lines[j].strip()
                        if value_line and not value_line.startswith('"') and not value_line.startswith('{') and not value_line.startswith('}'):
                            game_data['installdir'] = value_line.strip('"')
                            break
            
            return game_data if game_data.get('name') and game_data.get('appid') else None
            
    except Exception as e:
        print(f"Error parsing ACF file {acf_path}: {e}")
        return None

def is_real_game(game_data):
    """Проверяет, является ли запись реальной игрой"""
    if not game_data:
        return False
        
    name = game_data.get('name', '').lower()
    appid = game_data.get('appid', '')
    
    # Игнорируем служебные аппы Steam
    ignored_apps = {
        '228980', '1070560', '1391110', '1628350', '1007', '205830',
        '211820', '219640', '221410', '228980', '233450', '2347770',
        '235780', '238960', '250820', '255710', '257850', '258550',
        '266840', '268400', '268410', '268420', '268430', '268440',
        '268450', '268460', '268470', '268480', '268490', '268500'
    }
    
    ignored_keywords = [
        'proton', 'runtime', 'redistributable', 'steamworks', 
        'depot', 'sdk', 'tool', 'test', 'demo', 'soundtrack',
        'server', 'dedicated server', 'content', 'workshop'
    ]
    
    if appid in ignored_apps:
        return False
    
    for keyword in ignored_keywords:
        if keyword in name:
            return False
    
    # Игнорируем слишком короткие названия (скорее всего ошибки парсинга)
    if len(name) < 3:
        return False
    
    return True

def create_game_command(game):
    """Создание команды для запуска игры"""
    appid = game.get('appid', '')
    
    # Просто возвращаем Steam URI, а XMB интерфейс сам разберется как его открыть
    return f'steam://rungameid/{appid}'

def clean_existing_games():
    """Очистка существующих игр из конфигурации"""
    data_dir = project_root / 'data'
    options_file = data_dir / 'options.json'
    
    try:
        with open(options_file, 'r', encoding='utf-8') as f:
            options_data = json.load(f)
    except FileNotFoundError:
        options_data = {}
    
    # Удаляем все игровые опции (те, что принадлежат подкатегории "Steam Game List")
    games_to_remove = []
    for option_name, option_data in options_data.items():
        subcategory = option_data.get('subcategory', '')
        if subcategory == 'Steam Game List':
            games_to_remove.append(option_name)
    
    for game_name in games_to_remove:
        del options_data[game_name]
        print(f"Removed existing game: {game_name}")
    
    # Сохраняем очищенные options
    with open(options_file, 'w', encoding='utf-8') as f:
        json.dump(options_data, f, indent=2, ensure_ascii=False)
    
    return len(games_to_remove)

def update_xmb_config(games):
    """Обновление конфигурационных файлов XMB с играми в новой структуре"""
    data_dir = project_root / 'data'
    options_file = data_dir / 'options.json'
    
    # Загружаем существующие конфиги
    try:
        with open(options_file, 'r', encoding='utf-8') as f:
            options_data = json.load(f)
    except FileNotFoundError:
        options_data = {}
    
    # Добавляем игры в options.json с указанием подкатегории
    for game in games:
        game_name = game['name']
        game_command = create_game_command(game)
        
        # Добавляем игру в options.json с указанием подкатегории
        options_data[game_name] = {
            "subcategory": "Steam Game List",
            "icon": "game_blank.png",
            "command": game_command
        }
    
    # Сохраняем обновленные конфиги
    try:
        with open(options_file, 'w', encoding='utf-8') as f:
            json.dump(options_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully updated configuration!")
        print(f"Added {len(games)} unique games to Steam Game List")
        return True
        
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def ensure_game_list_subcategory():
    """Проверяем, что подкатегория Steam Game List существует в subcategories.json"""
    data_dir = project_root / 'data'
    subcategories_file = data_dir / 'subcategories.json'
    
    try:
        with open(subcategories_file, 'r', encoding='utf-8') as f:
            subcategories_data = json.load(f)
    except FileNotFoundError:
        subcategories_data = {}
    
    # Добавляем подкатегорию Steam Game List если её нет
    if "Steam Game List" not in subcategories_data:
        subcategories_data["Steam Game List"] = {
            "category": "Game",
            "icon": "steam.png",
            "type": 1
        }
        print("Added 'Steam Game List' subcategory to subcategories.json")
        
        # Сохраняем обновленный файл
        with open(subcategories_file, 'w', encoding='utf-8') as f:
            json.dump(subcategories_data, f, indent=2, ensure_ascii=False)
    
    return True

def main():
    """Основная функция"""
    print("Steam Games Parser for XMB Interface")
    print("Updated for new config structure")
    print("=" * 50)
    
    if not VDF_AVAILABLE:
        print("Warning: vdf library not found. Using basic parser.")
        print("For better results, install: pip install vdf")
    
    # Убеждаемся, что подкатегория Steam Game List существует
    print("\n1. Ensuring Steam Game List subcategory exists...")
    ensure_game_list_subcategory()
    
    # Очищаем существующие игры
    print("\n2. Cleaning existing games from configuration...")
    removed_count = clean_existing_games()
    if removed_count > 0:
        print(f"Removed {removed_count} existing games")
    
    # Находим пути Steam
    print("\n3. Finding Steam installations...")
    steam_paths = get_steam_library_paths()
    if not steam_paths:
        print("Error: Could not find Steam installation")
        return False
    
    print(f"Found Steam: {steam_paths}")
    
    # Парсим библиотеки
    steamapps_paths = []
    for steam_path in steam_paths:
        libraries = parse_steam_libraries(steam_path)
        steamapps_paths.extend(libraries)
    
    if not steamapps_paths:
        print("Error: Could not find any Steam libraries")
        return False
    
    print(f"Found libraries: {steamapps_paths}")
    
    # Получаем список игр
    print("\n4. Scanning for games (removing duplicates)...")
    games = get_steam_games(steamapps_paths)
    
    if not games:
        print("No games found in Steam libraries")
        return True  # Возвращаем успех, но без игр
    
    # Сортируем игры по названию
    games.sort(key=lambda x: x['name'].lower())
    
    print(f"\n5. Found {len(games)} unique games:")
    for i, game in enumerate(games, 1):
        print(f"   {i:2d}. {game['name']} (AppID: {game['appid']})")
    
    # Обновляем конфигурацию XMB
    print("\n6. Updating XMB configuration...")
    success = update_xmb_config(games)
    
    if success:
        print("\n✅ Update completed successfully!")
        print("   Restart XMB Interface to see the changes.")
        print("   Games are now in: Game → Steam Game List")
    else:
        print("\n❌ Update failed!")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        if os.name == 'nt':
            print("\nPress any key to exit...")
            input()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        if os.name == 'nt':
            input("Press any key to exit...")
        sys.exit(1)