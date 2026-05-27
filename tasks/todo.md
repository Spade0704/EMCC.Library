# Task Backlog — EMCC.Library

> Newest sprint at top. Older sprints rolled to `tasks/archive.md` once their work is complete.

## Past sprint — S004-mentor-v1.1-migration (2026-05-28, CLOSED)

Cross-repo sprint with `spade0704/Project-Mentor`. Mentor migrated v1.0 → v1.1 canonical layout; Library shipped MI-16 + MI-18 closures + walker fix + manifest update.

### Done (Library side)
- [x] Phase A — open Session 4 + bank architect plan §S004 + Mentor pre-migration anchor SHA
- [x] Phase C — `sync_from_kit.py` v1.1 contract rewrite (MI-16 closure); consumer-name auto-discovery; 17 tests pass + 4 new TestConsumerDiscovery cases; spec doc §4.2 updated
- [x] Phase D — MI-18 canon-lookup marker-walk: `_lib/frontmatter.py::find_canon_dir` + `find_decisions_dir` + extended `_find_wiki_root` with v1.1 consumer marker; 12 scripts retrofitted; 9 new tests; MI-18 registered + RESOLVED
- [x] Phase E — end-to-end validation + carry fixes: `find_config_dir` extension (7 more scripts retrofitted), `markdown.py::iter_content_pages` raw/ exclusion, `update_dashboards.py` CLI arg (MI-17 partial), REORGANIZATION-INSTRUCTIONS Mentor per-project moves + cross-repo Library moves section
- [x] Phase F — Auditor dispatch verdict `concerns` (5 findings); F10 MI-16 registry header RESOLVED-disposition fixed inline; F11 + F12 fixed cross-repo on Mentor side
- [x] S004 CLOSE record on `tasks/sessions.md`

### Cross-repo commits (Mentor side, branch `claude/s004-mentor-v1.1-migration-na3hg`)
- 12 commits: Phase A (`caafc8a`) + B1-B10 (`a966d27` → `f8e919a`) + close (`42dd4fc`) + F4 (`4e985bc`) + CLOSE record (`867c03b`)
- Mentor at v1.1 canonical layout post-S004; baseline parity vs M001 verified (27 pages / 0 contradictions / 54% cross-link)

### Migration issues resolved
- **MI-16** RESOLVED — sync_from_kit v1.1 contract rewrite
- **MI-18** RESOLVED — canon/decisions/config-lookup marker-walk

→ See `tasks/sessions.md` Session 4 CLOSED entry for full close record + Auditor findings table.
→ See `tasks/architect-notes.md` §S004 for the architect plan, risk register, AC1-AC10.
→ See `REORGANIZATION-INSTRUCTIONS.md` §Mentor for per-project moves manifest.

## Carried + Open (post-S004)

### Library-side
- [ ] **MI-17 full closure** — 16 scripts still use hardcoded `WIKI_ROOT = Path(__file__).resolve().parent.parent`. S004 closed `_lib/frontmatter.py::WIKI_ROOT` + `update_dashboards.py` CLI arg only. Per-script CLI argparse support pending. Tests don't currently cover these scripts' default-WIKI_ROOT behavior; add coverage as part of follow-up.
- [ ] **MI-12** (historical curation, S001 carry) — Codex-class entries from project-codex's tasks/* (5,223 lines) + CHANGELOG.md (337KB) classifying for migration. Low priority.
- [ ] **OBS-1** (S002 carry, Auditor info) — AC12 sweep methodology under-counts; explicit runtime allow-list for legitimate verbatim/template encoding. Audit-method sprint TBD.
- [ ] **OBS-4** (S002 carry, Auditor info) — persona-mirror drift risk between `.claude/personas/CLAUDE.librarian.md` and `wiki.codex/git/codex/CODEX_LIBRARIAN.md`. Persona-discipline sprint TBD.
- [ ] **Library `_dashboards/` location** — consider migrating from `wikisys.library/_dashboards/` to `wiki.codex/git/_dashboards/` (content-side; matches Mentor convention from S004 F12). Operator decision; default path math change is invasive.
- [ ] **portfolio-folder-structure-spec.md line 881 outdated** — reads "Mentor was greenfield, no migration needed" — false post-S004. Carry to next spec touch.

### Cross-repo (Mentor-side; tracked here for visibility)
- [ ] Mentor SPLIT pairing for Karpathy + Cherny — backfill stub R-XXXXX on next publish event
- [ ] Mentor R-00008 cross-link surface (M001 follow-up)
- [ ] Mentor JP CheatSheet canonicalization (operator decision)

## Next sprints (planned)

- **S003** (master plan Step 5) — Telegram channel boot. **Partially done**: Option A (local-only Windows env vars) configured by operator post-S002. Cloud-CC remainder: no action required (network policy blocks `api.telegram.org`; soft-compliance contract honored).
- **S005** (master plan Step 7) — bootstrap DFDU's own `wiki/` directory.
- **S006+** — remaining consumer wikis (Aviation / Tat / iSommelier / eddyandwolff / aviation-career / EMCC / EMCC.DFDU) on v1.1 canonical scaffold. No migration needed — greenfield via `bootstrap.py <projectname> --full`.

---

## Past sprint — Post-S002 stabilization (2026-05-27, CLOSED) — PR #5 → #10

Six-PR cleanup arc between S002 close and S004 open. All merged to `main`. See `tasks/sessions.md` "Post-S002 stabilization" entry for full close record + per-PR table.

### Done

- [x] PR #5 — Index.md backfill + CLAUDE.md read-order update (`8735f76`)
- [x] PR #6 — OBS-4 urgent fix: Librarian persona template sync (`ceb4f1d`)
- [x] PR #7 — S002c Library staleness audit (READ-ONLY); 157-line report (`403e860`)
- [x] PR #8 — S003a Library staleness cleanup phase 1 (path refresh + v1.1 alignment) (`f8feca1`)
- [x] PR #9 — S003b Library staleness cleanup phase 2 (archive banners + relocations) (`8c2193c`)
- [x] PR #10 — MI-17 full resolution: `find_wiki_root()` across all 17 scripts (`6b14cb6`)
- [x] PR #11 — Post-MI-17 housekeeping: tasks/{sessions,todo,lessons}.md updated (`bf36e9d`)

### MIs touched this arc

- **MI-17** — Resolved (PR #10). Marker-walk pattern lifted into `_lib/frontmatter.py::find_wiki_root()` public API; 17 scripts converted. (S004 D superseded the content-side resolution with install-root + companion `find_*_dir()` helpers; this arc was the intermediate step.)
- **MI-18** — Surfaced (post-PR-#10), Resolved in S004 D.

---

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
