# Migration Issues Registry — EMCC.Library

Append-only registry of issues encountered during the Codex extraction (Session 1 / master plan Step 3) and any subsequent module-extraction-related work in Library.

Mirrors the convention established by `EMCC.DFDU/MIGRATION-ISSUES.md` which extends `EMCC.DFDU/documents/lattice/10-MIGRATION-TRIGGERS.md` §2. Where DFDU's registry covers Lattice 2.0 → Lattice 3.0 extraction, this registry covers Codex (from project-codex) → Library.

## Canonical issues inherited from DFDU's registry (Codex-relevant only)

| # | Issue | Resolution at Library Phase 1 (Session 1) |
|---|---|---|
| **MI-01** | Hardcoded paths in scripts | Not encountered at extraction. Codex scripts use `pathlib.Path(__file__).resolve().parent...` patterns + a `_scripts/_lib/config_loader.py` discovery layer. Path-agnostic by design (per `CODEX_BUILD_SPEC_v1_3.md` R_ARCH "always use pathlib.Path; never raw string concatenation"). |
| **MI-02** | Shared utility scripts | Not encountered. Codex `_lib/` (frontmatter, markdown, topics, dashboard, doc_lint, config_loader) is Codex-only; DFDU `lattice_scripting/` is DFDU-only. No cross-module imports. |
| **MI-03** | CLAUDE.md cross-refs | project-codex `CLAUDE.md` and `README.md` rewritten as archive banners in Phase B8 (this session), pointing readers at EMCC.Library and EMCC.DFDU. EMCC.Library's own `CLAUDE.md` (this commit) is freshly authored — references DFDU canon at `EMCC.DFDU/documents/lattice/`. |
| **MI-04** | CI/Actions | RESOLVED at Phase B2 (this commit). `.github/workflows/test.yml` runs `python -m unittest discover -s tests -t .` on Python 3.11. No `pip install` step — Codex spec mandates stdlib-only (per AC8 "no spec changes during extraction"). |
| **MI-05** | History loss from clean-slate | Accepted. Source commit SHA `ccf21b7` recorded in `SOURCE-HISTORY.md`. Per-file destination paths also recorded there. Library starts at `094e8a3` (Phase A: session-open commit) before any source files arrived. |
| **MI-06** | Bootstrap referencing legacy templates | Not encountered at extraction. Codex's `bootstrap.py` uses `Path(__file__).resolve().parent / "_template"` for template lookup — moves cleanly to Library. `SCRIPT_IGNORE_PATTERNS` at `bootstrap.py:46-52` keeps defensively the `lattice_*.py` + `lattice-bridge.py` exclusions even though those files now live only in project-codex — harmless inert defense. |
| **MI-07** | Active development during migration | project-codex's S048 (operational mini-cycles, no spec changes) was the in-flight work surface; S048 is OPEN at extraction trigger. project-codex archive disposition (Phase B8) handles the strikethrough of Library-related items in `tasks/todo.md`; the rest of S048 stays operationally relevant to project-codex's archive state. |
| **MI-08** | Renames mid-migration | None this session. Codex spec, scripts, and tests all kept their existing names. Personas relocate from `.claude/personas/` (project-codex layout) → `personas/` (DFDU/Library flat-personas layout) — that is a path move, not a rename. Pattern matches DFDU's MI-08 resolution: "rename sweep" lands in the spec maturation phase (Step 4 Codex v1.1 update), not during extraction. |

## Phase 1 (this session) issues encountered

### A1 — Lattice 2.0 scripts entangled with Codex test suite

**Discovered:** Pre-flight inventory (Phase A architect plan, 2026-05-27).

**Description:** `_scripts/lattice-bridge.py`, `_scripts/lattice_session_start.py`, and `_scripts/lattice_valid_roles_audit.py` plus their 5 tests (`test_lattice_bridge.py`, `test_lattice_bridge_dedupe.py`, `test_lattice_bridge_state.py`, `test_lattice_session_start.py`, `test_lattice_valid_roles_audit.py`) live in Codex's `_scripts/` and `tests/` directories but are Lattice 2.0 infrastructure, not Codex protocol.

**Resolution:** STAY in project-codex archive. Library extraction excludes these 8 files. A3 cross-module import verification (this session, Phase B1) confirmed Codex GOES scripts have NO functional imports of these files — the two grep hits (`bootstrap.py:50` defensive `SCRIPT_IGNORE_PATTERNS` entry; `build_canon_drift_report.py:350` historical docstring comment) are both inert. Library's test count post-extraction: ~821, not 826 (acceptance criterion AC1 updated accordingly).

### A2 — Lattice 2.0 tactical tests in Codex test suite

**Discovered:** Pre-flight inventory (Phase A architect plan, 2026-05-27).

**Description:** `test_phase6_full_chain_e2e.py` and `test_steel_thread_tracker.py` (plus the script `steel_thread_tracker.py`) cover Lattice 2.0 tactical work (Phase 6 = bridge dogfood E2E; steel threads = Lattice 2.0 feature-tracking convention). Not Codex.

**Resolution:** STAY in project-codex archive. Library exclusion noted in A1's count refinement.

### A3 — Cross-module import verification (preventive)

**Discovered:** Phase B1 pre-extraction verification (this session).

**Description:** Before removing A1's 8 files from the GOES set, verified that Codex's `bootstrap.py` and remaining `_scripts/` have no Python imports of the lattice-2.0 scripts.

**Resolution:** VERIFIED. Two grep hits, both inert: `bootstrap.py:50` (defensive ignore pattern; harmless if pattern target doesn't exist) and `build_canon_drift_report.py:350` (docstring comment, no code dependency). Safe to remove A1's files from GOES.

## Open items deferred to Step 4 (Codex v1.0 → v1.1 update)

- **MI-09 (potential, deferred):** Folder restructure under `Biz.Automation/wikisys.<projectname>/` + `wiki.<projectname>/` split, per operator's first-draft consumer-project layout (2026-05-27). Resolution depends on portfolio-room refined spec (F1–F11). Mechanical extraction (this session) preserves current single-root layout to keep the relocation cleanly auditable; restructure happens in Step 4.
- **Spec edits surfaced during AC8:** Any `_scripts/` path references in `CODEX_BUILD_SPEC_v1_3.md` that need adjustment for the Library home — captured as Step 4 follow-up rather than edited mid-extraction.
