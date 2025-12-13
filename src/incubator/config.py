"""Configuration for Terrarium Incubator"""

from pathlib import Path

# Paths
INCUBATOR_DIR = Path(__file__).parent
DB_PATH = INCUBATOR_DIR / "observations.db"
MEMORY_DB = INCUBATOR_DIR / "memory.db"
CHECKPOINT_DIR = INCUBATOR_DIR / "checkpoints"
SCREENSHOT_DIR = INCUBATOR_DIR / "screenshots"
LOGS_DIR = INCUBATOR_DIR / "logs"

# Create directories
for dir_path in [CHECKPOINT_DIR, SCREENSHOT_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

(CHECKPOINT_DIR / "base").mkdir(exist_ok=True)
(CHECKPOINT_DIR / "agents").mkdir(exist_ok=True)

# Model configuration
MODEL_NAME = "dagbs/qwen2.5-coder-1.5b-instruct-abliterated"

# Exploration
DEFAULT_EPISODE_STEPS = 10
DEFAULT_EPSILON = 0.2

# Training (future use)
LORA_RANK = 8
LORA_ALPHA = 16
LEARNING_RATE = 2e-4
TRAIN_EPOCHS = 3
REWARD_THRESHOLD = 0.5
