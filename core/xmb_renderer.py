# xmb_renderer.py
import pygame
from config import *

class XMBRenderer:
    def __init__(self, xmb_interface):
        self.xmb = xmb_interface
    
    def draw_main_menu(self):
        """Отрисовка основного меню с прозрачностью"""
        # Создаем временную поверхность для основного меню
        menu_surface = pygame.Surface((self.xmb.screen.get_width(), self.xmb.screen.get_height()), pygame.SRCALPHA)
        
        # Отрисовываем фон (видео или градиент)
        self.xmb.background.update()
        self.xmb.background.draw(menu_surface)
        
        # Обновляем анимацию позиций
        self.xmb.animations.update_category_positions()
        self.xmb.animations.update_subcategory_positions()
        self.xmb.animations.update_option_positions()
        self.xmb.animations.update_fade_animation()
        self.xmb.animations.update_interface_offset()
        
        # Обновляем время для пульсации
        self.xmb.animation_manager.update_pulse()
        
        # Рисуем все элементы
        self._draw_categories(menu_surface)
        self._draw_subcategories(menu_surface)
        self._draw_options(menu_surface)
        
        # Применяем прозрачность основного меню и рисуем на экран
        menu_surface.set_alpha(self.xmb.main_menu_alpha)
        self.xmb.screen.blit(menu_surface, (0, 0))
    
    def _draw_categories(self, surface):
        """Отрисовка категорий"""
        for i, category in enumerate(self.xmb.categories):
            # В режиме выбранной подкатегории показываем только текущую категорию
            if self.xmb.subcategory_selected and i != self.xmb.current_category_index:
                continue
                
            x = category.current_x
            y = self.xmb.selection_y
            
            # Рисуем иконку категории
            icon = self.xmb.icons.get(category.name)
            if icon:
                # Применяем прозрачность к иконке
                icon_with_alpha = icon.copy()
                icon_with_alpha.set_alpha(category.alpha)
                surface.blit(icon_with_alpha, (x + CATEGORY_ICON_X_OFFSET, y + CATEGORY_ICON_Y_OFFSET))
            
            # Рисуем название категории БЕЗ СВЕЧЕНИЯ
            is_selected = (i == self.xmb.current_category_index)
            color = SELECTED_COLOR if is_selected else WHITE
            alpha = 255 if is_selected else 128
            
            text_surface = self.xmb.title_font.render(category.name, True, color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(x, y + CATEGORY_TEXT_Y_OFFSET))
            surface.blit(text_surface, text_rect)
    
    def _draw_subcategories(self, surface):
        """Отрисовка подкатегорий"""
        if self.xmb.categories[self.xmb.current_category_index].subcategories:
            category = self.xmb.categories[self.xmb.current_category_index]
            subcategories = self.xmb.subcategory_objects.get(category.name, [])
            
            # Рисуем подкатегории с анимацией
            sub_x = self.xmb.selection_x + SUBCATEGORY_X_OFFSET - self.xmb.interface_offset
            for i, subcategory_obj in enumerate(subcategories):
                subcategory = category.subcategories[i]
                y_pos = subcategory_obj.current_y
                
                # Пропускаем подкатегории с нулевой прозрачностью
                if subcategory_obj.alpha <= 0:
                    continue
                
                # Определяем выбрана ли подкатегория
                is_selected = (i == self.xmb.current_subcategory_index)
                
                # ПОДКАТЕГОРИИ СВЕТЯТСЯ ТОЛЬКО ЕСЛИ НЕ ОТКРЫТЫ OPTIONS
                should_glow = is_selected and self.xmb.navigation_level != 2
                
                text_position = (sub_x + SUBCATEGORY_TEXT_X_OFFSET, y_pos + SUBCATEGORY_TEXT_Y_OFFSET)

                # Определяем прозрачность в зависимости от режима
                if self.xmb.navigation_level == 2 and not is_selected:
                    base_alpha = 80
                else:
                    base_alpha = subcategory_obj.alpha

                # Рисуем текст подкатегории
                self._draw_subcategory_text(surface, subcategory, text_position, is_selected, should_glow, base_alpha)
                
                # Иконка подкатегории
                icon = self.xmb.icons.get(subcategory)
                if icon:
                    # Если подкатегория выбрана И НЕ ОТКРЫТЫ OPTIONS, рисуем пульсирующее свечение
                    if should_glow:
                        self.xmb.draw_glow(surface, sub_x, y_pos + SUBCATEGORY_ICON_Y_OFFSET, "subcategory", SUBCATEGORY_ICON_SIZE[0])
                    
                    # Применяем прозрачность к иконке
                    icon_with_alpha = icon.copy()
                    icon_with_alpha.set_alpha(base_alpha)
                    surface.blit(icon_with_alpha, (sub_x, y_pos + SUBCATEGORY_ICON_Y_OFFSET))
    
    def _draw_subcategory_text(self, surface, text, position, is_selected, should_glow, alpha):
        """Отрисовка текста подкатегории"""
        if should_glow:
            # Для текста со свечением
            color = SELECTED_COLOR if is_selected else WHITE
            text_surface = self.xmb.subcategory_font.render(text, True, color)
            text_width, text_height = text_surface.get_size()
            
            # Создаем свечение для текста
            cache_key = f"text_glow_{text_width}_{text_height}"
            if cache_key not in self.xmb.text_glow_cache:
                self.xmb.text_glow_cache[cache_key] = self.xmb.animation_manager.create_text_glow_surface(text_width, text_height)
            
            glow_surface = self.xmb.text_glow_cache[cache_key]
            pulse_factor = self.xmb.animation_manager.get_pulse_factor()
            glow_alpha = int(200 * pulse_factor)
            
            glow_surface_copy = glow_surface.copy()
            glow_surface_copy.set_alpha(glow_alpha)
            
            text_rect = text_surface.get_rect(midleft=position)
            glow_rect = glow_surface_copy.get_rect(
                midleft=(text_rect.left - (glow_surface.get_width() - text_width) // 2, 
                        text_rect.centery)
            )
            
            surface.blit(glow_surface_copy, glow_rect)
            surface.blit(text_surface, text_rect)
        else:
            # Без свечения
            color = SELECTED_COLOR if is_selected else WHITE
            text_surface = self.xmb.subcategory_font.render(text, True, color)
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(midleft=position)
            surface.blit(text_surface, text_rect)
    
    def _draw_options(self, surface):
        """Отрисовка опций"""
        if self.xmb.show_options and self.xmb.navigation_level == 2:
            current_options = self.xmb.get_current_options()
            if current_options:
                subcategory_name = self.xmb.categories[self.xmb.current_category_index].subcategories[self.xmb.current_subcategory_index]
                option_objects = self.xmb.option_objects.get(subcategory_name, [])
                
                # Позиция для опций
                option_x = self.xmb.selection_x + OPTION_X_OFFSET - self.xmb.interface_offset
                
                for i, option_obj in enumerate(option_objects):
                    if i >= len(current_options):
                        continue
                        
                    # option_obj - это объект XMBOption
                    y_pos = option_obj.current_y - 50
                    
                    is_selected = (i == self.xmb.current_option_index)
                    
                    # OPTIONS СВЕТЯТСЯ ТОЛЬКО ЕСЛИ ВЫБРАНЫ
                    should_glow = is_selected
                    
                    # Рисуем иконку опции
                    option_icon = self.xmb.icons.get(option_obj.name)
                    if option_icon:
                        # Если опция выбрана, рисуем пульсирующее свечение
                        if should_glow:
                            self.xmb.draw_glow(surface, option_x + OPTION_ICON_X_OFFSET, y_pos + OPTION_ICON_Y_OFFSET, "option", OPTION_ICON_SIZE[0])
                        
                        # Применяем прозрачность к иконке
                        icon_with_alpha = option_icon.copy()
                        icon_with_alpha.set_alpha(255 if is_selected else 128)
                        surface.blit(icon_with_alpha, (option_x + OPTION_ICON_X_OFFSET, y_pos + OPTION_ICON_Y_OFFSET))
                    
                    # Рисуем название опции
                    text_position = (option_x + OPTION_TEXT_X_OFFSET, y_pos + OPTION_TEXT_Y_OFFSET)
                    self._draw_option_text(surface, option_obj.name, text_position, is_selected, should_glow)
            else:
                # Если опций нет, показываем сообщение
                option_x = self.xmb.selection_x + OPTION_X_OFFSET - self.xmb.interface_offset
                option_y = OPTION_SELECTION_Y - 50
                text_surface = self.xmb.option_font.render("No options available", True, WHITE)
                text_rect = text_surface.get_rect(midleft=(option_x + OPTION_TEXT_X_OFFSET, option_y))
                surface.blit(text_surface, text_rect)
    
    def _draw_option_text(self, surface, text, position, is_selected, should_glow):
        """Отрисовка текста опции"""
        if should_glow:
            color = SELECTED_COLOR if is_selected else WHITE
            text_surface = self.xmb.option_font.render(text, True, color)
            text_width, text_height = text_surface.get_size()
            
            # Создаем свечение для текста
            cache_key = f"text_glow_{text_width}_{text_height}"
            if cache_key not in self.xmb.text_glow_cache:
                self.xmb.text_glow_cache[cache_key] = self.xmb.animation_manager.create_text_glow_surface(text_width, text_height)
            
            glow_surface = self.xmb.text_glow_cache[cache_key]
            pulse_factor = self.xmb.animation_manager.get_pulse_factor()
            glow_alpha = int(200 * pulse_factor)
            
            glow_surface_copy = glow_surface.copy()
            glow_surface_copy.set_alpha(glow_alpha)
            
            text_rect = text_surface.get_rect(midleft=position)
            glow_rect = glow_surface_copy.get_rect(
                midleft=(text_rect.left - (glow_surface.get_width() - text_width) // 2, 
                        text_rect.centery)
            )
            
            surface.blit(glow_surface_copy, glow_rect)
            surface.blit(text_surface, text_rect)
        else:
            # Без свечения
            color = SELECTED_COLOR if is_selected else WHITE
            text_surface = self.xmb.option_font.render(text, True, color)
            text_surface.set_alpha(128)  # полупрозрачный для невыбранных
            text_rect = text_surface.get_rect(midleft=position)
            surface.blit(text_surface, text_rect)