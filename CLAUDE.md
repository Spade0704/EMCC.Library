# EMCC.Library — Claude Code Brain

> This file is for sessions working **on** EMCC.Library itself (the module's own development) AND serves as EMCC.Library's own consumer-side declaration when it dogfoods DFDU's Lattice 3.0 protocol for its own session work (see Session 1 in `tasks/sessions.md` for the first such usage).

## Live profile declaration (Library as a Lattice 3.0 consumer)

```yaml
LATTICE_PROFILE: l2-plus
AUDITOR_MODE: persona
LATTICE_BUS_ROOT: .lattice/bus
```

The bus root is relative; `SessionManager` resolves it against this repo root at session start. `.lattice/` is gitignored — bus state is per-machine, never committed. The `personas/CLAUDE.auditor.md` carry from DFDU is byte-equal (verified at Session 1 Phase B2); the Auditor judges Library work against the same canonical 116-line persona DFDU uses.

## Required reading (in this order, before any code)

1. `CODEX_BUILD_SPEC_v1_3.md` — authoritative Codex build specification. **Spec wins** any contradiction with this file; flag conflicts rather than resolving silently.
2. `INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` — ship **verbatim** into bootstrapped wikis' `_context/` folder. Never paraphrase, shorten, or "improve" them.
3. `CODEX_LIBRARIAN.md` — Librarian agent specification (the persona this module ships).
4. `PROJECT_WIKI_BUILD_SPEC.md` — wiki build spec (what `bootstrap.py` materializes for consuming projects).
5. `tasks/sessions.md` — most recent session entry for current operational context.

When the session is run under Lattice 3.0 protocol (Library dogfooding DFDU), also:

6. `EMCC.DFDU/documents/lattice/00-README.md` — canonical Lattice 3.0 ToC
7. `EMCC.DFDU/documents/lattice/01-LATTICE-AGENT.md` — Mandatory Workflow + system prompt
8. `EMCC.DFDU/documents/lattice/05-AUDIT-REGIMES.md` — regime decision before any Level-2+ work

## ROOT_INDEX

| Room | Contents | When to Load |
|---|---|---|
| `CODEX_BUILD_SPEC_v1_3.md` | Authoritative Codex spec. The single canonical version (v1_1/v1_2 stay archived in `spade0704/project-codex`). | Any spec change; clarifying scope |
| `INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` | Verbatim procedures shipped into bootstrapped wikis | Never edit without an explicit spec amendment |
| `CODEX_LIBRARIAN.md` | Librarian agent specification | Persona / agent work |
| `PROJECT_WIKI_BUILD_SPEC.md` | Wiki build spec (what bootstrap.py creates) | Bootstrap behavior changes |
| `_scripts/` | Codex automation (P1–P54-indexed; `_lib/` foundation; `launchers/` operator scripts) | Logic / script work |
| `_template/`, `_config/` | Templates + config YAMLs bootstrap copies into new wikis | Template / config changes |
| `tests/` | Python stdlib `unittest` suite (~821 tests post-extraction) | Test work; verify after any code change |
| `wiki.codex/` | Library's self-hosted dogfood wiki (Codex documenting Codex). Folder layout still in pre-Step-4 form. | Reference / self-documentation |
| `.claude/personas/CLAUDE.librarian.md` | Librarian persona (canonical) | Persona / agent work |
| `.claude/personas/CLAUDE.auditor.md` | Auditor persona (carried verbatim from DFDU) | On-demand audit work; Lattice 3.0 Regime B |
| `tasks/*.md` | Operational state for THIS repo's build | Every session start |
| `0-Inbox/` | Triage area for in-flight planning docs | When planning a change to canon |
| `module.json` | EMCC module registration | Module hookup |
| `SOURCE-HISTORY.md` | Pointer to project-codex archived SHA + per-file move inventory | "Where did this come from?" |
| `MIGRATION-ISSUES.md` | Append-only registry (MI-01..MI-08 + A1/A2/A3) | Any new extraction or rename touches |
| `Obsidian-Setup-Guide.md`, `codex-build-plan.html`, `documents/codex/` | Consumer guidance + build progress + Codex docs (PDF / cheatsheet) | Consumer-facing reference |

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
