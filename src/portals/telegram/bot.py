#!/usr/bin/env python
"""Simple Telegram bot with Claude Code CLI integration."""

import os
from pathlib import Path
from dotenv import load_dotenv
import click
from telegram import Update, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from warnings import filterwarnings
from mem0 import Memory
from src.portals.telegram.claude_engine import ClaudeEngine
from src.portals.telegram.session_manager import SessionManager

# Load environment variables from root .env
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_PATH = os.getenv("SESSION_DB_PATH", "data/sessions.db")
WORKING_DIR = os.getenv("CLAUDE_WORKING_DIR", os.getcwd())

filterwarnings("ignore")


# ============================================================================
# COMMAND HANDLERS
# ============================================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    click.secho(f"👋 User {user.first_name} ({user.id}) started bot", fg="bright_cyan", bold=True)

    # Initialize user data
    context.user_data["bot"] = None

    # Register user
    session_manager = context.bot_data["session_manager"]
    session_manager.register_user(user.id, user.username, user.first_name)

    await update.message.reply_text(
        f"👋✨ Welcome {user.first_name}!\n\n"
        f"I'm **Casper**, your Concierge to the Terrarium 🪴\n\n"
        "💬 Send me a message to chat\n"
        "🌿 Use `/bot <name>` to connect with different bots\n"
        "📖 Type `/help` for all commands",
        reply_markup=ReplyKeyboardRemove(),
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

**Usage:**
Send me any message to chat with the current bot, or use /bot <name> to connect with a different one.
Each bot has their own unique nature and capabilities - explore and discover!"""

    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


async def bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /bot <name> command."""
    parts = update.message.text.strip().split(maxsplit=1)

    if len(parts) < 2:
        await update.message.reply_text(
            "Usage: /bot <name>\n" "Example: /bot anya\n\n" "Use /bots to see available bots."
        )
        return

    bot_name = parts[1].lower().strip()
    user_id = update.effective_user.id
    claude_engine = context.bot_data["claude_engine"]

    # Validate bot (with user filtering)
    if bot_name not in claude_engine.list_bots(user_id=user_id):
        available = ", ".join(claude_engine.list_bots(user_id=user_id))
        await update.message.reply_text(f"❌ Bot '{bot_name}' not found.\n\n" f"Available: {available}")
        return

    # Switch bot and clear old session
    old_bot = context.user_data.get("bot")
    context.user_data["bot"] = bot_name

    session_manager = context.bot_data["session_manager"]
    session_manager.clear_session(user_id, bot_name)

    await update.message.reply_text(
        f"✨ Connected to **{bot_name.title()}**\n" f"Starting fresh conversation.", parse_mode=ParseMode.MARKDOWN
    )


async def bots_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /bots command."""
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

    msg = "🌿 **Bots in the Terrarium:**\n\n"
    for b in bots:
        emoji = bot_emojis.get(b, "🤖")
        description = bots_info.get(b, "No description available")
        msg += f"{emoji} **{b.title()}** - {description}\n\n"

    current = context.user_data.get("bot")
    if current:
        msg += f"**Currently connected:** {current.title()}\n"

    msg += "\n**Connect:** /bot <name>"

    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


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
        all_memories = memory.get_all(
            user_id=str(user_id),
            agent_id=agent_id
        )

        # Handle response - might be dict with 'results' or direct list
        if isinstance(all_memories, dict):
            memory_list = all_memories.get('results', all_memories.get('memories', []))
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
            memory_text = m.get('memory', m.get('text', str(m)))
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

    session_id = session_manager.get_session(user_id, bot)

    if not session_id:
        await update.message.reply_text("No active session to compact. Start chatting first!")
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
            parse_mode=ParseMode.MARKDOWN
        )

        click.secho(f"🗜️  Compacted session for user={user_id}, bot={bot}", fg="cyan")

    except Exception as e:
        await update.message.reply_text(f"❌ Error compacting: {e}")
        click.secho(f"❌ Compact error: {e}", fg="red")


# ============================================================================
# MESSAGE HANDLER
# ============================================================================


async def send_message_in_chunks(update: Update, message: str, chunk_size: int = 4096) -> None:
    """Send large message in chunks."""
    for i in range(0, len(message), chunk_size):
        await update.message.reply_text(message[i : i + chunk_size], parse_mode=ParseMode.MARKDOWN)


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular chat messages."""
    user = update.effective_user
    user_message = update.message.text

    click.secho(f"💬 {user.first_name} ({user.id}): {user_message[:50]}.", fg="cyan")

    claude_engine = context.bot_data["claude_engine"]
    session_manager = context.bot_data["session_manager"]

    # Register user activity
    session_manager.register_user(user.id, user.username, user.first_name)

    # Get bot and session
    bot = context.user_data.get("bot")
    session_id = session_manager.get_session(user.id, bot)

    try:
        # Show typing
        await update.message.chat.send_action("typing")

        # Retrieve most relevant memories
        memory = context.bot_data["memory"]
        agent_id = bot or "casper"
        memories = memory.search(
            query=user_message,
            user_id=str(user.id),
            agent_id=agent_id,
            limit=3  # Only get top 3 most relevant memories
        )

        # Enhance message with memory context if relevant memories found
        enhanced_message = user_message
        if memories:
            context_parts = [m['memory'] for m in memories]
            enhanced_message = f"{user_message}\n\n[Context: {'; '.join(context_parts)}]"
            click.secho(f"🧠 Added {len(memories)} relevant memories", fg="magenta")

        # Chat with Claude
        response, new_session_id, metadata = await claude_engine.chat(
            message=enhanced_message,
            session_id=session_id,
            bot=bot if not session_id else None,  # Only for new sessions
        )

        # Save session
        if new_session_id:
            session_manager.create_session(user.id, new_session_id, bot)
            if metadata.get("cost"):
                session_manager.update_session_metadata(user.id, bot, cost=metadata["cost"])

        # Store conversation in memory
        if response:
            try:
                memory.add(
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": response}
                    ],
                    user_id=str(user.id),
                    agent_id=agent_id
                )
                click.secho(f"💾 Stored memory", fg="green")
            except Exception as mem_error:
                click.secho(f"⚠️  Memory storage failed: {mem_error}", fg="yellow")

        # Send response
        await send_message_in_chunks(update, response)

        click.secho(f"✅ Response sent to {user.id} (length: {len(response)})", fg="green")

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

    # Initialize components
    claude_engine = ClaudeEngine(working_dir=WORKING_DIR)
    session_manager = SessionManager(db_path=DB_PATH)
    memory = Memory()

    # Build application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Store in bot_data
    application.bot_data["claude_engine"] = claude_engine
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

    # Add message handler for chat
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    # Start bot
    click.secho("✨ Bot started! Polling for messages.", fg="bright_green", bold=True)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
