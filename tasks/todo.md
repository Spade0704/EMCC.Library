# Task Backlog — EMCC.Library

> Newest sprint at top. Older sprints rolled to `tasks/archive.md` once their work is complete.

## Past sprint — S002-codex-v1.1-update (2026-05-27, CLOSED)

### Done
- [x] Phase A — open Session 2 + bank architect plan + Mentor spec correction
- [x] B1 .gitignore wiki.*/local/ extension + baseline assertions
- [x] B2 module source → Biz.Automation/wikisys.library/_* (65 git mv)
- [x] B3 Codex spec docs → wiki.codex/git/codex/ (10 git mv)
- [x] B4 wiki.codex/ internal restructure (git+local split; MI-14 + MI-15)
- [x] B5a path-lookup rebases (bootstrap.py + sync_from_kit + 10 test files)
- [x] B5b bootstrap.py full canonical-output rewrite per spec (c) + 21 new tests + 88 v1.0-shape tests retired (MI-16)
- [x] B6 5 new audit scripts (P0+P1) + FINDING #1 fix + 34 new tests
- [x] B7 CODEX_LIBRARIAN.md +174 lines (3 ops + 5 Mentor patterns + Telegram contract) + persona mirror + CLAUDE.md updates
- [x] B8 REORGANIZATION-INSTRUCTIONS.md flip (27 rows ⏳→✅) + S002-internal callers section
- [x] B9 module.json v1.1.0 + README + CLAUDE.md Path-migrations pointer + MI-10/11/12/13 dispositions
- [x] B10 Auditor dispatch — verdict `pass` with 4 info observations (OBS-2/OBS-3 fixed inline; OBS-1/OBS-4 deferred to architect-notes)

→ See `tasks/sessions.md` Session 2 CLOSED entry for full close record.
→ See `tasks/architect-notes.md` §S002 for the architect plan, Auditor observations, and deferred items.

## Next sprints (planned)

- **S003** (master plan Step 5) — Telegram channel boot (operator action; bot exists at chat_id 1415844818).
- **S004** (master plan Step 6) — bootstrap real consumer wikis (Aviation / Tat / etc.) on v1.1 canonical scaffold. Retires MI-16 deferral. Decides sync_from_kit's post-v1.1 delivery target.
- **S005** (master plan Step 7) — bootstrap DFDU's own `wiki/` directory.

---

## Past sprint — S001-codex-extraction (2026-05-27, CLOSED)

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
