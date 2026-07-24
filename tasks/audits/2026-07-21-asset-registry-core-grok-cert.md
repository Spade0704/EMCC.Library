---
date: 2026-07-24
slug: 2026-07-21-asset-registry-core
target_repo: D:/Projects/Enterprise Matrix/EMCC.Library
range: c87f323fefb3ad89e0c7ff1ec9f266fe0ed07cfa
certifier: Grok (xAI) — EMCC External Certifier
verdict: FAILED(executes-clean — independent suite disagrees with evidence_ref on Windows certifier host)
chat: FAILED(executes-clean host re-run: 20 errors + 3 fails in test_asset_registry; OSError EBADF on os.fsync in _move_asset)
execute: deferred (CISO gate)
vision: n/a
---

# Grok External Cert — asset-registry v1.4 CORE

## 1. Disclosure

Cold read of handoff `0-Inbox/grok-audit/2026-07-21-asset-registry-core.md`, commit
`c87f323fefb3ad89e0c7ff1ec9f266fe0ed07cfa` (object present; PR #68 squash-merged as `687c5f9` on
main — core blobs byte-identical to `c87f323`), evidence file, auditor note,
`CODEX_BUILD_SPEC_v1_4.md` §9, and DFDU Delta-Force gate
`EMCC.DFDU/tasks/delta-force/2026-07-21-library-asset-registry-core.md`.

Producer `lattice` / builder `lattice:EMCC.Library/registry-builder-01` (commit author Claude)
≠ certifier Grok (xAI). This session did not author any part of the range. No source patches;
deliverables are this verdict file + handoff status flip only.

**Supersedes** earlier same-day `verdict: PASS` commit `3b87e43`, which accepted Linux
`evidence_ref` without an independent suite re-run on the certifier host. Chat floor requires a
you-ran signal (`references/ciso-deferred-chat-floor.md`); that re-run RED'd.

## 2. Chat — scope, mechanical floor, proposal-vs-job, substance

| Check | Result |
|-------|--------|
| `validate_cert_handoff.py` | **PASS** (exit 0) |
| `evidence_ref` readable | **PASS** — file present; lattice capture claims `Ran 917 tests … OK (skipped=7)` under `/tmp/…` (Linux) |
| Independent suite re-run (certifier host Windows) | **FAIL** — `Ran 917 tests` → **FAILED (failures=3, errors=20, skipped=6)**; all 23 RED cases in `tests.test_asset_registry` |
| Targeted `python -m unittest tests.test_asset_registry` | **FAIL** — 20 ERROR + 3 FAIL / 43; root cause below |
| Non-registry residual | **PASS** — 874 tests OK (skipped=6) when asset_registry module excluded |
| Range object / scope | **PASS** — 6 files on `c87f323`; HEAD blobs for `asset_registry.py` / `.yaml` / `test_asset_registry.py` **identical** to range |
| Proposal / gate alignment (static) | **PASS** — §9.1–§9.4 CORE + CLI + remote_store stub; retro/reconcile deferred per DFDU gate |
| Network imports (AST) | **PASS** — stdlib + `_lib.frontmatter` only; no requests/urllib/httpx/aiohttp/socket |
| sync_from_kit exclusion | **PASS** — `SYNC_EXCLUDED_SCRIPTS/CONFIG` name the module files; tests green |
| Frontend / Vision | n/a |

**Root cause (independent porcelain):**

```text
File ".../asset_registry.py", line 814, in _move_asset
    os.fsync(handle.fileno())
OSError: [Errno 9] Bad file descriptor
```

`_move_asset` (lines 808–815) does `tempfile.mkstemp` → `os.close(fd)` → `shutil.copyfile` →
`open(tmp_name, "rb")` → `os.fsync(handle.fileno())`. On this Windows certifier host that
`fsync` raises **EBADF**, so every path that performs a real move ERROR's. Cascade:

- 20 ERRORs on filing-loop / schema / crash-resume / lineage / lock-release tests that call `file_inbox` → `_move_asset`
- 3 FAILs on CLI verbs expecting success / zone counts after a successful file

Static §9 substance is largely present (allocator O_EXCL + stale surface, REQUIRED_EXPLICIT,
zone predicate, opaque git index, remote_store stub, sync exclusion) — but **executes-clean does
not hold on the external certifier's environment**, and disagrees with `evidence_ref`.

**Auditor W1/W2** (representability after burn/move; missing newline-refusal regression) noted;
not the FAIL gate. FAIL gate is independent suite disagreement.

## 3. Execute

**deferred (CISO gate)** — handoff has no `execute_approved: true`. Full cross-vendor rebuild not
separately authorized.

Chat-floor targeted re-run (above) is the independent signal and is already **RED**. Even if
Execute were approved, agreement with Linux-only `evidence_ref` would fail on this host until
`_move_asset` fsync is portable (certifier does **not** patch source).

## 4. Vision

n/a — library automation; no UI/comp in range.

## 5. Verdict

**FAILED(executes-clean — independent suite disagrees with evidence_ref on Windows certifier host)**

- Chat: **FAILED** — you-ran `unittest` on certifier host RED (20E+3F in module under test;
  EBADF at `asset_registry.py:814`).
- Execute: **deferred (CISO gate)**.
- Vision: **n/a**.
- Lattice `evidence_ref` remains a Linux OK capture; it is **not** corroborated here.
- Certifier does not author a fix. Builder/Director: make move durability Windows-safe (or
  document Linux-only + provide a certifier-runnable evidence path), re-queue handoff attempt N+1.

Director does **not** get dual-PASS on this leg. Human merge of product code already landed via
#68; this record blocks treating the Grok leg as certified-clean until re-attempt.
