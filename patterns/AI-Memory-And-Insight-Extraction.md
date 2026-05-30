---
title: "Pattern — AI Memory & Insight Extraction"
type: reference
visibility: internal
completion: 38
status: outlined
last_updated: 2026-05-30
dependencies: ["patterns/Soft-Delete-Signal-Preservation"]
public_pair: null
blocking_questions: ["Which parts generalize vs. stay consumer-specific to the assistant's persona?"]
topics: []
related_files: []
tags: []
canon_sources: []
unverified_claims: []
---

# AI Memory & Insight Extraction

> The data architecture below generalizes; the assistant's *persona* and extraction prompts stay
> consumer-specific. Lifted from the consumer's "Memory System v1.2" design.

## Problem

An AI co-pilot that forgets everything between sessions can't personalize, and one that stores
raw chat transcripts forever is a privacy and cost liability. You want **durable, compact,
de-identified** memory plus a cheap path for routine turns and an expensive path for generation.

## Pattern

Three layers:

1. **Schema** — a small set of per-user collections that hold *derived* memory, not transcripts:
   - `userProfile` — stable preferences/traits
   - `chatInsights` — extracted, generalized observations (with provenance)
   - `userReflexes` — compiled fast-path rules the assistant can apply without a model call
   - `insightRejections` — audit trail of insights that failed validation (privacy + tuning)

2. **Extraction + validation pipeline** — after a conversation, a model extracts candidate
   insights; each must pass a **3-check gate** before it's written: *no PII, no direct
   identifiers, generalizable*. Failures land in `insightRejections` (never silently dropped).

3. **Compression + routing**:
   - **Compression levels** — store insights compactly (L1 plain-English -> L2 shorthand) to
     bound context cost.
   - **Model routing** — a cheap model handles classification / routine replies; an expensive
     model handles generation. Route on task type; **log every call's cost** for observability.

```
chat -> cheap model (route/classify) -> {reflex hit? answer now}
                                    \-> expensive model (generate) -> extract insights
                                                                  \-> 3-check gate -> chatInsights | insightRejections
```

## Implementation guidance

1. **Never persist raw transcripts as memory.** Persist validated, generalized insights.
2. **Make the validation gate structural**, not advisory — an unvalidated insight cannot reach
   `chatInsights` by construction (DFDU "Structural over Advisory").
3. **Compile reflexes** from repeated insights so common cases skip the model entirely
   (latency + cost win).
4. **Budget context** by reading top-K compressed insights, not the whole store.
5. **Tie deletion to memory** — when a user deletes data, purge derived insights that could
   re-identify (pairs with Soft-Delete-Signal-Preservation).

## When to use / avoid

- **Use** for any assistant that should feel like it remembers the user across sessions.
- **Avoid** shipping the extraction without the privacy gate or the cost logging — those two are
  what make this safe and affordable, not optional polish.
