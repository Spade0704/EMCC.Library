# Architect Notes — EMCC.Library

> Active scope notes, open threads, deferred decisions. Auditor MAY READ this for scope context (per `EMCC.DFDU/personas/CLAUDE.auditor.md` allow-list — `tasks/lessons.md` and `tasks/plans/` are off-limits; this file is not).

## S001-codex-extraction (2026-05-27) — Architect plan

### Goal
Extract Codex (Librarian protocol) from `spade0704/project-codex` to this repo. **Mechanical relocation only**; spec changes deferred to a follow-up "Codex v1.0 → v1.1 update" session (master plan Step 4).

### Source-of-truth references
- Master plan: `/root/.claude/plans/check-the-dfdu-project-bubbly-knuth.md` (operator-approved 2026-05-27)
- Source repo HEAD at session start: `ccf21b7` on `spade0704/project-codex@main` (S048-session-close, 2026-05-25)
- Destination branch (this repo): `claude/lattice-3-production-check-Rdkfu`
- DFDU production-ready stamp: Session 8 / `f056f81` (2026-05-27)

### Goes/stays inventory (locked)

**GOES → EMCC.Library:**

| # | Path in project-codex | Kind |
|---|---|---|
| G1 | `bootstrap.py` | Codex entry |
| G2 | `CODEX_BUILD_SPEC_v1_3.md` | Spec (single canonical per locked decision; v1_1/v1_2 stay as historical archive) |
| G3 | `CODEX_LIBRARIAN.md` | Librarian agent spec |
| G4 | `INGEST_PROCEDURE.md` | Doctrine (verbatim) |
| G5 | `SEMANTIC_LINT_PROCEDURE.md` | Doctrine (verbatim) |
| G6 | `PROJECT_WIKI_BUILD_SPEC.md` | Wiki build spec |
| G7 | `Obsidian-Setup-Guide.md` | Consumer guidance |
| G8 | `_scripts/` minus 3 lattice-2.0 scripts (see A1) | Automation |
| G9 | `_template/` (26 wiki template files) | Templates |
| G10 | `_config/` (5 YAML + README) | Config |
| G11 | `tests/` minus 5 lattice-2.0 tests + 2 lattice-tactical tests (see A1, A2) | Test suite (~821 tests) |
| G12 | `documents/Codex_Project_Documentation.pdf` | Doc |
| G13 | `documents/Codex_Workflow_Cheatsheet_v1.txt` | Cheatsheet |
| G14 | `documents/codex-build-progress.md` | Build progress log |
| G15 | `codex-build-plan.html` | Build plan |
| G16 | `.claude/personas/CLAUDE.librarian.md` | Persona |
| G17 | `Sources/Raw/` | Source-archive convention root (currently README only) |
| G18 | Codex-class entries curated from `tasks/{lessons,architect-notes,sessions,auditor-notes}.md` | Curated migration |
| G19 | `tasks/v1.1-backlog.md` | Codex v1.1 backlog |
| G20 | Codex-class entries curated from `CHANGELOG.md` | Curated migration |

**STAYS in project-codex (archive):**

`CLAUDE.md` (rewritten as archive banner), `README.md` (rewritten as archive banner), all 7 `LATTICE_v0.*_SPEC.md` files, `CODEX_BUILD_SPEC_v1_1.md` + `v1_2.md` (historical), `PROJECT_INDEX.md`, `documents/lattice/` (13 files), `.claude/personas/{architect,auditor,craftsman,scribe}.md`, `.claude/settings.json`, `tasks/lattice-extraction-tracker.md`, `tasks/{lessons,architect-notes,sessions,auditor-notes}.md` (post-curation residue), `tasks/todo.md` (with strikethroughs), `tasks/archive.md`, `0-Inbox/`, `.gitignore`, plus the A1/A2 carry below.

### Ambiguities flagged (audit gate)

**A1.** `_scripts/lattice-bridge.py`, `_scripts/lattice_session_start.py`, `_scripts/lattice_valid_roles_audit.py` + their 5 tests (`test_lattice_bridge*.py`, `test_lattice_session_start.py`, `test_lattice_valid_roles_audit.py`) are Lattice 2.0, not Codex. **Decision: STAY** in project-codex archive.

**A2.** `test_phase6_full_chain_e2e.py` and `test_steel_thread_tracker.py` — Phase 6 / steel threads were Lattice 2.0 tactical work, not Codex. **Decision: STAY** in project-codex archive. (Note: `steel_thread_tracker.py` script also STAYS.)

**A3.** **VERIFY (in Phase B1)** that `bootstrap.py` and the remaining Codex `_scripts/` have no Python imports from A1's three lattice-2.0 scripts before removing them from the GOES set. If imports exist, either fold the import target into Codex (rename to remove "lattice" prefix) or leave the dependency edge as a documented carry.

### Sub-phase decomposition

**B1. Pre-extraction prep.**
- Rename `0. Inbox/` → `0-Inbox/` (locked canonical naming) — done in Phase A
- A3 cross-module import verification: grep `bootstrap.py` + all GOES `_scripts/` for `import lattice_` / `from lattice_` / `lattice-bridge` / `lattice_session_start` / `lattice_valid_roles_audit` references; document findings
- Create `pyproject.toml` (declares `librarian` package + DFDU as dev dep for protocol-following)
- Extend `.gitignore` with Codex test artifacts (`tests/fixtures/source_delta/`, etc., per project-codex pattern) + bus state if added later

**B2. Bootstrap files.**
- `CLAUDE.md` (light version — points at DFDU canon, declares this as a consumer of DFDU AND a producer of Codex)
- `module.json` (mirrors DFDU pattern; `module_type: protocol-wrapper`; `produces_for: [...]`; `consumes: [DFDU]`)
- `SOURCE-HISTORY.md` (pointer to project-codex SHA `ccf21b7`; date; license carry)
- `MIGRATION-ISSUES.md` (append-only registry header; references DFDU's MI-01..MI-08 convention)
- `README.md` (replace not-ready placeholder with production-ready text)
- `.github/workflows/test.yml` (matches DFDU pattern: pytest + python 3.11; pinned `actions/checkout@v4` + `actions/setup-python@v5`)
- `requirements.txt` + `requirements-dev.txt` (Codex's actual runtime + dev deps — read from project-codex test imports if no manifest exists)
- `personas/CLAUDE.auditor.md` (copy from DFDU verbatim — same 116-line file)
- `personas/CLAUDE.librarian.md` (G16 — copy from project-codex `.claude/personas/`)
- `TIERS.md` (optional — only if Codex has Subagent-N analogue; deferred to Phase B2 if not)

**B3. Relocate G1–G17.**
- Copy files from project-codex to corresponding Library paths (mechanical; preserves layout aside from inbox rename)
- For root-level docs (`G1, G2, G3, G4, G5, G6, G7, G15`), destination = Library root (matches project-codex layout)
- For `_scripts/`, `_template/`, `_config/`, `Sources/Raw/`: destination = same relative path
- For `tests/`: destination = same; rewire any hardcoded `project-codex/` paths (likely none — Codex was designed path-agnostic)
- For `documents/Codex_*`: destination = Library `documents/codex/` (new sub-directory for Codex docs)
- For G16 persona: destination = Library `personas/CLAUDE.librarian.md` (no `.claude/` nesting — matches DFDU's flat `personas/` pattern)
- Record source SHA + per-file destination in `SOURCE-HISTORY.md`
- Wiki dogfood note: existing `wiki.codex/` stays in current location and layout (operator decision; F7/F8 folder restructure happens in Step 4)

**B4. Curated migration: tasks/* + CHANGELOG.**
- For each of project-codex's `tasks/{lessons,architect-notes,sessions,auditor-notes}.md`: extract Codex-class entries (anything tagged with codex/librarian/ingest/wiki concerns) → append to Library's corresponding `tasks/` files; leave Lattice-class entries in project-codex
- For `tasks/v1.1-backlog.md` (G19): full move (it's Codex-only)
- For `CHANGELOG.md` (~337KB): extract Codex-class lines → new `CHANGELOG.md` at Library root with timestamps preserved; Lattice-class lines stay in project-codex's CHANGELOG
- Curation criterion: anything that references Codex agent spec / bootstrap / ingest / semantic lint / template / config / spec versions is Codex-class. Lattice 2.0 (bridge, session_start, valid_roles_audit, steel_thread, telegram_l1_l2, scribe spec, etc.) is Lattice-class.

**B5. Test infrastructure rewire + pytest green.**
- Run `pytest tests/` from Library root post-relocation
- Expected count: ~821 (826 − 5 lattice-bridge − ? lattice-tactical, refined during B3)
- Fix import paths if any test references `project-codex/...` directly (likely zero — verify)
- Add `tests/__init__.py` if needed
- Tests must pass before B6

**B6. Synthetic wiki bootstrap validation.**
- Run `python bootstrap.py /tmp/extraction-validation-wiki` from Library root
- Verify: scaffold succeeds; all dashboards build; all validators pass with 0 errors
- This validates end-to-end Codex still works after extraction

**B7. EMCC consumer template flip (cross-repo edit on EMCC's branch).**
- Edit `EMCC/templates/consumer-project/emcc.modules.json`: `library.status` `"not-ready"` → `"ready"`
- Commit on `claude/lattice-3-production-check-Rdkfu` in EMCC repo

**B8. project-codex archive disposition (cross-repo edits on project-codex's branch).**
- Replace `CLAUDE.md` content with archive banner pointing at EMCC.Library + EMCC.DFDU
- Replace `README.md` content with archive notice
- Apply strikethroughs to `tasks/todo.md` items now done by Library
- Commit on `claude/lattice-3-production-check-Rdkfu` in project-codex repo

**B9. Auditor dispatch + verdict + Session 1 close.**
- Construct `audit_request` payload: this architect plan + acceptance criteria + post-extraction artifact summary (file moves, test count, bootstrap synth validation result)
- Build prompt via DFDU's `build_auditor_prompt` helper (importable from `EMCC.DFDU/scripts/lattice_scripting/audit/dispatch_adapters.py`)
- Dispatch Auditor via Claude Code Agent tool with fresh context
- Read `audit_result`; record verdict + findings in Boris log Session 1 close entry
- If `pass`: close Session 1
- If `concerns`: address each; re-dispatch if needed; close on `pass`
- If `block`: surface to operator; do not commit final state

### Acceptance criteria (AC1–AC8)

- **AC1.** All G1–G20 items relocated to Library. ~821 tests pass post-relocation (refined count established in B5).
- **AC2.** `python bootstrap.py /tmp/synth-wiki` succeeds from Library root; synthetic wiki passes its own validators with 0 errors.
- **AC3.** Library has full module-level bootstrap: `CLAUDE.md`, `module.json`, `tasks/{todo,sessions,architect-notes,lessons,archive}.md`, `SOURCE-HISTORY.md`, `MIGRATION-ISSUES.md`, `pyproject.toml`, `.github/workflows/test.yml`, `personas/CLAUDE.{auditor,librarian}.md`.
- **AC4.** `INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` byte-equal between project-codex source and Library destination (verbatim discipline preserved). Verify via `diff` after B3.
- **AC5.** EMCC `templates/consumer-project/emcc.modules.json` Library status flipped `not-ready` → `ready`.
- **AC6.** project-codex archive banners applied to `CLAUDE.md` + `README.md`; `tasks/todo.md` Library-related items struck through with reference to Library Session 1.
- **AC7.** Auditor verdict on extraction: `pass` (or `concerns` with documented resolution + re-audit `pass`).
- **AC8.** No Codex spec content changes during extraction — pure relocation. Any spec edits required for relocation paths (e.g., `_scripts/` path references in `CODEX_BUILD_SPEC_v1_3.md` if any) are flagged for Step 4 follow-up rather than edited mid-extraction.

### Auditor dispatch plan

- **Trigger basis:** schedule (sprint close at extraction completion) + risk (Level-2+ cross-repo + 50+ file moves + new module ship)
- **Mechanism:** Claude Code Agent tool dispatch using fresh context. If `EMCC.DFDU.scripts.lattice_scripting.audit.dispatch_adapters.build_auditor_prompt` is importable from the session env, use it verbatim. Else inline-construct an equivalent prompt that includes: Auditor persona content + audit_request payload + envelope-writing instructions per §4.
- **Auditor persona content:** `EMCC.DFDU/personas/CLAUDE.auditor.md` embedded in dispatch prompt (canonical 116-line version)
- **Audit envelope payload includes:**
  - This architect plan §S001
  - AC1–AC8
  - File-by-file move summary (source SHA + destination path for each G1–G20)
  - Test result summary (count + duration + zero-regression confirmation)
  - Bootstrap synth validation transcript
  - Cross-repo summary (B7 + B8 commits)
- **Verdict integration:** Written to Boris log Session 1 close entry; full envelope content saved in `tasks/architect-notes.md` §S001-audit-result section

### Deferred to Step 4 (Codex v1.0 → v1.1 update session)

- Operator's portfolio-room refined folder-structure spec (resolves F1–F11; drives `Biz.Automation/wikisys.<projectname>/` vs `wiki.<projectname>/` split for consumer wikis)
- Mentor wiki report findings
- 5 deferred Librarian-spec items from EMCC `tasks/todo.md` (TF-IDF cross-link curation, routing tag work queue, Maintenance loop tag-scan, three-tier tag namespace authority, plug-in failure handling)
- S048-T1 findings from project-codex (if/when that sprint closes)
- Spec edits surfaced during AC8 (path references, etc.)
- Library's own dogfood wiki rebuild under new folder layout
- Bus infrastructure for Library's own Lattice 3.0 sessions (if Library becomes its own Lattice 3.0 client beyond ad-hoc dispatches)
