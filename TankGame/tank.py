# tank.py
import pygame
import os
import random
from base_item import BaseItem
from config import SCREEN_WIDTH, SCREEN_HEIGHT

# 延迟导入（避免循环）
def import_bullet():
    from bullet import Bullet
    return Bullet

def import_explosion():
    from explosion import Explosion
    return Explosion

class Tank(BaseItem):
    def __init__(self, left, top):
        super().__init__()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # 我方坦克图片路径
        self.images = {
            "Up": pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "tank", "p2tankU.gif")),
            "Down": pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "tank", "p2tankD.gif")),
            "Left": pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "tank", "p2tankL.gif")),
            "Right": pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "tank", "p2tankR.gif")),
        }
        self.direction = "Up"
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.speed = 5
        self.stop = True
        self.is_live = True
        self.oldLeft = self.rect.left
        self.oldTop = self.rect.top

    def move(self):
        """坦克移动逻辑"""
        self.oldLeft = self.rect.left
        self.oldTop = self.rect.top
        if self.direction == 'Left':
            if self.rect.left > 0:
                self.rect.left -= self.speed
        elif self.direction == 'Up':
            if self.rect.top > 0:
                self.rect.top -= self.speed
        elif self.direction == 'Down':
            if self.rect.top < SCREEN_HEIGHT - self.rect.height:
                self.rect.top += self.speed
        elif self.direction == 'Right':
            if self.rect.left < SCREEN_WIDTH - self.rect.width:
                self.rect.left += self.speed

    def stay(self):
        """碰撞后回退位置"""
        self.rect.left = self.oldLeft
        self.rect.top = self.oldTop

    def hit_wall(self, wall_list):
        """改为接收wall_list参数，消除对MainGame的引用"""
        for wall in wall_list:
            if pygame.sprite.collide_rect(self, wall):
                self.stay()

    def shoot(self):
        """发射子弹（延迟导入Bullet）"""
        Bullet = import_bullet()
        return Bullet(self)

    def displayTank(self, window):
        """改为接收window参数"""
        self.image = self.images[self.direction]
        window.blit(self.image, self.rect)

class MyTank(Tank):
    def __init__(self, left, top):
        super(MyTank, self).__init__(left, top)

    def myTank_hit_enemy(self, enemy_tank_list, explosion_list):
        """【核心修改】碰撞后仅销毁敌方，我方回退位置，避免同归于尽"""
        Explosion = import_explosion()
        for enemyTank in enemy_tank_list:
            if enemyTank.is_live and pygame.sprite.collide_rect(enemyTank, self):
                # 敌方死亡，我方回退到碰撞前位置（不死亡）
                enemyTank.is_live = False
                self.stay()  # 我方坦克回退，避免卡入敌方位置
                explosion = Explosion(enemyTank)
                explosion_list.append(explosion)

class EnemyTank(Tank):
    def __init__(self, left, top, speed):
        super(EnemyTank, self).__init__(left, top)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # 敌方坦克图片路径
        self.images = {
            "Up": pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "tank", "enemy1U.gif")),
            "Down": pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "tank", "enemy1D.gif")),
            "Left": pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "tank", "enemy1L.gif")),
            "Right": pygame.image.load(os.path.join(BASE_DIR, "Resource", "img", "tank", "enemy1R.gif")),
        }
        self.direction = self.randomDirection()
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.top = top
        self.speed = speed
        self.step = 40

    def randomDirection(self):
        """随机方向"""
        num = random.randint(1, 4)
        direction_map = {1: "Up", 2: "Down", 3: "Left", 4: "Right"}
        return direction_map[num]

    def randomMove(self, enemy_tank_list):  # 新增参数enemy_tank_list
        if self.step <= 0:
            self.direction = self.randomDirection()
            self.step = random.randint(20, 50)
        
        # 新增：预判目标位置
        target_left, target_top = self.rect.left, self.rect.top
        if self.direction == 'Up': target_top -= self.speed
        elif self.direction == 'Down': target_top += self.speed
        elif self.direction == 'Left': target_left -= self.speed
        elif self.direction == 'Right': target_left += self.speed
        target_rect = pygame.Rect(target_left, target_top, self.rect.width, self.rect.height)
        
        # 新增：检测重叠
        overlap = False
        for other_tank in enemy_tank_list:
            if other_tank != self and other_tank.is_live and target_rect.colliderect(other_tank.rect):
                overlap = True
                break
        
        # 新增：重叠则换方向，否则正常移动
        if overlap:
            self.direction = self.randomDirection()
            self.step = 0
        else:
            self.move()
            self.step -= 1
    # def randomMove(self):
    #     self.oldLeft = self.rect.left  # 新增：记录移动前位置
    #     self.oldTop = self.rect.top    # 新增：记录移动前位置
    #     """敌方随机移动"""
    #     if self.step <= 0:
    #         self.direction = self.randomDirection()
    #         self.step = 40
    #     else:
    #         self.move()
    #         self.step -= 1

    def shoot(self):
        """敌方射击（降低频率）"""
        num = random.randint(1, 80)
        if num < 2:
            Bullet = import_bullet()
            return Bullet(self)