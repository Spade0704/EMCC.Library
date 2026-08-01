# Evidence — A4-MOD-13 validate_topic_registry absent-input fail-closed

**atom:** `A4-MOD-13`  
**directive_id:** `dir-20260801-a4-mod13-topic-registry-absent-input`  
**repo:** `EMCC.Library`  
**builder:** `grok:EMCC-dfdu` (Lattice)  
**product:** `Biz.Automation/wikisys.library/_scripts/validate_topic_registry.py`  
**tests:** `tests/test_validate_topic_registry.py`

## Problem

When `_canon/topics.yaml` was **absent**, `run()` wrote a dashboard via
`render_validation_report([], …)` which embeds
**"All topic-registry checks passed."** and returned `errors_count: 0`.
CLI `__main__` always exited 0. A gate wiring this script got permanent green
meaning "found nothing to check."

## Fix (fail-closed)

1. `render_absent_input_report()` — ERROR dashboard body; **never** `SUCCESS_MESSAGE`.
2. `run()` on missing `topics.yaml`: `input_absent=True`, `errors_count=1`, `exit_code=2`,
   stderr prints `ABSENT_INPUT_MESSAGE`.
3. `__main__`: `sys.exit(2)` when `input_absent` / `exit_code` set.
4. Present valid registry + clean pages: unchanged green (exit 0).

## Suite (authoritative CI floor)

```text
python -m unittest discover -s tests -t .
→ Ran 957 tests in ~31s
→ OK (skipped=6)
```

Target module:

```text
python -m unittest tests.test_validate_topic_registry -q
→ Ran 18 tests … OK
```

Raw: `tasks/evidence/2026-08-01-a4-mod13-topic-registry-absent-input.txt`

## Falsifier (criterion 4)

Hide/remove input: empty temp wiki without `_canon/topics.yaml`:

- `run()` → `input_absent=True`, `errors_count=1`, dashboard lacks success text
- CLI subprocess → **returncode != 0**, stderr contains ERROR, not success path

Recorded by:

- `test_topics_yaml_absent_is_error_not_success`
- `test_absent_input_process_exit_nonzero`

## Scope

MOD-14 / MOD-15 **not** bundled. Topic registry validator only.

## dual-PASS remaining (Phase B — not this seat)

Regime-B Auditor → flip handoff `status: pending` → Claude External Cert → Director close → human merge.
