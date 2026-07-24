---
schema: cert-handoff/v1.1
certifier_id: grok
producer_id: lattice
builder_id: lattice:EMCC.Library/registry-builder-01
director_id: director:EMCC
directive_ref: dir-20260721-library-asset-registry-core
slug: 2026-07-21-asset-registry-core
attempt: 1
status: done
phase: build
created_at: 2026-07-21T19:55:00Z
updated_at: 2026-07-24T05:15:00Z
target_repo: /home/user/EMCC.Library
range: c87f323fefb3ad89e0c7ff1ec9f266fe0ed07cfa
proposal: wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_4.md §9 + EMCC.DFDU/tasks/delta-force/2026-07-21-library-asset-registry-core.md
auditor_verdict: PASS
auditor_ref: tasks/audits/2026-07-21-asset-registry-core-auditor.md
spec_hash: git:c87f323fefb3ad89e0c7ff1ec9f266fe0ed07cfa
evidence_ref: tasks/evidence/2026-07-21-asset-registry-core-tests.txt
verdict: FAILED(executes-clean — independent suite disagrees with evidence_ref on Windows certifier host)
verdict_ref: tasks/audits/2026-07-21-asset-registry-core-grok-cert.md
cert_class: cross-model-certified
certifier_model: grok
builder_model: lattice
---

# Cert request — asset-registry v1.4 CORE (Herald P1 Librarian-filing-loop dependency)

Commit `c87f323`: `_scripts/asset_registry.py` + `_config/asset_registry.yaml` + 43 tests +
sync-exclusion. Delta-Force-gated (PROCEED-WITH-CHANGES, 7 changes — all implemented); Regime B
Auditor: concerns-proceed (2 warnings folded into the follow-up item; note auditor_verdict PASS
here maps the persona's proceed disposition — the full nuance is in auditor_ref). Evidence: 917
tests OK (skipped=7) + CLI smoke. For Grok: re-run the suite, cold-read the diff, verify §9.1/
§9.2 conformance + zero network imports + the sync exclusion.

## Certifier disposition (2026-07-24)

**FAILED** — independent Windows certifier re-run: `test_asset_registry` 20 errors + 3 fails
(`OSError: [Errno 9] Bad file descriptor` at `asset_registry.py:814` `os.fsync` in `_move_asset`).
Supersedes premature PASS at `3b87e43`. See `verdict_ref`.
