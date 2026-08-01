---
schema: cert-handoff/v1.1
certifier_id: claude
producer_id: grok:EMCC-dfdu
builder_id: grok:EMCC-dfdu
builder_llm: grok
builder_model: grok
certifier_model: claude
director_id: grok:EMCC-Director
directive_ref: tasks/orchestrator-log.jsonl#dir-20260801-w2-mod14-cross-manual
slug: 2026-08-01-w2-mod14-cross-manual
attempt: 2
status: awaiting_auditor
phase: build
created_at: 2026-08-01T20:30:00Z
updated_at: 2026-08-01T23:30:00Z
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: PLACEHOLDER
branch: grok/w2-mod14-cross-manual-consume
pr: 76
proposal: W2-MOD-14 rework — cross_manual unset-means-allow + loud drops (CERT_FAIL B1)
auditor_verdict: pending
auditor_id: ""
auditor_seat: grok:EMCC-Auditor
auditor_ref: ""
evidence_ref: tasks/audits/2026-08-01-w2-mod14-cross-manual-evidence.md
spec_author_llm: grok
spec_author_seat: grok:EMCC-Director
cert_class: parked-awaiting-cross-model
decorrelation: cross
wake_build: false
caveat: "parked-awaiting-cross-model is NOT cross-model certified. status: awaiting_auditor (rul-20260801). Attempt 2 after CERT_FAIL B1; policy EMCC tasks/decisions/2026-08-01-w2-mod14-cross-manual-default.md. Flip to pending only after Regime-B PASS."
---

# CERT_REQ - W2-MOD-14 cross_manual rework (PR #76 attempt 2)

Hold for Regime-B Auditor. Not claimable until `status: pending`.

## Independence

- **Builder:** `grok:EMCC-dfdu`
- **Auditor (owed):** `grok:EMCC-Auditor`
- **Certifier (later):** Claude
- **Policy:** EMCC `tasks/decisions/2026-08-01-w2-mod14-cross-manual-default.md`

## Success criteria

1. Registry present + field **unset** → cross-container edges **kept** (no silent mass drop)
2. Explicit `cross_manual: false` → same-container only + **loud** WARNING + `cross_manual_drops > 0`
3. Explicit `true` / no registry → allow cross (back-compat)
4. Tests cover unset-with-registry branch (attempt-1 gap)
5. MOD-15 not bundled

## Executes-clean

```
python -m pytest tests/test_cross_link_topics.py tests/_lib/test_topics.py -q
# 86 passed
```

## Product paths

- `Biz.Automation/wikisys.library/_scripts/cross_link_topics.py`
- `Biz.Automation/wikisys.library/_scripts/_lib/topics.py`
- `Biz.Automation/wikisys.library/_template/_canon__SEP__topics.yaml`
- `tests/test_cross_link_topics.py`
- `tests/_lib/test_topics.py`

## Range (C1)

`merge-base(origin/main)..PR tip` after push; product rework commit ancestor of tip.
