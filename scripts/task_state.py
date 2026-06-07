#!/usr/bin/env python3
"""Task state machine — the reconciled v2.1 orchestration flow (framework/19).

Formalizes the task lifecycle the operator + Grok drafted in "Task Orchestration Protocol v2",
RECONCILED with EMCC's locked human-at-merge invariant (the unanimous council verdict
`tasks/council/council-2026-06-06-feedback-auto-loop.md`: *"NEVER auto-merges; the human merges
everything."*). The council on the v2 proposal (`tasks/council/2026-06-06-task-orchestration-v2.md`)
adopted v2's flow-control half (state machine + Focus Mode + Routine-triggered drafting) and
rejected its trust-transfer half (scoring authoritative → autonomous merge).

The load-bearing invariant, enforced HERE in code, not just prose:
  * Only the **operator** can transition a task into DONE. Scoring (DFTS) and sessions/Routines
    can draft, route, and order work; they can NEVER merge. `validate_transition(..., actor=...)`
    raises if anyone but the operator moves FOR_REVIEW/NEEDS_OPERATOR → DONE.

Two more rules carried from the v2 design + framework/09 §3:
  * **Scoring is mandatory before autonomous drafting.** A task cannot reach SCORED or READY
    without a recorded DFTS score (`requires_score`). This is "the scoring step is mandatory
    before any task reaches DFDU for execution" — made structural.
  * **Atomic/idempotent recovery.** This module *supports* (does not enforce — that is a process
    rule about how tasks are written) the atomic/idempotent contract: an interrupted/stalled
    IN_PROGRESS run is allowed to revert to READY, because tasks are required to be re-runnable
    from a fresh stateless clone (operator decision: no checkpoint/resume engine; framework/19
    §"Resilience"). The machine permits the safe revert; the task author guarantees idempotency.

Pure + stdlib only (mirrors scripts/director_memory.py): the transition table, validation,
selection, and the todo lint are all I/O-free except the thin `parse_todo` file read. Tested in
tests/test_task_state.py.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

# --- canonical states (the v2.1 lifecycle) ---------------------------------------------
BACKLOG = "Backlog"                 # raw / unprioritized pool
PROPOSED = "Proposed"               # ready for DFTS scoring (a.k.a. Needs-Scoring)
SCORED = "Scored"                   # scored, not yet routed
READY = "Ready"                     # cleared for autonomous DRAFTING (never merging)
IN_PROGRESS = "In-Progress"         # a session/Routine is drafting it
FOR_REVIEW = "For-Review"           # a DRAFT PR is open, awaiting the operator's merge
DONE = "Done"                       # operator merged — the ONLY way out the top
NEEDS_OPERATOR = "Needs-Operator"   # escalated (rails/deep/unknown/risky-mid-run)
SUPERSEDED = "Superseded"           # obsolete; kept for provenance, not actionable

STATES = frozenset({BACKLOG, PROPOSED, SCORED, READY, IN_PROGRESS,
                    FOR_REVIEW, DONE, NEEDS_OPERATOR, SUPERSEDED})
TERMINAL = frozenset({DONE, SUPERSEDED})

# --- actors (who may drive a transition) -----------------------------------------------
OPERATOR = "operator"   # the human — the ONLY merge authority
SESSION = "session"     # a Claude Code session / Routine / draft loop (drafts, never merges)
SCORING = "scoring"     # the DFTS gate (routes + scores, never authorizes a merge)
ACTORS = frozenset({OPERATOR, SESSION, SCORING})


class TransitionError(ValueError):
    """Raised when a state transition is illegal or the actor lacks authority."""


@dataclass(frozen=True)
class Transition:
    to: str
    actors: frozenset            # who may perform it
    requires_score: bool = False  # target needs a recorded DFTS score
    note: str = ""               # inline doc; reserved for the deferred live driver's audit log


# Legal transitions. Anything not listed is illegal (fail-closed, like decision_loop.route()).
# The merge fence: ONLY OPERATOR appears on any edge INTO DONE.
_T = Transition
LEGAL_TRANSITIONS: dict[str, tuple[Transition, ...]] = {
    BACKLOG: (
        _T(PROPOSED, frozenset({OPERATOR, SESSION, SCORING}), note="queued for scoring"),
        _T(SUPERSEDED, frozenset({OPERATOR}), note="operator retires a raw item"),
    ),
    PROPOSED: (
        _T(SCORED, frozenset({SCORING}), requires_score=True, note="DFTS scored it"),
        _T(NEEDS_OPERATOR, frozenset({SCORING, SESSION}), note="hard-trigger/deep/unknown → escalate"),
        _T(SUPERSEDED, frozenset({OPERATOR})),
    ),
    SCORED: (
        # DFTS clears it for autonomous DRAFTING (Level 0/1, no rail) — never for merge.
        _T(READY, frozenset({SCORING}), requires_score=True, note="cleared for autonomous draft"),
        # Level-2+ / rails / contested → the operator decides (the rejected-auto-exec path).
        _T(NEEDS_OPERATOR, frozenset({SCORING}), note="Level-2+/rail → operator"),
        _T(SUPERSEDED, frozenset({OPERATOR})),
    ),
    READY: (
        # The autonomous-drafting START edge — gated by a recorded score so NO session/Routine
        # can ever draft an unscored task, regardless of how the task reached READY. This is the
        # structural enforcement of "scoring is mandatory before AUTONOMOUS drafting" (§1.1 rule 2).
        _T(IN_PROGRESS, frozenset({SESSION}), requires_score=True, note="a session/Routine starts drafting"),
        _T(NEEDS_OPERATOR, frozenset({SESSION, OPERATOR})),
        _T(SUPERSEDED, frozenset({OPERATOR})),
    ),
    IN_PROGRESS: (
        _T(FOR_REVIEW, frozenset({SESSION}), note="draft PR opened (never a merge)"),
        # Became unclear/risky mid-run → escalate (process-feedback fence #2).
        _T(NEEDS_OPERATOR, frozenset({SESSION, OPERATOR}), note="unclear/risky mid-run → escalate"),
        # Stalled/interrupted Routine run: discard partial work, revert for a fresh re-run.
        # Safe BECAUSE tasks are atomic + idempotent (no checkpoint engine). framework/19.
        _T(READY, frozenset({SESSION, OPERATOR}), note="stalled run discarded → re-runnable"),
        _T(SUPERSEDED, frozenset({OPERATOR})),
    ),
    FOR_REVIEW: (
        _T(DONE, frozenset({OPERATOR}), note="THE INVARIANT — only the operator merges"),
        _T(IN_PROGRESS, frozenset({OPERATOR, SESSION}), note="operator requested changes → re-draft"),
        _T(NEEDS_OPERATOR, frozenset({OPERATOR})),
        _T(SUPERSEDED, frozenset({OPERATOR})),
    ),
    NEEDS_OPERATOR: (
        # Operator-authority edges: the operator is exempt from the autonomous scoring gate (they
        # ARE the authority). Routing a clarified task back to READY needs no score here — but it
        # still can't be autonomously drafted until scored, because READY→IN_PROGRESS is gated.
        _T(READY, frozenset({OPERATOR}), note="operator clarified → re-enter flow (re-scored before autonomous draft)"),
        _T(IN_PROGRESS, frozenset({OPERATOR}), note="operator fast-tracks drafting (exempt — operator authority)"),
        _T(DONE, frozenset({OPERATOR}), note="operator resolved directly (still a human merge)"),
        _T(SUPERSEDED, frozenset({OPERATOR})),
    ),
    DONE: (),          # terminal
    SUPERSEDED: (),    # terminal
}


def validate_transition(from_state: str, to_state: str, *, actor: str,
                        has_score: bool = False) -> bool:
    """Return True if the transition is legal for `actor`; raise TransitionError otherwise.

    Fail-closed: unknown states/actors and unlisted edges all raise. Enforces the two structural
    rules — only OPERATOR may move a task into DONE, and SCORED/READY need a recorded score.
    """
    if from_state not in STATES:
        raise TransitionError(f"unknown from-state: {from_state!r}")
    if to_state not in STATES:
        raise TransitionError(f"unknown to-state: {to_state!r}")
    if actor not in ACTORS:
        raise TransitionError(f"unknown actor: {actor!r}")
    for t in LEGAL_TRANSITIONS[from_state]:
        if t.to == to_state:
            if actor not in t.actors:
                raise TransitionError(
                    f"actor {actor!r} may not perform {from_state} → {to_state} "
                    f"(allowed: {sorted(t.actors)})")
            if t.requires_score and not has_score:
                raise TransitionError(
                    f"{from_state} → {to_state} requires a recorded DFTS score "
                    "(scoring is mandatory before autonomous drafting)")
            return True
    raise TransitionError(f"illegal transition: {from_state} → {to_state}")


def is_terminal(state: str) -> bool:
    return state in TERMINAL


def apply_transition(task: "Task", to_state: str, *, actor: str) -> "Task":
    """The blessed state mutator — the ONLY path that should move a Task between states.

    Derives `has_score` from the task itself (`task.score is not None`), so a caller can NOT assert
    a score it doesn't have (closing the `validate_transition(has_score=True)` bypass), validates
    the move (raising `TransitionError` on an illegal/unauthorized one), then sets `task.state`.
    Returns the same Task for chaining.

    Prefer this over writing `task.state` directly or calling `validate_transition` ad hoc: it
    makes the safe path the only path, so the human-at-merge invariant (only the operator reaches
    `Done`) and mandatory-scoring can't be skipped by a caller who forgets to validate. A future
    live driver MUST route programmatic board writes through here; `lint_todo` is the static-board
    backstop for hand edits (see framework/19 §1.1).
    """
    validate_transition(task.state, to_state, actor=actor, has_score=task.score is not None)
    task.state = to_state
    return task


# --- todo.md mapping + parsing (the only I/O) ------------------------------------------
# tasks/todo.md uses a deliberately smaller 5-value vocabulary (it is the operator's working
# board, not the full machine). These are the recognized values; everything else is a lint
# finding. The canonical 9-state machine above is the orchestration superset.
TODO_STATE_MAP = {
    "not started": BACKLOG,
    "in progress": IN_PROGRESS,
    "for review": FOR_REVIEW,
    "done": DONE,
    "superseded": SUPERSEDED,
}

_PRIORITY_BY_GLYPH = {"🔴": "critical", "🟡": "high", "🟢": "medium", "⚪": "low"}
_PRIORITY_RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0, "none": 0}
_DFTS_RE = re.compile(r"\bDFTS[:= ]\s*(\d+)", re.I)

# --- autonomy-routing policy (consumed by task_driver.route_scored) ---------------------
# DFTS 0,1,2,3 may be routed for autonomous DRAFTING; DFTS 4+ goes to a human (this matches the
# Delta-Force convene gate at >=4, framework/09 §3). The name encodes the boundary: autonomous iff
# score < AUTONOMOUS_DFTS_BELOW.
AUTONOMOUS_DFTS_BELOW = 4

# Rail backstop: a task whose title/category/notes hit any of these words is routed to the operator
# regardless of its DFTS score — a single operator-entered number must NOT be able to send
# safety-critical work down the autonomous-drafting path (Delta-Force Breaker finding). Word-level
# matched (re.findall), like the model_router/focus matching.
# Kept domain-specific to avoid false positives (NOT generic words like "rail"/"token" which collide
# with "no rails"/"design token"). Word-level matched against title+category+notes (lowercased).
RAIL_SIGNALS = frozenset({
    "auth", "authentication", "authorization", "security", "secret", "credential", "credentials",
    "vulnerability", "exploit", "injection", "permission", "permissions", "rls", "rbac",
    "oauth", "oauth2", "password", "passwords", "login", "encrypt", "encryption", "firewall",
    "apikey", "ciso", "aegis", "guardhouse", "killswitch", "schema", "schemas",
    "migration", "migrate", "datamodel", "billing", "payment", "payments", "stripe",
})
# Multi-word / hyphenated rails that word-level matching can't catch (e.g. "data model" tokenizes to
# {data, model}, neither a signal). Substring-matched against the lowercased title+category+notes.
# These were named as rails in the design but slipped to Ready until this fix (Regime-B audit).
RAIL_PHRASES = (
    "data model", "data-model", "kill switch", "access control", "private key", "api key", "api-key",
)
_MAX_PATH_LEN = 260  # ~Windows MAX_PATH; a longer str is treated as markdown content, not a path
# Strip only a SINGLE TRAILING parenthetical annotation (e.g. "Not Started (Operator)") + bold/
# code markers — NOT interior parens (stripping those fused "Do(x)ne" → "Done", a smuggle bug).
_STATUS_ANNOTATION_RE = re.compile(r"\s*\([^)]*\)\s*$")


@dataclass
class Task:
    title: str
    state: str               # canonical state (mapped); == raw_status if unrecognized
    raw_status: str          # the original Status cell, verbatim
    priority: str = "none"   # critical | high | medium | low | none
    category: str = ""
    notes: str = ""          # the Notes cell verbatim (carries "DFTS: N" + free-text)
    score: Optional[int] = None   # DFTS score if recorded in the row (Notes "DFTS: N")
    recognized: bool = True       # False if the Status value isn't in TODO_STATE_MAP

    @property
    def focus_hay(self) -> str:
        return f"{self.title} {self.category}".lower()


def _priority_from(cell: str) -> str:
    for glyph, name in _PRIORITY_BY_GLYPH.items():
        if glyph in cell:
            return name
    return "none"


def parse_todo(source) -> list[Task]:
    """Parse markdown task TABLES (rows with a Status column) out of a tasks/todo.md.

    `source` is a Path, a path-like string, or raw markdown text. Only rows from tables that have
    a `Status` header column are parsed (the prose status-log sections are skipped). Unrecognized
    Status values are kept with `recognized=False` so the lint can flag them — never coerced.
    """
    if isinstance(source, Path):
        text = source.read_text(encoding="utf-8", errors="replace")
    elif isinstance(source, str) and "\n" not in source and len(source) < _MAX_PATH_LEN and Path(source).is_file():
        text = Path(source).read_text(encoding="utf-8", errors="replace")
    else:
        text = str(source)
    tasks: list[Task] = []
    header: Optional[list[str]] = None
    col: dict[str, int] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if set(cells) <= {""} or all(set(c) <= {"-", ":"} for c in cells if c):
            continue  # separator row
        low = [c.lower() for c in cells]
        if "status" in low and ("task" in low or "item" in low):
            header = low
            col = {name: i for i, name in enumerate(low)}
            continue
        if header is None or len(cells) < len(header):
            continue
        status_cell = cells[col["status"]]
        title_idx = col.get("task", col.get("item", 0))
        title = re.sub(r"\*\*|`", "", cells[title_idx]).strip()
        if not title:
            continue
        raw = _STATUS_ANNOTATION_RE.sub("", status_cell.replace("*", "").replace("`", "")).strip()
        canonical = TODO_STATE_MAP.get(raw.lower())
        notes_cell = cells[col["notes"]] if "notes" in col else ""
        score_m = _DFTS_RE.search(notes_cell)
        tasks.append(Task(
            title=title,
            state=canonical or raw,
            raw_status=status_cell,
            priority=_priority_from(cells[col["priority"]]) if "priority" in col else "none",
            category=cells[col["category"]] if "category" in col else "",
            notes=notes_cell,
            score=int(score_m.group(1)) if score_m else None,
            recognized=canonical is not None,
        ))
    return tasks


def lint_todo(tasks: Sequence[Task]) -> list[dict]:
    """Return lint findings over parsed tasks. Pure. Each finding: {task, issue, detail}.

    Flags: (a) an unrecognized Status value (not in the 5-value todo vocabulary); (b) a row in an
    autonomous-drafting-eligible state with no recorded DFTS score (the "Ready without a score"
    smell — scoring is mandatory before drafting).

    SCOPE — what this does NOT do: it is a vocabulary/score smell-check, NOT a provenance
    backstop. It canNOT tell a legitimately-merged `Done` row from one a hand-edit/Routine wrote
    without ever passing the operator actor gate — that requires reconciling the board against
    `orchestrator-log.jsonl`, which is the live driver's + CI's job (framework/19 §1.1). Note (b)
    only ever fires for programmatically-constructed Tasks (or the future driver): `parse_todo`
    can't emit SCORED/READY because the markdown board's `TODO_STATE_MAP` has no such vocabulary.
    """
    findings: list[dict] = []
    for t in tasks:
        if not t.recognized:
            findings.append({"task": t.title, "issue": "unrecognized-status",
                             "detail": f"{t.raw_status!r} not in {sorted(set(TODO_STATE_MAP))}"})
        if t.state in (SCORED, READY) and t.score is None:
            findings.append({"task": t.title, "issue": "ready-without-score",
                             "detail": "autonomous-drafting state with no recorded DFTS score"})
    return findings


# --- Focus Mode + Routine selection (pure) ---------------------------------------------
_ACTIONABLE = frozenset({BACKLOG, PROPOSED, SCORED, READY, IN_PROGRESS})
# Mirrors token_accounting.GOALS (both sourced from config/token-economics.json "goal"); kept as a
# local copy rather than a cross-import to preserve the pure-module boundary. Keep them in sync.
_GOALS = frozenset({"save_budget", "balanced", "maximize_ai"})
_FOCUS_STOPWORDS = frozenset({"the", "and", "for", "with", "this", "that", "only",
                              "focus", "work", "into", "next", "all", "any", "new",
                              "let", "lets", "please", "should", "would"})


def select_actionable(tasks: Sequence[Task], *, focus: Optional[str] = None,
                      goal: Optional[str] = None) -> dict:
    """Filter + order the actionable queue for Focus Mode / Routine pick. Pure.

    `focus` is the operator's natural-language directive (e.g. "Library docs"); its alpha words are
    matched against the WORDS of each task's title+category (word-level, not substring — so "art"
    does not match "cartometrics"), surfacing only in-focus work. `goal` is the token-economics
    dial (config/token-economics.json): under `save_budget` the queue is conservative — only
    critical/high priority survive; `balanced`/`maximize_ai` are accepted for API symmetry with
    `token_accounting` but impose no extra queue filter here (only `save_budget` narrows). Ordering
    is priority desc, stable within a tier (preserves the operator's hand-ordering). Returns
    {selected, focus_terms, goal, dropped_for_focus, dropped_for_goal}.
    """
    if goal is not None and goal not in _GOALS:
        raise ValueError(f"unknown goal {goal!r}; expected one of {sorted(_GOALS)}")
    actionable = [t for t in tasks if t.state in _ACTIONABLE]
    focus_terms = sorted(set(re.findall(r"[a-z]{3,}", (focus or "").lower())) - _FOCUS_STOPWORDS)

    in_focus, dropped_focus = [], []
    for t in actionable:
        hay_words = set(re.findall(r"[a-z]+", t.focus_hay))   # word-level match, not substring
        if not focus_terms or any(term in hay_words for term in focus_terms):
            in_focus.append(t)
        else:
            dropped_focus.append(t.title)

    selected, dropped_goal = [], []
    for t in in_focus:
        if goal == "save_budget" and t.priority not in ("critical", "high"):
            dropped_goal.append(t.title)
        else:
            selected.append(t)

    selected.sort(key=lambda t: _PRIORITY_RANK.get(t.priority, 0), reverse=True)
    return {"selected": selected, "focus_terms": focus_terms, "goal": goal,
            "dropped_for_focus": dropped_focus, "dropped_for_goal": dropped_goal}
