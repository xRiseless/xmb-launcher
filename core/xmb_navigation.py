# xmb_navigation.py
import pygame
from config import *

class XMBNavigation:
    def __init__(self, xmb_interface):
        self.xmb = xmb_interface
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return self._handle_escape()
                        
                elif self.xmb.navigation_level == 1:
                    return self._handle_level1_navigation(event)
                        
                elif self.xmb.navigation_level == 2:
                    return self._handle_level2_navigation(event)
                        
        return True
    
    def _handle_escape(self):
        if self.xmb.navigation_level == 2:
            # Возвращаемся из режима выбранной подкатегории к полному списку
            self.xmb.subcategory_selected = False
            self.xmb.target_offset = 0
            self.xmb.navigation_level = 1
            self.xmb.sound_manager.play_sound("click")
        else:
            return False
        return True
    
    def _handle_level1_navigation(self, event):
        if event.key == pygame.K_UP:
            self._move_subcategory(-1)
        elif event.key == pygame.K_DOWN:
            self._move_subcategory(1)
        elif event.key == pygame.K_LEFT:
            self._move_category(-1)
        elif event.key == pygame.K_RIGHT:
            self._move_category(1)
        elif event.key == pygame.K_RETURN:
            self._execute_current_subcategory()
        return True
    
    def _handle_level2_navigation(self, event):
        current_options = self.xmb.get_current_options()
        if current_options:
            if event.key == pygame.K_UP:
                self._move_option(-1)
            elif event.key == pygame.K_DOWN:
                self._move_option(1)
        else:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.xmb.sound_manager.play_sound("click")
                
        if event.key == pygame.K_LEFT or event.key == pygame.K_ESCAPE:
            self._return_to_subcategories()
        elif event.key == pygame.K_RETURN:
            self.xmb.execute_option()
        return True
    
    def _move_subcategory(self, direction):
        if self.xmb.categories[self.xmb.current_category_index].subcategories:
            self.xmb.current_subcategory_index = (
                self.xmb.current_subcategory_index + direction
            ) % len(self.xmb.categories[self.xmb.current_category_index].subcategories)
            self.xmb.update_subcategory_positions()
            self.xmb.sound_manager.play_sound("click")
    
    def _move_category(self, direction):
        # Сохраняем предыдущую категорию для анимации
        self.xmb.previous_category_index = self.xmb.current_category_index
        
        # Сохраняем текущую подкатегорию перед сменой категории
        self.xmb.categories[self.xmb.current_category_index].last_subcategory_index = self.xmb.current_subcategory_index
        self.xmb.current_category_index = (self.xmb.current_category_index + direction) % len(self.xmb.categories)
        # Восстанавливаем сохраненную подкатегорию для новой категории
        self.xmb.current_subcategory_index = self.xmb.categories[self.xmb.current_category_index].last_subcategory_index
        self.xmb.update_category_positions()
        self.xmb.sound_manager.play_sound("click")
        
        # Если это первое посещение категории, инициализируем позиции без анимации
        if self.xmb.categories[self.xmb.current_category_index].first_visit:
            self.xmb.update_subcategory_positions(initial=True)
            self.xmb.categories[self.xmb.current_category_index].first_visit = False
        else:
            self.xmb.update_subcategory_positions()
    
    def _move_option(self, direction):
        current_options = self.xmb.get_current_options()
        self.xmb.current_option_index = (self.xmb.current_option_index + direction) % len(current_options)
        self.xmb.update_option_positions()
        self.xmb.sound_manager.play_sound("click")
    
    def _execute_current_subcategory(self):
        if self.xmb.categories[self.xmb.current_category_index].subcategories:
            current_subcategory = self.xmb.categories[self.xmb.current_category_index].subcategories[self.xmb.current_subcategory_index]
            self.xmb.execute_subcategory(current_subcategory)
    
    def _return_to_subcategories(self):
        self.xmb.subcategory_selected = False
        self.xmb.target_offset = 0
        self.xmb.navigation_level = 1
        self.xmb.show_options = False
        self.xmb.current_option_index = 0
        self.xmb.sound_manager.play_sound("click")