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
status: done
verdict: PASS
verdict_ref: tasks/audits/2026-08-01-w2-mod14-cross-manual-lattice-certifier-r2.md
phase: build
created_at: 2026-08-01T20:30:00Z
updated_at: 2026-08-01T24:00:00Z
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
cert_class: cross-model-certified
decorrelation: cross
wake_build: false
caveat: "cross-model-certified after Claude CERT_PASS r2 + Director dual-PASS close-20260801-w2-mod14-dual-pass. Product d4d9c5e; PR #76 human merge before #77."
---

# CERT_REQ - W2-MOD-14 cross_manual (PR #76) - DUAL_PASS CLOSED

- **Builder:** grok:EMCC-dfdu
- **Auditor:** grok:EMCC-Auditor AUDITOR_PASS r2
- **Certifier:** claude CERT_PASS r2 (blocking=0)
- **Director:** dual-PASS close-20260801-w2-mod14-dual-pass
- **Product:** d4d9c5e unset-means-allow + loud cross_manual drops
- **Human:** squash-merge #76 then #77 (stack)

## Executes-clean

```
pytest tests/test_cross_link_topics.py tests/_lib/test_topics.py -q
# 86 passed
```

## Policy

EMCC tasks/decisions/2026-08-01-w2-mod14-cross-manual-default.md (unset means ALLOW)
