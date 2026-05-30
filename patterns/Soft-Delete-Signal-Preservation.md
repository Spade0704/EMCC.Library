---
title: "Pattern — Soft Delete & Signal Preservation"
type: reference
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-30
dependencies: []
public_pair: null
blocking_questions: []
topics: []
related_files: []
tags: []
canon_sources: []
unverified_claims: []
---

# Soft Delete & Signal Preservation

## Problem

Hard deletes are unrecoverable and destroy information twice over: the user loses an item they
might want back, and the product loses the **signal** that the user chose to remove it (often a
useful behavioral input). But "keep everything forever" violates user expectation and privacy law.

## Pattern

Two complementary moves:

1. **Park, don't delete.** Mark the record `status: deleted` with a `deletedAt` timestamp and
   hide it from default views, instead of removing the row. Restoration is a flag flip.
2. **Preserve the signal, not the content.** On deletion, optionally emit a small, de-identified
   record ("user removed an item of type X in context Y") to a separate analytics/insight
   collection — never the raw content. This keeps the learning signal while letting the actual
   content be purged on schedule or on a hard-delete request.

## Implementation guidance

1. **Cascade explicitly.** Deleting a parent soft-deletes its children in a defined order
   (e.g. project → its tasks → its ideas). Make the order a documented decision.
2. **Two-phase account deletion.** Purge user data first, then the auth identity; handle the
   re-auth-timeout edge case so a slow purge can't strand a half-deleted account.
3. **Retention job.** A scheduled task hard-purges `status: deleted` rows older than the
   retention window — soft delete is a grace period, not "forever."
4. **Privacy gate on the signal.** Anything written to the insight collection passes a
   no-PII / no-identifiers / generalizable check (see AI-Memory-And-Insight-Extraction).
5. **Honor erasure requests** by purging both the parked content *and* any derived signal that
   could re-identify, with an audit-trail entry recording that you did.

## Data shape (generalized)

```jsonc
// parked item
{ "id": "t_123", "status": "deleted", "deletedAt": "2026-05-30T10:00:00Z", "...": "content" }

// preserved signal (separate collection; de-identified)
{ "kind": "deletion", "itemType": "task", "context": "errand", "at": "2026-05-30T10:00:00Z" }
```

## When to use / avoid

- **Use** whenever recoverability matters or deletion behavior is a useful product signal.
- **Avoid** retaining the *signal* without a privacy gate, and avoid soft delete with **no**
  retention job — that's just an unbounded, un-audited data store wearing a "deleted" label.
