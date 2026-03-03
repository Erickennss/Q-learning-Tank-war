# bullet.py
import pygame
import os
from base_item import BaseItem
from config import SCREEN_WIDTH, SCREEN_HEIGHT

def import_explosion():
    from explosion import Explosion
    return Explosion

class Bullet(BaseItem):
    def __init__(self, tank):
        super().__init__()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.image = pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "fire", "1.png"))
        self.direction = tank.direction
        self.rect = self.image.get_rect()

        # 子弹位置计算
        if self.direction == "Up":
            self.rect.left = tank.rect.left + tank.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top - self.rect.height
        elif self.direction == "Down":
            self.rect.left = tank.rect.left + tank.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top + tank.rect.height
        elif self.direction == "Left":
            self.rect.left = tank.rect.left - self.rect.width/2 - self.rect.width/2
            self.rect.top = tank.rect.top + tank.rect.width/2 - self.rect.width/2
        elif self.direction == "Right":
            self.rect.left = tank.rect.left + tank.rect.width
            self.rect.top = tank.rect.top + tank.rect.height/2 - self.rect.width/2

        self.speed = 8
        self.is_live = True

    def moveBullet(self):
        if self.direction == "Up":
            if self.rect.top > 0:
                self.rect.top -= self.speed
            else:
                self.is_live = False
        elif self.direction == "Down":
            if self.rect.top < SCREEN_HEIGHT - self.rect.height:
                self.rect.top += self.speed
            else:
                self.is_live = False
        elif self.direction == "Left":
            if self.rect.left > 0:
                self.rect.left -= self.speed
            else:
                self.is_live = False
        elif self.direction == "Right":
            if self.rect.left < SCREEN_WIDTH - self.rect.width:
                self.rect.left += self.speed
            else:
                self.is_live = False

    def hit_wall(self, wall_list):
        for wall in wall_list:
            if pygame.sprite.collide_rect(self, wall):
                self.is_live = False

    def displayBullet(self, window):
        window.blit(self.image, self.rect)

    def my_bullet_hit_enemy(self, enemy_tank_list, explosion_list):
        Explosion = import_explosion()  # 延迟导入
        for enemyTank in enemy_tank_list:
            if enemyTank.is_live and pygame.sprite.collide_rect(enemyTank, self):
                enemyTank.is_live = False
                self.is_live = False
                explosion = Explosion(enemyTank)
                explosion_list.append(explosion)

    def enemy_bullet_hit_myTank(self, my_tank, explosion_list):
        Explosion = import_explosion()  # 延迟导入
        if my_tank and my_tank.is_live:
            if pygame.sprite.collide_rect(my_tank, self):
                self.is_live = False
                my_tank.is_live = False
                explosion = Explosion(my_tank)
                explosion_list.append(explosion)