#!/usr/bin/env python3
"""Sync prompt files back to Open WebUI database."""

import sqlite3
import json
import time
from pathlib import Path
import click


def get_model_name_from_filename(filename):
    """Convert filename to model name (e.g., cassia.md -> Cassia)."""
    return filename.stem.title()


def sync_prompts_to_db(prompts_dir, db_path, dry_run=False, skip_confirm=False):
    """Sync all prompts from markdown files to Open WebUI database."""

    prompts_dir = Path(prompts_dir)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    updates = []

    # Read all markdown files
    for prompt_file in prompts_dir.glob("*.md"):
        model_name = get_model_name_from_filename(prompt_file)

        # Read the new prompt content
        with open(prompt_file, "r") as f:
            new_prompt = f.read()

        # Find the model in the database (case-insensitive search)
        cursor.execute(
            "SELECT id, name, params FROM model WHERE LOWER(name) = LOWER(?)",
            (model_name,),
        )
        result = cursor.fetchone()

        if not result:
            click.secho(
                f"⚠️  No model found for {model_name} ({prompt_file.name})", fg="yellow"
            )
            continue

        model_id, db_name, params_json = result
        params = json.loads(params_json)

        # Update the system prompt
        old_prompt = params.get("system", "")
        params["system"] = new_prompt

        # Store the update
        updates.append(
            {
                "id": model_id,
                "name": db_name,
                "file": prompt_file.name,
                "params": json.dumps(params),
                "old_length": len(old_prompt),
                "new_length": len(new_prompt),
            }
        )

    if not updates:
        click.secho("No models found to update.", fg="yellow")
        return

    # Display updates
    click.secho(f"\n📝 Found {len(updates)} models to update:", fg="cyan", bold=True)
    for update in updates:
        click.echo(f"  • {update['name']}")
        click.echo(f"    File: {update['file']}")
        click.echo(
            f"    Prompt length: {update['old_length']} → {update['new_length']} chars"
        )

    if dry_run:
        click.secho("\n🔍 Dry run - no changes made.", fg="blue", bold=True)
        conn.close()
        return

    # Confirm before updating
    if not skip_confirm:
        click.echo()
        if not click.confirm("Update these models in Open WebUI?"):
            click.secho("Cancelled.", fg="yellow")
            conn.close()
            return

    # Perform updates
    current_time = int(time.time())
    for update in updates:
        cursor.execute(
            "UPDATE model SET params = ?, updated_at = ? WHERE id = ?",
            (update["params"], current_time, update["id"]),
        )

    conn.commit()
    conn.close()

    click.secho(
        f"\n✨ Successfully updated {len(updates)} models!", fg="green", bold=True
    )
    click.secho("Refresh Open WebUI to see the changes.", fg="cyan")


@click.command()
@click.option(
    "--prompts-dir",
    default="src/prompts",
    type=click.Path(exists=True),
    help="Directory containing prompt markdown files",
)
@click.option(
    "--db-path",
    default=str(Path.home() / ".open-webui" / "webui.db"),
    type=click.Path(exists=True),
    help="Path to Open WebUI database",
)
@click.option(
    "--dry-run", is_flag=True, help="Show what would be updated without making changes"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def main(prompts_dir, db_path, dry_run, yes):
    """Sync prompt files back to Open WebUI database."""

    click.secho("\n🌿 Terrarium → Open WebUI Sync", fg="green", bold=True)
    click.secho("=" * 50, fg="green")

    sync_prompts_to_db(prompts_dir, db_path, dry_run, yes)


if __name__ == "__main__":
    main()
