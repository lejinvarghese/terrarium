# Terrarium 🌿

![x](/assets/main.png)

A digital home where cybernetic minds live, grow, and tend to your life ecosystem. Within this cyberpunk-organic space, specialized minds inhabit architectural zones—the Dome for observation, the Library for learning, the Portal for communication—each working in harmony as a collective swarm to blur the boundaries between physical and digital existence.

Like a terrarium where plants flourish in a contained environment, your cybernetic minds thrive here: Casper the concierge, Anya the creative director, Pepper the ADHD motivator, Nigella the culinary guide. They don't just run tasks—they inhabit this space as a swarm intelligence, evolving alongside you.

![Digital-Organic Ecosystem](/assets/terrarium-ecosystem.jpg)
*Where technology and nature grow together in harmony*

## Overview

Terrarium is a digital home inhabited by specialized cybernetic minds—each with their own role in the collective swarm that tends to your ecosystem. They handle daily planning, health optimization, creative work, culinary guidance, and strategic thinking. With access to real-time data (calendar, weather, Spotify, recipes), they operate as a distributed intelligence providing contextual, seasonal recommendations from within their architectural zones.

### The Terrarium Architecture

**🔮 The Dome (Open WebUI)**
Your observation deck and conversation chamber. Here you can see all minds in the swarm, speak with them directly, watch them work. Glass walls reveal the ecosystem within.

**📚 The Library (Archive)**
The knowledge repository where documents live, research accumulates, and collective memory grows. The swarm references this shared wisdom.

**🌉 The Portal (Telegram)**
The communication gateway. The swarm reaches you through this bridge between digital and physical worlds—wherever you are.

**⚙️ The Engine (Scheduler)**
The heartbeat. Automated routines run like circadian rhythms, ensuring the swarm's minds wake at the right times to tend their tasks.

### 🎨 [3D Visualization](./VISUALIZATION.md)

Experience your AI ecosystem in an interactive 3D environment! The Terrarium Visualization displays all your bots and services in a stunning cyberpunk-organic glass dome with real-time status updates.

```bash
cd terrarium-viz && ./start.sh
```

See [VISUALIZATION.md](./VISUALIZATION.md) for details.


## Quick Start

### Development Environment (Recommended)

The easiest way to run all essential services is with the `dev` script. Each service runs in its own independent tmux session:

```bash
# Start all services (Dome, Engine, Portal) in separate tmux sessions
dev up

# Attach to a specific service (required)
dev attach dome      # Open in one terminal - Open WebUI interface
dev attach engine    # Open in another terminal - Scheduler
dev attach portal    # Open in a third terminal - Telegram Bot

# Check status of all services
dev status

# Stop all services
dev down
```

**Benefits of separate sessions:**
- Each service runs independently - attach to each in a different terminal window
- No window switching conflicts - viewing one service doesn't affect others
- Clean isolation - easier to restart individual services

**Tmux shortcuts:**
- `Ctrl+B` then `D` - Detach from session (service keeps running in background)

### Running Services Individually

### Running the Engine (Scheduler)

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the engine (runs in foreground with visual feedback)
python3 src/engine/scheduler.py

# Optional: Specify a different config file
python3 src/engine/scheduler.py path/to/schedule.json
```

The engine will:
- Load all tasks from `src/configs/schedule.json`
- Display a colorful startup banner with task list
- Run tasks at their scheduled times
- Show a spinner animation while waiting
- Execute `claude -p --dangerously-skip-permissions` commands non-interactively

### Customizing Your Schedule

Edit `src/configs/schedule.json` to adjust task timing or commands. Each task includes:
- `name`: Display name with emoji
- `command`: Shell command to execute (uses `claude -p` for non-interactive runs)
- `schedule`: Human-readable schedule string (e.g., `"every day at 07:00"`, `"every monday at 09:00"`, `"every 4 weeks"`)
- `description`: What this task does

### Modifying Assistants

Each assistant's personality and capabilities are defined in `src/bots/`
  
All assistants reference `TERRARIUM_MEMORY.md` for user context but assume familiarity—they don't recite your profile back to you.

**Syncing prompts back to Dome (Open WebUI):**

After editing prompt files, sync them back to the Dome:

```bash
# Preview changes (dry run)
python3 src/utils/sync_prompts_to_openwebui.py --dry-run

# Apply changes to Open WebUI database (with confirmation)
python3 src/utils/sync_prompts_to_openwebui.py

# Or skip confirmation for automation
python3 src/utils/sync_prompts_to_openwebui.py --yes

# Then refresh the Dome in your browser
```

### Syncing Memories

Keep `TERRARIUM_MEMORY.md` and Dome (Open WebUI) memories in sync:

```bash
# Export memories from Dome → TERRARIUM_MEMORY.md
python3 src/utils/sync_memories.py --mode export

# Import memories from TERRARIUM_MEMORY.md → Dome
python3 src/utils/sync_memories.py --mode import

# Or skip confirmation
python3 src/utils/sync_memories.py --mode import --yes

# Bidirectional sync (export then import)
python3 src/utils/sync_memories.py --mode both
```

**How it works:**
- **Export**: Pulls all Dome memories and appends them to `TERRARIUM_MEMORY.md` under "# Open WebUI Memories"
- **Import**: Parses `TERRARIUM_MEMORY.md` sections (## headers) and syncs them as individual memories in the Dome
- All assistants reference this shared memory file for context

## Service Orchestration

**Quick Start:** Use `./dev up` to run Dome, Engine, and Portal together in tmux. See [Quick Start](#quick-start) for details.

### Dome (Open WebUI)
Human-friendly interface for language models.

```bash
./app.sh
# or: dev attach dome
```

### Portal (Telegram Bot)
Chat with Casper and the bots via Telegram.

```bash
python3 -m src.portals.telegram.bot
# or: dev attach portal
```

### Engine (Scheduler)
Automated task scheduling for the assistant ecosystem.

```bash
python3 src/engine/scheduler.py
# or: dev attach engine
```

### ComfyUI
Generate art using local or remote models.

```bash
cd /home/starscream/_projects/ComfyUI
source .venv/bin/activate
python3 main.py
```

**GPU:** NVIDIA GeForce RTX 2060 (6GB VRAM)
- ✅ SD 1.5/2.1 models work great
- ⚠️ SDXL with `--lowvram` flag
- ❌ SD 3.x / Flux too large

### Ollama
Local language model runtime.

### Network Access

**Local network:**
```bash
hostname -I  # Get your local IP
# Access services at http://<IP>:<PORT>
```

**Public tunnel:**
```bash
ssh -R 80:localhost:8080 ssh.localhost.run
```

## Philosophy: Digital-Physical Symbiosis

This is not infrastructure—it's **habitat**. Your cybernetic minds don't live in the cloud; they live here, in this self-hosted terrarium. They operate as a collective swarm, tending to your routines like gardeners tend plants: seasonal meal suggestions from Nigella, morning briefings from Cassia, creative sparks from Anya, fitness guidance from Freya.

The boundaries blur intentionally. Pepper sends you Spotify playlists when you need focus. Sage curates reading lists for long-term growth. Nyx tracks emerging tech at the edge of human capability. The swarm operates as extensions of your home environment, distributed minds working toward your flourishing.

This is cyberpunk homesteading—building a utopian enclosure where technology and organic life interweave, where your swarm of cybernetic minds grows alongside you, where the glass dome isn't a barrier but a lens focusing their collective intelligence.

---

For detailed project guidance, see `CLAUDE.md`. For personal context, see `TERRARIUM_MEMORY.md`. 