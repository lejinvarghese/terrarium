#!/usr/bin/env python3
"""Culture analysis - landscape-agnostic"""

import click
import sqlite3
from collections import Counter, defaultdict, namedtuple
from datetime import datetime

from src.core.landscapes import get_memory_path, list_landscapes

Memory = namedtuple(
    "Memory",
    ["memory_id", "memory", "input", "agent_id", "user_id", "topics", "updated_at"],
)


class CultureAnalyzer:
    """Analyze agent memory patterns and culture"""

    def __init__(self, landscape_name: str):
        self.landscape = landscape_name
        self.memory_path = get_memory_path(landscape_name)

    def _get_connection(self):
        return sqlite3.connect(str(self.memory_path))

    def get_all_agent_ids(self):
        """Get list of all agent_ids in memory database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT agent_id FROM agno_memories")
        agent_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return agent_ids

    def get_agent_memories(self, agent_id: str):
        """Get all memories for specific agent"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT memory_id, memory, input, agent_id, user_id, topics, updated_at FROM agno_memories WHERE agent_id = ?",
                (agent_id.lower(),),
            )

            rows = cursor.fetchall()
            conn.close()

            memories = []
            for row in rows:
                import json

                mem = Memory(
                    memory_id=row[0],
                    memory=json.loads(row[1]) if row[1] else "",
                    input=row[2],
                    agent_id=row[3],
                    user_id=row[4],
                    topics=json.loads(row[5]) if row[5] else [],
                    updated_at=row[6],
                )
                memories.append(mem)

            return memories

        except Exception as e:
            click.secho(f"Error querying memories: {e}", fg="red")
            return []

    def analyze_agent(self, agent_id: str):
        """Analyze agent's cultural development"""
        memories = self.get_agent_memories(agent_id)

        if not memories:
            return {"agent_id": agent_id, "total_memories": 0}

        topic_frequency = Counter()
        for mem in memories:
            if mem.topics:
                topic_frequency.update(mem.topics)

        sorted_memories = sorted(memories, key=lambda x: x.updated_at)

        recent_topics = []
        for mem in sorted_memories[-10:]:
            if mem.topics:
                recent_topics.extend(mem.topics)

        return {
            "agent_id": agent_id,
            "total_memories": len(memories),
            "top_interests": topic_frequency.most_common(10),
            "recent_focus": Counter(recent_topics).most_common(5),
            "oldest_memory": datetime.fromtimestamp(
                sorted_memories[0].updated_at
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "newest_memory": datetime.fromtimestamp(
                sorted_memories[-1].updated_at
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }

    def compare_agents(self, agent_ids: list):
        """Compare cultural development across agents"""
        cultures = {}
        for agent_id in agent_ids:
            culture = self.analyze_agent(agent_id)
            if culture.get("total_memories", 0) > 0:
                cultures[agent_id] = culture

        if not cultures:
            return {"message": "No agents with memories to compare"}

        all_topics = defaultdict(set)
        for agent_id, culture in cultures.items():
            for topic, count in culture["top_interests"]:
                all_topics[topic].add(agent_id)

        common_topics = [
            topic
            for topic, agents in all_topics.items()
            if len(agents) == len(cultures)
        ]

        unique_topics = {
            agent_id: [
                topic
                for topic, count in culture["top_interests"]
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

    def track_evolution(self, agent_id: str, time_periods: int = 4):
        """Track how agent interests evolve over time"""
        memories = self.get_agent_memories(agent_id)
        if not memories:
            return {"message": "No memories to track"}

        sorted_memories = sorted(memories, key=lambda x: x.updated_at)

        period_size = len(sorted_memories) // time_periods
        if period_size == 0:
            return {"message": "Not enough memories to track evolution"}

        evolution = {}
        for i in range(time_periods):
            start_idx = i * period_size
            end_idx = (
                start_idx + period_size
                if i < time_periods - 1
                else len(sorted_memories)
            )

            period_memories = sorted_memories[start_idx:end_idx]
            period_topics = []
            for mem in period_memories:
                if mem.topics:
                    period_topics.extend(mem.topics)

            period_start = datetime.fromtimestamp(
                period_memories[0].updated_at
            ).strftime("%Y-%m-%d")
            period_end = datetime.fromtimestamp(
                period_memories[-1].updated_at
            ).strftime("%Y-%m-%d")

            evolution[f"Period {i+1} ({period_start} to {period_end})"] = {
                "memory_count": len(period_memories),
                "top_topics": Counter(period_topics).most_common(5),
            }

        return evolution

    def display_overview(self):
        """Display overview of all agents"""
        click.secho("Agent Memory Overview:\n", fg="cyan", bold=True)

        for agent_id in self.get_all_agent_ids():
            memories = self.get_agent_memories(agent_id)
            click.secho(f"  {agent_id}", fg="yellow")
            click.secho(f"    {len(memories)} memories", fg="white")

            if memories:
                topics = []
                for mem in memories:
                    if mem.topics:
                        topics.extend(mem.topics)
                if topics:
                    top_topic = Counter(topics).most_common(1)[0]
                    click.secho(
                        f"    Primary interest: {top_topic[0]}", fg="white", dim=True
                    )

        click.secho(f"\nℹ️  Use --agent <id> for detailed analysis", fg="cyan")
        click.secho(f"   Use --compare to compare all agents", fg="cyan")

    def display_agent_detail(self, agent_id: str, show_evolution: bool = False):
        """Display detailed analysis for specific agent"""
        culture_data = self.analyze_agent(agent_id)

        if culture_data.get("total_memories", 0) == 0:
            click.secho(f"No memories found for agent {agent_id}", fg="yellow")
            return

        click.secho(f"Agent: {culture_data['agent_id']}", fg="cyan", bold=True)

        click.secho(f"\nMemory Statistics:", fg="green", bold=True)
        click.secho(f"  Total memories: {culture_data['total_memories']}", fg="white")
        click.secho(f"  Oldest memory: {culture_data['oldest_memory']}", fg="white")
        click.secho(f"  Newest memory: {culture_data['newest_memory']}\n", fg="white")

        click.secho(f"Top Interests (All Time):", fg="green", bold=True)
        for i, (topic, count) in enumerate(culture_data["top_interests"][:5], 1):
            click.secho(f"  {i}. {topic} ({count} memories)", fg="white")

        if culture_data["recent_focus"]:
            click.secho(f"\nRecent Focus (Last 10 memories):", fg="green", bold=True)
            for i, (topic, count) in enumerate(culture_data["recent_focus"], 1):
                click.secho(f"  {i}. {topic} ({count} mentions)", fg="white")

        if show_evolution:
            click.secho(f"\nCultural Evolution:", fg="green", bold=True)
            evo = self.track_evolution(agent_id)
            if "message" in evo:
                click.secho(f"  {evo['message']}", fg="yellow")
            else:
                for period_name, period_data in evo.items():
                    click.secho(f"\n  {period_name}", fg="cyan")
                    click.secho(
                        f"    Memories: {period_data['memory_count']}", fg="white"
                    )
                    if period_data["top_topics"]:
                        click.secho(f"    Top topics:", fg="white")
                        for topic, count in period_data["top_topics"][:3]:
                            click.secho(
                                f"      • {topic} ({count})", fg="white", dim=True
                            )

    def display_comparison(self):
        """Display comparison across all agents"""
        result = self.compare_agents(self.get_all_agent_ids())

        if "message" in result:
            click.secho(result["message"], fg="yellow")
            return

        click.secho(
            f"Comparing {len(result['agents_compared'])} agents:\n",
            fg="cyan",
            bold=True,
        )

        for agent_id in result["agents_compared"]:
            culture_data = result["cultures"][agent_id]
            click.secho(f"  {agent_id}", fg="yellow")
            click.secho(f"    Memories: {culture_data['total_memories']}", fg="white")
            click.secho(
                f"    Top interest: {culture_data['top_interests'][0][0] if culture_data['top_interests'] else 'None'}",
                fg="white",
            )

        if result["common_interests"]:
            click.secho(f"\nCommon interests across all agents:", fg="green", bold=True)
            for topic in result["common_interests"]:
                click.secho(f"  • {topic}", fg="white")

        if any(result["unique_interests"].values()):
            click.secho(f"\nUnique interests by agent:", fg="green", bold=True)
            for agent_id, topics in result["unique_interests"].items():
                if topics:
                    click.secho(f"  {agent_id}:", fg="yellow")
                    for topic in topics[:3]:
                        click.secho(f"    • {topic}", fg="white")


@click.command()
@click.option(
    "--landscape",
    "-l",
    type=click.Choice(list_landscapes()),
    required=True,
    help="Landscape to analyze",
)
@click.option("--agent", "-a", help="Analyze specific agent")
@click.option("--compare", "-c", is_flag=True, help="Compare all agents")
@click.option("--evolution", "-e", is_flag=True, help="Track cultural evolution")
def culture(landscape: str, agent: str, compare: bool, evolution: bool):
    """Analyze agent culture and memory patterns"""

    click.secho("\n" + "=" * 60, fg="cyan")
    click.secho(f"{landscape.title()} - Culture Analysis", fg="cyan", bold=True)
    click.secho("=" * 60 + "\n", fg="cyan")

    analyzer = CultureAnalyzer(landscape)

    if not analyzer.get_all_agent_ids():
        click.secho("No agents with memories found", fg="yellow")
        return

    if compare:
        analyzer.display_comparison()
    elif agent:
        analyzer.display_agent_detail(agent, show_evolution=evolution)
    else:
        analyzer.display_overview()


if __name__ == "__main__":
    culture()
