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

### A2 — Initial misclassification of two Codex tests as Lattice tactical (REVOKED in Phase B3)

**Discovered:** Pre-flight inventory (Phase A architect plan, 2026-05-27).

**Initial (incorrect) classification:** `test_phase6_full_chain_e2e.py` and `test_steel_thread_tracker.py` (plus the script `steel_thread_tracker.py`) called as Lattice 2.0 tactical work (Phase 6 = bridge dogfood E2E; steel threads = Lattice 2.0 feature-tracking convention).

**Revocation (Phase B3, 2026-05-27):** Re-reading the actual files showed both are explicitly Codex:
- `steel_thread_tracker.py` docstring: "P14 validator (v1.0). Spec contract: CODEX_BUILD_SPEC_v1_2.md §2.4 row 11" — it's Codex's P14 script, listed in project-codex CLAUDE.md R_LOGIC D_SERVICES table alongside the other 14 Codex automation scripts.
- `test_phase6_full_chain_e2e.py` docstring: "Per CODEX_BUILD_SPEC_v1_3.md §7 Phase 6 self-test invariants + CLAUDE.md D_VERIFICATION Stage 5" — it's Codex's spec §7 Phase 6 self-test (bootstrap + sync + scaffolds + Librarian wiring), the SHIP-readiness final gate.

**Final resolution:** BOTH GO to Library. The initial misclassification was a naming-overlap error: "Phase 6" appears in both Codex's spec §7 build phases AND Lattice 2.0's bridge dogfood phase numbering; "steel threads" is generic-enough phrasing that I mistook it for Lattice 2.0's concept. Lesson for capture after session close: verify any "this stays in archive" classification by reading the file's docstring + spec cross-reference before locking it.

**Net effect on Library test count:** Same as A1 alone — 5 lattice-bridge tests stay; expected post-extraction count = total − 5 (~821 by initial spec, refined in B5).

### A3 — Cross-module import verification (preventive)

**Discovered:** Phase B1 pre-extraction verification (this session).

**Description:** Before removing A1's 8 files from the GOES set, verified that Codex's `bootstrap.py` and remaining `_scripts/` have no Python imports of the lattice-2.0 scripts.

**Resolution:** VERIFIED. Two grep hits, both inert: `bootstrap.py:50` (defensive ignore pattern; harmless if pattern target doesn't exist) and `build_canon_drift_report.py:350` (docstring comment, no code dependency). Safe to remove A1's files from GOES.

## Phase 2 (S002 / v1.1 update arc) issues encountered

### MI-14 — Stale `wiki.codex/_scripts/` bootstrap output discovered during B4

**Discovered:** Phase B4 (2026-05-27) during wiki.codex/ restructure inventory.

**Description:** `wiki.codex/_scripts/` contained 27 tracked Python files that were bootstrap output from a pre-S048-T0 sync of project-codex into the dogfood wiki. 4 of the 27 files (`_lib/doc_lint.py`, `_lib/frontmatter.py`, `check_concept_coverage.py`, `cross_link_topics.py`) drifted backward — the wiki.codex copies were *older* (mtimes 2026-05-16 → 2026-05-22) than the post-Session-1 canonical at `Biz.Automation/wikisys.library/_scripts/` (mtimes 2026-05-27, includes S048-T0 SPEC_2_3_FM_FIELDS SSOT cure). The remaining 23 files were byte-equal to the canonical.

**Resolution:** `git rm -r wiki.codex/_scripts/` in B4 (commit pending). The dogfood wiki's _scripts/ drop-in will be regenerated by post-B5 `bootstrap.py` execution against `Biz.Automation/wikisys.library/_scripts/` (the new canonical source). No content lost — the canonical wikisys.library copy IS the newer version.

**Net effect:** Library tree no longer carries two divergent copies of Codex automation scripts. Post-B5, `bootstrap.py` regenerates `wiki.codex/git/_scripts/` (or equivalent — depends on canonical-output tree decision) as drop-in for the dogfood wiki, sourced from wikisys.library.

### MI-16 — sync_from_kit v1.1 contract rewrite (RESOLVED in S004; was: v1.0 shape tests retired + rewrite deferred to S004)

**Discovered:** Phase B5b (2026-05-27) during bootstrap.py canonical-output rewrite per spec section (c).

**Description:** v1.1 `bootstrap.py` is a SCAFFOLD-ONLY rewrite per `tasks/plans/portfolio-folder-structure-spec.md` section (c). It emits the canonical portfolio frame (`0-Inbox/`, `Biz.Automation/wikisys.<name>/_*/.gitkeep`, `wiki.<name>/{git,local}/`, `tasks/{todo,sessions,lessons,archive}.md`, `assets/<6 subfolders>/.gitkeep`, root stubs `Index.md`/`CLAUDE.md`/`Cheatsheet.md`/`.gitignore`) — but does NOT copy Codex's `_scripts/` / `_template/` / `_config/` contents into the consumer wiki. Script + template delivery is `sync_from_kit.py`'s job (Sync operation per spec §4.2).

This is a fundamental contract change from v1.0:
- **v1.0 bootstrap** = copy Codex scripts + templates into the consumer wiki (`mentor/_scripts/`, `mentor/_template/`, etc.).
- **v1.1 bootstrap** = scaffold-only (no `_scripts/`, no `_template/`, no `_context/` inside the consumer wiki).

5 test files retire as MI-16 because they assert v1.0 contract end-to-end:

| Test file | Test count | What it asserts |
|---|---|---|
| `tests/test_bootstrap.py` | 44 | v1.0 CLI signature + 15-script copy + `__SEP__` template substitution + WIKI_FOLDERS Lattice-2.0-flavored output |
| `tests/test_t1_p52_bootstrap_operation.py` | 10 | v1.0 bootstrap end-to-end with 25-script copy + `_canon/topics.yaml`/`_config/cross_link.yaml` placement |
| `tests/test_t2_p53_sync_operation.py` | 19 | v1.0 sync_from_kit precedence map against bootstrap-output wikis |
| `tests/test_t3_p54_ingest_operation.py` | 10 | v1.0 ingest-readiness static infrastructure (`_sources/raw/`, `_inbox/`, `_decisions/ingest-log.md`) |
| `tests/test_phase6_full_chain_e2e.py` | 8 | v1.0 SHIP-readiness full-chain (bootstrap + sync + scaffold + Librarian wiring) |

All 5 files raise `unittest.SkipTest` at module import time with MI-16 reason. Net: 88+ tests skipped (discovery time; not counted in suite total).

**S004 (consumer wikis sprint) inherits two coupled decisions:**

1. **Where does post-v1.1 sync deliver procedure docs?** spec (c) consumer wiki tree has no `_context/`. Options:
   - (a) Sync delivers procedure docs to `Biz.Automation/wikisys.<name>/_context/` (operator-facing system-side location).
   - (b) Sync delivers nothing into the consumer wiki; the consumer's Claude session reads procedure docs directly from the Library install via path indirection.
   - (c) Spec (c) extends with a hidden `_context/` in the wiki — operator's call.

2. **How do legacy v1.0 wikis migrate forward?** Existing pre-S002 wikis bootstrapped with v1.0 still have `_scripts/`, `_template/`, `_context/` at their root. Sync_from_kit currently expects this shape. Options:
   - (a) Sync_from_kit ships with a v1.0-compat detection mode (reads consumer wiki shape; writes to old paths if v1.0, new paths if v1.1).
   - (b) Force-migrate: a one-shot `migrate_v1_to_v1_1.py` script rewrites legacy wikis into new shape.
   - (c) Accept that v1.0 wikis frozen; only new bootstraps get v1.1 shape; legacy stays maintainable in v1.0 forever.

**S002 disposition:** Retire the 5 deprecated-shape test files; ship 21 new canonical-shape tests in `tests/test_bootstrap_canonical.py` covering --full / --minimal / --code / --website / idempotency-and-safety / CLI parser. `sync_from_kit.py` unchanged in S002 (still v1.0 contract; broken in practice against v1.1-bootstrap wikis but the path-lookup updates in B5a keep its source-side reads correct for the new Library layout).

**Net test suite delta (S001 → S002):**
- S001 baseline: 615 tests / 611 pass / 3 fail / 1 skip
- S002 close: 548 tests / 540 pass / 2 fail / 6 skipped-modules (~88 tests retired under MI-16)
- 21 new canonical-shape tests added
- 1 baseline fail dropped (test_phase6_librarian_persona_files_byte_equivalent was in test_phase6_full_chain_e2e.py — now module-skipped)
- MI-10 fail (test_check_frontmatter_persona_class_drop_ins_lint_clean) remains until B9 generalizes the test.

**Implementation deviation from spec (c) §`--code` mode:** Spec (c) says `--code adds mentor/<product-code-root>/.gitkeep`. The literal placeholder `<product-code-root>` contains Win32-illegal chars (`<`, `>`). v1.1 bootstrap.py emits NO folder placeholder for --code; operator names + creates the actual code root (Flutter `lib/`, Python `src/`, etc.). --code's contribution is the code-aware .gitignore additions only. Spec text reads as guidance pattern, not literal output.

### MI-15 — Sources/Raw/ legacy README superseded by wiki-internal canonical

**Discovered:** Phase B4 (2026-05-27) during sources merge.

**Description:** Two READMEs lived in the source/raw zones:
- `Sources/Raw/README.md` at Library root (4-line stub: "Drop all your original DOCX, PDF, HTML files here. Codex will later process...") — project-codex-legacy convention.
- `wiki.codex/_sources/raw/README.md` (60+ lines: Ingest semantics, canon_sources discipline, versioning) — canonical wiki-internal convention.

**Resolution:** B4 kept the canonical wiki-internal version (`wiki.codex/_sources/raw/README.md` → `wiki.codex/git/raw/README.md`). The root `Sources/Raw/README.md` was deleted as superseded. Root `Sources/` shell removed (now empty).

### MI-17 — Codex scripts' WIKI_ROOT defaults broken at Library install post-restructure

**Discovered:** 2026-05-27 post-PR-#4 CI red diagnostic (S002 wrap).

**Description:** Every Codex script under `Biz.Automation/wikisys.library/_scripts/` defines its own `WIKI_ROOT = Path(__file__).resolve().parent.parent` (2 levels up from the script). `_lib/frontmatter.py` defines `WIKI_ROOT = Path(__file__).resolve().parent.parent.parent` (3 levels up, since it's one level deeper). Both worked when `_scripts/` lived at the install/wiki root. After S002's restructure (`_scripts/` moved to `Biz.Automation/wikisys.library/_scripts/`), these path-walks now resolve to `wikisys.library/` instead of Library's repo root.

For BOOTSTRAPPED CONSUMING WIKIS the old math still works correctly (the bootstrapped layout retains `<wiki>/_scripts/` at the wiki root), so production usage is unaffected. The break only manifests when Codex scripts are invoked from Library's install location without an explicit wiki-path argument — primarily caught by `tests/_lib/test_frontmatter.py::test_wiki_root_resolves_correctly` since the other 13 scripts' default `WIKI_ROOT` isn't covered by their tests.

**Partial resolution (PR #6 era, 2026-05-27 morning):** `_lib/frontmatter.py::WIKI_ROOT` rewritten to use marker-based ancestor walk (`Home.md` for bootstrapped wikis OR `CLAUDE.md` + `module.json` co-existing for Library install). Handles both contexts correctly. Test updated to assert against either marker set. Result: 589/589 tests pass.

**Full resolution (this commit — S002f follow-up):** Three changes land:

1. **`find_wiki_root()` enhanced** in `_lib/frontmatter.py` — adds Case 2 detection: when an ancestor has `CLAUDE.md` + at least one `wiki.<name>/git/Home.md` subpath, return that wiki content dir. Library install now resolves WIKI_ROOT to `wiki.codex/git/` (the content side) instead of Library repo root (install side); future v1.1-bootstrapped consumer projects resolve similarly to `<project>/wiki.<name>/git/`. Public function (renamed `_find_wiki_root` → `find_wiki_root`); back-compat alias preserved.

2. **All 17 scripts updated** to use `WIKI_ROOT = frontmatter.find_wiki_root()` in place of the broken `parent.parent` walk: `check_framework_briefing_sync.py`, `steel_thread_tracker.py`, `build_topic_index.py`, `validate_terminology.py`, `validate_canon_integrity.py`, `delta_source_docs.py`, `validate_reveal_conceit.py`, `build_completion_dashboard.py`, `check_cascade.py`, `check_canon_consistency.py`, `update_dashboards.py`, `build_canon_drift_report.py`, `collect_open_questions.py`, `check_cross_refs.py`, `cross_link_topics.py`, `check_concept_coverage.py`, `validate_topic_registry.py`. `frontmatter` import added to the 2 scripts that didn't already have it (`steel_thread_tracker.py`, `build_canon_drift_report.py`).

3. **`.gitignore` extended** with `wiki.codex/git/_dashboards/` (the new canonical output location post-fix). Previous `wiki.codex/_dashboards/` rule retained for backward-compat with any wiki.codex-internal _dashboards/ artifact still on disk.

**Verified end-to-end:** Running `python Biz.Automation/wikisys.library/_scripts/update_dashboards.py` from Library root now produces real dashboards at `wiki.codex/git/_dashboards/` reflecting Library's actual dogfood wiki content (27 pages tracked, 37% avg completion, 20/34 cross-link coverage). 16 of 17 sub-scripts emit clean dashboards. The 17th (`check_concept_coverage.py`) fails on missing `_canon/roster.yaml` — surfaced as MI-18.

**Full closure (post-S004 carry — this commit):** Two coupled changes land, resolving the per-script CLI gap and the dashboard-output leak that the S002/S004 partial fixes left open.

1. **Content-root resolver** — `_lib/frontmatter.py::find_wiki_content_root()`. The S002 partial fix pointed scripts at `find_wiki_root()`, which for a v1.1 install returns the *install root* (`EMCC.Library/`), not the content side. Symptom: standalone runs wrote dashboards to `<install>/_dashboards/` (a non-gitignored repo-root leak) and scanned the whole repo for content pages. The new helper returns the v1.0 wiki root unchanged but descends a v1.1 install to `<install>/wiki.<name>/git/`. All 17 dashboard/validator scripts switched their module-level `WIKI_ROOT` to it; dashboards now land at `wiki.codex/git/_dashboards/` (already gitignored) and page-walks scan only the content side. Matches Mentor's S004 F12 content-side convention.

2. **Per-script `--wiki-root` CLI** — new `_lib/cli.py::resolve_cli_wiki_root()`. Previously only `update_dashboards.py` accepted an explicit root (bare positional). Every standalone P-script `__main__` now rebinds `WIKI_ROOT` via the shared helper, accepting `--wiki-root PATH` or a bare positional (named wins). `build_canon_drift_report.py` got `--wiki-root` added to its own argparse (it has `--snapshot`). `delta_source_docs.py` keeps its bespoke `<version_a> <version_b>` positional contract (already takes `wiki_root` as a param; module default now points content-side).

**Verified:** `build_completion_dashboard.py` standalone writes to `wiki.codex/git/_dashboards/completion.md` (27 pages, content side — no more repo-root leak); `--wiki-root tests/fixtures/sample_wiki` correctly retargets (5 pages). 615 tests pass (+10: 5 `find_wiki_content_root` + 5 `resolve_cli_wiki_root`). **Status: RESOLVED.**

### MI-18 — `_canon/` lookup divergence for system-vs-content split (surfaced post-MI-17)

**Discovered:** 2026-05-27 immediately after MI-17 fix landed — first time `update_dashboards.py` correctly targeted `wiki.codex/git/` and `check_concept_coverage.py` ran with a real WIKI_ROOT.

**Description:** Several validator/dashboard scripts read `_canon/*.yaml` files from `<WIKI_ROOT>/_canon/`. In v1.0-shape wikis (Mentor, future bootstrapped consumers), `_canon/` lives at the wiki root — works. In Library's v1.1 layout, `_canon/` was extracted to `Biz.Automation/wikisys.library/_canon/` (system side, per portfolio spec F6), and `wiki.codex/git/` (content side) has no `_canon/` subfolder. Scripts that hardcode `WIKI_ROOT / "_canon"` now fail when run against Library's dogfood wiki.

Surfaced concretely by `check_concept_coverage.py`:
```
P13 check_concept_coverage -- FAILED:
FileNotFoundError: required canon file missing:
/home/user/EMCC.Library/wiki.codex/git/_canon/roster.yaml
```

Same structural concern likely applies to `_decisions/ingest-log.md` reads (the "Recent Ingest" section of `health.md` shows empty for Library — the dashboard generator can't find the ingest log on the content side because the log lives at `wikisys.library/_decisions/ingest-log.md` system-side).

**Resolution options (deferred to S004 or dedicated sprint):**

- (a) **Make canon lookup canonical-layout aware** — scripts try `<WIKI_ROOT>/_canon/` first, fall back to `<install_root>/Biz.Automation/wikisys.<name>/_canon/` for Library/v1.1-consumer layouts. Same for `_decisions/`. Adds layout-detection to each affected script.
- (b) **Symlink/copy canon into wiki content side** — `<wiki_root>/_canon/` becomes a pointer to `<install_root>/wikisys.<name>/_canon/`. Simpler at the script level but requires bootstrap.py to create the link/copy.
- (c) **Factor canon-discovery into `_lib/config_loader.py` or new `_lib/canon.py`** — analogous to `find_wiki_root()`; scripts call `find_canon_dir(wiki_root)`. Most architectural; matches the marker-walk pattern.

**Recommendation:** Option (c) for consistency with how MI-17 was resolved. Defer to S004 or a focused S005x sprint; not blocking Library's v1.1 production status (the 16 other sub-scripts work; `check_concept_coverage` was previously also broken — just silently because WIKI_ROOT was wrong; now it fails loudly).

### MI-18 — Canon + decisions lookup divergence post-S002 split (RESOLVED in S004)

**Discovered:** 2026-05-27 during S004 planning. Surfaced explicitly by operator as a coupled fix alongside MI-16 (sync_from_kit v1.1 rewrite). Latent since S002 close.

**Description:** S002 moved `_canon/` and `_decisions/` from the wiki content side to the system side at `Biz.Automation/wikisys.library/_canon/` and `_decisions/`. The 5 Codex scripts that read canon yaml files (`check_concept_coverage.py`, `check_canon_consistency.py`, `build_canon_drift_report.py`, `build_topic_index.py`, `validate_topic_registry.py`) all use `wiki_root / "_canon"` path math. Same with `update_dashboards.py` for `_decisions/ingest-log.md` in the Recent Ingest health.md section.

Symptoms in Library's `health.md` post-S002: Recent Ingest section reads `_No ingest entries yet._` despite `Biz.Automation/wikisys.library/_decisions/ingest-log.md` having content. Same false-empty would manifest in any v1.1 consumer.

**Resolution:** Extend the MI-17 marker-walk pattern in `_lib/frontmatter.py` with two new helpers and an additional consumer-side marker:

- `_find_install_root(start_path)` — walks up looking for `CLAUDE.md` co-existing with either `module.json` (Library install) or `emcc.modules.json` (consumer install).
- `find_canon_dir(start_path=None)` — returns `<start>/_canon/` if exists (v1.0 wiki); else walks up to install root, globs `<install>/Biz.Automation/wikisys.*/_canon/`, returns first match. Raises `FileNotFoundError` on no match.
- `find_decisions_dir(start_path=None)` — same pattern for `_decisions/`.
- Extended `_find_wiki_root()` marker set: added `CLAUDE.md + emcc.modules.json` as v1.1 consumer marker (alongside existing `Home.md` v1.0 marker + `CLAUDE.md + module.json` Library marker).

Updated 5 scripts to use `find_canon_dir()`: `check_concept_coverage.py`, `check_canon_consistency.py`, `build_canon_drift_report.py` (2 sites), `build_topic_index.py`, `validate_topic_registry.py`. Updated `update_dashboards.py::_section_recent_ingest` to use `find_decisions_dir()`. Each script preserves prior graceful-fallback behavior on FileNotFoundError (early-exit with empty dashboard, or empty canon state).

9 new tests in `tests/_lib/test_frontmatter.py::TestCanonAndDecisionsLookup` cover both v1.0 and v1.1 layout fixtures + the new install-root markers.

**Net test suite delta (S002 → S004):**
- S002 close: 589 / 589 / 6 skipped (~88 retired under MI-16)
- S004 C close: 593 / 593 / 6 skipped (+4 from sync_from_kit v1.1 tests)
- S004 D close: 602 / 602 / 6 skipped (+9 from canon+decisions lookup tests)

**Status:** RESOLVED in S004 Phase D.

## S002 dispositions for MI-10, MI-11, MI-12, MI-13 (resolved / carried)

Per S002 architect plan §B9 disposition table:

| MI | Type | Disposition | Status |
|---|---|---|---|
| **MI-10** | Lattice-2 persona drop-in test (>=4 personas hard-asserted) | **Resolved B9**: `tests/test_doc_lint.py::TestCheckFrontmatter::test_check_frontmatter_persona_class_drop_ins_lint_clean` generalized to lint whatever drop-ins ARE present (Library has 2: auditor + librarian); existence-of-Lattice-2-personas assertion retired. Test now passes. | ✅ Done in S002 B9 (commit pending this session) |
| **MI-11** | `test_doc_lint_full_tree.py` empty in Library (`documents/lattice/` doesn't exist) | **Resolved B9**: dynamic-test-generation root repointed from `documents/lattice/` to `wiki.codex/git/codex/` (post-B3 Codex spec docs location). 10 dynamic tests now generate against Library's spec doc set; test class no longer empty. | ✅ Done in S002 B9 (commit pending this session) |
| **MI-12** | Historical `tasks/*` + `CHANGELOG.md` curation deferred | **Carried**: per S001 close decision + S002 architect plan, the editorial work of classifying every line of project-codex's tasks/* (5,223 lines) and CHANGELOG.md (78 dense bullets) as Codex-class vs Lattice-class doesn't affect any AC. Pre-extraction history accessible at project-codex SHA `ccf21b7`; Library's authoritative history starts at S001. Defer to S004 or dedicated curation sub-session. | ⏳ Carried to S004+ |
| **MI-13** | `pyproject.toml` not landed despite architect-plan AC3 | **Resolved as drop**: Codex's stdlib-only discipline (`CODEX_BUILD_SPEC_v1_3.md` R_ARCH) means even a PEP 621 metadata-only `pyproject.toml` adds no value. Library never distributes as a wheel — consumers run `bootstrap.py` + `sync_from_kit.py` directly from a clone or vendored copy. Architect plan AC3 implicit amendment: drop `pyproject.toml` requirement for stdlib-only modules. Re-open only if Library ships wheels (unlikely). | ✅ Done in S002 B9 (decision logged here; no file changes needed) |

## Open items deferred to Step 4 (Codex v1.0 → v1.1 update)

- **MI-09 (potential, deferred):** Folder restructure under `Biz.Automation/wikisys.<projectname>/` + `wiki.<projectname>/` split, per operator's first-draft consumer-project layout (2026-05-27). Resolution depends on portfolio-room refined spec (F1–F11). Mechanical extraction (this session) preserves current single-root layout to keep the relocation cleanly auditable; restructure happens in Step 4.
- **MI-10 (deferred — known test regression):** `tests/test_doc_lint.py::TestCheckFrontmatter::test_check_frontmatter_persona_class_drop_ins_lint_clean` is Lattice-2.0-specific (hard-asserts ≥4 persona drop-ins at `.claude/personas/`, expecting the 4 Lattice 2.0 personas `architect`/`auditor`/`craftsman`/`scribe`). Library has 2 personas at `.claude/personas/` (`auditor` carried verbatim from DFDU + `librarian` from G16); Lattice 2.0 personas STAY in project-codex per locked goes/stays. The test currently FAILS in Library — single net regression vs project-codex baseline (which had 2 pre-existing failures `test_wiki_root_resolves_correctly` + `test_phase6_librarian_persona_files_byte_equivalent`, both env / fixture issues unrelated to extraction). Resolution options for Step 4: generalize the test to count whatever persona drop-ins are present (and lint them under appropriate schema) OR retire the test as Lattice-2.0-specific. Recommended: generalize — the doc_lint smoke check is still valuable for Codex's own personas.
- **MI-11 (deferred — known test inertness):** `tests/test_doc_lint_full_tree.py` dynamically generates one test per `documents/lattice/*.md` at module import time. Library does not have `documents/lattice/` (it stays in project-codex archive); test class is empty in Library (0 tests vs 12 in project-codex). Not a regression — inert by design when the fixture directory is absent. Resolution for Step 4: either generalize the test to iterate `documents/codex/*.md` (Library's own docs dir) or retire as Lattice-2.0-specific.
- **Spec edits surfaced during AC8:** Any `_scripts/` path references in `CODEX_BUILD_SPEC_v1_3.md` that need adjustment for the Library home — captured as Step 4 follow-up rather than edited mid-extraction. Same goes for any internal cross-refs in INGEST_PROCEDURE.md, SEMANTIC_LINT_PROCEDURE.md, CODEX_LIBRARIAN.md, PROJECT_WIKI_BUILD_SPEC.md, codex-build-plan.html that reference project-codex-specific paths.
- **Persona path unification:** Library currently uses `.claude/personas/` for both Codex's Librarian + DFDU's carried-verbatim Auditor (matches project-codex; preserves AC8 — bootstrap.py + test_phase6_full_chain_e2e.py expect this exact path). DFDU itself uses flat `personas/`. Step 4 should reconcile to a single convention org-wide.
- **MI-13 (deferred — pyproject.toml not landed despite architect plan AC3):** Architect plan B2 + AC3 both listed `pyproject.toml` among required Library bootstrap files (mirroring DFDU's pattern). On execution, the Lattice Agent determined Library can match DFDU's actual on-disk pattern (no `pyproject.toml`, no `setup.py`, just `requirements.txt` + `requirements-dev.txt`) — but Codex's stdlib-only discipline (`CODEX_BUILD_SPEC_v1_3.md` R_ARCH: "Pure Python stdlib only. No pip install.") means even `requirements.txt` is unnecessary. CI workflow uses `python -m unittest discover` with no `pip install` step. Architect plan AC3 needs to either (a) be amended to drop `pyproject.toml` as not-applicable for stdlib-only modules, or (b) ship a minimal PEP 621 `pyproject.toml` with metadata-only (no dependencies). Auditor verdict was `pass` with this flagged as F-2 observation (not concerns or block). Defer to Step 4 v1.1 update; pick (a) or (b) based on whether Library will ever distribute as a wheel.
- **MI-12 (deferred — scope reduction on B4 curated migration):** Per architect plan B4, Codex-class entries from project-codex's `tasks/{lessons,architect-notes,sessions,auditor-notes,archive}.md` (5,223 lines combined) and `CHANGELOG.md` (337KB / 78 dense bullets covering v1.0 + S047 dogfood mini-cycles) should be curated and migrated to Library. **Scope reduced in this session** to just `tasks/v1.1-backlog.md` (G19; 59 lines; 100% Codex by design, verbatim move). Historical tasks/* and CHANGELOG curation deferred to Step 4 or a dedicated curation sub-session — the editorial work of classifying every line as Codex-class vs Lattice-class would expand this session significantly without affecting extraction acceptance criteria (AC1–AC8 do not depend on historical-curation completeness). project-codex's pre-extraction tasks/* + CHANGELOG remain accessible at SHA `ccf21b7` and are referenceable from any future curation effort. Library's authoritative history starts at S001 (commit `094e8a3`).

## Cross-consumer issues (post-S004; surfaced during portfolio consumption)

### MI-19 — Stale vendored Codex engine in consumers bootstrapped before `find_wiki_content_root()` (consumer re-sync advisory)

**Discovered:** 2026-06-06, cross-room coordination. One room consuming Library found **Project-Mentor** running a stale vendored Codex engine that predated `find_wiki_content_root()` (the content-root resolver landed under MI-17 "Full closure"). That room fixed Mentor by re-syncing via `sync_from_kit.py` (engine now byte-equal to Library; 631/631 Library tests pass) and flagged that other pre-fix consumers are likely also stale.

**Description:** A consumer that vendored its Codex `_scripts/` engine **before** the MI-17 content-root fix resolves `WIKI_ROOT`/content-root to the **repo root** instead of `<project>/wiki.<name>/git/`. Symptoms (same class MI-17 fixed inside Library): dashboard runs leak output to a stray repo-root `_dashboards/` (not gitignored), and page-walks scan non-content dirs (`tasks/`, `Biz.Automation/`) as wiki content. Library itself is correct — all its scripts call `find_wiki_content_root()`.

**Verified blast radius (read-only scan of each consumer's `Biz.Automation/wikisys.*/_scripts/` on current `main`, 2026-06-06).** Signal = whether the engine defines + calls `find_wiki_content_root` and carries the full 34-file script set:

- **CURRENT** (defines fn + 19 callers, 34 `.py`): `EMCC`, `EMCC.CRW`, `EMCC.Cartometrics`, `EMCC.DFDU`, `EMCC.Guard-House`, `Gateway`, `isommelier`, `project_iron_soul`, `supplystationusa`, `tat_app`, and Library itself. No action.
- **STALE** (no `find_wiki_content_root`, ~32 `.py` — same pattern as pre-fix Mentor): **`eddyandwolff`**. Needs a `/sync` (`sync_from_kit.py`).
- **`Project-Mentor`**: stale on `main` at scan time, but **already fixed in the discovering room** (re-synced, byte-equal, pending merge to `main`). Do NOT re-fix — coordinate / let that PR land.
- **`aviation`**: a **separate case**, not a simple stale-sync. It runs a bespoke 15-file `build_wiki` toolchain (PDF→markdown), and has **never** been moved to the synced Codex Librarian engine. Needs its own assessment before any `/sync` (a sync may not be the right action).
- **`residehub`**: scaffold-only (`0 .py` under `_scripts/`) — not stale, just not bootstrapped yet.

**Resolution (per-consumer):** re-sync the vendored engine via `EMCC.Library/Biz.Automation/wikisys.library/_scripts/sync_from_kit.py` so it is byte-equal to Library canon, then re-run the consumer's dashboards to confirm output lands at `wiki.<name>/git/_dashboards/`. Library canon needs no change — the fix already lives here (MI-17).

**Advisory:** any Codex consumer bootstrapped before the MI-17 content-root fix should run a `/sync`. Mentor handled (out-of-room); `eddyandwolff` is the one clear remaining stale consumer on `main`; `aviation` is a distinct toolchain migration question.

**Follow-ups (proposed; gate before building):**
- **Version-staleness detection (the other room's request (b)):** `sync_from_kit.py` does not stamp a version into consumers, and Library has no `CHANGELOG`, so staleness is undetectable without a manual scan. Proposed: have `sync_from_kit.py` write a `codex_engine_version` stamp into each consumer + add a Library `CHANGELOG`/`module.json` line on the content-root fix. This is a **code change to `sync_from_kit.py`** (Level-2+) — gate (`/delta-force`) and coordinate with any active Library room before building.
- **`eddyandwolff` re-sync** — mechanical but a separate-repo build change; surface for operator go.
- **`aviation` toolchain assessment** — decide whether it adopts the Codex engine at all, or stays on bespoke `build_wiki`.

**Status:** OPEN (advisory recorded; Mentor handled out-of-room; `eddyandwolff` re-sync + `aviation` assessment + version-stamp mechanism are proposed follow-ups).
