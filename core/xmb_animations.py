# xmb_animations.py
from config import *

class XMBAnimations:
    def __init__(self, xmb_interface):
        self.xmb = xmb_interface
    
    def update_category_positions(self):
        """Обновление целевых позиций категорий для анимации"""
        for i, category in enumerate(self.xmb.categories):
            # Вычисляем смещение относительно выбранной категории
            offset = (i - self.xmb.current_category_index) * CATEGORY_SPACING
            
            # Применяем общий сдвиг интерфейса
            category.target_x = self.xmb.selection_x + offset - self.xmb.interface_offset
            
            # Плавная анимация движения
            category.current_x = self.xmb.animation_manager.lerp_position(
                category.current_x, category.target_x
            )
    
    def update_subcategory_positions(self, initial=False):
        """Обновление целевых позиций подкатегорий для вертикальной анимации"""
        current_category = self.xmb.categories[self.xmb.current_category_index]
        if current_category.subcategories:
            subcategories = self.xmb.subcategory_objects.get(current_category.name, [])
            
            for i, subcategory_obj in enumerate(subcategories):
                # Базовое расстояние между подкатегориями
                base_spacing = SUBCATEGORY_SPACING
                
                # Увеличиваем расстояние между выбранной подкатегорией и предыдущей
                spacing = base_spacing + SUBCATEGORY_SELECTED_EXTRA_SPACING
                
                # Вычисляем смещение относительно выбранной подкатегории
                offset = 0
                for j in range(i, self.xmb.current_subcategory_index):
                    if j == self.xmb.current_subcategory_index - 1:
                        offset += spacing
                    else:
                        offset += base_spacing
                
                # Корректируем направление смещения
                if i < self.xmb.current_subcategory_index:
                    offset = -offset
                elif i > self.xmb.current_subcategory_index:
                    offset = 0
                    for j in range(self.xmb.current_subcategory_index, i):
                        if j == self.xmb.current_subcategory_index:
                            offset += base_spacing
                        else:
                            offset += base_spacing
                
                subcategory_obj.target_y = self.xmb.subcategory_selection_y + offset
                
                # Если это первая инициализация, сразу устанавливаем позицию
                if initial or not subcategory_obj.initialized:
                    subcategory_obj.current_y = subcategory_obj.target_y
                    subcategory_obj.initialized = True
                else:
                    # Плавная анимация движения
                    subcategory_obj.current_y = self.xmb.animation_manager.lerp_position(
                        subcategory_obj.current_y, subcategory_obj.target_y
                    )
    
    def update_option_positions(self, initial=False):
        """Обновление целевых позиций опций для вертикальной анимации"""
        if self.xmb.navigation_level == 2 and self.xmb.categories[self.xmb.current_category_index].subcategories:
            subcategory_name = self.xmb.categories[self.xmb.current_category_index].subcategories[self.xmb.current_subcategory_index]
            current_options = self.xmb.option_objects.get(subcategory_name, [])
            
            for i, option_obj in enumerate(current_options):
                base_spacing = OPTION_SPACING
                spacing = base_spacing
                
                # Вычисляем смещение относительно выбранной опции
                offset = 0
                for j in range(i, self.xmb.current_option_index):
                    offset += base_spacing
                
                # Корректируем направление смещения
                if i < self.xmb.current_option_index:
                    offset = -offset
                elif i > self.xmb.current_option_index:
                    offset = 0
                    for j in range(self.xmb.current_option_index, i):
                        offset += base_spacing
                
                option_obj.target_y = OPTION_SELECTION_Y + offset
                
                # Если это первая инициализация, сразу устанавливаем позицию
                if initial or not option_obj.initialized:
                    option_obj.current_y = option_obj.target_y
                    option_obj.initialized = True
                else:
                    # Плавная анимация движения
                    option_obj.current_y = self.xmb.animation_manager.lerp_position(
                        option_obj.current_y, option_obj.target_y
                    )
    
    def update_fade_animation(self):
        """Обновление анимации плавного появления/исчезания подкатегорий"""
        current_category = self.xmb.categories[self.xmb.current_category_index]
        previous_category = self.xmb.categories[self.xmb.previous_category_index]
        
        # Если сменили категорию
        if self.xmb.current_category_index != self.xmb.previous_category_index:
            # Старые подкатегории исчезают
            if previous_category.subcategories:
                old_subcategories = self.xmb.subcategory_objects.get(previous_category.name, [])
                for subcategory in old_subcategories:
                    if subcategory.alpha > 0:
                        subcategory.alpha = max(0, self.xmb.animation_manager.lerp_alpha(
                            subcategory.alpha, 0
                        ))
            
            # Новые подкатегории появляются
            if current_category.subcategories:
                new_subcategories = self.xmb.subcategory_objects.get(current_category.name, [])
                for subcategory in new_subcategories:
                    if subcategory.alpha < 255:
                        subcategory.alpha = min(255, self.xmb.animation_manager.lerp_alpha(
                            subcategory.alpha, 255
                        ))
        else:
            # Если категория не менялась, все подкатегории должны быть полностью видимы
            if current_category.subcategories:
                subcategories = self.xmb.subcategory_objects.get(current_category.name, [])
                for subcategory in subcategories:
                    if subcategory.alpha < 255:
                        subcategory.alpha = min(255, self.xmb.animation_manager.lerp_alpha(
                            subcategory.alpha, 255
                        ))
    
    def update_interface_offset(self):
        """Обновление анимации сдвига интерфейса"""
        self.xmb.interface_offset = self.xmb.animation_manager.lerp_offset(
            self.xmb.interface_offset, self.xmb.target_offset
        )