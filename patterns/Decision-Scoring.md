---
title: "Pattern — Weighted Decision Scoring"
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

# Weighted Decision Scoring

## Problem

A work queue (tasks, leads, tickets) sorted by a single field — usually due date or a manual
priority flag — surfaces the wrong item first. Urgency, importance, effort, recent momentum,
and downstream-unblocking value all matter, and their relative weight differs per user and per
domain.

## Pattern

Compute a single scalar **score** per item from a small set of normalized signals (each in
`[0,1]`), combined by a weight vector that sums to 1. Sort descending by score. Expose the
weights as configuration so they can be tuned — and, optionally, learned per user from manual
override behavior over a trailing window.

```
score = Σ (wᵢ · signalᵢ),  where Σ wᵢ = 1
```

### Reference weighting (from the lifting consumer)

| Signal | Weight | Notes |
|---|---|---|
| Deadline proximity (D) | 0.30 | Overdue → today → soon → none, mapped to [0,1] |
| Priority (P) | 0.25 | User/derived importance |
| Effort (E) | 0.20 | **Inverted** — lower effort scores higher (momentum-first; see Neurodivergent-First-UX) |
| Momentum (M) | 0.15 | Recency of last action on the parent project |
| Blocker-unblock (B) | 0.10 | How much completing this unblocks |

> The **effort inversion** is the domain-specific twist: a generic productivity tool weights
> effort the opposite way. Keep the sign of each signal a documented decision, not an accident.

> Implementation note from the source app: the weighted formula is specified in the consumer's
> design docs, while the shipped sort currently uses a simpler tier + priority-rank comparator —
> a reminder to keep "the spec" and "what ships" explicitly distinguished.

## Implementation guidance

1. **Normalize every signal to [0,1]** in a pure function so the score is testable in isolation.
2. **Keep weights in one config object** (not scattered constants); validate they sum to 1.
3. **Memoize** the sorted order; invalidate only when inputs or weights change.
4. **Tier before you score** when there are hard ordering rules (e.g. overdue always above
   not-overdue): bucket into tiers first, then score *within* a tier.
5. **Per-user weight evolution** (optional): start from defaults; after N days, nudge weights
   toward the pattern implied by the user's manual reorderings. Cap the drift; keep an audit
   trail so it's explainable.

## Reference snippet (generalized Dart)

```dart
class ScoreWeights {
  final double deadline, priority, effort, momentum, blocker;
  const ScoreWeights({
    this.deadline = 0.30, this.priority = 0.25, this.effort = 0.20,
    this.momentum = 0.15, this.blocker = 0.10,
  });
  double get sum => deadline + priority + effort + momentum + blocker; // assert ≈ 1.0
}

/// All inputs already normalized to [0,1]. `effort` is pre-inverted by the caller.
double scoreItem(WorkItem i, ScoreWeights w) =>
    w.deadline * i.deadline +
    w.priority * i.priority +
    w.effort   * i.effort +
    w.momentum * i.momentum +
    w.blocker  * i.blocker;
```

## When to use / avoid

- **Use** when ranking is multi-factor and "sort by one column" demonstrably mis-orders.
- **Avoid** when a strict lexicographic rule is genuinely correct — a weighted blend then just
  hides the real rule. Prefer tiers for hard constraints, scoring for soft trade-offs.
