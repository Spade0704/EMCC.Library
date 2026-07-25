---
schema: cert-handoff/v1.1
certifier_id: grok
producer_id: lattice
builder_id: lattice:EMCC.Library/registry-builder-01
director_id: director:EMCC
directive_ref: dir-20260726-library-librarian-visual-evidence-op
slug: 2026-07-26-librarian-visual-evidence-op
attempt: 1
status: done
phase: build
created_at: 2026-07-26T00:10:00Z
updated_at: 2026-07-26T22:30:00Z
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 11554de2e88f452123513008662af2579f09a231..eb10f0f197f08283d23cc011a1a5d88bdb1b4668
base: 11554de2e88f452123513008662af2579f09a231
pr: DRAFT (parks for operator morning; human-at-merge)
proposal: wiki.codex/git/codex/CODEX_LIBRARIAN.md v1.5 + CODEX_BUILD_SPEC_v1_4.md §9.9 + §9.10
auditor_verdict: PASS
auditor_ref: tasks/audits/2026-07-26-librarian-visual-evidence-op-auditor.md
evidence_ref: tasks/evidence/2026-07-26-librarian-visual-evidence-op-tests.txt
verdict: PASS
verdict_ref: tasks/audits/2026-07-26-librarian-visual-evidence-op-grok-cert.md
cert_class: cross-model-certified
certifier_model: grok
builder_model: lattice
---

# Cert request — Librarian v1.5 persona op (visual-evidence ingest + base-identity registry)

**Doc/persona class** (additive to the already-landed `validate_visual_evidence.py`, PR #72 on
main). Adds a v1.5 extension to the canonical `CODEX_LIBRARIAN.md` — two operations
(Register-Base-Identity, Ingest-Visual-Asset) + hard rules — and regenerates the drop-in
`.claude/personas/CLAUDE.librarian.md` (the drop-in is GENERATED; drift guard
`tests/test_persona_dropin.py`). Range `11554de..eb10f0f`.

## What
- **Register-Base-Identity**: register an APPROVED base as `asset_class: base-identity`
  (human-approved before a derived frame binds).
- **Ingest-Visual-Asset**: `validate_visual_evidence.py` PASS is a PRECONDITION of the registry
  write (schema + R1/R2 + checks 1/3 + §9.10 base-identity binding + style-bible); on PASS fold
  the sidecar via `sidecar_to_recipe` (recipe scalars + `derived_from`, no RECORD_FIELDS change).
- Hard rules: validate-before-write; two legs never "certified" (`cert_class` handoff-only,
  never a sidecar field); registry proves records+bytes / Anvil proves pixels; flag fresh-gen.

## Producer evidence (Windows 11, Python 3.13.14)
- `python -m unittest tests.test_persona_dropin` → **Ran 8 → OK**
- `generate_persona_dropin.py --check` → **exit 0 (in sync)**
- `python -m unittest discover -s tests -t .` → **Ran 956 → OK (skipped=6)**

## Library-side gate (satisfied; builder ≠ certifier)
- Regime B Auditor **PASS — no findings** (`auditor_ref`): every persona claim corroborated
  against `validate_visual_evidence.py` + spec §9.9/§9.10; drop-in a clean regeneration (drift
  green); verbatim procedures (INGEST/SEMANTIC_LINT) untouched; scope confined to persona +
  drop-in + evidence.

## For Grok
Cold-read the `11554de..eb10f0f` diff. This is doc-class — verify: (1) the v1.5 persona text
does NOT misrepresent what `validate_visual_evidence.py` + §9.9/§9.10 actually do (accuracy is
the cert here); (2) the drop-in EQUALS a regeneration from the canonical (run
`generate_persona_dropin.py --check` on your host → exit 0); (3) full suite green on Windows;
(4) INGEST_PROCEDURE.md / SEMANTIC_LINT_PROCEDURE.md untouched (verbatim-locked). DUAL PASS
(Auditor PASS + your PASS) → the DRAFT PR parks for the Operator's morning merge.
