---
date: 2026-07-24
slug: 2026-07-24-fsync-fix
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: 7e7e53cdfddd4ecf1252a689a0b72f58c464b4e7..5badaf01b3e2df836c28ac81a96b07f30c070814
certifier: Grok (xAI) — EMCC External Certifier
verdict: PASS
chat: PASS
execute: PASS
vision: n/a
---

# Grok cert — 2026-07-24-fsync-fix (Windows `_move_asset` EBADF)

## 1. Disclosure

Cold external cert. Certifier did not author the range under review. Producer =
`lattice` / builder `lattice:EMCC.Library/registry-builder-01`. Range lives on
PR #70 (`fix/asset-registry-fsync-windows-ebadf`); coordination artifacts
(handoff + directive log) on `main`. Attempt 1 was pre-gate REFUSE
(`directive_ref` unresolved); attempt 2 re-drops after Director registered
`dir-20260724-library-asset-registry-fsync-fix` in `tasks/orchestrator-log.jsonl`.

## 2. Chat

### Scope
- `Biz.Automation/wikisys.library/_scripts/asset_registry.py` — `_move_asset` only
  (11 lines net on the fix commit `4763b0a`)
- Plus Auditor verdict + Windows evidence on `5badaf0`
- 3 files total in range; no unrelated edits

### Mechanical floor
| Check | Result |
|-------|--------|
| `validate_poll_handoff.py` / validator | **PASS** (directive_ref resolves on main) |
| `evidence_ref` present + passing | **PASS** — `tasks/evidence/2026-07-24-fsync-fix-windows-tests.txt` (43 OK + 917 OK skipped=6) |
| `auditor_verdict` / `auditor_ref` | **PASS** — Regime B Auditor PASS, independent Windows re-run |
| Diff vs proposal (§9.3 crash-safe filing / `_move_asset`) | **PASS** — temp→fsync→replace preserved; fsync now on writable fd |
| Stdlib-only / no new deps | **PASS** |

### Proposal-vs-job
Handoff claims: fix Windows `os.fsync` EBADF by copying through the owned writable
mkstemp handle (`os.fdopen(fd,"wb")` + `copyfileobj` + `flush` + `fsync` +
`os.replace`). Diff matches claim byte-for-byte. Pattern mirrors existing
`atomic_write_text` in the same module. Prior false-PASS lesson (Linux-only
evidence) is addressed by Windows producer evidence + HARD REQUIREMENT for
certifier Windows re-run.

### Substance
- Removed `os.close(fd)` then reopen-as-`"rb"` + fsync path (EBADF on Windows).
- `os.fdopen` owns the mkstemp fd; single close via context manager — no double-close.
- Crash-safe ordering unchanged: write temp → fsync → `os.replace`.
- Except-path cleanup not regressively touched in this diff hunk.
- INFO (Auditor, non-blocking): forfeits platform fast-copy; unavoidable for
  writable-handle fsync. Not a defect.

## 3. Execute

Independent re-run on certifier host (Windows, Python 3.13.14), detached worktree
at `5badaf0` (range head):

```
python -m unittest tests.test_asset_registry
→ Ran 43 tests in 1.477s  OK

python -m unittest discover -s tests -t .
→ Ran 917 tests in 26.007s  OK (skipped=6)
```

Agreement with `evidence_ref`: same counts (43 / 917 skipped=6), both OK.
EBADF regression gone. CISO gate: Director HARD REQUIREMENT explicitly requires
Windows executes-clean on this cert — Execute in scope and satisfied.

## 4. Vision

n/a — library/script change; no frontend / no committed UI comp.

## 5. Verdict

**PASS**

Chat mechanical floor clean + Execute agreement on Windows + Vision n/a.
Director closes on DUAL PASS (Auditor PASS + this Grok PASS). Certifier does not merge.
PR: https://github.com/Spade0704/EMCC.Library/pull/70
