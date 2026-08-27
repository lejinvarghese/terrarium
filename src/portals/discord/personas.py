"""Persona voices for Discord.

One webhook per channel is enough: `Webhook.send(username=...)` overrides the
display name per message, so every agent speaks through the same webhook with
its own name and avatar. Threads reuse their parent channel's webhook.
"""

import os

import click

import discord
from src.portals.core.personas import display_name, emoji

MAX_CHARS = 2000
WEBHOOK_NAME = "Terrarium"

# Agents may mention each other's roles; they may never ping the room
MENTIONS = discord.AllowedMentions(everyone=False, roles=True, users=True)

# Optional per-agent avatars, e.g. DISCORD_AVATAR_NYX=https://.../nyx.png
_AVATAR_ENV = "DISCORD_AVATAR_{}"


def avatar_url(persona: str | None) -> str | None:
    """Avatar override for a persona, if one is configured in the environment."""
    return os.getenv(_AVATAR_ENV.format((persona or "casper").upper()))


def _paragraphs(text: str, size: int):
    """Yield paragraphs, hard-splitting any that exceed the limit on their own."""
    for para in text.split("\n\n"):
        if len(para) <= size:
            yield para
        else:
            yield from (para[i : i + size] for i in range(0, len(para), size))


def chunk(text: str, size: int = MAX_CHARS) -> list[str]:
    """Split text into Discord-sized pieces, preferring paragraph boundaries."""
    text = text or "…"
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    current = ""
    for para in _paragraphs(text, size):
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) > size:
            chunks.append(current)
            current = para
        else:
            current = candidate
    return [*chunks, current]


class Voices:
    """Resolves and caches the webhook each channel speaks through."""

    def __init__(self):
        self._webhooks: dict[int, discord.Webhook] = {}
        self.webhook_ids: set[int] = set()

    @staticmethod
    def _target(channel) -> tuple[discord.TextChannel, discord.Thread | None]:
        """Split a send target into (parent channel, thread)."""
        if isinstance(channel, discord.Thread):
            return channel.parent, channel
        return channel, None

    async def _webhook(self, parent: discord.TextChannel) -> discord.Webhook:
        """Get or create this channel's Terrarium webhook."""
        if parent.id in self._webhooks:
            return self._webhooks[parent.id]

        existing = [w for w in await parent.webhooks() if w.name == WEBHOOK_NAME]
        hook = existing[0] if existing else await parent.create_webhook(name=WEBHOOK_NAME)

        self._webhooks[parent.id] = hook
        self.webhook_ids.add(hook.id)
        click.secho(f"🔗 Webhook ready in #{parent.name}", fg="blue")
        return hook

    async def speak(self, persona: str | None, content: str, channel) -> discord.WebhookMessage:
        """Post as a persona, chunked. Returns the last message sent."""
        parent, thread = self._target(channel)
        hook = await self._webhook(parent)
        kwargs = {
            "username": display_name(persona),
            "avatar_url": avatar_url(persona),
            "allowed_mentions": MENTIONS,
            "wait": True,
        }
        if thread:
            kwargs["thread"] = thread

        message = None
        for piece in chunk(content):
            message = await hook.send(piece, **kwargs)
        return message

    async def thinking(self, persona: str | None, channel) -> discord.WebhookMessage:
        """Post a placeholder to edit in place once the agent responds."""
        return await self.speak(persona, f"{emoji(persona)} *thinking…*", channel)
