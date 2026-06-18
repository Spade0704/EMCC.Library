---
title: "Fail-Closed Input Validation"
type: framework
visibility: internal
completion: 60
status: solid
last_updated: 2026-06-18
dependencies: ["01-Architecture/Automation-Scripts", "02-Operations/Bootstrap"]
public_pair: null
blocking_questions: []
topics: [codex_architecture, codex_operations]
related_files: [01-Architecture/Automation-Scripts.md, 02-Operations/Bootstrap.md, 02-Operations/Ingest.md]
tags: [codex_architecture, codex_operations]
canon_sources: ["EMCC.Library commit 2e524a0 (PR #55, S-AUDIT-01 B3+B4)"]
unverified_claims: []
---

# Fail-Closed Input Validation

Two Codex entry points accept **agent-populated or operator-supplied paths/names**
and turn them into filesystem operations: `route_inbox.py` (the Inbox-Sort helper)
and `bootstrap.py` (new-wiki scaffolder). Both now enforce a fail-closed
input-validation contract so an arbitrary path or name can never escape the project
tree or be coerced into traversal. The guards are **additive and fail-closed**:
valid inputs behave exactly as before; invalid inputs are rejected (or skipped and
flagged) rather than executed.

Origin: the S-AUDIT-01 security audit, findings **B3** (route_inbox) and **B4**
(bootstrap). Both guards landed together in PR #55.

## Why this is load-bearing

`route_inbox.py` is a two-phase Librarian helper: a script scans `0-Inbox/` and emits
a manifest, the **Librarian fills in destinations**, then the script executes the moves.
The destination — and, after this change, the source — are agent-populated arbitrary
strings. Without confinement, a populated `destination` of `../../etc/foo` or an
absolute path outside the wiki would move files anywhere the process can write.
`bootstrap.py` takes a `projectname` straight from the CLI and uses it to build paths;
an unsanitized name with separators or `..` tokens would scatter scaffold files outside
the intended tree.

The contract: **confine, don't trust.** Resolve the path; if it falls outside the
project root, refuse it.

## B3 — `route_inbox.execute_manifest()` tree confinement

`execute_manifest()` confines every move to the project tree. Both the agent-populated
`destination` and the `source_abs` are resolved to absolute paths and must resolve
**inside the scan root**, or the entry is skipped and flagged to stderr — the run is
**never aborted** (one bad manifest entry does not kill an otherwise-good batch).

- New `root` argument defaults to the manifest's parent directory (the scan phase emits
  the manifest at `<root>/route_candidates.json`), so **existing callers are unaffected** —
  the default reconstructs the same root the scan used.
- Skip-and-flag, not halt: a confinement violation produces a stderr warning and the entry
  is left in place; valid entries in the same manifest still execute. This matches the
  Librarian "halt-loud on tool failure, but isolate one bad item" discipline.

## B4 — `bootstrap()` projectname validation

`bootstrap()` enforces the help-text "Filesystem-safe characters only" contract that was
previously documentation-only. `projectname` is validated **at the top, before any
filesystem work**:

- Must match `^[A-Za-z0-9._-]+$` (letters, digits, dot, underscore, hyphen).
- Path separators (`/`, `\`) and the `.` / `..` traversal tokens are rejected explicitly.
- On any violation, bootstrap exits **non-zero with a clear message** before creating a
  single file — fail-closed at the door, not mid-scaffold.

## Discipline (for future Codex entry points)

Any new script that turns an externally-supplied string into a path or filename inherits
this contract:

- **Resolve, then confine.** Compare the resolved absolute path against the project root;
  refuse anything outside it.
- **Validate names against an allowlist** (`^[A-Za-z0-9._-]+$`), not a denylist.
- **Reject traversal tokens** (`..`) and path separators in name fields explicitly.
- **Fail-closed:** refuse before any side effect. For batch operations, skip-and-flag the
  bad entry rather than aborting the whole run.

## Related

- [[Automation-Scripts]] — `route_inbox.py` (Inbox-Sort helper) and `bootstrap.py` in the script inventory.
- [[Bootstrap]] — the one-time wiki-creation operation `bootstrap.py` drives.
- [[Ingest]] — the wiki-internal `_inbox/` source-integration flow (distinct from the project-root `0-Inbox/` that `route_inbox.py` sorts).
