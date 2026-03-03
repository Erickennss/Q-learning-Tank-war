# base_item.py
import pygame
from pygame.sprite import Sprite

class BaseItem(Sprite):
    def __init__(self, color=None, width=None, height=None):
        pygame.sprite.Sprite.__init__(self)