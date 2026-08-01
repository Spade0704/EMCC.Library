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
status: pending
phase: build
created_at: 2026-08-01T20:30:00Z
updated_at: 2026-08-01T23:45:00Z
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 3782f5eab606e2d63f1d20205b03e5e484e91760..d4d9c5e13bd5a272c6b430eeab62cf1d9f96ad58
branch: grok/w2-mod14-cross-manual-consume
pr: 76
proposal: W2-MOD-14 rework cross_manual unset-means-allow + loud drops (CERT_FAIL B1)
auditor_verdict: PASS
auditor_id: grok:EMCC-Auditor
auditor_seat: grok:EMCC-Auditor
auditor_ref: tasks/audits/2026-08-01-w2-mod14-cross-manual-auditor-r2.md
evidence_ref: tasks/audits/2026-08-01-w2-mod14-cross-manual-evidence.md
spec_author_llm: grok
spec_author_seat: grok:EMCC-Director
cert_class: parked-awaiting-cross-model
decorrelation: cross
wake_build: false
caveat: "parked-awaiting-cross-model is NOT cross-model certified. Regime-B AUDITOR_PASS r2 after CERT_FAIL B1 rework. External cert Claude (builder_llm=grok). Policy: unset-means-allow."
---

# CERT_REQ - W2-MOD-14 cross_manual rework (PR #76 attempt 2)

You are **Claude External Certifier**. Claimable: `status: pending` + `auditor_verdict: PASS`.

Not Director. Not Grok builder. Not Grok Auditor.

## Independence

- **Builder:** `grok:EMCC-dfdu`
- **Auditor:** `grok:EMCC-Auditor` — **AUDITOR_PASS r2** at `auditor_ref`
- **Prior:** attempt-1 AUDITOR_PASS then CERT_FAIL B1 (silent mass drop via default False)
- **Policy:** EMCC `tasks/decisions/2026-08-01-w2-mod14-cross-manual-default.md`

## Success criteria

1. Registry present + field **unset** → cross-container edges **kept**
2. Explicit `cross_manual: false` → same-container only + **loud** WARNING + drops > 0
3. Explicit `true` / no registry → allow cross
4. Tests cover unset-with-registry branch
5. MOD-15 not bundled

## Product

- `cross_link_topics.py` + `_lib/topics.py` + template topics.yaml
- Tests: CrossManualConsumeTests (incl. registry-present/field-unset)

## Executes-clean

```
python -m pytest tests/test_cross_link_topics.py tests/_lib/test_topics.py -q
# Auditor r2: 86 passed
```

## Range (C1)

Product `d4d9c5e` inside range; tip may advance with this auditor commit.
