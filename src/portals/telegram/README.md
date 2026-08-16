# Telegram Claude Bot

A Telegram bot that integrates directly with Claude Code CLI, supporting multiple bot personalities within the Terrarium ecosystem.

## Features

- **Direct Claude Code Integration**: Uses `claude` CLI for full Claude Code capabilities
- **Multiple Bot Personalities**: Switch between specialized AI bots, each with unique capabilities
- **Terrarium Metaphor**: High-tech terrarium environment with Casper as your Concierge
- **Session Persistence**: Conversations maintained across bot restarts via SQLite
- **Colorful Console Logging**: Fun, emoji-rich console output for monitoring
- **Simple Commands**: Easy-to-use command interface

## Architecture

```
src/portals/telegram/
├── bot.py              # Main bot application
├── claude_engine.py    # Claude Code CLI wrapper (Undergrowth bots)
├── session_manager.py  # SQLite session persistence
└── README.md          # This file
```

## Prerequisites

1. **Claude CLI installed and authenticated**

   ```bash
   # Install Claude Code
   npm install -g @anthropic-ai/claude-code

   # Login
   claude --login
   ```

2. **Telegram Bot Token**
   - Create a bot via [@BotFather](https://t.me/botfather) on Telegram
   - Get your bot token
   - Add to `.env` as `TELEGRAM_TOKEN`

3. **Python Dependencies**
   ```bash
   pip3 install python-telegram-bot python-dotenv click
   ```

## Configuration

Add to your root `.env` file:

```bash
TELEGRAM_TOKEN=your_telegram_bot_token_here
CLAUDE_WORKING_DIR=/path/to/your/project  # Optional, defaults to current directory
SESSION_DB_PATH=data/sessions.db           # Optional, defaults to data/sessions.db
```

## Running the Bot

### Start the Bot

From the project root directory:

```bash
python3 -m src.portals.telegram.bot
```

You should see colorful console output:

- 🤖 Starting telegram bot
- ⚙️ ClaudeEngine initialized
- 💾 SessionManager initialized
- 📊 Database tables initialized
- ✨ Bot started! Polling for messages

### Stopping the Bot

Press `Ctrl+C` to gracefully shut down the bot.

## Usage

### Commands

- `/start` - Enter the terrarium and meet Casper
- `/help` - Show all available commands
- `/bot <name>` - Connect with a specific bot
- `/bots` - List all available bots in the terrarium
- `/clear` - Start a fresh conversation
- `/status` - View your current state and session info

### How to Chat

1. Send any message to start chatting with Casper (default Concierge)
2. Use `/bot <name>` to connect with specialized bots
3. Conversations persist automatically via Claude sessions
4. Each bot has unique capabilities - use `/bots` to discover them
5. Use `/clear` to start fresh with the current bot

### Bot Switching

Use `@botname` syntax to switch between Undergrowth bots:

```
@sage what's new in AI research?
@anya create a synthwave mood board
```

**Architecture:**

- `@sage/@anya/etc` → ClaudeEngine → Claude CLI → Undergrowth bot (mem0 memory)

## How It Works

1. **Session Management**: Each user + bot combination gets a unique Claude session ID
2. **Claude CLI**: Uses `claude --add-dir <dir> --resume <session-id> -p --output-format json "message"`
3. **Persistence**: Session IDs stored in SQLite, survive bot restarts
4. **Bot Personalities**: Applied via `--system-prompt-file` from `.claude/agents/` on new sessions
5. **Event Parsing**: Parses JSON event stream from Claude CLI for responses and metadata

## Example Interaction

```
You: /start
Bot: 👋✨ Welcome!
     I'm Casper, your Concierge to the Terrarium 🪴
     💬 Send me a message to chat
     🌿 Use /bot <name> to connect with different bots
     📖 Type /help for all commands

You: What can you help me with?
Bot: [Casper explains the terrarium and available bots]

You: /bot anya
Bot: ✨ Connected to Anya
     Starting fresh conversation.

You: Generate an image of a cyberpunk cityscape
Bot: [Anya responds with creative vision and generates image]
```

## Database Schema

**sessions table:**

- `user_id` - Telegram user ID
- `persona` - Active bot name (or NULL for Casper)
- `session_id` - Claude session ID
- `message_count` - Number of messages in session
- `total_cost` - Accumulated API cost
- `created_at`, `updated_at` - Timestamps

**users table:**

- `user_id` - Telegram user ID
- `username`, `first_name` - User info
- `message_count` - Total messages sent
- `last_active` - Last activity timestamp

## Troubleshooting

**Bot not responding:**

- Check Claude CLI is authenticated: `claude --version`
- Verify `TELEGRAM_TOKEN` in `.env`
- Check colorful console logs for error messages

**Session not persisting:**

- Verify `data/` directory exists
- Check SQLite database permissions
- Look for 💾 SessionManager initialization message

**Bot personality not working:**

- Verify bot files exist in `.claude/agents/` (casper.md, anya.md, etc.)
- Check bot file has valid markdown format with frontmatter
- Look for 🎭 Using bot message in console logs

**JSON parsing errors:**

- Ensure Claude CLI is up to date: `npm update -g @anthropic-ai/claude-code`
- Check that `--output-format json` is supported in your CLI version
