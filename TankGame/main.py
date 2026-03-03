# main.py 最顶部
import os
import warnings
# 屏蔽pygame警告
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings('ignore', category=UserWarning, module='pygame')

import pygame
import time, random
import numpy as np
import pickle

from config import *
from base_item import BaseItem
from tank import Tank, MyTank, EnemyTank
from bullet import Bullet
from wall import Wall
from explosion import Explosion

class MainGame:
    window = None
    my_tank = None
    enemyTankList = []
    enemyTankCount = 3
    myBulletList = []
    enemyBulletList = []
    explosionList = []
    wallList = []

    # Q-Learning 核心属性
    last_state = None
    last_action = None
    reward = 0
    train_step = 0
    last_enemy_count = 0
    q_table_loaded = False
    total_reward = 0
    Q_TABLE = {}  # Q表：key=状态元组，value=动作Q值列表

    # training round and game state
    current_round = 1
    round_reward = 0
    round_steps = 0
    is_round_ended = False
    current_action = None
    action_hold_count = 0
    
    # game state
    game_state = "menu"          # "menu" / "mode_select" / "playing"
    game_mode = None             # "ai_train" (AI训练) / "human_vs_ai" (人机对战)
    clock = pygame.time.Clock()  # 新增：帧率控制

    my_tank_lives = 0  # 当前剩余生命数
    my_tank_lives_init = MY_TANK_INIT_LIVES  # 初始生命数（3）

    def __init__(self):
        pass

    def draw_main_menu(self):
        self.window.fill((0, 0, 0))
        pygame.font.init()
        title_font = pygame.font.SysFont(TEXT_FONT, 48)
        info_font = pygame.font.SysFont(TEXT_FONT, 24)
        small_font = pygame.font.SysFont(TEXT_FONT, 18)
        
        # 游戏标题
        title_text = title_font.render("TANK GAME", True, (0, 255, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
        self.window.blit(title_text, title_rect)
        
        # 模式选择
        start_text = info_font.render("Press ENTER to Select Mode", True, (255, 255, 0))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.window.blit(start_text, start_rect)
        
        # 按键说明
        key_text1 = small_font.render("ESC   : Exit Game", True, (255, 255, 255))
        
        self.window.blit(key_text1, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 50))

        
        pygame.display.update()

    def draw_mode_select_menu(self):
        self.window.fill((0, 0, 0))
        pygame.font.init()
        title_font = pygame.font.SysFont(TEXT_FONT, 36)
        info_font = pygame.font.SysFont(TEXT_FONT, 24)
        small_font = pygame.font.SysFont(TEXT_FONT, 18)
        
        # 模式选择标题
        title_text = title_font.render("SELECT GAME MODE", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
        self.window.blit(title_text, title_rect)
        
        # 模式选项
        mode1_text = info_font.render("1 - AI Training Mode (Auto Play)", True, (0, 255, 255))
        mode2_text = info_font.render("2 - Human vs AI Mode (Manual Control)", True, (255, 255, 0))
        back_text = small_font.render("Press ESC to Back to Main Menu", True, (255, 255, 255))
        
        self.window.blit(mode1_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 20))
        self.window.blit(mode2_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 30))
        self.window.blit(back_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 80))
        
        pygame.display.update()

    # handle human input
    def handle_human_input(self):
        """handel human input(keyboard),move tank and shoot"""
        if not self.my_tank or not self.my_tank.is_live:
            return
        
        keys = pygame.key.get_pressed()
        self.my_tank.stop = True
        
        # direction control
        if keys[pygame.K_UP]:
            self.my_tank.direction = 'Up'
            self.my_tank.stop = False
        elif keys[pygame.K_DOWN]:
            self.my_tank.direction = 'Down'
            self.my_tank.stop = False
        elif keys[pygame.K_LEFT]:
            self.my_tank.direction = 'Left'
            self.my_tank.stop = False
        elif keys[pygame.K_RIGHT]:
            self.my_tank.direction = 'Right'
            self.my_tank.stop = False
        
        # shoot control（space）
        if keys[pygame.K_SPACE]:
            # limit bullet count at most 2
            if len(self.myBulletList) < 2:
                self.myBulletList.append(Bullet(self.my_tank))

    def start_game(self):
        pygame.display.init()
        pygame.display.set_caption("Tank Game - Dual Mode (800x600 | 60FPS)")
        self.window = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        
        while True:
            # ========== Main menu ==========
            if self.game_state == "menu":
                self.draw_main_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.game_state = "mode_select"  # 进入模式选择
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            exit()
                continue
            
            # ========== select mode ==========
            if self.game_state == "mode_select":
                self.draw_mode_select_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN:
                        # 1: AI training mode
                        if event.key == pygame.K_F1:
                            self.game_mode = "ai_train"
                            self.game_state = "playing"
                            self.load_q_table()
                            self.init_round()
                        # 2: Human vs AI mode
                        elif event.key == pygame.K_F2:
                            self.game_mode = "human_vs_ai"
                            self.game_state = "playing"
                            self.init_round()
                        # ESC返回主菜单
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = "menu"
                continue
            
            # ========== running state ==========
            self.clock.tick(FPS)  # control frame rate
            self.window.fill((0, 0, 0))
            self.get_event()
            
            self.blit_all_elements()
            self.draw_info()

            # detect enemy all dead
            if self.get_enemy_count() == 0 and not self.is_round_ended:
                self.handle_round_win()

            # 游戏逻辑分支（根据模式）
            if self.my_tank and self.my_tank.is_live and not self.is_round_ended:
                # mode1：AI training mode(Q-Learning auto play)
                if self.game_mode == "ai_train":
                    current_state = self.get_state()
                    self.calculate_reward(current_state)
                    if self.last_state is not None:
                        self.update_q_table()

                    # 动作持续控制
                    if self.action_hold_count <= 0:
                        self.current_action = self.choose_action(current_state)
                        self.action_hold_count = ACTION_HOLD_FRAMES
                    else:
                        self.action_hold_count -= 1

                    self.execute_action(self.current_action)
                
                # mode2：Human vs AI mode
                elif self.game_mode == "human_vs_ai":
                    self.handle_human_input()

                # 移动+碰撞检测
                if not self.my_tank.stop:
                    self.my_tank.move()
                    self.detect_collision()

                # steps count
                if self.game_mode == "ai_train":
                    self.last_state = self.get_state() if self.game_mode == "ai_train" else None
                    self.last_action = self.current_action
                    self.last_enemy_count = self.get_enemy_count()
                    self.train_step += 1
                    self.round_steps += 1

                    # steps over limit
                    if self.train_step >= MAX_TRAIN_STEPS:
                        self.end_game()

            elif self.is_round_ended:
                time.sleep(1)
                if AUTO_RESET_AFTER_WIN and self.current_round < MAX_TRAIN_ROUNDS:
                    self.reset_game_for_new_round()
                else:
                    self.end_game()
            elif self.my_tank and not self.my_tank.is_live:
                # # 我方被击中，重置本轮
                # print(f"第{self.current_round}轮：我方被击中，重置！")
                # self.init_round()
                self.my_tank_lives -= 1  # 生命-1
                print(f"【生命】我方坦克被击毁！剩余生命：{self.my_tank_lives}")
                
                if self.my_tank_lives > 0:
                    # life>0 → recreate my tank
                    print(f"第{self.current_round}轮：剩余生命{self.my_tank_lives}，重新生成坦克！")
                    self.createMyTank()  # 重新创建我方坦克
                    # reset this round partially state（keep round and life unchanged）
                    self.last_state = None
                    self.last_action = None
                    self.round_steps = 0
                else:
                    # life=0 → end game
                    print(f"第{self.current_round}轮：生命耗尽！游戏结束")
                    self.end_game()

            pygame.display.update()

    # ===================== 核心方法（保留原有修复逻辑）=====================
    def get_state(self):
        if not self.my_tank or not self.my_tank.is_live:
            return (0, 0, DIR_NONE, DIR_NONE, 0, 0)
        
        my_x = self.my_tank.rect.left // X_STEP
        my_y = self.my_tank.rect.top // Y_STEP
        my_x = max(0, min(X_BINS-1, my_x))
        my_y = max(0, min(Y_BINS-1, my_y))

        dir_map = {"Up": DIR_UP, "Down": DIR_DOWN, "Left": DIR_LEFT, "Right": DIR_RIGHT}
        my_dir = dir_map.get(self.my_tank.direction, DIR_NONE)

        nearest_enemy_dir = DIR_NONE
        min_dist = float('inf')
        enemy_list = [e for e in self.enemyTankList if e.is_live]
        for enemy in enemy_list:
            dist = np.sqrt(
                (self.my_tank.rect.centerx - enemy.rect.centerx)**2 +
                (self.my_tank.rect.centery - enemy.rect.centery)**2
            )
            if dist < min_dist:
                min_dist = dist
                nearest_enemy_dir = dir_map.get(enemy.direction, DIR_NONE)

        enemy_count = len(enemy_list)
        enemy_count = max(0, min(3, enemy_count))
        my_bullet_count = 1 if len(self.myBulletList) > 0 else 0

        return (my_x, my_y, my_dir, nearest_enemy_dir, enemy_count, my_bullet_count)

    def choose_action(self, state):
        if state not in self.Q_TABLE:
            self.Q_TABLE[state] = [0.0] * ACTION_NUM
        
        global EPSILON
        if EPSILON > EPSILON_MIN:
            EPSILON *= EPSILON_DECAY

        if random.random() < EPSILON:
            return random.choice(ACTION_LIST)
        else:
            q_values = self.Q_TABLE[state]
            max_q = max(q_values)
            max_actions = [i for i, q in enumerate(q_values) if q == max_q]
            return random.choice(max_actions)

    def execute_action(self, action):
        """execute AI action"""
        tank = self.my_tank
        if not tank or not tank.is_live:
            return
        
        tank.stop = True
        if action == ACTION_UP:
            tank.direction = 'Up'
            tank.stop = False
        elif action == ACTION_DOWN:
            tank.direction = 'Down'
            tank.stop = False
        elif action == ACTION_LEFT:
            tank.direction = 'Left'
            tank.stop = False
        elif action == ACTION_RIGHT:
            tank.direction = 'Right'
            tank.stop = False
        elif action == ACTION_SHOOT:
            if len(self.myBulletList) < 2:
                self.myBulletList.append(Bullet(tank))

    def calculate_reward(self, current_state):
        """calculate reward"""
        self.reward = 0
        self.reward += REWARD_SURVIVE

        # 2. Positive rewarded：destroy enemy
        enemy_killed = self.last_enemy_count - self.get_enemy_count()
        if enemy_killed > 0:
            self.reward += enemy_killed * REWARD_KILL_ENEMY

        # 3. Positive rewarded：destroy enemy(not killed)
        for bullet in self.myBulletList:
            for enemy in self.enemyTankList:
                if enemy.is_live and pygame.sprite.collide_rect(bullet, enemy):
                    self.reward += REWARD_HIT_ENEMY
                    break

        # 4. Negative punishment: hitting the wall
        if self.my_tank.oldLeft == self.my_tank.rect.left and \
        self.my_tank.oldTop == self.my_tank.rect.top and not self.my_tank.stop:
            self.reward += PUNISH_HIT_WALL

        # 4. Negative punishment: tank collision
        tank_collision = False
        for enemy in self.enemyTankList:
            if enemy.is_live and self.my_tank.rect.colliderect(enemy.rect.inflate(-5, -5)):
                tank_collision = True
                break
        if tank_collision:
            self.reward += PUNISH_TANK_COLLISION
            # print(f"【惩罚】我方与敌方坦克碰撞，奖励扣减{PUNISH_TANK_COLLISION}")

        # 5. Negative punishment: being hit by the enemy
        if self.my_tank and not self.my_tank.is_live:
            self.reward += PUNISH_BE_HIT

        # 6. Negative punishment: meaningless movement (moving away from the nearest enemy)
        if self.last_state is not None:
            last_enemy_dist = self.get_enemy_distance(self.last_state)
            current_enemy_dist = self.get_enemy_distance(current_state)
            if current_enemy_dist > last_enemy_dist + 10:
                self.reward += PUNISH_USELESS_MOVE

        self.round_reward += self.reward
        self.total_reward += self.reward

    def get_enemy_distance(self, state):
        """Calculate the distance to the nearest enemy"""
        if not self.my_tank or not self.my_tank.is_live:
            return float('inf')
        min_dist = float('inf')
        for enemy in self.enemyTankList:
            if enemy.is_live:
                dist = np.sqrt(
                    (self.my_tank.rect.centerx - enemy.rect.centerx)**2 +
                    (self.my_tank.rect.centery - enemy.rect.centery)**2
                )
                min_dist = min(min_dist, dist)
        return min_dist

    def handle_round_win(self):
        """Handle round win"""
        self.is_round_ended = True
        self.reward += REWARD_ROUND_WIN if self.game_mode == "ai_train" else 0
        self.round_reward += REWARD_ROUND_WIN if self.game_mode == "ai_train" else 0
        self.total_reward += REWARD_ROUND_WIN if self.game_mode == "ai_train" else 0

        # 区分模式打印信息
        mode_text = "AI训练模式" if self.game_mode == "ai_train" else "人机对战模式"
        print(f"\n===== 第{self.current_round}轮胜利 | {mode_text} =====")
        if self.game_mode == "ai_train":
            print(f"本轮步数：{self.round_steps} | 本轮奖励：{self.round_reward:.1f}")
            print(f"累计奖励：{self.total_reward:.1f} | Q表状态数：{len(self.Q_TABLE)}")
            print(f"当前探索率：{EPSILON:.4f}")
        print("======================================")

    def update_q_table(self):
        if self.last_state not in self.Q_TABLE:
            self.Q_TABLE[self.last_state] = [0.0] * ACTION_NUM
        current_state = self.get_state()
        if current_state not in self.Q_TABLE:
            self.Q_TABLE[current_state] = [0.0] * ACTION_NUM

        old_q = self.Q_TABLE[self.last_state][self.last_action]
        current_q_values = self.Q_TABLE[current_state]
        max_current_q = max(current_q_values)
        
        new_q = old_q + ALPHA * (self.reward + GAMMA * max_current_q - old_q)
        self.Q_TABLE[self.last_state][self.last_action] = new_q

    # ===================== 辅助方法（调整墙壁数量）=====================
    def detect_collision(self):
        """detect collision between tank and wall"""
        self.my_tank.hit_wall(self.wallList)
        self.my_tank.myTank_hit_enemy(self.enemyTankList, self.explosionList)

    def blit_all_elements(self):
        """draw all elements on the screen"""
        self.blit_my_tank()
        self.blitEnemyTanks()
        self.blitMyBullets()
        self.blitEnemyBullets()
        self.blitExplosions()
        self.blitWall()

    def init_round(self):
        """init single round"""
        self.enemyTankList.clear()
        self.myBulletList.clear()
        self.enemyBulletList.clear()
        self.explosionList.clear()
        self.wallList.clear()

        self.createMyTank()
        self.createWall()       
        self.createEnemyTanks()

        self.current_action = None
        self.action_hold_count = 0
        self.last_state = None
        self.last_action = None
        self.reward = 0
        self.last_enemy_count = self.get_enemy_count()
        self.is_round_ended = False
        self.round_reward = 0 if ROUND_REWARD_RESET else self.round_reward
        self.round_steps = 0

        if self.current_round == 1:
            self.my_tank_lives = self.my_tank_lives_init  # 第一轮设置为3条生命
        print(f"【生命】剩余生命：{self.my_tank_lives} | 本轮：{self.current_round}")

        if self.game_mode == "ai_train" and self.my_tank and self.my_tank.is_live:
            initial_state = self.get_state()
            if initial_state not in self.Q_TABLE:
                self.Q_TABLE[initial_state] = [0.0] * ACTION_NUM

    def reset_game_for_new_round(self):
        """restart game for new round"""
        self.current_round += 1
        self.init_round()
        print(f"\n开始第{self.current_round}轮... | 模式：{self.game_mode}")

    def get_enemy_count(self):
        """get enemy count"""
        return len([e for e in self.enemyTankList if e.is_live])

    def load_q_table(self):
        if os.path.exists(Q_TABLE_FILE):
            try:
                with open(Q_TABLE_FILE, 'rb') as f:
                    self.Q_TABLE = pickle.load(f)
                self.q_table_loaded = True
                print(f"成功加载Q表，共 {len(self.Q_TABLE)} 个状态")
            except Exception as e:
                print(f"加载Q表失败：{e}")
                self.Q_TABLE = {}
        else:
            print("未找到Q表，从头训练")

    def save_q_table(self):
        """保存Q表（仅AI训练模式）"""
        if self.game_mode == "ai_train":
            try:
                with open(Q_TABLE_FILE, 'wb') as f:
                    pickle.dump(self.Q_TABLE, f)
                print(f"Q表已保存到 {Q_TABLE_FILE}")
            except Exception as e:
                print(f"保存Q表失败：{e}")

    def draw_info(self):
        """绘制游戏信息（新增模式显示+生命显示）"""
        def getTextSurface(text, color=TEXT_COLOR):
            pygame.font.init()
            font = pygame.font.SysFont(TEXT_FONT, 18)
            return font.render(text, True, color)
        
        # display mode
        mode_color = (0, 255, 255) if self.game_mode == "ai_train" else (255, 255, 0)
        mode_text = f"Mode: {self.game_mode.upper().replace('_', ' ')}"
        self.window.blit(getTextSurface(mode_text, mode_color), (20, 20))
        
        # display life
        life_color = (255, 0, 0)  # red
        life_text = f"Lives: {self.my_tank_lives}/{MY_TANK_INIT_LIVES}"  # remaining lives/total lives
        self.window.blit(getTextSurface(life_text, life_color), (20, 32))
        
        # basic information
        self.window.blit(getTextSurface(f"Round: {self.current_round}/{MAX_TRAIN_ROUNDS}"), (20, 47))
        self.window.blit(getTextSurface(f"Enemies: {self.get_enemy_count()}"), (20, 70))
        
        # AI Training mode information
        if self.game_mode == "ai_train":
            self.window.blit(getTextSurface(f"Step: {self.train_step} | Epsilon: {EPSILON:.4f}"), (20, 95))
            self.window.blit(getTextSurface(f"Round Reward: {self.round_reward:.1f}"), (20, 120))
            self.window.blit(getTextSurface(f"Total Reward: {self.total_reward:.1f}"), (20, 145))
            self.window.blit(getTextSurface(f"Q-Table States: {len(self.Q_TABLE)}"), (20, 170))
        
        # Human vs AI mode information
        if self.game_mode == "human_vs_ai":
            self.window.blit(getTextSurface("↑↓←→ : Move | Space : Shoot", (100, 200, 100)), (20, 95))
        
        # Frame rate
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        self.window.blit(getTextSurface(fps_text, (0, 255, 0)), (SCREEN_WIDTH - 80, 20))

        # Winning text
        if self.is_round_ended:
            win_text = getTextSurface(f"Round {self.current_round} Win! All Enemies Killed!", (0, 255, 0))
            self.window.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2))


    def createEnemyTanks(self):
        """create enemy tanks"""
        target_enemy_count = self.enemyTankCount
        created_count = 0
        max_retries = 2000
        retry_count = 0
        top_base = 50
        tank_size = TANK_SIZE
        my_tank_rect = self.my_tank.rect if self.my_tank else None

        while created_count < target_enemy_count and retry_count < max_retries:
            retry_count += 1
            left = random.randint(tank_size, SCREEN_WIDTH - 2*tank_size)
            top = random.randint(top_base, SCREEN_HEIGHT - 2*tank_size)
            speed = ENEMY_TANK_SPEED
            new_enemy = EnemyTank(left, top, speed)

            if (new_enemy.rect.left < tank_size/2 or 
                new_enemy.rect.right > SCREEN_WIDTH - tank_size/2 or 
                new_enemy.rect.top < tank_size/2 or 
                new_enemy.rect.bottom > SCREEN_HEIGHT - tank_size/2):
                continue

            overlap_enemy = False
            for existing_enemy in self.enemyTankList:
                if new_enemy.rect.colliderect(existing_enemy.rect.inflate(10, 10)):
                    overlap_enemy = True
                    break
            if overlap_enemy:
                continue

            if my_tank_rect and new_enemy.rect.colliderect(my_tank_rect.inflate(10, 10)):
                continue

            overlap_wall = False
            for wall in self.wallList:
                if new_enemy.rect.colliderect(wall.rect):
                    overlap_wall = True
                    break
            if overlap_wall:
                continue

            self.enemyTankList.append(new_enemy)
            created_count += 1

        if created_count < target_enemy_count:
            print(f"警告：第{self.current_round}轮仅生成 {created_count}/{target_enemy_count} 个敌方坦克")
        else:
            print(f"第{self.current_round}轮：成功生成 {created_count} 个敌方坦克（无重叠）")

    def createMyTank(self):
        """create my tank"""
        self.my_tank = MyTank(SCREEN_WIDTH//2 - TANK_SIZE//2, SCREEN_HEIGHT - TANK_SIZE - 20)

    def createWall(self):
        """create wall"""
        target_wall_count = WALL_COUNT  # 使用新的常量
        created_count = 0
        wall_size = WALL_SIZE
        max_retries = 1000
        retry_count = 0

        while created_count < target_wall_count and retry_count < max_retries:
            retry_count += 1
            left = random.randint(wall_size, SCREEN_WIDTH - 2*wall_size)
            top = random.randint(wall_size, SCREEN_HEIGHT - 2*wall_size)
            new_wall = Wall(left, top)

            if (new_wall.rect.left < wall_size/2 or 
                new_wall.rect.right > SCREEN_WIDTH - wall_size/2 or 
                new_wall.rect.top < wall_size/2 or 
                new_wall.rect.bottom > SCREEN_HEIGHT - wall_size/2):
                continue

            is_overlap = False
            for existing_wall in self.wallList:
                if new_wall.rect.colliderect(existing_wall.rect):
                    is_overlap = True
                    break
            if self.my_tank and new_wall.rect.colliderect(self.my_tank.rect.inflate(10, 10)):
                is_overlap = True

            if not is_overlap:
                self.wallList.append(new_wall)
                created_count += 1

        if created_count < target_wall_count:
            print(f"第{self.current_round}轮：仅生成 {created_count}/{target_wall_count} 个墙壁")
        else:
            print(f"第{self.current_round}轮：成功生成 {target_wall_count} 个墙壁")

    # ===================== 绘制方法（适配更大界面）=====================
    def blit_my_tank(self):
        if self.my_tank and self.my_tank.is_live:
            self.my_tank.displayTank(self.window)
        else:
            if self.my_tank:
                del self.my_tank
            self.my_tank = None

    def blitEnemyTanks(self):
        for enemytank in self.enemyTankList:
            if enemytank.is_live:
                enemytank.displayTank(self.window)
                enemytank.randomMove(self.enemyTankList)
                enemytank.hit_wall(self.wallList)
                enemyBullet = enemytank.shoot()
                if enemyBullet is not None:
                    self.enemyBulletList.append(enemyBullet)
            else:
                self.enemyTankList.remove(enemytank)

    def blitMyBullets(self):
        for myBullet in self.myBulletList:
            if myBullet.is_live:
                myBullet.displayBullet(self.window)
                myBullet.moveBullet()
                myBullet.my_bullet_hit_enemy(self.enemyTankList, self.explosionList)
                myBullet.hit_wall(self.wallList)
            else:
                self.myBulletList.remove(myBullet)

    def blitEnemyBullets(self):
        for enemyBullet in self.enemyBulletList:
            if enemyBullet.is_live:
                enemyBullet.displayBullet(self.window)
                enemyBullet.moveBullet()
                enemyBullet.enemy_bullet_hit_myTank(self.my_tank, self.explosionList)
                enemyBullet.hit_wall(self.wallList)
            else:
                self.enemyBulletList.remove(enemyBullet)

    def blitExplosions(self):
        for explosion in self.explosionList:
            if explosion.is_live:
                explosion.displayExplosion(self.window)
            else:
                self.explosionList.remove(explosion)

    def blitWall(self):
        for wall in self.wallList:
            wall.displayWall(self.window)

    def get_event(self):
        """处理游戏事件"""
        eventList = pygame.event.get()
        for event in eventList:
            if event.type == pygame.QUIT:
                self.save_q_table()
                self.end_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.save_q_table()
                self.end_game()

    def end_game(self):
        """结束游戏"""
        self.save_q_table()
        print("\n===== 游戏结束 =====")
        if self.game_mode == "ai_train":
            print(f"总训练轮次：{self.current_round}")
            print(f"总训练步数：{self.train_step}")
            print(f"总奖励：{self.total_reward:.1f}")
            print(f"Q表最终状态数：{len(self.Q_TABLE)}")
            print(f"最终探索率：{EPSILON:.4f}")
        else:
            print(f"模式：人机对战 | 总轮次：{self.current_round}")
        print("====================")
        
        if self.game_mode == "ai_train":
            print("\nQ表示例（状态→动作Q值）：")
            for i, (state, q_vals) in enumerate(self.Q_TABLE.items()):
                if i >= 5:
                    break
                print(f"状态{state}: Q值={[round(q, 2) for q in q_vals]}")
        
        pygame.quit()
        exit()

if __name__ == "__main__":
    MainGame().start_game()