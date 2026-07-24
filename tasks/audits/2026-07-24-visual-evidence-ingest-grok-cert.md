---
date: 2026-07-24
slug: 2026-07-24-visual-evidence-ingest
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 25eb936a887ea133bd35fe973a135756a36bfecb..616c9cb
pr: https://github.com/Spade0704/EMCC.Library/pull/72
certifier: Grok (xAI) — EMCC External Certifier
verdict: PASS
chat: PASS
execute: PASS
vision: n/a
---

# Grok External Cert — Lane-6 B3+B4+B5 visual-evidence ingest (§9.9 + §9.10)

## 1. Disclosure

Cold read of handoff
`0-Inbox/grok-audit/2026-07-24-visual-evidence-ingest.md` (status:pending, folded B3+B4+B5)
plus product range `25eb936..616c9cb` on branch `feat/visual-evidence-ingest` (PR #72) via
`git show` / detached worktree. Producer `lattice` / builder
`lattice:EMCC.Library/registry-builder-01` != certifier Grok (xAI). This session did not
author any product of the claimed range. Deliverables only: this verdict file + handoff status flip.

Director fold (2026-07-24T06:41:16Z): one Grok cert over B3+B4+B5 because B3+B4 had not been
picked up. Stack base `25eb936` includes #70 (fsync) + #71 (schema v0.1) so the suite is green
relative to a plain-main base that is still RED from unmerged EBADF.

## 2. Chat

| Check | Result |
|-------|--------|
| `poll_select.py` | Selected `EMCC.Library/0-Inbox/grok-audit/2026-07-24-visual-evidence-ingest.md` |
| `validate_poll_handoff.py` / `validate_cert_handoff.py` | **PASS** (exit 0) |
| `evidence_ref` | Present at range head `616c9cb` (not on main yet — product rides PR branch): B3+B4 Windows transcript + B5 Windows transcript; both claim Windows 11 / Python 3.13.14; B5 final counts 39 + 956 OK skipped=6 |
| `auditor_ref` | Regime B **PASS** on B3+B4 (2 info findings raised then closed in hardening) AND B5 (commit-state confirmed; 2 non-blocking INFO) |
| Scope (name-only) | 7 files: `asset_registry.yaml` (classes), `validate_visual_evidence.py` (new), `sync_from_kit.py` (exclude), two evidence files, `tests/test_validate_visual_evidence.py`, `CODEX_BUILD_SPEC_v1_4.md` (§9.9/§9.10) |
| Proposal vs job | Matches handoff + §9.9/§9.10: game classes; stdlib schema walker + R1/R2 + checks 1/3; recursive cert_class reject; path sandbox; `sidecar_to_recipe` scalar-only; B5 base-identity binding + style-bible resolve; sync-excluded |

### Diff substance (cold)

- **B3**: `asset_classes` adds `sprite` / `base-identity` / `pose-anim-frame` / `audio-cue` (§9.8).
- **B4**: new `validate_visual_evidence.py` — stdlib draft-07 subset walker (type/required/enum/properties/items; bool excluded from integer/number); R1 XOR fresh-gen; R2 signoff name; recursive `_contains_key` for `cert_class`; check-1 sha256 re-hash; check-3 path-binding refuses absolute/`..` escape; `sidecar_to_recipe` folds into existing `recipe:`/`derived_from` with **no RECORD_FIELDS change**; sync exclusion mirrors `asset_registry.py`.
- **B5**: `check_base_identity_binding` (resolve ast_id both zones, class==base-identity, re-hash base bytes); `check_style_bible` path resolve; optional `--wiki-root` / `--bible-root`; §9.10 prose matches impl. Perceptual distance / palette-subset correctly left to Anvil pixel floor.
- **Tests**: 39 real non-vacuous cases covering schema, rules, nesting, path sandbox, ingest mapping, CLI, B5 failure modes.
- Floor scripts `nonbuild_check` / `doc_drift_check` / `reconcile_backlog` / `eval_runner`: **absent** in this consumer (probed, skip-with-note).

## 3. Execute (mandatory Windows)

Host: Windows 11 (win32), Python 3.13.14.
Detached worktree: `D:/Projects/Enterprise Matrix/_worktrees/emcc-library-cert-visual-evidence` @
`616c9cb1f9cf818ee2d9c484857d24579076b5f0` (handoff range head).

| Command | Result |
|---------|--------|
| `python -m unittest tests.test_validate_visual_evidence` | **Ran 39 in 0.060s — OK** |
| `python -m unittest discover -s tests -t .` | **Ran 956 in 23.570s — OK (skipped=6)** |

Porcelain before/after full suite: empty in the cert worktree (tests use temp dirs only).

Agreement vs producer `evidence_ref` at `616c9cb`:
- targeted 39 OK (producer 0.046s / certifier 0.060s)
- full 956 OK skipped=6 (producer 17.417s / certifier 23.570s)
Same counts on Windows; no Linux-only acceptance. Meets Director hard requirement that
executes-clean runs on the Windows certifier host.

## 4. Vision

n/a — library validator + unittest surface; no UI comps / frontend screenshots in range.

## 5. Verdict

**PASS**

Chat mechanical floor clean; evidence_ref is a real Windows transcript at range head;
independent Windows Execute agrees with producer counts (39 + 956); scope confined to
registry-side visual-evidence ingest; §9.9/§9.10 substance real-not-stub; Auditor dual-PASS
paired with this external half. Certifier does not merge — Director closes on DUAL PASS after
merge order #70 → #71 → #72.
