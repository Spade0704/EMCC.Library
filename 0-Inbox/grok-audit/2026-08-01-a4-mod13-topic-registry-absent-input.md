---
schema: cert-handoff/v1.1
certifier_id: claude
producer_id: grok:EMCC-dfdu
builder_id: grok:EMCC-dfdu
builder_llm: grok
builder_model: grok
certifier_model: claude
director_id: grok:EMCC-Director
directive_ref: tasks/orchestrator-log.jsonl#dir-20260801-a4-mod13-topic-registry-absent-input
slug: 2026-08-01-a4-mod13-topic-registry-absent-input
attempt: 1
status: awaiting_auditor
phase: build
created_at: 2026-08-01T22:05:00Z
updated_at: 2026-08-01T22:05:00Z
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 2da101dfdadb93b2c5bd504af9c6887e58a36069..f677ae2ff128cfd999f3711ec63eec9b14bb9a36
branch: grok/a4-mod13-topic-registry-absent-input
pr: 74
proposal: A4-MOD-13 validate_topic_registry ERROR+nonzero when topics.yaml absent; present valid stays green
auditor_verdict: pending
auditor_id: ""
auditor_seat: grok:EMCC-Auditor
auditor_ref: ""
evidence_ref: tasks/audits/2026-08-01-a4-mod13-topic-registry-absent-input-evidence.md
spec_author_llm: grok
spec_author_seat: grok:EMCC-Director
cert_class: parked-awaiting-cross-model
decorrelation: cross
wake_build: false
caveat: "parked-awaiting-cross-model is NOT cross-model certified. status: awaiting_auditor (rul-20260801) — flip to pending only after Regime-B Auditor PASS. External cert Claude (builder_llm=grok). Coordination root 0-Inbox/grok-audit."
---

# CERT_REQ - A4-MOD-13 topic registry absent-input fail-closed (attempt 1)

You are **not** claimable until Regime-B Auditor PASS and `status: pending`.

**Builder seat only** dropped this with `status: awaiting_auditor` per
`rul-20260801-handoff-awaiting-auditor-convention`.

## Independence

- **Builder:** `grok:EMCC-dfdu`
- **Auditor (owed):** `grok:EMCC-Auditor` != builder
- **Certifier (after auditor):** Claude (`builder_llm=grok`)
- **Directive:** `tasks/orchestrator-log.jsonl#dir-20260801-a4-mod13-topic-registry-absent-input` (flat kind in **this** repo)

## Success criteria

1. Absent `_canon/topics.yaml` → process exit **non-zero**
2. Message is **not** `All topic-registry checks passed.`
3. Present valid input → green / exit 0
4. Falsifier in evidence (hide input → non-success)

## Product

- `Biz.Automation/wikisys.library/_scripts/validate_topic_registry.py`
- `tests/test_validate_topic_registry.py`
- No MOD-14/15 bundling

## Executes-clean

```
python -m unittest discover -s tests -t .
# builder: Ran 957 OK (skipped=6)

python -m unittest tests.test_validate_topic_registry -q
# 18 OK
```

## Gate status

| Leg | Status |
|-----|--------|
| Build | this drop |
| Regime-B Auditor | **awaiting** (do not claim pending) |
| Claude CERT | after auditor PASS + status flip |
| Director dual-PASS | not yet |
| Human merge | PR only after dual-PASS |

## Range (C1)

`merge-base(origin/main)..PR tip`; product commit must be ancestor of tip.
