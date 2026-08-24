# User Database System

## Overview

The Terrarium user database provides a secure, lightweight way to manage user identities and preferences without exposing personal information in committed code.

## Architecture

- **Database**: SQLite (`data/users.db`)
- **Profile Facts**: Stored in Qdrant via `data/profiles.json` seed file
- **User Metadata**: Username, aliases, agent audiences in SQLite
- **NO hardcoded user data** in Python files

## Setup

### 1. Initial Database Setup (One-Time)

```bash
# Create users from environment variables
uv run python scripts/init_users.py
```

This reads user chat IDs from `.env` and creates users with default aliases.

**After running:** Delete or secure `scripts/init_users.py` - it's a one-time setup script.

### 2. Create Profile Data File

Create `data/profiles.json` with user profile facts:

```json
{
  "user1": ["Name: ...", "Location: ...", "Preferences: ..."],
  "user2": ["Name: ...", "Role: ...", "Preferences: ..."]
}
```

**This file is gitignored** - never commit it.

### 3. Seed Profile Facts into Qdrant

```bash
uv run python scripts/migrate_memory.py
```

This loads profile facts from `data/profiles.json` and stores them in Qdrant with `category="profile"`.

## User Management

### List all users

```bash
uv run python -m src.engine.user_db list
```

### Add a new user

```bash
uv run python -m src.engine.user_db add <chat_id> <username> --alias <alias> --full-name "Full Name"
```

Example:

```bash
uv run python -m src.engine.user_db add 123456789 alice --alias "a" --full-name "Alice Smith"
```

### Show user details

```bash
uv run python -m src.engine.user_db show <username|alias|chat_id>
```

### Set agent audience

Configure which user an agent writes to by default:

```bash
uv run python -m src.engine.user_db set-audience <agent_name> <username>
```

Example:

```bash
uv run python -m src.engine.user_db set-audience mybot alice
```

## Usage in Code

### Resolve user ID from username/alias

```python
from src.engine import user_db

# Resolve any identifier to a user_id
user_id = user_db.resolve_user_id("alice")  # or alias, or chat_id
user_id = user_db.resolve_user_id(None)     # Returns primary user
```

### Get user profile

```python
from src.engine import user_db

user = user_db.get_user("alice")
print(user["user_id"], user["username"])
```

### Get agent audience

```python
from src.engine import user_db

audience_id = user_db.get_agent_audience("mybot")  # Returns user_id or None
```

### Access profile facts

```python
from src.engine import memory_store

# Get all profile facts for a user
facts = memory_store.get_profile("alice")

# Render as markdown block for agent prompts
block = memory_store.render_profile("alice")
```

## Security

### What's Gitignored

- `data/users.db` - User database
- `data/profiles.json` - Profile facts source
- `scripts/init_users.py` - One-time setup script
- `.env` - Environment variables with chat IDs

### What's Committed

- `src/engine/user_db.py` - Database module (no user data)
- `src/engine/memory_store.py` - Memory interface (no user data)
- `scripts/migrate_memory.py` - Profile seeding script (loads from gitignored file)

## Troubleshooting

### "User not found" error

1. Check users: `uv run python -m src.engine.user_db list`
2. Add missing user: `uv run python -m src.engine.user_db add <id> <username>`

### Profile facts not loading

1. Ensure `data/profiles.json` exists and is valid JSON
2. Re-run: `uv run python scripts/migrate_memory.py`
3. Check Qdrant: Profile facts have `category="profile"`

### Agent not finding audience

```bash
uv run python -m src.engine.user_db set-audience <agent> <username>
```

Example:

```bash
uv run python -m src.engine.user_db set-audience mybot alice
```
