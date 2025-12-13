# Incubator

RL-style environment for training synthetic agents through exploration and self-directed learning.

## Overview

Incubator uses an **episode-based exploration** approach where agents interact with tools (web search, arxiv, spotify, etc.) to learn about the world. Each episode consists of multiple steps, with observations and rewards tracked for future training.

**Current Agents:**
- **A001**: Curious explorer discovering the digital world
- **A002**: Inquisitive learner exploring knowledge
- **A003**: Gentle soul exploring the beauty of nature

## Quick Start

### 1. Run Exploration Episode

Run an agent through an exploration episode:

```bash
# Basic exploration (10 steps, default objective, ε=0.2)
python -m src.incubator.explore -a A001

# Custom objective and steps
python -m src.incubator.explore -a A002 \
  -o "Learn about quantum physics and its applications" \
  -s 5

# With custom timeout per step (default: 180s)
python -m src.incubator.explore -a A003 -t 300

# Adjust epsilon for more/less random exploration
python -m src.incubator.explore -a A001 -e 0.5  # 50% random tangents
python -m src.incubator.explore -a A001 -e 0.0  # Pure structured exploration
python -m src.incubator.explore -a A001 -e 1.0  # Pure random exploration
```

### 2. View Recent Observations

Check what agents have been learning:

```bash
# View last 10 observations (all agents)
python -m src.incubator.utils

# View specific agent's recent observations
python -m src.incubator.utils -a A001 -n 20

# View specific episode
python -m src.incubator.utils -e A001_1234567890

# Show full observation text (not just preview)
python -m src.incubator.utils -a A001 -v
```

### 3. Analyze Agent Culture

Understand what interests agents have developed:

```bash
# View agent memory overview
python -m src.incubator.culture

# Detailed analysis for specific agent
python -m src.incubator.culture -a A001

# Track cultural evolution over time
python -m src.incubator.culture -a A001 -e

# Compare all agents
python -m src.incubator.culture -c
```

### 4. Initialize Agents

Set up agent personas in the database:

```bash
python -m src.incubator.agents
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
src/incubator/
├── README.md                  # This file
├── config.py                  # Configuration (model, paths, hyperparams)
├── agents.py                  # Agent persona definitions
├── environment.py             # RL-style exploration environment
├── explore.py                 # Episode runner (CLI entry point)
├── models.py                  # Database models (observations, agents)
├── tools.py                   # MCP tool configuration
├── culture.py                 # Memory and interest analysis
├── utils.py                   # Observation viewer utilities
└── observations.db            # SQLite database (generated)
```

## RL Terminology

- **Episode**: Complete exploration session (e.g., 10 steps exploring nature)
- **Step**: Single action where agent uses tools and receives reward
- **Observation**: What agent discovers/learns in a step
- **Reward**: Quality score for observation (-0.5 to 0.7)
- **State**: Agent's accumulated knowledge and context
- **Action**: Agent's tool usage and information gathering
- **Epsilon (ε)**: Exploration-exploitation tradeoff parameter (0.0-1.0)
  - At each step, with probability ε, agent follows a **random tangent** (explore)
  - With probability 1-ε, agent follows **structured prompts** (exploit)
  - Default ε=0.2 (20% random exploration)

### Epsilon-Greedy Exploration

The agent balances two strategies:

**Structured Prompts (Exploitation - probability 1-ε):**
- Follow logical progression: deeper analysis → patterns → synthesis
- Build coherent understanding of the objective
- Systematic knowledge accumulation

**Random Prompts (Exploration - probability ε):**
- "Follow a tangent. Pick something unrelated and see where it leads."
- "What's the weirdest thing you could explore right now?"
- "Find a connection between this topic and something completely unrelated."
- Discover unexpected connections and novel insights

Higher ε → more serendipity and creativity
Lower ε → more focused and systematic exploration

## Configuration

Edit `src/incubator/config.py`:

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
from src.incubator.explore import run_episode

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
from src.incubator.environment import ExplorationEnvironment

# Initialize
env = ExplorationEnvironment(agent_id="A001", timeout=180)

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
from src.incubator.utils import get_recent_observations

# Get recent observations
obs = get_recent_observations(agent_id="A001", limit=10)

for o in obs:
    print(f"[{o.timestamp}] Reward: {o.reward:.2f}")
    print(f"  {o.observation_text[:100]}...")
```

### Analyze Culture

```python
from src.incubator.culture import analyze_agent_culture

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

Configure in `src/incubator/tools.py`.

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
