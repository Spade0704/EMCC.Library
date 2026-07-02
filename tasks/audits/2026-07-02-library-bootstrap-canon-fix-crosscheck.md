---
verdict: PASS
risk_class: low
---

# Cross-check — EMCC.Library PR #62 (bootstrap canon fix)

Decorrelated leg-2 manual peer cross-check (Grok cross-model plane unavailable). Read cold from git; produced none of this build.

- **Target:** PR #62, branch `claude/bootstrap-canon-fix`, commits `cbebc9e` + `973abb0` on `origin/main 7db7ea6`.
- **Diff read via:** `git diff origin/main...origin/claude/bootstrap-canon-fix` (4 files: `bootstrap.py`, `tasks/plans/portfolio-folder-structure-spec.md`, `tests/test_bootstrap_canonical.py`, `wiki.codex/git/00-Start-Here/How-to-Use-This-Wiki.md`).
- **Contract:** `tasks/plans/2026-07-02-bootstrap-canon-fix-architect-plan.md`; Delta-Force `tasks/delta-force/2026-07-02-wiki-section-numbering-scheme.md` (unanimous B — semantic slots, no empty stubs).

## 1. Suite (COLD, from branch worktree)

Ran from `.claude/worktrees/bootstrap-fix` (tip `973abb0`):
`python -m unittest discover -s tests -t .` → **`Ran 873 tests in 16.843s` / `OK (skipped=6)`**. GREEN. (The three `ERROR:` lines are asserted-stderr from projectname-validation negative tests, not failures.) Matches expected ~873.

## 2. Diff vs instruction — A + B and ONLY A + B

- **Item A (semantic-slots policy, docs-only):** Wiki `How-to-Use-This-Wiki.md` gains a "Section numbering" note; spec (a) gains one sentence + canonical-page pointer. `bootstrap.py` section-logic UNTOUCHED (it already emitted no numbered section folders — confirmed by grep + the anti-regression test). Docs-only. ✅
- **Item B (assets opt-in):** `--assets` added as `parser.add_argument` at bootstrap.py:755 — OUTSIDE the `mode_group = add_mutually_exclusive_group()` (bootstrap.py:722; `--full/--minimal/--code/--website` are on `mode_group`). `action="store_true"`, default off. Six `assets/*` extracted to `ASSETS_FOLDERS` (bootstrap.py:85-92) and removed from `CANONICAL_FOLDERS_FULL`. Appended once (bootstrap.py:425, `if assets:`) — no double-add. Spec (c) invocation + `--full` tree + new `--assets adds` block amended. ✅
- No scope creep. Items 3/4/5 correctly untouched.

## 3. Docs real, not stubs

Wiki note is substantive: reserved two-digit semantic slots, **sparse by design**, gaps normal/expected, **never renumbered** (with the cross-link-graph rationale). Spec cross-references the canonical page. Matches the Delta-Force policy verbatim intent. ✅

## 4. No empty-stub regression

`test_full_omits_numbered_section_stubs` (Delta-Force chairman's first-test pick) pins that `--full` emits NO `0[123]-*` dirs under `wiki.<name>/git/`. Present + green. ✅

## 5. Index.md fix

assets row (bootstrap.py:200-201) uses the unconditional "(if present; scaffold via --assets)" annotation string — same idiom as sibling optional rows, NOT a conditional-emit bool thread. `test_full_index_md_assets_row_uses_if_present_idiom` guards it. ✅

## 6. Tests discover-compatible

All new tests are methods on `unittest.TestCase` subclasses (`TestCanonicalFullTree`, `TestCanonicalMinimalTree`, `TestCanonicalCodeMode`, `TestCLIParser`, new `TestSectionNumberingCanonicalNote`). No module-level `def test_` pytest-funcs. The 873 discover count includes them. ✅

## 7. Red flags

None. `INGEST_PROCEDURE.md` / `SEMANTIC_LINT_PROCEDURE.md` NOT in the diff (byte-identical). No mode double-adds assets (`test_assets_flag_independent_of_mode_group` + `test_minimal_composes_with_assets_flag` prove composition). No broken interpolation (ASSETS_FOLDERS carry no `{projectname}`; uniform `.format` pass is a documented no-op). `--code` assets default correctly flipped off with test updated.

## Verdict

**PASS.** Diff implements exactly A + B, docs are substantive (not stubs), the anti-regression + idiom + orthogonal-flag contracts are test-pinned, and the full suite is GREEN cold at 873/OK.
