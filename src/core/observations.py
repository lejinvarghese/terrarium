#!/usr/bin/env python3
"""View observations - landscape-agnostic"""

import click
from src.core.utils import get_recent_observations, display_observations
from src.core.database import DatabaseManager
from src.core.landscapes import get_observations_path, list_landscapes


@click.command()
@click.option(
    "--landscape",
    "-l",
    type=click.Choice(list_landscapes()),
    required=True,
    help="Landscape to query",
)
@click.option("--agent", "-a", help="Filter by agent ID")
@click.option("--episode", "-e", help="Filter by episode ID")
@click.option("--limit", "-n", default=10, help="Number of observations to show")
@click.option("--verbose", "-v", is_flag=True, help="Show full observation text")
def observations(landscape: str, agent: str, episode: str, limit: int, verbose: bool):
    """View recent observations"""

    click.secho("\n" + "=" * 60, fg="cyan")
    click.secho(f"{landscape.title()} - Recent Observations", fg="cyan", bold=True)
    click.secho("=" * 60 + "\n", fg="cyan")

    db_manager = DatabaseManager(get_observations_path(landscape))
    obs = get_recent_observations(
        db_manager, agent_id=agent, episode_id=episode, limit=limit
    )
    display_observations(obs, verbose=verbose)


if __name__ == "__main__":
    observations()
