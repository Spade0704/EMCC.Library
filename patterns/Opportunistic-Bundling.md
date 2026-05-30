---
title: "Pattern — Opportunistic Context Bundling"
type: reference
visibility: internal
completion: 38
status: outlined
last_updated: 2026-05-30
dependencies: ["patterns/Decision-Scoring"]
public_pair: null
blocking_questions: []
topics: []
related_files: []
tags: []
canon_sources: []
unverified_claims: []
---

# Opportunistic Context Bundling

> Generalized from the lifting consumer's "while you're at it" feature. Note: EMCC reserves the
> **Cartometrics / WYAI** module name for the portfolio-level version of this idea (currently
> deferred); this doc is the consumer-app-level pattern and a seed for that module.

## Problem

Items in a queue share latent context — same place, same tool, same vendor, same short
free-time window. Handling them one at a time wastes the setup cost common to the whole group
("I'm already at the store / already in the design tool / have 15 free minutes").

## Pattern

Tag each item with zero or more **context tokens**. When the user engages one item, surface the
other items that share a context token as an optional **bundle**: "while you're here, also do X
and Y." Bundling is a *suggestion surface*, never an automatic mutation.

### Context taxonomy (reference)

| Bundle type | Token source | Example |
|---|---|---|
| Location | place tag | all "hardware-store" errands |
| Tool/app | tool tag | all "design-tool" tasks |
| Vendor | vendor tag | all calls to one supplier |
| Time-box | effort estimate ≤ threshold | all "≤15 min" quick wins |
| Category | free-form tag | all "admin" items |
| Routine | recurrence group | this morning's recurring set |

## Implementation guidance

1. **Model context as a `List<String>` on the item**, not a single enum — items legitimately
   belong to several bundles.
2. **Infer where you can, let the user confirm.** Time-box bundles derive from the effort
   estimate; location/vendor often need a light tag. Don't block capture on tagging.
3. **Rank the bundle** with the same Decision-Scoring engine so the bundle's lead item is the
   one worth starting with.
4. **Keep it non-destructive.** The bundle is a view; completing/snoozing happens per item.
5. **Cap the surface.** Show the top-N bundle members, not an exhaustive list, to avoid
   re-creating the overwhelming queue the bundle was meant to relieve.

## Data shape (generalized)

```jsonc
// item document
{
  "title": "Buy picture hooks",
  "context": ["hardware-store", "errand"],   // bundle tokens
  "effortMinutes": 10,                         // feeds the time-box bundle
  "timeContext": "anytime"                     // morning|afternoon|evening|anytime
}
```

## When to use / avoid

- **Use** when items carry reusable setup cost and users batch naturally in the real world.
- **Avoid** turning every shared word into a bundle — noise destroys trust in the surface.
  Require either an explicit tag or a high-confidence inference.
