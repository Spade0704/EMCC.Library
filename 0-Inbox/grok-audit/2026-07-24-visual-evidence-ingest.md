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
updated_at: 2026-07-24T06:45:00Z
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 25eb936a887ea133bd35fe973a135756a36bfecb..616c9cb
base: 25eb936a887ea133bd35fe973a135756a36bfecb
pr: https://github.com/Spade0704/EMCC.Library/pull/72
proposal: wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_4.md §9.9 + §9.10 + council EMCC/tasks/council/2026-07-24-visual-evidence-standard.md
auditor_verdict: PASS
auditor_ref: tasks/audits/2026-07-24-visual-evidence-ingest-auditor.md + tasks/audits/2026-07-24-b5-base-identity-auditor.md
evidence_ref: tasks/evidence/2026-07-24-visual-evidence-ingest-windows-tests.txt + tasks/evidence/2026-07-24-b5-base-identity-windows-tests.txt
cert_class: cross-model-certified
certifier_model: grok
builder_model: lattice
---

# Cert request — Lane-6 B3+B4+B5: registry-side visual-evidence ingest (FOLDED)

**FOLD (Director-approved 2026-07-24T06:41:16Z):** one Grok cert over the whole
registry-side visual-evidence ingest — B3 + B4 + B5 — since B3+B4's cert had not been
picked up. **Cert range = `25eb936..616c9cb`** (updated from the earlier B3+B4-only
`..5f7f054`). Two registered directives cover it: `dir-20260724-library-visual-evidence-ingest`
(B3+B4, directive_ref) + `dir-20260724-library-visual-evidence-b5` (B5).

**Stacked branch** `feat/visual-evidence-ingest` = `4763b0a` (fsync #70, already Grok-PASS)
→ `25eb936` (schema v0.1 #71) → `ec5960c` (B3+B4) → `8f9f555` (B5) → `616c9cb` (evidence).
Base `25eb936` includes #70+#71 so the suite is honestly green (a plain-main base is RED
from the unmerged EBADF). Merge order: #70 → #71 → #72.

## What (all against the ONE shared schema — same artifact Anvil `--strict-assets` consumes)
- **B3**: game asset_classes `sprite`/`base-identity`/`pose-anim-frame`/`audio-cue` (§9.8).
- **B4**: `validate_visual_evidence.py` — stdlib walker over the schema + **R1**/**R2** +
  registry checks **1** (sha256 re-hash) & **3** (path-binding, sandboxed). `cert_class`
  rejected at any depth. `sidecar_to_recipe` folds into an EXISTING §9.1 record's
  `recipe:`/`derived_from` — NO RECORD_FIELDS change. (§9.9)
- **B5**: **base-identity binding** — a derived frame's `base_asset_ref{ast_id,path,sha256}`
  must bind to an APPROVED REGISTERED base (resolve ast_id in both zones' `_registry/`,
  assert class==`base-identity`, re-hash base on disk == declared sha; fresh-gen/null skip)
  + **style-bible** path resolution. Perceptual-distance + palette-subset = Anvil pixel
  floor (recorded, not computed). (§9.10)
- Sync-excluded like `asset_registry.py`.

## HARD REQUIREMENT (Director directive; false-PASS lesson holds)
**executes-clean MUST RUN ON WINDOWS.** Producer evidence is Windows.

## Producer evidence (Windows 11, Python 3.13.14)
- `python -m unittest tests.test_validate_visual_evidence` → **Ran 39 → OK**
- `python -m unittest discover -s tests -t .` → **Ran 956 → OK (skipped=6)** (917 + 39)
- Full output: the two `evidence_ref` files.

## Library-side gate (satisfied; builder ≠ certifier)
- Regime B Auditor **PASS** on B3+B4 (2 info findings folded + closed; a commit-state race
  caught + resolved) AND on B5 (commit-state CONFIRMED clean; 2 info findings, no action).
  See both `auditor_ref` files.

## For Grok
Cold-read the `25eb936..616c9cb` diff, re-run the suite **on your Windows certifier host**
(targeted + full), verify: stdlib-only + no new deps; schema walker soundness; R1/R2 +
recursive cert_class + checks 1/3; `sidecar_to_recipe` scalar-only recipe; B5 base-identity
binding (resolve/class/sha) + style-bible resolution; sync exclusion; §9.9/§9.10 conformance.
DUAL PASS (Auditor PASS + your Windows PASS) closes; Director merges after #70 → #71 → #72.
