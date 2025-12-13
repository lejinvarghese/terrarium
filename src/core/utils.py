#!/usr/bin/env python3
"""Shared utility functions for landscapes"""

import click
from src.core.database import Observation, DatabaseManager


def get_recent_observations(
    db_manager: DatabaseManager,
    agent_id: str = None,
    limit: int = 10,
    episode_id: str = None,
):
    """Get most recent observations

    Args:
        db_manager: DatabaseManager instance for the landscape
        agent_id: Filter by specific agent (optional)
        limit: Number of observations to return
        episode_id: Filter by specific episode (optional)

    Returns:
        List of Observation objects
    """
    session = db_manager.get_session()
    query = session.query(Observation)

    if agent_id:
        query = query.filter_by(agent_id=agent_id)

    if episode_id:
        query = query.filter_by(episode_id=episode_id)

    observations = query.order_by(Observation.timestamp.desc()).limit(limit).all()
    session.close()

    return observations


def display_observations(observations, verbose: bool = False):
    """Display observations in a formatted way

    Args:
        observations: List of Observation objects
        verbose: Show full observation text
    """
    if not observations:
        click.secho("No observations found.", fg="yellow")
        return

    click.secho(f"\n{'='*80}", fg="cyan")
    click.secho(f"Found {len(observations)} observations", fg="cyan", bold=True)
    click.secho(f"{'='*80}\n", fg="cyan")

    for i, obs in enumerate(observations, 1):
        # Header
        click.secho(f"[{i}] Observation #{obs.id}", fg="yellow", bold=True)
        click.secho(
            f"    Agent: {obs.agent_id} | Episode: {obs.episode_id}", fg="white"
        )
        click.secho(
            f"    Time: {obs.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", fg="white"
        )
        click.secho(
            f"    Reward: {obs.reward:.2f}", fg="green" if obs.reward > 0 else "red"
        )

        # Action
        if obs.action_code:
            click.secho(f"    Action: {obs.action_code}", fg="blue")

        # Observation
        if verbose:
            click.secho(f"\n    Observation:", fg="cyan")
            click.secho(f"    {obs.observation_text}\n", fg="white", dim=True)
        else:
            preview = obs.observation_text[:200] if obs.observation_text else ""
            preview = preview.replace("\n", " ")
            click.secho(f"    Preview: {preview}...", fg="white", dim=True)

        click.secho("")
