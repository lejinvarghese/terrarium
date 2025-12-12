# Terrarium Incubator: SmolVLM Learning System

## Vision

A self-improving AI swarm where multiple SmolVLM2 agents with distinct personas explore the Terrarium ecosystem, observe actions/outcomes, and learn through continual training.

---

## Research Summary

### SmolVLM2 (Latest: Early 2025)
- **SmolVLM2-500M-Instruct**: Best balance of capability and efficiency
- Architecture: SigLIP encoder + SmolLM2 1.7B backbone
- Runs on <1GB GPU RAM, supports images/video + text
- Apache 2.0, native `transformers` support

**Sources:** [SmolVLM Blog](https://huggingface.co/blog/smolvlm) | [SmolVLM2 Release](https://huggingface.co/blog/smolvlm2) | [Model Card](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct)

### Smolagents (Released: Late Dec 2024)
- Minimalist framework (~1K LOC)
- Code agents write actions as executable code
- Sandboxed execution, model-agnostic, 30% more efficient
- Hub integration, multimodal support

**Sources:** [smolagents.org](https://smolagents.org/) | [GitHub](https://github.com/huggingface/smolagents) | [Intro Blog](https://huggingface.co/blog/smolagents)

### Inference Framework: **Transformers**
- Direct SmolVLM2 support via `AutoProcessor` + `AutoModelForVision2Seq`
- Simple integration with smolagents
- PyTorch backend for training compatibility

**Sources:** [VLMs 2025](https://huggingface.co/blog/vlms-2025) | [vLLM GitHub](https://github.com/vllm-project/vllm)

---

## Architecture

```
┌────────────────────────────────────────────┐
│  Multiple Agents (each with persona)      │
│                                            │
│  Agent: "observer" → Monitor services      │
│  Agent: "analyst" → Investigate patterns   │
│  Agent: "tester" → Try new interactions    │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  observations.db (SQLite)                  │
│  • agent_id, persona                       │
│  • observation + screenshots               │
│  • action + outcome + reward               │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  train.py (Per-Agent LoRA Adapters)       │
│  • Train separate adapters per agent       │
│  • Or shared adapter with agent context    │
└────────────────────────────────────────────┘
```

---

## File Structure

```
src/incubator/
├── PLAN.md
├── explore.py          # Exploration agent runner
├── train.py            # Training pipeline
├── config.py           # Configuration
├── models.py           # SQLite schema
├── tools.py            # Terrarium tools for smolagents
├── agents.py           # Agent persona definitions
├── observations.db
├── checkpoints/
│   ├── base/
│   └── agents/
│       ├── observer/
│       ├── analyst/
│       └── tester/
└── screenshots/
```

---

## Database Schema

```python
# models.py

class Agent:
    """Agent persona definitions"""
    agent_id: str          # Unique identifier (e.g., "observer-001")
    name: str              # Display name
    persona: str           # Description of agent's role
    system_prompt: str     # Persona-specific instructions
    created_at: datetime

class Observation:
    """Individual agent observations"""
    id: int
    agent_id: str          # Which agent made this observation
    episode_id: str        # Group related observations
    timestamp: datetime
    observation_text: str
    screenshot_path: str
    action_code: str       # Code executed by agent
    outcome: str
    reward: float          # -1 to 1
    model_checkpoint: str  # Which model version was used
```

---

## Agent Personas (Example)

```python
# agents.py

AGENTS = {
    "observer": {
        "name": "Observer",
        "persona": "Monitors Terrarium services and detects anomalies",
        "system_prompt": """You are a vigilant observer of the Terrarium ecosystem.
Your goal is to continuously monitor service health, log patterns, and memory usage.
Report anomalies and track service uptime."""
    },

    "analyst": {
        "name": "Analyst",
        "persona": "Investigates patterns in bot interactions and memory",
        "system_prompt": """You are an analytical agent studying Terrarium's behavior.
Your goal is to discover patterns in how bots interact with users, which memories
are frequently accessed, and how tasks are scheduled."""
    },

    "tester": {
        "name": "Tester",
        "persona": "Experiments with new tool combinations and workflows",
        "system_prompt": """You are an experimental agent testing Terrarium capabilities.
Your goal is to try novel combinations of tools, test edge cases, and discover
new ways to accomplish tasks."""
    }
}
```

---

## Implementation: `explore.py`

### Core Loop (Multi-Agent)

```python
def run_exploration(agent_id: str, objective: str, steps: int = 10):
    """Run exploration episode for specific agent"""

    # 1. Load agent config
    agent_config = AGENTS[agent_id]

    # 2. Initialize SmolVLM2
    model = AutoModelForVision2Seq.from_pretrained(MODEL_NAME)
    processor = AutoProcessor.from_pretrained(MODEL_NAME)

    # 3. Create CodeAgent with agent-specific system prompt
    agent = CodeAgent(
        model=model,
        system_prompt=agent_config["system_prompt"],
        tools=get_terrarium_tools()
    )

    # 4. Exploration loop
    episode_id = f"{agent_id}_{int(time.time())}"

    for step in range(steps):
        # a. Observe current state
        context = gather_context(agent_id)

        # b. Agent generates hypothesis and code
        result = agent.run(f"{objective}\n\nContext: {context}")

        # c. Store observation
        observation = Observation(
            agent_id=agent_id,
            episode_id=episode_id,
            observation_text=result["observation"],
            action_code=result["code"],
            outcome=result["outcome"],
            reward=calculate_reward(result)
        )
        db.add(observation)
```

### Simple Terrarium Tools

```python
# tools.py

@tool
def check_service_status() -> str:
    """Check which Terrarium services are running via tmux"""
    result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}: #{session_attached}"],
        capture_output=True, text=True
    )
    return result.stdout

@tool
def read_recent_logs(service: str, lines: int = 50) -> str:
    """Read last N lines from service logs"""
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", service, "-S", f"-{lines}"],
        capture_output=True, text=True
    )
    return result.stdout

@tool
def query_memory(query: str, limit: int = 5) -> List[str]:
    """Search Terrarium's Qdrant memory"""
    from src.engine.memory_config import memory
    results = memory.search(query, limit=limit)
    return [r["content"] for r in results]

@tool
def take_screenshot(url: str) -> str:
    """Capture screenshot of web interface"""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        path = f"screenshots/{int(time.time())}.png"
        page.screenshot(path=path)
        browser.close()
        return path

@tool
def get_scheduler_tasks() -> Dict:
    """Load current scheduled tasks"""
    with open("src/configs/schedule.json") as f:
        return json.load(f)

@tool
def get_bot_definitions() -> List[Dict]:
    """List available bot personas"""
    bots = []
    for file in glob.glob("src/bots/*.md"):
        with open(file) as f:
            content = f.read()
            bots.append({
                "name": Path(file).stem,
                "content": content[:500]  # First 500 chars
            })
    return bots
```

---

## Training Pipeline: `train.py`

**Multi-Agent Training Options:**

1. **Per-Agent Adapters**: Train separate LoRA adapters for each agent
2. **Shared Adapter**: Single adapter with agent_id in training context

**Process:**
```python
def train_agent(agent_id: str):
    """Train LoRA adapter for specific agent"""

    # 1. Load base model
    model = AutoModelForVision2Seq.from_pretrained(MODEL_NAME)

    # 2. Filter observations for this agent (reward > 0.5)
    observations = db.query(Observation).filter(
        Observation.agent_id == agent_id,
        Observation.reward > 0.5
    ).all()

    # 3. Convert to instruction format
    dataset = create_instruction_dataset(observations)

    # 4. Configure LoRA
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"]
    )

    # 5. Fine-tune
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=lora_config
    )
    trainer.train()

    # 6. Save adapter
    model.save_pretrained(f"checkpoints/agents/{agent_id}")
```

---

## Web Interface

**Route:** `/incubator` (Next.js)

**Sections:**
- **Agent Dashboard**: List all agents, their observation counts, latest activity
- **Observation Log**: Filterable by agent_id, episode_id, reward
- **Training Status**: Per-agent training metrics
- **Manual Controls**: Launch agent episodes, trigger training

---

## Dependencies

```
transformers>=4.46.0
smolagents>=1.0.0
peft>=0.13.0
trl>=0.11.0
torch>=2.5.0
pillow>=10.0.0
sqlalchemy>=2.0.0
playwright>=1.40.0
```

---

## Execution Plan

1. ✅ Research complete
2. **Implement multi-agent `explore.py` with simple tools** ← START HERE
3. Define 3 initial agent personas
4. Test exploration loop with agent_id logging
5. Implement `train.py` for per-agent LoRA fine-tuning
6. Build web monitoring interface with agent filtering

---

**Status:** 🟢 Ready for Implementation
**Last Updated:** 2025-12-11
