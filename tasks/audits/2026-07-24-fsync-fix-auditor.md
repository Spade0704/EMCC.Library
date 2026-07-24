---
date: 2026-07-24
slug: 2026-07-24-fsync-fix
target: Biz.Automation/wikisys.library/_scripts/asset_registry.py (_move_asset)
branch: fix/asset-registry-fsync-windows-ebadf
commit: 4763b0a
regime: B (independent verification of builder's change)
builder: lattice:EMCC.Library (Librarian session, Claude)
auditor: Lattice Auditor (independent subagent; builder != auditor)
verdict: PASS
---

# Auditor verdict — asset-registry fsync-fix (Windows EBADF)

## Scope
Fix for `os.fsync` EBADF in `_move_asset` that RED'd the asset-registry CORE on
Windows (Grok cert FAILED 7e7e53c, superseding false-PASS 3b87e43). Change: copy
through the writable temp handle we own (`os.fdopen(fd,"wb")` + `shutil.copyfileobj`),
flush + fsync THAT handle before `os.replace` — mirrors `atomic_write_text`.

## Independent test re-run (Windows 11, Python 3.13.14, HEAD 4763b0a)
- `python -m unittest tests.test_asset_registry` → **Ran 43 → OK**
- `python -m unittest discover -s tests -t .` → **Ran 917 → OK (skipped=6)**

Prior RED (20 errors + 3 fails) gone. Numbers match the committed evidence file
(`tasks/evidence/2026-07-24-fsync-fix-windows-tests.txt`).

## Correctness
- fsync now on a **writable** fd; crash-safe temp→fsync→replace ordering (§9.3) preserved.
- `os.fdopen` owns the mkstemp fd — closed exactly once by its context manager; the
  removed `os.close(fd)` was correct to drop. No double-close, no fd leak on the normal path.
- Except-cleanup (`os.unlink(tmp_name)` guarded by `OSError`) unchanged and still correct.
- `copyfileobj` is chunked — memory-safe for large files; no regression vs `copyfile`.

## Findings
- INFO (non-blocking): manual `copyfileobj` forfeits platform fast-copy
  (`os.sendfile`/`CopyFileEx`) that `shutil.copyfile` may use. Unavoidable — fsync
  requires a writable handle. File metadata behavior unchanged. Not a defect.

## Scope discipline
Clean. Diff confined to the 11-line fsync fix + evidence file (2 files). Stdlib-only,
no new deps, no unrelated edits, no spec violation.

## Verdict
**PASS.** Library-side gate satisfied (executes-clean on Windows + independent Auditor).
Remaining for DUAL PASS: external Grok cross-check on a real **Windows** re-run
(no Linux-only evidence — the prior false-PASS lesson holds).
