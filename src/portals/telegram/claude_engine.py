#!/usr/bin/env python
"""Claude Engine - Wrapper for Claude Code CLI integration with session and persona management."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import click

# Add project root to path for user_db import
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.engine import user_db  # noqa: E402


class ClaudeEngine:
    """
    Manages interactions with Claude Code CLI.
    Handles session persistence, persona switching, and command routing.
    """

    def __init__(
        self,
        working_dir: str | None = None,
        timeout: int = 300,
    ):
        """
        Initialize Claude Engine.

        Args:
            working_dir: Working directory for Claude Code context
            timeout: Command timeout in seconds
        """
        self.working_dir = working_dir or str(Path.cwd())
        self.timeout = timeout
        self.bot_prompts_dir = Path(__file__).parent.parent.parent.parent / ".claude" / "agents"
        click.secho(f"⚙️  ClaudeEngine initialized: {self.working_dir}", fg="blue")

    def list_bots(self, user_id: int | None = None) -> list[str]:
        """
        Get list of available bots.

        Args:
            user_id: Telegram user ID for filtering bots

        Returns:
            List of bot names
        """
        if not self.bot_prompts_dir.exists():
            return []

        all_bots = sorted([f.stem for f in self.bot_prompts_dir.glob("*.md")])

        # Filter bots based on agent audiences (e.g., pepper is only for specific users)
        if user_id is not None:
            filtered_bots = []
            for bot in all_bots:
                audience_id = user_db.get_agent_audience(bot)
                # Include bot if:
                # - It has no specific audience (available to all), OR
                # - Its audience matches this user
                if audience_id is None or str(user_id) == audience_id:
                    filtered_bots.append(bot)
            return filtered_bots

        return all_bots

    def get_bot_file(self, bot: str) -> Path | None:
        """
        Get the file path for a bot.

        Args:
            bot: Name of bot

        Returns:
            Path to bot file, or None if not found
        """
        bot_file = self.bot_prompts_dir / f"{bot.lower()}.md"
        return bot_file if bot_file.exists() else None

    def get_bot_description(self, bot: str) -> str | None:
        """
        Extract bot description from agent file (line 2 of frontmatter).

        Args:
            bot: Name of bot

        Returns:
            Bot description string, or None if not found
        """
        bot_file = self.get_bot_file(bot)
        if not bot_file:
            return None

        try:
            lines = bot_file.read_text().splitlines()
            # Line 0: ---
            # Line 1: name: .
            # Line 2: description: .
            if len(lines) > 2 and lines[2].startswith("description:"):
                return lines[2].replace("description:", "").strip()
            return None
        except Exception as e:
            click.secho(f"⚠️  Failed to read description for {bot}: {e}", fg="yellow")
            return None

    def get_all_bots_info(self, user_id: int | None = None) -> dict[str, str]:
        """
        Get descriptions for all available bots.

        Args:
            user_id: Telegram user ID for filtering bots

        Returns:
            Dictionary mapping bot names to their descriptions
        """
        bots_info = {}
        for bot in self.list_bots(user_id=user_id):
            description = self.get_bot_description(bot)
            if description:
                bots_info[bot] = description
        return bots_info

    def _build_command(self, message: str, session_id: str | None, bot: str | None) -> list[str]:
        """Build Claude CLI command with appropriate flags."""
        cmd = [
            "claude",
            "-p",
            "--output-format",
            "json",
            "--dangerously-skip-permissions",
        ]

        if self.working_dir:
            cmd.extend(["--add-dir", self.working_dir])

        if session_id:
            cmd.extend(["--resume", session_id])
            click.secho(f"🔄 Resuming session: {session_id[:8]}.", fg="yellow")
        else:
            self._add_bot_prompt(cmd, bot)

        cmd.extend(["--", message])
        return cmd

    def _add_bot_prompt(self, cmd: list[str], bot: str | None):
        """Add bot system prompt to command for new sessions."""
        click.secho("✨ Starting new session", fg="bright_cyan")
        bot_to_use = bot or "casper"
        bot_file = self.get_bot_file(bot_to_use)
        if bot_file:
            cmd.extend(["--system-prompt-file", str(bot_file)])
            if bot:
                click.secho(f"🎭 Using bot: {bot}", fg="magenta")
            else:
                click.secho("🪴 Using Casper (Concierge)", fg="cyan")

    async def _execute_command(self, cmd: list[str]) -> tuple[bytes, bytes, int]:
        """Execute Claude CLI command with timeout handling."""
        click.secho("🚀 Executing Claude CLI.", fg="bright_blue")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.working_dir,
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
            returncode = 1 if process.returncode is None else process.returncode
            return stdout, stderr, returncode
        except asyncio.TimeoutError as e:
            process.kill()
            await process.wait()
            raise TimeoutError(f"Claude command timed out after {self.timeout}s") from e

    def _extract_text_from_content(self, content) -> str:
        """Extract text from message content list."""
        if not isinstance(content, list):
            return ""
        for item in content:
            if item.get("type") == "text":
                return item.get("text", "")
        return ""

    def _extract_response_text(self, events: list[dict]) -> str:
        """Extract assistant message text from event stream."""
        for event in events:
            if event.get("type") != "assistant":
                continue
            message = event.get("message")
            if not isinstance(message, dict):
                continue
            content = message.get("content", [])
            text = self._extract_text_from_content(content)
            if text:
                return text
        return ""

    def _extract_metadata(self, events: list[dict]) -> dict[str, Any]:
        """Extract metadata from result event."""
        for event in events:
            if event.get("type") == "result":
                return {
                    "cost": event.get("total_cost_usd"),
                    "duration": event.get("duration_ms"),
                    "turn": event.get("num_turns"),
                    "model": None,
                }
        return {}

    def _extract_session_id(self, events: list[dict], fallback: str | None) -> str:
        """Extract session ID from any event in the stream."""
        for event in events:
            if "session_id" in event:
                return event["session_id"]
        return fallback or "unknown"

    def _parse_events(self, output: str, session_id: str | None) -> tuple[str, str, dict]:
        """Parse JSON event stream from Claude CLI."""
        try:
            events = json.loads(output)
            if not isinstance(events, list) or not events:
                click.secho("⚠️  Unexpected JSON format from Claude CLI", fg="yellow")
                return "", session_id or "unknown", {}

            response_text = self._extract_response_text(events)
            new_session_id = self._extract_session_id(events, session_id)
            metadata = self._extract_metadata(events)

            session_display = new_session_id[:8] + "." if new_session_id else "unknown"
            click.secho(
                f"✅ Response received (length: {len(response_text)}, session: {session_display})",
                fg="green",
            )
            return response_text, new_session_id, metadata

        except json.JSONDecodeError as e:
            click.secho(f"⚠️  Failed to parse JSON output: {e}", fg="yellow")
            return output, session_id or "unknown", {}

    async def chat(
        self,
        message: str,
        session_id: str | None = None,
        bot: str | None = None,
    ) -> tuple[str, str, dict[str, Any]]:
        """
        Send a message to Claude Code CLI.

        Args:
            message: User message
            session_id: Existing session ID to resume (optional)
            bot: Bot name to use (optional, only for new sessions)

        Returns:
            Tuple of (response_text, session_id, metadata)
        """
        try:
            cmd = self._build_command(message, session_id, bot)
            stdout, stderr, returncode = await self._execute_command(cmd)

            if returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                click.secho(
                    f"❌ Claude CLI failed with return code: {returncode}", fg="red", bold=True
                )
                click.secho(f"❌ stderr: {error_msg}", fg="red")
                raise RuntimeError(f"Claude CLI failed: {error_msg}")

            return self._parse_events(stdout.decode().strip(), session_id)

        except Exception as e:
            click.secho(f"🔥 Error in chat: {e}", fg="red", bold=True)
            raise

    async def analyze_code(self, code: str, language: str = "python") -> str:
        """
        Analyze code snippet.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Analysis result
        """
        prompt = f"Please analyze this {language} code:\n\n```{language}\n{code}\n```"
        response, _, _ = await self.chat(prompt)
        return response

    def get_status(self) -> dict[str, Any]:
        """
        Get current engine status.

        Returns:
            Status information
        """
        return {
            "working_dir": self.working_dir,
            "timeout": self.timeout,
            "bots_available": self.list_bots(),
            "bot_dir": str(self.bot_prompts_dir),
        }

    @staticmethod
    def is_bot_command(message: str) -> bool:
        """
        Check if message is a bot-level command (not for Claude).

        Args:
            message: Message text

        Returns:
            True if it's a bot command
        """
        bot_commands = [
            "/clear",
            "/new",
            "/bot",
            "/bots",
            "/status",
            "/help",
            "/start",
            "/cancel",
        ]
        message_lower = message.lower().strip()
        return any(message_lower.startswith(cmd) for cmd in bot_commands)
