# REORGANIZATION-INSTRUCTIONS.md (master)

> **Purpose:** Cross-repo source-of-truth for path-migration **patterns**
> (P1–P8) and **audit-hook contract**. The concrete (Old path) → (New path)
> rows for any one project live in that project's own
> `reorganization-instructions.<projectname>.md` at the project root (see
> "Per-project files" index below).

> **Audience:** the Librarian agent, audit scripts
> (`audit_doc_pairing.py`, `audit_gitignore.py`, `route_inbox.py`, etc.),
> bootstrap tooling, and any Claude Code session that hits a "file not
> found" error referencing an old path.

> **Convention (introduced 2026-05-28, pre-S006):** Each project that
> adopts the canonical portfolio layout SHIPS its own
> `reorganization-instructions.<projectname>.md` at its root. The master
> (this file) holds patterns + audit-hook contract; per-project files
> hold the concrete moves. `bootstrap.py` emits a stub of the per-project
> file alongside the other root stubs (`CLAUDE.md`, `Index.md`,
> `Cheatsheet.md`).

> **Pair docs:** `SOURCE-HISTORY.md` (where this Library's content came
> from originally — project-codex SHA), `MIGRATION-ISSUES.md` (issues
> encountered during migration), `tasks/plans/portfolio-folder-structure-spec.md`
> (the narrative + decisions; per-project manifests are the machine-readable
> derivatives).

---

## How to use this file

1. **Lookup by pattern.** If you encounter a path like `_scripts/` or
   `wiki.codex/_sources/raw/` in a script or doc and don't know the new
   location, scan the "Patterns" table below. The pattern row tells you
   the canonical transformation.
2. **Lookup by project.** For project-specific moves (the concrete rows),
   open that project's `reorganization-instructions.<projectname>.md` —
   see the "Per-project files" index.
3. **Audit at runtime.** Audit scripts parse this file's pattern table
   for generic rules + each per-project file's concrete tables for
   explicit overrides.

---

## Patterns (generic transformation rules)

The eight pattern classes below cover every move recorded in any project
manifest. Each pattern maps to one of the locked F-resolutions in
`tasks/plans/portfolio-folder-structure-spec.md`.

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

- Tools (Librarian, audit scripts) parse this file's pattern table and
  apply pattern matching: if an old path matches `wiki.<name>/_brain_dump/`,
  then the new path is `wiki.<name>/local/ideas/` (P4).
- For paths not covered by a pattern, the project's own
  `reorganization-instructions.<projectname>.md` records the explicit
  mapping.
- Patterns are the source of truth; per-project files are the
  materialized manifests derived from applying patterns to each
  project's pre-migration inventory.

---

## Per-project files

Each project that has migrated (or is scheduled to migrate) maintains
its own per-project manifest. The table below indexes them.

### Migrated

| Project | Manifest location | Status |
|---|---|---|
| **EMCC.Library** (this module) | `EMCC.Library/reorganization-instructions.library.md` (this repo) | Migration closed in S002 + S003b (2026-05-27). Manifest extracted from this master 2026-05-28. |

### Pending cross-repo migration

These projects have a manifest authored but it has not yet been moved
to its destination repo. Each carries a TODO at the top of its file
naming the next session that must complete the cross-repo move.

| Project | Manifest staging location | Destination | Status |
|---|---|---|---|
| **Project-Mentor** | `EMCC.Library/tasks/plans/cross-repo-pending/reorganization-instructions.mentor.md` | `<mentor-root>/reorganization-instructions.mentor.md` | Migration closed in S004 (2026-05-28). Manifest extracted from this master 2026-05-28; awaits cross-repo move when next Mentor session opens. |

### Planned (greenfield bootstrap or migration not yet started)

These projects do NOT yet have a per-project manifest. When their
migration runs (or, for greenfield, when `bootstrap.py` is invoked),
the per-project file will be emitted at their root by `bootstrap.py`'s
stub generator (see `bootstrap.py::_stub_reorganization_md`) and
populated from the project's punchlist in
`tasks/plans/portfolio-folder-structure-spec.md` section (b).

| Project | Section in spec | Difficulty | Suggested order |
|---|---|---|---|
| Mentor (greenfield) | section c | None (bootstrap) | 1st (smoke test for bootstrap.py) — **DONE in S004** |
| EMCC.Library (this module) | section b | Significant | 2nd (after S002 = first real migration) — **DONE in S002/S003b** |
| EMCC | section b | Significant | 3rd |
| EMCC.DFDU | section b | Light | 4th |
| Aviation | section b | Significant | NEXT — Phase 1 seed manifest staged at `tasks/plans/aviation-bootstrap-seed/reorganization-instructions.aviation.md` |
| tat_app | section b | Light | 5th |
| isommelier | section b | Significant | 6th |
| aviation-career | section b | Clean minimal | 8th |
| eddyandwolff | section b | Gnarliest | LAST (zoning + 4-deep nesting) |

---

## CLAUDE.md update (MUST APPLY at end of any migration)

When any project's migration completes, the project's `CLAUDE.md` MUST be
updated to include a pointer to BOTH:

1. **The project's own `reorganization-instructions.<projectname>.md`**
   at the project root (for that project's concrete moves).
2. **EMCC.Library's master `REORGANIZATION-INSTRUCTIONS.md`** (for
   patterns and cross-repo conventions).

This is the **defensive indirection layer**: when a future Claude
session or script hits an unknown path reference, CLAUDE.md tells them
to check both manifests.

**Suggested wording for `CLAUDE.md`** (insert as a new section
between "Required reading" and "ROOT_INDEX", or as a standalone
reminder near the top):

```markdown
## Path migrations

This project has been reorganized into the canonical portfolio layout
(per `EMCC.Library/tasks/plans/portfolio-folder-structure-spec.md`).

**If you encounter an old path reference** in a script, doc, import, or
test fixture, **consult** `reorganization-instructions.<projectname>.md`
**at this project's root** for concrete moves. If the path matches a
generic pattern (e.g., `_scripts/` at project root, `wiki.codex/_brain_dump/`,
`Sources/Raw/`) and isn't enumerated, fall back to
`EMCC.Library/REORGANIZATION-INSTRUCTIONS.md` master for patterns P1–P8.

**Do NOT guess** at the new path. Use the manifests. If a path you
encounter isn't covered by either, surface it as a finding (it may
indicate an incomplete migration or a stale reference needing explicit
disposition).
```

**For consumer projects** that vendor Library, the pattern-lookup pointer
becomes:

```markdown
For pattern lookups, consult EMCC.Library's `REORGANIZATION-INSTRUCTIONS.md`
in your Library clone (vendored copy, git submodule, or sibling-directory
checkout). Library is not currently distributed as a Python wheel (per
MI-13 disposition — stdlib only, no PEP 621 manifest). Consumers run
Codex's `bootstrap.py` + `sync_from_kit.py` directly from a clone or
vendored copy; resolve the manifest path the same way.
```

---

## Conventions for adding to a per-project manifest

When a migration runs for project `<projectname>`:

1. **If the project was bootstrapped via `bootstrap.py`** the stub
   `reorganization-instructions.<projectname>.md` will already exist
   at the project root. Open it.
2. **Otherwise** (migration of a pre-canonical project), create
   `<projectroot>/reorganization-instructions.<projectname>.md` using
   any existing per-project manifest as a starting template.
3. Add the (Old path) → (New path) → (Pattern) → (Status) rows in
   tables grouped by sprint or phase.
4. If the migration encounters a path that doesn't match any of P1–P8,
   propose a new pattern (P9+) here in the master with a written
   justification, then add the row.
5. Status column values: `✅ Done in <session>`, `⏳ Pending <session>`,
   `❌ Skipped — <reason>`.
6. Reference the spec section that authorized the move (e.g., "F6 + F7"
   or "section b EMCC.Library punchlist item 4").
7. Keep entries chronological per project (oldest-state to newest-state
   in left-to-right table columns).
8. After completing a migration, **add the project's entry to the
   "Migrated" table in this master** so the cross-repo index stays
   current.

---

## Open questions / future patterns

- **P9 (potential):** Cross-project shared content (Codex topic appears in
  3+ project wikis). Where does it live? Spec section d Operation 6 raises
  this; resolution deferred to Phase 2.
- **P10 (potential):** Subject-named wiki variance. Some projects use
  `wiki.<subject>/` instead of `wiki.<projectname>/` (e.g., `wiki.etihad/`
  inside `aviation/`, `wiki.codex/` inside `EMCC.Library/`). This is a
  permitted variance, not a transformation pattern — but tooling that
  parses any per-project manifest must recognize both forms.

---

## Audit hooks (script integration)

Once `audit_doc_pairing.py`, `audit_gitignore.py`, etc. ship in
`Biz.Automation/wikisys.library/_scripts/`, they should:

1. On startup, parse this master file's pattern table into a Python list
   of regex transformations.
2. Parse the consuming project's
   `reorganization-instructions.<projectname>.md` (if it exists) into
   a dict keyed by old path → new path.
3. Cross-reference every path string they encounter in the consuming
   project's tree against the dict + patterns.
4. Emit findings for any old-path match found (e.g., a script reference
   to `_scripts/build_topic_index.py` when the canonical path is now
   `Biz.Automation/wikisys.library/_scripts/build_topic_index.py`).
5. Optionally apply fixes when invoked with `--apply` flag (subject to
   operator confirmation per `CODEX_LIBRARIAN.md` "ingest proposes,
   humans dispose" hard rule).

This integration is part of S002 scope (5 P0/P1 new scripts in
`wikisys.library/_scripts/`).

---

## Change log

| Date | Change | Authority |
|---|---|---|
| 2026-05-27 | Initial master created during S002 / Library v1.1 migration | S002 close record |
| 2026-05-28 | Split: per-project content extracted to `reorganization-instructions.<projectname>.md` at each project root; this master retained patterns + audit hooks + index. `bootstrap.py` updated to emit a stub at root for new projects. Mentor section staged at `tasks/plans/cross-repo-pending/` pending cross-repo move. Aviation seed staged at `tasks/plans/aviation-bootstrap-seed/`. | Pre-S006 prep sprint |
