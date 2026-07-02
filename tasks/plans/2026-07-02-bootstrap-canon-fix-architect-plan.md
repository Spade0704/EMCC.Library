# Architect Plan — Bootstrap canon fix (items 1 + 2)

- **Date:** 2026-07-02
- **Architect:** Librarian (EMCC.Library). **Coder:** Fable-5 Lattice peer (Director-routed). **NOT self-coded** (framework/22).
- **Branch/worktree:** `claude/bootstrap-canon-fix` off origin/main (7db7ea6), isolated worktree `EMCC.Library/.claude/worktrees/bootstrap-fix`.
- **Regime:** Lattice 3.0 Regime B (L2+, spec-touch). Gate: build → executes-clean (verified evidence_ref) → validate_cert_handoff.py → independent Auditor → Grok cross-check → DRAFT PR → Librarian co-sign → operator merge.
- **Scope:** exactly two items. Items 3/4/5 dropped (3+5 EMCC-side/per-repo; 4 per-repo content). See peer thread + reorg plan `EMCC/tasks/plans/2026-07-02-cross-repo-folder-structure-pattern-and-plan.md`.
- **Precondition (item 1 only):** operator ratifies the POLICY (section numbers = semantic slots, gaps by-design, 03-gap won't-fix). Item 2 may proceed regardless.

---

## Item 1 — Wiki section-numbering: semantic slots (Delta Force → Candidate B)

**Ruling source:** `tasks/delta-force/2026-07-02-wiki-section-numbering-scheme.md` (5/5 unanimous B). NO fixed 5-slot taxonomy, NO empty 01/02/03 stubs, NO per-project config. Section numbers are reserved SEMANTIC SLOTS: sparse-is-canonical, create-when-earned, never renumber (wikilinks `[[FileStem]]` + `related_files`/`canon_sources` are stem/path-bound).

**Why not stubs (do not regress to this):** empty 01/02/03 stubs would (a) fight `demote_boilerplate_stubs.py`, (b) count perpetually-RED in `check_concept_coverage.py` + completion dashboard, (c) collide with DFDU/Mentor hand-built 01/02 → dup pages/ambiguous wikilinks, (d) reintroduce the empty-scaffold smell the sibling assets/ opt-in ruling kills.

**Changes (docs + one existing-template line; bootstrap.py NOT touched for item 1):**

1. **Canonical page** `wiki.codex/git/00-Start-Here/How-to-Use-This-Wiki.md` — this is the SINGLE upstream home (boilerplate-location convention, operator-ratified 2026-06-11; consumer wikis carry a generated pointer-stub, never a fork). In the **"Folder layout"** section (currently lists `00-Start-Here/` + `04-Contributing/`), add a short **"Section numbering"** note, verbatim intent:
   > Section folders use reserved two-digit semantic slots (`00-Start-Here`, `01-Architecture`, `02-Operations`, `04-Contributing`, …). Numbering is **sparse by design** — a project creates a numbered section only when its content earns one, so gaps (e.g. no `03-`) are normal and expected, not a defect. Existing sections are **never renumbered**: wikilinks (`[[FileStem]]`) and `related_files`/`canon_sources` cite stems and paths, so a renumber would silently break the cross-link graph.
   Do NOT edit the per-repo pointer-stub `Biz.Automation/wikisys.library/_template/00-Start-Here__SEP__How-to-Use-This-Wiki.md` — it already says "read the canonical page for the folder layout … conventions." The note lives once, upstream.

2. **Spec** `tasks/plans/portfolio-folder-structure-spec.md` — in the wiki subsection of section (a), add one sentence + a pointer to the canonical page, so the cross-repo measuring stick records the policy: "Wiki section numbers are reserved semantic slots; sparse numbering (gaps) is canonical; sections are created when content exists and never renumbered. Canonical statement: `wiki.codex/git/00-Start-Here/How-to-Use-This-Wiki.md` §Section numbering."

3. **Audit disposition:** the "03-section gap" finding (EMCC reorg plan §2 #10 + path-consumer audit) closes **WON'T-FIX — intended behavior (semantic slots)**. The finding lives EMCC-side; Director records the disposition citing the Delta Force transcript. Librarian supplies the disposition text (this section).

**Tests (add):**
- Assert `wiki.codex/git/00-Start-Here/How-to-Use-This-Wiki.md` contains a "Section numbering" note mentioning "semantic slot" / "never renumber" (guards the self-explaining contract against silent removal). New test file or extend an existing wiki-content test.
- Regression guard: assert `bootstrap.py` output (`--full`) contains NO `01-*`/`02-*`/`03-*` section folders under `wiki.<name>/git/` (guards against a future stub-regression toward Candidate A). Add to `test_bootstrap_canonical.py`.

**bootstrap.py:** unchanged for item 1 (it already emits no numbered section folders — correct).

---

## Item 2 — assets/ opt-in (Q6 ruling; mechanical)

**Ruling:** empty `assets/` 6-gitkeep scaffold is a smell → OPT-IN, not scaffold-for-all. `--full`/`--code`/`--website` no longer emit `assets/` by default; a new independent `--assets` flag adds the six subfolders.

**Design — flag shape:** `--assets` is an **independent boolean flag**, NOT part of the mutually-exclusive mode group (`--full`/`--minimal`/`--code`/`--website`). Orthogonal: it appends the assets folders on top of whatever mode is selected. Default off. (Rationale: assets is an OPTIONAL root folder per spec L381; orthogonal flag = lowest code, no mode-group churn. `--minimal --assets` is legal and simply adds assets to the thin tree — cheaper than special-casing a reject.)

**Changes:**

1. `bootstrap.py`:
   - Remove the six `assets/*` entries from `CANONICAL_FOLDERS_FULL` (L72-77). Move them into a new module constant `ASSETS_FOLDERS = ("assets/logos", "assets/brand", "assets/photos", "assets/videos", "assets/designs", "assets/generated")`.
   - Add `--assets` to the parser (`_build_parser`) as `action="store_true"`, OUTSIDE the mode mutually-exclusive group. Thread `assets: bool` through `main()` → `bootstrap()` → `_materialize_folder_list(mode, projectname, assets)`.
   - In `_materialize_folder_list`, append `ASSETS_FOLDERS` (interpolated — they have no `{projectname}`, so interpolation is a no-op but keep the uniform `.format` pass) when `assets=True`.
   - Update the module docstring modes block (L22-34) + the CLI help + the `_post_bootstrap_checklist` note (L601 references assets heavy-file patterns — keep, but it's now conditional; reword to "if you passed --assets …").
   - `.gitignore` stub already ships commented assets heavy-file patterns (L363-368) — LEAVE (harmless when assets absent; useful when present).

2. **Spec** `tasks/plans/portfolio-folder-structure-spec.md` section (c):
   - Invocation line (L903): add `[--assets]`.
   - `--full` output block (L916-949): remove the `assets/…` subtree from the default `--full` tree; add an `--assets adds:` block documenting the six subfolders. Mirror the existing `--code adds` / `--website adds` doc style.
   - Section (a) variance table row for `assets/` already says OPTIONAL "Add to project when first brand/photo lands" (L381) — consistent, no change needed, but cross-reference the `--assets` flag.

**Tests (rework in `test_bootstrap_canonical.py`):**
- `test_full_emits_all_canonical_top_level_entries` (L55): remove `"assets"` from `expected_top`.
- `test_full_emits_assets_six_subfolders` (L101): rename/rework → assert `--full` alone emits NO `assets/`, AND a new `--assets` run emits the six `assets/*/.gitkeep`.
- `test_code_emits_same_canonical_tree_as_full` (L280): drop the `assets/logos` assertion (assets no longer default under --code).
- `test_minimal_omits_biz_automation_and_assets` (L235): still passes (minimal without --assets = no assets); optionally add a `--minimal --assets` composability assertion.
- Add `test_assets_flag_composes_with_full` + `test_no_assets_flag_omits_assets`.
- Update the module docstring tree (L14) to drop assets from the default depiction.
- `test_audit_assets.py` / `audit_assets.py`: verify the audit script's expectations still hold (it flags empty assets as a smell — now consistent with opt-in). Coder confirms no assertion breaks; if `audit_assets.py` assumed assets/ always present, align it.
- `test_t1_p52_bootstrap_operation.py`: DEPRECATED/MI-16 (module SkipTest) — confirm still skipped, no action.

---

## Cross-cutting acceptance criteria (both items, lockstep)

1. `python -m unittest discover -s tests -t .` — full suite GREEN (644 tests / 6 skipped baseline; net count may shift by the added/reworked tests — report the new baseline).
2. Tripwires green: `test_persona_dropin.py` (drift-guard) untouched-and-passing; bootstrap-e2e passing.
3. `python bootstrap.py <tmp> --full` → canonical tree with NO `assets/`, NO numbered section folders. `python bootstrap.py <tmp> --full --assets` → adds the six assets folders. `--minimal`/`--code`/`--website` behave per spec.
4. Spec (c) + bootstrap.py + templates/canonical-page + tests changed IN ONE PR (lockstep — no spec/code drift).
5. Verbatim discipline intact: INGEST_PROCEDURE.md + SEMANTIC_LINT_PROCEDURE.md byte-unchanged.
6. Stdlib-only; `pathlib`; Windows-safe. No new dependencies.
7. Item 1 canonical-page edit is to the UPSTREAM page only; the per-repo pointer-stub is NOT forked.
8. cert-handoff/v1.1 fields populated (builder_id/director_id/directive_ref); evidence_ref points at the executes-clean test run.

## Out of scope (do not touch)
- No renumbering of any existing section (04→03 FORBIDDEN).
- No `assets/` changes to existing repos (that's the reorg's per-repo lane, not this scaffold PR).
- Items 3 (ui/), 4 (README/Cheatsheet rot), 5 (emcc.modules.json detection) — not this build.
- Dogfood wiki's hand-built `01-Architecture/`, `02-Operations/` — leave as-is.

## First test to write (Delta Force chairman's pick)
`test_bootstrap_canonical.py::test_full_omits_numbered_section_stubs` — asserts `--full` emits no `01/02/03-*` dirs under `wiki.<name>/git/`. Encodes the anti-regression contract before any other change lands.
