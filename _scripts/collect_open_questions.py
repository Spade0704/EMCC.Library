"""Collect blocking_questions from all wiki content pages and write the dashboard.

P4 aggregator. Walks the wiki for content pages (skipping infrastructure
folders prefixed with `_`), parses each page's frontmatter via _lib.frontmatter,
collects pages whose `blocking_questions` is truthy, and writes a markdown
dashboard at `_dashboards/open_questions.md`.

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "pages_with_questions": int,
                "total_questions": int,
                "dashboard_path": Path,
            }

The script lives at <wiki>/_scripts/collect_open_questions.py.
WIKI_ROOT = parent.parent (one fewer level than _lib/, which sits one
directory deeper inside _scripts/).
"""

from datetime import date
from pathlib import Path
from typing import Any, Dict

from _lib import dashboard
from _lib import frontmatter
from _lib import markdown


WIKI_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_RELATIVE = "_dashboards/open_questions.md"


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk the wiki, collect blocking_questions, write the dashboard."""
    wiki_root = Path(wiki_root)
    pages = []
    total = 0
    for page_path in markdown.iter_content_pages(wiki_root):
        page = frontmatter.load_page(page_path)
        questions = page["frontmatter"].get("blocking_questions") or []
        if not questions:
            continue
        pages.append((page_path, questions))
        total += len(questions)
    pages.sort(key=lambda p: p[0].relative_to(wiki_root).as_posix())

    content = _build_dashboard_markdown(wiki_root, pages, total)
    dashboard_path = dashboard.write_dashboard(wiki_root, DASHBOARD_RELATIVE, content)

    return {
        "pages_with_questions": len(pages),
        "total_questions": total,
        "dashboard_path": dashboard_path,
    }


def _build_dashboard_markdown(wiki_root, pages, total):
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header("Open Questions", today=today))
    lines.append("")
    lines.append("# Open Questions — " + today)
    lines.append("")
    lines.append("**Pages with open questions:** " + str(len(pages)))
    lines.append("**Total questions:** " + str(total))
    lines.append("")
    if not pages:
        lines.append("No open questions found.")
        lines.append("")
        return "\n".join(lines)
    for page_path, questions in pages:
        rel = page_path.relative_to(wiki_root).as_posix()
        stem = page_path.stem
        lines.append("## [[" + stem + "]] (" + rel + ")")
        for q in questions:
            lines.append("- " + q)
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    summary = run(WIKI_ROOT)
    rel = summary["dashboard_path"].relative_to(WIKI_ROOT).as_posix()
    print("open_questions: pages={} questions={} -> {}".format(
        summary["pages_with_questions"],
        summary["total_questions"],
        rel,
    ))
