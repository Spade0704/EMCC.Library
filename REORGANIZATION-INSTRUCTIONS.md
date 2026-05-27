# REORGANIZATION-INSTRUCTIONS.md

> **Purpose:** Authoritative manifest of every path migration applied when a
> project adopts the canonical portfolio folder layout (per
> `tasks/plans/portfolio-folder-structure-spec.md`). When a script, doc,
> import statement, or test fixture references an OLD path, **consult this
> file** to find the new location. Do not guess. Do not "fix" path
> references by inferring — use this manifest.

> **Audience:** the Librarian agent, audit scripts (`audit_doc_pairing.py`,
> `audit_gitignore.py`, `route_inbox.py`, etc.), bootstrap tooling, and any
> Claude Code session that hits a "file not found" error referencing an
> old path.

> **Pair docs:** `SOURCE-HISTORY.md` (where this Library's content came from
> originally — project-codex SHA), `MIGRATION-ISSUES.md` (issues encountered
> during migration), `tasks/plans/portfolio-folder-structure-spec.md` (the
> narrative + decisions; this file is the machine-readable manifest derived
> from that spec).

---

## How to use this file

1. **Lookup by old path.** If you encounter a path like `_scripts/` or
   `wiki.codex/_sources/raw/` in a script or doc, search this file for that
   string. The "New path" column gives the canonical location after
   migration.
2. **Lookup by pattern.** If the specific path isn't enumerated but matches
   a generic pattern (e.g., "Codex source folder at project root"), use the
   "Patterns" section to derive the new path mechanically.
3. **Lookup by project.** Each project that has migrated (or is scheduled to
   migrate) has a "Per-project moves" section listing every concrete move.
4. **Audit at runtime.** Audit scripts can parse this file's tables to
   verify that no stale path references remain.

---

## Patterns (generic transformation rules)

The eight pattern classes below cover every move in this manifest. Each
pattern maps to one of the locked F-resolutions in the spec (F1–F12).

| # | Pattern name | Old form | New form | Resolution |
|---|---|---|---|---|
| **P1** | Codex source → wikisys | `<root>/_scripts/`, `_template/`, `_config/`, `_canon/`, `_context/`, `_decisions/` | `<root>/Biz.Automation/wikisys.<projectname>/_scripts/` (and parallel) | F5 + F6 |
| **P2** | Spec docs → wiki topic | `<root>/CODEX_BUILD_SPEC*.md`, `CODEX_LIBRARIAN.md`, `INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`, `PROJECT_WIKI_BUILD_SPEC.md`, `Obsidian-Setup-Guide.md`, `codex-build-plan.html`, `documents/codex/*` | `<root>/wiki.<projectname>/git/codex/<filename>` | DFDU analogy `documents/lattice/` → `wiki.dfdu/git/lattice/` |
| **P3** | Sources rename + relocate | `<root>/Sources/Raw/`, `wiki.<name>/_sources/raw/` | `<root>/wiki.<projectname>/git/raw/` | F7 |
| **P4** | Brain dump rename + zone | `<root>/wiki.<name>/_brain_dump/` (gitignored) | `<root>/wiki.<projectname>/local/ideas/` (gitignored via new pattern) | F8 + F10 |
| **P5** | Wiki content under git/ | `<root>/wiki.<name>/<topic>/`, `wiki.<name>/Home.md` | `<root>/wiki.<projectname>/git/<topic>/`, `wiki.<projectname>/git/Home.md` | F10 |
| **P6** | Inbox canonical | `0. Inbox/`, `_inbox/`, `inbox/` (at project root) | `0-Inbox/` | F3 |
| **P7** | Persona drop-ins | varies (`wiki.<name>/.claude/personas/`, etc.) | `<root>/.claude/personas/CLAUDE.*.md` | F1 |
| **P8** | Task filename casing | `Tasks/`, `Todo.md`, `Sessions.md`, etc. (Title-Case) | `tasks/todo.md`, `tasks/sessions.md`, `tasks/lessons.md`, `tasks/archive.md` (lowercase) | spec add-on |

**How patterns translate at the consumer:**

- Tools (Librarian, audit scripts) parse this file's tables and apply
  pattern matching: if an old path matches `wiki.<name>/_brain_dump/`, then
  the new path is `wiki.<name>/local/ideas/` (P4).
- For paths not covered by a pattern, the "Per-project moves" section
  records the explicit mapping.
- Patterns are the source of truth; per-project tables are the materialized
  manifest derived from applying patterns to each project's pre-migration
  inventory.

---

## Per-project moves

### EMCC.Library (this module — partial migration via Session 1; remainder S002)

**Pre-Session-1 state:** SHA `156c253` on `main`. Library was the
`not-ready` placeholder; only `wiki.codex/` (dogfood wiki) + `0. Inbox/`
+ `.gitignore` + `README.md` existed at root.

**Session 1 (master plan Step 3) moves** — commits `094e8a3` → `ab94fc7`
on `claude/lattice-3-production-check-Rdkfu`, pushed 2026-05-27. These
moves brought Codex MODULE source files from project-codex into Library
root; they did NOT yet apply the canonical-layout restructure.

| Old path (project-codex SHA `ccf21b7`) | New path (Library Session 1) | Pattern | Status |
|---|---|---|---|
| `0. Inbox/codex-wiki-folder-org-principle.md` | `0-Inbox/codex-wiki-folder-org-principle.md` | P6 | ✅ Session 1 |
| `bootstrap.py` | `bootstrap.py` (Library root) | — | ✅ Session 1 |
| `CODEX_BUILD_SPEC_v1_3.md` | `CODEX_BUILD_SPEC_v1_3.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `CODEX_LIBRARIAN.md` | `CODEX_LIBRARIAN.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `INGEST_PROCEDURE.md` | `INGEST_PROCEDURE.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `SEMANTIC_LINT_PROCEDURE.md` | `SEMANTIC_LINT_PROCEDURE.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `PROJECT_WIKI_BUILD_SPEC.md` | `PROJECT_WIKI_BUILD_SPEC.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `Obsidian-Setup-Guide.md` | `Obsidian-Setup-Guide.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `codex-build-plan.html` | `codex-build-plan.html` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `_scripts/` (minus 3 lattice-2.0 scripts) | `_scripts/` (Library root) | — | ✅ Session 1 (S002 moves it again per P1) |
| `_template/` | `_template/` (Library root) | — | ✅ Session 1 (S002 moves it again per P1) |
| `_config/` | `_config/` (Library root) | — | ✅ Session 1 (S002 moves it again per P1) |
| `tests/` (minus 5 lattice-2.0 tests) | `tests/` (Library root) | — | ✅ Session 1 (stays at root per `<product-code-root>` rule) |
| `Sources/Raw/` | `Sources/Raw/` (Library root) | — | ✅ Session 1 (S002 moves it again per P3) |
| `documents/Codex_*.{pdf,txt}` + `documents/codex-build-progress.md` | `documents/codex/<filename>` | — | ✅ Session 1 (S002 moves them again per P2) |
| `.claude/personas/CLAUDE.librarian.md` | `.claude/personas/CLAUDE.librarian.md` (Library root) | P7 | ✅ Session 1 |
| (NEW) | `.claude/personas/CLAUDE.auditor.md` (byte-equal from `EMCC.DFDU/personas/CLAUDE.auditor.md`) | P7 | ✅ Session 1 |
| (NEW) | `CLAUDE.md`, `module.json`, `SOURCE-HISTORY.md`, `MIGRATION-ISSUES.md`, `.github/workflows/test.yml` | — | ✅ Session 1 |
| `tasks/v1.1-backlog.md` | `tasks/v1.1-backlog.md` (Library) | — | ✅ Session 1 |
| (NEW) | `tasks/{todo,sessions,lessons,archive}.md` | — | ✅ Session 1 |

**S002 / Codex v1.1 moves** — module source files extracted to
`Biz.Automation/wikisys.library/`; spec docs became wiki content under
`wiki.codex/git/codex/`; `wiki.codex/` internal restructure into
`git/` + `local/` subfolders. Closed 2026-05-27 with 8+ commits on
`claude/codex-v1.1-S002-restructure`.

| Old path (Library Session 1) | New path (post-S002) | Pattern | Status |
|---|---|---|---|
| `_scripts/` | `Biz.Automation/wikisys.library/_scripts/` | P1 | ✅ Done in S002 B2 (commit `1e675fd`) |
| `_template/` | `Biz.Automation/wikisys.library/_template/` | P1 | ✅ Done in S002 B2 (commit `1e675fd`) |
| `_config/` | `Biz.Automation/wikisys.library/_config/` (merged with `wiki.codex/_config/`) | P1 | ✅ Done in S002 B2 + B4 (commits `1e675fd` + `d0dfdbb`) |
| `Sources/Raw/` | `wiki.codex/git/raw/` (merged with `wiki.codex/_sources/raw/`; root README deleted as superseded — MI-15) | P3 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `CODEX_BUILD_SPEC_v1_3.md` | `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `CODEX_LIBRARIAN.md` | `wiki.codex/git/codex/CODEX_LIBRARIAN.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `INGEST_PROCEDURE.md` | `wiki.codex/git/codex/INGEST_PROCEDURE.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `SEMANTIC_LINT_PROCEDURE.md` | `wiki.codex/git/codex/SEMANTIC_LINT_PROCEDURE.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `PROJECT_WIKI_BUILD_SPEC.md` | `wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `Obsidian-Setup-Guide.md` | `wiki.codex/git/codex/Obsidian-Setup-Guide.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `codex-build-plan.html` | `wiki.codex/git/codex/codex-build-plan.html` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `documents/codex/Codex_Project_Documentation.pdf` | `wiki.codex/git/codex/Codex_Project_Documentation.pdf` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `documents/codex/Codex_Workflow_Cheatsheet_v1.txt` | `wiki.codex/git/codex/Codex_Workflow_Cheatsheet_v1.txt` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `documents/codex/codex-build-progress.md` | `wiki.codex/git/codex/codex-build-progress.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `wiki.codex/Home.md` | `wiki.codex/git/Home.md` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/00-Start-Here/` | `wiki.codex/git/00-Start-Here/` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/01-Architecture/` | `wiki.codex/git/01-Architecture/` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/02-Operations/` | `wiki.codex/git/02-Operations/` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/04-Contributing/` | `wiki.codex/git/04-Contributing/` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/.claude/` | `wiki.codex/git/.claude/` (dogfood Librarian drop-in) | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_canon/` | `Biz.Automation/wikisys.library/_canon/` | P1 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_config/` | `Biz.Automation/wikisys.library/_config/` (merged with root `_config/`) | P1 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_context/` | `Biz.Automation/wikisys.library/_context/` | P1 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_decisions/` | `Biz.Automation/wikisys.library/_decisions/` | P1 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_sources/raw/` | `wiki.codex/git/raw/` (merged with root `Sources/Raw/`) | P3 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_brain_dump/` | `wiki.codex/local/ideas/` (untracked content; gitignored under new `wiki.*/local/` rule) | P4 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_scripts/` (27 stale bootstrap-output files) | DELETED (older than canonical; documented as MI-14) | — | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `bootstrap.py` | `bootstrap.py` (STAYS at Library root — entry script) | — | ✅ Stays |
| `tests/` | `tests/` (STAYS at root — `<product-code-root>` rule) | — | ✅ Stays |
| `.claude/personas/CLAUDE.{auditor,librarian}.md` | `.claude/personas/CLAUDE.{auditor,librarian}.md` (STAYS — P7 already canonical) | — | ✅ Stays |
| `module.json`, `CLAUDE.md`, `SOURCE-HISTORY.md`, `MIGRATION-ISSUES.md`, `README.md`, `.gitignore` | (STAY at root) | — | ✅ Stays |
| `Index.md`, `Cheatsheet.md` | (NEW root files; ship in S004 first real consumer-project bootstrap; Library itself uses CLAUDE.md ROOT_INDEX as Index.md surrogate per spec a variance allowance) | — | ⏳ Deferred to S004 |

**S003b / Library staleness archive sweep** — closed 2026-05-27 on
`claude/library-staleness-S003b-n8r3w`. Two full relocations (rest of
the audit's 9 ARCHIVE candidates use banner-at-current-path so the
cross-link validator stays green — those banner-only files do NOT
appear in this manifest because path is unchanged).

| Old path (post-S002) | New path (post-S003b) | Pattern | Status |
|---|---|---|---|
| `0-Inbox/codex-wiki-folder-org-principle.md` | `wiki.codex/git/_archive/_inbox/codex-wiki-folder-org-principle.md` | — (full relocation; 0 inbound wikilinks; move = Librarian-discipline empty-inbox signal) | ✅ Done in S003b |
| `Biz.Automation/wikisys.library/_scripts/launchers/` (5 files: 4 .ps1 + README.md) | `Biz.Automation/wikisys.library/_scripts/_archive/launchers/` (+ new `_archive/README.md` documenting Lattice 2.0 → 3.0 transition) | — (full relocation; Lattice 2.0 Nexus 4-persona model retired; no active dependents — `test_bootstrap.py` reference is MI-16-retired) | ✅ Done in S003b |

### S002-internal callers updated

The B5a path-rebase commit (`7707d5b`) and B5b bootstrap.py rewrite
(`9bf1004`) updated the following internal callers to read from the
new source-of-truth paths:

| Caller | Changed via | Update |
|---|---|---|
| `bootstrap.py` `_resolve_source_scripts_dir()` (line 62) | B5a `7707d5b` | default → `Biz.Automation/wikisys.library/_scripts` |
| `bootstrap.py` `_resolve_template_dir()` (line 114) | B5a `7707d5b` | default → `Biz.Automation/wikisys.library/_template` |
| `bootstrap.py` (entire file) | B5b `9bf1004` | full canonical-output rewrite per spec (c); scaffold-only (no script copy); `<projectname>` positional CLI; 5 stub generators |
| `Biz.Automation/wikisys.library/_scripts/sync_from_kit.py` | B5a `7707d5b` | new `WIKISYS_REL` + `SPEC_DOCS_REL` constants; `_required_sources()` + `_build_plan()` prefix source paths with `wikisys.library/` + `wiki.codex/git/codex/` |
| `Biz.Automation/wikisys.library/_scripts/_lib/frontmatter.py` `parse_config_yaml` | B6 `0127c4e` | FINDING #1: block-list sub-list under continuation field — `pending_subkey` FSM state added |
| `tests/__init__.py` sys.path | B5a `7707d5b` | rebase to `wikisys.library/_scripts` |
| `tests/perf/bench_frontmatter.py` sys.path inserts (×2) | B5a `7707d5b` | rebase |
| `tests/test_phase6_full_chain_e2e.py` (REPO_ROOT-relative paths) | B5a `7707d5b` then B5b `9bf1004` (module SkipTest) | rebased; later skipped as MI-16 |
| `tests/test_scaffold_source.py`, `tests/test_scaffold_brain_dump.py` (SCAFFOLD_PY) | B5a `7707d5b` | rebase |
| `tests/test_t1_p52_bootstrap_operation.py` (TEMPLATE_DIR, CODEX_SCRIPTS) | B5a then B5b skip | rebased then MI-16 retire |
| `tests/test_t2_p53_sync_operation.py` (multiple REPO_ROOT paths) | B5a then B5b skip | rebased then MI-16 retire |
| `tests/test_t3_p54_ingest_operation.py` (TEMPLATE_DIR) | B5a then B5b skip | rebased then MI-16 retire |
| `tests/test_sync_from_kit.py` `_make_codex_install` fixture | B5a `7707d5b` | fixture rewrites source layout to mirror new split (wikisys + spec-docs roots) |
| `tests/test_bootstrap.py` (entire file) | B5b `9bf1004` (module SkipTest) | MI-16 retire — file tests v1.0 contract |

**Note on `_scripts/_lib/config_loader.py`:** the discovery layer
turned out to accept a `config_path` argument (relative to the
consuming wiki, not Library), so no Library-internal path rebase was
needed. The B5a path-rebase plan over-allocated edit time here.

**Note on `_template/_context__SEP__INGEST_PROCEDURE.md`:** the
manifest pre-flight predicted this template file would need rewiring
to read from `wiki.codex/git/codex/` after S002. It turned out the
template file is byte-equal to the spec doc; the symlink/copy chain
flows through `sync_from_kit.py`'s `SPEC_DOCS_REL`-prefixed source
lookup (now in place per B5a). No template-file edit was required.

### Mentor (Project-Mentor — first consumer migration, S004 / 2026-05-28)

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

**Cross-repo Library moves (S004 / MI-16 + MI-18 closure):**

| File | Change | Pattern |
|---|---|---|
| `Biz.Automation/wikisys.library/_scripts/sync_from_kit.py` | v1.1 contract rewrite (target paths -> consumer's `Biz.Automation/wikisys.<name>/_*` + `wiki.<name>/git/codex/`; consumer-name auto-discovery; rc=4 ambiguous-discovery exit) | MI-16 closure |
| `Biz.Automation/wikisys.library/_scripts/_lib/frontmatter.py` | Added `_find_install_root()`, `find_canon_dir()`, `find_decisions_dir()`, `find_config_dir()` marker-walk helpers; extended `_find_wiki_root()` with v1.1 consumer marker (`CLAUDE.md + emcc.modules.json`) | MI-18 closure |
| `Biz.Automation/wikisys.library/_scripts/{check_concept_coverage,check_canon_consistency,build_canon_drift_report,build_topic_index,validate_topic_registry,check_cascade,delta_source_docs,steel_thread_tracker,validate_reveal_conceit,validate_terminology}.py` + `_lib/topics.py` | Switched from hardcoded `wiki_root / "_canon"` / `_config` / `_decisions` to `find_*_dir()` discovery | MI-18 closure |
| `Biz.Automation/wikisys.library/_scripts/update_dashboards.py` | `_section_recent_ingest` uses `find_decisions_dir()` (fixes empty "Recent Ingest" in Library `health.md`); orchestrator CLI accepts positional `wiki_root` arg | MI-18 + MI-17 partial closure |
| `Biz.Automation/wikisys.library/_scripts/_lib/markdown.py` | `iter_content_pages` skips canonical v1.1 `raw/` source-archive zone (was skipping only `_*`-prefixed) | walker extension |
| `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` §4.2 | Sync section rewritten for v1.1 contract (consumer-root invocation, target paths, NEVER-touched list, v1.0-shape-retired note) | MI-16 closure |
| `tests/test_sync_from_kit.py` | Full rewrite for v1.1 contract (17 tests; new TestConsumerDiscovery class) | MI-16 closure |
| `tests/_lib/test_frontmatter.py::TestCanonAndDecisionsLookup` | 12 new tests for `find_canon_dir` + `find_decisions_dir` + `find_config_dir` + `_find_install_root` against v1.0 + v1.1 fixtures | MI-18 closure |
| `tests/test_lib_markdown.py::IterContentPagesTests` | New `raw/` exclusion fixture row | walker extension |
| `MIGRATION-ISSUES.md` | MI-18 registry entry added (RESOLVED in S004); MI-16 disposition flipped to RESOLVED | — |

### tat_app, aviation, aviation-career, eddyandwolff, isommelier, EMCC, EMCC.DFDU

**Status: deferred — to be materialized when each project's migration runs.**

These projects have not yet migrated. Their per-project moves tables will
be appended to this manifest WHEN their migration punchlist (in
`tasks/plans/portfolio-folder-structure-spec.md` section b) is executed.

Pre-execution, the punchlist serves as the migration plan; the manifest
table is generated FROM the punchlist by mapping each narrative step to
its (Old path) → (New path) row.

**Project list (with punchlist references in the spec):**

| Project | Section in spec | Difficulty | Suggested order |
|---|---|---|---|
| Mentor (greenfield) | section c | None (bootstrap) | 1st (smoke test for bootstrap.py) |
| EMCC.Library (this module) | section b | Significant | 2nd (after S002 = first real migration; this manifest gets fleshed out) |
| EMCC | section b | Significant | 3rd |
| EMCC.DFDU | section b | Light | 4th |
| tat_app | section b | Light | 5th |
| isommelier | section b | Significant | 6th |
| aviation | section b | Significant | 7th |
| aviation-career | section b | Clean minimal | 8th |
| eddyandwolff | section b | Gnarliest | LAST (zoning + 4-deep nesting) |

---

## CLAUDE.md update (MUST APPLY at end of any migration)

When any project's migration completes, the project's `CLAUDE.md` MUST be
updated to include a pointer to this file. This is the **defensive
indirection layer**: when a future Claude session or script hits an
unknown path reference, CLAUDE.md tells them to check the manifest.

**Suggested wording for CLAUDE.md** (insert as a new section between
"Required reading" and "ROOT_INDEX", or as a standalone reminder near
the top):

```markdown
## Path migrations

This project has been reorganized into the canonical portfolio layout
(per `EMCC.Library/tasks/plans/portfolio-folder-structure-spec.md`).

**If you encounter an old path reference** in a script, doc, import, or
test fixture (e.g., `_scripts/` at project root, `wiki.codex/_brain_dump/`,
`Sources/Raw/`), **consult**
`EMCC.Library/REORGANIZATION-INSTRUCTIONS.md` for the new location.

**Do NOT guess** at the new path. Do NOT "fix" path references by
inferring from context. Use the manifest. Patterns P1–P8 in the
manifest cover the eight generic transformation classes; the
per-project moves table records the explicit mappings.

If a path you encounter isn't in either the patterns OR the
per-project table, surface it as a finding (it may indicate an
incomplete migration or a stale reference that needs explicit
disposition).
```

**For consumer projects** that vendor Library, the pointer becomes:

```markdown
## Path migrations

If you encounter an old path reference in a script or doc, consult
EMCC.Library's `REORGANIZATION-INSTRUCTIONS.md` in your Library
clone (vendored copy, git submodule, or sibling-directory checkout).
Library is not currently distributed as a Python wheel (per MI-13
disposition — stdlib only, no PEP 621 manifest). Consumers run
Codex's `bootstrap.py` + `sync_from_kit.py` directly from a clone or
vendored copy; resolve the manifest path the same way.
```

---

## Conventions for adding to this manifest

When a migration runs:

1. Add the project's section under "Per-project moves" with the (Old path)
   → (New path) → (Pattern) → (Status) rows.
2. If the migration encounters a path that doesn't match any of P1–P8,
   propose a new pattern (P9+) with a written justification, then add the
   row.
3. Status column values: `✅ Done in <session>`, `⏳ Pending <session>`,
   `❌ Skipped — <reason>`.
4. Reference the spec section that authorized the move (e.g., "F6 + F7" or
   "section b EMCC.Library punchlist item 4").
5. Keep entries chronological per project (oldest-state to newest-state in
   left-to-right table columns).

---

## Open questions / future patterns

- **P9 (potential):** Cross-project shared content (Codex topic appears in
  3+ project wikis). Where does it live? Spec section d Operation 6 raises
  this; resolution deferred to Phase 2.
- **P10 (potential):** Subject-named wiki variance. Some projects use
  `wiki.<subject>/` instead of `wiki.<projectname>/` (e.g., `wiki.etihad/`
  inside `aviation/`, `wiki.codex/` inside `EMCC.Library/`). This is a
  permitted variance, not a transformation pattern — but tooling that
  parses this manifest must recognize both forms.

---

## Audit hooks (script integration)

Once `audit_doc_pairing.py`, `audit_gitignore.py`, etc. ship in
`Biz.Automation/wikisys.library/_scripts/`, they should:

1. On startup, parse this manifest into a Python dict keyed by old path.
2. Cross-reference every path string they encounter in the consuming
   project's tree against the dict.
3. Emit findings for any old-path match found (e.g., a script reference to
   `_scripts/build_topic_index.py` when the canonical path is now
   `Biz.Automation/wikisys.library/_scripts/build_topic_index.py`).
4. Optionally apply fixes when invoked with `--apply` flag (subject to
   operator confirmation per `CODEX_LIBRARIAN.md` "ingest proposes, humans
   dispose" hard rule).

This integration is part of S002 scope (5 P0/P1 new scripts in
`wikisys.library/_scripts/`).
