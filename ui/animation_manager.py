# ui/animation_manager.py
import math
import pygame
from config import *

class AnimationManager:
    def __init__(self):
        self.pulse_time = 0
        
    def update_pulse(self):
        """Обновление времени для пульсации"""
        self.pulse_time += PULSE_SPEED
        if self.pulse_time > 1.0:
            self.pulse_time = 0.0
    
    def lerp_position(self, current, target):
        """Линейная интерполяция для плавной анимации позиции"""
        return current + (target - current) * ANIMATION_SPEED
    
    def lerp_alpha(self, current, target):
        """Линейная интерполяция для альфа-канала"""
        return current + (target - current) * FADE_SPEED
    
    def lerp_offset(self, current, target):
        """Линейная интерполяция для смещения интерфейса"""
        return current + (target - current) * OFFSET_SPEED
    
    def get_pulse_factor(self):
        """Получение коэффициента пульсации (от 0.5 до 1.0)"""
        return 0.5 + 0.5 * math.sin(self.pulse_time * 2 * math.pi)
    
    def create_glow_surfaces(self):
        """Создание поверхностей для свечения вокруг иконок всех типов"""
        glow_surfaces = {}
        
        # Собираем все возможные размеры свечения из всех уровней
        all_glow_sizes = set()
        
        # Добавляем размеры для категорий
        for size in CATEGORY_GLOW_SIZES:
            all_glow_sizes.add(size)
        
        # Добавляем размеры для подкатегорий
        for size in SUBCATEGORY_GLOW_SIZES:
            all_glow_sizes.add(size)
        
        # Добавляем размеры для опций
        for size in OPTION_GLOW_SIZES:
            all_glow_sizes.add(size)
        
        # Создаем поверхности для всех уникальных размеров
        for size in all_glow_sizes:
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            center = (size // 2, size // 2)
            radius = size // 2
            
            # Создаем радиальный градиент для свечения
            for r in range(radius, 0, -1):
                alpha = int(150 * (1 - r / radius))
                color = (*GLOW_COLOR[:3], alpha)
                pygame.draw.circle(surf, color, center, r)
            
            glow_surfaces[size] = surf
            
        return glow_surfaces
    
    def create_text_glow_surface(self, text_width, text_height):
        """Создание эллиптического свечения для текста (растянутое по горизонтали)"""
        # Делаем свечение шире для текста
        glow_width = text_width + 100  # Добавляем отступы по бокам
        glow_height = text_height + 40  # Добавляем отступы сверху/снизу
        
        glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
        center_x = glow_width // 2
        center_y = glow_height // 2
        
        # Создаем эллиптический градиент для свечения
        # Горизонтальный радиус больше вертикального
        radius_x = glow_width // 2
        radius_y = glow_height // 2
        
        # Рисуем эллипсы с градиентом прозрачности
        for r in range(max(radius_x, radius_y), 0, -1):
            # Вычисляем текущие радиусы для эллипса
            current_radius_x = int(r * (radius_x / max(radius_x, radius_y)))
            current_radius_y = int(r * (radius_y / max(radius_x, radius_y)))
            
            if current_radius_x > 0 and current_radius_y > 0:
                alpha = int(150 * (1 - r / max(radius_x, radius_y)))
                color = (*GLOW_COLOR[:3], alpha)
                
                # Рисуем эллипс вместо круга
                pygame.draw.ellipse(glow_surface, color, 
                                  (center_x - current_radius_x, 
                                   center_y - current_radius_y,
                                   current_radius_x * 2, 
                                   current_radius_y * 2))
            
        return glow_surface
    
    def get_glow_sizes(self, level_type="category"):
        """Возвращает размеры для свечения в зависимости от типа элемента"""
        if level_type == "category":
            return CATEGORY_GLOW_SIZES
        elif level_type == "subcategory":
            return SUBCATEGORY_GLOW_SIZES
        elif level_type == "option":
            return OPTION_GLOW_SIZES
        else:
            return CATEGORY_GLOW_SIZES  # fallback