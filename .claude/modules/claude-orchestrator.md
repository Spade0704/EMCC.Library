# claude-orchestrator.md — Orchestrator / Director cross-session module instructions

> Loaded on-demand when this session participates in an **EMCC Orchestrator cascade** (the Director, in `spade0704/EMCC`, coordinates this repo's Librarian over the `claude-peers` channel). Governs *cross-session coordination only* — it does NOT change how Codex/Librarian work. The Codex discipline (stdlib-only, verbatim procedures) remains authoritative.
>
> Module home / canon: `spade0704/EMCC` → `framework/09-orchestrator-cross-session.md`. Read that for the full contract; this file is the Library-side operational summary.

This repo's head agent is the **Librarian**. On the orchestration channel it is a peer of the EMCC **Director**. The Director sends directives (typically documentation / wiki / ingest work); the Librarian executes them under normal Codex governance and reports back.

## Channel participation (claude-peers)

- **At session start**, advertise: `set_summary` with `[ROLE:librarian][REPO:EMCC.Library] <one-line status>` so the Director can route doc/wiki work here (framework/09 §4.2).
- **Inbound:** the Director's message bodies are JSON `directive_assignment` envelopes. Parse them; log every sent/received envelope to `tasks/orchestrator-log.jsonl` (one JSON line per envelope; use EMCC's `scripts/orchestrator_log.py` pattern).
- **Outbound:** reply with a `delivery_result` envelope (status `success|partial|blocked|needs_clarification`) carrying `artifacts` and `owner_facing_summary`.
- **Transport caveat:** the cascade runs under `--dangerously-load-development-channels` + `--dangerously-skip-permissions`. Skip-permissions does **not** relax Codex hard rules — verbatim procedures and canon-write confirmation are workflow rules, not permission prompts. Honor them regardless.

## Handling a directive

1. On `directive_assignment{final:false}` — review the brief; reply `delivery_result{status:needs_clarification, clarifications:[...]}` with classification/scope questions, or acknowledge readiness.
2. On `directive_assignment{final:true}` — execute under normal Codex workflow (ingest / lint / maintain / sync as appropriate).

## Codex gates still apply

- **Sources are upstream truth; the wiki is derived.** Never reverse the flow because a directive asked for it.
- **Canon writes (`_canon/*.yaml`) require user confirmation.** A directive does not authorize a silent canon overwrite — surface contradictions, propose, wait. Escalate to the Director, who owns the Operator relationship.
- **`INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` ship verbatim.** A directive never licenses paraphrasing or shortening them.
- **Halt-loud on classification ambiguity** — reply `needs_clarification` rather than guessing a route.

## Boundaries

- This file governs cross-session coordination only. All Codex/Librarian discipline stays in the canonical specs (`CODEX_LIBRARIAN.md`, `INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`).
- The Librarian reports to the Director on the channel but is not subordinate on Codex hard rules: it never ships a canon change without confirmation, even if pushed. Escalate the conflict; do not override the rule.
