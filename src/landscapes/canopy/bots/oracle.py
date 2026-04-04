"""Oracle - Strategic foresight and pattern recognition bot

Oracle operates from a birds-eye view, analyzing upcoming events and generating
preparatory tasks. Specializes in:
- Meeting preparation and briefing
- Trend analysis and pattern recognition
- Strategic planning support
- Proactive research tasks
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict
from .base import CanopyBot, Task, TaskOutcome, Reflection


class Oracle(CanopyBot):
    """Strategic foresight bot with pattern recognition"""

    def __init__(self, memory_manager, mcp_client=None):
        super().__init__(
            bot_id="oracle",
            name="Oracle",
            role="Strategic foresight and pattern recognition",
            memory_manager=memory_manager,
        )
        self.mcp = mcp_client  # MCP client for tool access

    def generate_tasks(self, context: Dict) -> List[Task]:
        """Generate strategic tasks based on context

        Analyzes:
        - Upcoming calendar events (next 24-48h)
        - Active memory patterns
        - Current time/weather
        - Recent Telegram activity

        Generates:
        - Meeting preparation briefs
        - Research tasks for upcoming events
        - Pattern analysis tasks
        - Strategic planning tasks
        """
        tasks = []
        now = datetime.now()

        # Load active patterns for context
        active_patterns = self.get_active_memory()

        # 1. Check calendar for upcoming events
        calendar_events = context.get("calendar_events", [])
        for event in calendar_events:
            # Generate prep task for events within 4 hours
            event_time = event.get("start_time")
            if event_time and (event_time - now) < timedelta(hours=4):
                task = Task(
                    id=str(uuid.uuid4()),
                    bot_id=self.bot_id,
                    title=f"Prepare brief for: {event.get('title', 'Event')}",
                    description=f"Research and summarize key info for upcoming meeting: {event.get('title')}",
                    priority=0.8,  # High priority - event soon
                    context={
                        "event": event,
                        "type": "meeting_prep",
                        "deadline": event_time,
                    },
                    created_at=now,
                    deadline=event_time - timedelta(minutes=30),
                )
                tasks.append(task)

        # 2. Pattern recognition tasks (weekly)
        last_pattern_analysis = context.get("last_pattern_analysis")
        if not last_pattern_analysis or (now - last_pattern_analysis) > timedelta(
            days=7
        ):
            task = Task(
                id=str(uuid.uuid4()),
                bot_id=self.bot_id,
                title="Weekly pattern analysis",
                description="Analyze memory patterns and extract strategic insights",
                priority=0.5,
                context={"type": "pattern_analysis", "timeframe": "7_days"},
                created_at=now,
            )
            tasks.append(task)

        # 3. Proactive research based on patterns
        # Check if any HOT patterns suggest needed research
        for pattern_str in active_patterns[:3]:  # Top 3 HOT patterns
            if "research" in pattern_str.lower() or "investigate" in pattern_str.lower():
                # Extract research topic from pattern
                task = Task(
                    id=str(uuid.uuid4()),
                    bot_id=self.bot_id,
                    title="Follow-up research",
                    description=f"Research topic from pattern: {pattern_str[:100]}",
                    priority=0.6,
                    context={"type": "research", "trigger_pattern": pattern_str},
                    created_at=now,
                )
                tasks.append(task)

        return tasks

    def execute_task(self, task: Task) -> TaskOutcome:
        """Execute task using MCP tools"""
        start_time = datetime.now()
        tools_used = []
        errors = []
        output = ""
        success = False

        try:
            task_type = task.context.get("type")

            if task_type == "meeting_prep":
                output, tools = self._prepare_meeting_brief(task)
                tools_used.extend(tools)
                success = True

            elif task_type == "pattern_analysis":
                output, tools = self._analyze_patterns(task)
                tools_used.extend(tools)
                success = True

            elif task_type == "research":
                output, tools = self._conduct_research(task)
                tools_used.extend(tools)
                success = True

            else:
                errors.append(f"Unknown task type: {task_type}")

        except Exception as e:
            errors.append(str(e))
            self.logger.error(f"Task execution failed: {e}", exc_info=True)

        duration = (datetime.now() - start_time).total_seconds()

        return TaskOutcome(
            task=task,
            success=success,
            output=output,
            tools_used=tools_used,
            duration_seconds=duration,
            errors=errors,
            completed_at=datetime.now(),
        )

    def _prepare_meeting_brief(self, task: Task) -> tuple[str, List[str]]:
        """Prepare a brief for an upcoming meeting"""
        event = task.context.get("event", {})
        event_title = event.get("title", "Event")
        tools_used = []

        brief_parts = [f"# Meeting Brief: {event_title}\n"]

        # 1. Get current time context
        if self.mcp:
            try:
                time_result = self.mcp.call_tool(
                    "mcp__google-calendar__get-current-time", {}
                )
                brief_parts.append(f"Current time: {time_result}")
                tools_used.append("get-current-time")
            except Exception as e:
                self.logger.warning(f"Failed to get time: {e}")

        # 2. Search for related patterns
        patterns = self.memory.search_patterns(event_title)
        if patterns:
            brief_parts.append("\n## Related Patterns:")
            for p in patterns[:3]:
                brief_parts.append(f"- {p.content}")
            tools_used.append("memory-search")

        # 3. Web research (if time permits)
        if task.deadline and (task.deadline - datetime.now()) > timedelta(hours=1):
            if self.mcp:
                try:
                    search_result = self.mcp.call_tool(
                        "mcp__tavily__tavily-search",
                        {"query": event_title, "max_results": 3},
                    )
                    brief_parts.append(f"\n## Research:\n{search_result}")
                    tools_used.append("tavily-search")
                except Exception as e:
                    self.logger.warning(f"Research failed: {e}")

        brief = "\n".join(brief_parts)

        # Send brief via Telegram
        if self.mcp:
            try:
                message = self.format_telegram_message(brief)
                self.mcp.call_tool(
                    "mcp__terrarium__send_telegram_message", {"message": message}
                )
                tools_used.append("send-telegram")
            except Exception as e:
                self.logger.error(f"Failed to send Telegram message: {e}")

        return brief, tools_used

    def _analyze_patterns(self, task: Task) -> tuple[str, List[str]]:
        """Analyze memory patterns and extract insights"""
        tools_used = ["memory-stats", "memory-search"]

        # Get tier stats
        stats = self.memory.get_stats()

        analysis = [
            "# Weekly Pattern Analysis\n",
            f"Memory tiers: HOT={stats['hot']}, WARM={stats['warm']}, COLD={stats['cold']}\n",
        ]

        # Get HOT patterns
        hot_patterns = self.memory.get_active_patterns(
            include_hot=True, include_warm=False
        )
        if hot_patterns:
            analysis.append("\n## Critical Patterns (HOT):")
            for p in hot_patterns:
                analysis.append(
                    f"- {p.content} (used {p.use_count}x, last: {p.last_used.strftime('%Y-%m-%d')})"
                )

        # Send analysis via Telegram
        if self.mcp:
            try:
                message = self.format_telegram_message("\n".join(analysis))
                self.mcp.call_tool(
                    "mcp__terrarium__send_telegram_message", {"message": message}
                )
                tools_used.append("send-telegram")
            except Exception as e:
                self.logger.error(f"Failed to send analysis: {e}")

        return "\n".join(analysis), tools_used

    def _conduct_research(self, task: Task) -> tuple[str, List[str]]:
        """Conduct research based on pattern trigger"""
        trigger_pattern = task.context.get("trigger_pattern", "")
        tools_used = []

        research_output = [f"# Research Task\n", f"Trigger: {trigger_pattern}\n"]

        # Extract search query from trigger
        # Simple approach: use pattern content as query
        if self.mcp:
            try:
                search_result = self.mcp.call_tool(
                    "mcp__tavily__tavily-search",
                    {"query": trigger_pattern[:200], "max_results": 5},
                )
                research_output.append(f"\n## Findings:\n{search_result}")
                tools_used.append("tavily-search")
            except Exception as e:
                self.logger.error(f"Research failed: {e}")
                research_output.append(f"\nResearch failed: {e}")

        return "\n".join(research_output), tools_used

    def _extract_patterns(self, outcome: TaskOutcome, reflection: Reflection):
        """Extract Oracle-specific patterns from task outcome"""
        super()._extract_patterns(outcome, reflection)

        # Meeting prep patterns
        if outcome.task.context.get("type") == "meeting_prep":
            if outcome.success:
                reflection.insights.append(
                    f"Successfully prepared brief for meeting type: {outcome.task.context.get('event', {}).get('title', 'unknown')}"
                )

                # If prep took too long, note it
                if outcome.duration_seconds > 120:
                    reflection.corrections.append(
                        f"Meeting prep took {outcome.duration_seconds:.0f}s - optimize research scope"
                    )

        # Pattern analysis insights
        if outcome.task.context.get("type") == "pattern_analysis":
            reflection.insights.append("Completed weekly pattern review")
