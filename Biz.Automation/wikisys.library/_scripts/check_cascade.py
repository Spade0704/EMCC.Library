"""Validate cascade staleness — source -> derived doc mtime comparison.

P10 validator. Reads `_config/cascade_map.yaml`, enumerates source -> derived
pairs, stats both paths, classifies findings into 3 severity bands per
spec §2.4 row 6 + S034-T7 contract:

    error   cascade_map references source path not on disk (config drift)
    warning derived path missing while source exists (broken cascade pipe)
    info    source.stat().st_mtime > derived.stat().st_mtime AND both exist
            (stale derived; refresh needed but no broken pipe)

Writes a markdown dashboard at `_dashboards/cascade.md`. Pairs whose source
exists, derived exists, and source.mtime <= derived.mtime are fresh (no
finding emitted).

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "findings": list[dict],
                "pairs_scanned": int,
            }
        where each finding is:
            {
                "severity": "error" | "warning" | "info",
                "source_path": str,    # wiki-root-relative, forward-slash
                "derived_path": str,   # wiki-root-relative, forward-slash
                "reason": str,         # human-readable
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki, structurally malformed
        cascade_map.yaml, IO error).

`_config/cascade_map.yaml` schema:
    pairs:
      - source: <wiki-root-relative path>
        derived: <wiki-root-relative path>

Consumes `_lib.dashboard` primitives (T6 promotion gate validation):
    `render_fm_header` (1 call-site), `SEVERITY_ORDER` (4 call-sites:
    sort key + group_by_fixed_order arg + counts-line iteration +
    section-render iteration), `group_by_fixed_order` (1 call-site).
"""

import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from _lib import dashboard
from _lib import frontmatter
from _lib.config_loader import ConfigYamlError, load_config_yaml


WIKI_ROOT = frontmatter.find_wiki_root()
DASHBOARD_RELATIVE = "_dashboards/cascade.md"
CONFIG_RELATIVE = "_config/cascade_map.yaml"

REASON_SOURCE_MISSING = "cascade_map source path not on disk (config drift)"
REASON_DERIVED_MISSING = "derived path not on disk while source exists"
REASON_STALE = "source mtime exceeds derived mtime (refresh needed)"


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk cascade_map pairs, compare mtimes, write the dashboard."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )
    pairs = _load_cascade_map(wiki_root)
    findings: List[Dict[str, str]] = []
    for pair in pairs:
        finding = _classify_pair(wiki_root, pair)
        if finding is not None:
            findings.append(finding)

    findings.sort(key=lambda f: (
        dashboard.SEVERITY_ORDER.index(f["severity"]),
        f["source_path"],
    ))

    content = _build_dashboard_markdown(findings, len(pairs))
    dashboard_path = wiki_root / DASHBOARD_RELATIVE
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(content, encoding="utf-8")

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "pairs_scanned": len(pairs),
    }


def _load_cascade_map(wiki_root: Path) -> List[Dict[str, str]]:
    """Read `_config/cascade_map.yaml`; return list of validated pair dicts.

    Missing file -> []. Per-pair malformation (non-mapping, missing keys)
    -> skipped with stderr WARN; valid pairs still applied. Structural
    YAML failure or top-level `pairs` not a list propagates
    `ConfigYamlError` to the caller. Mirrors P6/P8 yaml-loading convention.
    """
    raw_pairs = load_config_yaml(
        wiki_root / CONFIG_RELATIVE,
        wrapper_key="pairs",
        required_keys=("source", "derived"),
        entity_noun="pair",
    )
    return [
        {"source": str(raw["source"]), "derived": str(raw["derived"])}
        for raw in raw_pairs
    ]


def _classify_pair(
    wiki_root: Path, pair: Dict[str, str]
) -> Optional[Dict[str, str]]:
    """Classify one pair into a finding dict or None if fresh.

    Order: error (source missing) > warning (derived missing) > info
    (stale). Returns None when source exists, derived exists, and
    source.mtime <= derived.mtime.
    """
    source = wiki_root / pair["source"]
    derived = wiki_root / pair["derived"]
    source_exists = source.exists()
    derived_exists = derived.exists()

    if not source_exists:
        return {
            "severity": "error",
            "source_path": pair["source"],
            "derived_path": pair["derived"],
            "reason": REASON_SOURCE_MISSING,
        }
    if not derived_exists:
        return {
            "severity": "warning",
            "source_path": pair["source"],
            "derived_path": pair["derived"],
            "reason": REASON_DERIVED_MISSING,
        }
    if source.stat().st_mtime > derived.stat().st_mtime:
        return {
            "severity": "info",
            "source_path": pair["source"],
            "derived_path": pair["derived"],
            "reason": REASON_STALE,
        }
    return None


def _build_dashboard_markdown(
    findings: List[Dict[str, str]], pairs_scanned: int
) -> str:
    today = date.today().isoformat()
    by_severity = dashboard.group_by_fixed_order(
        findings, dashboard.SEVERITY_ORDER, lambda f: f["severity"]
    )

    lines = list(dashboard.render_fm_header(
        "Cascade Staleness Dashboard", today=today
    ))
    lines.append("")
    lines.append("# Cascade Staleness — " + today)
    lines.append("")
    lines.append("**Pairs scanned:** " + str(pairs_scanned))
    counts = []
    for sev in dashboard.SEVERITY_ORDER:
        n = len(by_severity[sev])
        counts.append("{} {}{}".format(n, sev, "s" if n != 1 else ""))
    lines.append(
        "**Findings:** {} ({})".format(len(findings), " / ".join(counts))
    )
    lines.append("")

    if not findings:
        lines.append("No cascade staleness findings.")
        lines.append("")
        return "\n".join(lines)

    for sev in dashboard.SEVERITY_ORDER:
        bucket = by_severity[sev]
        if not bucket:
            continue
        lines.append("## " + sev)
        for f in bucket:
            lines.append("- {}: {} -> {}: {}".format(
                sev, f["source_path"], f["derived_path"], f["reason"]
            ))
        lines.append("")
    return "\n".join(lines)


def _main(wiki_root, stdout=None, stderr=None):
    """CLI entry-point body. Returns exit code; lets callers test without subprocess."""
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    wiki_root = Path(wiki_root)
    try:
        summary = run(wiki_root)
    except ConfigYamlError as exc:
        print(
            "error: cascade_map.yaml is structurally malformed: {}".format(exc),
            file=stderr,
        )
        return 2
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=stderr)
        return 2

    findings = summary["findings"]
    for f in findings:
        print("{}: {} -> {}: {}".format(
            f["severity"], f["source_path"], f["derived_path"], f["reason"]
        ), file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    print("cascade: pairs_scanned={} findings={} -> {}".format(
        summary["pairs_scanned"],
        len(findings),
        rel,
    ), file=stdout)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(_main(WIKI_ROOT))
