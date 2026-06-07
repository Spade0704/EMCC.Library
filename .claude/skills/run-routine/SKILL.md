---
name: run-routine
description: "The autonomous-drafting caller a scheduled Routine runs: route scored Backlog tasks, claim the next Ready one (lease, fail-closed), and DRAFT a PR for it — then delegate the drafting/gate/Auditor/fences to /process-feedback. NEVER merges; the human merges everything. Drafts one atomic task per run."
---

# Run Routine — the autonomous-drafting caller (Routine-invoked)

> **Naming:** a *Routine* is the Claude Code **platform** feature (cloud-scheduled trigger,
> claude.ai/code/routines); **this skill** (`/run-routine`) is what that Routine's prompt invokes
> inside the woken session. Don't confuse the two.
>
> This is the **task-queue sibling** of `/process-feedback`: same council-locked draft-PR factory,
> but the work item comes from the task board's `Ready` lane (with a claim/lease) instead of the
> feedback queue. Canon: `framework/19-task-orchestration.md` §3 + the
> `Documentation/routine-draft-pr-playbook.md`. Gate: `EMCC.DFDU/tasks/delta-force/2026-06-06-routine-caller.md`.

## When to trigger
"run routine", "/run-routine", "work the Ready queue", "draft the next ready task" — or a scheduled
Routine whose prompt is "Run /run-routine".

## NEVER block (step 0 — read before anything else)
- **NEVER merge.** The output is **always a DRAFT PR**. The human merges everything (council-locked).
- **NEVER touch the safety rails** — the gates, triage rules, the kill switch, Guard-House, auth,
  the data model. Rail work escalates to `Needs-Operator`, unconditionally.
- **If any step is unclear, rail-adjacent, or Level-2+ → stop and escalate to `Needs-Operator`.**
- Every "open a PR" instruction below means **open a DRAFT PR**.

## The loop (one atomic task per run — daily-cap-aware)

1. **Kill switch.** If `DECISION_LOOP_ENABLED` is false/unset → draft nothing; stop. (Same fence as
   `/process-feedback` #4.)

2. **Route.** `python scripts/task_driver.py --route-scored` — promotes scored Backlog tasks to
   `Ready` (DFTS<4, no rail) or `Needs-Operator` (DFTS>=4 **or** a rail signal). The rail check is
   **signal-based, not exhaustive** — it's the first of two automated layers (step 6 is the second, a
   post-draft touched-path re-check), and the operator's merge review is the ultimate backstop. If a
   task looks rail-adjacent in any way the signals didn't catch, escalate it to `Needs-Operator`
   yourself. Review the printed summary; if it reports `DRIFT`, surface that and skip those tasks.

3. **Select.** `select_next(parse_todo("tasks/todo.md"), read_transitions(log), focus=…, goal=…)`
   (`scripts/task_driver.py`) → the next `Ready`+unclaimed task, Focus-Mode/goal ordered. If none →
   stop ("nothing Ready to draft"). Work **one** task this run.

4. **Claim (lease, fail-closed).** `claim_task(title, run_id=<this claude/ branch>, log_path=…,
   score=…)`.
   - If not `ok` (`already_claimed` / `not_ready` / `unscored`) → pick the next, or stop.
   - On `ok`: **commit + push** the claim, **then verify the push succeeded**, then `git pull`.
     **`claim_winner(title, read_transitions(log))` must equal your `run_id`** — if it doesn't (a
     second clone won the race), `revert_stalled(title, log_path=…)` and **stop** (discard, no draft).
   - If the push **fails**, `revert_stalled` the local claim and stop (never draft off an unpushed
     claim — that double-drafts).

5. **Verify-gap check.** Confirm the task is verifiable **in this clone** (its tests/build/lint can
   run here). If it cannot be verified at all in-environment → `record_transition(title,
   Needs-Operator, actor=session)` and stop. Do **not** draft code you can't check.

6. **Draft — delegate to `/process-feedback`.** Treat the claimed task as the work item and follow
   the **`/process-feedback` draft-PR contract verbatim** (do not restate or weaken its fences here):
   make the change on the claimed branch, run the gate appropriate to the task's level (DFTS<4 atomic
   → self-review; anything that turns out Level-2+/rail mid-draft → **stop, escalate**), run the
   **Regime-B Auditor** on the diff, and **re-check the touched paths** — if the diff touched a rail
   file (auth/security/data-model/gates/kill-switch/Guard-House), abort to `Needs-Operator` and open
   **no** PR (the second rail layer). **Idempotency:** before opening a PR, check there isn't already
   an open PR for this task/branch (a re-run must not open a second).

7. **Open the DRAFT PR.** Body staples, top-to-bottom: the **task title + origin**, the **DFTS
   score**, the **rail-check result**, the **Auditor verdict verbatim**, and a bold
   **"This is a DRAFT — you merge it; I cannot."** Then `record_transition(title, For-Review,
   actor=session)` (the board view reflects it under *Needs Human Review*). Stop.

## Report
"drafted (your merge): `<task>` → PR #N" or "escalated to Needs-Operator: `<task>` (`<reason>`)" or
"nothing Ready to draft". Never a merge.

## Deferred / out of scope
The live always-on caller and any auto-merge are out by council decision. This skill runs under a
scheduled Routine (operator-configured) or interactively; the dry-run path
(`task_driver.py --route-scored --dry-run`, `--next`, `--claim … --dry-run`) is the verification
harness (`routine-draft-pr-playbook.md` §Verification). Surfaces in the dashboard **Decisions** view.
