# DUAL-PASS CLOSE - W2-MOD-14 cross_manual (PR #76)

- **Close id:** `close-20260801-w2-mod14-dual-pass`
- **Wave:** WAVE-E E2
- **Director:** `grok:EMCC-Director`
- **Verdict:** **DUAL_PASS**
- **Status:** `dual_pass_closed_pending_human_merge`
- **Date:** 2026-08-01

## Chain

| Leg | Result |
|-----|--------|
| Build | product `d4d9c5e` unset-means-allow + loud drops (attempt 2) |
| Auditor | PASS r2 (`tasks/audits/2026-08-01-w2-mod14-cross-manual-auditor-r2.md`) |
| Certifier | CERT_PASS blocking=0 (`...-lattice-certifier-r2.md`) |
| Director | DUAL_PASS this file |
| Policy | EMCC `tasks/decisions/2026-08-01-w2-mod14-cross-manual-default.md` |

## Human next

Squash-merge **#76** then **#77** (stacked: #77 bases on #76). WAVE-E E3 dual-PASS pack next.

## Carries (non-blocking from cert)

C1 range ends at product; C2 ASCII handoff preferred; C3 cert_class move on close; C4 aggregate drop warn.

## STATUS

```text
STATUS|W2-MOD-14|DUAL_PASS
pr=76
product=d4d9c5e
next=human-merge-#76-then-#77
```
