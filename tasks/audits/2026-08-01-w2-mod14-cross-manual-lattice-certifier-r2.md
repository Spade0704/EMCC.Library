# CERT VERDICT (re-cert after rework) - W2-MOD-14 cross_manual consume (PR #76)

- **Verdict:** CERT_PASS (blocking=0; B1 from the prior CERT_FAIL is closed)
- **Supersedes:** `2026-08-01-w2-mod14-cross-manual-lattice-certifier.md` (CERT_FAIL, B1)
- **Loop:** LOOP-DEFINITION-wave-e-w2-rest-certifier, post-rework pass
- **Certifier:** claude:EMCC-ExternalCertifier (certifier_id: claude, certifier_model: claude)
- **Builder:** grok:EMCC-dfdu (builder_llm: grok) - CF3 decorrelation holds
- **Auditor:** grok:EMCC-Auditor, AUDITOR_PASS r2 (`...-auditor-r2.md`)
- **Handoff:** `0-Inbox/grok-audit/2026-08-01-w2-mod14-cross-manual.md`, **attempt 2**
- **Certified range:** 3782f5ea..d1ab6a5 (product `d4d9c5e`; **tip pushed** - `origin/grok/w2-mod14-cross-manual-consume` = `d1ab6a5`)
- **Governing ruling:** `tasks/decisions/2026-08-01-w2-mod14-cross-manual-default.md` - unset means ALLOW
- **Date:** 2026-08-01

## What changed since the CERT_FAIL

```
d4d9c5e fix(codex): W2-MOD-14 rework unset-means-allow + loud cross_manual drops
13e205b docs(cert): W2-MOD-14 attempt-2 handoff range (awaiting_auditor)
d1ab6a5 docs(audit): W2-MOD-14 Regime-B AUDITOR_PASS r2 (CERT B1 rework)
```

Three product surfaces: `_lib/topics.py` (`cross_manual: Optional[bool] = None`; unset key no longer
coerced to `False`), `cross_link_topics.py` (unset topics are not written into the map; drops are
recorded and warned), and the `_canon` template comment. Plus tests in two files.

The handoff correctly sat at `awaiting_auditor` for both ticks between the rework and the r2 audit;
I refused it each time without opening product.

## B1 retest - the exact measurement that produced the FAIL

The CERT_FAIL rested on one number: running the shipped entry point with no arguments against this
module's own `wiki.codex/git` deleted 300 of 630 `related_files` edges. I re-ran that measurement
unchanged in form - `origin/main` in one detached worktree, `d1ab6a5` in another, `python
cross_link_topics.py` in each:

| | Attempt 1 | Attempt 2 |
|---|---|---|
| edges pre / post | 630 -> 330 | **630 -> 630** |
| edges removed | **300 (48%)** | **0** |
| pages with a changed edge set | 23 of 27 | **0 of 27** |
| run counters vs origin/main | `updated=22 idempotent=1` | `updated=23 idempotent=0` - **identical to origin/main** |
| stderr | silent | silent (nothing to warn about) |

Zero drift against pre-atom behaviour on the real wiki. That is the finding closed, measured the
same way it was opened.

## Policy matrix driven as a process (Director ruling)

Fixture wiki, three pages across two containers, one registry per case:

| Registry | cross-container edge kept | `cross_manual_drops` | stderr |
|---|---|---|---|
| `cross_manual: false` (explicit) | **no** - denied | 4 | `WARNING: codex cross_manual drop: edges=4 pages=3 topics=smoke (explicit cross_manual:false only; unset allows)` |
| `cross_manual: true` (explicit) | yes | 0 | none |
| key **omitted** (the B1 case) | **yes** | 0 | none |

All three rows match the ruling exactly: unset allows, explicit `true` allows, explicit `false`
denies **and is loud**. The warning names edges, pages and topics, so a future restriction is
attributable rather than a silent diff.

## Floors RUN by certifier (detached worktree at d1ab6a5; live tree never mutated)

| Floor | Command | Result | Exit |
|---|---|---|---|
| Declared | `python -m unittest tests.test_cross_link_topics -q` | **Ran 55, OK** (was 52) | 0 |
| Declared | `python -m unittest tests._lib.test_topics -q` | **Ran 31, OK** | 0 |
| CI-equivalent | `python -m unittest discover -s tests -t .` | **Ran 965, OK (skipped=6)** (was 962) | 0 |

## Falsifiers - every reworked control is load-bearing

Each mutation asserted non-identity before running; a no-op would have been reported as a failed
probe, not a pass.

| Probe | Mutation | Applied | Suite |
|---|---|---|---|
| **R1** | delete `if t.cross_manual is None: continue` so unset is written into the map as `False` - **this is exactly the B1 regression** | YES | FAILED (1): **`test_registry_present_field_unset_allows_cross`** |
| **R2** | dataclass default back to `False` | YES | FAILED (1): `test_topic_defaults` |
| **R3** | loader maps unset -> `False` instead of `None` | YES | FAILED (1): `test_topic_defaults` |
| **R4** | remove the loud WARNING block | YES | FAILED (1): **`test_cross_manual_false_drop_is_loud`** |
| **R5** | disable the gate entirely | YES | FAILED (5) incl. `test_compute_records_drop_events_on_explicit_false` |

R1 is the one that matters. At attempt 1 the equivalent probe left the whole suite green - that
absence of a lock was half of B1. The rework's new test is named for exactly that branch and reds
when the branch is broken. R4 does the same job for the loudness requirement. Both of the tests the
Director's rework list called for exist and are load-bearing, not decorative.

Probes reverted, both worktrees force-removed and pruned, live EMCC.Library tree clean.

## Ruling compliance (`2026-08-01-w2-mod14-cross-manual-default.md`)

| # | Requirement | Status |
|---|---|---|
| 1 | Default allow when unset; only explicit `false` denies | **done** - matrix above, R1/R2/R3 lock it |
| 2 | Loud drop, never silent mass delete | **done** - WARNING with edges/pages/topics + `cross_manual_drops` in the summary; R4 locks it |
| 3 | Test: registry present, field unset -> edge kept | **done** - `test_registry_present_field_unset_allows_cross` |
| 4 | Test: explicit `false` -> excluded + loud signal | **done** - `test_cross_manual_false_same_container_only` + `test_cross_manual_false_drop_is_loud` |
| 5 | Do not bundle MOD-15 | **done** - `grep -c "fail_on_truncation\|truncation_events"` on this branch returns **0** |
| 6 | dual-PASS re-cert after rework | this verdict |

The spec-amend the ruling asked for also landed: the `topics.py` docstring and the `_canon`
template comment now read *"omitted = allow"* instead of *"default false"*. The stale documentation
was part of how the original default looked intentional, so correcting it matters more than a
comment usually would.

## Everything from attempt 1 that already passed, re-verified

| Check | Result |
|---|---|
| PREM-1: `cross_manual` was inert pre-atom | still true - established at attempt 1 against `origin/main` |
| Explicit `false` actually gates cross-container edges | verified (matrix row 1) |
| Registry-load failure fails open with a warning | unchanged code path |
| MOD-15 not bundled | verified by grep |
| Full Library suite | 965 OK, exit 0 |

## Carries (non-blocking)

**C1 - declared range still ends at the product commit.** The handoff declares
`3782f5ea..d4d9c5e`, and `d4d9c5e` **is** the product commit, so the r2 audit record is outside it.
I certified through `d1ab6a5`. All four pinned blobs identical at both. Eleventh consecutive atom;
the standing suggestion is unchanged - declare base + product commit and let the certifier resolve
the tip.

**C2 - the attempt-2 handoff carries non-ASCII bytes.** My front-matter poller crashed on it this
session with `UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d`, and I had to re-run with
an explicit decode to see the queue at all. Coordination files are meant to be ASCII-only; the same
shape was carried on W2-MOD-4s2 (C3). Nothing rides on it for this cert - the pre-gate passes - but
a handoff that crashes a reader is a discovery-plane risk, not a cosmetic one.

**C3 - `cert_class` correctly still `parked-awaiting-cross-model`.** Moves to
`cross-model-certified` with `status: done` + this verdict on the Director's close - the shape
W2-MOD-6 requires.

**C4 - drop attribution is aggregate, not per-page.** The WARNING reports totals plus the topic
list; the per-edge records live in `drop_events`, which `run()` does not return. Fine as shipped -
the operator gets a loud, attributable signal - but if a future consumer needs to report *which*
page lost *which* edge, the data exists and is simply not surfaced.

## Disposition

- **CP1** CERT_PASS, blocking=0; C1-C4 non-blocking.
- **CP2** Did not merge. Did not Director dual-PASS close. Signalling Director.
- **CP3** Handoff cert fields left to seat protocol / Director pack.

## Explicit refuses

- Did not build product, act as Regime-B Auditor, merge, or dual-PASS close.
- Did not certify while the rework sat at `awaiting_auditor` on the two intervening ticks.
- Did not accept the rework on its commit message or on the r2 audit; re-ran the **same** wiki.codex
  measurement that produced the FAIL and required it to go from 300 removed to 0.
- Did not accept "the missing test was added" from the diff; broke the exact branch (R1) and
  required the new test to red.
- Did not check only the case that failed - drove all three policy rows (false / true / unset),
  since a rework that fixes `unset` by disabling the gate would also show 0 edges removed.
- Did not bundle this with W2-MOD-15, which is certified separately on its own attempt 2.
