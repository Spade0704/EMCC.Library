"""route_inbox.py (S002 P0) — half-script / half-agent contract for 0-Inbox sort.

Per `tasks/plans/portfolio-folder-structure-spec.md` section (d) "New
scripts" Inbox-Sort operation (S002 B7 Librarian extension).

Two-phase contract:

    Phase 1: `python route_inbox.py scan --root <projectroot>`
        Enumerates `<root>/0-Inbox/` contents and writes a per-file
        manifest at `<root>/route_candidates.json`. Each entry carries
        deterministic metadata (filename, extension, size, mtime, sha256
        first-N-bytes). Librarian agent reads this manifest and
        populates each entry's `destination` field with the resolved
        target zone (wiki / tasks / assets / website / code) and the
        full target path.

    Phase 2: `python route_inbox.py execute --manifest <path>`
        Reads the populated manifest and applies the moves
        mechanically (mkdir target parent, mv source → destination).
        Refuses to execute if any entry has `destination: null`.

The split is deliberate: classification is semantic (agent's job);
file movement is mechanical (script's job).

Exit codes:
    0  success (scan emitted manifest; or execute applied all moves)
    1  partial failure (e.g. some moves failed during execute)
    2  malformed input (unparseable manifest JSON, or a top-level value that
       is not a list, during execute). Per-entry null destinations are NOT a
       hard error: they are reported as status="skipped" in the report.
    3  inbox not found / not a directory
"""
# @component Codex[ingest]

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def scan_inbox(inbox: Path) -> List[Dict[str, Any]]:
    """Walk inbox; return manifest entries (destination empty for agent)."""
    entries: List[Dict[str, Any]] = []
    if not inbox.is_dir():
        return entries
    for entry in sorted(inbox.iterdir()):
        if entry.name in (".gitkeep",) or entry.name.startswith("."):
            continue
        if not entry.is_file():
            continue
        try:
            stat = entry.stat()
            first_bytes = entry.read_bytes()[:4096]
            digest = hashlib.sha256(first_bytes).hexdigest()
        except OSError:
            digest = ""
            stat = None
        entries.append({
            "filename": entry.name,
            "source_abs": str(entry.resolve()),
            "size_bytes": stat.st_size if stat else None,
            "mtime_iso": _format_mtime(stat.st_mtime) if stat else None,
            "extension": entry.suffix,
            "sha256_first_4kb": digest,
            "destination": None,            # Librarian fills this in
            "destination_zone": None,       # Librarian fills (wiki/tasks/assets/website/code)
            "rationale": None,              # Librarian fills (one-line "why this zone")
        })
    return entries


def _format_mtime(ts: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _within_root(candidate: str, root: Path) -> bool:
    """True if `candidate` resolves to a path inside `root` (inclusive).

    Fail-closed confinement helper for execute (audit B3): manifest
    `destination` / `source_abs` values are agent-populated and could point
    at arbitrary absolute paths. A path that does not resolve under `root`
    is rejected by the caller (skipped + flagged), never moved.
    """
    try:
        Path(candidate).resolve().relative_to(root)
        return True
    except ValueError:
        return False


def execute_manifest(manifest_path: Path,
                     root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Apply moves per manifest; return per-entry result records.

    `root` confines every move to the project tree (audit B3): both the
    entry `destination` and `source_abs` must resolve INSIDE `root`, else the
    entry is skipped + flagged (never aborts the whole run). When `root` is
    None it defaults to the manifest's parent directory — the manifest is
    emitted at `<root>/route_candidates.json` by scan, so its parent IS the
    scan root.
    """
    confine_root = (root or manifest_path.parent).resolve()
    text = manifest_path.read_text(encoding="utf-8")
    entries = json.loads(text)
    if not isinstance(entries, list):
        raise json.JSONDecodeError(
            "manifest top-level value is not a list", text, 0
        )
    results: List[Dict[str, Any]] = []
    for entry in entries:
        dest = entry.get("destination")
        src_abs = entry.get("source_abs")
        if not dest:
            results.append({**entry, "status": "skipped", "reason": "destination null"})
            continue
        # Confinement gate (audit B3): destination + source must stay inside
        # the project tree. Skip + flag an escaping entry; do not abort.
        if not _within_root(dest, confine_root):
            reason = "destination escapes root {}: {}".format(confine_root, dest)
            sys.stderr.write("warning: skipping entry — {}\n".format(reason))
            results.append({**entry, "status": "skipped", "reason": reason})
            continue
        if src_abs and not _within_root(src_abs, confine_root):
            reason = "source escapes root {}: {}".format(confine_root, src_abs)
            sys.stderr.write("warning: skipping entry — {}\n".format(reason))
            results.append({**entry, "status": "skipped", "reason": reason})
            continue
        src = Path(src_abs) if src_abs else None
        if src is None or not src.exists():
            results.append({**entry, "status": "failed", "reason": "source missing"})
            continue
        dst = Path(dest)
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            results.append({**entry, "status": "moved", "destination_resolved": str(dst.resolve())})
        except Exception as exc:
            results.append({
                **entry,
                "status": "failed",
                "reason": "{}: {}".format(type(exc).__name__, exc),
            })
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="route_inbox.py")
    sub = parser.add_subparsers(dest="phase", required=True)

    scan_p = sub.add_parser("scan", help="Phase 1: enumerate 0-Inbox + emit manifest.")
    scan_p.add_argument("--root", type=Path, default=Path.cwd())
    scan_p.add_argument("--manifest", type=Path, default=None,
                        help="Output manifest path (default <root>/route_candidates.json).")

    exec_p = sub.add_parser("execute", help="Phase 2: apply moves per manifest.")
    exec_p.add_argument("--manifest", type=Path, required=True)
    exec_p.add_argument("--report", type=Path, default=None,
                        help="Output execution report path (default <manifest>.report.json).")

    args = parser.parse_args(argv)

    if args.phase == "scan":
        root = args.root.resolve()
        inbox = root / "0-Inbox"
        if not inbox.is_dir():
            sys.stderr.write("error: {} not a directory\n".format(inbox))
            return 3
        entries = scan_inbox(inbox)
        manifest_path = args.manifest or (root / "route_candidates.json")
        manifest_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        sys.stdout.write("Manifest written: {}\n".format(manifest_path))
        sys.stdout.write("Inbox entries: {}\n".format(len(entries)))
        return 0

    # phase == "execute"
    manifest_path = args.manifest
    if not manifest_path.is_file():
        sys.stderr.write("error: manifest not found: {}\n".format(manifest_path))
        return 2
    try:
        results = execute_manifest(manifest_path, root=manifest_path.resolve().parent)
    except json.JSONDecodeError as exc:
        sys.stderr.write("error: malformed manifest JSON: {}\n".format(exc))
        return 2
    failed = [r for r in results if r["status"] == "failed"]
    moved = [r for r in results if r["status"] == "moved"]
    skipped = [r for r in results if r["status"] == "skipped"]
    report_path = args.report or manifest_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    sys.stdout.write("Report written: {}\n".format(report_path))
    sys.stdout.write("Moved: {} | Skipped: {} | Failed: {}\n".format(
        len(moved), len(skipped), len(failed)
    ))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
