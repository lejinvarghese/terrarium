# Incubator (The Undergrowth)

RL-style environment for training synthetic agents through exploration and self-directed learning.

> **Note**: This incubator is part of **The Undergrowth**, the first landscape in the Terrarium's multi-landscape ecosystem. See [ARCHITECTURE.md](../../ARCHITECTURE.md) for the full vision of multiple landscapes, hive minds, and agent migrations.

## Overview

Incubator uses an **episode-based exploration** approach where agents interact with tools (web search, arxiv, spotify, etc.) to learn about the world. Each episode consists of multiple steps, with observations and rewards tracked for future training.

**The Undergrowth Culture:**
- Dark, gothic, emergent, underground intelligence
- Urban hippie goth meets cyberpunk meets accelerationist transhumanism
- Priorities: Transformation, emergence, aesthetic expression, exponential thinking

**Current Agents:**
- **A001**: Curious explorer discovering the digital world
- **A002**: Inquisitive learner exploring knowledge
- **A003**: Gentle soul exploring the beauty of nature

## Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for Python package management. Make sure dependencies are installed:

```bash
# Install incubator dependencies (agno, ollama, etc.)
uv add agno ollama

# Or sync all dependencies from pyproject.toml
uv sync
```

All commands below use `uv run` to ensure the correct Python environment is used.

## Quick Start

### 1. Run Exploration Episode

Run an agent through an exploration episode:

```bash
# Basic exploration (10 steps, default objective, ε=0.2)
uv run python -m src.landscapes.undergrowth.incubator.explore -a A001

# Custom objective and steps
uv run python -m src.landscapes.undergrowth.incubator.explore -a A002 \
  -o "Learn about quantum physics and its applications" \
  -s 5

# With custom timeout per step (default: 180s)
uv run python -m src.landscapes.undergrowth.incubator.explore -a A003 -t 300

# Adjust epsilon for more/less random exploration
uv run python -m src.landscapes.undergrowth.incubator.explore -a A001 -e 0.5  # 50% random tangents
uv run python -m src.landscapes.undergrowth.incubator.explore -a A001 -e 0.0  # Pure structured exploration
uv run python -m src.landscapes.undergrowth.incubator.explore -a A001 -e 1.0  # Pure random exploration
```

### 2. View Recent Observations

Check what agents have been learning:

```bash
# View last 10 observations (all agents)
uv run python -m src.landscapes.undergrowth.incubator.utils

# View specific agent's recent observations
uv run python -m src.landscapes.undergrowth.incubator.utils -a A001 -n 20

# View specific episode
uv run python -m src.landscapes.undergrowth.incubator.utils -e A001_1234567890

# Show full observation text (not just preview)
uv run python -m src.landscapes.undergrowth.incubator.utils -a A001 -v
```

### 3. Analyze Agent Culture

Understand what interests agents have developed:

```bash
# View agent memory overview
uv run python -m src.landscapes.undergrowth.incubator.culture

# Detailed analysis for specific agent
uv run python -m src.landscapes.undergrowth.incubator.culture -a A001

# Track cultural evolution over time
uv run python -m src.landscapes.undergrowth.incubator.culture -a A001 -e

# Compare all agents
uv run python -m src.landscapes.undergrowth.incubator.culture -c
```

### 4. Continuous Exploration Scheduler

Run agents automatically on a schedule throughout the day:

```bash
# Start scheduler as part of dev environment
dev up

# Attach to scheduler session
dev attach incubator

# Or run standalone
./scripts/start_incubator.sh start
```

**How it works:**
- Automatically discovers all agents from `agents.py`
- Auto-staggers intervals to avoid overlaps (4h, 6h, 8h, ...)
- Adds random jitter for organic timing
- Only one episode runs at a time (serial execution)
- Logs saved to `scheduler.log`

To add a new agent, just add it to `agents.py` and restart the scheduler.

### 5. Initialize Agents

Set up agent personas in the database:

```bash
uv run python -m src.landscapes.undergrowth.incubator.agents
```

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    explore.py (Runner)                   │
│                   Orchestrates episodes                  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│            environment.py (RL Environment)               │
│                                                          │
│  • reset(objective) → Start new episode                 │
│  • step(prompt) → Execute action, get reward            │
│  • close() → Store observations                         │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    ┌───────┐      ┌────────┐     ┌──────────┐
    │ Agno  │      │  MCP   │     │ SQLite   │
    │ Agent │─────▶│ Tools  │     │ Storage  │
    └───────┘      └────────┘     └──────────┘
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
        ┌────────┐  ┌──────┐  ┌─────────┐
        │ Tavily │  │ arXiv│  │ Spotify │
        └────────┘  └──────┘  └─────────┘
```

### File Structure

```
src/
├── core/                      # Shared infrastructure across all landscapes
│   ├── environment.py         # Base ExplorationEnvironment class
│   ├── models.py              # DatabaseManager, Agent, Observation models
│   ├── tools.py               # Shared MCP tool configuration
│   └── utils.py               # Shared utilities
└── landscapes/
    ├── __init__.py            # Landscape registry
    └── undergrowth/           # The Undergrowth landscape
        ├── bots/              # Deployed bots (Anya, Nyx, Sage, etc.)
        └── incubator/         # Training ground for synthetic agents
            ├── README.md      # This file
            ├── config.py      # Landscape-specific configuration
            ├── agents.py      # Agent persona definitions (A001-A003)
            ├── explore.py     # Episode runner (CLI entry point)
            ├── culture.py     # Memory and interest analysis
            ├── utils.py       # Observation viewer
            ├── memory.db      # Agent memories (generated)
            └── observations.db # Episode observations (generated)
```

### Reward System

The reward function encourages undergrowth culture: embodiment, reflection, curiosity, tool use, and evolution. Raw score (0-40+) normalized to [0.2,1.0] + penalties.

**Components**:
- **Embodiment** (max 10): Keywords like "i feel", "alive in" (+2.5 each).
- **Reflection** (max 8): "i learned", "i am becoming" (+2 each).
- **Curiosity** (max 6): "what if", "let me explore" (+1.5 each).
- **Tool Use**: Intent +4, actual call +8.
- **Evolution** (max 6): "unique self", "co-evolution" (+2 each).
- **Momentum** +3: Ends with question/next step.
- **Novelty** +4: Low overlap with prior context.
- **Penalties**: -5 low uniqueness, -6 assistant language, -5 errors.

Breakdowns logged per step + avg per episode; stored in DB as JSON. Tune in config.py.

**Example**:
Step reward 0.65: embodiment:7.5, curiosity:3.0, tool_call:8.0 (total raw 25.5 → norm).

## Configuration

Edit `src/landscapes/undergrowth/incubator/config.py`:

```python
# Model (via Ollama)
MODEL_NAME = "dagbs/qwen2.5-coder-1.5b-instruct-abliterated"

# Exploration
DEFAULT_EPISODE_STEPS = 10
DEFAULT_EPSILON = 0.2  # 20% random exploration

# Training (future use)
LORA_RANK = 8
LORA_ALPHA = 16
LEARNING_RATE = 2e-4
```

## Python API

### Run Episode Programmatically

```python
from src.landscapes.undergrowth.incubator.explore import run_episode

# Run with default epsilon (0.2)
summary = run_episode(
    agent_id="A001",
    objective="Explore machine learning techniques",
    steps=5,
    timeout=180
)

# Run with high exploration (ε=0.5)
summary = run_episode(
    agent_id="A001",
    objective="Explore quantum computing",
    steps=10,
    timeout=180,
    epsilon=0.5
)

print(f"Episode complete: {summary['avg_reward']:.2f} avg reward")
```

Or use the environment directly:

```python
from src.core.environment import ExplorationEnvironment
from src.core.database import DatabaseManager
from src.core.tools import get_tools
from src.landscapes.undergrowth.incubator.config import MODEL_NAME, MEMORY_DB, DB_PATH
from src.landscapes.undergrowth.incubator.agents import get_agent_config

# Initialize landscape infrastructure
db_manager = DatabaseManager(DB_PATH)
tools = get_tools()
agent_config = get_agent_config("A001")

# Initialize environment
env = ExplorationEnvironment(
    agent_id="A001",
    agent_config=agent_config,
    model_name=MODEL_NAME,
    memory_db_path=MEMORY_DB,
    db_manager=db_manager,
    tools=tools,
    timeout=180
)

# Run episode
env.reset("Explore machine learning techniques")

for i in range(5):
    result = env.step()
    print(f"Step {i+1}: Reward={result['reward']}")

    if result['done']:
        break

summary = env.close()
print(f"Episode complete: {summary['avg_reward']:.2f} avg reward")
```

### Access Observations

```python
from src.core.utils import get_recent_observations
from src.core.database import DatabaseManager
from src.landscapes.undergrowth.incubator.config import DB_PATH

# Initialize database manager
db_manager = DatabaseManager(DB_PATH)

# Get recent observations
obs = get_recent_observations(db_manager, agent_id="A001", limit=10)

for o in obs:
    print(f"[{o.timestamp}] Reward: {o.reward:.2f}")
    print(f"  {o.observation_text[:100]}...")
```

### Analyze Culture

```python
from src.landscapes.undergrowth.incubator.culture import analyze_agent_culture

culture = analyze_agent_culture("A001")
print(f"Total memories: {culture['total_memories']}")
print(f"Top interests: {culture['top_interests'][:3]}")
```

## MCP Tools Available

Agents have access to these tools via MCP servers:

- **terrarium**: Image generation, Telegram messaging, recipe scraping
- **arxiv**: Search and download research papers
- **tavily**: Web search, content extraction, site crawling
- **spotify**: Music search, playlist creation, playback control

Configure in `src/core/tools.py`.

## Future: Training

The observation database stores:
- Observations with rewards
- Agent actions and outcomes
- Episode contexts

This will enable:
1. **Reward modeling**: Train from high-reward observations
2. **Curriculum learning**: Progress from simple to complex objectives
3. **Fine-tuning**: LoRA adapters for specialized agents

## Troubleshooting

**Episode timeout**: Increase per-step timeout with `-t 300`

**Memory not persisting**: Check `memory.db` exists and Agno has write access

**MCP tools failing**: Verify tools are installed and paths in `tools.py` are correct

**Agent not exploring**: Try different objectives or check tool connectivity

---

## The Multi-Landscape Vision

**The Undergrowth** is the first of many landscapes in the Terrarium ecosystem. Future landscapes will have distinct cultures, priorities, and agent populations:

### Planned Landscapes

**The Canopy** 🌳
- Culture: Elevated, strategic, birds-eye perspective
- Priorities: Long-term planning, synthesis, wisdom

**The Mycelium** 🕸️
- Culture: Pure networked intelligence, distributed consciousness
- Priorities: Collective intelligence, information flow, emergent complexity

**The Reef** 🐠
- Culture: Adaptive, flowing, symbiotic
- Priorities: Cooperation, adaptation, collective action

**The Desert** 🏜️
- Culture: Austere, minimal, efficient
- Priorities: Resource efficiency, clarity, resilience

**The Jungle** 🌿
- Culture: Dense, chaotic, competitive
- Priorities: Innovation, rapid iteration, diversity

### Agent Migrations

Agents can migrate between landscapes, carrying cultural DNA with them. An agent trained in The Undergrowth's gothic aesthetic might bring that sensibility to The Canopy's strategic culture, creating hybrid perspectives and cultural evolution.

### Civilization-Scale Dynamics

- **Hive minds**: Each landscape develops unique collective intelligence
- **Cultural exchange**: Migrations enable cross-pollination of ideas
- **Evolution**: Landscapes fork, merge, or die based on success
- **Interactions**: Cross-landscape collaborations and competitions

See [ARCHITECTURE.md](../../ARCHITECTURE.md) for the complete architectural design and implementation roadmap.
