---
date: 2026-06-27
slug: 2026-06-27-library-m001-tier-aware-coverage
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 9e5b65d (branch m001-tier-aware-coverage; DRAFT, human-at-merge)
certifier: Grok (xAI) — EMCC External Certifier
verdict: PASS
chat: PASS
execute: deferred (CISO gate)
vision: n/a
producer_model: Claude Opus 4.8 (Lattice peer)
cross_check_model: Grok
same_model_fallback: false
shared_fs: true
---

# Grok cert — EMCC.Library M001 tier-aware concept-coverage

## 1. Disclosure

Cold read by Grok (xAI), EMCC External Certifier. This session did not author or commit any part of
range `9e5b65d` on branch `m001-tier-aware-coverage`. Producer was Lattice (`builder_id: lattice`);
certifier is decorrelated by position, model, and vendor. `shared_fs: true` — independence is
position + model, not filesystem isolation.

Handoff: `0-Inbox/grok-audit/2026-06-27-library-m001-tier-aware-coverage.md`
(`validate_cert_handoff.py` → PASS). `directive_ref` resolves on `origin/main` orchestrator-log
(`dir-2026-06-27-library-m001-tier-aware-coverage`).

## 2. Chat — mechanical floor + substance

### Scope (cold)

5 code/doc files at `9e5b65d` + evidence txt at `704e6e7` (on branch, not merged):

- `Biz.Automation/wikisys.library/_scripts/check_concept_coverage.py` — tier_filter gating
- `Biz.Automation/wikisys.library/_config/concept_coverage.yaml` — config header + commented example
- `Biz.Automation/wikisys.library/_canon/roster.yaml` — header comment only (no entity data)
- `tests/test_check_concept_coverage.py` — TierFilterTests T1–T10
- `wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md` — §2.5 schema rows

Fixtures untouched. No drive-by refactor.

### Mechanical floor (certifier re-run)

| Command | Result |
|---|---|
| `python validate_cert_handoff.py <handoff>` | PASS |
| `python -m unittest tests.test_check_concept_coverage` | Ran 43 tests, OK |
| `python -m unittest discover -t . -s tests -p 'test_*.py'` | Ran 867 tests, OK (skipped=6) |

Evidence_ref (`tasks/audits/2026-06-27-library-m001-tier-aware-coverage-executes-clean.txt`)
reports identical counts (43/43 module, 867/867 full). Certifier independently reproduced both.

EMCC.Library has no `nonbuild_check.py` / `doc_drift_check.py` portfolio scripts; tests are the
hard gate for this repo. `eval-check`: INERT (no baseline pinned in Library).

### Proposal-vs-job

Directive (`dir-2026-06-27-library-m001-tier-aware-coverage`) instructs: tier_filter config flag
(default OFF, byte-identical) + optional roster `tier:` key + UNION skip predicate + spec §2.5.
Handoff and diff deliver all four. No undercoverage.

### Substance (invariants independently traced)

1. **Default-OFF byte-identical** — `DEFAULTS["tier_filter"] = None` (line 102); skip block gated
   `if tier_filter is not None:` (line 174). Config loader accepts only non-empty string (lines
   300–306). Test T3 asserts byte-identical dashboard.
2. **Fail-OPEN never-silent-drop** — `isinstance(raw_tier, str) and raw_tier.strip()` guard (lines
   180–185), NOT `.get("tier", default)`. Empty `tier:` in list item → `[]` per
   `frontmatter.py:694–700`. Null/`~` → `None` via `_parse_value`. All funnel to `DEFAULT_TIER` →
   included. Tests T4, T8, T10.
3. **UNION with exclude_entities** — separate `continue` predicates (lines 166–167 vs 174–195).
   Test T5.
4. **Casefold compare** — both sides casefolded (line 194). Test T9.
5. **Unknown-tier WARN** — advisory stderr before skip (lines 186–193); exit unchanged. Tests T7,
   T7b.

Non-blocking cosmetic (handoff-disclosed, corroborated): unknown-tier WARN over-warns when
`tier_filter` itself is an unknown value matching an entry tier — over-warns, never drops.

Auditor Regime-B verdict (`auditor_ref`) independently corroborates all five invariants; certifier
did not defer to it — traced code path independently.

## 3. Execute

No `execute_approved: true` on handoff; cross-vendor Execute deferred per CISO interim gate.

Certifier independently re-ran both suites on branch `m001-tier-aware-coverage` (commit includes
`9e5b65d`) and results match `evidence_ref` exactly. Execute token recorded as deferred (CISO
gate); agreement noted for operator visibility but does not substitute for CISO clearance.

## 4. Vision

n/a — backend Python stdlib module; no frontend/UI/comp.

## 5. Verdict

**PASS** — Chat mechanical floor clean, all five M001 invariants hold with file:line evidence,
tests reproduce builder evidence counts, scope matches directive, no undercoverage. Execute deferred
(CISO gate); Vision n/a.