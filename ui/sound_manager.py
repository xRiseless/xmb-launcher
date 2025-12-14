# ui/sound_manager.py
import pygame
import os

class SoundManager:
    def __init__(self):
        self.sounds = {}
    
    def load_sounds(self, resources_dir):
        """Загрузка звуковых эффектов"""
        sound_path = os.path.join(resources_dir, "sounds", "navigation.mp3")
        
        try:
            if os.path.exists(sound_path):
                self.sounds["click"] = pygame.mixer.Sound(sound_path)
                print(f"Loaded sound: navigation.mp3")
            else:
                print(f"Warning: Sound file not found: navigation.mp3")
                # Создаем заглушку для звука
                self.sounds["click"] = None
        except Exception as e:
            print(f"Error loading sound: {e}")
            self.sounds["click"] = None
            
        return self.sounds
    
    def play_sound(self, sound_name):
        """Воспроизведение звукового эффекта"""
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")