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

# Grok External Cert — asset-registry fsync-fix (Windows EBADF)

## 1. Disclosure

Cold read of handoff `0-Inbox/grok-audit/2026-07-24-fsync-fix.md` (attempt 2, status:pending on main)
plus product range at `5badaf0` via `git show` / detached worktree. Producer `lattice` /
builder `lattice:EMCC.Library/registry-builder-01` != certifier Grok (xAI). This session did not
author any product of the claimed range. Deliverables only: this verdict file + handoff status flip.

**attempt 2 context:** attempt-1 Grok close was `FAILED(validator: directive_ref unresolved)` while
the product/Auditor already sat at `5badaf0`. Director registered
`kind:directive_assignment` id `dir-20260724-library-asset-registry-fsync-fix` on main; pre-gate
now resolves. This file overwrites the attempt-1 pre-gate refuse path with a full Windows dual-PASS
close.

PR #70 tip at cert time was `99115be` (docs: prior handoff drop + attempt-1 FAILED cert only). Product
fix + Auditor + Windows evidence are at handoff range head `5badaf0` (commits `4763b0a` fix +
`5badaf0` auditor). Cert range bound to handoff `base..range` / `7e7e53c..5badaf0`.

## 2. Chat

| Check | Result |
|-------|--------|
| `poll_select.py` | Selected `EMCC.Library/0-Inbox/grok-audit/2026-07-24-fsync-fix.md` |
| `validate_cert_handoff.py` | **PASS** (exit 0) |
| `directive_ref` | Resolves: `kind:directive_assignment` + `id:dir-20260724-library-asset-registry-fsync-fix` in `tasks/orchestrator-log.jsonl` (main) |
| `evidence_ref` | Present + readable at head: `tasks/evidence/2026-07-24-fsync-fix-windows-tests.txt` (Windows host; targeted 43 OK; full 917 OK skipped=6) |
| `auditor_ref` | Regime B PASS at head; independent Windows re-run; scope + crash-safe ordering affirmed |
| Scope (name-only) | `Biz.Automation/wikisys.library/_scripts/asset_registry.py` + auditor + evidence only (product); confining docs on PR tip |
| Proposal vs job | Matches CODEX_BUILD_SPEC v1.4 §9.3 crash-safe filing / `_move_asset`; unblocks Windows EBADF from prior FAILED CORE `7e7e53c` |

### Diff substance (cold)

Prior `_move_asset`: `os.close(fd)` then `shutil.copyfile` then reopen temp `"rb"` + `os.fsync` —
writable-fd requirement violated on Windows → `OSError [Errno 9] EBADF`.

Fix at `4763b0a`: keep mkstemp fd, `os.fdopen(fd, "wb")` + `shutil.copyfileobj` + `flush` +
`os.fsync(handle.fileno())` then `os.replace`. Mirrors existing `atomic_write_text` durability
pattern in the same module. Temp→fsync→replace order preserved. Except-path `unlink` unchanged.
Stdlib-only; no new deps.

INFO note from Auditor (non-blocking): copyfileobj may forfeit platform fast-copy — accepted trade
for a writable fsync handle.

## 3. Execute (mandatory Windows)

Host: Windows 11 (win32), Python 3.13.14, MSC v.1944 64-bit.
Pinned worktree: `D:/Projects/Enterprise Matrix/EMCC.Library-wt-fsync-fix-cert` @
`5badaf01b3e2df836c28ac81a96b07f30c070814` (detached; `git rev-parse HEAD` matched handoff range).

| Command | Result |
|---------|--------|
| `python -m unittest tests.test_asset_registry -v` | **Ran 43 in 1.334s — OK** |
| `python -m unittest discover -s tests -t .` | **Ran 917 in 18.851s — OK (skipped=6)** |

Agreement vs producer `evidence_ref`: same targeted 43 OK and full 917 OK skipped=6 on Windows.
No Linux-only acceptance. EBADF class of failures gone under independent Windows re-run.

## 4. Vision

n/a — no UI / comps; library script + unittest surface only.

## 5. Verdict

**PASS**

Chat mechanical floor clean; directive resolves; evidence_ref is a real Windows transcript;
independent Windows Execute agrees with producer counts; scope confined; §9.3 ordering preserved
on a writable fd. Two-model agreement with Auditor Regime-B PASS is concurrence, not proof of
merge readiness alone — Director closes dual-PASS and human merges PR #70.

Certifier does not merge.
