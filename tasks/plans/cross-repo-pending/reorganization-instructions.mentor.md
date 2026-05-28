# reorganization-instructions.mentor.md

> **Status:** PENDING migration to Mentor's own repo root.
>
> This file is the per-project path-migration manifest for **Project-Mentor**
> (`claude-prompts/mentor` repo). It is parked in EMCC.Library at
> `tasks/plans/cross-repo-pending/` because Mentor wasn't open during the
> S005-prep sprint that introduced the
> `reorganization-instructions.<projectname>.md` convention (2026-05-28).
>
> **Next Mentor session must:**
>
> 1. `git mv` (or copy + remove) this file to `<mentor-root>/reorganization-instructions.mentor.md`.
> 2. Update Mentor's `CLAUDE.md` Path migrations pointer to reference the
>    new per-project file (currently points at `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md`).
> 3. Delete this Library-side copy after the cross-repo move lands.
> 4. Remove the Mentor entry from
>    `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md` §"Per-project files"
>    table → "Pending migration" list (move to "Migrated" list).

> **Scope:** Per-project path-migration manifest for **Project-Mentor**
> only. Cross-repo patterns (P1–P8), audit-hook contract, and master index
> live in `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md`.

---

## Mentor — per-project moves (S004 / 2026-05-28)

**Pre-S004 state:** Mentor was bootstrapped 2026-05-25 via Codex S048-T1 BEFORE S002 v1.1 spec landed 2026-05-27. On-disk shape was v1.0 (`<wiki>/_scripts/`, `<wiki>/_canon/`, etc. at wiki root). Spec line 881 "no migration needed" was outdated at S004 open; this manifest section + S004 close fix the disconnect.

**S004 moves** — branch `claude/s004-mentor-v1.1-migration-na3hg`, Mentor pre-migration SHA `932e3ee`. Cross-repo sprint with Library MI-16 + MI-18 closure.

| Old path (Mentor pre-S004) | New path (Mentor post-S004) | Pattern | Status |
|---|---|---|---|
| `wiki/_scripts/` (27 files: 20 P-indexed + 7 _lib/) | `Biz.Automation/wikisys.mentor/_scripts/` | P1 | ✅ Done in S004 B2 |
| `wiki/_canon/` (6 yaml + README) | `Biz.Automation/wikisys.mentor/_canon/` | P1 | ✅ Done in S004 B3 |
| `wiki/_config/` (2 yaml: concept_coverage, cross_link) | `Biz.Automation/wikisys.mentor/_config/` | P1 | ✅ Done in S004 B3 |
| `wiki/_context/` (4 md: CLAUDE_CONTEXT_RULES, CODEX_LIBRARIAN, INGEST, LINT) | `Biz.Automation/wikisys.mentor/_context/` | P1 | ✅ Done in S004 B3 |
| `wiki/_decisions/` (ingest-log + reference-last-checked + README — canon-decision files) | `Biz.Automation/wikisys.mentor/_decisions/` | P1 | ✅ Done in S004 B3 + B9 (subset moved to root tasks/) |
| `wiki/_decisions/{todo,sessions,lessons,archive}.md` (Boris operational state) | `tasks/{todo,sessions,lessons,archive}.md` | P8 + B9 split | ✅ Done in S004 B9 |
| `wiki/_dashboards/` (15 generated md) | `Biz.Automation/wikisys.mentor/_dashboards/` | P1 | ✅ Done in S004 B3 |
| `wiki/_sources/raw/` (60 files: youtube/web/x/legacy-*) | `wiki.mentor/git/raw/` | P3 | ✅ Done in S004 B4 |
| `wiki/_brain_dump/` (README only — Library template) | `wiki.mentor/local/ideas/` (gitignored; README dropped) | P4 | ✅ Done in S004 B5 |
| `wiki/00-Start-Here/` (6 md) | `wiki.mentor/git/00-Start-Here/` | P5 | ✅ Done in S004 B6 |
| `wiki/01-Authorities/` (4 md: Karpathy, Cherny, Nate-Herk, Printing-Press) | `wiki.mentor/git/01-Authorities/` | P5 | ✅ Done in S004 B6 |
| `wiki/02-References/` (9 md: R-00001..R-00008 + REGISTRY) | `wiki.mentor/git/02-References/` | P5 | ✅ Done in S004 B6 |
| `wiki/03-Topics/` (empty) | `wiki.mentor/git/03-Topics/.gitkeep` | P5 | ✅ Done in S004 B6 |
| `wiki/04-Contributing/` (7 md: Authority-Content-Policy, File-Routing, Mentor-Conventions, Mentor-Ingestion-Notes, Project-Continuity, Style-Guide, Update-Cascade) | `wiki.mentor/git/04-Contributing/` | P5 | ✅ Done in S004 B6 |
| `wiki/Home.md` | `wiki.mentor/git/Home.md` | P5 | ✅ Done in S004 B6 |
| `wiki_legacy_2026-05-25/` (project-root; previously gitignored 7.2MB) | `wiki.mentor/git/_archive/wiki_legacy_2026-05-25/` + banner README (tracked) | P5 + operator D3 | ✅ Done in S004 B6 |
| `wiki/_confidential/` (Confidential_Profile.md template only) | `wiki.mentor/local/_confidential/` (gitignored zone) | P4 zone | ✅ Done in S004 B7 (on-disk only; no tracked-state change) |
| `wiki/.claude/personas/CLAUDE.librarian.md` | `.claude/personas/CLAUDE.librarian.md` (project root) | P7 | ✅ Done in S004 B8 |
| (NEW) | `.claude/personas/CLAUDE.auditor.md` (byte-equal carry from EMCC.Library) | P7 | ✅ Done in S004 B8 |
| (NEW) | `CLAUDE.md` (v1.1 rewrite — Path-migrations pointer + ROOT_INDEX) | — | ✅ Done in S004 B9 |
| (NEW) | `Index.md` (Mentor-specific file-map) | — | ✅ Done in S004 B9 |
| (NEW) | `emcc.modules.json` (consumer module references — Library + DFDU) | — | ✅ Done in S004 B9 |
| (NEW) | `tasks/architect-notes.md` (Mentor-specific architect record) | — | ✅ Done in S004 B9 |
| `0. Inbox/` (empty) | `0-Inbox/.gitkeep` | P6 | ✅ Done in S004 B9 |
| (NEW) | `assets/{logos,brand,photos,videos,designs,generated}/.gitkeep` | — | ✅ Done in S004 B9 |
| `tasks/{Archive,INGEST,Lessons,REFERENCE_LAST_CHECKED,Sessions,Todo}.md` (Title-Case mirrors) | DELETED (were stale convenience mirrors superseded by lowercase Boris-state files) | — | ✅ Done in S004 B9 |
| `wiki/.gitkeep`, `wiki/_inbox/README.md` | DELETED (post-B-phase shell cleanup) | — | ✅ Done in S004 B10 |
| `wiki/Attachments/`, `wiki/public/`, `wiki/scripts/` (M002 pre-existing empty stubs) | DELETED (untracked empty dirs) | — | ✅ Done in S004 B10 |
| `.obsidian/{app,appearance,core-plugins,workspace}.json` (operator-local UI state) | UNTRACKED via git rm --cached (machine-local; .gitignore .obsidian/ blanket) | — | ✅ Done in S004 B1 |
| `JP CheatSheet` (operator-personal grok-tui cheatsheet) | STAYS at project root (canonical rename to Cheatsheet.md deferred per architect-notes) | — | ⏳ Deferred |

### Cross-repo Library moves (S004 / MI-16 + MI-18 closure)

These rows describe Library-side changes triggered by Mentor's
migration. They are also recorded in
`EMCC.Library/reorganization-instructions.library.md` for Library's own
audit trail; duplicated here so Mentor's manifest is self-contained for
future archaeology.

| File | Change | Pattern |
|---|---|---|
| `Biz.Automation/wikisys.library/_scripts/sync_from_kit.py` | v1.1 contract rewrite (target paths → consumer's `Biz.Automation/wikisys.<name>/_*` + `wiki.<name>/git/codex/`; consumer-name auto-discovery; rc=4 ambiguous-discovery exit) | MI-16 closure |
| `Biz.Automation/wikisys.library/_scripts/_lib/frontmatter.py` | Added `_find_install_root()`, `find_canon_dir()`, `find_decisions_dir()`, `find_config_dir()` marker-walk helpers; extended `_find_wiki_root()` with v1.1 consumer marker (`CLAUDE.md + emcc.modules.json`) | MI-18 closure |
| `Biz.Automation/wikisys.library/_scripts/{check_concept_coverage,check_canon_consistency,build_canon_drift_report,build_topic_index,validate_topic_registry,check_cascade,delta_source_docs,steel_thread_tracker,validate_reveal_conceit,validate_terminology}.py` + `_lib/topics.py` | Switched from hardcoded `wiki_root / "_canon"` / `_config` / `_decisions` to `find_*_dir()` discovery | MI-18 closure |
| `Biz.Automation/wikisys.library/_scripts/update_dashboards.py` | `_section_recent_ingest` uses `find_decisions_dir()` (fixes empty "Recent Ingest" in Library `health.md`); orchestrator CLI accepts positional `wiki_root` arg | MI-18 + MI-17 partial closure |
| `Biz.Automation/wikisys.library/_scripts/_lib/markdown.py` | `iter_content_pages` skips canonical v1.1 `raw/` source-archive zone (was skipping only `_*`-prefixed) | walker extension |
| `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` §4.2 | Sync section rewritten for v1.1 contract (consumer-root invocation, target paths, NEVER-touched list, v1.0-shape-retired note) | MI-16 closure |
| `tests/test_sync_from_kit.py` | Full rewrite for v1.1 contract (17 tests; new TestConsumerDiscovery class) | MI-16 closure |
| `tests/_lib/test_frontmatter.py::TestCanonAndDecisionsLookup` | 12 new tests for `find_canon_dir` + `find_decisions_dir` + `find_config_dir` + `_find_install_root` against v1.0 + v1.1 fixtures | MI-18 closure |
| `tests/test_lib_markdown.py::IterContentPagesTests` | New `raw/` exclusion fixture row | walker extension |
| `MIGRATION-ISSUES.md` | MI-18 registry entry added (RESOLVED in S004); MI-16 disposition flipped to RESOLVED | — |

---

## See also

- `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md` (master) — patterns
  P1–P8, audit hooks contract, per-project file index.
- `EMCC.Library/reorganization-instructions.library.md` — Library-side
  manifest (includes the cross-repo rows duplicated above).
- `EMCC.Library/tasks/plans/portfolio-folder-structure-spec.md` —
  narrative + decisions.
