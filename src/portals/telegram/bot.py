#!/usr/bin/env python
"""Simple Telegram bot with Claude Code CLI integration."""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
import click
from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    InlineQueryHandler,
    filters,
)
from warnings import filterwarnings
from mem0 import Memory
from mem0.configs.base import MemoryConfig, EmbedderConfig, LlmConfig
from mem0.vector_stores.configs import VectorStoreConfig
from src.portals.telegram.claude_engine import ClaudeEngine
from src.portals.telegram.openclaw_router import OpenClawRouter
from src.portals.telegram.session_manager import SessionManager

# Load environment variables from root .env
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_PATH = os.getenv("SESSION_DB_PATH", "data/sessions.db")
WORKING_DIR = os.getenv("CLAUDE_WORKING_DIR", os.getcwd())
MEMORY_VECTOR_PATH = os.getenv("MEMORY_VECTOR_PATH", "data/memory_vectors")
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))  # Default: 24 hours

# Incubator agent mapping (for message routing)
INCUBATOR_AGENTS = {
    "atlas": "A001",
    "aria": "A002",
    "aris": "A003",
}

filterwarnings("ignore")


# ============================================================================
# MEMORY PROMPTS
# ============================================================================

CUSTOM_FACT_EXTRACTION_PROMPT = """
Extract and store only significant, actionable, or reference-worthy information. Focus on facts that provide lasting value for future conversations.

STORE these categories:
- Personal preferences, decisions, and commitments
- Work goals, projects, technical insights, and learnings
- Health and fitness progress, goals, and routines
- Important plans, events, and time-sensitive information
- Specific facts about interests, hobbies, and values
- Behavioral patterns and productivity insights
- Relationship details and social commitments

IGNORE these patterns:
- Greetings, small talk, acknowledgments ("hi", "thanks", "okay")
- Simple queries with transactional responses (weather, time, calculations)
- Speculation without commitment ("might", "maybe", "I think", "possibly")
- Information already clearly stored in memory
- Bot capabilities or feature discussions
- Temporary context that won't be useful later

Examples:

Input: Hi! How are you today?
Output: {"facts": []}

Input: What's the weather like tomorrow?
Output: {"facts": []}

Input: I might try going to the gym next week.
Output: {"facts": []}

Input: I've decided to start going to the gym 4 times a week, focusing on strength training.
Output: {"facts": ["Committed to gym 4x per week with strength training focus"]}

Input: I just finished reading Cryptonomicon and loved it. Next I'm starting Gödel, Escher, Bach.
Output: {"facts": ["Finished reading Cryptonomicon (enjoyed it)", "Starting Gödel, Escher, Bach next"]}

Input: I need to prepare a presentation on reinforcement learning for next Friday's team meeting.
Output: {"facts": ["Presenting on reinforcement learning at team meeting next Friday"]}

Return facts in JSON format as shown above. Be selective - only capture information worth remembering long-term.
"""

CUSTOM_UPDATE_MEMORY_PROMPT = """
You manage memory for an AI assistant. Compare new facts with existing memories and decide:

ADD - New information not already stored
UPDATE - Changes to existing information (keep ID, update content)
DELETE - Contradictory or outdated information
NONE - Already stored or not worth storing

Guidelines:
- Prefer UPDATE over ADD when refining existing facts
- DELETE outdated information (old goals, completed tasks, changed preferences)
- Be aggressive with NONE for redundant or low-value information
- Preserve context in UPDATEs (e.g., "Updated goal from X to Y")

Output format:
{
  "memory": [
    {
      "id": "<existing_id or new>",
      "text": "<memory content>",
      "event": "ADD|UPDATE|DELETE|NONE",
      "old_memory": "<previous content if UPDATE>"
    }
  ]
}
"""


# ============================================================================
# COMMAND HANDLERS
# ============================================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command with bot selection panel."""
    user = update.effective_user
    click.secho(
        f"👋 User {user.first_name} ({user.id}) started bot",
        fg="bright_cyan",
        bold=True,
    )

    # Initialize user data
    context.user_data["bot"] = None

    # Register user
    session_manager = context.bot_data["session_manager"]
    session_manager.register_user(user.id, user.username, user.first_name)

    # Get available bots
    claude_engine = context.bot_data["claude_engine"]
    bots = claude_engine.list_bots(user_id=user.id)

    # Emoji mapping
    bot_emojis = {
        "anya": "🎨",
        "cassia": "📅",
        "freya": "💪",
        "nigella": "🍳",
        "nyx": "🚀",
        "sage": "📚",
        "pepper": "🌶️",
    }

    # Welcome message
    msg = (
        f"👋✨ Welcome {user.first_name}!\n\n"
        f"I'm **Casper**, your Concierge to the Terrarium 🪴\n\n"
        f"🌿 Choose a bot below to begin, or send me a message to chat with me directly.\n\n"
        f"👇 **Select a bot:**"
    )

    # Create inline keyboard with 2 buttons per row
    keyboard = []
    row = []
    for bot in bots:
        emoji = bot_emojis.get(bot, "🤖")
        button = InlineKeyboardButton(
            f"{emoji} {bot.title()}", callback_data=f"bot:{bot}"
        )
        row.append(button)

        if len(row) == 2:
            keyboard.append(row)
            row = []

    # Add remaining buttons
    if row:
        keyboard.append(row)

    # Add help button in its own row
    keyboard.append([InlineKeyboardButton("📖 Help", callback_data="help")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        msg,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = """✨ **Available Commands:**

/start - 👋 Enter the terrarium
/help -  📖 Show this help message
/bot <name> -  🌿 Connect with a bot
/bots - 🌱 List all bots in the terrarium
/clear - 🧹 Start a fresh conversation
/status - 📊 View your current state
/memories - 🧠 Show stored memories
/compact - 🗜️ Summarize and restart conversation

**Landscape Routing:**
Use @landscape to send messages to elevated intelligence layers (e.g., @canopy analyze next week's calendar)

**Bot Switching:**
Use @botname to switch bots and send a message (e.g., @sage what's new in AI research?)

**Incubator Agents:**
Send async messages to exploration agents: @atlas, @aria, @aris, or @incubator
They'll see your message on their next exploration (daily at 06:00)

**Usage:**
Send me any message to chat with the current bot, or use /bots to explore different bots!
Each bot has their own unique nature and capabilities - explore and discover!"""

    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /bot <name> command."""
    parts = update.message.text.strip().split(maxsplit=1)

    if len(parts) < 2:
        await update.message.reply_text(
            "Usage: /bot <name>\n"
            "Example: /bot anya\n\n"
            "Use /bots to see available bots."
        )
        return

    bot_name = parts[1].lower().strip()
    user_id = update.effective_user.id
    claude_engine = context.bot_data["claude_engine"]

    # Validate bot (with user filtering)
    if bot_name not in claude_engine.list_bots(user_id=user_id):
        available = ", ".join(claude_engine.list_bots(user_id=user_id))
        await update.message.reply_text(
            f"❌ Bot '{bot_name}' not found.\n\n" f"Available: {available}"
        )
        return

    # Switch bot and clear old session
    context.user_data["bot"] = bot_name
    session_manager = context.bot_data["session_manager"]
    session_manager.clear_session(user_id, bot_name)

    await update.message.reply_text(
        f"✨ Connected to **{bot_name.title()}**\n" f"Starting fresh conversation.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def bots_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /bots command with interactive button panel."""
    user_id = update.effective_user.id
    claude_engine = context.bot_data["claude_engine"]
    bots = claude_engine.list_bots(user_id=user_id)

    if not bots:
        await update.message.reply_text("The terrarium is empty.")
        return

    # Emoji mapping for each bot
    bot_emojis = {
        "anya": "🎨",
        "cassia": "📅",
        "freya": "💪",
        "nigella": "🍳",
        "nyx": "🚀",
        "sage": "📚",
        "pepper": "🌶️",
    }

    # Get descriptions dynamically from agent files (with user filtering)
    bots_info = claude_engine.get_all_bots_info(user_id=user_id)

    # Build message text
    msg = "🌿 **Bots in the Terrarium:**\n\n"
    for b in bots:
        emoji = bot_emojis.get(b, "🤖")
        description = bots_info.get(b, "No description available")
        msg += f"{emoji} **{b.title()}** - {description}\n\n"

    current = context.user_data.get("bot")
    if current:
        msg += f"✅ **Currently connected:** {current.title()}\n"

    msg += "\n👇 **Tap a bot below to connect:**"

    # Create inline keyboard with 2 buttons per row
    keyboard = []
    row = []
    for bot in bots:
        emoji = bot_emojis.get(bot, "🤖")
        button_text = f"{emoji} {bot.title()}"

        # Add checkmark if this is the current bot
        if bot == current:
            button_text = f"✓ {button_text}"

        button = InlineKeyboardButton(button_text, callback_data=f"bot:{bot}")
        row.append(button)

        if len(row) == 2:
            keyboard.append(row)
            row = []

    # Add remaining buttons
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /clear command."""
    user_id = update.effective_user.id
    bot = context.user_data.get("bot")

    session_manager = context.bot_data["session_manager"]
    session_manager.clear_session(user_id, bot)

    bot_msg = f" with {bot.title()} bot" if bot else ""
    await update.message.reply_text(
        f"🔄 Conversation cleared{bot_msg}. Starting fresh!\n\n"
        f"💡 Your memories are preserved. Use /memories to view them."
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command."""
    user_id = update.effective_user.id
    bot = context.user_data.get("bot")

    session_manager = context.bot_data["session_manager"]
    session_info = session_manager.get_session_info(user_id, bot)
    user_stats = session_manager.get_user_stats(user_id)
    all_sessions = session_manager.list_user_sessions(user_id)

    msg = "**📊 Terrarium Status**\n\n"
    msg += f"**Connected to:** {bot.title() if bot else 'Casper (Concierge)'}\n"

    if session_info:
        msg += f"**Conversation:** Active ({session_info['message_count']} messages)\n"
        if session_info["total_cost"] > 0:
            msg += f"**Cost:** ${session_info['total_cost']:.4f}\n"
    else:
        msg += "**Conversation:** None\n"

    if user_stats:
        msg += f"\n**Total messages:** {user_stats['message_count']}\n"
        msg += f"**Active conversations:** {user_stats['active_sessions']}\n"

    if len(all_sessions) > 1:
        msg += "\n**All Connections:**\n"
        for s in all_sessions:
            b = s["persona"] or "casper"
            msg += f"• {b.title()}: {s['message_count']} msgs\n"

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def memories_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /memories command - show stored memories."""
    user_id = update.effective_user.id
    bot = context.user_data.get("bot")
    memory = context.bot_data["memory"]

    # Always use casper as default if no bot selected
    agent_id = bot if bot else "casper"

    try:
        # Get all memories for this user and agent (pass as direct parameters)
        click.secho(
            f"🔍 Fetching memories: user_id={str(user_id)}, agent_id={agent_id}",
            fg="cyan",
        )
        all_memories = memory.get_all(user_id=str(user_id), agent_id=agent_id)
        click.secho(f"📦 Raw memory response type: {type(all_memories)}", fg="cyan")
        click.secho(f"📦 Raw memory response: {all_memories}", fg="cyan")

        # Handle response - might be dict with 'results' or direct list
        if isinstance(all_memories, dict):
            memory_list = all_memories.get("results", all_memories.get("memories", []))
        else:
            memory_list = all_memories if isinstance(all_memories, list) else []

        if not memory_list:
            await update.message.reply_text(
                f"No memories stored yet with {agent_id.title()}.\n\n"
                f"Start chatting and I'll remember important details!"
            )
            return

        # Show first 10 memories
        bot_name = agent_id.title()
        msg = f"🧠 **Memories with {bot_name}** ({len(memory_list)} total):\n\n"

        for i, m in enumerate(memory_list[:10], 1):
            memory_text = m.get("memory", m.get("text", str(m)))
            msg += f"{i}. {memory_text}\n"

        if len(memory_list) > 10:
            msg += f"\n...and {len(memory_list) - 10} more"

        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching memories: {str(e)}")
        click.secho(f"❌ Memory fetch error: {e}", fg="red")


async def compact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /compact command - summarize and restart session."""
    user_id = update.effective_user.id
    bot = context.user_data.get("bot")
    claude_engine = context.bot_data["claude_engine"]
    session_manager = context.bot_data["session_manager"]

    session_id = session_manager.get_session(user_id, bot, max_age_hours=SESSION_EXPIRY_HOURS)

    if not session_id:
        await update.message.reply_text(
            "No active session to compact. Start chatting first!"
        )
        return

    try:
        await update.message.chat.send_action("typing")

        # Ask Claude to summarize the conversation
        summary_request = (
            "Please provide a concise summary of our conversation so far, "
            "focusing on key facts, decisions, and context that should be "
            "remembered. Format as bullet points."
        )

        response, _, _ = await claude_engine.chat(
            message=summary_request,
            session_id=session_id,
            bot=None,  # Resume existing session
        )

        # Clear the session (forces new session on next message)
        session_manager.clear_session(user_id, bot)

        bot_name = bot.title() if bot else "Casper"
        await update.message.reply_text(
            f"🗜️ **Conversation Compacted with {bot_name}**\n\n"
            f"Summary:\n{response}\n\n"
            f"✨ Your memories are preserved. Next message starts a fresh session.",
            parse_mode=ParseMode.MARKDOWN,
        )

        click.secho(f"🗜️  Compacted session for user={user_id}, bot={bot}", fg="cyan")

    except Exception as e:
        await update.message.reply_text(f"❌ Error compacting: {e}")
        click.secho(f"❌ Compact error: {e}", fg="red")


async def bot_selection_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle bot selection from inline keyboard buttons."""
    query = update.callback_query
    await query.answer()  # Dismiss loading state

    callback_data = query.data
    user_id = query.from_user.id

    # Handle help button
    if callback_data == "help":
        help_text = """✨ **Available Commands:**

        /start - 👋 Enter the terrarium
        /help -  📖 Show this help message
        /bot <name> -  🌿 Connect with a bot
        /bots - 🌱 List all bots in the terrarium
        /clear - 🧹 Start a fresh conversation
        /status - 📊 View your current state
        /memories - 🧠 Show stored memories
        /compact - 🗜️ Summarize and restart conversation

        **Landscape Routing:**
        Use @landscape to send messages to elevated intelligence layers (e.g., @canopy analyze next week's calendar)

        **Bot Switching:**
        Use @botname to switch bots and send a message (e.g., @sage what's new in AI research?)

        **Incubator Agents:**
        Send async messages to exploration agents: @atlas, @aria, @aris, or @incubator
        They'll see your message on their next exploration (daily at 06:00)

        **Usage:**
        Send me any message to chat with the current bot, or use /bots to explore different bots!"""
        await query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN)
        return

    # Handle bot selection
    if not callback_data.startswith("bot:"):
        return

    bot_name = callback_data.split(":", 1)[1]
    claude_engine = context.bot_data["claude_engine"]
    session_manager = context.bot_data["session_manager"]

    # Validate bot exists (with user filtering)
    available_bots = claude_engine.list_bots(user_id=user_id)
    if bot_name not in available_bots:
        await query.edit_message_text("❌ Bot not available")
        return

    # Switch to the bot
    context.user_data["bot"] = bot_name
    session_manager.clear_session(user_id, bot_name)

    # Emoji mapping
    bot_emojis = {
        "anya": "🎨",
        "cassia": "📅",
        "freya": "💪",
        "nigella": "🍳",
        "nyx": "🚀",
        "sage": "📚",
        "pepper": "🌶️",
    }
    emoji = bot_emojis.get(bot_name, "🤖")

    await query.edit_message_text(
        f"✨ **Connected to {emoji} {bot_name.title()}**\n\n"
        f"Starting a fresh conversation.\n"
        f"Send me a message to begin!",
        parse_mode=ParseMode.MARKDOWN,
    )

    click.secho(f"🔄 User {user_id} switched to bot: {bot_name}", fg="cyan")


# ============================================================================
# INLINE QUERY HANDLER
# ============================================================================


async def inline_query_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle inline queries for direct bot access (e.g., @yourbot anya hello)."""
    query = update.inline_query.query
    user_id = update.inline_query.from_user.id
    claude_engine = context.bot_data["claude_engine"]

    if not query:
        return

    # Parse query: first word is bot name, rest is message
    parts = query.split(maxsplit=1)
    if len(parts) < 1:
        return

    bot_name = parts[0].lower()
    message = parts[1] if len(parts) > 1 else ""

    # Emoji mapping
    bot_emojis = {
        "anya": "🎨",
        "cassia": "📅",
        "freya": "💪",
        "nigella": "🍳",
        "nyx": "🚀",
        "sage": "📚",
        "pepper": "🌶️",
        "casper": "🪴",
    }

    available_bots = claude_engine.list_bots(user_id=user_id)

    # If only bot name entered, show available bots as suggestions
    if not message:
        results = []
        for bot in available_bots:
            emoji = bot_emojis.get(bot, "🤖")
            description = (
                claude_engine.get_bot_description(bot) or f"Talk to {bot.title()}"
            )

            result = InlineQueryResultArticle(
                id=bot,
                title=f"{emoji} {bot.title()}",
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text=f"/bot {bot}\n\nTip: Use inline mode like this:\n@yourbot {bot} your message here"
                ),
            )
            results.append(result)

        await update.inline_query.answer(results, cache_time=30)
        return

    # Validate bot exists
    if bot_name not in available_bots:
        # Show error result
        result = InlineQueryResultArticle(
            id="error",
            title=f"❌ Bot '{bot_name}' not found",
            description=f"Available bots: {', '.join(available_bots)}",
            input_message_content=InputTextMessageContent(
                message_text=f"Bot '{bot_name}' not available. Use /bots to see available bots."
            ),
        )
        await update.inline_query.answer([result], cache_time=0)
        return

    # Create a result that switches to the bot and sends the message
    # Use @botname syntax that chat_handler will recognize
    emoji = bot_emojis.get(bot_name, "🤖")
    result = InlineQueryResultArticle(
        id=f"{bot_name}:{message[:50]}",
        title=f"{emoji} Ask {bot_name.title()}: {message[:50]}",
        description=f"Send this message to {bot_name.title()}",
        input_message_content=InputTextMessageContent(
            message_text=f"@{bot_name} {message}"
        ),
    )

    await update.inline_query.answer([result], cache_time=0)
    click.secho(
        f"🔍 Inline query: user={user_id}, bot={bot_name}, query={message[:30]}",
        fg="cyan",
    )


# ============================================================================
# MESSAGE HANDLER
# ============================================================================


async def send_message_in_chunks(
    update: Update, message: str, chunk_size: int = 4096
) -> None:
    """Send large message in chunks, with fallback for markdown parsing errors."""
    for i in range(0, len(message), chunk_size):
        chunk = message[i : i + chunk_size]
        try:
            await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            # If markdown parsing fails, send as plain text
            if "can't parse entities" in str(e).lower():
                click.secho(
                    f"⚠️  Markdown parse error, sending as plain text", fg="yellow"
                )
                await update.message.reply_text(chunk)
            else:
                raise


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular chat messages."""
    user = update.effective_user
    user_message = update.message.text

    click.secho(f"💬 {user.first_name} ({user.id}): {user_message[:50]}.", fg="cyan")

    claude_engine = context.bot_data["claude_engine"]
    openclaw_router = context.bot_data["openclaw_router"]
    session_manager = context.bot_data["session_manager"]

    # Register user activity
    session_manager.register_user(user.id, user.username, user.first_name)

    # Check for @landscape syntax first (OpenClaw landscapes like Canopy)
    landscape_match = re.match(r"@(\w+)\s+(.*)", user_message, re.DOTALL)
    if landscape_match:
        target = landscape_match.group(1).lower()
        actual_message = landscape_match.group(2).strip()

        # Check if this is a landscape (not an Undergrowth bot)
        available_landscapes = openclaw_router.list_landscapes()
        if target in available_landscapes:
            await update.message.chat.send_action("typing")

            response, success = await openclaw_router.send_to_agent(
                landscape=target,
                message=actual_message,
                user_id=user.id
            )

            await update.message.reply_text(response)
            click.secho(f"🌿 Routed to landscape: {target}", fg="green")
            return  # Exit early - landscape handled via OpenClaw

    # Check for @incubator agent syntax (async message queue to exploration agents)
    incubator_match = re.match(r"@(atlas|aria|aris|incubator)\s+(.*)", user_message, re.DOTALL | re.IGNORECASE)
    if incubator_match:
        target = incubator_match.group(1).lower()
        message_text = incubator_match.group(2).strip()

        # Determine recipient
        if target == "incubator":
            agent_id = "all"  # Broadcast to all incubator agents
            display_name = "all incubator agents (Atlas, Aria, Aris)"
        else:
            agent_id = INCUBATOR_AGENTS[target]
            display_name = target.title()

        # Write to incubator message queue
        from src.landscapes.undergrowth.incubator.store import Store
        store = Store()
        try:
            store.write_message(
                from_agent=f"TELEGRAM_{user.id}",
                from_name=user.first_name,
                to_agent=agent_id,
                content=message_text
            )
            await update.message.reply_text(
                f"📨 Message queued for **{display_name}**.\n"
                f"They'll see it on their next exploration (daily at 06:00).",
                parse_mode=ParseMode.MARKDOWN
            )
            click.secho(f"📬 Incubator message queued: {user.first_name} → {target}", fg="green")
        finally:
            store.close()
        return  # Exit early - message queued

    # Check for @botname syntax: @sage how are you?
    at_bot_match = re.match(r"@(\w+)\s+(.*)", user_message, re.DOTALL)
    if at_bot_match:
        bot_name = at_bot_match.group(1).lower()
        actual_message = at_bot_match.group(2).strip()

        # Validate bot exists (with user filtering)
        available_bots = claude_engine.list_bots(user_id=user.id)
        if bot_name in available_bots:
            # Switch to the bot
            context.user_data["bot"] = bot_name
            session_manager.clear_session(user.id, bot_name)

            # Update the message to process
            user_message = actual_message
            click.secho(f"🔄 @bot syntax switch to: {bot_name}", fg="cyan")
        else:
            await update.message.reply_text(
                f"❌ Bot '{bot_name}' not found.\n"
                f"Available bots: {', '.join(available_bots)}\n\n"
                f"Tip: Use @botname followed by your message (e.g., @sage what's new?)"
            )
            return

    # Get bot and session (with auto-expiry)
    bot = context.user_data.get("bot")
    session_id = session_manager.get_session(user.id, bot, max_age_hours=SESSION_EXPIRY_HOURS)

    try:
        # Show typing
        await update.message.chat.send_action("typing")

        # Retrieve most relevant memories
        memory = context.bot_data["memory"]
        agent_id = bot or "casper"
        memory_list = []

        try:
            memories_response = memory.search(
                query=user_message,
                user_id=str(user.id),
                agent_id=agent_id,
                limit=3,  # Only get top 3 most relevant memories
            )

            # Handle response format
            if isinstance(memories_response, dict):
                memory_list = memories_response.get(
                    "results", memories_response.get("memories", [])
                )
            else:
                memory_list = (
                    memories_response if isinstance(memories_response, list) else []
                )
        except Exception as mem_error:
            click.secho(f"⚠️  Memory retrieval failed: {mem_error}", fg="yellow")
            memory_list = []

        # Enhance message with memory context if relevant memories found
        enhanced_message = user_message
        if memory_list:
            context_parts = [
                m.get("memory", m.get("text", str(m))) for m in memory_list
            ]
            enhanced_message = (
                f"{user_message}\n\n[Context: {'; '.join(context_parts)}]"
            )
            click.secho(f"🧠 Added {len(memory_list)} relevant memories", fg="magenta")

        # Chat with Claude
        try:
            response, new_session_id, metadata = await claude_engine.chat(
                message=enhanced_message,
                session_id=session_id,
                bot=bot if not session_id else None,  # Only for new sessions
            )
        except RuntimeError as e:
            # Handle expired/invalid session - clear and retry with new session
            if "No conversation found with session ID" in str(e):
                click.secho(f"⚠️  Session expired, starting fresh", fg="yellow")
                session_manager.clear_session(user.id, bot)
                # Retry with new session
                response, new_session_id, metadata = await claude_engine.chat(
                    message=enhanced_message,
                    session_id=None,  # Force new session
                    bot=bot,
                )
            else:
                raise  # Re-raise other RuntimeErrors

        # Save session
        if new_session_id:
            session_manager.create_session(user.id, new_session_id, bot)
            if metadata.get("cost"):
                session_manager.update_session_metadata(
                    user.id, bot, cost=metadata["cost"]
                )

        # Store conversation in memory
        if response:
            try:
                result = memory.add(
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": response},
                    ],
                    user_id=str(user.id),
                    agent_id=agent_id,
                )
                # Only log if memories were actually stored
                if (
                    result
                    and (isinstance(result, dict) and result.get("results"))
                    or (isinstance(result, list) and len(result) > 0)
                ):
                    memory_count = (
                        len(result.get("results", result))
                        if isinstance(result, dict)
                        else len(result)
                    )
                    click.secho(
                        f"💾 Stored {memory_count} memory/memories: user_id={str(user.id)}, agent_id={agent_id}",
                        fg="green",
                    )
                else:
                    click.secho(
                        f"📝 No significant facts to store (filtered by extraction prompt)",
                        fg="cyan",
                    )
            except Exception as mem_error:
                click.secho(f"⚠️  Memory storage failed: {mem_error}", fg="yellow")

        # Send response
        await send_message_in_chunks(update, response)

        click.secho(
            f"✅ Response sent to {user.id} (length: {len(response)})", fg="green"
        )

    except TimeoutError:
        await update.message.reply_text("⏱️ Request timed out. Please try again.")
        click.secho("⏱️ Request timed out", fg="yellow")
    except RuntimeError as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        click.secho(f"❌ Runtime error: {e}", fg="red")
    except Exception as e:
        click.secho(f"🔥 Error in chat_handler: {e}", fg="red", bold=True)
        await update.message.reply_text(f"❌ Unexpected error: {str(e)}")


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:
    """Run the bot."""
    click.secho("🤖 Starting telegram bot.", fg="bright_magenta", bold=True)

    # Configure Mem0 with Qdrant server (concurrent access for bot + scheduler)
    mem0_config = MemoryConfig(
        vector_store=VectorStoreConfig(
            provider="qdrant",
            config={
                "host": "localhost",
                "port": 6333,
            },
        ),
        embedder=EmbedderConfig(
            provider="openai",
            config={
                "model": "text-embedding-3-small",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "openai_base_url": "https://api.openai.com/v1"
            }
        ),
        llm=LlmConfig(
            provider="openai",
            config={
                "model": "gpt-4o-mini",
                "temperature": 0,
                "api_key": os.getenv("OPENAI_API_KEY"),
                "openai_base_url": "https://api.openai.com/v1"
            }
        ),
        custom_fact_extraction_prompt=CUSTOM_FACT_EXTRACTION_PROMPT,
        custom_update_memory_prompt=CUSTOM_UPDATE_MEMORY_PROMPT,
    )

    # Initialize components
    claude_engine = ClaudeEngine(working_dir=WORKING_DIR)
    openclaw_router = OpenClawRouter()
    session_manager = SessionManager(db_path=DB_PATH)
    memory = Memory(config=mem0_config)

    # Build application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Store in bot_data
    application.bot_data["claude_engine"] = claude_engine
    application.bot_data["openclaw_router"] = openclaw_router
    application.bot_data["session_manager"] = session_manager
    application.bot_data["memory"] = memory

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("bot", bot_command))
    application.add_handler(CommandHandler("bots", bots_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("memories", memories_command))
    application.add_handler(CommandHandler("compact", compact_command))

    # Add callback query handler for inline keyboard buttons
    application.add_handler(CallbackQueryHandler(bot_selection_callback))

    # Add inline query handler for direct bot access
    application.add_handler(InlineQueryHandler(inline_query_handler))

    # Add message handler for chat
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler)
    )

    # Start bot
    click.secho("✨ Bot started! Polling for messages.", fg="bright_green", bold=True)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
