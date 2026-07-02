# Multi-User Implementation Plan

**Status**: Planning
**Last Updated**: 2025-12-11
**Target Completion**: TBD

---

## Table of Contents

1. [Current Architecture Assessment](#current-architecture-assessment)
2. [Migration Strategy](#migration-strategy)
3. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
4. [Scaling Beyond Initial Implementation](#scaling-beyond-initial-implementation)
5. [Testing Strategy](#testing-strategy)
6. [Rollback Plan](#rollback-plan)

---

## Current Architecture Assessment

### Strengths

- ✅ **Memory layer already multi-user ready**: mem0 + Qdrant supports `user_id` and `agent_id` separation
- ✅ **Bot system is modular**: Agent files in `.claude/agents/` are well-structured with frontmatter metadata
- ✅ **Session management exists**: Claude Code CLI handles session persistence per conversation
- ✅ **Clean separation**: Telegram portal, scheduler, and bots are decoupled components

### Bottlenecks

- ❌ **Hardcoded user IDs**: `USER_ID` and `DANIELLE_USER_ID` defined in environment variables
- ❌ **Hardcoded routing logic**: `if bot_name == "pepper"` → user mapping scattered across multiple files:
  - `src/engine/scheduler.py` (lines 36, 80)
  - `src/portals/telegram/claude_engine.py` (line 53)
- ❌ **No user registry**: No central configuration defining users and their permissions
- ❌ **No bot assignment system**: Cannot dynamically assign bots to users without code changes
- ❌ **Single-instance scheduler**: All tasks run from one process with hardcoded user routing logic

### Files Requiring Changes

| File | Current Issue | Required Change |
|------|---------------|-----------------|
| `src/engine/memory_config.py` | Hardcoded user IDs | Load from user registry |
| `src/engine/scheduler.py` | Hardcoded user routing | Dynamic user lookup |
| `src/portals/telegram/claude_engine.py` | Hardcoded bot filtering | Dynamic bot assignment |
| `src/configs/schedule.json` | Implicit user assignment | Explicit user_id field |

---

## Migration Strategy

### Design Principles

1. **Backward compatibility first**: Existing setup must continue working
2. **Minimal code churn**: Avoid rewriting working code
3. **Configuration over code**: User management via config files, not code changes
4. **Incremental rollout**: Each phase independently testable

### Success Criteria

- [ ] Support 3+ users without code changes
- [ ] Users can be added via configuration file
- [ ] Bots can be assigned to users dynamically
- [ ] Existing functionality remains unchanged
- [ ] Memory isolation per user works correctly

---

## Phase-by-Phase Implementation

### Phase 1: User Registry (1-2 hours)

**Goal**: Centralize user configuration

**Implementation**:

Create `src/configs/users.json`:

```json
{
  "users": [
    {
      "id": "user_1_id",
      "name": "User 1",
      "telegram_chat_id": "user_1_telegram_id",
      "bots": ["cassia", "nyx", "sage", "anya", "nigella", "freya"],
      "active": true,
      "timezone": "America/Toronto",
      "preferences": {
        "language": "en",
        "notifications": true
      }
    },
    {
      "id": "user_2_id",
      "name": "User 2",
      "telegram_chat_id": "user_2_telegram_id",
      "bots": ["pepper"],
      "active": true,
      "timezone": "America/Toronto",
      "preferences": {
        "language": "en",
        "notifications": true
      }
    }
  ]
}
```

Update `src/engine/memory_config.py`:

```python
"""Shared memory configuration for Terrarium."""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from mem0 import Memory
from mem0.configs.base import MemoryConfig, EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Load users from registry
def load_users():
    """Load user registry from configuration file."""
    users_file = Path(__file__).parent.parent / "configs" / "users.json"
    if users_file.exists():
        with open(users_file) as f:
            data = json.load(f)
            return {u["telegram_chat_id"]: u for u in data["users"]}
    return {}

USERS = load_users()

# Backward compatibility: keep env vars as fallback
USER_ID = os.getenv("TELEGRAM_CHAT_ID", "user_1_id")
DANIELLE_USER_ID = os.getenv("DANIELLE_TELEGRAM_CHAT_ID", "user_2_id")

# Memory configuration
MEMORY_VECTOR_PATH = os.getenv("MEMORY_VECTOR_PATH", "data/memory_vectors")

# ... rest of existing code ...
```

**Testing**:
- [ ] Verify users.json loads correctly
- [ ] Verify backward compatibility with env vars
- [ ] Verify USERS dict has correct structure

**Impact**: ✅ No behavior changes, foundation for next phases

---

### Phase 2: Dynamic Bot Routing (2-3 hours)

**Goal**: Remove hardcoded bot-to-user mapping

**Implementation**:

Update `src/engine/memory_config.py` with helper function:

```python
def get_user_for_bot(bot_name: str) -> str:
    """Determine which user a bot is assigned to.

    Args:
        bot_name: Name of the bot (e.g., 'pepper', 'cassia')

    Returns:
        User's telegram_chat_id
    """
    for user_id, user in USERS.items():
        if bot_name in user.get("bots", []):
            return user_id

    # Fallback to main user if bot not explicitly assigned
    return USER_ID

def get_bots_for_user(user_id: str) -> list[str]:
    """Get list of bots assigned to a user.

    Args:
        user_id: User's telegram_chat_id

    Returns:
        List of bot names
    """
    user = USERS.get(str(user_id))
    if user:
        return user.get("bots", [])
    return []  # No bots if user not found
```

Update `src/engine/scheduler.py`:

```python
from memory_config import get_memory, USER_ID, DANIELLE_USER_ID, get_user_for_bot

def run_command(name, command, description=""):
    """Execute a shell command with memory context injection."""
    # ... existing code ...

    if bot_name:
        try:
            memory = get_memory()

            # NEW: Dynamic user lookup instead of hardcoded
            target_user_id = get_user_for_bot(bot_name)

            # Search for relevant memories using task description as query
            # ... rest of existing code ...
```

Update `src/portals/telegram/claude_engine.py`:

```python
from memory_config import get_bots_for_user

class ClaudeEngine:
    def list_bots(self, user_id: Optional[int] = None) -> list[str]:
        """Get list of bots available to a specific user.

        Args:
            user_id: Telegram user ID for filtering bots

        Returns:
            List of bot names accessible to the user
        """
        if not self.bot_prompts_dir.exists():
            return []

        all_bots = sorted([f.stem for f in self.bot_prompts_dir.glob("*.md")])

        # If no user_id, return all bots (backward compat)
        if user_id is None:
            return all_bots

        # NEW: Get bots assigned to this user
        assigned_bots = get_bots_for_user(str(user_id))

        # Return intersection of available bots and assigned bots
        if assigned_bots:
            return [bot for bot in all_bots if bot in assigned_bots]

        # Fallback: return all bots if user has no explicit assignments
        return all_bots
```

**Testing**:
- [ ] Verify Pepper only shows for User 2's user_id
- [ ] Verify other bots show for main user
- [ ] Add test user with single bot, verify isolation
- [ ] Verify scheduler routes memory to correct user

**Impact**: ✅ Bot assignment now configuration-driven

---

### Phase 3: Schedule Task Assignment (1-2 hours)

**Goal**: Explicit user assignment in scheduled tasks

**Implementation**:

Update `src/configs/schedule.json` schema:

```json
{
  "tasks": [
    {
      "name": "🌅 Cassia - Morning Briefing",
      "user_id": "user_1_id",
      "command": "cat src/landscapes/undergrowth/bots/cassia.md | claude -p ...",
      "schedule": "every day at 07:00",
      "description": "Daily morning briefing with calendar + weather integration"
    },
    {
      "name": "🌶️ Pepper - Morning Motivation",
      "user_id": "user_2_id",
      "command": "cat src/landscapes/undergrowth/bots/pepper.md | claude -p ...",
      "schedule": "every day at 07:00",
      "description": "Daily ADHD-friendly morning motivation for User 2"
    }
  ]
}
```

Update `src/engine/scheduler.py`:

```python
def run_command(name, command, description="", user_id=None):
    """Execute a shell command with memory context injection.

    Args:
        name: Task name
        command: Shell command to execute
        description: Task description
        user_id: Optional explicit user_id for this task
    """
    timestamp = click.style(time.strftime("%H:%M:%S"), fg="cyan", bold=True)
    task_name = click.style(name, fg="yellow", bold=True)
    click.echo(f"⚡ [{timestamp}] {task_name}")

    bot_match = re.search(r'[^\w]*(\w+)\s*-', name)
    bot_name = bot_match.group(1).lower() if bot_match else None

    enhanced_command = command
    memory = None

    if bot_name:
        try:
            memory = get_memory()

            # Use explicit user_id if provided, otherwise infer from bot
            if user_id:
                target_user_id = user_id
            else:
                target_user_id = get_user_for_bot(bot_name)

            # ... rest of existing memory logic ...

# Update main scheduler loop:
def main(config_file):
    # ... existing code ...

    for task in config["tasks"]:
        name = task["name"]
        command = task["command"]
        schedule_str = task["schedule"]
        description = task.get("description", "")
        user_id = task.get("user_id")  # NEW: read user_id from task

        # Pass user_id to run_command
        # ... schedule logic with user_id parameter ...
```

**Testing**:
- [ ] Verify tasks run for correct users
- [ ] Verify tasks without user_id still work (backward compat)
- [ ] Add task for third user, verify execution

**Impact**: ✅ Tasks explicitly assigned, supports multiple users with same bot

---

### Phase 4: Environment Variable Migration (30 min)

**Goal**: Deprecate hardcoded environment variables

**Implementation**:

Update `.env.example`:

```bash
# === Core Configuration ===
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id  # DEPRECATED: Use users.json instead

# === User-Specific (DEPRECATED) ===
# These are kept for backward compatibility only.
# New installations should configure users in src/configs/users.json
DANIELLE_TELEGRAM_CHAT_ID=user_2_id  # DEPRECATED: Use users.json

# === Memory & Storage ===
MEMORY_VECTOR_PATH=data/memory_vectors
```

Create migration helper in `memory_config.py`:

```python
def migrate_env_to_users():
    """Helper to migrate from env vars to users.json.

    Prints migration instructions if env vars detected.
    """
    if os.getenv("DANIELLE_TELEGRAM_CHAT_ID") and not USERS:
        click.secho("⚠️  Legacy environment variables detected!", fg="yellow")
        click.secho("   Consider migrating to src/configs/users.json", fg="yellow")
        click.secho("   See docs/MULTI_USER_IMPLEMENTATION.md for details", fg="cyan")

# Call on import for visibility
migrate_env_to_users()
```

**Testing**:
- [ ] Test with only users.json (no env vars)
- [ ] Test with only env vars (backward compat)
- [ ] Test with both (users.json takes precedence)

**Impact**: ✅ Clean migration path, deprecation warnings

---

## Scaling Beyond Initial Implementation

### 5-20 Users: SQLite Database

**When**: User management becomes frequent, need audit logs

**Implementation** (~2 hours):

```python
# src/engine/user_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "users.db"

def init_db():
    """Initialize SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_chat_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            bots_json TEXT NOT NULL,  -- JSON array
            active INTEGER DEFAULT 1,
            timezone TEXT DEFAULT 'America/Toronto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def load_users():
    """Load users from SQLite."""
    import json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT * FROM users WHERE active = 1")
    users = {}
    for row in cursor:
        users[row[0]] = {
            "telegram_chat_id": row[0],
            "name": row[1],
            "bots": json.loads(row[2]),
            "active": bool(row[3]),
            "timezone": row[4]
        }
    conn.close()
    return users
```

**Migration**: JSON → SQLite script included in `scripts/migrate_users_to_db.py`

---

### 20-50 Users: Per-User Scheduler Instances

**When**: Need isolation, independent scaling, user-specific cron schedules

**Architecture**:

```
┌─────────────────────────────────────┐
│   Scheduler Manager (main process)  │
│   - Loads users from DB              │
│   - Spawns subprocess per user       │
│   - Monitors health                  │
└─────────────────────────────────────┘
            │
            ├───► User 1 Scheduler (subprocess)
            ├───► User 2 Scheduler (subprocess)
            └───► User N Scheduler (subprocess)
```

**Implementation** (~4 hours):

```python
# src/engine/scheduler_manager.py
import multiprocessing
from user_db import load_users

def run_user_scheduler(user_id: str, tasks: list):
    """Run scheduler for a specific user."""
    # Load user-specific tasks
    # Run schedule loop
    pass

def main():
    users = load_users()
    processes = []

    for user_id, user in users.items():
        # Filter tasks for this user
        user_tasks = [t for t in all_tasks if t["user_id"] == user_id]

        # Spawn subprocess
        p = multiprocessing.Process(
            target=run_user_scheduler,
            args=(user_id, user_tasks)
        )
        p.start()
        processes.append(p)

    # Monitor processes
    for p in processes:
        p.join()
```

---

### 50+ Users: Production Architecture

**When**: Commercial deployment, high availability requirements

**Stack**:
- **Database**: PostgreSQL (ACID, replication, backup)
- **Cache**: Redis (session management, rate limiting)
- **Queue**: Celery + Redis (distributed task execution)
- **Auth**: OAuth2 + JWT (proper authentication)
- **API**: FastAPI (REST API for management)
- **Monitoring**: Prometheus + Grafana (metrics, alerting)

**Architecture**:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Web UI     │────▶│  FastAPI     │────▶│  PostgreSQL  │
│  (Next.js)   │     │  (REST API)  │     │  (Users DB)  │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            │
                     ┌──────▼──────┐
                     │    Redis    │
                     │   (Cache)   │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │   Celery    │
                     │  (Workers)  │
                     └─────────────┘
```

**Implementation**: 2-3 weeks (requires architecture overhaul)

---

## Testing Strategy

### Unit Tests

Create `tests/test_multi_user.py`:

```python
import pytest
from src.engine.memory_config import load_users, get_user_for_bot, get_bots_for_user

def test_load_users():
    """Test user registry loading."""
    users = load_users()
    assert "user_1_id" in users
    assert "user_2_id" in users
    assert users["user_2_id"]["name"] == "User 2"

def test_get_user_for_bot():
    """Test bot to user mapping."""
    assert get_user_for_bot("pepper") == "user_2_id"
    assert get_user_for_bot("cassia") == "user_1_id"
    assert get_user_for_bot("nonexistent") == "user_1_id"  # fallback

def test_get_bots_for_user():
    """Test user to bots mapping."""
    bots = get_bots_for_user("user_2_id")
    assert "pepper" in bots
    assert "cassia" not in bots

def test_bot_isolation():
    """Test that users only see their assigned bots."""
    from src.portals.telegram.claude_engine import ClaudeEngine
    engine = ClaudeEngine()

    # User 2 should only see pepper
    danielle_bots = engine.list_bots(user_id=user_2_id)
    assert "pepper" in danielle_bots
    assert "cassia" not in danielle_bots

    # Main user should see all except pepper
    main_bots = engine.list_bots(user_id=user_1_id)
    assert "pepper" not in main_bots
    assert "cassia" in main_bots
```

### Integration Tests

1. **Test User Addition**:
   - Add new user to `users.json`
   - Verify bot assignment works
   - Verify memory isolation

2. **Test Schedule Execution**:
   - Add task for new user
   - Run scheduler for 1 minute
   - Verify task executes for correct user

3. **Test Telegram Portal**:
   - Send message from different user_ids
   - Verify correct bot list shown
   - Verify memory stored under correct user_id

---

## Rollback Plan

### If Phase 1 Fails

**Symptom**: Users fail to load, system breaks

**Action**:
1. Remove `load_users()` call from `memory_config.py`
2. Revert to hardcoded `USER_ID` and `DANIELLE_USER_ID`
3. Delete `users.json` if corrupted

**Recovery Time**: < 5 minutes

---

### If Phase 2 Fails

**Symptom**: Wrong bots shown to users, routing errors

**Action**:
1. Revert `src/engine/scheduler.py` changes
2. Restore hardcoded `if bot_name == "pepper"` logic
3. Revert `claude_engine.py` filtering logic

**Recovery Time**: < 10 minutes (git revert)

---

### If Phase 3 Fails

**Symptom**: Scheduled tasks don't run or run for wrong users

**Action**:
1. Remove `user_id` fields from `schedule.json`
2. Revert `run_command()` signature changes
3. Fall back to Phase 2 bot-based routing

**Recovery Time**: < 15 minutes

---

## Recommended Implementation Timeline

### Immediate (This Week)
- [ ] Implement Phase 1: User Registry
- [ ] Implement Phase 2: Dynamic Bot Routing
- [ ] Test with 3rd test user

**Time Investment**: ~1 day
**Value**: Foundation for 10-20 users with no future code changes

### Short-term (Next Month)
- [ ] Implement Phase 3: Schedule Task Assignment
- [ ] Implement Phase 4: Environment Variable Migration
- [ ] Add comprehensive tests

**Time Investment**: ~1 day
**Value**: Clean architecture, easy onboarding

### Mid-term (3-6 Months)
- [ ] SQLite migration (if >5 users)
- [ ] Web-based user management UI
- [ ] Per-user scheduler instances (if >20 users)

**Time Investment**: ~1 week
**Value**: Production-ready multi-user system

### Long-term (6-12 Months)
- [ ] PostgreSQL migration (if >50 users)
- [ ] Celery task queue
- [ ] OAuth authentication
- [ ] Monitoring & alerting

**Time Investment**: 2-3 weeks
**Value**: Enterprise-grade platform

---

## Notes

- **Current capacity**: 2 users (hardcoded)
- **Phase 1-2 capacity**: 10-20 users (JSON config)
- **Phase 3 capacity**: 20-50 users (SQLite + isolation)
- **Production capacity**: 1000+ users (PostgreSQL + queue)

**Next Steps**: Begin Phase 1 implementation with `src/configs/users.json` creation.
