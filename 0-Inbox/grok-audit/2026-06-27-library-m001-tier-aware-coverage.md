---
schema: cert-handoff/v1.1
certifier_id: grok
producer_id: lattice
builder_id: lattice
director_id: director
directive_ref: tasks/orchestrator-log.jsonl#dir-2026-06-27-library-m001-tier-aware-coverage
slug: 2026-06-27-library-m001-tier-aware-coverage
attempt: 1
status: pending
phase: build
created_at: 2026-06-27T16:40:00Z
updated_at: 2026-06-27T16:40:00Z
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 9e5b65d (branch m001-tier-aware-coverage; DRAFT, human-at-merge)
proposal: tasks/orchestrator-log.jsonl#dir-2026-06-27-library-m001-tier-aware-coverage
auditor_verdict: PASS
auditor_ref: tasks/audits/2026-06-27-library-m001-independent-regime-b-audit.md
spec_hash: git:9e5b65d
evidence_ref: tasks/audits/2026-06-27-library-m001-tier-aware-coverage-executes-clean.txt
verdict: pending
verdict_ref: tasks/audits/2026-06-27-library-m001-tier-aware-coverage-grok-cert.md
---

# EMCC.Library — M001 tier-aware concept-coverage (Grok cert-handoff)

**Change:** make P13 `_scripts/check_concept_coverage.py` tier-aware. Optional `tier_filter` config
key + optional roster `tier:` key; a roster entry is skipped when its tier != `tier_filter` (casefold,
after strip). Independent **UNION** with the existing `exclude_entities` skip (neither supersedes).
Default OFF → dashboard output **byte-identical** to pre-M001 (load-bearing: `_scripts/` OVERWRITE-ships
portfolio-wide before any consumer opts in; `_config/` is MERGE-NEW/SKIP so existing consumers never
receive the new key).

**Build (DRAFT):** branch `m001-tier-aware-coverage`, commit `9e5b65d` (code) + `704e6e7` (evidence).
5 files: `check_concept_coverage.py`, `_config/concept_coverage.yaml`, `_canon/roster.yaml` (header
comment), `tests/test_check_concept_coverage.py`, `wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md`
§2.5. Fixtures untouched. Build code stays on the branch — only this handoff + evidence + audit live on
`main`.

**Gate trail:**
- **Delta-Force (Lattice, decorrelated from the Director's pre-gate): PROCEED 5/5.** Caught a HIGH-sev
  silent-drop in the pre-build plan. The plan resolved `str(entry.get("tier","Authoritative"))`, whose
  default fires only on a *missing* key — but Codex's YAML-subset parser renders an empty `tier:` in a
  list item as `[]` (not None) and `tier: null`/`~` as None, so under an active filter empty/null/typo'd
  tiers would be **silently dropped**. Fix keys the resolution on `isinstance(raw_tier, str) and .strip()`
  → None/`[]`/empty/whitespace all funnel to `DEFAULT_TIER` → **included** (fail-OPEN; an advisory
  validator over-reports, never silently hides a gap). Comparison is **casefold** (tier is a
  controlled-vocabulary label, not prose) → kills the case-typo drop class. Director APPROVED the
  correction over his verbatim plan. Transcript:
  `EMCC.DFDU/tasks/delta-force/2026-06-27-library-m001-tier-aware-coverage-lattice-gate.md`.
- **Executes-clean:** 43/43 module suite + 867/867 full Library suite OK (6 skipped). See `evidence_ref`.
  (Full suite needs `python -m unittest discover -t . -s tests` — `-t .` makes `tests/__init__.py` insert
  the source `_scripts` path before the `tests/_lib` test-package shadows the source `_lib`; without it
  you get ~35 spurious ImportErrors — harness artifact, not the diff. Documented in the evidence header.)
- **Auditor (Regime B): PASS — independent, Director-routed (NOT builder-spawned), diff-only, zero build
  context.** All 5 invariants HOLD with file:line evidence; the never-silent-drop confirmed structurally
  (independently traced `[]`/null/missing → all → DEFAULT_TIER=included; no drop path exists). See
  `auditor_ref`. (A builder-spawned pre-cert self-check PASSed separately; logged as prior, NOT the binding
  gate, per framework/22 step 7.)

**Grok /cross-check — please verify the diff independently:**
1. **Default-OFF byte-identical** (test T3 compares actual dashboard bytes: tier-present-but-OFF vs no-tier).
2. **Fail-OPEN** on missing/empty/null/whitespace tier — never silently drops a gap (T8/T10). Trace the
   `[]`-not-None detail in `_scripts/_lib/frontmatter.py:694-700` (empty list-item value → `[]`) and the
   `isinstance(raw_tier, str)` guard in `check_concept_coverage.py`.
3. **UNION with `exclude_entities`** — independent skip predicates (T5).
4. **WARN** on a present-but-unknown filtered tier — advisory, exit code unchanged, entry still filtered (T7).
5. **Scope** — 5 declared files + the evidence txt; fixtures untouched; no drive-by refactor.
- Open `evidence_ref` and confirm a passing run.
- **Disclosed cosmetic (non-blocking, independently corroborated by the Regime-B Auditor):** the
  unknown-tier WARN over-warns when `tier_filter` itself is an unknown value matching an equally-unknown
  entry tier — over-warns, never under-warns, never drops, exit unchanged.

`builder(lattice) != director != certifier(grok)` — role separation clean; `validate_cert_handoff.py`
passes on the IDs and the `directive_ref` resolves in Library's own `tasks/orchestrator-log.jsonl`.
