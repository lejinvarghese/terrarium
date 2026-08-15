# Setup Guide

Get Terrarium running in 5 minutes.

---

## Prerequisites

- Python 3.12+
- Node.js 18+
- Git

---

## Install

```bash
# Clone
git clone https://github.com/lejinvarghese/terrarium.git
cd terrarium

# Configure
cp .env.example .env
nano .env  # Add your API keys

# Install dependencies
pip3 install -r requirements.txt
cd web && npm install && cd ..
```

---

## Run

```bash
# Start everything
./dev up

# Access services
# - Dome: http://localhost:8080
# - Web: http://localhost:3000
# - Telegram: Message your bot

# Stop
./dev down
```

---

## Required API Keys

Add to `.env`:

```bash
TELEGRAM_TOKEN=...          # Create via @BotFather
TELEGRAM_CHAT_ID=...        # Get from @userinfobot
OPENWEATHER_API_KEY=...     # https://openweathermap.org
RUNWARE_API_KEY=...         # https://runware.ai
TAVILY_API_KEY=...          # https://tavily.com
```

**Optional keys:** Spoonacular (recipes), Spotify (music), OpenAI (embeddings), GitHub

---

## Configuration

### Scheduler Tasks

Edit `src/configs/schedule.json`:

```json
{
  "tasks": [
    {
      "name": "Morning Briefing",
      "command": "claude -p cassia 'Give morning briefing'",
      "schedule": "every day at 07:00"
    }
  ]
}
```

### Bot Personalities

Edit `.claude/agents/*.md` to customize bot behavior and capabilities.

---

## Optional Services

**Ollama (Local LLMs):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull qwen2.5:3b
```
Add to Dome: Settings → Connections → `http://localhost:11434`

**ComfyUI (Art Generation):**
```bash
# Set in .env
COMFYUI_PATH=/path/to/ComfyUI

# Run
cd $COMFYUI_PATH
source .venv/bin/activate
python main.py
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Service won't start | `./dev restart <service>` |
| Port in use | `lsof -i :8080` then `kill -9 <PID>` |
| Telegram not responding | Check `.env` token, verify `./dev status` |

---

## Next Steps

- **[USAGE.md](USAGE.md)** - How to use services and bots
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Multi-landscape design
- **[help/](help/)** - Deployment, networking, advanced config
