# Evidence — W2-MOD-14 cross_manual consumption

**atom:** `W2-MOD-14`  
**directive_id:** `dir-20260801-w2-mod14-cross-manual`  
**repo:** `EMCC.Library`  
**builder:** `grok:EMCC-dfdu`  
**attempt:** 1

## PREM-1

`Topic.cross_manual` was type-checked in `_lib/topics.py` and never read by
`cross_link_topics.compute_related_files` / `run()` — present-and-vacuous control.

## Fix

- `compute_related_files(..., wiki_root, topic_cross_manual)` filters cross-container
  candidates when the topic is in the registry with `cross_manual: false`.
- `run()` loads `_canon/topics.yaml` and passes the flag map.
- Topics absent from the registry keep pre-MOD-14 allow-cross back-compat.

## Suite

```text
python -m unittest tests.test_cross_link_topics -q
→ Ran 52 tests … OK
```

## Falsifier

Without the flag map, cross-container peers are admitted again
(`test_falsifier_ignoring_flag_would_include_cross`).

## Scope

MOD-15 not bundled.
