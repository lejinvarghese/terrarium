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


def _build_system_prompt(agent_config: dict) -> str:
    return (
        agent_config["persona_template"]
        + "\n\nOTHER AGENTS IN THE UNDERGROWTH (leave them notes with write_message):\n"
        + _peer_roster(agent_config["id"])
    )


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
        parts.append(f"\nNotes waiting for you from other agents:\n{notes}")
    parts.append("\nBegin exploring now. Reach for a tool on your very first move.")
    return "\n".join(parts)


def _as_message_dict(msg) -> dict:
    """Normalise an Ollama response message into a plain dict for history."""
    d = {"role": "assistant", "content": msg.get("content") or ""}
    tcs = msg.get("tool_calls")
    if tcs:
        d["tool_calls"] = tcs
    return d


def run_episode(
    agent_id: str,
    objective: str | None = None,
    steps: int = DEFAULT_EPISODE_STEPS,
    epsilon: float = DEFAULT_EPSILON,
    model_name: str = MODEL_NAME,
    store: Store | None = None,
    verbose: bool = True,
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
        click.secho(f"\n{'=' * 62}", fg="cyan")
        click.secho(f"{cfg['name']} ({agent_id})  ·  {model_name}", fg="green", bold=True)
        click.secho(f"Goal: {objective}", fg="yellow")
        if carry:
            click.secho(f"Carrying over from {carry['day']}", fg="magenta")
        if inbox:
            click.secho(f"{len(inbox)} note(s) from peers", fg="magenta")
        click.secho(f"{'=' * 62}\n", fg="cyan")

    ep_id = store.start_episode(agent_id, cfg["name"], objective, day)
    history = [
        {"role": "system", "content": _build_system_prompt(cfg)},
        {"role": "user", "content": _build_kickoff(objective, carry, inbox)},
    ]

    idx = 0
    tool_calls = 0
    start = time.time()

    for step in range(1, steps + 1):
        if verbose:
            click.secho(f"[step {step}/{steps}]", fg="cyan")
        for _ in range(MAX_TOOL_ROUNDS):
            try:
                resp = ollama.chat(
                    model=model_name, messages=history, tools=Toolbox.schemas, options=MODEL_OPTIONS
                )
            except Exception as e:
                click.secho(f"  model error: {e}", fg="red")
                store.log_step(ep_id, agent_id, idx, "thought", content=f"[model error] {e}")
                idx += 1
                break
            msg = resp["message"]
            history.append(_as_message_dict(msg))

            if msg.get("content"):
                store.log_step(ep_id, agent_id, idx, "thought", content=msg["content"])
                idx += 1
                if verbose:
                    click.secho(f"  💭 {msg['content'].strip()[:200]}", fg="white")

            tcs = msg.get("tool_calls")
            if not tcs:
                break
            for tc in tcs:
                name = tc.function.name
                args = dict(tc.function.arguments or {})
                result = toolbox.call(name, args)
                tool_calls += 1
                store.log_step(
                    ep_id,
                    agent_id,
                    idx,
                    "tool",
                    tool_name=name,
                    tool_args=json.dumps(args),
                    tool_result=result,
                )
                idx += 1
                if verbose:
                    click.secho(f"  🔧 {name}({args}) → {result[:120].strip()}…", fg="blue")
                history.append({"role": "tool", "content": result, "tool_name": name})

        if step < steps:
            history.append({"role": "user", "content": random.choice(FOLLOWUP_PROMPTS)})

    # Reflection → journal (no tools; we want prose)
    if verbose:
        click.secho("[reflection] writing journal entry…", fg="cyan")
    history.append({"role": "user", "content": REFLECTION_PROMPT})
    try:
        resp = ollama.chat(model=model_name, messages=history, options=MODEL_OPTIONS)
        summary = (resp["message"].get("content") or "").strip()
    except Exception as e:
        summary = f"[reflection failed: {e}]"
    store.set_journal(agent_id, day, summary)
    store.log_step(ep_id, agent_id, idx, "summary", content=summary)
    store.end_episode(ep_id, steps, tool_calls, summary)

    duration = time.time() - start
    if verbose:
        click.secho(f"\n📔 {summary}\n", fg="bright_yellow")
        click.secho(
            f"done in {duration:.0f}s · {tool_calls} tool calls · episode {ep_id}\n",
            fg="green",
            bold=True,
        )

    if owns_store:
        store.close()

    return {
        "agent_id": agent_id,
        "agent_name": cfg["name"],
        "episode_id": ep_id,
        "objective": objective,
        "steps": steps,
        "tool_calls": tool_calls,
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
