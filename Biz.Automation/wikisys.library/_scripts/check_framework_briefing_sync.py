"""Validate framework ↔ public-pair briefing-sync staleness.

P11 validator. Walks content pages, filters `type: framework` AND
non-null `public_pair` fm fields, resolves public_pair path
(wiki-root-relative), stats both, classifies findings into 3 severity
bands per spec §2.4 row 8 + S034-T9 contract:

    error   public_pair declared in framework fm but file not on disk
            (broken pair contract; pair declaration points at nothing)
    warning framework.mtime > public_pair.mtime (STALE BRIEFING — primary
            real-world finding class per spec §1 line 64 'a framework
            changed, but its briefing guide is still last quarter's
            version')
    info    public_pair.mtime > framework.mtime (briefing newer than
            framework; spec Principle #4 'Source -> Derived -> Wiki.
            NEVER reverse' directional-cascade candidate violation —
            info-class because briefing-drafting cycles may legitimately
            produce this transiently)

Writes a markdown dashboard at `_dashboards/framework_briefing_sync.md`.
Framework pages with public_pair.mtime == framework.mtime are fresh
(no finding emitted). Non-framework pages and framework-with-null-or-
missing-public_pair pages are skipped silently.

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "findings": list[dict],
                "frameworks_scanned": int,
            }
        where each finding is:
            {
                "severity": "error" | "warning" | "info",
                "framework_path": str,   # wiki-root-relative forward-slash
                "public_pair_path": str, # wiki-root-relative forward-slash
                "reason": str,           # human-readable
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki, IO error).

Page fm contract (per spec §2.3):
    type: framework | reference | guide | ...
    public_pair: "<wiki-root-relative path>" | null

Consumes (T6/P1/T8.5 promotions):
    `_lib.dashboard` — render_fm_header (1 call-site), SEVERITY_ORDER
        (4 call-sites: sort key + group_by_fixed_order arg + counts-line
        + section-render), group_by_fixed_order (1 call-site).
    `_lib.frontmatter.load_page` — 1 call-site (per-page in scan loop).
    `_lib.markdown.iter_content_pages` — 1 call-site (outer page-walk).

NO `_lib.config_loader` consumption — P11 reads page fm, NOT
_config/*.yaml (S034-T9 R2 DISCIPLINE-3 EXHIBIT: pre-dispatch
fact-check + plan-stage independent verification reverted T8
Craftsman+Auditor next_risk INCORRECT claim).
"""

import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from _lib import dashboard
from _lib import frontmatter
from _lib import markdown


WIKI_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_RELATIVE = "_dashboards/framework_briefing_sync.md"

REASON_PAIR_MISSING = "public_pair declared but target file not on disk"
REASON_STALE_BRIEFING = "framework mtime exceeds public_pair mtime (stale briefing)"
REASON_REVERSE_CASCADE = "public_pair mtime exceeds framework mtime (reverse cascade)"


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk content pages, filter framework+public_pair, write the dashboard."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )
    findings: List[Dict[str, str]] = []
    frameworks_scanned = 0
    for page_path in markdown.iter_content_pages(wiki_root):
        page = frontmatter.load_page(page_path)
        fm = page["frontmatter"]
        if fm.get("type") != "framework":
            continue
        public_pair = fm.get("public_pair")
        if not public_pair:
            continue
        frameworks_scanned += 1
        finding = _classify_pair(wiki_root, page_path, str(public_pair))
        if finding is not None:
            findings.append(finding)

    findings.sort(key=lambda f: (
        dashboard.SEVERITY_ORDER.index(f["severity"]),
        f["framework_path"],
    ))

    content = _build_dashboard_markdown(findings, frameworks_scanned)
    dashboard_path = wiki_root / DASHBOARD_RELATIVE
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(content, encoding="utf-8")

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "frameworks_scanned": frameworks_scanned,
    }


def _classify_pair(
    wiki_root: Path, framework_path: Path, public_pair: str
) -> Optional[Dict[str, str]]:
    """Classify one framework-pair into a finding dict or None if fresh.

    Order: error (target missing) > warning (framework newer) > info
    (briefing newer). Returns None when both exist AND mtimes are equal.
    """
    target = wiki_root / public_pair
    framework_rel = framework_path.relative_to(wiki_root).as_posix()

    if not target.exists():
        return {
            "severity": "error",
            "framework_path": framework_rel,
            "public_pair_path": public_pair,
            "reason": REASON_PAIR_MISSING,
        }
    f_mtime = framework_path.stat().st_mtime
    t_mtime = target.stat().st_mtime
    if f_mtime > t_mtime:
        return {
            "severity": "warning",
            "framework_path": framework_rel,
            "public_pair_path": public_pair,
            "reason": REASON_STALE_BRIEFING,
        }
    if t_mtime > f_mtime:
        return {
            "severity": "info",
            "framework_path": framework_rel,
            "public_pair_path": public_pair,
            "reason": REASON_REVERSE_CASCADE,
        }
    return None


def _build_dashboard_markdown(
    findings: List[Dict[str, str]], frameworks_scanned: int
) -> str:
    today = date.today().isoformat()
    by_severity = dashboard.group_by_fixed_order(
        findings, dashboard.SEVERITY_ORDER, lambda f: f["severity"]
    )

    lines = list(dashboard.render_fm_header(
        "Framework ↔ Briefing Sync Dashboard", today=today
    ))
    lines.append("")
    lines.append("# Framework ↔ Briefing Sync — " + today)
    lines.append("")
    lines.append("**Frameworks scanned:** " + str(frameworks_scanned))
    counts = []
    for sev in dashboard.SEVERITY_ORDER:
        n = len(by_severity[sev])
        counts.append("{} {}{}".format(n, sev, "s" if n != 1 else ""))
    lines.append(
        "**Findings:** {} ({})".format(len(findings), " / ".join(counts))
    )
    lines.append("")

    if not findings:
        lines.append("No framework-briefing-sync findings.")
        lines.append("")
        return "\n".join(lines)

    for sev in dashboard.SEVERITY_ORDER:
        bucket = by_severity[sev]
        if not bucket:
            continue
        lines.append("## " + sev)
        for f in bucket:
            lines.append("- {}: {} ↔ {}: {}".format(
                sev, f["framework_path"], f["public_pair_path"], f["reason"]
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
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=stderr)
        return 2

    findings = summary["findings"]
    for f in findings:
        print("{}: {} ↔ {}: {}".format(
            f["severity"], f["framework_path"], f["public_pair_path"], f["reason"]
        ), file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    print("framework_briefing_sync: frameworks_scanned={} findings={} -> {}".format(
        summary["frameworks_scanned"],
        len(findings),
        rel,
    ), file=stdout)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(_main(WIKI_ROOT))
