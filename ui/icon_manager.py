# ui/icon_manager.py
import pygame
import os
from config import *

class IconManager:
    def __init__(self):
        self.icons = {}
        self.option_icon = None
        self.glow_surfaces = {}
        
    def load_icons(self, categories_data, subcategories_data, options_data, resources_dir):
        """Загрузка иконок из конфигурационных данных"""
        self.icons = {}
        
        # Загрузка иконок категорий
        for category in categories_data:
            icon_name = category.get("icon")
            display_name = category["name"]
            if icon_name:
                filepath = os.path.join(resources_dir, "icons", icon_name)
                self.icons[display_name] = self._load_single_icon(filepath, display_name, CATEGORY_ICON_SIZE)
            else:
                # Создаем заглушку если иконка не указана
                self.icons[display_name] = self._create_placeholder_icon(display_name, CATEGORY_ICON_SIZE)
        
        # Загрузка иконок подкатегорий
        for sub_name, sub_data in subcategories_data.items():
            icon_name = sub_data.get("icon")
            if icon_name:
                filepath = os.path.join(resources_dir, "icons", icon_name)
                self.icons[sub_name] = self._load_single_icon(filepath, sub_name, SUBCATEGORY_ICON_SIZE)
            else:
                # Создаем заглушку если иконка не указана
                self.icons[sub_name] = self._create_placeholder_icon(sub_name, SUBCATEGORY_ICON_SIZE)
        
        # Загрузка иконок опций
        for opt_name, opt_data in options_data.items():
            icon_name = opt_data.get("icon")
            if icon_name:
                filepath = os.path.join(resources_dir, "icons", icon_name)
                self.icons[opt_name] = self._load_single_icon(filepath, opt_name, OPTION_ICON_SIZE)
            else:
                # Создаем заглушку если иконка не указана
                self.icons[opt_name] = self._create_placeholder_icon(opt_name, OPTION_ICON_SIZE)
        
        print(f"Loaded {len(self.icons)} icons")
        return self.icons, self.option_icon
    
    def _load_single_icon(self, filepath, name, icon_size):
        """Загрузка одной иконки с указанным размером"""
        try:
            if os.path.exists(filepath):
                # Загружаем изображение
                icon = pygame.image.load(filepath).convert_alpha()
                
                # Получаем размеры оригинальной иконки
                original_width, original_height = icon.get_size()
                
                # Вычисляем новые размеры с сохранением пропорций
                ratio = min(icon_size[0] / original_width, icon_size[1] / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                
                # Масштабируем с сохранением пропорций и сглаживанием
                icon = pygame.transform.smoothscale(icon, (new_width, new_height))
                
                # Создаем поверхность нужного размера с прозрачностью
                final_surface = pygame.Surface(icon_size, pygame.SRCALPHA)
                
                # Вычисляем позицию для центрирования иконки
                x_pos = (icon_size[0] - new_width) // 2
                y_pos = (icon_size[1] - new_height) // 2
                
                # Помещаем иконку в центр
                final_surface.blit(icon, (x_pos, y_pos))
                
                print(f"Loaded icon: {os.path.basename(filepath)} for '{name}' ({original_width}x{original_height} -> {new_width}x{new_height})")
                return final_surface
            else:
                print(f"Warning: Icon not found: {os.path.basename(filepath)} for '{name}'")
                return self._create_placeholder_icon(name, icon_size)
        except Exception as e:
            print(f"Error loading icon {filepath} for '{name}': {e}")
            return self._create_placeholder_icon(name, icon_size)
    
    def _create_placeholder_icon(self, name, icon_size):
        """Создание заглушки для иконки с указанным размером"""
        surf = pygame.Surface(icon_size, pygame.SRCALPHA)
        
        # Серебристый градиент
        for i in range(icon_size[0]):
            for j in range(icon_size[1]):
                brightness = 200 - (i + j) * 100 // (icon_size[0] + icon_size[1])
                color = (brightness, brightness, brightness, 255)
                surf.set_at((i, j), color)
        
        # Темная рамка
        pygame.draw.rect(surf, (100, 100, 100), (0, 0, icon_size[0], icon_size[1]), 2, border_radius=8)
        
        # Текст с первой буквой имени
        if name:
            text_char = name[0].upper()
        else:
            text_char = "?"
            
        font_size = min(icon_size[0] // 2, 24)
        font = pygame.font.SysFont('Arial', font_size, bold=True)
        text = font.render(text_char, True, WHITE)
        text_rect = text.get_rect(center=(icon_size[0]//2, icon_size[1]//2))
        surf.blit(text, text_rect)
        
        return surf
    
    def get_icon(self, name):
        """Получение иконки по имени"""
        return self.icons.get(name)
    
    def get_option_icon(self):
        """Получение иконки для опций"""
        return self.option_icon