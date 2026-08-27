"""Mentionable roles, so @agent autocompletes in Discord's picker.

A role with no members still appears in the `@` picker and renders in its own
colour, and pings nobody. That gives every agent a real mention - for humans
typing and for agents pulling each other in - without a Discord application per
agent. Inbound, role mentions are normalised back to `@name` so parsing stays
uniform; outbound, `@name` is rewritten to a role mention so it renders.
"""

import re

import click

import discord
from src.portals.core.personas import color

ROLE_MENTION = re.compile(r"<@&(\d+)>")
NAME_MENTION = re.compile(r"@(\w+)")


class Roster:
    """Maps agents to the roles that make them mentionable."""

    def __init__(self):
        self._by_name: dict[str, int] = {}
        self._by_id: dict[int, str] = {}

    def _remember(self, agent: str, role_id: int) -> None:
        self._by_name[agent] = role_id
        self._by_id[role_id] = agent

    async def _adopt(self, guild: discord.Guild, agent: str, role: discord.Role | None):
        """Create the agent's role, or bring an existing one in line.

        Role names stay lowercase so a mention reads `@nyx`, matching how agents
        write each other's names.
        """
        try:
            if role is None:
                return await guild.create_role(
                    name=agent,
                    colour=discord.Colour(color(agent)),
                    mentionable=True,
                    reason="Terrarium agent mention",
                )

            changes = {}
            if role.name != agent:
                changes["name"] = agent
            if not role.mentionable:
                changes["mentionable"] = True
            if changes:
                await role.edit(**changes, reason="Terrarium agent mention")
            return role
        except discord.Forbidden:
            click.secho(
                f"⚠️  Cannot manage @{agent} - grant Manage Roles and drag the bot's "
                "role above the agent roles",
                fg="yellow",
            )
            return None

    async def ensure(self, guild: discord.Guild, agents: list[str]) -> None:
        """Give every agent a mentionable role in this guild."""
        existing = {r.name.lower(): r for r in guild.roles}
        for agent in agents:
            role = await self._adopt(guild, agent, existing.get(agent))
            if role:
                self._remember(agent, role.id)
        click.secho(f"🏷️  {len(self._by_name)} agent roles in {guild.name}", fg="blue")

    # -- translation --------------------------------------------------------
    def normalize(self, content: str) -> str:
        """Rewrite inbound role mentions as @name, leaving unknown roles alone."""
        return ROLE_MENTION.sub(
            lambda m: f"@{self._by_id[int(m.group(1))]}" if int(m.group(1)) in self._by_id else "",
            content or "",
        ).strip()

    def linkify(self, content: str) -> str:
        """Rewrite outbound @name as a role mention so Discord renders it."""
        return NAME_MENTION.sub(
            lambda m: (
                f"<@&{self._by_name[m.group(1).lower()]}>"
                if m.group(1).lower() in self._by_name
                else m.group(0)
            ),
            content or "",
        )
