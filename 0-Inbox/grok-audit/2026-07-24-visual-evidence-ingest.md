---
schema: cert-handoff/v1.1
certifier_id: grok
producer_id: lattice
builder_id: lattice:EMCC.Library/registry-builder-01
director_id: director:EMCC
directive_ref: dir-20260724-library-visual-evidence-ingest
slug: 2026-07-24-visual-evidence-ingest
attempt: 1
status: pending
phase: build
created_at: 2026-07-24T06:25:00Z
updated_at: 2026-07-24T06:25:00Z
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 25eb936a887ea133bd35fe973a135756a36bfecb..5f7f054b6c939d4e64d80d0d84ce93d6070c6240
base: 25eb936a887ea133bd35fe973a135756a36bfecb
pr: https://github.com/Spade0704/EMCC.Library/pull/72
proposal: wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_4.md §9.9 + council EMCC/tasks/council/2026-07-24-visual-evidence-standard.md
auditor_verdict: PASS
auditor_ref: tasks/audits/2026-07-24-visual-evidence-ingest-auditor.md
evidence_ref: tasks/evidence/2026-07-24-visual-evidence-ingest-windows-tests.txt
cert_class: cross-model-certified
certifier_model: grok
builder_model: lattice
---

# Cert request — Lane-6 B3+B4: §9.9 visual-evidence validator + game asset_classes

**Stacked branch.** `feat/visual-evidence-ingest` = `4763b0a` (fsync fix, PR #70,
already Grok-PASS) → `25eb936` (shared schema v0.1, PR #71) → `ec5960c` (B3+B4 code) →
`5f7f054` (evidence). **Cert range = `25eb936..5f7f054`** (the B3+B4 delta only; the fsync
fix and schema landing were certified/handled separately). Base `25eb936` includes #70+#71
so the suite is honestly green — a plain-main base would be RED from the unmerged EBADF.

## What
- **B3**: game asset_classes `sprite`/`base-identity`/`pose-anim-frame`/`audio-cue` →
  `_config/asset_registry.yaml` (§9.8 Operator-trigger).
- **B4**: `validate_visual_evidence.py` — a **stdlib** walker (no `jsonschema` pip) over the
  SHARED canonical schema `wiki.codex/git/codex/schemas/visual-evidence.schema.json` (the
  SAME artifact iron-soul-anvil `pnpm anvil test --strict-assets` consumes) + council rules
  **R1** (base_asset_ref XOR fresh-gen) / **R2** (signoff name non-empty) + registry-side
  **check-1** (sha256 re-hash) & **check-3** (path-binding, sandboxed). Checks 2/4/6 are the
  Anvil pixel floor (§9.9). `cert_class` rejected at ANY depth in a sidecar (anti self-cert).
  `sidecar_to_recipe` folds the sidecar into an EXISTING §9.1 record's `recipe:`/`derived_from`
  — **NO RECORD_FIELDS change** (recipe is a freeform scalar mapping). Sync-excluded like
  `asset_registry.py`.

## HARD REQUIREMENT (Director directive; the false-PASS lesson holds)
**executes-clean MUST RUN ON WINDOWS.** Producer evidence is Windows.

## Producer evidence (Windows 11, Python 3.13.14)
- `python -m unittest tests.test_validate_visual_evidence` → **Ran 31 → OK**
- `python -m unittest discover -s tests -t .` → **Ran 948 → OK (skipped=6)** (917 + 31)
- Full output: `evidence_ref`.

## Library-side gate (satisfied; builder ≠ certifier)
- Regime B Auditor **PASS** (`auditor_ref`) — independent Windows re-run (31/948). Two info
  findings (path-sandbox, recursive cert_class) RAISED then folded in + re-verified CLOSED;
  a concurrent commit-state race was resolved by re-committing the hardening into `ec5960c`
  (committed artifact == audited code; pushed tip `5f7f054`).

## For Grok
Cold-read the `25eb936..5f7f054` diff, re-run the suite **on your Windows certifier host**
(targeted + full), verify: stdlib-only + no new deps; the walker soundly enforces the schema
subset; R1/R2 + recursive cert_class + checks 1/3 correct; `sidecar_to_recipe` yields
scalar-only recipe (else §9 frontmatter refuses it); sync exclusion; no §9.9 contradiction.
DUAL PASS (Auditor PASS + your Windows PASS) closes; Director merges after #70 → #71 → #72.
