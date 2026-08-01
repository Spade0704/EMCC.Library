# Evidence — W2-MOD-15 see-also truncation loud / strict

**atom:** `W2-MOD-15`  
**directive_id:** `dir-20260801-w2-mod15-see-also-truncation`  
**repo:** `EMCC.Library`  
**builder:** `grok:EMCC-dfdu`  
**attempt:** 2  
**product:** `00b8d18` (CERT B1 orchestrator fix)  
**prior product:** `44fc05f` (attempt-1 loud WARN + CLI exit)  
**PR:** https://github.com/Spade0704/EMCC.Library/pull/77

## PREM-1 (attempt 1)

`process_page` with `max_links>0` sliced related lists with **no warning** — silent edge drop.

## PREM-2 (CERT B1 — attempt 2)

`cross_link_topics.run` under `fail_on_truncation: true` set `truncation_failed` and CLI `__main__` exited 1, but the **canonical orchestrator** (`update_dashboards` CROSS_LINK_PIPELINE) only caught `Exception`. Policy non-success still printed `#17 -- OK` and orchestrator **exit 0**.

## Fix

### Attempt 1 (`44fc05f`)

- On truncate: stderr `WARNING: codex see-also truncation: ... dropped=N` + `truncation_events`
- Config `see_also.fail_on_truncation` (default false): when true + drops →
  `summary["truncation_failed"]=True` + ERROR + `__main__` exit 1
- Uncapped (`max_links=0`) still green with zero truncation

### Attempt 2 (`00b8d18`) — CERT B1

- After `#17` `module.run(...)`, if result dict has `truncation_failed`: append to orchestrator `failures` with `exc_type=truncation_failed`, WARN on stderr
- `_print_summary` prefers `failures` over result-present → prints `#17 -- FAILED`, not false OK
- Exit path already `return 1 if summary["failures"] else 0` → non-zero once #17 is on failures
- Result dict **retained** for health synthesis (policy fail ≠ missing result)

## Stack

Branch restacked onto MOD-14 tip (`13e205b` / product `d4d9c5e`) via merge `3110913`. MOD-14 product is stack base only — not a second atom in this PR's cert claim.

## Suite (Windows, builder machine)

```text
PYTHONPATH=Biz.Automation/wikisys.library/_scripts
python -m unittest tests.test_cross_link_topics tests.test_update_dashboards -q
→ Ran 72 tests … OK
```

Targeted CERT B1:

```text
python -m unittest tests.test_update_dashboards.TestCrossLinkPipeline.test_truncation_failed_is_orchestrator_non_success -v
→ ok
python -m unittest tests.test_cross_link_topics.SeeAlsoTruncationLoudTests -v
→ 4 OK (WARN events, run.truncation_failed, uncapped green, CLI exit 1)
```

## Falsifier

1. Without WARN path / events → `test_process_page_truncation_warns_and_records` RED.
2. Without orchestrator check of `truncation_failed` → `test_truncation_failed_is_orchestrator_non_success` RED (`#17 -- OK`, rc would be 0 if failures empty).
3. CLI process path without `sys.exit(1)` → `test_cli_process_exits_1_on_fail_on_truncation` RED.

## Scope

- Product paths: `cross_link_topics.py` (attempt 1), `update_dashboards.py` (attempt 2), tests.
- No merge / no self-audit / handoff stays `awaiting_auditor` until Regime-B.
