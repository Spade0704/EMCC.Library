---
title: "Pattern — Offline-First Sync Queue"
type: reference
visibility: internal
completion: 42
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

# Offline-First Sync Queue

## Problem

A cloud-backed app that reads/writes only when online stalls on poor connectivity and loses
writes made while disconnected. Users expect the app to keep working and reconcile later.

## Pattern

- **Reads** come from a local cache first (instant), with the remote stream merged in when it
  arrives. The cache is the source of truth for the UI; the remote is the source of truth for
  the data.
- **Writes** apply optimistically to the cache and are appended to a **durable queue**. A
  connectivity listener **flushes the queue in FIFO order** when the device comes back online,
  and on next launch if ops were left from a prior session.

```
UI --read--> local cache <--merge-- remote stream
UI --write-> local cache --enqueue--> op queue --(online)--> remote
```

## Implementation guidance

1. **One cache box per collection**; a small wrapper exposes `get/put/replaceAll/delete` plus a
   change notification so providers can rebuild.
2. **Queue ops as serializable records** (`{op, collection, id, payload}`) in the same durable
   store, so a crash or cold start doesn't lose them.
3. **Flush triggers:** connectivity `none -> online` transition, *and* a startup check when
   `pendingOpsCount > 0`. Guard with an `isFlushing` flag to prevent concurrent flushes.
4. **Hardening the lifting consumer still owes** (the generalized "do it right" list):
   - **Bounded retry with backoff** instead of indefinite immediate retry on each reconnect.
   - **Dead-letter** an op after K failed attempts so one poison op can't wedge the queue.
   - **Idempotency keys** so a replayed op can't double-apply after an ambiguous failure.
   - **Conflict policy** (last-write-wins vs. merge) made explicit per collection.

## Reference shape (generalized Dart)

```dart
class SyncService {
  bool _isOnline = true, _isFlushing = false;

  Future<void> init() async {
    _isOnline = await _checkConnectivity();
    _connectivity.onChanged.listen((online) {
      final reconnected = online && !_isOnline;
      _isOnline = online;
      if (reconnected) flushPendingOps();
    });
    if (_isOnline && _cache.pendingOpsCount > 0) flushPendingOps();
  }

  void enqueue(SyncOp op) { _cache.appendOp(op); if (_isOnline) flushPendingOps(); }

  Future<void> flushPendingOps() async {
    if (_isFlushing) return;
    _isFlushing = true;
    try {
      for (final op in _cache.pendingOps) {       // FIFO
        await _applyRemote(op);                    // TODO: backoff + dead-letter + idempotency
        _cache.removeOp(op);
      }
    } finally { _isFlushing = false; }
  }
}
```

## When to use / avoid

- **Use** for mobile/field apps where connectivity is intermittent and writes must survive it.
- **Avoid** the full queue when the backend SDK already provides robust offline persistence that
  meets your conflict and durability needs — don't reimplement it half-way.
