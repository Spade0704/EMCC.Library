"""Snapshot + diff of `_canon/*.yaml` over time.

P15 validator. Reads the current state of the 4 canon files
(counts / roster / taxonomy / timeline) and compares against the
latest snapshot under `_canon/.snapshots/<iso8601>/`. Emits findings
per change-class (add / remove / modify) at entity-level granularity.
Optional `--snapshot` flag writes a new snapshot before diffing.

Spec contract: CODEX_BUILD_SPEC_v1_2.md §2.4 row 12 (snapshot + diff
of `_canon/` over time).

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "findings": list[dict],
                "baseline_snapshot_id": str | None,
                "current_canon_files": int,
                "baseline_missing": bool,
            }
        where each finding is:
            {
                "severity": "info",
                "change_class": "add" | "remove" | "modify",
                "canon_file": str,
                "entity": str,
                "baseline_value": dict | None,
                "current_value": dict | None,
                "changed_fields": list[str] | None,
                "reason": str,
            }

Exit codes (in __main__):
    0 — clean run, no findings (or first-run empty-baseline).
    1 — drift findings present (dashboard still written).
    2 — script-level error (missing wiki, IO error, malformed canon yaml).

Snapshot layout (Option (a) — source-adjacent dot-prefix; spec §2.2
constraint preserves zero-amendment minimum-touch path):
    <wiki>/_canon/.snapshots/<YYYY-MM-DDTHH-MM-SSZ>/<file>.yaml

Diff algorithm:
    Structural per-key entity-level. Per canon file: build
    `{lookup_key_value: entry_dict}` for current + baseline via
    `_lib.config_loader.load_config_yaml`; compute key-set diff.
    Modify finding cites `changed_fields` list (entries present in
    both but with at least one differing field).
"""

import argparse
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from _lib import dashboard
from _lib import frontmatter
from _lib.config_loader import ConfigYamlError, load_config_yaml


WIKI_ROOT = frontmatter.find_wiki_root()
DASHBOARD_RELATIVE = "_dashboards/canon_drift.md"
SNAPSHOT_BASE_RELATIVE = "_canon/.snapshots"

CANON_LOOKUP: Dict[str, Dict[str, Any]] = {
    "counts": {
        "wrapper_key": "counts",
        "lookup_key": "name",
        "required_keys": ("name",),
    },
    "roster": {
        "wrapper_key": "entities",
        "lookup_key": "canonical_name",
        "required_keys": ("canonical_name",),
    },
    "taxonomy": {
        "wrapper_key": "categories",
        "lookup_key": "name",
        "required_keys": ("name",),
    },
    "timeline": {
        "wrapper_key": "events",
        "lookup_key": "name",
        "required_keys": ("name",),
    },
}

CHANGE_ADD = "add"
CHANGE_REMOVE = "remove"
CHANGE_MODIFY = "modify"
CHANGE_CLASS_ORDER: Tuple[str, ...] = (CHANGE_ADD, CHANGE_REMOVE, CHANGE_MODIFY)
CHANGE_CLASS_LABEL: Dict[str, str] = {
    CHANGE_ADD: "Added",
    CHANGE_REMOVE: "Removed",
    CHANGE_MODIFY: "Modified",
}

REASON_ENTITY_ADDED = "entity present in current state but absent in baseline"
REASON_ENTITY_REMOVED = "entity present in baseline but absent in current state"
REASON_ENTITY_MODIFIED = "entity present in both states but at least one field differs"

WARN_NO_BASELINE = (
    "warning: _canon/.snapshots/ empty; run with --snapshot to establish baseline"
)


def run(wiki_root: Path) -> Dict[str, Any]:
    """Read current canon state + latest snapshot, diff, write dashboard."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )

    current_state = _load_canon_state(wiki_root)
    baseline_snapshot_id, baseline_state = _read_latest_snapshot(wiki_root)
    baseline_missing = baseline_snapshot_id is None

    findings: List[Dict[str, Any]] = []
    if not baseline_missing:
        findings = _diff_state(baseline_state, current_state)

    findings.sort(key=_finding_sort_key)

    content = _build_dashboard_markdown(
        findings,
        baseline_snapshot_id,
        baseline_missing,
        current_canon_files=len([f for f in CANON_LOOKUP if f in current_state]),
    )
    dashboard_path = dashboard.write_dashboard(wiki_root, DASHBOARD_RELATIVE, content)

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "baseline_snapshot_id": baseline_snapshot_id,
        "baseline_missing": baseline_missing,
        "current_canon_files": len([f for f in CANON_LOOKUP if f in current_state]),
    }


def _load_canon_state(wiki_root: Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Load each `_canon/<file>.yaml` if present; return {file_stem: {lookup: entry}}.

    Missing canon file omitted from result (key absent). load_config_yaml
    handles per-entry required_keys WARN-skip semantics.

    S004 MI-18: discovery via frontmatter.find_canon_dir() handles v1.0 +
    v1.1 layouts. Missing canon dir -> empty state.
    """
    try:
        canon_dir = frontmatter.find_canon_dir(wiki_root)
    except FileNotFoundError:
        return {}
    return _load_state_from_dir(canon_dir, entries_only=True)


def _read_latest_snapshot(
    wiki_root: Path,
) -> Tuple[Optional[str], Dict[str, Dict[str, Dict[str, Any]]]]:
    """Find latest snapshot dir (ISO8601 lex-sort); load its canon state.

    Returns (snapshot_id, state) or (None, {}) when no snapshot exists.
    """
    base = wiki_root / SNAPSHOT_BASE_RELATIVE
    if not base.is_dir():
        return None, {}
    subdirs = sorted(p for p in base.iterdir() if p.is_dir())
    if not subdirs:
        return None, {}
    latest = subdirs[-1]
    state = _load_state_from_dir(latest, entries_only=True)
    return latest.name, state


def _load_state_from_dir(
    canon_dir: Path, entries_only: bool
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Load all canon yaml files in `canon_dir`; return {file_stem: {lookup: entry}}.

    `entries_only` reserved for future extensibility (kept for symmetry
    with possible per-file metadata loading; currently always True).
    """
    state: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for file_stem, spec in CANON_LOOKUP.items():
        path = canon_dir / "{}.yaml".format(file_stem)
        if not path.exists():
            continue
        entries = load_config_yaml(
            path,
            wrapper_key=spec["wrapper_key"],
            required_keys=spec["required_keys"],
            entity_noun="canon entry",
        )
        lookup_key = spec["lookup_key"]
        state[file_stem] = {
            str(entry[lookup_key]): entry for entry in entries
        }
    return state


def _diff_state(
    baseline: Dict[str, Dict[str, Dict[str, Any]]],
    current: Dict[str, Dict[str, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Compute structural per-key entity-level diff."""
    findings: List[Dict[str, Any]] = []
    file_stems = sorted(set(CANON_LOOKUP) & (set(baseline) | set(current)))
    for file_stem in file_stems:
        base_entries = baseline.get(file_stem, {})
        curr_entries = current.get(file_stem, {})
        added_keys = sorted(set(curr_entries) - set(base_entries))
        removed_keys = sorted(set(base_entries) - set(curr_entries))
        common_keys = sorted(set(base_entries) & set(curr_entries))
        for key in added_keys:
            findings.append({
                "severity": "info",
                "change_class": CHANGE_ADD,
                "canon_file": file_stem,
                "entity": key,
                "baseline_value": None,
                "current_value": curr_entries[key],
                "changed_fields": None,
                "reason": REASON_ENTITY_ADDED,
            })
        for key in removed_keys:
            findings.append({
                "severity": "info",
                "change_class": CHANGE_REMOVE,
                "canon_file": file_stem,
                "entity": key,
                "baseline_value": base_entries[key],
                "current_value": None,
                "changed_fields": None,
                "reason": REASON_ENTITY_REMOVED,
            })
        for key in common_keys:
            base_entry = base_entries[key]
            curr_entry = curr_entries[key]
            changed = _diff_entry_fields(base_entry, curr_entry)
            if not changed:
                continue
            findings.append({
                "severity": "info",
                "change_class": CHANGE_MODIFY,
                "canon_file": file_stem,
                "entity": key,
                "baseline_value": base_entry,
                "current_value": curr_entry,
                "changed_fields": changed,
                "reason": REASON_ENTITY_MODIFIED,
            })
    return findings


def _diff_entry_fields(
    base_entry: Dict[str, Any], curr_entry: Dict[str, Any]
) -> List[str]:
    """Return sorted list of field names that differ between two entries."""
    all_fields = set(base_entry) | set(curr_entry)
    changed: List[str] = []
    for field in sorted(all_fields):
        if base_entry.get(field) != curr_entry.get(field):
            changed.append(field)
    return changed


def _finding_sort_key(f: Dict[str, Any]) -> Tuple[int, str, str]:
    return (
        CHANGE_CLASS_ORDER.index(f["change_class"]),
        f["canon_file"],
        f["entity"],
    )


def _build_dashboard_markdown(
    findings: List[Dict[str, Any]],
    baseline_snapshot_id: Optional[str],
    baseline_missing: bool,
    current_canon_files: int,
) -> str:
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header(
        "Canon Drift Dashboard", today=today
    ))
    lines.append("")
    lines.append("# Canon Drift - " + today)
    lines.append("")
    lines.append("**Canon files in current state:** " + str(current_canon_files))
    lines.append(
        "**Baseline snapshot:** "
        + (baseline_snapshot_id if baseline_snapshot_id else "(none)")
    )
    counts = {cls: 0 for cls in CHANGE_CLASS_ORDER}
    for f in findings:
        counts[f["change_class"]] += 1
    counts_strs = []
    for cls in CHANGE_CLASS_ORDER:
        counts_strs.append("{} {}".format(counts[cls], cls))
    lines.append(
        "**Findings:** {} ({})".format(len(findings), " / ".join(counts_strs))
    )
    lines.append("")

    if not findings:
        if baseline_missing:
            lines.append("No prior snapshot found; baseline empty.")
        else:
            lines.append("No canon drift detected since baseline.")
        lines.append("")
        return "\n".join(lines)

    by_class: Dict[str, List[Dict[str, Any]]] = {cls: [] for cls in CHANGE_CLASS_ORDER}
    for f in findings:
        by_class[f["change_class"]].append(f)

    for cls in CHANGE_CLASS_ORDER:
        bucket = by_class[cls]
        if not bucket:
            continue
        lines.append("## " + CHANGE_CLASS_LABEL[cls])
        for f in bucket:
            lines.append(_render_finding_line(f))
        lines.append("")
    return "\n".join(lines)


def _render_finding_line(f: Dict[str, Any]) -> str:
    if f["change_class"] == CHANGE_MODIFY:
        fields_text = (
            ",".join(f["changed_fields"]) if f["changed_fields"] else ""
        )
        return (
            "- {severity}: {canon_file}: {entity}: fields=[{fields_text}]: {reason}"
        ).format(
            severity=f["severity"],
            canon_file=f["canon_file"],
            entity=f["entity"],
            fields_text=fields_text,
            reason=f["reason"],
        )
    return (
        "- {severity}: {canon_file}: {entity}: {reason}"
    ).format(
        severity=f["severity"],
        canon_file=f["canon_file"],
        entity=f["entity"],
        reason=f["reason"],
    )


def _write_snapshot(wiki_root: Path) -> Optional[str]:
    """Create a new snapshot dir + byte-copy each canon yaml into it.

    Returns the snapshot id (ISO8601 UTC subdir name). NTFS-colon-
    illegal-filename swap applied per 2026-05-07 lesson + lattice-bridge
    filename convention.
    """
    # S004 MI-18: discovery via frontmatter.find_canon_dir() handles v1.0 +
    # v1.1 layouts.
    try:
        canon_dir = frontmatter.find_canon_dir(wiki_root)
    except FileNotFoundError:
        return None
    snapshot_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    target = wiki_root / SNAPSHOT_BASE_RELATIVE / snapshot_id
    target.mkdir(parents=True, exist_ok=True)
    for file_stem in CANON_LOOKUP:
        src = canon_dir / "{}.yaml".format(file_stem)
        if not src.exists():
            continue
        shutil.copy2(src, target / "{}.yaml".format(file_stem))
    return snapshot_id


def _main(wiki_root, argv=None, stdout=None, stderr=None):
    """CLI entry-point body. Returns exit code; lets callers test without subprocess."""
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    wiki_root = Path(wiki_root)
    parser = argparse.ArgumentParser(prog="build_canon_drift_report")
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Write a new snapshot under _canon/.snapshots/ before diffing.",
    )
    args = parser.parse_args(argv if argv is not None else [])

    try:
        if args.snapshot:
            snapshot_id = _write_snapshot(wiki_root)
            if snapshot_id is not None:
                print(
                    "canon_drift: wrote snapshot {}".format(snapshot_id),
                    file=stdout,
                )
        summary = run(wiki_root)
    except ConfigYamlError as exc:
        print(
            "error: canon yaml is structurally malformed: {}".format(exc),
            file=stderr,
        )
        return 2
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=stderr)
        return 2

    if summary["baseline_missing"]:
        print(WARN_NO_BASELINE, file=stderr)

    findings = summary["findings"]
    for f in findings:
        print(dashboard.strip_finding_bullet(_render_finding_line(f)), file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    print(
        "canon_drift: canon_files={} baseline={} findings={} -> {}".format(
            summary["current_canon_files"],
            summary["baseline_snapshot_id"] or "(none)",
            len(findings),
            rel,
        ),
        file=stdout,
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(_main(WIKI_ROOT, sys.argv[1:]))
