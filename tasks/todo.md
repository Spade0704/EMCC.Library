# Task Backlog — EMCC.Library

> Newest sprint at top. Older sprints rolled to `tasks/archive.md` once their work is complete.

## Current sprint — S001-codex-extraction (2026-05-27, CLOSED)

### Done
- [x] Phase A — open Lattice 3.0 session + architect plan
- [x] B1 pre-extraction prep (A3 import verification + .gitignore extension; pyproject.toml deferred to MI-13)
- [x] B2 bootstrap files (CLAUDE.md / module.json / SOURCE-HISTORY.md / MIGRATION-ISSUES.md / README.md / .github/workflows/test.yml / .claude/personas/CLAUDE.auditor.md)
- [x] B3 relocate G1–G17 (148-file commit; A2 revoked in-flight; personas at .claude/personas/)
- [x] B4 (reduced scope) — v1.1-backlog.md only; historical curation deferred to MI-12
- [x] B5 test infrastructure verified — 615 tests / 611 pass / 3 fail (2 baseline + 1 MI-10) / 1 skip
- [x] B6 synthetic wiki bootstrap validation — all 15 validators OK / 0 errors
- [x] B7 EMCC consumer template flip (cross-repo `b10c766`)
- [x] B8 project-codex archive disposition (cross-repo `53b4fa9`)
- [x] B9 Auditor dispatch — verdict `pass` with 3 observations (F-1 fixed inline; F-2 → MI-13; F-3 implicit Step 4)

→ See `tasks/sessions.md` Session 1 CLOSED entry for full close record.

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
