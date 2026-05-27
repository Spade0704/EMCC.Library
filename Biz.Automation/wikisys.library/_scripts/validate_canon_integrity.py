"""Validate canon-integrity for status:ready pages.

P7 validator. Walks the wiki for content pages (skipping infrastructure
folders prefixed with `_`), filters to pages with status == "ready", and
flags two violations:

    missing_canon_sources       canon_sources is absent or empty
    unverified_claims_present   unverified_claims is a non-empty list

Writes a markdown dashboard at `_dashboards/canon_integrity.md`. Pages
without status == "ready" are excluded from BOTH `pages_scanned` and
`findings`. A single page can produce both findings (one per category).

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "findings": list[dict],
                "pages_scanned": int,
            }
        where each finding is:
            {
                "page": str,        # rel-fwd-slash path
                "category": str,    # missing_canon_sources | unverified_claims_present
                "reason": str,
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki, IO error).
"""

import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict

from _lib import dashboard
from _lib import frontmatter
from _lib import markdown


WIKI_ROOT = frontmatter.find_wiki_root()
DASHBOARD_RELATIVE = "_dashboards/canon_integrity.md"
CATEGORY_ORDER = ("missing_canon_sources", "unverified_claims_present")
REASON_MISSING = "status:ready page has no canon_sources"
REASON_UNVERIFIED = "status:ready page has unverified_claims pending"


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk the wiki, scan ready pages, write the dashboard."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )
    findings = []
    pages_scanned = 0
    for page_path in markdown.iter_content_pages(wiki_root):
        page = frontmatter.load_page(page_path)
        fm = page["frontmatter"]
        if fm.get("status") != "ready":
            continue
        pages_scanned += 1
        rel = page_path.relative_to(wiki_root).as_posix()
        if not fm.get("canon_sources"):
            findings.append({
                "page": rel,
                "category": "missing_canon_sources",
                "reason": REASON_MISSING,
            })
        if fm.get("unverified_claims"):
            findings.append({
                "page": rel,
                "category": "unverified_claims_present",
                "reason": REASON_UNVERIFIED,
            })

    findings.sort(key=lambda f: (
        CATEGORY_ORDER.index(f["category"]),
        f["page"],
    ))

    content = _build_dashboard_markdown(findings, pages_scanned)
    dashboard_path = wiki_root / DASHBOARD_RELATIVE
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(content, encoding="utf-8")

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "pages_scanned": pages_scanned,
    }


def _build_dashboard_markdown(findings, pages_scanned):
    today = date.today().isoformat()
    by_cat = dashboard.group_by_fixed_order(
        findings, CATEGORY_ORDER, lambda f: f["category"]
    )

    lines = list(dashboard.render_fm_header("Canon Integrity Dashboard", today=today))
    lines.append("")
    lines.append("# Canon Integrity — " + today)
    lines.append("")
    lines.append("**Pages scanned:** " + str(pages_scanned))
    lines.append("**Findings:** " + str(len(findings)))
    lines.append("")

    if not findings:
        lines.append("No canon-integrity findings.")
        lines.append("")
        return "\n".join(lines)

    for name in CATEGORY_ORDER:
        bucket = by_cat[name]
        if not bucket:
            continue
        lines.append("## " + name)
        for f in bucket:
            stem = Path(f["page"]).stem
            lines.append(
                "- [[" + stem + "]] (" + f["page"] + ") — " + f["reason"]
            )
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
        print("{}: {}: {}".format(f["category"], f["page"], f["reason"]),
              file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    print("canon_integrity: pages_scanned={} findings={} -> {}".format(
        summary["pages_scanned"],
        len(findings),
        rel,
    ), file=stdout)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(_main(WIKI_ROOT))
