#!/usr/bin/env python3
"""Simple CLI command scheduler using schedule library."""

import itertools
import json
import subprocess
import sys
import time
import uuid

import click
import schedule


def run_command(name, command, description=None):
    """Execute a shell command with memory context injection."""
    timestamp = click.style(time.strftime("%H:%M:%S"), fg="cyan", bold=True)
    task_name = click.style(name, fg="yellow", bold=True)
    click.echo(f"⚡ [{timestamp}] {task_name}")

    # Agents now handle their own memory via MCP tools
    enhanced_command = command

    # Add fresh session ID to prevent Claude context accumulation
    session_id = str(uuid.uuid4())
    if "claude -p" in enhanced_command:
        # Inject --session-id flag to force fresh session per run
        enhanced_command = enhanced_command.replace(
            "claude -p --dangerously-skip-permissions",
            f"claude -p --dangerously-skip-permissions --session-id {session_id}",
            1,  # Only replace first occurrence
        )
        click.secho(f"  🆔 Session: {session_id[:8]}...", fg="cyan", dim=True)

    # Execute command
    result = subprocess.run(enhanced_command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        click.secho("  ✨ Done", fg="green")
        # Agents now store their own memories via add_memory() tool
    else:
        click.secho(f"  ❌ Failed (exit code: {result.returncode})", fg="red")

    if result.stdout:
        click.echo(f"  📄 {result.stdout.strip()}")
    click.echo()  # blank line for readability


def _schedule_task(schedule_str: str, name: str, command: str, description: str):
    """Parse schedule string and register task."""
    parts = schedule_str.split()

    if parts[0] != "every":
        return

    # Handle: every 10 minutes
    if len(parts) >= 3 and parts[1].isdigit():
        n = int(parts[1])
        unit = parts[2]
        schedule.every(n).__getattribute__(unit).do(run_command, name, command, description)
        return

    # Handle: every day at 10:30
    if "day" in parts and "at" in parts:
        time_str = parts[-1]
        schedule.every().day.at(time_str).do(run_command, name, command, description)
        return

    # Handle: every monday at 10:30
    if "at" in parts:
        day = parts[1]
        time_str = parts[-1]
        schedule.every().__getattribute__(day).at(time_str).do(
            run_command, name, command, description
        )
        return

    # Handle: every hour
    if len(parts) == 2:
        unit = parts[1]
        schedule.every().__getattribute__(unit).do(run_command, name, command, description)


def _display_task(name: str, schedule_str: str, description: str):
    """Display scheduled task info."""
    click.secho(f"  ✓ {name}", fg="green", bold=True)
    click.secho(f"    🕐 {schedule_str}", fg="cyan")
    if description:
        click.secho(f"    💬 {description}", fg="white", dim=True)
    click.echo()


def _run_scheduler_loop():
    """Run the main scheduler loop with spinner."""
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    try:
        while True:
            schedule.run_pending()
            spinner_char = click.style(next(spinner), fg="cyan", bold=True)
            message = click.style("Waiting for next task.", fg="white", dim=True)
            sys.stdout.write(f"\r{spinner_char} {message}")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * 50 + "\r")
        click.secho("\n🛑 Scheduler stopped by user.", fg="yellow", bold=True)
        click.secho("👋 Goodbye!\n", fg="cyan")


@click.command()
@click.argument("config_file", default="configs/schedule.json", type=click.Path(exists=True))
def main(config_file):
    """Run scheduled commands from CONFIG_FILE (JSON format)."""
    click.secho("\n🌿 Terrarium Scheduler", fg="green", bold=True)
    click.secho("=" * 50, fg="green")

    with open(config_file) as f:
        config = json.load(f)

    click.secho(f"\n📋 Loading {len(config['tasks'])} tasks from {config_file}", fg="blue")
    click.echo()

    for task in config["tasks"]:
        _schedule_task(task["schedule"], task["name"], task["command"], task.get("description", ""))
        _display_task(task["name"], task["schedule"], task.get("description", ""))

    click.secho("=" * 50, fg="green")
    click.secho("✨ Scheduler is running. Press Ctrl+C to stop.", fg="magenta", bold=True)
    click.secho("=" * 50 + "\n", fg="green")

    _run_scheduler_loop()


if __name__ == "__main__":
    main()
