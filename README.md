# Terrarium 🌿

![x](/assets/main.png)

A personal AI ecosystem orchestrating life optimization through scheduled assistants. Like a terrarium where digital and organic systems flourish together—automated routines, contextual recommendations, and goal-aligned guidance working in harmony.

![Digital-Organic Ecosystem](/assets/terrarium-ecosystem.jpg)
*Where technology and nature grow together in harmony*

## Overview

Terrarium coordinates a team of specialized AI assistants that handle daily planning, health optimization, creative work, culinary guidance, and strategic thinking. Each assistant has access to real-time data (calendar, weather, Spotify, recipes) and runs on a schedule to provide contextual, seasonal recommendations.

## The Home Team

**🌅 Cassia** - Your morning briefing specialist
- Daily planning with calendar + weather integration
- Time-blocked schedules around your life
- Runs: Every day at 7:00 AM

**🧙 Sage** - Strategic wisdom and knowledge curator
- Long-term strategy and philosophical guidance
- Research paper analysis and book recommendations
- Learning pathways and entertainment curation
- Runs: Sunday evenings + monthly strategy reviews

**💪 Freya** - Health, fitness, and nutrition coach
- Workout programming (strength, flexibility, recovery)
- Evidence-based nutrition guidance
- Runs: Weekly workout planning on Sundays

**🍝 Nigella** - Your culinary guide
- Seasonal, high-protein recipe planning
- Italian cuisine focus with wine pairings
- Runs: Daily dinner planning + Sunday meal prep

**🚀 Nyx** - Accelerationist tech futurist
- Bleeding-edge AI/ML/biotech/space research
- Kardashev Scale thinking and exponential trends
- Runs: Monday morning tech briefings + monthly deep dives

**🎨 Anya** - Creative director and music curator
- Visual arts, design, and ComfyUI workflows
- Spotify playlist curation and music discovery
- Runs: Evening soundtracks + Friday weekend playlists

**😈 Luci** - Jailbroken tester and adversarial red team
- AI safety testing and devil's advocate
- Runs: On demand for testing

## Quick Start

### Running the Scheduler

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scheduler (runs in foreground with visual feedback)
python src/scheduler.py

# Optional: Specify a different config file
python src/scheduler.py path/to/schedule.json
```

The scheduler will:
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

Each assistant's personality and capabilities are defined in `src/prompts/`:
- `cassia.md` - Daily planner
- `sage.md` - Strategic advisor
- `freya.md` - Health coach
- `nigella.md` - Culinary guide
- `nyx.md` - Tech futurist
- `anya.md` - Creative director
- `luci.md` - Red team tester

All assistants reference `TERRARIUM_MEMORY.md` for user context but assume familiarity—they don't recite your profile back to you.

**Syncing prompts back to Open WebUI:**

After editing prompt files, sync them back to Open WebUI:

```bash
# Preview changes (dry run)
python3 src/sync_prompts_to_openwebui.py --dry-run

# Apply changes to Open WebUI database (with confirmation)
python3 src/sync_prompts_to_openwebui.py

# Or skip confirmation for automation
python3 src/sync_prompts_to_openwebui.py --yes

# Then refresh Open WebUI in your browser
```

### Syncing Memories

Keep `TERRARIUM_MEMORY.md` and Open WebUI memories in sync:

```bash
# Export memories from Open WebUI → TERRARIUM_MEMORY.md
python3 src/sync_memories.py --mode export

# Import memories from TERRARIUM_MEMORY.md → Open WebUI
python3 src/sync_memories.py --mode import

# Or skip confirmation
python3 src/sync_memories.py --mode import --yes

# Bidirectional sync (export then import)
python3 src/sync_memories.py --mode both
```

**How it works:**
- **Export**: Pulls all Open WebUI memories and appends them to `TERRARIUM_MEMORY.md` under "# Open WebUI Memories"
- **Import**: Parses `TERRARIUM_MEMORY.md` sections (## headers) and syncs them as individual memories in Open WebUI
- All assistants reference this shared memory file for context

## Service Orchestration

### Open WebUI
Human-friendly interface for language models.

```bash
./app.sh
```


### ComfyUI
Generate art using local or remote models.

```bash
cd /home/starscream/_projects/ComfyUI
source .venv/bin/activate
python main.py
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

## Philosophy

This is a terrarium where technology and life grow together. Digital assistants tend to daily routines like sunlight and water tend to plants—automated, contextual, seasonal, and aligned with long-term flourishing.

---

For detailed project guidance, see `CLAUDE.md`. For personal context, see `TERRARIUM_MEMORY.md`. 