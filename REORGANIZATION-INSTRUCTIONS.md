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

**S002 / Codex v1.1 planned moves** — module source files extract to
`Biz.Automation/wikisys.library/`; spec docs become wiki content under
`wiki.codex/git/codex/`; `wiki.codex/` internal restructure into
`git/` + `local/` subfolders.

| Old path (Library Session 1) | New path (post-S002) | Pattern |
|---|---|---|
| `_scripts/` | `Biz.Automation/wikisys.library/_scripts/` | P1 |
| `_template/` | `Biz.Automation/wikisys.library/_template/` | P1 |
| `_config/` | `Biz.Automation/wikisys.library/_config/` (merged with `wiki.codex/_config/`) | P1 |
| `Sources/Raw/` | `wiki.codex/git/raw/` | P3 |
| `CODEX_BUILD_SPEC_v1_3.md` | `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` | P2 |
| `CODEX_LIBRARIAN.md` | `wiki.codex/git/codex/CODEX_LIBRARIAN.md` | P2 |
| `INGEST_PROCEDURE.md` | `wiki.codex/git/codex/INGEST_PROCEDURE.md` | P2 |
| `SEMANTIC_LINT_PROCEDURE.md` | `wiki.codex/git/codex/SEMANTIC_LINT_PROCEDURE.md` | P2 |
| `PROJECT_WIKI_BUILD_SPEC.md` | `wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md` | P2 |
| `Obsidian-Setup-Guide.md` | `wiki.codex/git/codex/Obsidian-Setup-Guide.md` | P2 |
| `codex-build-plan.html` | `wiki.codex/git/codex/codex-build-plan.html` | P2 |
| `documents/codex/Codex_Project_Documentation.pdf` | `wiki.codex/git/codex/Codex_Project_Documentation.pdf` | P2 |
| `documents/codex/Codex_Workflow_Cheatsheet_v1.txt` | `wiki.codex/git/codex/Codex_Workflow_Cheatsheet_v1.txt` | P2 |
| `documents/codex/codex-build-progress.md` | `wiki.codex/git/codex/codex-build-progress.md` | P2 |
| `wiki.codex/Home.md` | `wiki.codex/git/Home.md` | P5 |
| `wiki.codex/00-Start-Here/` | `wiki.codex/git/00-Start-Here/` | P5 |
| `wiki.codex/01-Architecture/` | `wiki.codex/git/01-Architecture/` | P5 |
| `wiki.codex/02-Operations/` | `wiki.codex/git/02-Operations/` | P5 |
| `wiki.codex/04-Contributing/` | `wiki.codex/git/04-Contributing/` | P5 |
| `wiki.codex/_canon/` | `Biz.Automation/wikisys.library/_canon/` | P1 |
| `wiki.codex/_config/` | `Biz.Automation/wikisys.library/_config/` (merges with root `_config/`) | P1 |
| `wiki.codex/_context/` | `Biz.Automation/wikisys.library/_context/` | P1 |
| `wiki.codex/_decisions/` | `Biz.Automation/wikisys.library/_decisions/` | P1 |
| `wiki.codex/_sources/raw/` | `wiki.codex/git/raw/` (merges with root `Sources/Raw/`) | P3 |
| `wiki.codex/_brain_dump/` | `wiki.codex/local/ideas/` | P4 |
| `bootstrap.py` | `bootstrap.py` (STAYS at Library root — entry script) | — |
| `tests/` | `tests/` (STAYS at root — `<product-code-root>` rule) | — |
| `.claude/personas/CLAUDE.{auditor,librarian}.md` | `.claude/personas/CLAUDE.{auditor,librarian}.md` (STAYS — P7 already canonical) | — |
| `module.json`, `CLAUDE.md`, `SOURCE-HISTORY.md`, `MIGRATION-ISSUES.md`, `README.md`, `.gitignore`, `Index.md` (NEW), `Cheatsheet.md` (NEW) | (STAY at root) | — |

**Library-internal callers that will need updating during S002:**

The S002 implementation session must check the following for hardcoded old
paths and update them per this manifest. These ARE Codex code changes (not
forbidden by AC8 — v1.1 explicitly allows code changes for path
adjustments).

- `bootstrap.py` — currently reads templates from `_template/`, config from
  `_config/`, etc. Must be updated to read from
  `Biz.Automation/wikisys.library/_template/` (or use a single canonical
  config-lookup helper that the operator can override).
- `_scripts/_lib/config_loader.py` — discovery layer for `_config/` lookup.
  May need update.
- `_scripts/sync_from_kit.py` — overwrites wiki `_context/`,
  `_scripts/`, etc. from Codex install. Must be updated to read from
  `Biz.Automation/wikisys.library/_context/` etc.
- All `tests/*.py` that compute paths relative to repo root.
- `_template/_context__SEP__INGEST_PROCEDURE.md` — symlinks/byte-copy
  source. Should be wired to read from `wiki.codex/git/codex/` after S002.

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

**For consumer projects** that vendor or pip-install Library, the
pointer becomes:

```markdown
## Path migrations

If you encounter an old path reference in a script or doc, consult
EMCC.Library's `REORGANIZATION-INSTRUCTIONS.md` (in your Library
clone, e.g. via `python -c "import librarian, pathlib; print(pathlib.Path(librarian.__file__).resolve().parent.parent / 'REORGANIZATION-INSTRUCTIONS.md')"`).
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
