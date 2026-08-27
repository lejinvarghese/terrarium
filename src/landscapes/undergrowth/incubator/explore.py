#!/usr/bin/env python3
"""Lean exploration runner for incubator agents.

One `run_episode` == one agent's exploration for one day:

  1. Load carry-over: yesterday's journal entry + unread notes from peers.
  2. Pick a goal (persona interests, with epsilon-random tangents).
  3. Loop `steps` model turns; each turn the model may call tools
     (web_search / web_fetch / read_message / write_message), resolved over
     up to MAX_TOOL_ROUNDS rounds.
  4. Write a private journal entry — the ONE thing tomorrow's self remembers.

Everything is logged to SQLite + JSONL via Store. Pure-sync, no MCP, no asyncio.
"""

import json
import random
import time

import click
import ollama

from src.core.goals import GoalGenerator
from src.landscapes.undergrowth.incubator import prompts
from src.landscapes.undergrowth.incubator.agents import agent_registry
from src.landscapes.undergrowth.incubator.config import (
    DEFAULT_EPISODE_STEPS,
    DEFAULT_EPSILON,
    FOLLOWUP_PROMPTS,
    LANDSCAPE_DISPLAY_NAME,
    MAX_TOOL_ROUNDS,
    MODEL_NAME,
    MODEL_OPTIONS,
    REFLECTION_PROMPT,
)
from src.landscapes.undergrowth.incubator.store import Store
from src.landscapes.undergrowth.incubator.tools import Toolbox


def _peer_roster(agent_id: str) -> str:
    peers = []
    for pid in agent_registry.list_agents():
        if pid == agent_id:
            continue
        c = agent_registry.get_config(pid)
        peers.append(f"  - {c['name']} ({pid}): {c.get('archetype', 'explorer')}")
    return "\n".join(peers) if peers else "  (you are the only agent so far)"


def _build_system_prompt(cfg: dict, delivery: str | None = "telegram") -> str:
    """Identity + exploration drive + tools + wherever findings are sent."""
    peers = (
        "OTHER AGENTS IN THE UNDERGROWTH (leave them notes with write_message):\n"
        + _peer_roster(cfg["id"])
    )
    return prompts.compose(cfg, task=prompts.EXPLORE, delivery=delivery, extra=peers)


def _build_chat_prompt(cfg: dict, delivery: str | None = None, extra: str = "") -> str:
    """Identity + conversational framing. No drive, no exploration toolset."""
    return prompts.compose(cfg, task=prompts.CHAT, delivery=delivery, extra=extra)


def _build_kickoff(objective: str, carry: dict | None, inbox: list[dict]) -> str:
    parts = [f"Today's exploration goal: {objective}"]
    if carry:
        parts.append(
            f"\nYesterday ({carry['day']}) you wrote in your journal:\n\"{carry['summary']}\"\n"
            "Continue from there — build on it, don't start over."
        )
    if inbox:
        notes = "\n".join(
            f"  - {m['from_name']} ({m['from_agent']}): {m['content']}" for m in inbox
        )
        parts.append(f"\nNotes waiting for you:\n{notes}")
    parts.append("\nBegin exploring now. Reach for a tool on your very first move.")
    return "\n".join(parts)


def _as_message_dict(msg) -> dict:
    """Normalise an Ollama response message into a plain dict for history."""
    d = {"role": "assistant", "content": msg.get("content") or ""}
    tcs = msg.get("tool_calls")
    if tcs:
        d["tool_calls"] = tcs
    return d


CONVERSE_TOOLS = ("web_search", "web_fetch", "note_to_self")
CHAT_MEMORY_TURNS = 6


def _background(carry: dict | None) -> str:
    """What the agent has been exploring lately, as background rather than an agenda."""
    if not carry or not carry.get("summary"):
        return ""
    return (
        "\n\nWhat you've been exploring lately (background — bring it up only if it's "
        f"relevant, never lead with it):\n{carry['summary'][:400]}"
    )


def _prior_turns(past: list[dict]) -> list[dict]:
    """Earlier exchanges, replayed as conversation so the agent remembers them."""
    turns = []
    for chat in past:
        turns.append({"role": "user", "content": chat["objective"].removeprefix("[chat] ")})
        turns.append({"role": "assistant", "content": chat["summary"]})
    return turns


class _Recorder:
    """Logs every step of one episode and keeps the running index."""

    def __init__(self, store: Store, ep_id: int, agent_id: str, verbose: bool = False):
        self.store, self.ep_id, self.agent_id, self.verbose = store, ep_id, agent_id, verbose
        self.idx = 0
        self.tool_calls = 0

    def thought(self, content: str) -> None:
        self.store.log_step(self.ep_id, self.agent_id, self.idx, "thought", content=content)
        self.idx += 1
        if self.verbose:
            click.secho(f"  💭 {content.strip()[:200]}", fg="white")

    def tool(self, name: str, args: dict, result: str) -> None:
        self.store.log_step(
            self.ep_id,
            self.agent_id,
            self.idx,
            "tool",
            tool_name=name,
            tool_args=json.dumps(args),
            tool_result=result,
        )
        self.idx += 1
        self.tool_calls += 1
        if self.verbose:
            click.secho(f"  🔧 {name}({args}) → {result[:120].strip()}…", fg="blue")

    def summary(self, content: str) -> None:
        self.store.log_step(self.ep_id, self.agent_id, self.idx, "summary", content=content)
        self.idx += 1


def _turn(history: list[dict], toolbox: Toolbox, model_name: str, rec: _Recorder) -> bool:
    """One model turn plus any tools it calls. False when it has nothing more to do."""
    try:
        resp = ollama.chat(
            model=model_name, messages=history, tools=toolbox.schemas, options=MODEL_OPTIONS
        )
    except Exception as e:
        click.secho(f"  model error: {e}", fg="red")
        rec.thought(f"[model error] {e}")
        return False

    msg = resp["message"]
    history.append(_as_message_dict(msg))
    if msg.get("content"):
        rec.thought(msg["content"])

    tool_calls = msg.get("tool_calls")
    if not tool_calls:
        return False

    for call in tool_calls:
        name = call.function.name
        args = dict(call.function.arguments or {})
        result = toolbox.call(name, args)
        rec.tool(name, args, result)
        history.append({"role": "tool", "content": result, "tool_name": name})
    return True


def _final_text(history: list[dict], model_name: str) -> str:
    """The agent's answer, forced into prose if it only ever called tools."""
    for msg in reversed(history):
        if msg["role"] == "assistant" and msg.get("content", "").strip():
            return msg["content"].strip()

    history.append({"role": "user", "content": "Now answer me, in plain words."})
    resp = ollama.chat(model=model_name, messages=history, options=MODEL_OPTIONS)
    return (resp["message"].get("content") or "").strip()


def _announce(cfg, agent_id, model_name, objective, carry, inbox) -> None:
    """Console header for an interactive episode."""
    click.secho(f"\n{'=' * 62}", fg="cyan")
    click.secho(f"{cfg['name']} ({agent_id})  ·  {model_name}", fg="green", bold=True)
    click.secho(f"Goal: {objective}", fg="yellow")
    if carry:
        click.secho(f"Carrying over from {carry['day']}", fg="magenta")
    if inbox:
        click.secho(f"{len(inbox)} note(s) from peers", fg="magenta")
    click.secho(f"{'=' * 62}\n", fg="cyan")


def _explore_loop(
    history: list[dict],
    toolbox: Toolbox,
    model_name: str,
    rec: "_Recorder",
    steps: int,
    verbose: bool,
) -> None:
    """One episode's exploration: each step resolves its tool calls, then a nudge."""
    for step in range(1, steps + 1):
        if verbose:
            click.secho(f"[step {step}/{steps}]", fg="cyan")
        for _ in range(MAX_TOOL_ROUNDS):
            if not _turn(history, toolbox, model_name, rec):
                break
        if step < steps:
            history.append({"role": "user", "content": random.choice(FOLLOWUP_PROMPTS)})


def _report(summary: str, duration: float, tool_calls: int, ep_id: int) -> None:
    """Console footer for an interactive episode."""
    click.secho(f"\n📔 {summary}\n", fg="bright_yellow")
    click.secho(
        f"done in {duration:.0f}s · {tool_calls} tool calls · episode {ep_id}\n",
        fg="green",
        bold=True,
    )


def _write_journal(history: list[dict], model_name: str, verbose: bool) -> str:
    """The one thing tomorrow's self remembers. No tools; we want prose."""
    if verbose:
        click.secho("[reflection] writing journal entry…", fg="cyan")
    history.append({"role": "user", "content": REFLECTION_PROMPT})
    try:
        resp = ollama.chat(model=model_name, messages=history, options=MODEL_OPTIONS)
        return (resp["message"].get("content") or "").strip()
    except Exception as e:
        return f"[reflection failed: {e}]"


def converse(
    agent_id: str,
    message: str,
    context: str = "",
    delivery: str | None = None,
    model_name: str = MODEL_NAME,
    store: Store | None = None,
    max_rounds: int = MAX_TOOL_ROUNDS,
) -> dict:
    """Answer a message as this agent.

    A conversation, not an exploration: no goal, no carry-over journal, no
    followup prompts, no reflection, and a toolbox that can research but cannot
    reply anywhere other than here. The return value is the reply itself.
    """
    cfg = agent_registry.get_config(agent_id)
    owns_store = store is None
    store = store or Store()
    toolbox = Toolbox(store, agent_id, cfg["name"], allow=CONVERSE_TOOLS)

    carry = store.last_journal(agent_id)
    past = store.recent_chats(agent_id, limit=CHAT_MEMORY_TURNS)

    ep_id = store.start_episode(agent_id, cfg["name"], f"[chat] {message[:120]}")
    history = [
        {
            "role": "system",
            "content": _build_chat_prompt(cfg, delivery, context) + _background(carry),
        },
        *_prior_turns(past),
        {"role": "user", "content": message},
    ]

    rec = _Recorder(store, ep_id, agent_id)
    start = time.time()

    for _ in range(max_rounds):
        if not _turn(history, toolbox, model_name, rec):
            break

    reply = _final_text(history, model_name)
    store.end_episode(ep_id, rec.idx, rec.tool_calls, reply)
    if owns_store:
        store.close()

    return {
        "agent_id": agent_id,
        "agent_name": cfg["name"],
        "episode_id": ep_id,
        "reply": reply,
        "tool_calls": rec.tool_calls,
        "duration_s": round(time.time() - start, 1),
    }


def run_episode(
    agent_id: str,
    objective: str | None = None,
    steps: int = DEFAULT_EPISODE_STEPS,
    epsilon: float = DEFAULT_EPSILON,
    model_name: str = MODEL_NAME,
    store: Store | None = None,
    verbose: bool = True,
    delivery: str | None = "telegram",
) -> dict:
    """Run one daily exploration episode for an agent. Returns a summary dict."""
    cfg = agent_registry.get_config(agent_id)
    owns_store = store is None
    store = store or Store()
    from datetime import date

    day = date.today().isoformat()

    if objective is None:
        objective = GoalGenerator(epsilon).generate(cfg)

    carry = store.last_journal(agent_id, before_day=day) or store.last_journal(agent_id)
    inbox = store.read_messages(agent_id, mark_read=True)
    toolbox = Toolbox(store, agent_id, cfg["name"])

    if verbose:
        _announce(cfg, agent_id, model_name, objective, carry, inbox)

    ep_id = store.start_episode(agent_id, cfg["name"], objective, day)
    history = [
        {"role": "system", "content": _build_system_prompt(cfg, delivery)},
        {"role": "user", "content": _build_kickoff(objective, carry, inbox)},
    ]

    rec = _Recorder(store, ep_id, agent_id, verbose)
    start = time.time()

    _explore_loop(history, toolbox, model_name, rec, steps, verbose)

    summary = _write_journal(history, model_name, verbose)
    store.set_journal(agent_id, day, summary)
    rec.summary(summary)
    store.end_episode(ep_id, steps, rec.tool_calls, summary)

    duration = time.time() - start
    if verbose:
        _report(summary, duration, rec.tool_calls, ep_id)

    if owns_store:
        store.close()

    return {
        "agent_id": agent_id,
        "agent_name": cfg["name"],
        "episode_id": ep_id,
        "objective": objective,
        "steps": steps,
        "tool_calls": rec.tool_calls,
        "duration_s": round(duration, 1),
        "summary": summary,
    }


@click.command()
@click.option(
    "--agent",
    "-a",
    type=click.Choice(agent_registry.list_agents()),
    required=True,
    help="Agent to run (e.g. A001)",
)
@click.option("--objective", "-o", default=None, help="Explicit goal (auto-generated if omitted)")
@click.option("--steps", "-s", default=DEFAULT_EPISODE_STEPS, help="Model turns this episode")
@click.option("--epsilon", "-e", default=DEFAULT_EPSILON, type=float, help="Exploration rate 0-1")
@click.option("--model", "-m", default=MODEL_NAME, help="Ollama model id")
def explore(agent, objective, steps, epsilon, model):
    """Run a single agent's daily exploration episode."""
    click.secho(f"\n{LANDSCAPE_DISPLAY_NAME} · incubator", fg="cyan", bold=True)
    run_episode(agent_id=agent, objective=objective, steps=steps, epsilon=epsilon, model_name=model)


if __name__ == "__main__":
    explore()
