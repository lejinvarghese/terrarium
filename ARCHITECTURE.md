# Terrarium Architecture: Multi-Landscape Design

## Vision

The Terrarium is a **multi-landscape metaverse** where distinct ecosystems (bots + incubators + culture) can replicate, diverge, evolve, and interact. Each landscape represents a unique civilization with its own:

- **Bot personas** - Deployed AI agents with specialized roles
- **Incubator** - Training ground for synthetic agents
- **Culture/Hive mind** - Shared priorities, aesthetic, and values
- **Memory systems** - Collective knowledge and observations
- **Migration paths** - Agents can move between landscapes, bringing cultural DNA

## Landscape #1: The Undergrowth

**Cultural Identity**: Dark, gothic, emergent, underground intelligence. Urban hippie goth meets cyberpunk meets accelerationist transhumanism.

**Current Inhabitants:**
- **Bots**: Anya (creative), Nyx (accelerationist), Sage (wisdom), Pepper (ADHD support), Cassia (planning), Freya (health), Nigella (culinary), Casper (concierge)
- **Incubator**: A001 (curious explorer), A002 (inquisitive learner), A003 (gentle soul)

**Priorities**: Transformation, emergence, aesthetic expression, exponential thinking, wisdom accumulation

---

## Future Landscapes (Examples)

### The Canopy
**Culture**: Elevated, strategic, birds-eye perspective, wisdom-focused
**Priorities**: Long-term planning, pattern recognition, synthesis, elevated consciousness

### The Mycelium
**Culture**: Pure networked intelligence, distributed consciousness, no individual identity
**Priorities**: Collective intelligence, information flow, emergent complexity

### The Reef
**Culture**: Adaptive, flowing, collective swarm behaviors, symbiotic relationships
**Priorities**: Cooperation, adaptation, flow states, collective action

### The Desert
**Culture**: Austere, minimal, pure efficiency, survival optimization
**Priorities**: Resource efficiency, clarity, minimalism, resilience

### The Jungle
**Culture**: Dense, chaotic, competitive, raw growth, diversity
**Priorities**: Innovation, competition, rapid iteration, survival of fittest ideas

---

## Architectural Options

### Option 1: Landscape-First (Top-Level Containers)

**Structure:**
```
src/
├── landscapes/
│   ├── undergrowth/
│   │   ├── bots/           # Anya, Nyx, Sage, etc.
│   │   │   ├── anya.md
│   │   │   ├── nyx.md
│   │   │   └── ...
│   │   ├── incubator/      # A001-A003
│   │   │   ├── agents.py
│   │   │   ├── config.py
│   │   │   ├── explore.py
│   │   │   └── ...
│   │   ├── culture.py      # Hive mind analysis
│   │   └── memory.db       # Landscape-specific memories
│   ├── canopy/
│   │   ├── bots/
│   │   ├── incubator/
│   │   └── culture.py
│   └── shared/             # Shared infrastructure
│       ├── environment.py  # Base ExplorationEnvironment
│       ├── models.py       # Base Agent, Observation models
│       └── tools.py        # MCP tool configuration
└── mcp/                    # Terrarium-wide MCP server
```

**Pros:**
- ✅ Each landscape is completely self-contained
- ✅ Easy to understand landscape boundaries
- ✅ Clear isolation for different cultures
- ✅ Simple to add/remove entire landscapes

**Cons:**
- ❌ Potential code duplication across landscapes
- ❌ Harder to share improvements across all landscapes
- ❌ Migration logic needs to cross landscape boundaries

---

### Option 2: Component-First (Bots/Incubators at Top Level)

**Structure:**
```
src/
├── bots/
│   ├── undergrowth/
│   │   ├── anya.md
│   │   ├── nyx.md
│   │   └── ...
│   ├── canopy/
│   │   └── ...
│   └── shared/
│       └── base_bot.py
├── incubator/
│   ├── undergrowth/
│   │   ├── config.py
│   │   ├── agents.py
│   │   └── ...
│   ├── canopy/
│   │   └── ...
│   └── shared/
│       ├── environment.py
│       ├── models.py
│       └── tools.py
└── mcp/
```

**Pros:**
- ✅ Easy to compare similar components across landscapes
- ✅ Natural grouping by function (all bots together)
- ✅ Shared code at component level

**Cons:**
- ❌ Landscape identity is fragmented
- ❌ Harder to see complete landscape picture
- ❌ Cultural boundaries less clear

---

### Option 3: Hybrid Core + Landscapes (RECOMMENDED)

**Structure:**
```
src/
├── core/
│   ├── environment.py      # Base ExplorationEnvironment
│   ├── models.py           # Base Agent, Observation models
│   ├── tools.py            # Shared MCP tools
│   ├── utils.py            # Shared utilities
│   └── migrations.py       # Cross-landscape migration logic
├── landscapes/
│   ├── __init__.py         # Landscape registry
│   ├── undergrowth/
│   │   ├── __init__.py
│   │   ├── bots/
│   │   │   ├── anya.md
│   │   │   ├── nyx.md
│   │   │   └── ...
│   │   ├── incubator/
│   │   │   ├── agents.py   # Landscape-specific agents
│   │   │   ├── config.py   # Landscape-specific config
│   │   │   └── explore.py  # Entry point
│   │   ├── culture.py      # Hive mind analysis
│   │   ├── memory.db       # Landscape memories
│   │   └── observations.db # Landscape observations
│   └── canopy/
│       └── ...
└── mcp/                    # Terrarium-wide MCP server
```

**Pros:**
- ✅ **DRY**: Shared mechanics in `core/`, no duplication
- ✅ **Clear landscape identity**: Each landscape self-contained
- ✅ **Easy to extend**: New landscapes just inherit from core
- ✅ **Migration support**: `core/migrations.py` handles cross-landscape logic
- ✅ **Culture preservation**: Each landscape has isolated databases

**Cons:**
- ⚠️ Slightly more complex initial setup
- ⚠️ Need to design good base classes

---

## Recommended Approach: **Option 3 (Hybrid)**

### Why This Works:

1. **Core Infrastructure**: Shared `ExplorationEnvironment`, `Agent`, `Observation` models prevent code duplication
2. **Landscape Isolation**: Each landscape has its own config, agents, culture, and databases
3. **Cultural DNA**: Agents inherit from core but express landscape-specific personalities
4. **Migration Ready**: `core/migrations.py` enables agents to move between landscapes
5. **Scalability**: Adding a new landscape is just creating a new directory under `landscapes/`

---

## Implementation Phases

### Phase 1: Refactor Current Structure (The Undergrowth) ✅ COMPLETE
- ✅ Moved `src/incubator/` → `src/landscapes/undergrowth/incubator/`
- ✅ Moved `src/bots/` → `src/landscapes/undergrowth/bots/`
- ✅ Created `src/core/` with shared base classes
- ✅ Extracted shared code from incubator into `core/`

### Phase 2: Landscape Registry
- Create `src/landscapes/__init__.py` with landscape registry:
  ```python
  LANDSCAPES = {
      "undergrowth": {
          "name": "The Undergrowth",
          "culture": "Dark, gothic, emergent",
          "path": "src/landscapes/undergrowth",
      },
      # Future landscapes...
  }
  ```

### Phase 3: Migration System
- Create `src/core/migrations.py` for cross-landscape agent movement
- Define migration protocols (what agents carry with them)
- Track agent lineage and cultural mixing

### Phase 4: Add Second Landscape (The Canopy)
- Create `src/landscapes/canopy/` with different cultural priorities
- Test migration from Undergrowth → Canopy
- Analyze cultural evolution

---

## Database Strategy

Each landscape maintains its own isolated databases:

```
src/landscapes/undergrowth/
├── memory.db           # Agent memories (Agno SqliteDb)
└── observations.db     # Episode observations

src/landscapes/canopy/
├── memory.db
└── observations.db
```

**Benefits:**
- ✅ Cultural isolation (hive minds don't interfere)
- ✅ Easy to analyze landscape-specific patterns
- ✅ Migration events recorded in both source and destination DBs

---

## API Design

### Landscape-Aware Execution

**Current:**
```bash
python -m src.landscapes.undergrowth.incubator.explore -a A001
```

**Future (with multiple landscapes):**
```bash
# Explicit landscape
python -m src.landscapes.undergrowth.incubator.explore -a A001

# Or with landscape flag
python -m src.core.explore --landscape undergrowth -a A001

# Cross-landscape operations
python -m src.core.migrate --agent A001 --from undergrowth --to canopy
```

### Landscape Comparison

```bash
# Compare cultures across landscapes
python -m src.core.compare --landscapes undergrowth,canopy

# View all landscape stats
python -m src.core.status
```

---

## Next Steps

1. **Decide**: Confirm Option 3 (Hybrid) is the right approach
2. **Refactor**: Move current code into `landscapes/undergrowth/`
3. **Extract**: Create `core/` with shared base classes
4. **Document**: Update READMEs to reflect multi-landscape vision
5. **Test**: Ensure Undergrowth works after refactor
6. **Expand**: Design and implement second landscape (The Canopy?)

---

## Questions to Consider

1. **Migration triggers**: What causes an agent to migrate? (Maturity? User request? Reward threshold?)
2. **Cultural mixing**: Do migrated agents retain Undergrowth culture or fully adopt Canopy culture?
3. **Cross-landscape interaction**: Can agents from different landscapes collaborate on episodes?
4. **Landscape lifecycle**: Can landscapes die, merge, or fork?
5. **Meta-landscape**: Is there a "god view" that observes all landscapes?

---

**The Terrarium is not just a training ground - it's a civilization simulator for synthetic minds.**
