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
/bot <name> -  🌿 Connect with a bot (anya, cassia, freya, nigella, nyx, sage)
/bots - 🌱 List all bots in the terrarium
/clear - 🧹 Start a fresh conversation
/status - 📊 View your current state

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
    claude_engine = context.bot_data["claude_engine"]

    # Validate bot
    if bot_name not in claude_engine.list_bots():
        available = ", ".join(claude_engine.list_bots())
        await update.message.reply_text(f"❌ Bot '{bot_name}' not found.\n\n" f"Available: {available}")
        return

    # Switch bot and clear old session
    old_bot = context.user_data.get("bot")
    context.user_data["bot"] = bot_name

    user_id = update.effective_user.id
    session_manager = context.bot_data["session_manager"]
    session_manager.clear_session(user_id, bot_name)

    await update.message.reply_text(
        f"✨ Connected to **{bot_name.title()}**\n" f"Starting fresh conversation.", parse_mode=ParseMode.MARKDOWN
    )


async def bots_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /bots command."""
    claude_engine = context.bot_data["claude_engine"]
    bots = claude_engine.list_bots()

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
    }

    # Get descriptions dynamically from agent files
    bots_info = claude_engine.get_all_bots_info()

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
    await update.message.reply_text(f"🔄 Conversation cleared{bot_msg}. Starting fresh!")


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

        # Chat with Claude
        response, new_session_id, metadata = await claude_engine.chat(
            message=user_message,
            session_id=session_id,
            bot=bot if not session_id else None,  # Only for new sessions
        )

        # Save session
        if new_session_id:
            session_manager.create_session(user.id, new_session_id, bot)
            if metadata.get("cost"):
                session_manager.update_session_metadata(user.id, bot, cost=metadata["cost"])

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

    # Build application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Store in bot_data
    application.bot_data["claude_engine"] = claude_engine
    application.bot_data["session_manager"] = session_manager

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("bot", bot_command))
    application.add_handler(CommandHandler("bots", bots_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("status", status_command))

    # Add message handler for chat
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    # Start bot
    click.secho("✨ Bot started! Polling for messages.", fg="bright_green", bold=True)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
