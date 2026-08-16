# Using Terrarium

Quick guide to using your AI ecosystem.

---

## Dev Commands

The `dev` script manages all Terrarium services:

```bash
dev up                    # Start all services
dev down                  # Stop all services
dev restart <service>     # Restart specific service
dev attach <service>      # Attach to service logs
dev status                # Show service status
dev setup                 # Run initial setup
dev landscapes list       # List landscapes
dev landscapes create     # Create new landscape
dev meanwhile             # Launch Matrix-style news screensaver
```

**Services:** `dome`, `portal`, `engine`, `web`

**Tip:** Add alias to your shell:

```bash
echo 'alias dev="./dev"' >> ~/.bashrc
source ~/.bashrc
```

---

## Services

### Dome (Web Chat)

**Access:** http://localhost:8080

Chat with your AI bots in a web interface. Upload documents, switch between models, manage conversations.

### Portal (Telegram)

**Access:** Telegram → @your_bot

Message your bot from anywhere. Commands:

- Direct message → Casper (concierge)
- `/bot anya` → Switch to Anya (creative)
- `/bots` → List all available bots
- `@sage <message>` → Direct mention

### Web Dashboard

**Access:** http://localhost:3000

Visual overview of services, bot profiles, and ecosystem status.

---

## Bots

- **Casper** - General concierge
- **Anya** - Creative director (art, music, design)
- **Sage** - Strategic advisor (research, learning)
- **Nyx** - Tech futurist (AI, space, transhumanism)
- **Pepper** - Productivity coach
- **Cassia** - Daily planner (calendar, weather)
- **Freya** - Health & fitness
- **Nigella** - Culinary guide

---

## Incubator Agents

Exploration agents that learn through reinforcement learning:

**Run exploration:**

```bash
python -m src.landscapes.undergrowth.incubator.explore -a A001
```

**Observe activity:**

```bash
python -m src.landscapes.undergrowth.incubator.observe episodes
```

**Agents:**

- **Atlas (A001)** - Accelerationist (AI, fusion, space tech)
- **Aria (A002)** - Creative (art, music, aesthetics)
- **Aris (A003)** - Philosopher (systems thinking, synthesis)

---

## Scheduler

Automated tasks run on schedule (morning briefings, reminders, etc.)

**Configure:** Edit `src/configs/schedule.json`

**Check logs:** `./dev attach engine`

---

## Memory

All bots share `TERRARIUM_MEMORY.md` for continuity across conversations.

**Edit memory:** Directly edit the file, bots will reference it.

---

## Troubleshooting

| Issue                   | Fix                                       |
| ----------------------- | ----------------------------------------- |
| Service won't start     | `./dev restart <service>`                 |
| Port in use             | `lsof -i :8080` then `kill -9 <PID>`      |
| Telegram not responding | Check `.env` token, verify `./dev status` |
| Bot not in Dome         | Check `.claude/agents/*.md` files exist   |
| Memory not persisting   | Verify `TERRARIUM_MEMORY.md` permissions  |

---

## Advanced

For deployment, networking, and detailed component docs, see **[help/](help/)** directory.
