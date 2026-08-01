# CERT VERDICT - W2-MOD-15 see-also truncation loud (PR #77)

- **Verdict:** CERT_FAIL (one blocking finding, B1; the loudness half of the atom is correct and
  well locked - the strict-policy half does not produce non-success in the canonical runner)
- **Loop:** LOOP-DEFINITION-wave-e-w2-rest-certifier (WAVE-E Phase J)
- **Seat checklist:** EMCC `tasks/checklists/wave-e-w2-rest-certifier.md`
- **Certifier:** claude:EMCC-ExternalCertifier (certifier_id: claude, certifier_model: claude)
- **Builder:** grok:EMCC-dfdu (builder_llm/builder_model: grok) - CF3 decorrelation holds
- **Auditor:** grok:EMCC-Auditor, AUDITOR_PASS
- **Handoff:** `0-Inbox/grok-audit/2026-08-01-w2-mod15-see-also-truncation.md`, attempt 1
- **Range examined:** 3782f5ea..76067cc (declared tip 44fc05f = the product commit; see C1)
- **Date:** 2026-08-01

## Summary

The silent-drop defect this atom exists to kill is genuinely killed. Truncation now warns on stderr
with a per-page dropped count and an event record, in every path I could drive, and both of those
are locked by tests that red when I remove them. Criterion 2 (uncapped still succeeds) and
criterion 3 (visible, not silent) pass.

I am failing on criterion 1's second conjunct - *"non-success when policy is strict"*. Under the
orchestrator that the Codex spec designates for this pipeline, `fail_on_truncation: true` drops
edges, prints its ERROR line, and the run still reports `#17 cross_link_topics -- OK` and
contributes nothing to the exit code. The strict knob is a policy control that, in the canonical
runner, does not enforce. For an atom whose whole subject is a control failing quietly, that is the
same defect one level up.

The behaviour work is right and does not need redoing. The fix is a few lines plus two tests.

## Pre-gate (CF2, CF4, CF8)

```
cd EMCC.Library && python <EMCC>/scripts/validate_cert_handoff.py 0-Inbox/grok-audit/2026-08-01-w2-mod15-see-also-truncation.md
PASS
exit 0
```

`status: pending` + `auditor_verdict: PASS` + `auditor_id` + `auditor_ref` present. W2-MOD-14 was
still `awaiting_auditor` on `origin/grok/w2-mod14-cross-manual-consume` when I selected, so I
refused it per CF8 and opened no MOD-14 product. One atom this tick (CF1).

**Zero involvement:** I did not build, audit or advise this atom. First contact with the product
diff was this cert.

## Product pins (identical at product 44fc05f and examined tip 76067cc)

| Path | sha256 |
|---|---|
| Biz.Automation/wikisys.library/_scripts/cross_link_topics.py | a32955116ff1d58c... |
| Biz.Automation/wikisys.library/_scripts/_lib/topics.py | 62d2a861c8a68bdb... |
| tests/test_cross_link_topics.py | d1da9f00d378ab46... |

Changed paths in range: the two product scripts, the test file, plus handoff / auditor / evidence /
sample docs and the orchestrator log. No unrelated surface. MOD-14 is correctly not bundled
(separate PR #76), which the inventory requires.

## Floors RUN by certifier (detached worktree at 76067cc; live tree never mutated)

| Floor | Command | Result | Exit |
|---|---|---|---|
| Declared | `python -m unittest tests.test_cross_link_topics -q` | **Ran 50, OK** | 0 |
| CI-equivalent | `python -m unittest discover -s tests -t .` | **Ran 960, OK (skipped=6)** | 0 |

Builder and Auditor claim of "50 OK" reproduces exactly.

## Criteria re-verified (driven as processes, not read off the evidence)

| # | Criterion | How | Result |
|---|---|---|---|
| 1a | Truncation cannot drop edges without error/warn | ran both entry points on a real fixture wiki with `max_links_per_page: 2` and 5 sibling pages | **PASS** - `WARNING: codex see-also truncation ... dropped=N` on stderr in every path, strict or not |
| 1b | non-success when policy is strict | direct CLI **and** orchestrator, both probed | **FAIL** - see B1. CLI exits 1; the orchestrator does not |
| 2 | Valid graph still succeeds | uncapped fixture | **PASS** - `links_truncated=0`, `truncation_failed=False`, exit 0, all 3 links written |
| 3 | Falsifier: truncate path -> visible fail, not silent | P2/P3 below | **PASS** |
| 4 | dual-PASS + human merge | blocked by B1 | - |

**Scope check.** Before accepting that the WARNING covers the whole plane, I looked for other places
an edge can be dropped. `compute_related_files` unions and sorts without capping; `rank_related`
reorders without truncating; `render_see_also_block` has no cap. `cross_link_topics.py` has exactly
one slice site (line 299-303) and that is the one the atom instrumented. The loudness fix is not
narrower than the surface it claims.

## PREM-1 and falsifiers (isolated worktree, proof-of-application, restored)

Every mutation asserted non-identity against the original before running, so a no-op could not print
like a passing probe.

| Probe | Mutation | Applied | Suite |
|---|---|---|---|
| **P1** | delete `if summary.get("truncation_failed"): sys.exit(1)` from `__main__` | YES | **Ran 50, OK, exit 0** |
| **P2** | delete the stderr WARNING `print` | YES | FAILED (failures=2): `test_process_page_truncation_warns_and_records`, `test_run_fail_on_truncation_sets_failed` |
| **P3** | `truncation_failed = False` unconditionally | YES | FAILED (failures=1): `test_run_fail_on_truncation_sets_failed` |

P2 and P3 are the good news: the loud path and the strict computation are both load-bearing, not
decorative. P1 is half of B1 - the only line in the codebase that turns strict policy into an actual
process failure can be deleted with all 50 tests green.

## BLOCKING finding

**B1 - strict `fail_on_truncation` is not a non-success in the canonical runner, and the one path
where it is non-success has no test.**

*The orchestrator half (present gap, not future rot).* `update_dashboards.py` is the spec-designated
orchestrator for this pipeline - it declares `CROSS_LINK_PIPELINE = [#16 build_topic_index,
#17 cross_link_topics, #18 validate_topic_registry]` with the comment *"per spec v1.3 §2.4
orchestrator note"*. Its loop calls `module.run(wiki_root)` inside a `try/except Exception`, so only
a **raised exception** lands in `summary["failures"]`; a returned `truncation_failed: True` is
ignored. `_main` then returns `1 if summary["failures"] else 0`.

Driven in-process on a fixture wiki with `max_links_per_page: 2` and `fail_on_truncation: true`:

```
strict=True   cross_link run() -> truncation_failed=True, links_truncated=18
              orchestrator failures containing #17: []
strict=False  cross_link run() -> truncation_failed=False, links_truncated=18
              orchestrator failures containing #17: []

failure p_nums, strict:     [13]
failure p_nums, non-strict: [13]
failure sets IDENTICAL across strict / non-strict: True
```

(The `13` is `check_concept_coverage` failing on my minimal fixture's missing `_canon/` - my harness,
not the product, which is exactly why I compared the **failure sets** rather than the exit codes.
The load-bearing observation is that `#17` never appears in either set, so on a wiki whose other
scripts pass, a strict truncation exits **0**.)

The orchestrator prints `#17 cross_link_topics -- OK` in the strict run.

*The test half (rot channel).* P1: deleting the `sys.exit(1)` from `__main__` - the one place strict
becomes a process failure - leaves all 50 tests green. `test_run_fail_on_truncation_sets_failed`
asserts the **returned dict**, never a process outcome. So even the working CLI path can be removed
by a later refactor with CI fully green.

*Consequence.* An operator who sets `fail_on_truncation: true` and runs the pipeline the documented
way gets stderr noise and a green run. The policy silently declines to enforce - the failure mode
this lane exists to kill, one level up from the silent link drop the atom correctly fixed.

*Note on scope.* The evidence file does scope its claim narrowly - *"`__main__` exit 1"* - and that
claim is true; I verified exit 1. I am not failing the atom for lying. I am failing it against the
inventory criterion, which says *"non-success when policy is strict"* with no path qualifier, and
against the reality that the qualified path is not the one a scheduled run uses.

*Surgical fix (no redesign; the behaviour work all stands):*
1. Make the orchestrator honour the flag - in `update_dashboards.CROSS_LINK_PIPELINE`, after
   `results[p_num] = module.run(wiki_root)`, append a failure entry when the returned dict reports a
   policy non-success (e.g. `truncation_failed`). Alternatively raise from `cross_link_topics.run`
   under strict, which the existing `except Exception` already records - but that breaks the current
   return contract and its test, so the orchestrator-side check is the smaller change.
2. Lock the process outcome, not just the dict: one test asserting `#17` lands in `failures` (or the
   `_main` exit code is non-zero) under strict on an otherwise-clean fixture, and one asserting the
   direct `cross_link_topics.py` CLI exits 1 - so P1's deletion reds.

Rework is **this atom only** (CF9). The warning text, the event records, the config default, the
uncapped back-compat path and all 50 existing tests stand as-is.

## Non-blocking carries

**C1 - declared range ends at the product commit.** The handoff declares `3782f5ea..44fc05f`, and
`44fc05f` **is** the product commit, so the declared range excludes the handoff-range commit and the
auditor artifact. I examined `3782f5ea..76067cc`; all three product blobs are byte-identical at both.
Ninth consecutive atom with this shape - standing suggestion unchanged: declare base + product
commit and let the certifier resolve the tip.

**C2 - examined tip is unpushed.** `origin/grok/w2-mod15-see-also-truncation-loud` is at `e4b5ef7`;
`76067cc` (the AUDITOR_PASS record) is local-only, so PR #77 does not currently show the file named
in `auditor_ref`. Recurring shape across this programme. Push before re-cert.

**C3 - the WARNING is stderr-only and unstructured for a caller.** `process_page` appends to
`truncation_events` only when the caller passes a list; the default is `None`. `run()` does pass one,
so the aggregate is available - this is not a hole, and I am recording it only because it means any
future direct caller of `process_page` gets the stderr line and nothing machine-readable. Relevant
if the B1 fix is built on the event list rather than the summary flag.

**C4 - `cert_class` correctly still `parked-awaiting-cross-model`** with an accurate caveat. No
action; recording that the handoff obeys the rule W2-MOD-6 introduced.

## Disposition - CERT_FAIL

- **CF1** Handoff NOT marked done-with-PASS. Left `status: pending` for Lattice rework; I did not
  edit the immutable body.
- **CF2** Enqueue **W2-MOD-15 only** -> Lattice rework. MOD-14 is a separate atom and separate PR.
- **CF3** Fail reason is surgical and named above with the probe output that produced it.
- Did not merge. Did not Director dual-PASS close.

## Explicit refuses

- Did not build product, act as Regime-B Auditor, merge, or dual-PASS close (CF5/CF6).
- Did not claim W2-MOD-14 while its handoff read `awaiting_auditor` (CF8), and did not certify two
  atoms in one tick (CF1).
- Did not report my first process probe: both entry points "exited 1" under strict, which looked
  like a pass, but the orchestrator's 1 came from `check_concept_coverage` failing on my fixture's
  missing `_canon/`. A positive from an unverified instrument is no better than a negative - I
  re-probed the failure **set** in-process, where strict vs non-strict is provably identical.
- Did not accept "fail_on_truncation -> ERROR + exit" from the evidence or the audit; ran both entry
  points against a real fixture wiki.
- Did not accept that the WARNING covers the plane; read `compute_related_files`, `rank_related` and
  `render_see_also_block` for other drop sites first and found the single slice.
- Did not fail the atom on the loudness work, which P2/P3 show is genuinely locked.
- Probe residue: mutations were applied only in a throwaway detached worktree and reverted after each
  run; that worktree was force-removed and pruned. The live EMCC.Library tree is clean at `76067cc`.
