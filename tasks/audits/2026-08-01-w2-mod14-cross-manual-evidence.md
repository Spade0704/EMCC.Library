# Evidence — W2-MOD-14 cross_manual consumption (attempt 2 rework)

**atom:** `W2-MOD-14`  
**directive_id:** `dir-20260801-w2-mod14-cross-manual`  
**repo:** `EMCC.Library`  
**builder:** `grok:EMCC-dfdu`  
**attempt:** 2  
**policy:** EMCC `tasks/decisions/2026-08-01-w2-mod14-cross-manual-default.md` (unset-means-allow)

## PREM-1 (attempt 1)

`Topic.cross_manual` was type-checked and unread — present-and-vacuous.

## CERT_FAIL B1 (attempt 1)

Attempt 1 bound schema default `False` for every registry topic (including key-absent).
On wiki.codex, zero of 10 topics set the field → silent drop of ~300/630 related_files
edges, exit 0, no warning. Tests stayed green because the unset-with-registry branch
was untested.

## Fix (attempt 2)

1. **`Topic.cross_manual: Optional[bool] = None`** — key omitted → `None` (allow).
2. **`run()` map is explicit-only** — topics with `cross_manual is None` are not inserted;
   `compute_related_files` already treats map-absent as allow-cross.
3. **Loud drop** — each explicit-`false` cross-container exclusion records a drop event;
   `run()` prints one stderr WARNING summary + `cross_manual_drops` in the summary dict.
4. **Tests added**
   - `test_registry_present_field_unset_allows_cross` (cert B1 missing branch)
   - `test_cross_manual_false_drop_is_loud`
   - `test_compute_records_drop_events_on_explicit_false`
5. Template comment amended to unset-means-allow.

## Suite

```text
python -m pytest tests/test_cross_link_topics.py tests/_lib/test_topics.py -q
→ 86 passed
```

## Falsifier

- Explicit `false` still drops cross-container + warns.
- Without map / with unset key, cross-container is admitted.

## Scope

MOD-15 not bundled (same file later; stack 14 before 15).
