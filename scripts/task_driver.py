#!/usr/bin/env python3
"""Live task transition driver — the runtime that mutates the board state machine (framework/19 §5).

Makes the deferred live driver real. It is the ONLY thing that should move a task between machine
states programmatically, and it does so by the two rules framework/19 makes structural:

  1. **Every transition routes through `task_state.apply_transition`** — so the human-at-merge
     invariant (only the operator reaches `Done`) and the mandatory-scoring gate (`Ready ->
     In-Progress` needs a score) can't be skipped.
  2. **Every transition is appended to `tasks/orchestrator-log.jsonl`** (via the existing
     `orchestrator_log.log_envelope`) as a distinct `task_transition` envelope — the log is the
     authoritative ledger of machine state. The markdown board (`tasks/todo.md`) stays the
     operator's 5-value working view; this driver NEVER rewrites it (framework/19 §1.2: the
     intermediate states Proposed/Scored/Ready/Needs-Operator live in the log, not as board cells).

**Claim / lease (framework/19 §3.1).** Routines run on fresh, stateless cloud clones; the only
shared state is the committed repo. `claim_task` writes a `Ready -> In-Progress` claim (with a
uuid `run_id`) to the log BEFORE drafting, fail-closed against a locally-visible active claim. But
two clones of a stale `main` can both pass that check and both append — so the honest winner is
decided AFTER commit+push+pull by `claim_winner` (the earliest active claim wins; a loser reverts
`In-Progress -> Ready` and discards its draft). The driver can't run git, so the Routine wrapper
does push/confirm; this module supplies the fail-closed claim + the winner check. Best-effort,
bounded by the daily run cap. The lease TTL is a long, documented fallback for a *dead* run only;
the primary recovery for a stalled run is the explicit revert.

Pure where it counts (parsing/winner logic are I/O-free); the only I/O is the log read + the
`log_envelope` append. Stdlib only (mirrors task_state.py / orchestrator_log.py). Tested in
tests/test_task_driver.py.

Note: `task_accounting._tasks_done` counts `delivery_result` envelopes by explicit type, so the new
`task_transition` type does NOT inflate productivity counts.
"""
from __future__ import annotations

import json
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))

import task_state as ts                     # noqa: E402
import orchestrator_log as olog            # noqa: E402

ENVELOPE_TYPE = "task_transition"
DEFAULT_LEASE_TTL_S = 7200  # 2h dead-run fallback ONLY; explicit In-Progress->Ready revert is primary

CLAIM_OK = "ok"
CLAIM_NOT_READY = "not_ready"
CLAIM_ALREADY_CLAIMED = "already_claimed"
CLAIM_UNSCORED = "unscored"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


@dataclass
class ClaimResult:
    ok: bool
    reason: str                       # CLAIM_OK | CLAIM_NOT_READY | CLAIM_ALREADY_CLAIMED | CLAIM_UNSCORED
    run_id: Optional[str] = None      # the run_id that holds (on ok) the claim
    holder: Optional[str] = None      # the OTHER run's id when reason == already_claimed


# --- log reads (the authoritative ledger) ----------------------------------------------

def read_transitions(log_path) -> list[dict]:
    """Return the `task_transition` envelopes from the JSONL log, in append order.

    Skips malformed / non-transition lines (a killed run can leave a half-written final line —
    Breaker finding; only committed, well-formed lines count). Returns the inner envelope dicts.
    """
    path = Path(log_path)
    if not path.is_file():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue  # half-written / corrupt line — skip, never crash the driver
        env = rec.get("envelope") if isinstance(rec, dict) else None
        # Require the fields the rest of the module dereferences (`task`, `to`) so a typed-but-
        # incomplete line can't KeyError downstream (audit defect: malformed-line tolerance is an
        # advertised guarantee; the log is a shared, hand-editable ledger).
        if (isinstance(env, dict) and env.get("envelope_type") == ENVELOPE_TYPE
                and env.get("task") and env.get("to")):
            out.append(env)
    return out


def _claim_is_live(env: dict, *, lease_ttl_s: int, now: datetime) -> bool:
    """True if `env` is an In-Progress claim (has a run_id) whose lease hasn't expired. A garbled/
    missing timestamp is treated as live (fail toward not-stealing — matches `active_claim`)."""
    if env.get("to") != ts.IN_PROGRESS or not env.get("run_id"):
        return False
    try:
        claimed_at = datetime.fromisoformat(env["at"])
    except (KeyError, ValueError):
        return True
    return (now - claimed_at).total_seconds() <= lease_ttl_s


def latest_transition(task_title: str, transitions: Sequence[dict]) -> Optional[dict]:
    """The most recent `task_transition` envelope for a task, or None."""
    for env in reversed(transitions):
        if env.get("task") == task_title:
            return env
    return None


def current_state(task_title: str, transitions: Sequence[dict], *,
                  board_state: Optional[str] = None) -> str:
    """The task's canonical machine state: the latest log transition's `to`, else the board state
    (mapped 5-value), else Backlog. The log wins over the board for machine state."""
    last = latest_transition(task_title, transitions)
    if last is not None:
        return last["to"]
    return board_state or ts.BACKLOG


def active_claim(task_title: str, transitions: Sequence[dict], *,
                 lease_ttl_s: int = DEFAULT_LEASE_TTL_S,
                 now: Optional[datetime] = None) -> Optional[dict]:
    """The active claim envelope for a task, or None.

    A claim is active iff the task's LATEST transition put it into In-Progress with a run_id, and
    the lease hasn't expired (a later transition out of In-Progress, or age > lease_ttl_s, ends it).
    """
    now = now or _utcnow()
    last = latest_transition(task_title, transitions)
    if last is None or last["to"] != ts.IN_PROGRESS or not last.get("run_id"):
        return None
    try:
        claimed_at = datetime.fromisoformat(last["at"])
    except (KeyError, ValueError):
        return last  # no/garbled timestamp -> treat as active (fail toward not-stealing)
    if (now - claimed_at).total_seconds() > lease_ttl_s:
        return None  # lease expired -> a dead run; reclaimable
    return last


def reconstruct_states(transitions: Sequence[dict], board_tasks: Sequence["ts.Task"] = (), *,
                       lease_ttl_s: int = DEFAULT_LEASE_TTL_S,
                       now: Optional[datetime] = None) -> dict:
    """Map every task seen (in the log or the board) -> {state, claim}. For the CLI / select_next."""
    now = now or _utcnow()
    titles = {env["task"] for env in transitions}
    board_by_title = {t.title: t for t in board_tasks}
    titles.update(board_by_title)
    out: dict = {}
    for title in titles:
        bstate = board_by_title[title].state if title in board_by_title else None
        out[title] = {
            "state": current_state(title, transitions, board_state=bstate),
            "claim": active_claim(title, transitions, lease_ttl_s=lease_ttl_s, now=now),
        }
    return out


# --- the one mutator (apply + append) --------------------------------------------------

def record_transition(task_title: str, to_state: str, *, actor: str,
                      transitions: Sequence[dict], log_path, run_id: Optional[str] = None,
                      score: Optional[int] = None, now: Optional[datetime] = None) -> dict:
    """Validate one transition via `apply_transition`, append it to the log, return the envelope.

    The `from` state is derived from the log (`current_state`), never trusted from a caller's stale
    object (Breaker #5). Validation runs `task_state.apply_transition` on an ephemeral Task carrying
    `score` (so the Ready->In-Progress score gate is enforced). Raises `task_state.TransitionError`
    on an illegal/unauthorized/unscored move.
    """
    now = now or _utcnow()
    from_state = current_state(task_title, transitions)
    task = ts.Task(title=task_title, state=from_state, raw_status=from_state, score=score)
    ts.apply_transition(task, to_state, actor=actor)  # validates; raises on illegal
    env = {
        "envelope_type": ENVELOPE_TYPE,
        "task": task_title,
        "from": from_state,
        "to": to_state,
        "actor": actor,
        "run_id": run_id,
        "score": score,
        "at": _iso(now),
    }
    olog.log_envelope(env, direction="sent", log_path=Path(log_path))
    return env


# --- claim / lease ---------------------------------------------------------------------

def claim_task(task_title: str, *, run_id: Optional[str] = None, log_path,
               score: Optional[int] = None, lease_ttl_s: int = DEFAULT_LEASE_TTL_S,
               now: Optional[datetime] = None) -> ClaimResult:
    """Attempt to claim a Ready task for autonomous drafting. Fail-closed; returns a ClaimResult.

    Rejects (no write) unless the log state is `Ready`, the task has a recorded score, and no other
    run holds an active claim. On success it appends a `Ready -> In-Progress` transition carrying
    `run_id` and returns ok=True. NOTE this closes only locally-visible races — the caller MUST
    commit+push+pull and then confirm via `claim_winner` (two stale clones can both reach here).
    """
    now = now or _utcnow()
    run_id = run_id or uuid.uuid4().hex
    transitions = read_transitions(log_path)

    # An ACTIVE claim by another run beats everything — report it (not the bare state).
    held = active_claim(task_title, transitions, lease_ttl_s=lease_ttl_s, now=now)
    if held is not None:
        return ClaimResult(ok=False, reason=CLAIM_ALREADY_CLAIMED, holder=held.get("run_id"))

    state = current_state(task_title, transitions)
    # No active claim but still In-Progress => an expired/dead lease. Recover it explicitly
    # (In-Progress -> Ready is legal for a session; In-Progress -> In-Progress is NOT) so a fresh
    # run can re-claim cleanly. The revert is logged, so the steal is auditable. This is the
    # dead-run fallback; a live stalled run should revert itself first (framework/19 §3.1).
    if state == ts.IN_PROGRESS:
        record_transition(task_title, ts.READY, actor=ts.SESSION, transitions=transitions,
                          log_path=log_path, now=now)
        transitions = read_transitions(log_path)
        state = current_state(task_title, transitions)

    if state != ts.READY:
        return ClaimResult(ok=False, reason=CLAIM_NOT_READY)
    if score is None:
        return ClaimResult(ok=False, reason=CLAIM_UNSCORED)  # mirrors the Ready->In-Progress gate
    record_transition(task_title, ts.IN_PROGRESS, actor=ts.SESSION, transitions=transitions,
                      log_path=log_path, run_id=run_id, score=score, now=now)
    return ClaimResult(ok=True, reason=CLAIM_OK, run_id=run_id)


def claim_winner(task_title: str, transitions: Sequence[dict], *,
                 lease_ttl_s: int = DEFAULT_LEASE_TTL_S,
                 now: Optional[datetime] = None) -> Optional[str]:
    """The run_id that owns the task after commit+push+pull: the EARLIEST active In-Progress claim.

    When two stale clones both appended a claim, the committed-log order breaks the tie — the
    earliest claim wins. A loser (its run_id != winner) must revert `In-Progress -> Ready` and
    discard its draft. Returns None if the task isn't actively claimed.
    """
    now = now or _utcnow()
    held = active_claim(task_title, transitions, lease_ttl_s=lease_ttl_s, now=now)
    if held is None:
        return None
    # The earliest *live* claim in the streak leading up to the active hold. A non-claim transition
    # (e.g. a revert) resets the streak; an EXPIRED claim resets it too — a dead run has abandoned
    # the task, so a later live claim must win, not the dead head (audit defect: claim_winner could
    # otherwise elect a dead run, telling the live run it lost and stalling the task).
    earliest: Optional[dict] = None
    for env in transitions:
        if env.get("task") != task_title:
            continue
        if _claim_is_live(env, lease_ttl_s=lease_ttl_s, now=now):
            if earliest is None:
                earliest = env
        else:
            earliest = None
    return (earliest or held).get("run_id")


def revert_stalled(task_title: str, *, actor: str = ts.SESSION, log_path,
                   now: Optional[datetime] = None) -> dict:
    """Discard a stalled/lost claim: append `In-Progress -> Ready` so a later run redoes it cleanly
    (atomic/idempotent recovery, framework/19 §3.1). Legal for session or operator."""
    transitions = read_transitions(log_path)
    return record_transition(task_title, ts.READY, actor=actor, transitions=transitions,
                             log_path=log_path, now=now)


# --- routing: scored Backlog -> Ready / Needs-Operator (the scoring/routing layer) -----

def _rail_hit(task: "ts.Task") -> Optional[str]:
    """Return the rail signal word a task trips, or None. Word-level over title+category+notes.

    The rail BACKSTOP (Delta-Force Breaker finding): a single operator-entered DFTS must NOT be able
    to send safety-critical work (auth/security/data-model/billing/rails) down the autonomous path —
    a rail hit forces Needs-Operator regardless of score.
    """
    import re as _re
    hay = f"{task.title} {task.category} {task.notes}".lower()
    for phrase in ts.RAIL_PHRASES:           # multi-word / hyphenated rails (substring)
        if phrase in hay:
            return phrase
    words = set(_re.findall(r"[a-z0-9]+", hay))   # single-token rails (word-level)
    for w in sorted(ts.RAIL_SIGNALS):
        if w in words:
            return w
    return None


_ROUTING_STATES = (ts.BACKLOG, ts.PROPOSED, ts.SCORED)


def _route_chain(from_state: str, target: str) -> list:
    """Remaining legal transition sequence from `from_state` to `target` (READY | NEEDS_OPERATOR).

    Resumes a partially-routed task — if a prior run crashed mid-chain leaving it in Proposed/Scored,
    the next run continues from there rather than stranding it (Regime-B audit Concern 2). Every edge
    is legal for actor=scoring (Backlog->Proposed->Scored->Ready, or ->Needs-Operator from any of
    Backlog/Proposed/Scored)."""
    to_ready = {ts.BACKLOG: [ts.PROPOSED, ts.SCORED, ts.READY],
                ts.PROPOSED: [ts.SCORED, ts.READY],
                ts.SCORED: [ts.READY]}
    to_needs = {ts.BACKLOG: [ts.PROPOSED, ts.NEEDS_OPERATOR],
                ts.PROPOSED: [ts.NEEDS_OPERATOR],
                ts.SCORED: [ts.NEEDS_OPERATOR]}
    return (to_ready if target == ts.READY else to_needs).get(from_state, [])


def route_scored(board_tasks: Sequence["ts.Task"], transitions: Sequence[dict], *, log_path,
                 now: Optional[datetime] = None, dry_run: bool = False) -> dict:
    """Route scored Backlog tasks to Ready (autonomous-draftable) or Needs-Operator (human). Returns
    a structured summary; does NOT compute scores (reads the recorded DFTS; skips unscored).

    Per task currently in Backlog with a recorded score:
      * rail hit (RAIL_SIGNALS) -> Needs-Operator, regardless of DFTS (reason `rail:<word>`);
      * else DFTS < AUTONOMOUS_DFTS_BELOW (=4) -> Ready (Backlog->Proposed->Scored->Ready);
      * else (>=4) -> Needs-Operator (reason `dfts>=4`).
    Idempotent: a task already past Backlog is skipped, but a currently-Ready task whose board score
    now disqualifies it (rail or >=4) is reported in `drift` (NOT auto-pulled — actor=scoring can't
    legally move Ready->Needs-Operator; that's an operator action; `lint_routing_drift` also flags
    it). Returns {routed_ready, routed_needs_operator:[(title,reason)], skipped, drift:[(title,reason)]}.
    """
    now = now or _utcnow()
    transitions = list(transitions)
    out = {"routed_ready": [], "routed_needs_operator": [], "skipped": [], "drift": []}

    def _disqualifier(t):
        rail = _rail_hit(t)
        if rail:
            return f"rail:{rail}"
        if t.score is not None and t.score >= ts.AUTONOMOUS_DFTS_BELOW:
            return "dfts>=4"
        return None

    for t in board_tasks:
        state = current_state(t.title, transitions)
        if state not in _ROUTING_STATES:
            # past routing (Ready/In-Progress/Done/...): idempotent skip, but flag a Ready task
            # whose board score/rail now disqualifies it (operator re-scored — surfaced, not pulled).
            if state == ts.READY:
                why = _disqualifier(t)
                if why:
                    out["drift"].append((t.title, why))
            out["skipped"].append(t.title)
            continue
        if t.score is None:
            out["skipped"].append(t.title)   # never invent a score; leave it where it is
            continue

        disq = _disqualifier(t)
        target = ts.NEEDS_OPERATOR if disq else ts.READY
        if dry_run:
            (out["routed_needs_operator"].append((t.title, disq)) if disq
             else out["routed_ready"].append(t.title))
            continue

        # Drive the remaining legal chain (resumes a partial route; preserves the structural
        # mandatory-scoring guarantee — apply_transition enforces a score on the Scored/Ready edges).
        for to_state in _route_chain(state, target):
            record_transition(t.title, to_state, actor=ts.SCORING, transitions=transitions,
                              log_path=log_path, score=t.score, now=now)
            transitions = read_transitions(log_path)
        (out["routed_needs_operator"].append((t.title, disq)) if disq
         else out["routed_ready"].append(t.title))
    return out


def lint_routing_drift(board_tasks: Sequence["ts.Task"], transitions: Sequence[dict], *,
                       now: Optional[datetime] = None) -> list:
    """Flag currently-Ready tasks whose board score/rail now disqualifies them (operator re-scored a
    task that's already autonomously claimable). Pure; surfaced for the operator to pull back."""
    now = now or _utcnow()
    findings = []
    for t in board_tasks:
        if current_state(t.title, transitions) != ts.READY:
            continue
        rail = _rail_hit(t)
        if rail:
            findings.append({"task": t.title, "issue": "ready-now-rail", "detail": f"rail:{rail}"})
        elif t.score is not None and t.score >= ts.AUTONOMOUS_DFTS_BELOW:
            findings.append({"task": t.title, "issue": "ready-now-needs-operator",
                             "detail": f"DFTS {t.score} >= {ts.AUTONOMOUS_DFTS_BELOW}"})
    return findings


# --- selection (Focus Mode over the Ready, unclaimed pool) -----------------------------

def select_next(board_tasks: Sequence["ts.Task"], transitions: Sequence[dict], *,
                focus: Optional[str] = None, goal: Optional[str] = None,
                lease_ttl_s: int = DEFAULT_LEASE_TTL_S,
                now: Optional[datetime] = None) -> dict:
    """Pick the next claimable task: Ready (per the log) AND unclaimed, ordered by Focus Mode.

    Overlays log state onto the board pool, keeps only Ready+unclaimed tasks, then runs
    `task_state.select_actionable` (focus filter + goal dial). Returns the select_actionable dict
    with an added `next` (the top task or None). Pure given `transitions`.
    """
    now = now or _utcnow()
    states = reconstruct_states(transitions, board_tasks, lease_ttl_s=lease_ttl_s, now=now)
    ready = []
    for t in board_tasks:
        st = states.get(t.title, {})
        if st.get("state") == ts.READY and st.get("claim") is None:
            # carry the board task but reflect its Ready machine-state for select_actionable
            ready.append(ts.Task(title=t.title, state=ts.READY, raw_status=t.raw_status,
                                 priority=t.priority, category=t.category, score=t.score))
    sel = ts.select_actionable(ready, focus=focus, goal=goal)
    sel["next"] = sel["selected"][0] if sel["selected"] else None
    return sel


# --- CLI -------------------------------------------------------------------------------

def _main(argv: Optional[list] = None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="task_driver", description=__doc__)
    p.add_argument("--log", default=str(Path("tasks") / "orchestrator-log.jsonl"))
    p.add_argument("--todo", default=str(Path("tasks") / "todo.md"))
    p.add_argument("--reconstruct", action="store_true", help="print every task's current state + claim")
    p.add_argument("--route-scored", action="store_true",
                   help="route scored Backlog tasks -> Ready (DFTS<4, no rail) / Needs-Operator")
    p.add_argument("--next", action="store_true", help="print the next claimable Ready task")
    p.add_argument("--focus", help="Focus Mode directive for --next")
    p.add_argument("--goal", choices=("save_budget", "balanced", "maximize_ai"), help="goal dial for --next")
    p.add_argument("--transition", metavar="TASK", help="apply a transition for TASK (mechanical)")
    p.add_argument("--to", help="target state for --transition")
    p.add_argument("--actor", choices=(ts.OPERATOR, ts.SESSION, ts.SCORING), default=ts.SESSION)
    p.add_argument("--score", type=int, help="DFTS score to attach (needed for the Ready gate)")
    p.add_argument("--claim", metavar="TASK", help="claim TASK for drafting (Ready->In-Progress)")
    p.add_argument("--run-id", help="run id for --claim/--transition (default: a fresh uuid)")
    p.add_argument("--dry-run", action="store_true", help="print the intended action; write nothing")
    args = p.parse_args(argv)

    transitions = read_transitions(args.log)
    board = ts.parse_todo(args.todo) if Path(args.todo).is_file() else []

    if args.reconstruct:
        for title, st in sorted(reconstruct_states(transitions, board).items()):
            claim = st["claim"]["run_id"] if st["claim"] else "-"
            print(f"{st['state']:<14} claim={claim:<34} {title}")
        return 0

    if args.route_scored:
        summary = route_scored(board, transitions, log_path=args.log, dry_run=args.dry_run)
        tag = "[dry-run] would route" if args.dry_run else "routed"
        print(f"{tag}: {len(summary['routed_ready'])} -> Ready, "
              f"{len(summary['routed_needs_operator'])} -> Needs-Operator, "
              f"{len(summary['skipped'])} skipped")
        for t in summary["routed_ready"]:
            print(f"  Ready          {t}")
        for t, why in summary["routed_needs_operator"]:
            print(f"  Needs-Operator {t}  ({why})")
        for t, why in summary["drift"]:
            print(f"  DRIFT (Ready now disqualified) {t}  ({why})")
        return 0

    if args.next:
        sel = select_next(board, transitions, focus=args.focus, goal=args.goal)
        nxt = sel["next"]
        print(f"next claimable: {nxt.title if nxt else '(none Ready+unclaimed)'}")
        if sel["dropped_for_focus"]:
            print(f"  parked out of focus: {', '.join(sel['dropped_for_focus'])}")
        return 0

    if args.transition:
        if not args.to:
            p.error("--transition requires --to")
        if args.dry_run:
            frm = current_state(args.transition, transitions)
            print(f"[dry-run] {frm} -> {args.to} (actor={args.actor}, score={args.score}) — nothing written")
            return 0
        env = record_transition(args.transition, args.to, actor=args.actor, transitions=transitions,
                                log_path=args.log, run_id=args.run_id, score=args.score)
        print(f"transitioned: {env['from']} -> {env['to']}  {env['task']}")
        return 0

    if args.claim:
        if args.dry_run:
            state = current_state(args.claim, transitions)
            held = active_claim(args.claim, transitions)
            print(f"[dry-run] claim {args.claim}: state={state} "
                  f"held_by={held['run_id'] if held else '-'} scored={args.score is not None} — nothing written")
            return 0
        res = claim_task(args.claim, run_id=args.run_id, log_path=args.log, score=args.score)
        if res.ok:
            print(f"claimed {args.claim} (run_id={res.run_id}) — commit+push, then confirm with claim_winner")
        else:
            print(f"NOT claimed ({res.reason}" + (f", holder={res.holder}" if res.holder else "") + ")")
            return 1
        return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
