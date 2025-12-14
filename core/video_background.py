# video_background.py
import pygame
import os
import math

try:
    import cv2
    import threading
    import numpy as np
    HAS_VIDEO = True
    print("OpenCV loaded successfully")
except ImportError:
    HAS_VIDEO = False
    print("Warning: OpenCV not available, using static background")

class VideoBackground:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.video_surface = None
        self.has_video = False
        self.current_frame = None
        self.video_thread = None
        self.running = True
        
        # Получаем корневую директорию проекта
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Попробуем загрузить видео
        self.load_video()
        
        # Если видео не загружено, создадим градиентный фон
        if not self.has_video:
            self.create_gradient_background()
    
    def load_video(self):
        """Загрузка видеофайла"""
        if not HAS_VIDEO:
            print("OpenCV not installed. Install with: pip install opencv-python")
            return
            
        video_paths = [
            os.path.join(self.project_root, "resources", "background.mp4"),
            os.path.join(self.project_root, "background.mp4"),
            os.path.join(self.project_root, "resources", "background.mkv"),
            os.path.join(self.project_root, "resources", "background.avi"),
            os.path.join(self.project_root, "resources", "background.mov"),
        ]
        
        for video_path in video_paths:
            if os.path.exists(video_path):
                try:
                    self.cap = cv2.VideoCapture(video_path)
                    if not self.cap.isOpened():
                        continue
                    
                    # Получаем параметры видео
                    self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                    self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
                    if self.fps <= 0:
                        self.fps = 30  # Значение по умолчанию
                    
                    self.has_video = True
                    print(f"Loaded video: {video_path} ({self.frame_count} frames, {self.fps} fps)")
                    
                    # Запускаем поток для воспроизведения видео
                    self.video_thread = threading.Thread(target=self._video_loop)
                    self.video_thread.daemon = True
                    self.video_thread.start()
                    break
                    
                except Exception as e:
                    print(f"Error loading video {video_path}: {e}")
        
        if not self.has_video:
            print("No video file found or video playback not supported")
    
    def _video_loop(self):
        """Цикл воспроизведения видео в отдельном потоке"""
        try:
            while self.running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    # Если видео закончилось, перематываем в начало
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Конвертируем BGR в RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Масштабируем под размер экрана
                frame_resized = cv2.resize(frame_rgb, (self.screen_width, self.screen_height))
                
                # Конвертируем в поверхность pygame
                frame_surface = pygame.image.frombuffer(frame_resized.tobytes(), frame_resized.shape[1::-1], "RGB")
                self.current_frame = frame_surface
                
                # Задержка для синхронизации с FPS видео
                if hasattr(self, 'fps') and self.fps > 0:
                    pygame.time.wait(int(1000 / self.fps))
                else:
                    pygame.time.wait(33)  # 30 FPS по умолчанию
                    
        except Exception as e:
            print(f"Video playback error: {e}")
        finally:
            if hasattr(self, 'cap'):
                self.cap.release()
    
    def create_gradient_background(self):
        """Создание градиентного фона если видео недоступно"""
        self.background = pygame.Surface((self.screen_width, self.screen_height))
        
        # Создаем градиент от темно-синего к черному
        for y in range(self.screen_height):
            # Вычисляем цвет для текущей строки
            ratio = y / self.screen_height
            r = int(10 * (1 - ratio))
            g = int(30 * (1 - ratio))
            b = int(80 * (1 - ratio))
            color = (r, g, b)
            pygame.draw.line(self.background, color, (0, y), (self.screen_width, y))
        
        # Добавляем легкий узор
        for i in range(0, self.screen_width, 40):
            for j in range(0, self.screen_height, 40):
                alpha = 10
                dot_color = (255, 255, 255, alpha)
                pygame.draw.circle(self.background, dot_color, (i, j), 1)
    
    def update(self):
        """Обновление видеофона"""
        pass  # Обновление происходит в отдельном потоке
    
    def draw(self, screen):
        """Отрисовка фона"""
        if self.has_video and self.current_frame is not None:
            # Рисуем текущий кадр видео
            screen.blit(self.current_frame, (0, 0))
        else:
            # Рисуем градиентный фон
            screen.blit(self.background, (0, 0))
    
    def stop(self):
        """Остановка видео"""
        self.running = False
        if hasattr(self, 'cap'):
            self.cap.release()