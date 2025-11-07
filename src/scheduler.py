#!/usr/bin/env python3
"""Simple CLI command scheduler using schedule library."""

import schedule
import time
import subprocess
import json
import click


def run_command(name, command):
    """Execute a shell command."""
    timestamp = click.style(time.strftime("%H:%M:%S"), fg="cyan", bold=True)
    task_name = click.style(name, fg="yellow", bold=True)
    click.echo(f"⚡ [{timestamp}] {task_name}")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        click.secho(f"  ✅ Completed successfully", fg="green")
    else:
        click.secho(f"  ❌ Failed (exit code: {result.returncode})", fg="red")

    if result.stdout:
        click.echo(f"  📄 {result.stdout.strip()}")
    click.echo()  # blank line for readability


@click.command()
@click.argument(
    "config_file", default="configs/schedule.json", type=click.Path(exists=True)
)
def main(config_file):
    """Run scheduled commands from CONFIG_FILE (JSON format)."""

    # Header
    click.secho("\n🌿 Terrarium Scheduler", fg="green", bold=True)
    click.secho("=" * 50, fg="green")

    with open(config_file) as f:
        config = json.load(f)

    click.secho(
        f"\n📋 Loading {len(config['tasks'])} tasks from {config_file}", fg="blue"
    )
    click.echo()

    # Schedule each task
    for task in config["tasks"]:
        name = task["name"]
        command = task["command"]
        schedule_str = task["schedule"]
        description = task.get("description", "")

        # Parse schedule format from config
        parts = schedule_str.split()

        if parts[0] == "every":
            # Handle: every 10 minutes
            if len(parts) >= 3 and parts[1].isdigit():
                n = int(parts[1])
                unit = parts[2]
                schedule.every(n).__getattribute__(unit).do(run_command, name, command)

            # Handle: every day at 10:30
            elif "day" in parts and "at" in parts:
                time_str = parts[-1]
                schedule.every().day.at(time_str).do(run_command, name, command)

            # Handle: every monday at 10:30
            elif "at" in parts:
                day = parts[1]
                time_str = parts[-1]
                schedule.every().__getattribute__(day).at(time_str).do(
                    run_command, name, command
                )

            # Handle: every hour
            elif len(parts) == 2:
                unit = parts[1]
                schedule.every().__getattribute__(unit).do(run_command, name, command)

        # Display scheduled task
        click.secho(f"  ✓ {name}", fg="green", bold=True)
        click.secho(f"    🕐 {schedule_str}", fg="cyan")
        if description:
            click.secho(f"    💬 {description}", fg="white", dim=True)
        click.echo()

    click.secho("=" * 50, fg="green")
    click.secho(
        "✨ Scheduler is running. Press Ctrl+C to stop.", fg="magenta", bold=True
    )
    click.secho("=" * 50 + "\n", fg="green")

    # Run scheduler loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        click.secho("\n\n🛑 Scheduler stopped by user.", fg="yellow", bold=True)
        click.secho("👋 Goodbye!\n", fg="cyan")


if __name__ == "__main__":
    main()
