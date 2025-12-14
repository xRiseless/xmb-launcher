# core/xmb_interface.py
import pygame
import sys
import os

# Обновленные импорты
from config import *
from core.video_background import VideoBackground
from models.xmb_item import XMBItem
from models.xmb_subcategory import XMBSubcategory  
from models.xmb_option import XMBOption
from ui.animation_manager import AnimationManager
from ui.icon_manager import IconManager
from ui.sound_manager import SoundManager
from data.menu_data import get_categories_with_subs, get_subcategories_data, get_options_data

# Импорты из core модуля
from core.xmb_navigation import XMBNavigation
from core.xmb_animations import XMBAnimations
from core.xmb_renderer import XMBRenderer
from core.xmb_startup import XMBStartup
from core.xmb_commands import XMBCommands

class XMBInterface:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("XMB Interface")
        self.clock = pygame.time.Clock()
        
        # Инициализация менеджеров
        self.animation_manager = AnimationManager()
        self.icon_manager = IconManager()
        self.sound_manager = SoundManager()
        
        # Инициализация компонентов
        self.background = VideoBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        self._initialize_resources()
        
        # Инициализация подсистем
        self.navigation = XMBNavigation(self)
        self.animations = XMBAnimations(self)
        self.renderer = XMBRenderer(self)
        self.startup = XMBStartup(self)
        self.commands = XMBCommands(self)
        
        # Инициализация интерфейса
        self._initialize_interface()
        
        # Кэш для свечения текста
        self.text_glow_cache = {}
        
    def _initialize_resources(self):
        """Инициализация всех ресурсов"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resources_dir = os.path.join(self.project_root, "resources")
    
        # Загрузка конфигурационных данных
        self.categories_data = get_categories_with_subs()
        self.subcategories_data = get_subcategories_data()
        self.options_data, self.options_by_subcategory = get_options_data()
        
        # Загрузка иконок
        self.icons, self.option_icon = self.icon_manager.load_icons(
            self.categories_data, 
            self.subcategories_data, 
            self.options_data, 
            resources_dir
        )
        
        # Загрузка звуков
        self.sounds = self.sound_manager.load_sounds(resources_dir)
        
        # Загрузка звука запуска
        self.startup_sound = self._load_startup_sound(resources_dir)
        
        # Создаем поверхность для легкого затемнения
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 50))
        
        # Загрузка шрифтов
        self._load_fonts()
        
        # Создаем поверхности для свечения
        self.glow_surfaces = self.animation_manager.create_glow_surfaces()
        
    def _load_startup_sound(self, resources_dir):
        """Загрузка звука запуска"""
        sound_path = os.path.join(resources_dir, "sounds", "startup.mp3")
        try:
            if os.path.exists(sound_path):
                sound = pygame.mixer.Sound(sound_path)
                print("Loaded startup sound: startup.mp3")
                return sound
            else:
                print(f"Warning: Startup sound not found: startup.mp3")
                return None
        except Exception as e:
            print(f"Error loading startup sound: {e}")
            return None
    
    def _load_fonts(self):
        """Загрузка шрифтов"""
        font_path = os.path.join(os.path.dirname(__file__), "resources", "font.ttf")
        
        try:
            if os.path.exists(font_path):
                # Основные шрифты
                self.title_font = pygame.font.Font(font_path, CATEGORY_FONT_SIZE)
                self.subcategory_font = pygame.font.Font(font_path, SUBCATEGORY_FONT_SIZE)
                self.option_font = pygame.font.Font(font_path, OPTION_FONT_SIZE)
                self.info_font = pygame.font.Font(font_path, INFO_FONT_SIZE)
                
                # Шрифты для вступительной анимации
                self.startup_sd_font = pygame.font.Font(font_path, STARTUP_SD_FONT_SIZE)
                self.startup_steam_deck_font = pygame.font.Font(font_path, STARTUP_STEAM_DECK_FONT_SIZE)
                
                print("Custom font loaded successfully with separate sizes")
            else:
                # Резервный системный шрифт
                self._load_system_fonts()
                print("Custom font not found, using Arial with separate sizes")
        except Exception as e:
            # В случае ошибки используем системные шрифты
            self._load_system_fonts()
            print(f"Error loading custom font: {e}")
    
    def _load_system_fonts(self):
        """Загрузка системных шрифтов как запасной вариант"""
        self.title_font = pygame.font.SysFont('Arial', CATEGORY_FONT_SIZE)
        self.subcategory_font = pygame.font.SysFont('Arial', SUBCATEGORY_FONT_SIZE)
        self.option_font = pygame.font.SysFont('Arial', OPTION_FONT_SIZE)
        self.info_font = pygame.font.SysFont('Arial', INFO_FONT_SIZE)
        self.startup_sd_font = pygame.font.SysFont('Arial', STARTUP_SD_FONT_SIZE)
        self.startup_steam_deck_font = pygame.font.SysFont('Arial', STARTUP_STEAM_DECK_FONT_SIZE)
    
    def _initialize_interface(self):
        """Инициализация интерфейса с новой структурой"""
        # Создание объектов категорий
        self.categories = []
        for category_data in self.categories_data:
            category = XMBItem(
                name=category_data["name"],
                icon=category_data.get("icon"),
                subcategories=category_data["subcategories"]
            )
            self.categories.append(category)
        
        # Создание объектов подкатегорий
        self.subcategory_objects = {}
        for sub_name, sub_data in self.subcategories_data.items():
            category_name = sub_data.get("category")
            if category_name:
                if category_name not in self.subcategory_objects:
                    self.subcategory_objects[category_name] = []
                
                subcategory = XMBSubcategory(
                    name=sub_name,
                    icon=sub_data.get("icon"),
                    subcategory_type=sub_data.get("type", 1),
                    command=sub_data.get("command")
                )
                self.subcategory_objects[category_name].append(subcategory)
        
        # Создание объектов опций
        self.option_objects = {}
        for subcategory_name, option_names in self.options_by_subcategory.items():
            option_list = []
            for option_name in option_names:
                opt_data = self.options_data.get(option_name, {})
                option = XMBOption(
                    name=option_name,
                    icon=opt_data.get("icon"),
                    command=opt_data.get("command")
                )
                option_list.append(option)
            self.option_objects[subcategory_name] = option_list
            print(f"Loaded {len(option_list)} options for subcategory: {subcategory_name}")
        
        # Инициализация навигации
        self.current_category_index = 5
        self.current_subcategory_index = 0
        self.current_option_index = 0
        self.previous_category_index = 0
        
        # Состояния навигации
        self.navigation_level = 1
        self.show_subcategories = True
        self.show_options = False
        
        # Позиция выбора
        self.selection_x = SELECTION_X
        self.selection_y = SELECTION_Y
        
        # Позиция выбора для подкатегорий
        self.subcategory_selection_y = SUBCATEGORY_SELECTION_Y
        
        # Анимация сдвига
        self.interface_offset = 0
        self.target_offset = 0
        
        # Флаг режима выбранной подкатегории
        self.subcategory_selected = False
        
        # Инициализация позиций
        self.animations.update_category_positions()
        self.animations.update_subcategory_positions(initial=True)
    
    # Делегирующие методы для обратной совместимости
    def handle_events(self):
        return self.navigation.handle_events()
    
    def update_category_positions(self):
        self.animations.update_category_positions()
    
    def update_subcategory_positions(self, initial=False):
        self.animations.update_subcategory_positions(initial)
    
    def update_option_positions(self, initial=False):
        self.animations.update_option_positions(initial)
    
    def update_fade_animation(self):
        self.animations.update_fade_animation()
    
    def update_interface_offset(self):
        self.animations.update_interface_offset()
    
    def execute_command(self, command):
        self.commands.execute_command(command)
    
    def draw_glow(self, screen, x, y, level_type="category", icon_size=None):
        # Реализация метода draw_glow (можно тоже вынести при желании)
        # Выбираем размеры свечения в зависимости от типа элемента
        if level_type == "category":
            glow_sizes = CATEGORY_GLOW_SIZES
            if icon_size is None:
                icon_size = CATEGORY_ICON_SIZE[0]
        elif level_type == "subcategory":
            glow_sizes = SUBCATEGORY_GLOW_SIZES
            if icon_size is None:
                icon_size = SUBCATEGORY_ICON_SIZE[0]
        elif level_type == "option":
            glow_sizes = OPTION_GLOW_SIZES
            if icon_size is None:
                icon_size = OPTION_ICON_SIZE[0]
        else:
            glow_sizes = CATEGORY_GLOW_SIZES
            if icon_size is None:
                icon_size = CATEGORY_ICON_SIZE[0]

        if len(glow_sizes) < 3:
            return

        glow_size_small = glow_sizes[0]
        glow_size_medium = glow_sizes[1]
        glow_size_large = glow_sizes[2]

        # Вычисляем центр иконки
        icon_center_x = x + icon_size // 2
        icon_center_y = y + icon_size // 2

        # Центрируем свечение относительно центра иконки
        glow_x_small = icon_center_x - glow_size_small // 2
        glow_y_small = icon_center_y - glow_size_small // 2

        glow_x_medium = icon_center_x - glow_size_medium // 2
        glow_y_medium = icon_center_y - glow_size_medium // 2

        glow_x_large = icon_center_x - glow_size_large // 2
        glow_y_large = icon_center_y - glow_size_large // 2

        # Вычисляем пульсацию
        pulse_factor = self.animation_manager.get_pulse_factor()

        # Создаем временные поверхности с пульсирующей прозрачностью
        pulse_alpha_small = int(180 * pulse_factor)
        pulse_alpha_medium = int(150 * pulse_factor)
        pulse_alpha_large = int(120 * pulse_factor)

        # Создаем копии поверхностей с пульсирующей прозрачностью
        if glow_size_small in self.glow_surfaces:
            glow_small = self.glow_surfaces[glow_size_small].copy()
            glow_small.set_alpha(pulse_alpha_small)
            screen.blit(glow_small, (glow_x_small, glow_y_small))
        
        if glow_size_medium in self.glow_surfaces:
            glow_medium = self.glow_surfaces[glow_size_medium].copy()
            glow_medium.set_alpha(pulse_alpha_medium)
            screen.blit(glow_medium, (glow_x_medium, glow_y_medium))
        
        if glow_size_large in self.glow_surfaces:
            glow_large = self.glow_surfaces[glow_size_large].copy()
            glow_large.set_alpha(pulse_alpha_large)
            screen.blit(glow_large, (glow_x_large, glow_y_large))
    
    def draw_text_with_glow(self, text, font, color, position, is_selected, alignment='center'):
        # Реализация метода draw_text_with_glow
        text_surface = font.render(text, True, color)
        text_width, text_height = text_surface.get_size()
        
        if is_selected:
            # Получаем или создаем свечение для текста
            cache_key = f"text_glow_{text_width}_{text_height}"
            if cache_key not in self.text_glow_cache:
                self.text_glow_cache[cache_key] = self.animation_manager.create_text_glow_surface(text_width, text_height)
            
            glow_surface = self.text_glow_cache[cache_key]
            glow_width, glow_height = glow_surface.get_size()
            
            # Применяем пульсацию к свечению
            pulse_factor = self.animation_manager.get_pulse_factor()
            glow_alpha = int(200 * pulse_factor)
            
            glow_surface_copy = glow_surface.copy()
            glow_surface_copy.set_alpha(glow_alpha)
            
            # Позиционируем свечение
            if alignment == 'center':
                glow_rect = glow_surface_copy.get_rect(center=position)
            else:  # midleft
                text_rect = text_surface.get_rect(midleft=position)
                glow_rect = glow_surface_copy.get_rect(
                    midleft=(text_rect.left - (glow_width - text_width) // 2, 
                            text_rect.centery)
                )
            
            # Рисуем свечение
            self.screen.blit(glow_surface_copy, glow_rect)
        
        # Рисуем основной текст
        if alignment == 'center':
            text_rect = text_surface.get_rect(center=position)
        else:  # midleft
            text_rect = text_surface.get_rect(midleft=position)
        
        self.screen.blit(text_surface, text_rect)
        return text_rect
    
    def has_options(self, subcategory_name):
        return subcategory_name in self.option_objects and len(self.option_objects[subcategory_name]) > 0
    
    def get_current_options(self):
        if self.navigation_level == 2 and self.categories[self.current_category_index].subcategories:
            subcategory_name = self.categories[self.current_category_index].subcategories[self.current_subcategory_index]
            options = self.option_objects.get(subcategory_name, [])
            print(f"Current subcategory: {subcategory_name}, options count: {len(options)}")
            return options
        return []
    
    def execute_subcategory(self, subcategory_name):
        current_category = self.categories[self.current_category_index]
        subcategory_obj = None
        
        # Находим объект подкатегории
        for sub_obj in self.subcategory_objects.get(current_category.name, []):
            if sub_obj.name == subcategory_name:
                subcategory_obj = sub_obj
                break
        
        if subcategory_obj:
            if subcategory_obj.type == 0 and subcategory_obj.command:
                # Выполняем команду напрямую
                self.execute_command(subcategory_obj.command)
                self.sound_manager.play_sound("click")
            elif subcategory_obj.type == 1:
                # Открываем меню опций
                self.subcategory_selected = True
                self.target_offset = INTERFACE_OFFSET_AMOUNT
                self.navigation_level = 2
                self.show_options = True
                self.current_option_index = 0
                self.update_option_positions(initial=True)
                self.sound_manager.play_sound("click")
    
    def execute_option(self):
        if self.navigation_level == 2:
            current_options = self.get_current_options()
            if current_options:
                option_obj = current_options[self.current_option_index]
                if option_obj.command:
                    self.execute_command(option_obj.command)
                    self.sound_manager.play_sound("click")
    
    def draw(self):
        """Основной метод отрисовки"""
        # Очищаем экран
        self.screen.fill(BLACK)
        
        if self.startup.is_active():
            # Вступительная анимация
            self.startup.update()
            self.startup.draw()
            self.main_menu_alpha = self.startup.get_main_menu_alpha()
        else:
            # Основное меню
            self.renderer.draw_main_menu()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        # Останавливаем видео перед выходом
        self.background.stop()
        pygame.quit()
        sys.exit()