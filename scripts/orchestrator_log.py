#!/usr/bin/env python3
"""Append-only audit log for Orchestrator cross-session envelopes.

claude-peers carries envelopes as schema-less message bodies; this helper recovers
the audit trail by appending every sent/received envelope as one JSON line to
``tasks/orchestrator-log.jsonl`` (per-repo, gitignored or committed per project policy).

See framework/09-orchestrator-cross-session.md §4.1. Stdlib only (matches the
Lattice/Codex stdlib-only discipline); pathlib everywhere; safe to call from any repo.

Usage (CLI):
    python scripts/orchestrator_log.py --direction sent --envelope '{"envelope_type": "directive_assignment", ...}'
    python scripts/orchestrator_log.py --direction received --envelope-file /tmp/env.json

Usage (import):
    from orchestrator_log import log_envelope
    log_envelope(envelope_dict, direction="sent")
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG = Path("tasks") / "orchestrator-log.jsonl"


def log_envelope(envelope: dict, direction: str, log_path: Path | None = None) -> Path:
    """Append one envelope record to the JSONL audit log. Returns the log path.

    direction is "sent" or "received". The record wraps the raw envelope with a
    receive/send timestamp and direction so the log reconstructs the full exchange.
    """
    if direction not in ("sent", "received"):
        raise ValueError(f"direction must be 'sent' or 'received', got {direction!r}")
    path = log_path or DEFAULT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "direction": direction,
        "envelope": envelope,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Append an Orchestrator envelope to the audit log.")
    parser.add_argument("--direction", required=True, choices=("sent", "received"))
    parser.add_argument("--envelope", help="Envelope JSON as a string.")
    parser.add_argument("--envelope-file", help="Path to a file containing envelope JSON.")
    parser.add_argument("--log-path", help="Override the default tasks/orchestrator-log.jsonl path.")
    args = parser.parse_args(argv)

    if bool(args.envelope) == bool(args.envelope_file):
        parser.error("provide exactly one of --envelope or --envelope-file")

    raw = args.envelope if args.envelope else Path(args.envelope_file).read_text(encoding="utf-8")
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError as exc:
        parser.error(f"envelope is not valid JSON: {exc}")

    log_path = Path(args.log_path) if args.log_path else None
    written = log_envelope(envelope, direction=args.direction, log_path=log_path)
    print(f"logged {args.direction} envelope -> {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
