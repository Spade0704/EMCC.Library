# CERT VERDICT (re-cert after rework) - W2-MOD-15 see-also truncation loud (PR #77)

- **Verdict:** CERT_PASS (blocking=0; B1 from the prior CERT_FAIL is closed, both halves)
- **Supersedes:** `2026-08-01-w2-mod15-see-also-truncation-lattice-certifier.md` (CERT_FAIL, B1)
- **Loop:** LOOP-DEFINITION-wave-e-w2-rest-certifier, post-rework pass
- **Certifier:** claude:EMCC-ExternalCertifier (certifier_id: claude, certifier_model: claude)
- **Builder:** grok:EMCC-dfdu (builder_llm: grok) - CF3 decorrelation holds
- **Auditor:** grok:EMCC-Auditor, AUDITOR_PASS r2 (`...-auditor-r2.md`)
- **Handoff:** `0-Inbox/grok-audit/2026-08-01-w2-mod15-see-also-truncation.md`, **attempt 2**
- **Certified range:** 3110913..d6cb325 (MOD-15's own product `00b8d18`; **tip pushed** - `origin/grok/w2-mod15-see-also-truncation-loud` = `d6cb325`)
- **Date:** 2026-08-01

## Stacking - checked before anything else

The attempt-2 branch merged MOD-14's tip (`3110913 merge: stack W2-MOD-15 onto MOD-14 tip`), so the
range `3782f5ea..d6cb325` contains both atoms' product. The inventory forbids bundling 14+15 in one
PR, so I checked the PR topology rather than assuming either way:

```
PR #76  head grok/w2-mod14-cross-manual-consume   base main
PR #77  head grok/w2-mod15-see-also-truncation-loud   base grok/w2-mod14-cross-manual-consume
```

#77 bases on the MOD-14 branch, not on main. That is a **stacked pair, not a bundle** - each PR
delivers exactly one atom's diff against its own base. Criterion 4 holds. Merge order is #76 then
#77; merging #77 first would carry MOD-14 into main under MOD-15's number.

Stack integrity verified rather than assumed: `d4d9c5e` (the MOD-14 rework product) **is** an
ancestor of `d6cb325`, and the MOD-14 controls I certified an hour ago are present verbatim on this
branch - `cross_manual: Optional[bool] = None` (topics.py:60) and `if t.cross_manual is None:`
(cross_link_topics.py:419). The only delta in those two files versus the MOD-14 tip is MOD-15's own
`fail_on_truncation` config key. So this branch does not silently regress the atom it stacks on.

## B1 retest - both halves, by the probes that produced the FAIL

**Half 1 - the orchestrator.** The FAIL rested on `update_dashboards.run()` treating only raised
exceptions as a `#17` failure, so `fail_on_truncation: true` left the canonical orchestrator
reporting `#17 cross_link_topics -- OK`. Re-ran the same in-process probe:

| | Attempt 1 | Attempt 2 |
|---|---|---|
| strict: `#17` in `summary["failures"]` | **no** | **yes** - `truncation_failed: see-also cap dropped 18 link(s) under fail_on_truncation=true` |
| non-strict: `#17` in failures | no | no |
| failure sets identical strict vs non-strict | **True** (the defect) | **False** |

End-to-end through `_main` on a fixture with `_canon/` and `Home.md`:

```
strict=True    #17 cross_link_topics -- FAILED: truncation_failed: see-also cap dropped 18 link(s)...
               orchestrator: 2 sub-script(s) failed; exit 1
strict=False   #17 cross_link_topics -- OK
               orchestrator: 1 sub-script(s) failed; exit 1
```

Stated precisely: my minimal fixture still has one unrelated sub-script failing, so both totals are
>= 1 and the exit code alone proves nothing - which is why I compare the `#17` line and the failure
count (2 vs 1). Those are what `1 if summary["failures"] else 0` reads, so on an otherwise-clean wiki
the strict run now exits non-zero on `#17` alone. Same discipline as attempt 1, where I refused to
read the exit code because my fixture polluted it.

The summary printer was also fixed to consult `failures` before `results`, so a policy non-success
that still returns a result dict prints `FAILED` rather than a false `OK`. That was the visible
symptom and it is gone.

**Half 2 - the untested CLI exit.** At attempt 1, deleting `sys.exit(1)` from
`cross_link_topics.__main__` left all 50 tests green. Re-ran that exact probe (S3): it now reds
`test_cli_process_exits_1_on_fail_on_truncation`. The one line that turns strict policy into a
process failure is locked.

## Floors RUN by certifier (detached worktree at d6cb325; live tree never mutated)

| Floor | Command | Result | Exit |
|---|---|---|---|
| Declared | `python -m unittest tests.test_cross_link_topics -q` | **Ran 59, OK** (was 50) | 0 |
| New | `python -m unittest tests.test_update_dashboards -q` | **Ran 13, OK** | 0 |
| CI-equivalent | `python -m unittest discover -s tests -t .` | **Ran 970, OK (skipped=6)** (was 960) | 0 |

## Falsifiers - every reworked control is load-bearing

| Probe | Mutation | Applied | Suite |
|---|---|---|---|
| **S1** | orchestrator ignores `truncation_failed` - **reinstates B1 half 1** | YES | FAILED (1): **`test_truncation_failed_is_orchestrator_non_success`** |
| **S2** | summary printer back to results-first (prints `OK`) | YES | FAILED (2): `test_truncation_failed_is_orchestrator_non_success`, `test_sub_script_failure_does_not_abort` |
| **S3** | delete `sys.exit(1)` from `__main__` - **the attempt-1 probe that stayed green** | YES | FAILED (1): **`test_cli_process_exits_1_on_fail_on_truncation`** |
| **S4** | `truncation_failed = False` unconditionally | YES | FAILED (2) incl. `test_run_fail_on_truncation_sets_failed` |

S1 and S3 are the two halves of B1, and each now has a test named for it that reds when the control
is removed. S2 is a bonus: the false-`OK` display is independently locked, and breaking the printer
also breaks the pre-existing failure-isolation test, so the fix did not weaken that contract.

Probes reverted, worktree force-removed and pruned, live EMCC.Library tree clean at `d6cb325`.

## Pins (at certified tip d6cb325)

| Path | sha256 |
|---|---|
| Biz.Automation/wikisys.library/_scripts/update_dashboards.py | 20816449adfad9ed... |
| Biz.Automation/wikisys.library/_scripts/cross_link_topics.py | fa08a60e3891884e... |
| tests/test_update_dashboards.py | 65e81556888539aa... |
| tests/test_cross_link_topics.py | 51678e41f60ddce7... |

`update_dashboards.py` and its test are byte-identical at `00b8d18` and `d6cb325`, so the r2 audit
commit added no product.

## Everything from attempt 1 that already passed, re-verified

| Check | Result |
|---|---|
| Loud WARNING on every truncation, strict or not | unchanged, still locked (S4) |
| Uncapped default still green, zero truncation | unchanged |
| Single truncation site - no second silent drop path in this file | re-read; still one slice |
| Declared floor reproduces the builder claim | 59 OK (grew from 50 with the rework) |

## Carries (non-blocking)

**C1 - declared range ends at the product commit.** The handoff declares `3782f5ea..00b8d18`, and
`00b8d18` **is** the product commit, so the r2 audit record falls outside it; the declared base also
predates the stack merge, which makes the field describe two atoms rather than this one. I certified
`3110913..d6cb325`. Twelfth consecutive atom with a stale range field. With stacked PRs now in play
the standing suggestion gets sharper: declare **base = the PR's actual base ref** plus the product
commit, and let the certifier resolve the tip.

**C2 - merge order is load-bearing and lives only in the PR base.** Nothing in the handoff records
that #77 must land after #76. If #77 were merged first it would carry MOD-14's product into main
under MOD-15's number - which is the bundling the inventory forbids, arrived at by merge order rather
than by diff. Worth one line in the close artifact.

**C3 - `cross_manual` drops still bypass the truncation accounting.** MOD-14's gate drops edges in
`compute_related_files` and reports them via its own `cross_manual_drops` counter and WARNING;
MOD-15's `links_truncated` / `truncation_failed` cover only the `max_links` slice. Both are loud now,
so nothing is silent - but an operator reading `truncated=N` is not seeing every edge the run
removed. Two counters, two warnings, one graph. A future consolidation is a docs or small-refactor
item, not a defect in either atom.

**C4 - `cert_class` correctly still `parked-awaiting-cross-model`.** Moves to
`cross-model-certified` with `status: done` + this verdict on the Director's close.

## Disposition

- **CP1** CERT_PASS, blocking=0; C1-C4 non-blocking.
- **CP2** Did not merge. Did not Director dual-PASS close. Signalling Director.
- **CP3** Handoff cert fields left to seat protocol / Director pack.

## Explicit refuses

- Did not build product, act as Regime-B Auditor, merge, or dual-PASS close.
- Did not certify while the rework sat at `awaiting_auditor`.
- Did not treat the stack merge as bundling on sight, nor wave it through - read both PRs' base refs
  and confirmed `d4d9c5e` is an ancestor with MOD-14's controls intact on this branch.
- Did not certify this atom and MOD-14 as one unit; each got its own pre-gate, floors, probes and
  verdict, in inventory order.
- Did not read the exit code as proof - my fixture retains one unrelated sub-script failure, so I
  compared the `#17` line and the failure count, the two inputs the exit predicate actually reads.
- Did not accept the rework on the r2 audit; re-ran S1 and S3, the two probes that produced the FAIL,
  and required both to flip from green to red.
