# main.py
import pygame
import sys
from core.xmb_interface import XMBInterface  # Измененный импорт

def main():
    pygame.init()
    app = XMBInterface()
    app.run()

if __name__ == "__main__":
    main()