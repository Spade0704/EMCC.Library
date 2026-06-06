---
name: process-feedback
description: "Run EMCC's feedback -> draft-PR loop in a Claude Code session (the council-locked design): read the compiled, triaged feedback, run /delta-force or /llm-council on an OBVIOUS low-risk item, and DRAFT a PR (the change + the gate transcript + the Auditor verdict) for the operator to review. DEEP / safety-rail / unknown items escalate. NEVER auto-merges; the human merges everything."
---

# Process Feedback — the draft-PR factory (session runtime)

> Implements the **unanimous** council verdict
> (`tasks/council/council-2026-06-06-feedback-auto-loop.md`): a **DRAFT-PR factory, NOT an
> auto-merge loop. The human merges everything.** Runs in a Claude Code session (no API key,
> iPad-friendly); every change is draft-only until the operator merges. Reads
> `scripts/feedback_log.py` (`compile_feedback` / `triage`).

## When to trigger
"process feedback", "/process-feedback", "act on the feedback", "draft fixes from feedback", "work the feedback queue".

## HARD FENCES (non-negotiable — from the council)
1. **NEVER auto-merge.** Every change is a **draft PR** the operator merges. No exceptions — not
   even a typo. Auto-merge was rejected unanimously (same-model gates are not independent review).
2. **NEVER draft a change to the SAFETY RAILS** — the gates (`/llm-council`, `/delta-force`, the
   Auditor), the triage rules, the kill switch, Guard-House, auth, or the data model. Those route
   to the operator as a `decision_needed`, **unconditionally**. (Code-enforced fence: the loop
   cannot weaken its own brakes.)
3. **Triage only ROUTES** (draft vs escalate) — it never authorizes an action. The hard judgment
   ("is this safe to change") is never ceded; that's why the human merges.
4. **Kill switch:** if `DECISION_LOOP_ENABLED` is false/unset, do NOT draft — escalate everything.

## The spine enforces the fences in code
`scripts/decision_loop.py` is the **built** spine: `route()` (fail-closed: kill-switch → rail →
allowlist `SAFE_SURFACES` → triage) and `process(items, *, enabled, draft_fn, escalate_fn)`. It
has **no merge function**. This skill supplies the injected `draft_fn` (run the gate + Auditor,
generate the diff, open a **draft** PR — returning `{draft: True, pr_ref, gate_ref, verdict}`)
and `escalate_fn` (emit a `decision_needed`). Let the spine route; you do the side-effects. A
`draft_fn` that can't honestly return `draft is True` must let `process` record it as escalated.

## The loop
1. **Read** the compiled, triaged feedback: `compile_feedback()` (human + the system's own `self`
   signals from the bus log), each carrying a `triage` ∈ obvious | deep | unknown.
2. **For each item:**
   - **rails / security / auth / data**, OR `triage` ∈ {deep, unknown} → **ESCALATE**: summarize it
     + ask the operator (a `decision_needed`). **Stop. Do not draft.**
   - `triage == obvious` **and** a low-risk surface (docs / copy / config) → **DRAFT**:
     1. run **`/delta-force`** (a code change) or **`/llm-council`** (a "what" decision) on it.
     2. make the change on a **new branch** (never `main`).
     3. run the **Regime-B Auditor** on the diff.
     4. open a **DRAFT PR** whose body staples: the **feedback origin**, the **gate transcript**,
        and the **Auditor verdict**. Leave it for the operator to review + merge.
3. **Report** a review queue: **"drafted (your merge): …"** + **"needs your decision: …"**. Never
   a merge.

## Deferred (needs the Director LLM runtime / not in this skill)
The autonomous *always-on* version and any *auto-merge* are out of scope by council decision. The
*code-generation quality* improves when the LLM tier lands (Gateway / API), but the draft-only
loop runs today in a session. Surfaces in the dashboard **Feedback** + **Decisions** views.

## Output
A review queue the operator works through — they remain the **only** one who merges.
