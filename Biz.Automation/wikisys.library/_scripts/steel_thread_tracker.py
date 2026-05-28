"""Multi-layer feature manifest tracker.

P14 validator (v1.0). Reads `_config/steel_threads.yaml` (optional),
classifies each declared steel-thread by per-layer file-existence
check, and reports threads that are incomplete (zero layers on disk;
warning-class) or partial (some layers on disk; info-class). Complete
threads (all declared layers on disk) are suppressed from the findings
list and counted only in the summary line.

Spec contract: CODEX_BUILD_SPEC_v1_2.md §2.4 row 11 + §2.5 line 222
(thin spec — operator-pick schema + detection strategy).

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "findings": list[dict],
                "threads_scanned": int,
                "layers_present": int,
                "layers_total": int,
            }
        where each finding is:
            {
                "severity": "warning" | "info",
                "name": str,         # thread name
                "status": str,       # complete | partial | incomplete
                "layers_present": int,
                "layers_total": int,
                "layers": list[str], # declared layer paths
                "reason": str,
            }

Exit codes (in __main__):
    0 — clean run, no findings (all threads complete OR manifest empty).
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki, IO error, malformed manifest).

Config file:
    _config/steel_threads.yaml  OPTIONAL — wrapper-key flat-mapping
        idiom: top-level `threads:` block-style list of entries with
        flat keys {name: str (required), layers: [flow-list-of-str]
        (required), status: str (optional override)}. Loaded via
        _lib.config_loader.load_config_yaml (2nd wrapper-key consumer
        post-T8 promo). Absent file -> empty manifest, dashboard
        skeleton written, advisory WARN to stderr, _main rc=0.

Layer-coverage detection (Path A.1 per plan):
    Each declared `layers` path interpreted wiki-root-relative; file
    existence checked via `(wiki_root / layer_path).exists()`. No fm
    scan, no body scan, no strip_code dependency. Simplest deterministic.

Status enum:
    complete    — all declared layers exist on disk
    partial     — some declared layers exist, some missing
    incomplete  — zero layers exist OR no layers declared

Status override:
    A thread entry's `status:` field, when present AND value is one of
    {'complete', 'partial', 'incomplete'}, takes operator-override
    precedence over the auto-derived value. Invalid override values
    (or absent field) fall to auto-derivation.

Severity mapping:
    incomplete -> warning   (broken thread; actionable)
    partial    -> info      (in-progress thread; advisory)
    complete   -> suppressed (no finding emitted)
"""

import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Set

from _lib import dashboard
from _lib import cli
from _lib import frontmatter
from _lib.config_loader import ConfigYamlError, load_config_yaml


WIKI_ROOT = frontmatter.find_wiki_content_root()
DASHBOARD_RELATIVE = "_dashboards/steel_threads.md"
CONFIG_RELATIVE = "_config/steel_threads.yaml"

STATUS_COMPLETE = "complete"
STATUS_PARTIAL = "partial"
STATUS_INCOMPLETE = "incomplete"
VALID_STATUS: Set[str] = {STATUS_COMPLETE, STATUS_PARTIAL, STATUS_INCOMPLETE}

SEVERITY_FOR_STATUS: Dict[str, str] = {
    STATUS_INCOMPLETE: "warning",
    STATUS_PARTIAL: "info",
}

REASON_INCOMPLETE = "no declared layers exist on disk"
REASON_PARTIAL = "some declared layers exist; manifest is in progress"

WARN_MANIFEST_MISSING = (
    "warning: _config/steel_threads.yaml not found; empty manifest"
)


def run(wiki_root: Path) -> Dict[str, Any]:
    """Read steel-threads manifest, classify each, write the dashboard."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )

    threads, manifest_missing = _load_threads(wiki_root)
    findings: List[Dict[str, Any]] = []
    layers_present_total = 0
    layers_total = 0

    for entry in threads:
        classified = _classify_thread(wiki_root, entry)
        layers_present_total += classified["layers_present"]
        layers_total += classified["layers_total"]
        if classified["status"] == STATUS_COMPLETE:
            continue
        findings.append(classified)

    findings.sort(key=lambda f: (
        dashboard.SEVERITY_ORDER.index(f["severity"]),
        f["name"],
    ))

    content = _build_dashboard_markdown(
        findings, len(threads), layers_present_total, layers_total
    )
    dashboard_path = wiki_root / DASHBOARD_RELATIVE
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(content, encoding="utf-8")

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "threads_scanned": len(threads),
        "layers_present": layers_present_total,
        "layers_total": layers_total,
        "manifest_missing": manifest_missing,
    }


def _load_threads(wiki_root: Path):
    """Read `_config/steel_threads.yaml`; optional.

    Returns (threads_list, manifest_missing_bool). Missing file ->
    ([], True). Malformed yaml or wrapper-not-list -> ConfigYamlError
    propagates.
    """
    # S004 MI-18: discovery via frontmatter.find_config_dir() handles v1.0 +
    # v1.1 layouts.
    try:
        config_dir = frontmatter.find_config_dir(wiki_root)
        config_path = config_dir / "steel_threads.yaml"
    except FileNotFoundError:
        config_path = wiki_root / CONFIG_RELATIVE  # sentinel; will fail .exists()
    if not config_path.exists():
        return [], True
    threads = load_config_yaml(
        config_path,
        wrapper_key="threads",
        required_keys=("name", "layers"),
        entity_noun="steel thread",
    )
    return threads, False


def _classify_thread(
    wiki_root: Path, entry: Dict[str, Any]
) -> Dict[str, Any]:
    """Classify one thread entry into a finding-shaped dict."""
    name = str(entry["name"])
    raw_layers = entry.get("layers")
    if isinstance(raw_layers, list):
        layers = [str(p) for p in raw_layers]
    else:
        layers = []
    layers_present = sum(
        1 for p in layers if (wiki_root / p).exists()
    )
    layers_total = len(layers)
    auto_status = _auto_derive_status(layers_present, layers_total)
    override = entry.get("status")
    if isinstance(override, str) and override in VALID_STATUS:
        status = override
    else:
        status = auto_status
    if status == STATUS_COMPLETE:
        severity = None
        reason = ""
    elif status == STATUS_PARTIAL:
        severity = SEVERITY_FOR_STATUS[STATUS_PARTIAL]
        reason = REASON_PARTIAL
    else:
        severity = SEVERITY_FOR_STATUS[STATUS_INCOMPLETE]
        reason = REASON_INCOMPLETE
    return {
        "severity": severity,
        "name": name,
        "status": status,
        "layers_present": layers_present,
        "layers_total": layers_total,
        "layers": layers,
        "reason": reason,
    }


def _auto_derive_status(present: int, total: int) -> str:
    if total == 0:
        return STATUS_INCOMPLETE
    if present == 0:
        return STATUS_INCOMPLETE
    if present == total:
        return STATUS_COMPLETE
    return STATUS_PARTIAL


def _build_dashboard_markdown(
    findings: List[Dict[str, Any]],
    threads_scanned: int,
    layers_present: int,
    layers_total: int,
) -> str:
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header(
        "Steel Threads Dashboard", today=today
    ))
    lines.append("")
    lines.append("# Steel Threads - " + today)
    lines.append("")
    lines.append("**Threads scanned:** " + str(threads_scanned))
    lines.append(
        "**Layers on disk:** {}/{}".format(layers_present, layers_total)
    )
    sev_counts = {sev: 0 for sev in dashboard.SEVERITY_ORDER}
    for f in findings:
        sev_counts[f["severity"]] += 1
    counts_strs = []
    for sev in dashboard.SEVERITY_ORDER:
        n = sev_counts[sev]
        counts_strs.append("{} {}{}".format(n, sev, "s" if n != 1 else ""))
    lines.append(
        "**Findings:** {} ({})".format(len(findings), " / ".join(counts_strs))
    )
    lines.append("")

    if not findings:
        lines.append("No steel thread findings.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Findings")
    for f in findings:
        lines.append(_render_finding_line(f))
    lines.append("")
    return "\n".join(lines)


def _render_finding_line(f: Dict[str, Any]) -> str:
    layers_text = ", ".join(f["layers"]) if f["layers"] else "<none>"
    return (
        "- {severity}: {name}: {status} ({present}/{total} layers on disk): "
        "layers=[{layers_text}]"
    ).format(
        severity=f["severity"],
        name=f["name"],
        status=f["status"],
        present=f["layers_present"],
        total=f["layers_total"],
        layers_text=layers_text,
    )


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
            "error: steel_threads.yaml is structurally malformed: {}".format(exc),
            file=stderr,
        )
        return 2
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=stderr)
        return 2

    if summary["manifest_missing"]:
        print(WARN_MANIFEST_MISSING, file=stderr)

    findings = summary["findings"]
    for f in findings:
        print(dashboard.strip_finding_bullet(_render_finding_line(f)), file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    print(
        "steel_threads: threads_scanned={} layers={}/{} findings={} -> {}".format(
            summary["threads_scanned"],
            summary["layers_present"],
            summary["layers_total"],
            len(findings),
            rel,
        ),
        file=stdout,
    )
    return 1 if findings else 0


if __name__ == "__main__":
    WIKI_ROOT = cli.resolve_cli_wiki_root(WIKI_ROOT)
    sys.exit(_main(WIKI_ROOT))
