# Source History — EMCC.Library

## Extraction event — Step 3 of master Codex-extraction plan (Session 1, 2026-05-27)

**Date:** 2026-05-27
**Source repo:** `spade0704/project-codex`
**Source branch:** `claude/lattice-3-production-check-Rdkfu` (= `main`)
**Source commit (HEAD at extraction):** `ccf21b7c` (S048-session-close — `tasks(sessions+todo): S048-session-close — 4 mini-cycle session-2 snapshot (T0 SSOT cure / T0a CHANGELOG fix-fwd / SSH-record HOLD / spec-pointer-reconcile); wiki #2 still pending → S048 STAYS OPEN`)

The source commit is the close of project-codex's S048 — final operational pass before the extraction trigger. Codex v1.0 had shipped earlier at `c106155` (2026-05-22); S048 was post-v1.0 dogfood-driven mini-cycle work (operational, not spec-changing).

## What moved

Per `tasks/architect-notes.md` §S001 goes/stays inventory G1–G20:

| # | Source path | Destination path | Note |
|---|---|---|---|
| G1 | `bootstrap.py` | `bootstrap.py` | Codex entry |
| G2 | `CODEX_BUILD_SPEC_v1_3.md` | `CODEX_BUILD_SPEC_v1_3.md` | Single canonical (v1_1/v1_2 STAY in project-codex archive) |
| G3 | `CODEX_LIBRARIAN.md` | `CODEX_LIBRARIAN.md` | Librarian agent spec |
| G4 | `INGEST_PROCEDURE.md` | `INGEST_PROCEDURE.md` | Verbatim discipline (byte-equal check post-move) |
| G5 | `SEMANTIC_LINT_PROCEDURE.md` | `SEMANTIC_LINT_PROCEDURE.md` | Verbatim discipline (byte-equal check post-move) |
| G6 | `PROJECT_WIKI_BUILD_SPEC.md` | `PROJECT_WIKI_BUILD_SPEC.md` | Wiki build spec |
| G7 | `Obsidian-Setup-Guide.md` | `Obsidian-Setup-Guide.md` | Consumer guidance |
| G8 | `_scripts/` (minus 3 lattice-2.0 scripts) | `_scripts/` | Automation; lattice-bridge.py + lattice_session_start.py + lattice_valid_roles_audit.py STAY in project-codex per A1 ambiguity resolution |
| G9 | `_template/` | `_template/` | 26 wiki template files |
| G10 | `_config/` | `_config/` | 5 YAML + README |
| G11 | `tests/` (minus 5 lattice-bridge tests; A2 was REVOKED in Phase B3 — see MIGRATION-ISSUES.md) | `tests/` | Per A1 ambiguity resolution; expected count ~821 |
| G12 | `documents/Codex_Project_Documentation.pdf` | `documents/codex/Codex_Project_Documentation.pdf` | New `documents/codex/` sub-dir for Codex docs |
| G13 | `documents/Codex_Workflow_Cheatsheet_v1.txt` | `documents/codex/Codex_Workflow_Cheatsheet_v1.txt` | Same |
| G14 | `documents/codex-build-progress.md` | `documents/codex/codex-build-progress.md` | Same |
| G15 | `codex-build-plan.html` | `codex-build-plan.html` | Codex build plan (priorities P1–P54) |
| G16 | `.claude/personas/CLAUDE.librarian.md` | `.claude/personas/CLAUDE.librarian.md` | Preserves project-codex layout per AC8 (Codex `bootstrap.py` + `test_phase6_full_chain_e2e.py::test_phase6_librarian_persona_files_byte_equivalent` reference `REPO_ROOT/.claude/personas/CLAUDE.librarian.md`; DFDU-style flat `personas/` is a Step 4 v1.1 follow-up). DFDU's auditor persona (`CLAUDE.auditor.md`) co-located here for Library's own Lattice 3.0 sessions. |
| G17 | `Sources/Raw/` | `Sources/Raw/` | Source-archive convention root (README only at extraction) |
| G18 | Curated Codex-class entries from `tasks/{lessons,architect-notes,sessions,auditor-notes}.md` | DEFERRED to Step 4 | See MI-12. Project-codex history at SHA `ccf21b7` referenced as historical record. |
| G19 | `tasks/v1.1-backlog.md` | `tasks/v1.1-backlog.md` | Codex v1.1 backlog (full verbatim move; 100% Codex by design) |
| G20 | Curated Codex-class entries from `CHANGELOG.md` | DEFERRED to Step 4 | See MI-12. Project-codex CHANGELOG at SHA `ccf21b7` referenced. |

## What stayed in project-codex (now archive)

Lattice 2.0 specs (7 `LATTICE_v0.*_SPEC.md` files), superseded Codex spec versions (`CODEX_BUILD_SPEC_v1_1.md`, `v1_2.md`), `documents/lattice/` (13 Lattice 2.0 docs), Lattice 2.0 personas (`.claude/personas/CLAUDE.{architect,auditor,craftsman,scribe}.md`), the 3 lattice-2.0 scripts + their 5 tests (A1), `PROJECT_INDEX.md` (project-codex-specific), `tasks/lattice-extraction-tracker.md`. Project-codex's `CLAUDE.md` + `README.md` rewritten as archive banners (Phase B8).

**A2 originally claimed `test_phase6_full_chain_e2e.py` + `test_steel_thread_tracker.py` + `steel_thread_tracker.py` would also stay — REVOKED in Phase B3** after re-reading each file's docstring + Codex spec cross-references (both tests + the script are explicitly Codex per spec §7 Phase 6 + P14). All three GO to Library, not stay. See MIGRATION-ISSUES.md §A2 for the full revocation trace. (F-1 Auditor observation 2026-05-27 audit, prose drift fixed here.)

## License carry

Project-codex was personal-tool / unlicensed at extraction. Library carries the same posture — no LICENSE file at extraction. Licensing question deferred to Step 4 if Codex is ever published.

## Verbatim discipline confirmations

Per AC4, post-extraction byte-equality verified via `diff`:
- `INGEST_PROCEDURE.md` — VERIFIED in Phase B3
- `SEMANTIC_LINT_PROCEDURE.md` — VERIFIED in Phase B3
