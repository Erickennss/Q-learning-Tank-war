# wall.py
import pygame
import os
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class Wall:
    def __init__(self, left, top):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.images = pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "wall", "steels.gif"))
        self.rect = self.images.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.is_live = True

    # 改为接收window参数，不再直接引用MainGame.window
    def displayWall(self, window):
        window.blit(self.images, self.rect)