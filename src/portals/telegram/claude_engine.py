#!/usr/bin/env python
"""Claude Engine - Wrapper for Claude Code CLI integration with session and persona management."""

import asyncio
import json
import click
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple


class ClaudeEngine:
    """
    Manages interactions with Claude Code CLI.
    Handles session persistence, persona switching, and command routing.
    """

    def __init__(
        self,
        working_dir: Optional[str] = None,
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
        self.bot_prompts_dir = (
            Path(__file__).parent.parent.parent.parent / ".claude" / "agents"
        )
        # Get Danielle's user ID from env (chat_id is same as user_id for DMs)
        self.danielle_user_id = os.getenv("DANIELLE_TELEGRAM_CHAT_ID")
        click.secho(f"⚙️  ClaudeEngine initialized: {self.working_dir}", fg="blue")

    def list_bots(self, user_id: Optional[int] = None) -> list[str]:
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

        # Filter out pepper unless user is Danielle
        if user_id is None or str(user_id) != self.danielle_user_id:
            all_bots = [bot for bot in all_bots if bot != "pepper"]

        return all_bots

    def get_bot_file(self, bot: str) -> Optional[Path]:
        """
        Get the file path for a bot.

        Args:
            bot: Name of bot

        Returns:
            Path to bot file, or None if not found
        """
        bot_file = self.bot_prompts_dir / f"{bot.lower()}.md"
        return bot_file if bot_file.exists() else None

    def get_bot_description(self, bot: str) -> Optional[str]:
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

    def get_all_bots_info(self, user_id: Optional[int] = None) -> Dict[str, str]:
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

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        bot: Optional[str] = None,
    ) -> Tuple[str, str, Dict[str, Any]]:
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
            # Build claude command
            cmd = [
                "claude",
                "-p",  # Print mode (non-interactive)
                "--output-format",
                "json",  # Get structured output with session ID
                "--dangerously-skip-permissions",
            ]

            # Add working directory access for file operations
            if self.working_dir:
                cmd.extend(["--add-dir", self.working_dir])

            # Resume existing session or start new
            if session_id:
                cmd.extend(["--resume", session_id])
                click.secho(f"🔄 Resuming session: {session_id[:8]}.", fg="yellow")
            else:
                click.secho("✨ Starting new session", fg="bright_cyan")
                # Add bot system prompt for new sessions (or casper if no bot selected)
                bot_to_use = bot or "casper"
                bot_file = self.get_bot_file(bot_to_use)
                if bot_file:
                    cmd.extend(["--system-prompt-file", str(bot_file)])
                    if bot:
                        click.secho(f"🎭 Using bot: {bot}", fg="magenta")
                    else:
                        click.secho(f"🪴 Using Casper (Concierge)", fg="cyan")

            # Add the message
            cmd.append(message)

            click.secho(f"🚀 Executing Claude CLI.", fg="bright_blue")

            # Execute claude CLI
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Claude command timed out after {self.timeout}s")

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                click.secho(f"❌ Claude CLI error: {error_msg}", fg="red", bold=True)
                raise RuntimeError(f"Claude CLI failed: {error_msg}")

            # Parse JSON output
            output = stdout.decode().strip()
            try:
                events = json.loads(output)

                if not isinstance(events, list) or not events:
                    click.secho(
                        f"⚠️  Unexpected JSON format from Claude CLI", fg="yellow"
                    )
                    return "", session_id or "unknown", {}

                # Extract data from event stream
                response_text = ""
                new_session_id = session_id
                metadata = {}

                for event in events:
                    event_type = event.get("type")

                    # Get session ID from init or any event
                    if "session_id" in event:
                        new_session_id = event["session_id"]

                    # Get assistant message text
                    if event_type == "assistant" and "message" in event:
                        message = event["message"]
                        content = message.get("content", [])
                        if content and isinstance(content, list):
                            for item in content:
                                if item.get("type") == "text":
                                    response_text = item.get("text", "")
                                    break

                    # Get metadata from result event
                    if event_type == "result":
                        metadata = {
                            "cost": event.get("total_cost_usd"),
                            "duration": event.get("duration_ms"),
                            "turn": event.get("num_turns"),
                            "model": None,  # Not directly in result, would need to extract from message
                        }

                if new_session_id:
                    session_display = new_session_id[:8] + "."
                else:
                    session_display = "unknown"

                click.secho(
                    f"✅ Response received (length: {len(response_text)}, session: {session_display})",
                    fg="green",
                )
                return response_text, new_session_id or "unknown", metadata

            except json.JSONDecodeError as e:
                click.secho(f"⚠️  Failed to parse JSON output: {e}", fg="yellow")
                # Fallback: return raw output
                return output, session_id or "unknown", {}

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

    def get_status(self) -> Dict[str, Any]:
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
