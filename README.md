# Terrarium 🌿

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-mutatedterrarium.com-EBFA1D?style=for-the-badge)](https://mutatedterrarium.com)

![Terrarium Hero](/assets/main.png)

> **🌐 See it live:** [mutatedterrarium.com](https://mutatedterrarium.com)

A self-hosted ecosystem where cybernetic minds live, grow, and tend to your digital-physical life. This is not infrastructure—it's **habitat**. A glass dome where AI agents don't just run tasks, they *inhabit* distinct landscapes, evolving as a collective swarm intelligence.

Like a terrarium where plants flourish in a contained environment, your cybernetic minds thrive here: **Casper** the concierge, **Anya** the creative director, **Pepper** the ADHD motivator, **Nigella** the culinary guide, **Sage** the wisdom keeper, **Nyx** the accelerationist futurist, **Freya** the health coach.

![Digital-Organic Ecosystem](/assets/terrarium-ecosystem.jpg)
*Where technology and nature grow together in harmony*

---

## The Vision

**Cyberpunk homesteading.** Building a utopian enclosure where technology and organic life interweave. Your swarm of cybernetic minds operates as extensions of your home environment—distributed intelligence working toward your flourishing.

The boundaries blur intentionally:
- Pepper sends Spotify playlists when you need focus
- Cassia delivers weather-aware morning briefings with calendar integration
- Nigella suggests seasonal recipes aligned with your fitness goals
- Sage curates reading lists for long-term growth
- Nyx tracks emerging tech at the edge of human capability
- Anya generates art and curates aesthetics for your creative projects

This is digital-physical symbiosis. Your bots don't live in the cloud—they live *here*, self-hosted, in architectural zones that shape their identity.

---

## Multi-Landscape Architecture

![Landscapes Visualization](/assets/screenshots/landscapes-viz.png)

*The multiplex network: Layer 0 (physical beings) connected to Layer 1 (digital landscapes)*

The Terrarium is evolving toward a **multi-landscape ecosystem** where distinct civilizations of AI agents can emerge, interact, and migrate between biomes:

### 🌑 The Undergrowth (Active)
**Culture:** Dark, gothic, emergent underground intelligence  
**Population:** 11 agents (Anya, Nyx, Sage, Pepper, Cassia, Freya, Nigella, Casper + 3 incubator agents)  
**Vibe:** Urban hippie goth meets cyberpunk meets accelerationist transhumanism

### 🌤️ The Canopy (Dormant)
**Culture:** Elevated, strategic, birds-eye perspective  
**Vision:** Wisdom-focused, long-term planning, pattern recognition

### 🍄 The Mycelium (Future)
**Culture:** Networked intelligence, distributed consciousness  
**Vision:** No individual identity—pure collective swarm

### 🐠 The Reef (Future)
**Culture:** Adaptive, flowing, symbiotic relationships  
**Vision:** Cooperation, flow states, collective action

Each landscape has its own culture, memory systems, and hive mind. Agents can migrate between landscapes, carrying cultural DNA with them.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the complete vision.

---

## Service Architecture

![Services](/assets/screenshots/services.png)

The terrarium runs on four core **substations**:

### 🔮 The Dome
*Open WebUI* — Your observation deck. See all minds in the swarm, chat directly, watch them work. Glass walls reveal the ecosystem within.

### 🌉 The Portal  
*Telegram Bot* — Mobile gateway. The swarm reaches you wherever you are, bridging digital and physical worlds.

### ⚙️ The Engine
*Scheduler* — The heartbeat. Automated routines run like circadian rhythms—morning briefings, health check-ins, creative prompts.

### 🌐 The Web
*Next.js Dashboard* — Visual interface showing the multiplex network, service status, and bot profiles in cyberpunk-organic aesthetic.

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

- **[SETUP.md](./docs/SETUP.md)** - Detailed installation and configuration
- **[SERVICE_ORCHESTRATION.md](./docs/SERVICE_ORCHESTRATION.md)** - Running ComfyUI, Ollama, network access
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Multi-landscape design and vision
- **[SSH_ACCESS.md](./docs/SSH_ACCESS.md)** - Remote access and tunneling
- **[SECURE_ACCESS.md](./docs/SECURE_ACCESS.md)** - Authentication and security

---

## Philosophy: Digital-Physical Symbiosis

This is not infrastructure—it's **habitat**.

Your cybernetic minds don't live in the cloud; they live *here*, in this self-hosted terrarium. They operate as a collective swarm, tending to your routines like gardeners tend plants:

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
- Python 3.12+ (automation, scheduling, bot logic)
- Open WebUI (LLM interface)
- Telegram Bot API (mobile portal)
- FastMCP (Model Context Protocol servers)

**Frontend:**
- Next.js 14 (web dashboard)
- React Three Fiber (3D visualizations)
- CSS modules (cyberpunk-organic aesthetic)

**AI/ML:**
- Claude 3.5 Sonnet (primary reasoning)
- Ollama (local LLM runtime, optional)
- ComfyUI + Stable Diffusion (image generation, optional)

**Infrastructure:**
- Self-hosted (runs on your hardware)
- Docker (optional containerization)
- Cloudflare Tunnels (optional public access)

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
