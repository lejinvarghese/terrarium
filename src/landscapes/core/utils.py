import asyncio
import click

from agno.memory import MemoryManager
from agno.models.ollama import Ollama

from src.landscapes.core.constants import DATABASE, DEFAULT_MODEL_NAME


async def optimize_user_memory(user_id: str, preview: bool = False):
    """Optimize and summarize user memories to remove duplicates."""
    memory_manager = MemoryManager(
        db=DATABASE,
        model=Ollama(id=DEFAULT_MODEL_NAME),
    )

    result = await memory_manager.aoptimize_memories(
        user_id=user_id,
        apply=not preview,
    )

    if preview:
        click.secho("Preview mode - no changes saved", fg="yellow")
    else:
        click.secho("Memories optimized successfully", fg="green")

    return result


@click.command()
@click.option(
    "--user-id", type=str, default="1", help="User ID to optimize memories for"
)
@click.option("--preview", is_flag=True, help="Preview optimization without saving")
def main(user_id: str, preview: bool):
    """Optimize and deduplicate user memories."""
    asyncio.run(optimize_user_memory(user_id, preview))


if __name__ == "__main__":
    main()
