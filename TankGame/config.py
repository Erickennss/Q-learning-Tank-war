import pygame

# Initialize pygame
pygame.init()

# ===================== 游戏基础配置（调整界面大小）=====================
SCREEN_WIDTH = 1000  
SCREEN_HEIGHT = 600 
FPS = 60            
TEXT_COLOR = (255, 255, 255)
TEXT_FONT = "Arial"

# ===================== 状态空间配置 =====================
X_BINS = 10
Y_BINS = 10
X_STEP = SCREEN_WIDTH // X_BINS
Y_STEP = SCREEN_HEIGHT // Y_BINS

# 方向常量
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3
DIR_NONE = 4

# ===================== 动作空间配置 =====================
ACTION_UP = 0
ACTION_DOWN = 1
ACTION_LEFT = 2
ACTION_RIGHT = 3
ACTION_SHOOT = 4
ACTION_LIST = [ACTION_UP, ACTION_DOWN, ACTION_LEFT, ACTION_RIGHT, ACTION_SHOOT]
ACTION_NUM = len(ACTION_LIST)
ACTION_HOLD_FRAMES = 5  # 防止坦克抽搐

# ===================== 奖励函数配置 =====================
# 正向奖励
REWARD_SURVIVE = 1
REWARD_HIT_ENEMY = 10
REWARD_KILL_ENEMY = 50
REWARD_ROUND_WIN = 100

# 负向惩罚
PUNISH_HIT_WALL = -15
PUNISH_BE_HIT = -80
PUNISH_USELESS_MOVE = -2
PUNISH_TANK_COLLISION = -30

# ===================== Q-Learning超参数 =====================
ALPHA = 0.1       # 学习率
GAMMA = 0.9       # 折扣因子
EPSILON = 0.5     # 初始探索率
EPSILON_DECAY = 0.999  # 探索率衰减
EPSILON_MIN = 0.01    # 最小探索率
Q_TABLE_FILE = "q_table.pkl"

# ===================== 训练配置 =====================
MAX_TRAIN_ROUNDS = 10
AUTO_RESET_AFTER_WIN = True
ROUND_REWARD_RESET = True
MAX_TRAIN_STEPS = 10000

# ===================== 游戏实体尺寸 =====================
TANK_SIZE = 50
WALL_SIZE = 50
BULLET_SIZE = 10
EXPLOSION_SIZE = 50
MY_TANK_INIT_LIVES = 3

# ===================== 移动速度 =====================
MY_TANK_SPEED = 2.25    # 玩家控制时速度稍快
ENEMY_TANK_SPEED = 2
BULLET_SPEED = 6

# ===================== 墙壁数量（增加）=====================
WALL_COUNT = 5  