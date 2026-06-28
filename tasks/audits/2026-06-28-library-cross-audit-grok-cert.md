---
date: 2026-06-28
slug: 2026-06-28-library-cross-audit
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: n/a (input_kind: findings_json — no git range)
certifier: Grok (xAI) — EMCC External Certifier
verdict: PASS
chat: PASS
execute: PASS
vision: n/a
---

# Grok External Cert — EMCC.Library findings.json cross-audit (5/7)

## 1. Disclosure

Cold read of `tasks/audits/2026-06-28-library-audit.json` (EMCC hub) and every cited
file:line opened independently in `EMCC.Library` (producer `claude:opus` ≠ certifier `grok`).
This is `input_kind: findings_json` — `/repo-cross-audit`, not `/cross-check`. No source edits;
deliverables are per-finding verdicts JSON + this cert record (reconcile is Claude-side).

## 2. Chat — scope, mechanical floor, substance

| Check | Result |
|-------|--------|
| `validate_cert_handoff.py` on handoff | PASS (exit 0, plan phase) |
| `findings_ref` readable | PASS — 10 gated findings + `not_checked` disclosure |
| F2 security rail — LIB-08 reviewed first | PASS — corroborated (healthy Info finding) |
| Tripwire: Confirmed/Certified status | CLEAN (all `claude-only`) |
| Production script grep (shell/eval/pickle) | CLEAN — no matches in `*.py` |

**Per-finding cold reads (security first):**

- **LIB-08 (corroborated):** Path confinement sound — `_validate_projectname` + `_refuse_outside_cwd` in bootstrap; `_within_root` in route_inbox execute path. Subprocess calls use list-form argv; pure stdlib.
- **LIB-01 (corroborated):** Eager `WIKI_ROOT = find_wiki_root()` at import (71); RuntimeError when no marker (57-62); config_loader imports at 39.
- **LIB-02 (corroborated):** `read_bytes()[:4096]` (55) loads full file for 4 KB hash.
- **LIB-03 (corroborated):** `shutil.move` (138) without overwrite guard; confinement stops escape not clobber.
- **LIB-04 (corroborated):** Empty-key semantics diverge: None (372) vs [] (707); docstring documents silent-loss class.
- **LIB-05 (corroborated):** `int('--5')` ValueError reproduced — guard at 472 insufficient.
- **LIB-06 (corroborated):** Non-file inbox entries skipped silently (51).
- **LIB-07 (corroborated):** No Win32 reserved-name rejection in `_validate_projectname`.
- **LIB-09 (corroborated):** CI single Python 3.11 pin; matrix gap noted.
- **LIB-10 (corroborated):** doc_lint fail-closed unreadable-page handling (318-336).

Verdicts written to `tasks/audits/2026-06-28-library-grok-verdicts.json`.

## 3. Execute

`python -m unittest discover -s tests -t .` — **867 tests OK** (6 skipped) in 21.5s.
Independent `_parse_value('--5')` reproduces LIB-05 ValueError. Agreement with PR1 static audit posture.

## 4. Vision

n/a — not a frontend build cert.

## 5. Verdict

**PASS** — all 10 Claude findings corroborated; no disputes; no grok-added findings this round.
Concurrence ≠ proof; operator holds stop until Claude-side `validate.py --reconcile`.