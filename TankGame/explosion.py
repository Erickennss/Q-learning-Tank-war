# explosion.py
import pygame
import os

class Explosion:
    def __init__(self, tank):
        self.rect = tank.rect
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.images = [
            pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "fire", "blast1.gif")),
            pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "fire", "blast2.gif")),
            pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "fire", "blast3.gif")),
            pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "fire", "blast4.gif"))
        ]
        self.index = 0
        self.image = self.images[self.index]
        self.is_live = True

    # 改为接收window参数，不再直接引用MainGame.window
    def displayExplosion(self, window):
        if self.index < len(self.images):
            self.image = self.images[self.index]
            self.index += 1
            window.blit(self.image, self.rect)
        else:
            self.is_live = False
            self.index = 0