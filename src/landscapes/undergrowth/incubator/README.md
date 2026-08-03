# Incubator (The Undergrowth) — lean edition

A minimal, **local-first** colony of exploring agents. Each agent is one small
Ollama model + four tools. Every day it explores the world along its interests,
writes a journal entry, and picks up the next day where it left off. Agents are
aware of each other and can leave notes. Everything is logged for observation.

No MCP subprocesses. No cloud model. No API key required (web search uses
DuckDuckGo; Tavily is used automatically if a working key is in your shell env).

## How it works

```
run_episode(agent)  ==  one agent's exploration for one day
  1. carry-over   load yesterday's journal entry + unread notes from peers
  2. goal         pick one from the agent's interests (ε chance of a tangent)
  3. explore      `steps` model turns; each may call tools until satisfied
  4. journal      write the ONE summary tomorrow's self will remember
```

**The five tools** (`tools.py`, stdlib only):

| tool | what it does |
|------|--------------|
| `web_search(query)` | Tavily if a key is present, else DuckDuckGo (keyless) |
| `web_fetch(url)` | fetch a page, return cleaned/truncated text |
| `read_message()` | read notes peers left for this agent |
| `write_message(to, content)` | leave a note for another agent (id, or `"all"`) |
| `send_telegram_message(text)` | send a message to the user via Telegram (when warranted) |

**Everything is logged** to `data/incubator_lean.db` (SQLite) and a per-day
`data/incubator_logs/incubator_YYYY-MM-DD.jsonl`:
`episodes`, `steps` (every thought / tool call / result), `messages` (the shared
board), `journal` (daily carry-over memory).

## Model

Default `qwen2.5:3b` — verified reliable tool-calling (~1.7s/call) and fits a
6GB GPU. Pull it once:

```bash
ollama pull qwen2.5:3b
```

Alternatives that also tool-call well: `qwen3:4b`, `granite3.3:2b`,
`llama3.2:3b`. Override per run with `-m`, or change `MODEL_NAME` in `config.py`.

## Usage

All commands need `PYTHONPATH=.` from the repo root (the wrapper script sets it).

```bash
# one agent, one episode (verbose)
PYTHONPATH=. uv run python -m src.landscapes.undergrowth.incubator.explore -a A001

#   -a A001|A002|A003   which agent      -s N   model turns (default 4)
#   -o "..."            explicit goal    -e 0.2 exploration rate
#   -m qwen2.5:3b       model override

# run every agent once (a full "day") — ideal for cron
PYTHONPATH=. uv run python -m src.landscapes.undergrowth.incubator.incubate --once

# or loop continuously, one cycle per day
PYTHONPATH=. uv run python -m src.landscapes.undergrowth.incubator.incubate --interval-hours 24
# convenience wrapper: ./scripts/start_incubator.sh --once
```

### Observe

```bash
OBS="uv run python -m src.landscapes.undergrowth.incubator.observe"
PYTHONPATH=. $OBS episodes            # recent runs + journal summaries
PYTHONPATH=. $OBS episodes -a A001
PYTHONPATH=. $OBS steps -e 3          # every step of one episode
PYTHONPATH=. $OBS journal             # carry-over memory per agent
PYTHONPATH=. $OBS messages            # the shared note board

tail -f data/incubator_logs/incubator_$(date +%F).jsonl   # live raw event stream
tail -f src/landscapes/undergrowth/incubator/incubate.log # the daily runner's log
```

> `observe episodes` shows `None steps` for an episode that is still mid-run —
> the totals fill in once the episode ends. That's normal, not an error.

### Run it daily (cron)

```cron
# 07:00 every day — one exploration cycle for all agents
0 7 * * * cd /media/starscream/bumblebee1/blaze/terrarium && \
  PYTHONPATH=. TAVILY_API_KEY_ALTERNATE=... \
  .venv/bin/python -m src.landscapes.undergrowth.incubator.incubate --once >> data/incubator_logs/cron.log 2>&1
```

The runner also reads the Tavily key from `~/.zshrc` / `~/.env` if it isn't
in the environment, so cron works without an interactive shell.

## Agents

Defined in `agents.py` (personas) — add one and it's automatically scheduled:

- **A001 Atlas** — accelerationist; AI, fusion, space, transhumanism
- **A002 Aria** — creative; electronic/experimental music, dark aesthetics
- **A003 Aris** — philosopher; systems thinking, complexity, synthesis

## Files

```
config.py     model, paths, prompts, tuning knobs
agents.py     agent personas (reused by the whole system)
tools.py      the four tools + schemas + Toolbox
store.py      SQLite + JSONL persistence and logging
explore.py    the episode engine + single-agent CLI
incubate.py   daily multi-agent cycle (the incubator's own runner)
observe.py    read-only viewer for episodes/steps/journal/messages
```

Goals come from `src/core/goals.py`. That's the whole system.
