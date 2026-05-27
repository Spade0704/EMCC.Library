# Task Backlog — EMCC.Library

> Newest sprint at top. Older sprints rolled to `tasks/archive.md` once their work is complete.

## Current sprint — S001-codex-extraction (2026-05-27, OPEN)

### In Progress
- [x] Phase A — open Lattice 3.0 session + architect plan (this file + `tasks/sessions.md` + `tasks/architect-notes.md`)
- [ ] Phase B — execution (pending operator green-light on architect plan)

### Backlog (this sprint)
- [ ] B1 pre-extraction prep (A3 import verification, pyproject.toml, gitignore extension; inbox rename done in Phase A)
- [ ] B2 bootstrap files (CLAUDE.md, module.json, SOURCE-HISTORY.md, MIGRATION-ISSUES.md, README.md, .github/workflows/test.yml, requirements{,-dev}.txt, personas/CLAUDE.{auditor,librarian}.md)
- [ ] B3 relocate G1–G17 (file moves; source SHA in SOURCE-HISTORY.md)
- [ ] B4 curated migration: tasks/* + CHANGELOG.md
- [ ] B5 test infrastructure rewire + pytest green (~821 tests)
- [ ] B6 synthetic wiki bootstrap validation
- [ ] B7 EMCC consumer template flip (cross-repo)
- [ ] B8 project-codex archive disposition (cross-repo)
- [ ] B9 Auditor dispatch + verdict + session close

## Next sprints (planned)

- **S002** (master plan Step 4) — Codex v1.0 → v1.1 update. Fold portfolio-room folder spec, mentor wiki report, 5 deferred Librarian-spec items, S048-T1 findings.
- **S003** (master plan Step 5) — Telegram channel setup (operator action; `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`).
- **S004** (master plan Step 6) — Bootstrap first real consumer wikis (Aviation / Mentor / Tat per portfolio room output).
- **S005** (master plan Step 7) — Bootstrap DFDU's own `wiki/` directory.

## Cross-repo task synchronization (handled during S001 B7/B8)

- EMCC `tasks/todo.md`: unblock Step 2 (was "blocked on project-codex v1.0 SHIP"); update branch-deletion items as completed when operator confirms
- EMCC.DFDU `tasks/todo.md`: mark Library-deferred items as resolved (extraction in progress)
- project-codex `tasks/todo.md`: strikethrough items now done by Library; retain rest as reference

## Out of scope (deferred per master plan §"Out of scope")

- EMCC Step 3 (build EMCC spine — Director + Migrator agents + shell)
- EMCC Step 4 (wire DFDU + Library to EMCC via Orchestrator envelopes); Librarian Phase 2 ships here
- Guard-House / Aegis module
- EMCC.Marketing module
- Codex v1.2+ feature work beyond S002 scope
