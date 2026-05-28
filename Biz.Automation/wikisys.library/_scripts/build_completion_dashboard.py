"""Build the red/yellow/green completion dashboard.

P5 aggregator. Walks the wiki for content pages (skipping infrastructure
folders prefixed with `_`), reads each page's `completion` value from
frontmatter, buckets pages into status bands per spec status-band semantics
(R_DATA > D_SCHEMAS), and writes a markdown dashboard at
`_dashboards/completion.md`.

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "pages_tracked": int,
                "average_completion": int | None,
                "dashboard_path": Path,
            }

Pages without an integer `completion` field are excluded entirely
(absent OR non-int → not in output). Out-of-band values land in nearest
extreme band by virtue of the threshold ladder; no clamping. Range
validation is a validator's job, not this aggregator's.

The script lives at <wiki>/_scripts/build_completion_dashboard.py.
WIKI_ROOT = parent.parent (one fewer level than _lib/, which sits one
directory deeper inside _scripts/).
"""

from datetime import date
from pathlib import Path
from typing import Any, Dict

from _lib import dashboard
from _lib import cli
from _lib import frontmatter
from _lib import markdown


WIKI_ROOT = frontmatter.find_wiki_content_root()
DASHBOARD_RELATIVE = "_dashboards/completion.md"


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk the wiki, classify by completion band, write the dashboard."""
    wiki_root = Path(wiki_root)
    banded = {name: [] for name in dashboard.BAND_ORDER}
    values = []
    for page_path in markdown.iter_content_pages(wiki_root):
        page = frontmatter.load_page(page_path)
        value = page["frontmatter"].get("completion")
        band = _band_for(value)
        if band is None:
            continue
        banded[band].append((page_path, value))
        values.append(value)

    pages_tracked = len(values)
    average_completion = (
        round(sum(values) / pages_tracked) if pages_tracked else None
    )

    for name in dashboard.BAND_ORDER:
        banded[name].sort(key=lambda p: p[0].relative_to(wiki_root).as_posix())

    content = _build_dashboard_markdown(
        wiki_root, banded, pages_tracked, average_completion
    )
    dashboard_path = dashboard.write_dashboard(wiki_root, DASHBOARD_RELATIVE, content)

    return {
        "pages_tracked": pages_tracked,
        "average_completion": average_completion,
        "dashboard_path": dashboard_path,
    }


def _band_for(value):
    """Return the band name for `value`, or None if value isn't a Python int.

    bool is excluded explicitly even though it's an int subclass —
    `completion: true` is malformed and shouldn't be banded.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    if value >= 80:
        return "ready"
    if value >= 55:
        return "solid"
    if value >= 30:
        return "outlined"
    return "gap"


def _build_dashboard_markdown(wiki_root, banded, n, avg):
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header("Completion Dashboard", today=today))
    lines.append("")
    lines.append("# Completion Dashboard — " + today)
    lines.append("")
    lines.append("**Pages with completion data:** " + str(n))
    avg_text = "—" if avg is None else str(avg) + "%"
    lines.append("**Average completion:** " + avg_text)
    lines.append("")
    if n == 0:
        lines.append("No completion data found.")
        lines.append("")
        return "\n".join(lines)
    for name in dashboard.BAND_ORDER:
        pages = banded[name]
        if not pages:
            continue
        lines.append("## " + name)
        for page_path, value in pages:
            rel = page_path.relative_to(wiki_root).as_posix()
            stem = page_path.stem
            lines.append(
                "- [[" + stem + "]] (" + rel + ") — " + str(value) + "%"
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    WIKI_ROOT = cli.resolve_cli_wiki_root(WIKI_ROOT)
    summary = run(WIKI_ROOT)
    rel = summary["dashboard_path"].relative_to(WIKI_ROOT).as_posix()
    avg = summary["average_completion"]
    avg_text = "—" if avg is None else str(avg) + "%"
    print("completion: tracked={} average={} -> {}".format(
        summary["pages_tracked"],
        avg_text,
        rel,
    ))
