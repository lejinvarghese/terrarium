"""Routing and guards for the shared channel.

Agents only ever answer an explicit @mention, and every agent-to-agent reply
costs a hop from a budget that only a human message refills. Together with the
cooldown, the daily spend ceiling and the concurrency cap, this is what keeps a
room full of agents from talking to each other until the money runs out.
"""

import asyncio
import re
import time
from datetime import date

import click

MENTION = re.compile(r"@(\w+)\b\s*(.*)", re.DOTALL)

MAX_HOPS = 3
COOLDOWN_SECONDS = 60
DAILY_BUDGET_USD = 5.0
MAX_CONCURRENT = 2


def parse_mention(text: str, known: list[str]) -> tuple[str | None, str]:
    """Split "@agent message" into (agent, message). Unknown names pass through."""
    match = MENTION.match((text or "").strip())
    if not match:
        return None, text

    name = match.group(1).lower()
    if name not in known:
        return None, text
    return name, match.group(2).strip()


class Guard:
    """Rate, depth and spend limits for agent turns."""

    def __init__(
        self,
        max_hops: int = MAX_HOPS,
        cooldown: int = COOLDOWN_SECONDS,
        daily_budget: float = DAILY_BUDGET_USD,
        max_concurrent: int = MAX_CONCURRENT,
    ):
        self.max_hops = max_hops
        self.cooldown = cooldown
        self.daily_budget = daily_budget
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._hops: dict[int, int] = {}
        self._last_spoke: dict[tuple[str, int], float] = {}
        self._spent = 0.0
        self._spent_on = date.today()

    # -- hop budget ---------------------------------------------------------
    def reset_hops(self, root_id: int) -> None:
        """A human spoke - the chain starts over."""
        self._hops[root_id] = 0

    def _hops_left(self, root_id: int) -> int:
        return self.max_hops - self._hops.get(root_id, 0)

    def spend(self, cost: float | None) -> None:
        """Record what a turn cost, rolling over at midnight."""
        if date.today() != self._spent_on:
            self._spent, self._spent_on = 0.0, date.today()
        self._spent += cost or 0.0

    @property
    def spent_today(self) -> float:
        return self._spent if date.today() == self._spent_on else 0.0

    # -- the gate -----------------------------------------------------------
    def check(self, agent: str, root_id: int, channel_id: int, from_agent: bool) -> str | None:
        """Reason to refuse this turn, or None to allow it."""
        if self.spent_today >= self.daily_budget:
            return f"daily budget reached (${self.spent_today:.2f})"

        elapsed = time.monotonic() - self._last_spoke.get((agent, channel_id), 0.0)
        if elapsed < self.cooldown:
            return f"{agent} is cooling down ({self.cooldown - elapsed:.0f}s)"

        if from_agent and self._hops_left(root_id) <= 0:
            return f"hop budget spent ({self.max_hops})"

        return None

    def claim(self, agent: str, root_id: int, channel_id: int, from_agent: bool) -> None:
        """Mark a turn as taken - call once the gate has been passed."""
        self._last_spoke[(agent, channel_id)] = time.monotonic()
        if from_agent:
            self._hops[root_id] = self._hops.get(root_id, 0) + 1
        click.secho(
            f"🎟️  {agent} turn (hops left {self._hops_left(root_id)}, "
            f"spent ${self.spent_today:.2f})",
            fg="cyan",
            dim=True,
        )
