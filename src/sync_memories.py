#!/usr/bin/env python3
"""Bidirectional sync between TERRARIUM_MEMORY.md and Open WebUI memories."""

import sqlite3
import time
import uuid
from pathlib import Path
import click


def get_user_id(cursor):
    """Get the first user ID from the database."""
    cursor.execute("SELECT id FROM user LIMIT 1")
    result = cursor.fetchone()
    if not result:
        raise Exception("No user found in Open WebUI database")
    return result[0]


def export_from_openwebui(db_path, output_file):
    """Export all memories from Open WebUI to markdown file."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all memories
    cursor.execute("SELECT content FROM memory ORDER BY created_at")
    memories = cursor.fetchall()
    conn.close()

    if not memories:
        click.secho("No memories found in Open WebUI.", fg="yellow")
        return

    # Read existing TERRARIUM_MEMORY.md
    output_path = Path(output_file)
    existing_content = ""
    if output_path.exists():
        with open(output_path, 'r') as f:
            existing_content = f.read()

    # Extract Open WebUI section or create new file
    openwebui_section = "\n\n---\n\n# Open WebUI Memories\n\n"
    for content, in memories:
        openwebui_section += content.strip() + "\n\n"

    # Check if we need to append or replace
    if "# Open WebUI Memories" in existing_content:
        # Replace the Open WebUI section
        parts = existing_content.split("# Open WebUI Memories")
        new_content = parts[0].rstrip() + openwebui_section
    else:
        # Append to existing file
        new_content = existing_content.rstrip() + openwebui_section

    # Write back
    with open(output_path, 'w') as f:
        f.write(new_content)

    click.secho(f"✨ Exported {len(memories)} memories to {output_file}", fg="green", bold=True)


def import_to_openwebui(db_path, input_file, skip_confirm=False):
    """Import memories from markdown file to Open WebUI."""

    input_path = Path(input_file)
    if not input_path.exists():
        click.secho(f"File not found: {input_file}", fg="red")
        return

    with open(input_path, 'r') as f:
        content = f.read()

    # Parse markdown sections (## headers as separate memories)
    sections = []
    current_section = []

    for line in content.split('\n'):
        if line.startswith('## ') and current_section:
            # Save previous section
            sections.append('\n'.join(current_section).strip())
            current_section = [line]
        else:
            current_section.append(line)

    # Add last section
    if current_section:
        sections.append('\n'.join(current_section).strip())

    # Filter out empty sections and metadata sections
    sections = [s for s in sections if s and len(s) > 20]

    if not sections:
        click.secho("No memory sections found in file.", fg="yellow")
        return

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    user_id = get_user_id(cursor)

    # Show preview
    click.secho(f"\n📝 Found {len(sections)} memory sections to sync:", fg="cyan", bold=True)
    for i, section in enumerate(sections, 1):
        preview = section[:80].replace('\n', ' ')
        click.echo(f"  {i}. {preview}...")

    if not skip_confirm:
        click.echo()
        if not click.confirm("Import these memories to Open WebUI (will replace existing)?"):
            click.secho("Cancelled.", fg="yellow")
            conn.close()
            return

    # Clear existing memories for this user
    cursor.execute("DELETE FROM memory WHERE user_id = ?", (user_id,))

    # Insert new memories
    current_time = int(time.time())
    for section in sections:
        memory_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO memory (id, user_id, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (memory_id, user_id, section, current_time, current_time)
        )

    conn.commit()
    conn.close()

    click.secho(f"\n✨ Successfully imported {len(sections)} memories to Open WebUI!", fg="green", bold=True)
    click.secho("Refresh Open WebUI to see the changes.", fg="cyan")


@click.command()
@click.option(
    '--mode',
    type=click.Choice(['export', 'import', 'both']),
    default='export',
    help='Sync direction: export (OpenWebUI→file), import (file→OpenWebUI), or both'
)
@click.option(
    '--memory-file',
    default='TERRARIUM_MEMORY.md',
    type=click.Path(),
    help='Path to memory markdown file'
)
@click.option(
    '--db-path',
    default='/home/starscream/.open-webui/webui.db',
    type=click.Path(exists=True),
    help='Path to Open WebUI database'
)
@click.option(
    '--yes', '-y',
    is_flag=True,
    help='Skip confirmation prompts'
)
def main(mode, memory_file, db_path, yes):
    """Bidirectional sync between TERRARIUM_MEMORY.md and Open WebUI memories."""

    click.secho("\n🌿 Terrarium Memory Sync", fg="green", bold=True)
    click.secho("=" * 50, fg="green")

    if mode in ['export', 'both']:
        click.secho("\n📤 Exporting from Open WebUI...", fg="blue")
        export_from_openwebui(db_path, memory_file)

    if mode in ['import', 'both']:
        click.secho("\n📥 Importing to Open WebUI...", fg="blue")
        import_to_openwebui(db_path, memory_file, yes)

    click.echo()


if __name__ == "__main__":
    main()
