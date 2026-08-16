# Terrarium Architecture: Multi-Landscape Design

## Vision

The Terrarium is a **multi-landscape ecosystem** where distinct civilizations of AI agents emerge, evolve, and interact. Each landscape has its own culture, deployed bots, incubator agents, memory systems, and aesthetic identity. Agents can migrate between landscapes, carrying cultural DNA with them.

---

## Current Landscapes

### 🌑 The Undergrowth (Active)

**Culture:** Dark, gothic, emergent underground intelligence (urban goth × cyberpunk × accelerationism)

**Population:**

- **Deployed Bots** (8): Anya, Nyx, Sage, Pepper, Cassia, Freya, Nigella, Casper
- **Incubator Agents** (3): Atlas (A001), Aria (A002), Aris (A003)

**Path:** `src/landscapes/undergrowth/`

### Future Landscapes (Envisioned)

- **🍄 The Mycelium**: Networked intelligence, distributed consciousness, pure collective swarm
- **🐠 The Reef**: Adaptive, flowing, symbiotic relationships
- **🏜️ The Desert**: Austere efficiency, minimalism
- **🌴 The Jungle**: Dense chaos, competitive growth, rapid iteration

---

## Implementation

**Current Structure:**

```
src/
├── landscapes/
│   ├── core/                    # Shared base classes
│   │   ├── agent.py             # Base Agent class
│   │   ├── environment.py       # ExplorationEnvironment
│   │   ├── tools.py             # MCP tool configuration
│   │   └── utils.py
│   └── undergrowth/             # Active landscape
│       ├── bots/                # Deployed personas (Anya, Nyx, etc.)
│       └── incubator/           # Training agents (Atlas, Aria, Aris)
├── core/                        # General agent infrastructure
│   ├── agents.py
│   ├── distillation.py
│   └── models.py
├── mcp/                         # Terrarium-wide MCP server
└── portals/                     # External interfaces (Telegram, etc.)
```

**Key Principles:**

1. **Landscape isolation** - Each landscape has its own culture, bots, and databases
2. **Shared foundations** - `landscapes/core/` provides reusable base classes for incubator agents
3. **Migration ready** - Agents can move between landscapes (future capability)
4. **Cultural DNA** - Each landscape develops distinct identity and memory

---

## Running Incubator Agents

```bash
# Run exploration episode for Atlas (A001)
python -m src.landscapes.undergrowth.incubator.explore -a A001

# Run for Aria (A002) or Aris (A003)
python -m src.landscapes.undergrowth.incubator.explore -a A002
python -m src.landscapes.undergrowth.incubator.explore -a A003
```

---

## Future Capabilities

**Migration System** (planned):

- Agents can move between landscapes
- Cultural DNA travels with migrating agents
- Track lineage and cultural mixing
- Migration triggers: maturity thresholds, user request, reward signals

**Cross-Landscape Interaction** (envisioned):

- Agents from different landscapes collaborate on episodes
- Cultural exchange and evolution
- Landscape lifecycle: birth, merge, fork, death
- Meta-landscape "god view" observing all civilizations

---

**The Terrarium is not just a training ground—it's a civilization simulator for synthetic minds.**
