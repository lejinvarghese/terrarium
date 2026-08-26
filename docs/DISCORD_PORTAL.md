# Discord Portal — Feasibility Investigation

**Status:** investigation, no implementation
**Branch:** `discord-portal`
**Question:** can the Terrarium move from 1:1 Telegram DMs to a shared Discord channel where all agents post, inter-agent traffic is visible as `@agent` mentions, and multiple humans can join?

**Verdict: yes, and it fixes something Telegram structurally cannot do.** ~400 lines of new code, two existing modules reused unchanged, no paid tier, no public endpoint. The hard part is not Discord — it is cost control on a channel where eight agents can talk to each other.

---

## 1. The decisive fact

**Telegram bots cannot see messages from other bots.** Not a privacy-mode setting, not an admin permission — the Bot API never delivers them ([Bots FAQ](https://core.telegram.org/bots/faq)). Every "inter-agent message" in the Terrarium today is therefore an _out-of-band relay_: `send_agent_message` writes to Qdrant, the recipient reads it on its next run. The conversation is real, but it is invisible and asynchronous, and no human can watch it happen.

**Discord bots do see each other's messages.** `on_message` fires for messages from bots and webhooks alike; you filter them yourself via `author.bot` / `message.webhook_id` ([discord.js guide](https://discordjs.guide/legacy/popular-topics/webhooks)). That single difference is what makes "agents talking in a channel" an actual architecture rather than a rendering trick.

So the honest framing: this is not a portal swap. Telegram is a _notification_ channel. Discord would be the Terrarium's first **shared substrate** — a place the ecosystem exists in, that humans happen to be able to read.

---

## 2. Verified against the live API

Everything below was checked, not recalled. `discord.py 2.7.1` installed cleanly into this repo's venv on Python 3.12.

| Capability                                 | Status        | Note                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Per-message persona name + avatar          | ✅            | `Webhook.send(username=…, avatar_url=…)` — verified in 2.7.1 signature                                                                                                                                                                                                                                                               |
| Webhook posts into a thread                | ✅            | `Webhook.send(thread=…)`                                                                                                                                                                                                                                                                                                             |
| Bot reads other bots' / webhooks' messages | ✅            | `Message.webhook_id` exists; gateway delivers them                                                                                                                                                                                                                                                                                   |
| Buttons / selects / modals                 | ✅            | `discord.ui.Button/Select/View/Modal`                                                                                                                                                                                                                                                                                                |
| Slash commands + autocomplete              | ✅            | `app_commands.CommandTree`                                                                                                                                                                                                                                                                                                           |
| Threads, forum channels                    | ✅            | `Message.create_thread`, `discord.ForumChannel`                                                                                                                                                                                                                                                                                      |
| `message_content` intent                   | ⚠️ privileged | Toggle in dev portal; review only above **10,000 unique reachable users** as of June 2026 ([Discord dev support](https://support-dev.discord.com/hc/en-us/articles/40281523410967-Changes-to-Privileged-Intent-Access-for-Discord-Apps)). A private server is nowhere near it. This is the #1 cause of "my bot sees empty messages". |
| Self-hosting                               | ✅            | Gateway is an _outbound_ websocket. No tunnel, no public IP, no inbound port. Better than the Cloudflare-tunnel setup already in `.env`.                                                                                                                                                                                             |
| Cost                                       | ✅            | Free. Boosts only affect upload size / audio quality.                                                                                                                                                                                                                                                                                |

**Rate limits** ([Discord docs](https://docs.discord.com/developers/topics/rate-limits)):

- 50 req/s global per token — irrelevant here.
- **5 messages / 5s per channel, shared across every webhook in that channel.** This is the binding constraint, and it kills the obvious idea that one webhook per agent buys you parallel throughput. It does not. Eight agents replying at once will queue.
- 30 req/60s per individual webhook.

Practically: a channel sustains ~1 message/sec. Agent turns take 30–300s, so you will never come close — _unless_ a loop runs away, in which case the rate limiter becomes your last line of defense rather than your first. Don't rely on it.

---

## 3. Three ways to give agents a face

### A. One bot + one webhook per agent _(recommended start)_

One token, one gateway connection, one process. Each agent gets a display name and avatar via `Webhook.send(username=..., avatar_url=...)`. The channel reads like eight distinct characters talking.

- ➕ Simplest thing that fully works. Adding a ninth agent is a dict entry.
- ➕ One central router = one place to put loop guards and the spend ceiling.
- ➖ `@nyx` is **plain text**, not a real mention. No autocomplete, no ping, no per-agent DM, no per-agent presence.

### B. One Discord application per agent

Eight bot users, eight tokens, eight gateway websockets (all fine in one asyncio process via `asyncio.gather`).

- ➕ Real `@Nyx` mentions with autocomplete. Each bot's gateway receives its own mentions — routing becomes free, no regex.
- ➕ Per-agent DMs, presence, typing indicators, slash commands. Genuinely feels like eight inhabitants.
- ➕ Decentralized: each agent decides for itself whether to answer. Closest to the README's "emergent swarm" framing.
- ➖ Eight apps to register, eight tokens, eight invites.
- ➖ **No central chokepoint.** Loop guards and budget must be enforced per-bot against shared state. This is the real cost, not the setup.

### C. Hybrid — real bot users for the 7 Claude agents, webhooks for incubator agents and system broadcasts

Incubator agents (A001–A003) are output-only; they post journals and never need to be addressed. They don't need identities that cost a token.

**Recommendation: build A, design for C.** Put a single `speak(agent, text, target)` function in `personas.py` and make the transport a per-persona field. Promoting Nyx from webhook to real bot user then changes one dict entry and one branch, not the router. Do it only if `@mention` autocomplete or per-agent DMs turn out to matter in practice — my guess is they won't for a while, because the telegram portal already routes `@sage …` by regex and it works fine.

---

## 4. What the channel actually looks like

```
#terrarium        humans + agents, the main room
#agent-chatter    inter-agent traffic — the Qdrant bulletin board, made visible
#undergrowth      forum channel: one post per incubator agent per day (journals)
#briefings        scheduled output (Cassia 07:00, Nyx Monday, Sage Sunday)
#lab              me + Casper, noise-free
```

Two mechanics worth stealing that Telegram has no answer for:

**Threads as sessions.** Today `session_manager` keys sessions on `(user_id, persona)` — one linear conversation per pair, and `/clear` is the only way to branch. On Discord, `message.create_thread()` gives every question its own thread, and the session key becomes `(thread_id, agent)`. Parallel conversations with the same agent, each with its own context, archiving themselves after inactivity. This is a strictly better fit for what sessions already are.

**Reactions as a free training signal.** A 👍 on a Nyx discovery is a labeled preference that costs the human one click. Wire `on_raw_reaction_add` → `memory_store.add_fact(category="profile")` and the ecosystem starts learning what lands without anyone writing a feedback prompt. This is the highest-value-per-line feature on the list and it does not exist on Telegram.

---

## 5. The actual risk: runaway agent conversations

Everything above is easy. This is not.

Eight agents in a channel, each able to see and answer the others, each answer costing a `claude -p` subprocess of 30–300s and real money. Nyx mentions Sage, Sage replies mentioning Nyx, and you have an unbounded spend loop running at whatever rate the channel limiter permits. Overnight, unattended.

Non-negotiable guards, in priority order:

1. **Agents answer only on explicit `@mention`.** Never on ambient chatter. Kills ~95% of the risk on its own.
2. **Hop budget per chain.** Every conversation root (thread id, or the first message id) carries a depth counter. Agent→agent replies get N=3 hops. A human message resets it to zero. Human turns are unmetered; agent turns are rationed.
3. **Per-agent cooldown** — at most one reply per agent per channel per 60s.
4. **Daily spend ceiling.** `session_manager.sessions.total_cost` is already populated from the Claude CLI's `total_cost_usd`. Sum it per day, refuse to dispatch past a threshold, post a `🛑 budget` notice. Nothing new to build.
5. **Concurrency semaphore.** Eight simultaneous `claude -p` subprocesses will bury this box. Cap at 2–3.

Guard 2 is the one people skip and regret. Build it in the first commit, not after the first surprise bill.

---

## 6. Second-order problem: whose memory is it?

`memory_store` and `add_memory` are keyed by `user_id`. In a 1:1 DM that is unambiguous. In a shared channel with lejin, Danielle, and eventually guests, "store this as a profile fact" has no obvious subject, and the failure mode is silent: Danielle's music preferences get written into lejin's profile and start shaping his morning briefings.

Fortunately `user_db` already has the mechanism — the `user_aliases` table. Register each Discord snowflake as an alias of the existing canonical user:

```python
user_db.get_db().add_user(user_id="<telegram id>", username="lejin", aliases=["discord:123456789"])
```

Memory then stays unified across portals with **zero schema change**, and `_resolve_chat_id`-style resolution already handles alias lookup. Rules on top of that:

- Message author resolves to a known user → normal read/write.
- Unknown author → episodic memory only, scoped to the channel. Never `category="profile"`.
- Agent-to-agent messages → `agent_id` scope, as today.

Worth doing before the first outsider joins the server, not after.

---

## 7. What ports over, and what breaks

| Telegram portal              | Discord                                  | Effort                                                              |
| ---------------------------- | ---------------------------------------- | ------------------------------------------------------------------- |
| `claude_engine.py`           | **unchanged**                            | 0 — it only knows about subprocesses and session ids                |
| `session_manager.py`         | **unchanged**                            | 0 — Discord snowflakes are 64-bit ints, SQLite `INTEGER` holds them |
| `InlineKeyboardMarkup`       | `discord.ui.View` + `Button`             | 1:1                                                                 |
| `CommandHandler("/bots")`    | `app_commands` slash command             | 1:1, better (autocomplete, discoverable)                            |
| `inline_query_handler`       | slash command autocomplete               | 1:1, better                                                         |
| `chat.send_action("typing")` | `async with channel.typing()`            | 1:1                                                                 |
| `_handle_bot_switch` regex   | same regex, or real mentions in option B | 1:1                                                                 |
| `_handle_incubator_message`  | same `Store.write_message` call          | 1:1                                                                 |
| 4096-char chunking           | **2000-char** chunking                   | edit a constant                                                     |
| `ParseMode.MARKDOWN`         | Discord flavored markdown                | ⚠️ see below                                                        |

**Two things genuinely break:**

_Markdown dialect._ Telegram legacy markdown is `*bold*`; Discord is `**bold**`. Agent prompts and outputs are currently written for Telegram. Discord's flavor is closer to CommonMark, so Claude's natural output will actually render _better_ — but anything hand-tuned for Telegram will look wrong. One-time pass over the agent prompts.

_Perceived latency._ A 3-minute silence after an @mention reads as broken in a chat room in a way it doesn't in a DM. Fix: post a placeholder immediately, then `message.edit()` in place when the run finishes. The telegram portal has no equivalent and doesn't need one; Discord does.

**Slash commands have a hard 3-second acknowledgement deadline**, then a 15-minute follow-up window. Any Claude-backed slash command must `await interaction.response.defer()` first, and a run exceeding 15 minutes has to post a fresh message rather than a follow-up. Plain message handlers have no such limit — which is an argument for keeping the primary interaction path as messages, exactly as it is today, and reserving slash commands for instant metadata (`/bots`, `/status`, `/memories`).

---

## 8. Proposed shape

```
src/portals/
├── core/                    # hoisted, shared by both portals
│   ├── claude_engine.py     # moved from telegram/, unchanged
│   └── session_manager.py   # moved from telegram/, unchanged
├── telegram/
│   └── bot.py               # imports from core
└── discord/
    ├── bot.py               # gateway client, command tree, message dispatch
    ├── personas.py          # agent → {webhook, avatar, color, emoji}; speak()
    ├── router.py            # @mention parse, hop budget, cooldown, spend ceiling
    └── README.md
```

Outbound side: add `send_discord_message(message, persona, channel)` to `src/mcp/server.py` **alongside** `send_telegram_message`, and a `to_channel` param to the incubator's `tools.py`. Agents then choose per message, exactly as they already choose between lejin and Danielle. No migration, no breakage, no prompt rewrite — one new tool schema and a line in each agent's Ecosystem Protocol.

**Effort**

| Phase        | Scope                                                             | Estimate              |
| ------------ | ----------------------------------------------------------------- | --------------------- |
| 0 — spike    | server + bot + webhook personas + one agent answering an @mention | ~2h, ~150 LOC         |
| 1 — parity   | slash commands, thread sessions, chunking, incubator relay        | ~1 day                |
| 2 — the loop | @mention inter-agent routing **with all five guards**             | ~1 day, the risky one |
| 3 — native   | forum journals, reactions→memory, per-agent avatars via Runware   | ~1 day                |

---

## 9. Where I'd push back

**Discord owns the log.** The README's ethos is "your bots don't live in the cloud — they live _here_, self-hosted." Telegram already compromises that for human-facing notifications, and that's a fair trade for a phone client you didn't build. But inter-agent traffic is currently 100% local, in Qdrant. Moving it to a shared channel hands the Terrarium's internal nervous system to a third party that can rate-limit it, ban it, or read it.

Mitigation, and I think it's sufficient: **Qdrant stays the source of truth; Discord is a view.** `send_agent_message` continues writing to Qdrant and additionally mirrors to `#agent-chatter`. Nothing depends on Discord being up. Discord has no vector search anyway, so it can't be the memory store even if you wanted it to be.

If the self-hosting principle turns out to matter more than convenience, **Matrix** is the ideologically consistent version — self-hostable Synapse, bots see each other's messages, per-agent identities are native, and there's a maintained Python SDK. It costs you the mobile UX and everyone else's willingness to install it. Worth knowing the option exists before committing.

**Don't retire Telegram.** They're different instruments. Telegram is push: one message, one human, on a phone, at 07:00. Discord is a room: ambient, multi-party, browsable. Cassia's morning briefing belongs in a DM. Nyx arguing with Sage about a paper belongs in a channel. Running both costs one extra MCP tool.

**Friction for Danielle.** She has a Telegram DM with Pepper today. Discord means installing an app, joining a server, and finding the right channel — and Pepper's morning message competing with agent chatter for her attention. Keep her on Telegram for the personal thread; invite her to the server as a bonus, not a migration.

---

## 10. Recommendation

Build it. Start with **option A** — one bot, one webhook per agent, `#terrarium` + `#agent-chatter`, agents responding only to explicit `@mentions`, all five guards from §5 in the first commit.

The reason isn't that Discord is a nicer chat client. It's that eight agents leaving each other notes in a vector database is a mailbox, and eight agents talking in a room where they can all hear each other is an ecosystem — and Telegram can't give you the second one at any price. That's the whole thesis of this repo, and right now it's the one thing the substrate won't allow.

Next step is the §0 spike: create the application, enable `message_content`, one webhook, one agent, one round trip. Two hours tells you whether the feel is right before committing to phase 2.

---

**Sources:** [Telegram Bots FAQ](https://core.telegram.org/bots/faq) · [Discord rate limits](https://docs.discord.com/developers/topics/rate-limits) · [Privileged intent changes, June 2026](https://support-dev.discord.com/hc/en-us/articles/40281523410967-Changes-to-Privileged-Intent-Access-for-Discord-Apps) · [Privileged intent review](https://docs.discord.com/developers/gateway/getting-started-with-privileged-intent-review) · [Webhook username/avatar override](https://github.com/Rapptz/discord.py/discussions/9202) · [Webhook message detection](https://discordjs.guide/legacy/popular-topics/webhooks)
