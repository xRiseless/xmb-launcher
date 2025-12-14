# xmb_startup.py
import pygame
import time
from config import *

class XMBStartup:
    def __init__(self, xmb_interface):
        self.xmb = xmb_interface
        
        # Переменные для вступительной анимации
        self.phase = "black"  # black, display, fade_out, main_menu
        self.start_time = time.time()
        self.alpha = 0
        self.sound_played = False
        self.main_menu_alpha = 0
    
    def update(self):
        """Обновление вступительной анимации"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if self.phase == "black":
            self.alpha = int(255)
            
            if not self.sound_played and self.xmb.startup_sound:
                self.xmb.startup_sound.play()
                self.sound_played = True
            
            if elapsed >= STARTUP_BLACK:
                self.phase = "display"
        
        elif self.phase == "display": 
            self.phase = "display"
            self.start_time = current_time
            # Держим надпись 3 секунды
            if elapsed >= STARTUP_DISPLAY_DURATION:
                self.phase = "fade_out"
                self.start_time = current_time
        
        elif self.phase == "fade_out":
            # Плавное исчезновение надписи за 1 секунду
            progress = min(elapsed / STARTUP_FADE_OUT_DURATION, 1.0)
            self.alpha = int(255 * (1.0 - progress))
            
            # Одновременно появляется основное меню
            self.main_menu_alpha = int(255 * progress)
            
            if progress >= 1.0:
                self.phase = "main_menu"
                self.alpha = 0
                self.main_menu_alpha = 255
    
    def draw(self):
        """Отрисовка вступительной анимации"""
        # Сначала рисуем фон (видео или градиент)
        self.xmb.background.update()
        self.xmb.background.draw(self.xmb.screen)
        
        # Затем создаем поверхность для затемнения поверх фона
        overlay = pygame.Surface((self.xmb.screen.get_width(), self.xmb.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.alpha))
        self.xmb.screen.blit(overlay, (0, 0))
        
        # Рисуем текст "SD" и "Steam Deck" поверх затемнения
        if self.alpha > 0:
            # Позиция по правому краю с отступом
            text_x = self.xmb.screen.get_width() - STARTUP_TEXT_RIGHT_MARGIN
            center_y = self.xmb.screen.get_height() // 2
            
            # Текст "SD"
            sd_text = self.xmb.startup_sd_font.render("SD", True, WHITE)
            sd_rect = sd_text.get_rect()
            sd_rect.midright = (text_x, center_y - STARTUP_STEAM_DECK_FONT_SIZE)
            sd_text.set_alpha(self.alpha)
            self.xmb.screen.blit(sd_text, sd_rect)
            
            # Текст "Steam Deck"
            steam_text = self.xmb.startup_steam_deck_font.render("Steam Deck", True, WHITE)
            steam_rect = steam_text.get_rect()
            steam_rect.midright = (text_x, center_y + STARTUP_SD_FONT_SIZE // 2)
            steam_text.set_alpha(self.alpha)
            self.xmb.screen.blit(steam_text, steam_rect)
    
    def is_active(self):
        """Проверяет, активна ли вступительная анимация"""
        return self.phase != "main_menu"
    
    def get_main_menu_alpha(self):
        """Возвращает прозрачность основного меню"""
        return self.main_menu_alpha