# Q-learning-Tank-war
A classic tank battle game implemented in Python (Pygame) with dual gameplay modes (AI training / human vs AI) and integrated Q-Learning reinforcement learning algorithm. The game features a 3-life system for the player tank, anti-overlap logic for enemy tanks, and complete collision detection mechanics.

## 📋 Project Introduction
### Core Features
- **Dual Game Modes**:
  - AI Training Mode: Q-Learning agent autonomously controls the player tank to learn combat strategies (obstacle avoidance, enemy elimination).
  - Human vs AI Mode: Players manually control the tank to fight against AI-driven enemy tanks.
- **3-Life System**: The player tank has 3 initial lives; the game ends when lives are exhausted.
- **Anti-Overlap for Enemy Tanks**: Enemy tanks avoid overlap during generation and movement via collision prediction.
- **Complete Collision Detection**: Supports tank-wall, tank-enemy, bullet-tank/bullet-wall collisions.
- **Q-Learning Integration**: Discrete state-action space design, ε-greedy exploration strategy, and reward-guided AI learning.
- **Round-Based Training**: Auto-reset after round victory (max 10 training rounds) with Q-table persistence.

### Technology Stack
- **Language**: Python 3.8+
- **Game Engine**: Pygame 2.5.2+
- **Reinforcement Learning**: Q-Learning (value-based RL algorithm)
- **Auxiliary Libraries**: Pickle (Q-table persistence), NumPy (state discretization)

## 🛠️ Environment Setup
### 1. Install Python
Download and install Python 3.8 or higher from [Python Official Website](https://www.python.org/downloads/).

### 2. Install Dependencies
Run the following command in the terminal to install required libraries:
```bash
pip install pygame numpy
```

## 🚀 Quick Start
### 1. Clone/Download Code
Save all project files (e.g., `main.py`, `tank.py`, `config.py`) to a single directory.

### 2. Run the Game
Execute the main file to start the game:
```bash
python main.py
```

### 3. Game Operation
#### Main Menu
- Press `ENTER` to enter mode selection.
- Press `ESC` to exit the game.

#### Mode Selection
- Press `1` to start **AI Training Mode** (AI controls the tank automatically).
- Press `2` to start **Human vs AI Mode** (manual control).
- Press `ESC` to return to the main menu.

#### Human Control (Human vs AI Mode)
- Movement: `W` (Up) / `S` (Down) / `A` (Left) / `D` (Right) (or arrow keys).
- Shoot: `SPACE` key (max 2 live bullets).
- Exit: `ESC` key.

#### AI Training Mode
- The AI will automatically learn and act; training progress (round, reward, Q-table size) is printed in the console.
- The game auto-resets after round victory (max 10 rounds) and saves the Q-table to `q_table.pkl` after training.

## 📂 Code Structure
| File Name       | Description                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| `main.py`       | Core game management: game loop, mode switching, Q-Learning training, collision scheduling. |
| `tank.py`       | Tank class definitions: `Tank` (base class), `MyTank` (player/AI tank), `EnemyTank` (AI enemy tank with anti-overlap). |
| `bullet.py`     | Bullet entity: movement, collision detection, lifecycle management.         |
| `wall.py`       | Indestructible wall obstacle: collision detection and rendering.            |
| `explosion.py`  | Explosion effect: animated rendering when tanks are destroyed.              |
| `config.py`     | Game configuration: constants (screen size, tank speed, reward values, Q-Learning parameters). |
| `base_item.py`  | Base class for all game entities: encapsulates common attributes (position, survival state) and methods (position rollback). |
| `q_table.pkl`   | Persisted Q-table file (generated after AI training, reused in subsequent runs). |

### Core Class Overview
| Class Name       | Core Responsibilities                                                                 |
|-------------------|--------------------------------------------------------------------------------------|
| `MainGame`        | Coordinates game flow, Q-Learning state acquisition/table update, round management.  |
| `MyTank`          | Player/AI-controlled tank with 3-life mechanism and dual-mode control.               |
| `EnemyTank`       | AI enemy tank with random movement (anti-overlap) and periodic shooting.             |
| `BaseItem`        | Base class for all entities (tanks, bullets, walls) with collision/position logic.   |

## 🧠 Q-Learning Algorithm
### Core Formula
The Q-Learning algorithm updates the Q-table (state-action value) using the following formula:
$$Q(s,a) = Q(s,a) + \alpha \times [r + \gamma \times \max(Q(s',a')) - Q(s,a)]$$
- $\alpha$ (Learning Rate): 0.1 (controls the weight of new experience).
- $\gamma$ (Discount Factor): 0.9 (prioritizes future rewards).
- $r$ (Immediate Reward): Custom reward function (e.g., +50 for killing an enemy, -80 for losing a life).

### State & Action Space
#### State Space (6-Dimensional Discrete Vector)
`(my_x, my_y, my_dir, nearest_enemy_dir, enemy_count, my_bullet_count)`:
- `my_x`/`my_y`: Discretized player tank position (800×600 screen → 10×10 bins).
- `my_dir`: Player tank direction (0=Up, 1=Down, 2=Left, 3=Right).
- `nearest_enemy_dir`: Direction to the nearest enemy (0-4, 4=no enemy).
- `enemy_count`: Number of live enemy tanks (0-3).
- `my_bullet_count`: Number of live bullets (0=none, 1=1+).

#### Action Space (5 Discrete Actions)
- 0: Move Up
- 1: Move Down
- 2: Move Left
- 3: Move Right
- 4: Shoot

### Reward Function
| Behavior                          | Reward Value |
|-----------------------------------|--------------|
| Survival per frame                | +1           |
| Hit enemy tank (non-lethal)       | +10          |
| Kill one enemy tank               | +50          |
| Round win (kill all enemies)      | +100         |
| Collide with wall                 | -15          |
| Be hit by enemy bullet (lose life)| -80          |
| Collide with enemy tank           | -30          |
| Move away from nearest enemy      | -2           |

## ❓ FAQ
### 1. Enemy Tanks Overlap
**Solution**: The `EnemyTank.randomMove()` method predicts movement positions and detects overlap with other enemies; if overlap is detected, the enemy tank changes direction immediately. Ensure:
- `randomMove` receives the full enemy tank list as a parameter.
- `oldLeft`/`oldTop` are recorded in the `move` method of `EnemyTank`.

### 2. AI Tank "Twitches" (Frequent Action Switching)
**Solution**: Each action is sustained for 5 frames (`ACTION_HOLD_FRAMES = 5`) to stabilize movement; reduce the decision frequency with `time.sleep(0.02)` in the game loop.

### 3. Life System Not Working
**Checklist**:
- `MY_TANK_INIT_LIVES = 3` is added in `config.py`.
- `my_tank_lives` is initialized in `MainGame.init_round()`.
- Life deduction logic is implemented in `MainGame.start_game()` (reduce life when the tank is destroyed).

### 4. Q-Learning KeyError
**Solution**: Initialize new states with `[0.0] * 5` in `MainGame.choose_action()` to avoid uninitialized state keys in the Q-table.

## 🚀 Extension Directions
- **Deep Q-Network (DQN)**: Replace Q-table with a neural network to handle larger state spaces (e.g., dynamic maps, more enemies).
- **Multi-Agent Training**: Let enemy tanks also learn via Q-Learning (instead of random movement).
- **Dynamic Difficulty**: Adjust enemy speed/shooting probability based on AI/player performance.
- **Sound Effects**: Add shooting/explosion/victory sound effects.
- **Map Customization**: Support multiple map layouts (random wall generation).

## 📄 License
This project is for educational purposes only (learning Pygame and Q-Learning). You are free to modify and extend the code for non-commercial use.

## 📞 Contact
If you encounter issues (e.g., code bugs, algorithm questions), feel free to raise an issue or contact the developer.
