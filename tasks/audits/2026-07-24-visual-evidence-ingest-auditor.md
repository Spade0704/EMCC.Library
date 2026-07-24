---
date: 2026-07-24
slug: 2026-07-24-visual-evidence-ingest
target: Biz.Automation/wikisys.library/_scripts/validate_visual_evidence.py + _config/asset_registry.yaml (B3+B4)
branch: feat/visual-evidence-ingest
range: 25eb936..5f7f054
certified_code_commit: ec5960c
regime: B (independent verification of builder's change)
builder: lattice:EMCC.Library (Librarian session)
auditor: Lattice Auditor (independent subagent; builder != auditor)
verdict: PASS
---

# Auditor verdict — Lane-6 B3+B4 (§9.9 visual-evidence validator + game classes)

## Scope
B3: game asset_classes (sprite/base-identity/pose-anim-frame/audio-cue) → config.
B4: `validate_visual_evidence.py` — stdlib walker over the shared schema + R1/R2 +
registry checks 1 (sha256) & 3 (path-binding). Stacked on #70 (fsync) + #71 (schema).

## Independent test re-run (Windows 11, Python 3.13.14)
Two passes were run by the independent Auditor across the build:
- Pre-hardening (94637e5): **Ran 28 → OK**, full **Ran 945 → OK (skipped=6)**.
- Post-hardening (ec5960c): **Ran 31 → OK**, full **Ran 948 → OK (skipped=6)**.

## Correctness (confirmed independently)
- Schema walker: union type-lists, required, enum, nested required, array items all
  enforced; `integer`/`number` correctly exclude bool. Sound for the frozen v0.1 schema.
- R1 (base_asset_ref XOR fresh-gen — no list bypass), R2 (name.strip()) correct.
- `sidecar_to_recipe`: scalar-only recipe, style_bible flatten, derived_from mapping
  correct (fresh-gen→[], object+ast_id→[ast_id], object w/o ast_id→[]). No RECORD_FIELDS
  change.
- check_mechanical: chunked sha256 re-hash + path-binding; refuse-branch returns before
  hashing.

## Two info findings — RAISED then CLOSED (hardening folded in + re-verified)
1. **Path traversal** (check_mechanical): now sandboxed — absolute / `..`-escaping
   `asset_path` refused before any hash; `root not in resolved.parents and resolved != root`
   is sound with no false-positive on legitimate nested paths (verified live).
   Test `test_dotdot_escaping_path_refused` plants a real out-of-root file and asserts
   refusal. **CLOSED.**
2. **cert_class root-only** → now recursive via `_contains_key` (dicts+lists, any depth);
   a nested `cert_class` is flagged. Test `test_cert_class_nested_rejected`. **CLOSED.**

## Process note (raised, resolved)
The Auditor's second pass caught (concurrently with the builder's own catch) that an
intermediate commit (d9fde6a/26e3026) did not contain the hardening in its tree — a
reset-soft/working-tree race. Resolved by re-committing the hardening into **ec5960c**
(verified present) with fresh evidence at **5f7f054**; the pushed branch tip contains the
audited code. Committed artifact == audited code.

## Verdict
**PASS.** Both info findings closed, no bypasses, no regression, tests real + green
(31/948). Library-side gate satisfied (Windows executes-clean + independent Auditor).
Remaining for DUAL PASS: external Grok Windows cross-check.
