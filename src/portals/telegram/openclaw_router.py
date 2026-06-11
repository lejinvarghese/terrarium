#!/usr/bin/env python
"""OpenClaw Router - Routes messages to OpenClaw landscape agents."""

import asyncio
import click
from typing import Tuple


class OpenClawRouter:
    """Routes messages to OpenClaw agents (Canopy and future landscapes)."""

    def __init__(self):
        """Initialize router with available landscapes."""
        self.agents = {
            "canopy": {
                "agent_name": "canopy",
                "working_dir": "/media/starscream/bumblebee1/blaze/terrarium/src/landscapes/canopy",
            }
            # Future landscapes: "mycelium", "reef", etc.
        }

    async def send_to_agent(
        self, landscape: str, message: str, user_id: int
    ) -> Tuple[str, bool]:
        """
        Send message to OpenClaw agent and let it handle response delivery.

        Args:
            landscape: Name of landscape (e.g., "canopy")
            message: User message
            user_id: Telegram user ID for delivery target

        Returns:
            (confirmation_text, success)
        """
        if landscape not in self.agents:
            available = ", ".join(self.agents.keys())
            return f"❌ Landscape '{landscape}' not available. Try: {available}", False

        agent_config = self.agents[landscape]

        # Call OpenClaw CLI - it handles everything (memory, processing, delivery)
        cmd = [
            "openclaw",
            "agent",
            "--agent",
            agent_config["agent_name"],
            "--message",
            message,
            "--deliver",  # OpenClaw sends response via Telegram
            "--channel",
            "telegram",
            "--to",
            str(user_id),
        ]

        try:
            click.secho(
                f"🌿 Routing to {landscape}: {message[:50]}...", fg="bright_green"
            )

            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=agent_config["working_dir"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            _, stderr = await asyncio.wait_for(
                process.communicate(), timeout=60
            )

            if process.returncode == 0:
                # OpenClaw handled everything - memory, processing, delivery
                click.secho(
                    f"✅ {landscape.title()} processed message", fg="green"
                )
                return f"✨ Message sent to {landscape.title()}", True
            else:
                error = stderr.decode().strip()
                click.secho(f"❌ {landscape} error: {error}", fg="red")
                return f"❌ Error from {landscape}: {error[:100]}", False

        except asyncio.TimeoutError:
            click.secho(f"⏱️ {landscape} timed out", fg="yellow")
            return f"⏱️ {landscape.title()} timed out", False
        except Exception as e:
            click.secho(f"❌ Failed to reach {landscape}: {e}", fg="red")
            return f"❌ Failed to reach {landscape}: {str(e)[:100]}", False

    def list_landscapes(self) -> list[str]:
        """Get available landscape names."""
        return list(self.agents.keys())
