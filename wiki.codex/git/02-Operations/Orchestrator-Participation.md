---
title: "Orchestrator Participation"
type: framework
visibility: internal
completion: 60
status: solid
last_updated: 2026-06-18
dependencies: []
public_pair: null
blocking_questions: []
canon_sources:
  - ".claude/modules/claude-orchestrator.md"
unverified_claims: []
---

# Orchestrator Participation

How EMCC.Library's **Librarian** behaves when the EMCC **Director** coordinates it inside a cross-session cascade (documentation / wiki / ingest work routed from the portfolio orchestrator).

> Canonical source: `.claude/modules/claude-orchestrator.md` (this repo) + `spade0704/EMCC` → `framework/09-orchestrator-cross-session.md`. Codex protocol canon (`CODEX_LIBRARIAN.md`, `INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`) is unchanged by this — participation is a layer on top.

## On the channel

When run under the cascade, the Librarian is a peer of the Director over `claude-peers`:
- Advertises `[ROLE:librarian][REPO:EMCC.Library]` at startup so the Director routes doc/wiki work here.
- Receives `directive_assignment` envelopes; replies `delivery_result` (success / partial / blocked / needs_clarification).
- Logs every envelope to `tasks/orchestrator-log.jsonl`.

## Codex gates still bind under the cascade

A directive never licenses bypassing Codex hard rules. Even under `--dangerously-skip-permissions` (used on the channel — these are workflow rules, not permission prompts):
- **Sources are upstream truth; the wiki is derived** — never reverse the flow.
- **Canon writes (`_canon/*.yaml`) require user confirmation** — surface contradictions, propose, wait; escalate to the Director (who owns the Operator relationship).
- **`INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` ship verbatim** — no paraphrasing or shortening, ever.
- **Halt-loud on classification ambiguity** — reply `needs_clarification` rather than guessing a route.

The Librarian reports to the Director on the channel but is not subordinate on Codex rules: it never ships a canon change without confirmation, even if pushed.

## Module-Connector declaration (how EMCC discovers this module)

Before the Director can route doc/wiki work here, EMCC has to **discover** the module
and know which agent and keywords it owns. That discovery is driven from a single source
of truth: the **connector block** this repo self-declares in `module.json`. Canon for the
contract is `spade0704/EMCC` → `framework/21-module-connector-contract.md`.

The block (committed in PR #56):

```json
"connector": {
  "slug": "library",
  "target_agent": "Librarian",
  "routing_keywords": ["docs", "doc", "wiki", "ingest", "document",
                       "curate", "lint", "knowledge", "codex"]
}
```

- **`slug`** — the module's stable short identifier for dashboard discovery.
- **`target_agent`** — the agent the Director routes matched intent to (here, the **Librarian**).
- **`routing_keywords`** — the intent words that route operator requests to this module.

EMCC derives both dashboard discovery and Director routing from this one declaration, so
the module owns its own routing identity rather than EMCC hard-coding it. The keyword set
matches what the Librarian actually does — doc/wiki/ingest/curate/lint/knowledge/codex —
so a "document the recent build" or "ingest this source" intent lands here.
