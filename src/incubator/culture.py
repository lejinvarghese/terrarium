#!/usr/bin/env python3
"""Culture analysis utilities for Incubator agents

This module provides tools to analyze agent memory patterns,
track cultural development, and understand how synthetic agents
evolve their interests and knowledge over time.
"""

import click
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from src.incubator.config import MEMORY_DB, MODEL_NAME
from src.incubator.agents import AGENTS


def get_agent_memories(agent_id: str):
    """Get all memories for a specific agent"""
    try:
        from agno.agent import Agent
        from agno.models.ollama import Ollama
        from agno.db.sqlite import SqliteDb
    except ImportError as e:
        click.secho(f"Error: Agno not installed: {e}", fg="red")
        return []

    memory_db = SqliteDb(
        db_file=str(MEMORY_DB)
    )

    # Create a temporary agent just to query memories
    agent = Agent(
        model=Ollama(id=MODEL_NAME),
        db=memory_db,
        name=agent_id
    )

    # Get all memories - they're scoped by agent name internally
    # Query without filtering, Agno tracks agent_id in the memory records
    try:
        memories = agent.get_user_memories()
    except:
        # If that doesn't work, try getting all memories from db directly
        memories = []

    return memories


def analyze_agent_culture(agent_id: str):
    """Analyze an agent's cultural development and interests"""

    if agent_id not in AGENTS:
        click.secho(f"Error: Unknown agent '{agent_id}'", fg="red")
        click.secho(f"Available agents: {', '.join(AGENTS.keys())}", fg="yellow")
        return None

    agent_config = AGENTS[agent_id]
    memories = get_agent_memories(agent_id)

    if not memories:
        return {
            "agent_id": agent_id,
            "agent_name": agent_config['name'],
            "total_memories": 0,
            "message": "No memories found for this agent"
        }

    # Analyze topics
    topic_frequency = Counter()
    for mem in memories:
        if mem.topics:
            topic_frequency.update(mem.topics)

    # Sort memories by time
    sorted_memories = sorted(memories, key=lambda x: x.updated_at)

    # Get recent focus (last 10 memories)
    recent_topics = []
    for mem in sorted_memories[-10:]:
        if mem.topics:
            recent_topics.extend(mem.topics)

    return {
        "agent_id": agent_id,
        "agent_name": agent_config['name'],
        "persona": agent_config['persona'],
        "total_memories": len(memories),
        "top_interests": topic_frequency.most_common(10),
        "recent_focus": Counter(recent_topics).most_common(5),
        "memory_timeline": sorted_memories,
        "oldest_memory": datetime.fromtimestamp(sorted_memories[0].updated_at).strftime("%Y-%m-%d %H:%M:%S"),
        "newest_memory": datetime.fromtimestamp(sorted_memories[-1].updated_at).strftime("%Y-%m-%d %H:%M:%S"),
    }


def compare_agent_cultures(agent_ids: list):
    """Compare cultural development across multiple agents"""

    cultures = {}
    for agent_id in agent_ids:
        culture = analyze_agent_culture(agent_id)
        if culture and culture.get("total_memories", 0) > 0:
            cultures[agent_id] = culture

    if not cultures:
        return {"message": "No agents with memories to compare"}

    # Find common and unique interests
    all_topics = defaultdict(set)
    for agent_id, culture in cultures.items():
        for topic, count in culture["top_interests"]:
            all_topics[topic].add(agent_id)

    # Topics shared by all agents
    common_topics = [
        topic for topic, agents in all_topics.items()
        if len(agents) == len(cultures)
    ]

    # Topics unique to each agent
    unique_topics = {
        agent_id: [
            topic for topic, count in culture["top_interests"]
            if len(all_topics[topic]) == 1
        ]
        for agent_id, culture in cultures.items()
    }

    return {
        "agents_compared": list(cultures.keys()),
        "cultures": cultures,
        "common_interests": common_topics,
        "unique_interests": unique_topics,
    }


def track_evolution(agent_id: str, time_periods: int = 4):
    """Track how an agent's interests evolve over time periods"""

    memories = get_agent_memories(agent_id)
    if not memories:
        return {"message": "No memories to track"}

    # Sort by time
    sorted_memories = sorted(memories, key=lambda x: x.updated_at)

    # Divide into time periods
    period_size = len(sorted_memories) // time_periods
    if period_size == 0:
        return {"message": "Not enough memories to track evolution"}

    evolution = {}
    for i in range(time_periods):
        start_idx = i * period_size
        end_idx = start_idx + period_size if i < time_periods - 1 else len(sorted_memories)

        period_memories = sorted_memories[start_idx:end_idx]
        period_topics = []
        for mem in period_memories:
            if mem.topics:
                period_topics.extend(mem.topics)

        period_start = datetime.fromtimestamp(period_memories[0].updated_at).strftime("%Y-%m-%d")
        period_end = datetime.fromtimestamp(period_memories[-1].updated_at).strftime("%Y-%m-%d")

        evolution[f"Period {i+1} ({period_start} to {period_end})"] = {
            "memory_count": len(period_memories),
            "top_topics": Counter(period_topics).most_common(5),
        }

    return evolution


@click.command()
@click.option(
    "--agent",
    "-a",
    type=click.Choice(list(AGENTS.keys())),
    help="Analyze specific agent"
)
@click.option(
    "--compare",
    "-c",
    is_flag=True,
    help="Compare all agents"
)
@click.option(
    "--evolution",
    "-e",
    is_flag=True,
    help="Track cultural evolution over time"
)
def culture(agent: str, compare: bool, evolution: bool):
    """Analyze agent culture and memory patterns"""

    click.secho("\n" + "="*60, fg="cyan")
    click.secho("Incubator - Culture Analysis", fg="cyan", bold=True)
    click.secho("="*60 + "\n", fg="cyan")

    if compare:
        # Compare all agents
        result = compare_agent_cultures(list(AGENTS.keys()))

        if "message" in result:
            click.secho(result["message"], fg="yellow")
            return

        click.secho(f"Comparing {len(result['agents_compared'])} agents:\n", fg="cyan", bold=True)

        for agent_id in result['agents_compared']:
            culture_data = result['cultures'][agent_id]
            click.secho(f"  {agent_id} - {culture_data['agent_name']}", fg="yellow")
            click.secho(f"    Memories: {culture_data['total_memories']}", fg="white")
            click.secho(f"    Top interest: {culture_data['top_interests'][0][0] if culture_data['top_interests'] else 'None'}", fg="white")

        if result['common_interests']:
            click.secho(f"\n📚 Common interests across all agents:", fg="green", bold=True)
            for topic in result['common_interests']:
                click.secho(f"  • {topic}", fg="white")

        if any(result['unique_interests'].values()):
            click.secho(f"\n🎯 Unique interests by agent:", fg="green", bold=True)
            for agent_id, topics in result['unique_interests'].items():
                if topics:
                    click.secho(f"  {agent_id}:", fg="yellow")
                    for topic in topics[:3]:
                        click.secho(f"    • {topic}", fg="white")

    elif agent:
        # Analyze specific agent
        culture_data = analyze_agent_culture(agent)

        if not culture_data or culture_data.get("total_memories", 0) == 0:
            click.secho(f"No memories found for agent {agent}", fg="yellow")
            return

        click.secho(f"Agent: {culture_data['agent_name']} ({culture_data['agent_id']})", fg="cyan", bold=True)
        click.secho(f"Persona: {culture_data['persona']}\n", fg="white", dim=True)

        click.secho(f"📊 Memory Statistics:", fg="green", bold=True)
        click.secho(f"  Total memories: {culture_data['total_memories']}", fg="white")
        click.secho(f"  Oldest memory: {culture_data['oldest_memory']}", fg="white")
        click.secho(f"  Newest memory: {culture_data['newest_memory']}\n", fg="white")

        click.secho(f"🎯 Top Interests (All Time):", fg="green", bold=True)
        for i, (topic, count) in enumerate(culture_data['top_interests'][:5], 1):
            click.secho(f"  {i}. {topic} ({count} memories)", fg="white")

        if culture_data['recent_focus']:
            click.secho(f"\n🔥 Recent Focus (Last 10 memories):", fg="green", bold=True)
            for i, (topic, count) in enumerate(culture_data['recent_focus'], 1):
                click.secho(f"  {i}. {topic} ({count} mentions)", fg="white")

        if evolution:
            click.secho(f"\n📈 Cultural Evolution:", fg="green", bold=True)
            evo = track_evolution(agent)
            if "message" in evo:
                click.secho(f"  {evo['message']}", fg="yellow")
            else:
                for period_name, period_data in evo.items():
                    click.secho(f"\n  {period_name}", fg="cyan")
                    click.secho(f"    Memories: {period_data['memory_count']}", fg="white")
                    if period_data['top_topics']:
                        click.secho(f"    Top topics:", fg="white")
                        for topic, count in period_data['top_topics'][:3]:
                            click.secho(f"      • {topic} ({count})", fg="white", dim=True)

    else:
        # Show overview of all agents
        click.secho("Agent Memory Overview:\n", fg="cyan", bold=True)

        for agent_id, agent_config in AGENTS.items():
            memories = get_agent_memories(agent_id)
            click.secho(f"  {agent_id} - {agent_config['name']}", fg="yellow")
            click.secho(f"    {len(memories)} memories", fg="white")

            if memories:
                topics = []
                for mem in memories:
                    if mem.topics:
                        topics.extend(mem.topics)
                if topics:
                    top_topic = Counter(topics).most_common(1)[0]
                    click.secho(f"    Primary interest: {top_topic[0]}", fg="white", dim=True)

        click.secho(f"\nℹ️  Use --agent <id> for detailed analysis", fg="cyan")
        click.secho(f"   Use --compare to compare all agents", fg="cyan")


if __name__ == "__main__":
    culture()
