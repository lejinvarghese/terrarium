"""Configuration for Terrarium Incubator"""

from pathlib import Path
import click

# Paths
INCUBATOR_DIR = Path(__file__).parent
DB_PATH = INCUBATOR_DIR / "observations.db"
CHECKPOINT_DIR = INCUBATOR_DIR / "checkpoints"
SCREENSHOT_DIR = INCUBATOR_DIR / "screenshots"
LOGS_DIR = INCUBATOR_DIR / "logs"

# Create directories
for dir_path in [CHECKPOINT_DIR, SCREENSHOT_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

(CHECKPOINT_DIR / "base").mkdir(exist_ok=True)
(CHECKPOINT_DIR / "agents").mkdir(exist_ok=True)

# Model configuration
# Using Ollama for automatic CPU/GPU offloading and memory management
USE_OLLAMA = True

# Model selection (uncomment one):
OLLAMA_MODEL = "dagbs/qwen2.5-coder-1.5b-instruct-abliterated"  # Current - 1.5B params
# OLLAMA_MODEL = "qwen2.5-coder:3b"  # ✅ RECOMMENDED if 1.5B struggles - better instruction following
# OLLAMA_MODEL = "qwen2.5:3b"  # ✅ Alternative - general purpose, good at following formats
# OLLAMA_MODEL = "smollm2:1.7b"  # ❌ Too small - struggled with instructions

# Note: If you see repeated formatting errors (missing <code> tags),
# try a larger model like qwen2.5-coder:3b for better instruction following

MODEL_NAME = "HuggingFaceTB/SmolVLM2-500M-Instruct"  # Fallback for transformers
DEVICE = "cuda"
MAX_NEW_TOKENS = 2048  # Increased for more complete code generation
TEMPERATURE = 0.7

# Exploration configuration
DEFAULT_EPISODE_STEPS = 10
SCREENSHOT_ENABLED = True

# Training configuration
LORA_RANK = 8
LORA_ALPHA = 16
LEARNING_RATE = 2e-4
TRAIN_EPOCHS = 3
REWARD_THRESHOLD = 0.5  # Only train on observations with reward > this

click.secho(f"[Incubator] Device: {DEVICE}", fg="cyan")
click.secho(f"[Incubator] Model: {MODEL_NAME}", fg="cyan")
click.secho(f"[Incubator] DB: {DB_PATH}", fg="cyan")
