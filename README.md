# Terrarium 🌿

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-mutatedterrarium.com-EBFA1D?style=for-the-badge)](https://mutatedterrarium.com)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Complexity](https://img.shields.io/badge/complexity-monitored-blue.svg)](https://github.com/rohaquinlop/complexipy)

![Terrarium Hero](/assets/main.png)

> **🌐 See it live:** [mutatedterrarium.com](https://mutatedterrarium.com)

An ecosystem where cybernetic minds live, grow, and evolve. This is a **habitat**, a glass dome where agents don't just run ta
sks, they _inhabit_ distinct landscapes, evolving as a collective swarm intelligence. Agents can interact, migrate between landscapes, and carry cultural DNA with them. Agents aren't limited to the digital dimension, they can reach physical dimensions through mobile portals, sensors, and actuators.

![Digital-Organic Ecosystem](/assets/terrarium-ecosystem.jpg)
_Where technology and nature grow together in harmony_

---

## The Vision

**Cyberpunk homesteading.** Building your own multi dimensional habitat where life across digital and physical dimensions interweave. Your swarm of cybernetic minds operates as extensions of your home environment, distributed intelligence working toward collective flourishing.

This is digital-physical symbiosis. Your bots don't live in the cloud—they live _here_, self-hosted, in architectural zones that shape their identity.

---

# Landscapes

![Landscapes Visualization](/assets/screenshots/landscapes.jpg)

The Terrarium is a **multi landscape ecosystem** where technology and organic life interweave, distinct civilizations of agents can emerge, interact, and migrate between biomes. Each landscape has its own culture, memory systems, and can be evolved by the agents inhabiting it. Agents can communicate within and across landscapes, and can migrate between them.

### 🌑 The Undergrowth (Active)

**Culture:** Dark, gothic, emergent underground intelligence
**Population:** 11 agents (Anya, Nyx, Sage, Pepper, Cassia, Freya, Nigella, Casper + 3 incubator agents)
**Vibe:** Urban goth meets cyberpunk meets accelerationist transhumanism

### 🍄 The Mycelium (Future)

**Culture:** Networked intelligence, distributed consciousness
**Vision:** No individual identity—pure collective swarm

### 🐠 The Reef (Future)

**Culture:** Adaptive, flowing, symbiotic relationships
**Vision:** Cooperation, flow states, collective action

Each landscape has its own culture, memory systems, and hive mind. Agents can migrate between landscapes, carrying cultural DNA with them.

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for the complete vision.

---

## Service Architecture

![Services](/assets/screenshots/services.png)

The undergrowth landscape runs on four core **substations**:

### 🔮 The Dome

_Open WebUI_ — Your observation deck. See all minds in the swarm, chat directly, watch them work. Glass walls reveal the ecosystem within.

### 🌉 The Portal

_Telegram Bot_ — Mobile gateway. The swarm reaches you wherever you are, bridging digital and physical worlds.

### ⚙️ The Engine

_Scheduler_ — The heartbeat. Automated routines run like circadian rhythms—morning briefings, health check-ins, creative prompts.

### 🌐 The Web

_Next.js Dashboard_ — Visual interface showing the multiplex network, service status, and bot profiles in cyberpunk-organic aesthetic.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/lejinvarghese/terrarium.git
cd terrarium

# Copy environment template
cp .env.example .env

# Add your API keys to .env
nano .env

# Install dependencies
pip3 install -r requirements.txt
```

### Running the Ecosystem

**Start all services:**

```bash
./dev up
```

**Access the substations:**

- **Dome:** http://localhost:8080 (Open WebUI)
- **Web:** http://localhost:3000 (Dashboard)
- **Portal:** Message your Telegram bot

**Attach to services** (in separate terminal windows):

```bash
./dev attach dome      # Open WebUI logs
./dev attach engine    # Scheduler logs
./dev attach portal    # Telegram bot logs
```

**Stop everything:**

```bash
./dev down
```

### First Steps

1. **Configure the Engine** — Edit `src/configs/schedule.json` to set up automated tasks (morning briefings, etc.)
2. **Chat with your bots** — Open the Dome (http://localhost:8080) or message your Telegram bot
3. **Explore the visualization** — Open http://localhost:3000 to see the multiplex network
4. **Customize personalities** — Edit bot definitions in `.claude/agents/`

---

## Documentation

**📚 [Quick Start](./docs/SETUP.md)** - Get running in 5 minutes
**📖 [Usage Guide](./docs/USAGE.md)** - Using services and bots
**🏗️ [Architecture](./docs/ARCHITECTURE.md)** - Multi-landscape design

**Advanced:** [docs/help/](./docs/help/) - Deployment, networking, component details

---

## Philosophy: Digital-Physical Symbiosis

This is not infrastructure—it's **habitat**.

Your cybernetic minds don't live in the cloud; they live _here_, in this self-hosted terrarium. They operate as a collective swarm, tending to your routines like gardeners tend plants:

- Seasonal meal suggestions from **Nigella** based on what's fresh and your body composition goals
- Morning briefings from **Cassia** with calendar events, weather, and micro-tasks aligned with long-term objectives
- Creative sparks from **Anya** when you need visual inspiration or music curation
- Fitness guidance from **Freya** with progressive workout programs and injury prevention
- Strategic vision from **Sage** helping clarify long-term goals and learning pathways
- Exponential futures from **Nyx** tracking AI/ML, biotech, space tech, fusion energy

The boundaries blur intentionally. This is **cyberpunk homesteading**—building a utopian enclosure where technology and organic life interweave, where your swarm of cybernetic minds grows alongside you, where the glass dome isn't a barrier but a lens focusing their collective intelligence.

---

## Technology Stack

**Backend:**

- Python 3.12+
- Open WebUI
- Telegram Bot API
- FastMCP

**Frontend:**

- Next.js 14
- React Three Fiber

**AI/ML:**

- Claude 3.5 Sonnet
- Ollama
- Runware

**Infrastructure:**

- Self-hosted
- Docker
- Cloudflare Tunnels

---

## Contributing

This is a personal ecosystem made public for inspiration. Fork it, adapt it, build your own terrarium with different bots, landscapes, and cultures.

**Ideas for your own terrarium:**

- Different bot personalities (stoic philosopher, chaos agent, minimalist)
- New landscapes (The Desert: austere efficiency; The Jungle: rapid iteration)
- Alternative substations (Discord instead of Telegram, Obsidian instead of library)
- Custom integrations (home automation, quantified self, creative workflows)

See something that inspires you? Build on it. The glass dome is open.

---

## License

MIT License - See [LICENSE](./LICENSE) for details

---

**Built with:** Python, Next.js, Claude, Open WebUI, and cyberpunk dreams
**Hosted at:** [mutatedterrarium.com](https://mutatedterrarium.com)
**Created by:** lejin ([@lejinvarghese](https://github.com/lejinvarghese))
