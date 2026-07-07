---
date: 2026-07-07
finding: LIB-09
repo: EMCC.Library
role: chief@EMCC.CRW (independent cross-check)
pr: EMCC.Library#64
fix_sha: ec7a887
base_sha: 78b51e2
branch: fix/lib-09-ci-matrix
actions_run: 28889908139
producer_model: claude-opus-4-8
cross_check_model: claude-opus-4-8
same_model_fallback: true
security: false
verdict: PASS
---

# Cross-check — LIB-09 (CI python 3.10–3.13 matrix + compileall + root pyproject)

FRESH session, independent identity (Chief from EMCC.CRW); built none of it. Diff read
cold; suite re-run in an isolated worktree @ `ec7a887`; GH Actions run pulled directly
(claim NOT trusted).

Diff = 2 files, +47/-1: `.github/workflows/test.yml` (+11/-1), `pyproject.toml` (+37, new).

## (a) YAML valid, matrix 3.10–3.13, fail-fast:false
- `strategy.matrix.python-version: ["3.10", "3.11", "3.12", "3.13"]` — exactly the 4 legs.
- `fail-fast: false` present → every version reports independently.
- setup-python consumes `${{ matrix.python-version }}` (was hardcoded `"3.11"`). Valid YAML.

## (b) ADDITIVE — runner unchanged, nothing weakened
- Test runner UNCHANGED: `python -m unittest discover -s tests -t .` (NOT swapped to pytest).
- `compileall -q scripts tests "Biz.Automation/wikisys.library/_scripts"` ADDED — a new
  static-check gate, additive only.
- No `continue-on-error`, no `|| true`, no `allow-failure` anywhere in the workflow (grep clean).
- ruff is simply ABSENT (deferred), NOT a silenced red — there is no ruff step to silence.
- pyproject.toml is new + additive: `requires-python = ">=3.10"`, no test-runner/tool config
  that would redirect the gate. No existing gate removed.

## (c) Repo suite still passes (re-run in worktree @ ec7a887)
```
$ python -m unittest discover -s tests -t .
Ran 873 tests in 20.75s
OK (skipped=6)
```
873 OK. The 6 skips are PRE-EXISTING (`_canon/topics.yaml not found; topic registry
validation skipped` — environmental, fires on base too), NOT introduced by this diff (which
touches only workflow + pyproject, no test files). Library runs plain unittest-discover (no
strict-skip gate), so these skips are acceptable and unchanged. `compileall scripts tests` → exit 0.

## (d) GH Actions run GENUINELY green across the matrix (pulled, not claimed)
`gh run view 28889908139 -R Spade0704/EMCC.Library --json ...`:
- `conclusion: success`, `status: completed`, `event: pull_request`, `workflowName: tests`
- `headSha: ec7a887…` == `origin/fix/lib-09-ci-matrix` head == the fix sha (run is on the right commit).
- 4/4 legs ✓: `test (3.10)`, `test (3.11)`, `test (3.12)`, `test (3.13)` all passed.
- Only annotations are the Node.js-20-deprecation NOTICE (a warning, not a failure).
Claimed 4/4 green — CONFIRMED independently.

## Independence
Independent IDENTITY (fresh session, cold diff, own worktree + own gh pull), NOT independent
model (both opus-4-8, shared FS) — `same_model_fallback: true`. Light-of-security (mechanical
CI, no security surface): this PASS + the green matrix = merge-ready, no Grok slot needed.

## Verdict
**PASS** — matrix is 3.10–3.13 + fail-fast:false, change is strictly additive (unittest-discover
runner intact, compileall added, no gate weakened, ruff-defer is absent not silenced), suite
passes (873 OK), and Actions run 28889908139 is genuinely 4/4 green on the fix sha.
