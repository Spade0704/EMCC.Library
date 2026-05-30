---
title: "Pattern — Neurodivergent-First UX"
type: guide
visibility: internal
completion: 36
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

# Neurodivergent-First UX

> Generalized UX principles for executive-function support, lifted from the consumer's
> "ADHD-first" design. Useful well beyond the original audience — the same moves reduce friction
> for any overwhelmed user.

## Problem

Conventional productivity UX assumes a user who can self-start, tolerate big backlogs, and read
overdue counters as motivation. For users with executive-function challenges these same patterns
produce shame, avoidance, and abandonment.

## Principles -> mechanisms

| Principle | Mechanism |
|---|---|
| **Micro-momentum over completeness** | Surface the *easiest* useful next action; weight low effort **higher** (see Decision-Scoring) |
| **Park, don't delete** | Soft-delete with restore, so nothing is "lost" and no decision is final (Soft-Delete-Signal-Preservation) |
| **Quick wins first** | Sort by effort, not difficulty; let a 2-minute task be the visible starting point |
| **No-shame language** | "Welcome back" not "12 overdue"; color-coded, non-aggressive deadline cues |
| **Adaptive rewards** | Daily-wins cap that adapts to streak length, with time-away decay so returning users aren't punished |
| **Reduce the surface** | Cap visible lists; bundle by context so the queue never reads as a wall (Opportunistic-Bundling) |
| **Voice / low-friction capture** | Make capture instant and unstructured; enrich later, never block on tagging |

## Implementation guidance

1. **Encode the principles as defaults**, not opt-in settings — the user who needs them most
   won't go find a toggle.
2. **Audit copy for shame.** Every empty state, overdue cue, and error is a chance to reassure
   instead of scold. Keep a forbidden-tone list.
3. **Make rewards adaptive, not fixed** — a static "streak" punishes the exact lapse this
   audience is prone to. Decay and re-welcome instead.
4. **Default to reversible.** Destructive actions get an undo or a park, not a confirm dialog.

## When to use / avoid

- **Use** as the baseline for any consumer tool whose users are overwhelmed or
  procrastination-prone — it generalizes past the clinical framing.
- **Avoid** treating it as theming. These are behavior + copy + default-value decisions; a color
  palette alone doesn't deliver them.
