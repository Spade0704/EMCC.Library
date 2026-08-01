# CERT VERDICT - A4-MOD-13 topic registry absent-input fail-closed (Library PR #74)

- **Verdict:** CERT_PASS (blocking=0; carries C1-C4 non-blocking)
- **Loop:** LOOP-DEFINITION-assurance-mod-certifier-wave, iteration 1
- **Certifier:** claude:EMCC-ExternalCertifier (certifier_id: claude, certifier_model: claude)
- **Builder:** grok:EMCC-dfdu (builder_llm/builder_model: grok) - CF3 vendor decorrelation holds
- **Auditor:** grok:EMCC-Auditor, AUDITOR_PASS
- **Handoff:** EMCC.Library/0-Inbox/grok-audit/2026-08-01-a4-mod13-topic-registry-absent-input.md, attempt 1
- **Certified range:** 2da101df..df07e98e (see C2 - declared tip was f677ae2f)
- **Product commit:** f677ae2f - verified ancestor of certified tip
- **Date:** 2026-08-01

## C0 - selection

Only one claimable handoff in the queue at claim time: `status: pending`, `auditor_verdict: PASS`,
`auditor_id` + `auditor_ref` present, builder vendor grok != claude, `directive_ref` resolves.
One atom this iteration (CF1).

## C1 - pre-gate (CF4)

```
python scripts/validate_cert_handoff.py <handoff>
PASS
exit 0
```

## C2 - zero involvement (CF5)

I did not build, audit, or advise this atom. First contact with the product diff was this cert.
No product authorship by me in this range.

## C3 - range + product pins

Local HEAD `df07e98e`; declared tip `f677ae2f` is the product commit itself. Product verified
ancestor of the certified tip. Changed paths in `2da101df..df07e98e`: two product files plus
coordination docs and `tasks/orchestrator-log.jsonl`.

| Path | sha256 (identical at f677ae2f and df07e98e) |
|------|---------------------------------------------|
| Biz.Automation/wikisys.library/_scripts/validate_topic_registry.py | 035d30872357b8dd7cd74691588794c244a62e23d5d033b7d75f2da0d44d0d25 |
| tests/test_validate_topic_registry.py | 400f7a9e68dc7935071dbbeadc422d82c7bab4c6d342247685d1a1bc649777ee |

## C4 - floors RUN by certifier (detached worktree at df07e98e; live tree never mutated)

| Floor | Command | Result | Exit |
|-------|---------|--------|------|
| Declared | python -m unittest tests.test_validate_topic_registry -q | 18 tests, OK | 0 |
| Full CI-equivalent | python -m unittest discover -s tests -t . | 957 tests, OK (skipped=6) | 0 |

Both builder claims ("18 OK", "957 OK (skipped=6)") reproduce exactly. The full-repo command is
what `.github/workflows` line 27 actually runs, so declared and CI floors agree on runner. I read
the workflow rather than assuming: sibling repos in this wave differ (DFDU is `pytest tests/`),
and a pytest-function test would not execute under unittest discover at all.

## C5 - success criteria re-verified (driven as a PROCESS, not via the summary dict)

| # | Criterion | Observed | Verdict |
|---|-----------|----------|---------|
| 1 | Absent `_canon/topics.yaml` -> non-zero exit | exit=2 | PASS |
| 2 | Message is not `All topic-registry checks passed.` | SUCCESS_MESSAGE absent from stdout+stderr; stderr carries the ERROR line | PASS |
| 3 | Present valid input -> green / exit 0 | exit=0, `pages=1 topics=1 errors=0 warnings=0` | PASS |
| 4 | Falsifier in evidence | reproduced independently - see C6 P4/P5 | PASS |

**Instrument correction, recorded for honesty.** My first criterion-3 fixture used `id:`/`label:`
keys and the process exited 1. That was a bad-fixture artifact, not a product defect - the real
schema is `name:`/`keywords:` per the repo's own `_write_topics_yaml` helper. I diagnosed the
traceback before reporting anything; a negative from an unverified instrument is not a finding.
Re-run with the repo's fixture shape gives exit 0 as above.

## C6 - vacuity falsifier (isolated worktree; world mutation; restored)

**P3 - discarded as too weak, recorded anyway.** Wholesale revert of the script to `2da101df`
produced a RED, but the RED was `ImportError: cannot import name 'ABSENT_INPUT_MESSAGE'` - the
test module failed to import. That reds for any test file importing a new symbol and says nothing
about whether the behaviour assertion is load-bearing. Not counted.

**P4 - behaviour-only revert, module kept importable.** Restored the old graceful early-exit body
(`render_validation_report([], wiki_root)`, the old "skipped" stderr line, and the old
zero-summary with no `input_absent`/`exit_code` keys) while leaving `ABSENT_INPUT_MESSAGE` and
`SUCCESS_MESSAGE` defined. Mutated lines printed back.

```
python -m unittest tests.test_validate_topic_registry -q
Ran 18 tests   FAILED (failures=2)   exit 1
FAIL: test_absent_input_process_exit_nonzero
FAIL: test_topics_yaml_absent_is_error_not_success
```

Assertion failures, not import failures. The two new tests are load-bearing against exactly the
behaviour the atom changed.

**P5 - vacuity control.** Held the P4 mutation and reverted the test file to `2da101df`
(9226 bytes, confirmed not to contain `test_topics_yaml_absent_is_error_not_success`), mutation
confirmed still present in the script.

```
Ran 17 tests   OK   exit 0
```

That is the pair that justifies the atom: under a script that treats absent input as a clean
skip, the old suite greens and the new suite fails. Reproduced, not read off the evidence file.

## C7 - MOD-8 silent-skip gate

Not applicable. `tests/ci_no_silent_skips.py` does not exist in EMCC.Library; that gate is an
EMCC-repo artifact (merged there as cb7b7876). The 6 skips in the full floor are pre-existing and
unattributed by any blocking gate in this repo - see C4 carry below.

## C10 - probes restored

Both scratch worktrees removed. Library live tree verified unchanged at `df07e98e`, no modified
tracked files.

## Carries (non-blocking; Director decisions - I acted on none of them)

**C1 - fail-closed on absent input, fail-OPEN on actual validation errors.** The `__main__`
exit gate reads `if summary.get("input_absent") or summary.get("exit_code")`. Neither key is set
on the normal path, so a run with real findings exits 0. Verified as a process, not inferred:

```
present topics.yaml + page referencing an unresolved topic
-> exit=0  ::  topic_registry_validation: pages=1 topics=1 errors=1 warnings=0
```

So a CI step invoking this script goes green with `errors=1`. This is outside the atom's declared
scope (absent-input only) and the atom does not worsen it, so it is not blocking. But the atom's
own framing is "absent input is a failure, not a skip-green" - and by the same reasoning a
detected error that exits 0 is a finding-green. Worth an assurance slot: make the exit code a
function of `errors_count` as well.

**C2 - declared tip is the product commit itself.** Handoff declares `2da101df..f677ae2f`, which
excludes the handoff and audit commits. The body flags "re-resolve if docs tip advances" but the
front-matter field was not updated. I certified `2da101df..df07e98e`. Product blob identical at
both, so nothing substantive rides on the gap. Fifth atom in a row with this shape - my standing
suggestion is to declare base + product commit and let the certifier resolve the tip.

**C3 - certified tip is UNPUSHED.** `git branch -r --contains df07e98e` returns nothing;
`origin/grok/a4-mod13-topic-registry-absent-input` is at `0d046df0`. The AUDITOR_PASS commit
exists only locally, so a fresh clone, CI on PR #74, and the dashboard currently see a branch
whose `auditor_ref` file does not exist. Same shape as A2-MOD-7 C2 and A3-MOD-12 C3. Push
`df07e98e` before the Director closes dual-PASS, then re-confirm the tip has not advanced.

**C4 - 6 unattributed skips in the Library full floor.** `OK (skipped=6)` with no per-test
attribution, because this repo has no equivalent of EMCC's blocking `ci_no_silent_skips.py`. I am
not asserting any of them is wrong - I did not enumerate them and that is outside this atom. Only
noting that Library CI cannot presently distinguish an expected skip from a newly-silent one,
which is the exact gap MOD-8 closed for EMCC.

**C5 - `cert_class` is still `parked-awaiting-cross-model`.** This CERT_PASS supplies the
cross-model leg (builder grok, certifier claude, decorrelation cross). Should move to
`cross-model-certified` and the caveat retire. Not mine to edit.

## Explicit refuses (CF5 / CF6 / CF7)

- Did not build, merge, push, open a PR, or dual-PASS close.
- Did not edit the immutable handoff body, the product script, or the product tests.
- Did not count P3 as a falsifier: an ImportError RED is not evidence that an assertion is
  load-bearing.
- Did not report my first criterion-3 run as a failure: the traceback showed my own fixture used
  the wrong schema keys.
- Did not fail the atom on C1 - the fail-open-on-errors path predates this change and lies
  outside the declared scope.
- Did not certify more than one atom this iteration (CF1); FAIL would have isolated here (CF9).
