"""Validate deeper link-graph integrity — reachability + dead-ends.

A graph-integrity layer that sits ABOVE the cross-reference validator
(`check_cross_refs.py`). Where cross-refs answers per-link questions ("does
this target resolve?", "does this page have ANY inbound link?"), this layer
answers whole-graph questions that those local checks cannot: is the page graph
actually *connected* from the reader's entry point, and can a reader navigate
*out* of every page? These are the integrity properties on the readiness path
from a cross-refs-clean wiki (~70) toward a navigable one (~80).

It reuses the SAME wikilink scan and resolver as `check_cross_refs` (imported,
not duplicated — single source of truth for link semantics), builds the directed
page graph, and emits two finding classes that cross-refs does NOT cover:

    unreachable_pages   content page not reachable from the wiki entry page
                        (`Home.md`, or the configured entry) by following
                        resolvable wikilinks. A mutually-linked island clears
                        every page's orphan status yet is still unreachable from
                        the front door — cross-refs' inbound-count check misses
                        it; a root-anchored BFS catches it.
    dead_end_pages      content page with zero OUTBOUND resolvable wikilinks (a
                        navigation sink — a reader who lands here cannot leave by
                        the graph). The directed dual of an orphan (zero inbound).

Both classes honour the same `allow_orphan: true` frontmatter escape hatch
cross-refs uses for orphan_pages: a page deliberately exempted from inbound-link
requirements is also exempted from reachability/dead-end requirements (it is an
acknowledged graph leaf, e.g. a changelog or an archive index). The entry page
itself is never reported (it is the BFS root, and a reader starts there).

This validator is READ-ONLY over content and ADDITIVE: it imports cross-refs'
resolver but changes none of its behaviour, adds no finding to the cross-refs
dashboard, and writes its own dashboard at `_dashboards/link_graph.md`.

Public API:
    run(wiki_root: Path, entry_stem: str = "Home") -> dict
        Returns:
            {
                "dashboard_path": Path,
                "unreachable": list[dict],   # {page_path}
                "dead_ends": list[dict],     # {page_path}
                "pages_scanned": int,
                "entry_page": Path | None,   # resolved entry, or None if absent
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki_root, IO error).
"""
# @component Codex[validators]

import sys
from collections import deque
from datetime import date
from pathlib import Path
from typing import Any, Dict

from _lib import dashboard
from _lib import cli
from _lib import frontmatter
from _lib import markdown

import check_cross_refs


WIKI_ROOT = frontmatter.find_wiki_content_root()
DASHBOARD_RELATIVE = "_dashboards/link_graph.md"
DEFAULT_ENTRY_STEM = "Home"
CLASS_ORDER = ("unreachable_pages", "dead_end_pages")


def _build_graph(wiki_root, pages):
    """Build the directed page graph by resolving every page's wikilinks.

    Returns (adjacency, allow_orphan), where:
        adjacency[page_path]   -> set of resolved destination page_paths
                                  (resolvable links only; broken/escaping links
                                  contribute no edge — they are cross-refs'
                                  concern, not the graph's).
        allow_orphan[page_path] -> bool from the page's frontmatter.

    Link scan + resolution are delegated to check_cross_refs so the two
    validators agree byte-for-byte on what a "link" is.
    """
    stem_to_page = {}
    for page_path in pages:
        stem_to_page.setdefault(page_path.stem, page_path)

    relpath_to_page = {}
    for page_path in pages:
        rel = page_path.relative_to(wiki_root).with_suffix("").as_posix()
        relpath_to_page.setdefault(rel, page_path)

    adjacency = {}
    allow_orphan = {}
    for page_path in pages:
        page = frontmatter.load_page(page_path)
        allow_orphan[page_path] = bool(page["frontmatter"].get("allow_orphan"))

        stripped = markdown.strip_code(page["body"])
        linking_page_dir = page_path.relative_to(wiki_root).parent.as_posix()

        out_edges = set()
        for target_stem, _body_line in check_cross_refs._iter_wikilinks(stripped):
            resolved, status = check_cross_refs._resolve_target(
                target_stem, stem_to_page, relpath_to_page, linking_page_dir
            )
            # A self-link is not an out-edge for navigation purposes (you cannot
            # leave a page by linking to itself), mirroring cross-refs' rule that
            # a self-link does not clear orphan status.
            if resolved is not None and resolved != page_path:
                out_edges.add(resolved)
        adjacency[page_path] = out_edges

    return adjacency, allow_orphan


def _reachable_from(entry_page, adjacency):
    """Return the set of pages reachable from entry_page via a BFS over edges."""
    seen = {entry_page}
    queue = deque([entry_page])
    while queue:
        current = queue.popleft()
        for nxt in adjacency.get(current, ()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def run(wiki_root: Path, entry_stem: str = DEFAULT_ENTRY_STEM) -> Dict[str, Any]:
    """Walk the wiki, build the link graph, report reachability + dead-ends."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )

    pages = list(markdown.iter_content_pages(wiki_root))
    pages_scanned = len(pages)

    adjacency, allow_orphan = _build_graph(wiki_root, pages)

    # Resolve the entry page by stem (Home.md by default). When absent, every
    # page is treated as unreachable EXCEPT exempted ones — a wiki with no entry
    # page is itself a finding the unreachable list will surface loudly.
    entry_page = None
    for page_path in pages:
        if page_path.stem == entry_stem:
            entry_page = page_path
            break

    if entry_page is not None:
        reachable = _reachable_from(entry_page, adjacency)
    else:
        reachable = set()

    unreachable = []
    dead_ends = []
    for page_path in pages:
        if allow_orphan[page_path]:
            continue
        if page_path == entry_page:
            # The entry page is the reader's starting point; never report it as
            # unreachable. It can still be a dead-end if it links nowhere, which
            # would be a real finding, so dead-end is checked below.
            pass
        elif page_path not in reachable:
            unreachable.append({"page_path": page_path})

        if not adjacency.get(page_path):
            dead_ends.append({"page_path": page_path})

    unreachable.sort(
        key=lambda f: f["page_path"].relative_to(wiki_root).as_posix()
    )
    dead_ends.sort(
        key=lambda f: f["page_path"].relative_to(wiki_root).as_posix()
    )

    content = _build_dashboard_markdown(
        wiki_root, unreachable, dead_ends, pages_scanned, entry_page, entry_stem
    )
    dashboard_path = dashboard.write_dashboard(
        wiki_root, DASHBOARD_RELATIVE, content
    )

    return {
        "dashboard_path": dashboard_path,
        "unreachable": unreachable,
        "dead_ends": dead_ends,
        "pages_scanned": pages_scanned,
        "entry_page": entry_page,
    }


def _build_dashboard_markdown(
    wiki_root, unreachable, dead_ends, pages_scanned, entry_page, entry_stem
):
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header("Link-Graph Dashboard", today=today))
    lines.append("")
    lines.append("# Link-Graph Integrity — " + today)
    lines.append("")
    lines.append("**Pages scanned:** " + str(pages_scanned))
    if entry_page is not None:
        entry_rel = entry_page.relative_to(wiki_root).as_posix()
        lines.append("**Entry page:** " + entry_rel)
    else:
        lines.append("**Entry page:** (none — no `{}.md` found)".format(entry_stem))
    n_unreach = len(unreachable)
    n_dead = len(dead_ends)
    lines.append("**Findings:** {} ({} unreachable / {} dead-end{})".format(
        n_unreach + n_dead,
        n_unreach,
        n_dead,
        "s" if n_dead != 1 else "",
    ))
    lines.append("")

    if not unreachable and not dead_ends:
        lines.append("No link-graph findings.")
        lines.append("")
        return "\n".join(lines)

    if unreachable:
        lines.append("## unreachable_pages")
        for f in unreachable:
            rel = f["page_path"].relative_to(wiki_root).as_posix()
            # Entry-line literal. Format:
            #   '- unreachable: <rel> (no path from entry page)'
            # Asserted by tests::test_dashboard_entry_line_literal_unreachable.
            # Edit this format string only with paired test update.
            lines.append(
                "- unreachable: {} (no path from entry page)".format(rel)
            )
        lines.append("")
    if dead_ends:
        lines.append("## dead_end_pages")
        for f in dead_ends:
            rel = f["page_path"].relative_to(wiki_root).as_posix()
            # Entry-line literal. Format:
            #   '- dead-end: <rel> (no outbound links)'
            # Asserted by tests::test_dashboard_entry_line_literal_dead_end.
            # Edit this format string only with paired test update.
            lines.append("- dead-end: {} (no outbound links)".format(rel))
        lines.append("")
    return "\n".join(lines)


def _main(wiki_root, stdout=None, stderr=None, entry_stem=DEFAULT_ENTRY_STEM):
    """CLI entry-point body. Returns exit code; lets callers test without subprocess."""
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    wiki_root = Path(wiki_root)
    try:
        summary = run(wiki_root, entry_stem=entry_stem)
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=stderr)
        return 2

    for f in summary["unreachable"]:
        rel = f["page_path"].relative_to(wiki_root).as_posix()
        print("unreachable: {}".format(rel), file=stdout)
    for f in summary["dead_ends"]:
        rel = f["page_path"].relative_to(wiki_root).as_posix()
        print("dead-end: {}".format(rel), file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    n_unreach = len(summary["unreachable"])
    n_dead = len(summary["dead_ends"])
    print(
        "link_graph: pages_scanned={} findings={} (unreachable={} dead_ends={}) -> {}".format(
            summary["pages_scanned"],
            n_unreach + n_dead,
            n_unreach,
            n_dead,
            rel,
        ),
        file=stdout,
    )
    return 1 if (n_unreach + n_dead) else 0


if __name__ == "__main__":
    WIKI_ROOT = cli.resolve_cli_wiki_root(WIKI_ROOT)
    sys.exit(_main(WIKI_ROOT))
