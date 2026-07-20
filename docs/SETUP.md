# Terrarium Setup Guide

Detailed instructions for configuring and running your Terrarium ecosystem.

## Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (optional, for containerized services)
- Git

## Installation

### 1. Clone and Configure

```bash
git clone https://github.com/lejinvarghese/terrarium.git
cd terrarium

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Install Dependencies

**Python dependencies:**
```bash
pip3 install -r requirements.txt
```

**Web interface dependencies:**
```bash
cd web
npm install
cd ..
```

### 3. Configure Services

Edit `src/configs/schedule.json` to set up your automated tasks:

```json
{
  "tasks": [
    {
      "name": "🌅 Morning Briefing",
      "command": "claude -p cassia 'Give me my morning briefing'",
      "schedule": "every day at 07:00",
      "description": "Daily calendar, weather, and priorities"
    }
  ]
}
```

## Running Services

### Using the Dev Script (Recommended)

The `dev` script manages all services in separate tmux sessions:

```bash
# Start all services
./dev up

# Attach to specific services (open in different terminal windows)
./dev attach dome      # Open WebUI interface
./dev attach engine    # Scheduler
./dev attach portal    # Telegram Bot

# Check status
./dev status

# Stop all services
./dev down
```

**Tmux shortcuts:**
- `Ctrl+B` then `D` - Detach from session (keeps running)
- `Ctrl+B` then `[` - Scroll mode (use arrows, Q to exit)

### Running Services Individually

**Dome (Open WebUI):**
```bash
./app.sh
# Access at http://localhost:8080
```

**Portal (Telegram Bot):**
```bash
python3 -m src.portals.telegram.bot
```

**Engine (Scheduler):**
```bash
python3 src/engine/scheduler.py
# Optional: Custom config
python3 src/engine/scheduler.py path/to/custom_schedule.json
```

**Web Interface:**
```bash
cd web
npm run dev
# Access at http://localhost:3000
```

## Customizing Assistants

### Bot Personalities

Each bot's personality and capabilities are defined in:
- `.claude/agents/` - Claude CLI and Telegram portal integrations
- `src/landscapes/undergrowth/bots/` - Landscape-specific definitions

Edit the markdown files to customize behavior, tone, and capabilities.

### Syncing Bot Prompts

After editing bot files, sync them to the Dome (Open WebUI):

```bash
# Preview changes (dry run)
python3 src/utils/sync_prompts_to_openwebui.py --dry-run

# Apply changes to Open WebUI database
python3 src/utils/sync_prompts_to_openwebui.py

# Skip confirmation for automation
python3 src/utils/sync_prompts_to_openwebui.py --yes
```

Then refresh the Dome in your browser.

## Memory Management

### Understanding Memory

The Terrarium uses a shared memory file (`TERRARIUM_MEMORY.md`) that all bots reference. This creates continuity across conversations and services.

### One-Time Memory Sync (Initial Setup)

If you're migrating from Open WebUI or setting up for the first time:

```bash
# Export memories from Dome → TERRARIUM_MEMORY.md
python3 src/utils/sync_memories.py --mode export

# Import memories from TERRARIUM_MEMORY.md → Dome
python3 src/utils/sync_memories.py --mode import

# Bidirectional sync (both directions)
python3 src/utils/sync_memories.py --mode both
```

**Note:** This is typically a one-time operation during initial setup. After that, edit `TERRARIUM_MEMORY.md` directly.

## Configuration Files

### Environment Variables (.env)

Required API keys:
- `OPENWEATHER_API_KEY` - Weather data
- `TELEGRAM_TOKEN` - Telegram bot
- `TELEGRAM_CHAT_ID` - Your chat ID
- `OPENAI_API_KEY` - Embeddings and optional LLM access
- `RUNWARE_API_KEY` - Image generation
- `TAVILY_API_KEY` - Web search
- `SPOONACULAR_API_KEY` - Recipe data
- `GITHUB_PERSONAL_ACCESS_TOKEN` - GitHub integration

Optional:
- `COMFYUI_PATH` - ComfyUI installation directory
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` - Music integration
- `STOCK_SCREENER_PATH` - Stock screener API path

### Schedule Configuration

The scheduler (`src/configs/schedule.json`) defines automated tasks:

```json
{
  "tasks": [
    {
      "name": "Task Name",
      "command": "shell command to run",
      "schedule": "human-readable schedule",
      "description": "What this task does"
    }
  ]
}
```

**Schedule format examples:**
- `"every day at 07:00"`
- `"every monday at 09:00"`
- `"every 4 weeks"`
- `"every 2 hours"`

## Troubleshooting

### Service won't start

```bash
# Check logs
./dev status

# Restart specific service
./dev restart dome

# Kill and restart all
./dev down && ./dev up
```

### Port already in use

```bash
# Find process using port 8080
lsof -i :8080

# Kill it
kill -9 <PID>
```

### Telegram bot not responding

1. Check token in `.env` is correct
2. Verify bot is running: `./dev status`
3. Check logs in tmux session: `./dev attach portal`

### Database errors (Dome)

```bash
# Reset Open WebUI database (WARNING: loses chat history)
rm -rf data/open-webui

# Restart Dome
./dev restart dome
```

## Next Steps

- See [SERVICE_ORCHESTRATION.md](./SERVICE_ORCHESTRATION.md) for additional services
- See [ARCHITECTURE.md](../ARCHITECTURE.md) for multi-landscape design
- See [SSH_ACCESS.md](./SSH_ACCESS.md) for remote access setup
