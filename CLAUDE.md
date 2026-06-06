# EMCC.Library — Claude Code Brain

> This file is for sessions working **on** EMCC.Library itself (the module's own development) AND serves as EMCC.Library's own consumer-side declaration when it dogfoods DFDU's Lattice 3.0 protocol for its own session work (see Session 1 in `tasks/sessions.md` for the first such usage).

## Live profile declaration (Library as a Lattice 3.0 consumer)

```yaml
LATTICE_PROFILE: l2-plus
AUDITOR_MODE: persona
LATTICE_BUS_ROOT: .lattice/bus
```

The bus root is relative; `SessionManager` resolves it against this repo root at session start. `.lattice/` is gitignored — bus state is per-machine, never committed. The `personas/CLAUDE.auditor.md` carry from DFDU is byte-equal (verified at Session 1 Phase B2); the Auditor judges Library work against the same canonical 116-line persona DFDU uses.

## The Library module — Codex (protocol) + Librarian (agent)

The Library module ships **two distinct things**; keep them separate.

- **Codex** is the **protocol / engine** — the *HOW*: the ingest + semantic-lint procedures, the frontmatter schema, the validators + dashboards, R-XXXXX numbering, and the cross-link graph. It defines how raw material becomes a structured, validated wiki. Canon lives in `wiki.codex/git/codex/` (spec `CODEX_BUILD_SPEC_v1_3.md`).
- **Librarian** is the **agent / persona** that *operates* Codex — the *WHO*: it ingests sources, curates pages, maintains canon, and runs the dashboards. Declared canonically in `wiki.codex/git/codex/CODEX_LIBRARIAN.md`; the `.claude/personas/CLAUDE.librarian.md` drop-in is **generated** from it (`generate_persona_dropin.py`).

This module is the **home** of both: changes to Codex (protocol) or the Librarian (persona) are made here and propagate to consumer projects (DFDU, Mentor, etc.) via Sync (`sync_from_kit.py`). Consumers never re-invent either — they vendor the engine and operate as the Librarian. Codex = the machine; the Librarian = the operator of the machine; the consuming project supplies the material + curation judgment.

## Required reading (in this order, before any code)

1. **`Index.md` — read FIRST.** File-map / routing table. Tells you where every folder + key file lives + when to load each. Avoids unnecessary searching; gives the operator + agent a shared mental model. Per portfolio spec section (a) RECOMMENDED set; `bootstrap.py` auto-emits this for new consumer projects (this Library copy was backfilled post-S002 since Library was hand-bootstrapped before the canonical-output rewrite landed).
2. `tasks/sessions.md` — most recent session entry for current operational context.
3. `tasks/todo.md` — current sprint + active tasks.
4. `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` — authoritative Codex build specification. **Spec wins** any contradiction with this file; flag conflicts rather than resolving silently. Load on demand for spec-related work (don't pre-load for unrelated tasks). (S002: relocated from Library root per spec section (b) — see `REORGANIZATION-INSTRUCTIONS.md` pattern P2.)
5. `wiki.codex/git/codex/INGEST_PROCEDURE.md` + `wiki.codex/git/codex/SEMANTIC_LINT_PROCEDURE.md` — ship **verbatim** into bootstrapped wikis' `_context/` folder. Never paraphrase, shorten, or "improve" them. Load on demand for ingest / lint work.
6. `wiki.codex/git/codex/CODEX_LIBRARIAN.md` — Librarian agent specification (the persona this module ships; S002 v1.1 extension adds 3 new ops + 5 Mentor patterns + Telegram auto-summary contract). Load on demand for Librarian-related work.
7. `wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md` — wiki build spec (what `bootstrap.py` materializes for consuming projects). Load on demand for bootstrap behavior changes.

## Routing discipline (wiki-as-memory)

> **Route, don't grep.** For a topic/domain/task question, go via `Index.md` **Zone 1** to the wiki router (`wiki.codex/git/Home.md`), load the ONE relevant page, then **expand one hop** via its `related_files:`/`[[wikilinks]]` for related context (the cross-link graph is the context engine — lexical, not vector). Drill to the Codex spec canon under `wiki.codex/git/codex/` only for authoritative precision / exact spec wording (**spec wins**). For "where does X live," use `Index.md` **Zone 2**. One canonical index per repo: **`Index.md`** (the ROOT_INDEX table below is the operating-room view; `Index.md` is the MAP + router). Standard: `EMCC/framework/18-wiki-memory-routing.md`.

## Path migrations

This module reorganized into the canonical portfolio layout in S002 (Codex v1.0 → v1.1, 2026-05-27). Module source files moved from project-root `_scripts/_template/_config/` to `Biz.Automation/wikisys.library/_*`; Codex spec docs moved from project-root markdown files to `wiki.codex/git/codex/<filename>`; `wiki.codex/` restructured into `git/`+`local/` subzones.

**If you encounter an old path reference** in a script, doc, import, or test fixture (e.g., `_scripts/` at project root, `wiki.codex/_brain_dump/`, `Sources/Raw/`, `documents/codex/`), **consult `reorganization-instructions.library.md`** for Library-specific moves. For cross-repo patterns + the index of other projects' manifests, fall back to **`REORGANIZATION-INSTRUCTIONS.md`** (master).

**Do NOT guess** at the new path. Do NOT "fix" path references by inferring from context. Use the manifests. Patterns P1–P8 (in the master) cover the eight generic transformation classes; the per-project `reorganization-instructions.library.md` records the explicit Session 1 + S002 + S003b mappings.

If a path you encounter isn't in either the patterns OR the per-project table, surface it as a finding (it may indicate an incomplete migration or a stale reference that needs explicit disposition; add as a new MI entry per `MIGRATION-ISSUES.md` convention).

When the session is run under Lattice 3.0 protocol (Library dogfooding DFDU), also:

8. `EMCC.DFDU/documents/lattice/00-README.md` — canonical Lattice 3.0 ToC
9. `EMCC.DFDU/documents/lattice/01-LATTICE-AGENT.md` — Mandatory Workflow + system prompt
10. `EMCC.DFDU/documents/lattice/05-AUDIT-REGIMES.md` — regime decision before any Level-2+ work

## ROOT_INDEX

Post-S002 / v1.1 layout. See `REORGANIZATION-INSTRUCTIONS.md` for the
machine-readable old-path → new-path manifest.

| Room | Contents | When to Load |
|---|---|---|
| `Index.md` | **File-map / routing table. Read FIRST every session.** Comprehensive list of every folder + key file + when-to-load guidance. Source of truth for "where is X?" lookups. | Every session start; updated as files/folders land |
| `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` | Authoritative Codex spec. The single canonical version. | Any spec change; clarifying scope |
| `wiki.codex/git/codex/INGEST_PROCEDURE.md` + `…/SEMANTIC_LINT_PROCEDURE.md` | Verbatim procedures shipped into bootstrapped wikis | Never edit without an explicit spec amendment |
| `wiki.codex/git/codex/CODEX_LIBRARIAN.md` | Librarian agent specification (S002 v1.1 extension: 3 new ops + 5 Mentor patterns + Telegram contract) | Persona / agent work |
| `wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md` | Wiki build spec (what bootstrap.py creates) | Bootstrap behavior changes |
| `Biz.Automation/wikisys.library/_scripts/` | Codex automation: 20 root `.py` (P1–P54-indexed) + 7 `_lib/` foundation modules + 5 new S002 audit scripts (audit_doc_pairing, audit_gitignore, route_inbox, audit_assets, audit_local_split) + 5 launcher `.ps1` | Logic / script work |
| `Biz.Automation/wikisys.library/_template/` | 26 wiki templates with `__SEP__` path encoding | Template work (Sync ships templates into consumer wikis) |
| `Biz.Automation/wikisys.library/_config/` | 5 YAML config files + README + cross_link.yaml | Config work |
| `Biz.Automation/wikisys.library/_canon/` | Library's own canon entities (roster/taxonomy/timeline/topics — Codex documenting Codex) | Canon work |
| `Biz.Automation/wikisys.library/_context/` + `_decisions/` | Runtime context rules + decision history | Reference |
| `bootstrap.py` | v1.1 canonical-output scaffolder per spec (c); `<projectname>` positional CLI | Bootstrap-behavior changes |
| `tests/` | Python stdlib `unittest` suite (~589 tests post-S002 / MI-16 retirements) | Test work; verify after any code change |
| `wiki.codex/git/` | Library's self-hosted dogfood wiki content + `git/.claude/personas/CLAUDE.librarian.md` drop-in | Reference / self-documentation |
| `wiki.codex/local/` | Library's private zone (gitignored; brain-dump / unfiled) | Operator's private |
| `.claude/personas/CLAUDE.librarian.md` | Librarian persona drop-in — **GENERATED** from `wiki.codex/git/codex/CODEX_LIBRARIAN.md` via `generate_persona_dropin.py`; do not hand-edit (drift guard: `tests/test_persona_dropin.py`). OBS-4 closure. | Persona / agent work |
| `.claude/personas/CLAUDE.auditor.md` | Auditor persona (carried verbatim from DFDU) | On-demand audit work; Lattice 3.0 Regime B |
| `tasks/*.md` | Operational state for THIS repo's build | Every session start |
| `0-Inbox/` | Triage area for in-flight planning docs | When planning a change to canon |
| `module.json` | EMCC module registration (v1.1.0) | Module hookup |
| `SOURCE-HISTORY.md` | Pointer to project-codex archived SHA + per-file move inventory | "Where did this come from?" |
| `MIGRATION-ISSUES.md` | Append-only registry (MI-01..MI-16) | Any new extraction or rename touches |
| `REORGANIZATION-INSTRUCTIONS.md` | **Master** manifest (patterns P1–P8 + audit hooks + cross-repo per-project index). | "Which pattern covers this old path?" — see also CLAUDE.md §Path migrations |
| `reorganization-instructions.library.md` | **Per-project** manifest for EMCC.Library itself (Session 1 + S002 + S003b concrete moves). Pairs with the master above per the v1.3 addendum (2026-05-28). | "Where did this Library PATH go specifically?" |

## R_STATE

R_STATE is **not** cached here — it lives in `tasks/*` as the canonical source. Read these at session start:

- **Current sprint + In Progress + Immediate + This Week + Backlog** → `tasks/todo.md`
- **Latest session detail (newest at top)** → `tasks/sessions.md` first entry
- **Architectural lessons** → `tasks/lessons.md` (Auditor NO READ per `EMCC.DFDU/documents/lattice/02-PRINCIPLES-AND-WORKFLOW.md` §B independence rule)
- **Open threads, deferred decisions** → `tasks/architect-notes.md`
- **Historical sprints** (rolled out of `todo.md` Done) → `tasks/archive.md`

## Development discipline

Codex is built under its own spec (§7 + §8): stdlib-only Python, `pathlib.Path` everywhere, Windows-safe path math, no external dependencies. Library inherits this discipline verbatim:

- **Spec wins.** If `CODEX_BUILD_SPEC_v1_3.md` contradicts anything here, the spec is authoritative — flag the conflict, don't resolve silently.
- **Stdlib only.** No `pip install`. Tests use `python -m unittest discover -s tests -t .` (matches Codex spec §7 Phase 3; matches `.github/workflows/test.yml`).
- **Verbatim discipline.** `INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` ship into bootstrapped wikis byte-identical. No paraphrasing, no "improvements," no shortening.
- **Lattice 3.0 protocol governs Library's own sessions.** When Library work is Level-2+ (cross-module touches, spec changes, etc.), Library boots a Lattice 3.0 session per the `LATTICE_PROFILE` block above. Architect plan + Auditor verdict required. Persona files in `.claude/personas/` (project-codex layout preserved per AC8; DFDU-style `personas/` flat layout is a Step 4 v1.1 follow-up).
- **Orchestrator participation (cross-session cascade).** When this session participates in an EMCC Orchestrator cascade (the Director coordinates this repo's Librarian over the `claude-peers` channel), load `.claude/modules/claude-orchestrator.md` on-demand. It covers channel participation + the rule that Codex hard rules (verbatim procedures, canon-write confirmation) still bind under the cascade. Canon: `spade0704/EMCC` → `framework/09-orchestrator-cross-session.md`.

## Out of scope (deferred to future sprints)

Per master plan `/root/.claude/plans/check-the-dfdu-project-bubbly-knuth.md` §"Out of scope" and `tasks/todo.md` "Next sprints":

- Codex v1.1 spec update (S002 / Step 4) — folder restructure per portfolio-room spec, mentor report integration, 5 deferred Librarian items
- Consumer-project wikis bootstrap (S004 / Step 6) — Aviation, Mentor, Tat, etc.
- DFDU's own `wiki/` bootstrap (S005 / Step 7)
- EMCC Steps 3+4 (orchestrator spine; Librarian Phase 2)

## Reminders

1. **Spec wins.** Flag contradictions, don't resolve silently.
2. **Verbatim means verbatim.** `INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` ship without modification.
3. **Tasks files are canonical for R_STATE.** Don't cache snapshots here; the cache drifted in project-codex and that lesson STAYs.
4. **Auditor NO READ** on `tasks/lessons.md` + `tasks/plans/`. Persona file (`personas/CLAUDE.auditor.md`) enforces this structurally; don't paraphrase the rule in dispatch prompts either.
5. **Stdlib only.** No external Python dependencies in `_scripts/` or `bootstrap.py`. Test runner is stdlib `unittest`.

## Telegram auto-summary contract (S002, 2026-05-27)

At the end of every turn that completes meaningful work (file edits committed, audit verdict received, sub-phase closed, or sprint close), in addition to the in-terminal output, call `mcp__plugin_telegram_telegram__reply` with `chat_id` from `$TELEGRAM_CHAT_ID` and a 2-4 line summary of:

  (a) what was just done,
  (b) what's next,
  (c) whether operator input is needed.

Skip for trivial turns (status checks, file reads with no state change, intermediate tool calls inside a multi-tool block).

**Soft compliance only** — if the reply tool errors or `chat_id` is unset, log and continue; never block the workflow on Telegram delivery. Operator monitors progress from phone via this channel; decision-needed escalations route to the same chat-id but with explicit `decision_needed` framing per `EMCC.DFDU/documents/lattice/13-TELEGRAM-INTEGRATION.md`. This auto-summary is the "here's where I am" complement.

Future v1.2 escalation: if compliance drifts in practice, ship Option B (Stop hook intervention) per `tasks/architect-notes.md` §S002 Telegram-auto-summary deferred-Option-B note.
