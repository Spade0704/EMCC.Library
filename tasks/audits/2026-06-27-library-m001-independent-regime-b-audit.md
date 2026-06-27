# Independent Regime-B Auditor verdict — EMCC.Library M001 tier-aware coverage

- **Target:** branch `m001-tier-aware-coverage`, commits `9e5b65d` (code) + `704e6e7` (evidence)
- **Repo:** `D:\Projects\Enterprise Matrix\EMCC.Library`
- **Auditor:** independent Regime-B (framework/22). No build context; verified by reading the actual code + re-running both suites.
- **Date:** 2026-06-27

## AUDITOR VERDICT: PASS

All 5 invariants independently hold against the real code path; both suites reproduce the builder's reported counts; no scope creep; fixtures untouched.

## Critical-path trace (invariant #1 — never-silent-drop)

The fail-open does NOT rely on a `.get(key, default)` default-arg. The guard is structural:

```
raw_tier = entry.get("tier")
entry_tier = raw_tier.strip() if isinstance(raw_tier, str) and raw_tier.strip() else DEFAULT_TIER
```
(`check_concept_coverage.py` run(), lines ~178-184)

I traced what the roster parser (`_lib/frontmatter.parse_config_yaml`, the list-of-mappings path) actually produces for each degenerate `tier:` form, because the whole invariant rests on the parser, not the guard's good intentions:

| roster form | parser output | `isinstance(str) and strip()` | result |
|---|---|---|---|
| key absent | `entry.get("tier")` -> `None` | False | DEFAULT_TIER -> **included** |
| `tier:` (empty) | continuation field empty-value branch sets `current_item[key] = []` (frontmatter.py ~698) | `isinstance([],str)` False | DEFAULT_TIER -> **included** |
| `tier: null` | `_parse_value("null")` -> `None` (frontmatter.py `_parse_value`, `s=="null"`) | False | DEFAULT_TIER -> **included** |
| `tier: ~` | `_parse_value("~")` -> `None` | False | DEFAULT_TIER -> **included** |
| `tier: "   "` | `_parse_value` strips quotes -> `"   "` | str True, `.strip()` falsy | DEFAULT_TIER -> **included** |

Every non-string / empty / null / whitespace form funnels to `DEFAULT_TIER = "Authoritative"`, which is in `KNOWN_TIERS` so it also emits no spurious WARN. The builder's claim ("empty list-item `tier:` renders `[]`") is verified true at `frontmatter.py` line ~698, and the `tier: null/~` -> `None` claim is verified at `_parse_value`. No silent-drop path exists.

## Per-invariant table

| # | Invariant | Verdict | Evidence (file:line @ branch state) |
|---|---|---|---|
| 1 | NEVER-SILENT-DROP (missing/empty/null/whitespace tier -> included) | **HOLDS** | `check_concept_coverage.py` run() ~178-184 (`isinstance(raw_tier,str) and raw_tier.strip()` guard, NOT a `.get` default); parser `frontmatter.py` ~698 (empty->`[]`) + `_parse_value` (`null`/`~`->`None`). Regression-guarded by test T8. |
| 2 | DEFAULT-OFF byte-identical | **HOLDS** | DEFAULTS `"tier_filter": None` (~102); whole skip block gated `if tier_filter is not None:` (~172) -> inert when off; `_load_concept_coverage_config` only sets it for a non-empty str (~300-306), else stays None. Test T3 asserts byte-identical dashboard. |
| 3 | UNION with exclude_entities (independent predicates) | **HOLDS** | `if canonical in exclude_entities: continue` (~167) runs first and independently; tier block is a separate later `if ... continue` (~172-194); neither bypasses the other. Test T5 asserts all three of ref-skip / exclude-skip / plain-fires. |
| 4 | CASEFOLD compare | **HOLDS** | `entry_tier.casefold() != tier_filter.casefold()` (~193) — both sides casefolded. Test T9 (lowercase `authoritative` matches). |
| 5 | WARN secondary signal on present-but-unknown filtered tier | **HOLDS** | `if entry_tier.casefold() not in KNOWN_TIERS: print(..., file=stderr)` (~185-191) emitted before skip; `KNOWN_TIERS={"authoritative","references"}`. Tests T7 (unknown->WARN), T7b (known->no WARN). `run(stderr=...)` injectable; `_main` wires it (~397). |

## Tests observed (re-run by auditor, not taken on faith)

- **Module suite** `python -m unittest tests.test_check_concept_coverage` -> **Ran 43 tests, OK** (matches builder's 43/43).
- **Full Library suite** `python -m unittest discover -t . -s tests -p 'test_*.py'` -> **Ran 867 tests, OK (skipped=6)** (matches builder's 867/867, 6 skipped).
- **Import-shadow artifact confirmed:** without `-t .` -> **Ran 164, FAILED (errors=35, skipped=5)**. The 35 errors are the `tests/_lib` vs source `_lib` top-level-dir shadow (harness artifact), NOT diff-caused. The builder's note to use `discover -t .` is accurate and necessary.

## Scope / fixtures

- **6 files** changed across both commits = the 5 declared (`check_concept_coverage.py`, `_config/concept_coverage.yaml`, `_canon/roster.yaml` header-comment-only, `tests/test_check_concept_coverage.py`, `PROJECT_WIKI_BUILD_SPEC.md §2.5`) + 1 expected evidence file (`tasks/audits/...executes-clean.txt`, commit `704e6e7`). No scope creep.
- **`roster.yaml`** change is header comment only (added tier doc block, lines 8-13) — no entity data altered.
- **Fixtures untouched** (no fixture/`_fixtures` path in the diff).

## Non-blocking findings

1. **Over-warn edge (cosmetic):** if an operator sets `tier_filter` itself to an unknown value (e.g. `tier_filter: "Bogus"`) and an entry carries the same `tier: Bogus`, the entry is correctly INCLUDED (casefold match) yet still emits the unknown-tier WARN. Advisory-only, arguably correct (surfaces off-vocabulary usage); not a drop. No action required.
2. **WARN fires per-entry** for unknown tiers — a roster with many unknown-tier entries under an active filter will repeat the WARN per entry. Acceptable for an advisory validator; could be de-duped later if noisy.

## AUDITOR VERDICT: PASS
