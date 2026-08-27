#!/usr/bin/env python
"""Discord portal - the Terrarium's shared channel.

Every agent speaks through one webhook under its own name, so a channel reads
like a room full of inhabitants. Agents answer only an explicit @mention, and
agent-to-agent replies draw on a hop budget only a human can refill.
"""

import asyncio
import os
from pathlib import Path

import click
from dotenv import load_dotenv

import discord
from discord import app_commands
from src.engine import memory_store, user_db
from src.landscapes.undergrowth.incubator.explore import converse
from src.landscapes.undergrowth.incubator.store import Store
from src.portals.core.claude_engine import ClaudeEngine
from src.portals.core.personas import color, display_name
from src.portals.core.session_manager import SessionManager
from src.portals.discord import status
from src.portals.discord.personas import Voices, chunk
from src.portals.discord.roles import Roster
from src.portals.discord.router import Guard, parse_mention

load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DB_PATH = os.getenv("SESSION_DB_PATH", "data/sessions.db")
WORKING_DIR = os.getenv("CLAUDE_WORKING_DIR", os.getcwd())
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))

# Local exploration agents. Naming one wakes it for a live episode; @incubator
# leaves a note for all three to pick up on their next scheduled run instead.
INCUBATOR_AGENTS = {"atlas": "A001", "aria": "A002", "aris": "A003"}
INCUBATOR_LOCK = asyncio.Semaphore(1)  # one small model, one GPU

# An agent's reply is the channel message, so the other portals stay shut for the turn
OTHER_PORTALS = [
    "mcp__terrarium__send_telegram_message",
    "mcp__terrarium__send_telegram_document",
    "mcp__terrarium__send_discord_message",
]

CHANNEL_BRIEF = (
    "You are speaking in the Terrarium's Discord channel. Your reply IS the message "
    "everyone sees - answer directly, and do not send it through any other portal. "
    "Keep it conversational and under 2000 characters. To bring in a peer, mention "
    "them as @name and they will answer here."
)

engine = ClaudeEngine(working_dir=WORKING_DIR)
sessions = SessionManager(db_path=DB_PATH)
voices = Voices()
roster = Roster()
guard = Guard(ledger=sessions)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# ============================================================================
# HELPERS
# ============================================================================


def known_agents() -> list[str]:
    """Claude agents that can be addressed in a channel."""
    return [b for b in engine.list_bots() if b != "bot.example"]


def addressable() -> list[str]:
    """Everyone a mention can reach, Claude agents and local explorers alike."""
    return [*known_agents(), *INCUBATOR_AGENTS]


def roster_brief() -> str:
    """Who else is in the room. The two colonies are otherwise unaware of each other."""
    terrarium = ", ".join(f"@{a}" for a in known_agents())
    undergrowth = ", ".join(f"@{a}" for a in INCUBATOR_AGENTS)
    return (
        f"\n\nAlso in this channel - Terrarium agents: {terrarium}. "
        f"Undergrowth explorers: {undergrowth}. "
        "Mention any of them by name, lowercase, to bring them into the conversation."
    )


def speaking_agent(message: discord.Message) -> str | None:
    """Which persona sent this, if it came from one of our webhooks."""
    if message.webhook_id not in voices.webhook_ids:
        return None
    name = message.author.name.split(" ")[-1].lower()
    return name if name in known_agents() else "system"


def resolve_user(author: discord.abc.User) -> str | None:
    """Map a Discord account to a canonical Terrarium user, if it is one of ours."""
    record = user_db.get_user(f"discord:{author.id}")
    return record["user_id"] if record else None


def queue_incubator(text: str, author: discord.abc.User) -> str:
    """Leave a note for every exploration agent to pick up on its next run."""
    store = Store()
    try:
        store.write_message(
            from_agent=f"DISCORD_{author.id}",
            from_name=author.display_name,
            to_agent="all",
            content=text,
        )
    finally:
        store.close()
    return "📨 Noted for Atlas, Aria and Aris - they'll read it on their next exploration."


async def reply_as(agent: str, text: str, placeholder: discord.WebhookMessage, channel) -> None:
    """Deliver an agent's answer, replacing its thinking placeholder."""
    pieces = chunk(roster.linkify(text))
    await placeholder.edit(content=pieces[0])
    for piece in pieces[1:]:
        await voices.speak(agent, piece, channel)


def _store_exchange(agent: str, asker: str, question: str, answer: str, channel: str) -> None:
    """Blocking half of remember() - Qdrant write plus an embedding call."""
    memory_store.add_fact(
        data=f"[#{channel}] {asker} asked: {question}\n{agent.title()} replied: {answer[:600]}",
        agent_id=agent,
        category="episodic",
    )


async def remember(agent: str, asker: str, question: str, answer: str, channel) -> None:
    """Persist a channel turn, so it outlives the 24h session it happened in."""
    try:
        await asyncio.to_thread(_store_exchange, agent, asker, question, answer, str(channel))
    except Exception as e:
        click.secho(f"⚠️  Could not remember {agent}'s turn: {e}", fg="yellow")


# ============================================================================
# AGENT TURNS
# ============================================================================


def _worked(metadata: dict) -> str:
    """A footer showing what the agent reached for, so a long turn is legible."""
    tools = [t.split("__")[-1] for t in metadata.get("tools") or []]
    if not tools:
        return ""
    shown = ", ".join(tools[:5]) + (f" +{len(tools) - 5}" if len(tools) > 5 else "")
    seconds = (metadata.get("duration") or 0) / 1000
    return f"\n\n-# {shown} · {seconds:.0f}s"


async def run_agent(agent: str, question: str, asker: str, channel, from_agent: bool) -> None:
    """Take one agent turn in a channel, subject to every guard."""
    scope_id = channel.id
    prompt = f"{CHANNEL_BRIEF}{roster_brief()}\n\n[{asker} in #{channel}]: {question}"
    refusal = guard.check(agent, scope_id, channel.id, from_agent)
    if refusal:
        click.secho(f"🛑 {agent} skipped: {refusal}", fg="yellow")
        return

    guard.claim(agent, scope_id, channel.id, from_agent)
    placeholder = await voices.thinking(agent, channel)

    async with guard.semaphore:
        try:
            session_id = sessions.get_session(scope_id, agent, max_age_hours=SESSION_EXPIRY_HOURS)
            response, new_session_id, metadata = await engine.chat(
                message=prompt,
                session_id=session_id,
                bot=agent if not session_id else None,
                disallowed_tools=OTHER_PORTALS,
            )
        except Exception as e:
            await placeholder.edit(content=f"❌ {agent} failed: {e}")
            click.secho(f"🔥 {agent}: {e}", fg="red", bold=True)
            return

    if new_session_id:
        sessions.create_session(scope_id, new_session_id, agent)
    guard.spend(metadata.get("cost"))
    await reply_as(agent, response + _worked(metadata), placeholder, channel)
    await remember(agent, asker, question, response, channel)
    click.secho(f"✅ {agent} answered in #{channel} ({len(response)} chars)", fg="green")


async def run_explorer(target: str, message: str, asker: str, channel) -> None:
    """Answer as a local Ollama agent - a conversation, not a daily exploration."""
    refusal = guard.check(target, channel.id, channel.id, from_agent=False)
    if refusal:
        click.secho(f"🛑 {target} skipped: {refusal}", fg="yellow")
        return

    guard.claim(target, channel.id, channel.id, from_agent=False)
    placeholder = await voices.thinking(target, channel)

    async with INCUBATOR_LOCK:
        try:
            result = await asyncio.to_thread(
                converse,
                INCUBATOR_AGENTS[target],
                message,
                context=roster_brief(),
                delivery="discord",
            )
        except Exception as e:
            await placeholder.edit(content=f"❌ {target} failed to answer: {e}")
            click.secho(f"🔥 {target}: {e}", fg="red", bold=True)
            return

    footer = f"-# {result['tool_calls']} tool calls · {result['duration_s']}s · local"
    await reply_as(target, f"{result['reply']}\n\n{footer}", placeholder, channel)
    await remember(target, asker, message, result["reply"], channel)
    click.secho(f"✅ {target} answered in #{channel} (ep {result['episode_id']})", fg="green")


async def dispatch(message: discord.Message, from_agent: bool) -> None:
    """Route one message to the agent it addresses, if any."""
    content = roster.normalize(message.content)
    target, text = parse_mention(content, [*addressable(), "incubator"])
    if not target or not text:
        return

    if target == "incubator":
        await message.channel.send(queue_incubator(text, message.author))
        return

    speaker = speaking_agent(message)
    if speaker == target:
        return

    asker = speaker or message.author.display_name

    if target in INCUBATOR_AGENTS:
        await run_explorer(target, text, asker, message.channel)
        return

    await run_agent(target, text, asker, message.channel, from_agent)


# ============================================================================
# EVENTS
# ============================================================================


@client.event
async def on_ready() -> None:
    """Sync commands into every guild - per-guild syncs appear immediately."""
    for guild in client.guilds:
        tree.copy_global_to(guild=guild)
        synced = await tree.sync(guild=guild)
        click.secho(f"⚡ {len(synced)} commands in {guild.name}", fg="blue")
        await roster.ensure(guild, addressable())

    if not client.guilds:
        click.secho("⚠️  Not in any server - re-invite the bot", fg="yellow", bold=True)

    click.secho(
        f"✨ Connected as {client.user} - the terrarium is open", fg="bright_green", bold=True
    )


@client.event
async def on_message(message: discord.Message) -> None:
    """Humans refill the hop budget; personas spend it."""
    agent = speaking_agent(message)
    if agent is None and message.author.bot:
        return

    if agent is None:
        guard.reset_hops(message.channel.id)
        sessions.register_user(message.author.id, message.author.name, message.author.display_name)

    await dispatch(message, from_agent=agent is not None)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    """A 👍 on a persona message is a preference worth remembering."""
    if str(payload.emoji) not in ("👍", "❤️") or not payload.member:
        return

    channel = client.get_channel(payload.channel_id)
    user_id = resolve_user(payload.member)
    if not channel or not user_id:
        return

    message = await channel.fetch_message(payload.message_id)
    agent = speaking_agent(message)
    if not agent:
        return

    memory_store.add_fact(
        data=f"Liked this from {agent.title()}: {message.content[:400]}",
        user_id=user_id,
        agent_id=agent,
        category="profile",
    )
    click.secho(f"👍 {payload.member.display_name} liked {agent}", fg="magenta")


# ============================================================================
# COMMANDS
# ============================================================================


@tree.command(name="bots", description="Who lives in the terrarium")
async def bots_command(interaction: discord.Interaction) -> None:
    """List addressable agents and how to reach them."""
    info = engine.get_all_bots_info()
    embed = discord.Embed(title="🌿 The Terrarium", color=color("system"))
    for name, description in info.items():
        embed.add_field(name=display_name(name), value=description[:200], inline=False)
    embed.set_footer(text="Mention an agent to talk to it, e.g. @nyx what's new in fusion?")
    await interaction.response.send_message(embed=embed)


def build_status_embed(channel_id: int) -> discord.Embed:
    """Assemble the terrarium digest. Blocking - call it off the event loop."""
    embed = discord.Embed(
        title="🌿 Terrarium status",
        description=status.channel_sessions(sessions, channel_id),
        color=color("system"),
    )
    embed.add_field(name="⏱️ Scheduler", value=status.scheduler_status()[:1024], inline=False)
    embed.add_field(name="🧠 Last seen doing", value=status.agent_activity()[:1024], inline=False)
    embed.add_field(name="🌱 Undergrowth", value=status.incubator_activity()[:1024], inline=False)
    return embed


@tree.command(name="status", description="What every bot in the terrarium has been doing")
async def status_command(interaction: discord.Interaction) -> None:
    """Channel sessions, scheduler state, and each agent's latest activity."""
    await interaction.response.defer(ephemeral=True)
    embed = await asyncio.to_thread(build_status_embed, interaction.channel_id)
    await interaction.followup.send(embed=embed, ephemeral=True)


@tree.command(name="clear", description="Start a fresh conversation with an agent here")
@app_commands.describe(agent="Agent to reset, or leave empty to reset all in this channel")
async def clear_command(interaction: discord.Interaction, agent: str | None = None) -> None:
    """Drop stored sessions so the next mention starts clean."""
    if agent:
        sessions.clear_session(interaction.channel_id, agent.lower())
    else:
        sessions.clear_all_sessions(interaction.channel_id)
    guard.reset_hops(interaction.channel_id)
    await interaction.response.send_message(
        f"🧹 Cleared {agent or 'all agents'} in this channel. Memories are kept.", ephemeral=True
    )


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:
    """Run the portal."""
    if not DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN not set - see src/portals/discord/README.md")

    click.secho("🤖 Starting discord portal.", fg="bright_magenta", bold=True)
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
