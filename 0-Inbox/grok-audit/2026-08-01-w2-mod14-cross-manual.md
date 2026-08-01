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
attempt: 1
status: pending
phase: build
created_at: 2026-08-01T20:30:00Z
updated_at: 2026-08-01T22:30:00Z
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 3782f5eab606e2d63f1d20205b03e5e484e91760..f61959508a7b75777c49d75392a12a57994ba0bb
branch: grok/w2-mod14-cross-manual-consume
pr: 76
proposal: W2-MOD-14 wire Topic.cross_manual into cross_link_topics cross-container filter
auditor_verdict: PASS
auditor_id: grok:EMCC-Auditor
auditor_seat: grok:EMCC-Auditor
auditor_ref: tasks/audits/2026-08-01-w2-mod14-cross-manual-auditor.md
evidence_ref: tasks/audits/2026-08-01-w2-mod14-cross-manual-evidence.md
spec_author_llm: grok
spec_author_seat: grok:EMCC-Director
cert_class: parked-awaiting-cross-model
decorrelation: cross
wake_build: false
caveat: "parked-awaiting-cross-model is NOT cross-model certified. Regime-B AUDITOR_PASS (WAVE-E Phase J). External cert Claude (builder_llm=grok)."
---

# CERT_REQ - W2-MOD-14 cross_manual consume (PR #76)

You are **Claude External Certifier**. Claimable: `status: pending` + `auditor_verdict: PASS`.

- **Builder:** grok:EMCC-dfdu
- **Auditor:** grok:EMCC-Auditor AUDITOR_PASS
- **Product:** cross_link_topics consumes Topic.cross_manual

## Executes-clean

```
python -m unittest tests.test_cross_link_topics -q  # 52 OK
```
