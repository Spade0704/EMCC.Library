"""Validate cross-references — broken [[wikilinks]] + orphan pages.

P9 validator. Walks the wiki for content pages (skipping infrastructure
folders prefixed with `_`), strips fenced and inline code spans, scans
each page's body for wikilinks (bare / alias / section / embed shapes),
resolves them (bare target by filename stem; path-qualified `Folder/Page`
target by full wiki-relative path; `./`- or `../`-bearing target page-relative
to the linking page's folder — see `_resolve_target`), and emits two finding
classes:

    broken_wikilinks  link target has no corresponding .md content page. The
                      dashboard distinguishes two reasons: 'target not found'
                      (a well-formed but missing target) and 'escapes wiki
                      root' (a `../` link over-popped above the wiki root).
    orphan_pages      content page receives zero inbound wikilinks AND
                      does not carry frontmatter `allow_orphan: true`

Wikilink syntax:
    [[Foo]]            bare
    [[Foo|display]]    alias  (display suffix dropped before stem-match)
    [[Foo#sec]]        section (section suffix dropped before stem-match)
    ![[Foo]]           embed  (! prefix is render-hint; target = stem)
    [[../bar/Foo]]     page-relative (any `..` segment resolves against the
                       linking page's folder; see `_resolve_target`)
    [[./bar/Foo]]      page-relative (leading `./` resolves against the linking
                       page's folder, coherent with `../`; see `_resolve_target`)

Orphan-clearance: a page does NOT clear its own orphan status by linking
to itself. Only inbound links from OTHER content pages count.
Stem-match is case-sensitive (Obsidian-graph semantics; cross-platform
reproducible).

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "broken_links": list[dict],   # {page_path, line, link}
                "orphans": list[dict],         # {page_path}
                "pages_scanned": int,
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki_root, IO error).
"""

import posixpath
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict

from _lib import dashboard
from _lib import cli
from _lib import frontmatter
from _lib import markdown


WIKI_ROOT = frontmatter.find_wiki_content_root()
DASHBOARD_RELATIVE = "_dashboards/cross_refs.md"
CLASS_ORDER = ("broken_wikilinks", "orphan_pages")

# Wikilink regex. Optional `!` embed prefix is consumed in one pass so an
# embed `![[Foo]]` does NOT also match the bare `[[Foo]]` substring inside.
# Target stem captured in group 'target'; alias suffix `|display` and
# section suffix `#sec` are non-capturing — both stripped at regex level.
_WIKILINK_RE = re.compile(
    r"!?\[\[(?P<target>[^\[\]\|#\n]+)(?:\|[^\]\n]*)?(?:#[^\]\n]*)?\]\]"
)


def _iter_wikilinks(text):
    """Yield (target_stem, body_line_1indexed) for each wikilink in text.

    text is expected pre-stripped via _lib.markdown.strip_code so example
    wikilinks inside fenced/inline code spans are not yielded.

    Module-private prototype. Per BUILD_DISCIPLINE 3rd-consumer rule, do
    NOT promote to _lib/markdown.py until a 3rd consumer arrives (P12
    check_canon_consistency is the likely call-site).
    """
    for match in _WIKILINK_RE.finditer(text):
        target = match.group("target").strip()
        if not target:
            continue
        body_line = text[:match.start()].count("\n") + 1
        yield target, body_line


# Resolution outcome status (third element of the _resolve_target tuple).
# ESCAPES_ROOT is reported with a distinct dashboard message; NOT_FOUND is the
# generic broken-target signal. OK means the target resolved to a real page.
STATUS_OK = "ok"
STATUS_NOT_FOUND = "not_found"
STATUS_ESCAPES_ROOT = "escapes_root"


def _resolve_page_relative(linking_page_dir, target):
    """Resolve a `.`/`..`-bearing target against the linking page's folder.

    Joins `linking_page_dir` (the wiki-relative posix dir of the page that
    CONTAINS the link, "" or "." for a root-level page) with `target`, then
    collapses `.`/`..` segments via `posixpath.normpath` (pure string math, no
    filesystem touch — never `Path.resolve()`, which would hit disk/symlinks).
    Returns the resulting wiki-relative key (no extension), or None when the
    `..` segments walk above the wiki root (an unresolvable escape) — callers
    map that None to STATUS_ESCAPES_ROOT (distinct from a resolvable-but-missing
    target). A `.`-only target (`./` from a root page) normalizes to the wiki
    root itself, which is not a page, so it too returns None-as-escape.
    """
    joined = posixpath.normpath(posixpath.join(linking_page_dir, target))
    if joined == ".." or joined.startswith("../") or joined == ".":
        return None
    return joined


def _resolve_target(target, stem_to_page, relpath_to_page, linking_page_dir):
    """Resolve a wikilink target to (page_or_None, status).

    status is one of STATUS_OK (resolved — page is non-None), STATUS_NOT_FOUND
    (a well-formed target with no destination page — the generic broken case),
    or STATUS_ESCAPES_ROOT (a page-relative target whose `..` segments walk
    above the wiki root — a distinct, more actionable author signal).

    A bare target (`Page`) resolves by filename stem. A path-qualified target
    (`Folder/Page`, the Style-Guide-mandated disambiguation form) resolves ONLY
    when its full wiki-relative path maps to a real page — never by last segment
    alone, which would mask genuinely broken or ambiguous links. A target that
    is page-relative — it starts with `./` OR carries ANY `..` segment —
    resolves against the linking page's own folder (`linking_page_dir`), like a
    filesystem path, and reports escapes-root if it walks above the wiki root.
    Leading `./` is page-relative for coherence with `../` (both mean "from
    here"): `[[./Sub/Page]]` from `a/` resolves to `a/Sub/Page`, not root
    `Sub/Page`. A bare `Folder/Page` with no `.`/`..` segments stays
    wiki-root-relative (the disambiguation form). A trailing `.md` is tolerated.
    Case-sensitive on every host. `.`/`..` are matched by exact segment, so a
    folder literally named e.g. `my..weird` or `.hidden` is unaffected.
    """
    t = target.strip()
    if t.endswith(".md"):
        t = t[:-3]
    if "/" in t:
        segments = t.split("/")
        if ".." in segments or t.startswith("./"):
            key = _resolve_page_relative(linking_page_dir, t)
            if key is None:
                return None, STATUS_ESCAPES_ROOT
            page = relpath_to_page.get(key)
            return (page, STATUS_OK) if page is not None else (None, STATUS_NOT_FOUND)
        page = relpath_to_page.get(t)
        return (page, STATUS_OK) if page is not None else (None, STATUS_NOT_FOUND)
    page = stem_to_page.get(t)
    return (page, STATUS_OK) if page is not None else (None, STATUS_NOT_FOUND)


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk the wiki, scan wikilinks + orphan pages, write the dashboard."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )

    pages = list(markdown.iter_content_pages(wiki_root))
    pages_scanned = len(pages)

    stem_to_page = {}
    for page_path in pages:
        stem_to_page.setdefault(page_path.stem, page_path)

    # Path-qualified resolution map: wiki-relative path WITHOUT extension
    # (posix, case-sensitive) -> page. The Style-Guide mandates the
    # `[[Folder/Page]]` form for disambiguation and the cross-link generator
    # emits it; resolving such a target by its bare last segment alone would
    # flip a false-positive into a false-negative (two `Setup.md` in different
    # folders collapsing, or `[[ghost/Page]]` matching a real `Page` elsewhere).
    # So a path-qualified target resolves ONLY when its full relative path maps
    # to a real page. Case-sensitive on every host (Obsidian-graph semantics).
    relpath_to_page = {}
    for page_path in pages:
        rel = page_path.relative_to(wiki_root).with_suffix("").as_posix()
        relpath_to_page.setdefault(rel, page_path)

    inbound_pages = set()
    page_meta = []
    broken_links = []
    for page_path in pages:
        page = frontmatter.load_page(page_path)
        fm = page["frontmatter"]
        allow_orphan = bool(fm.get("allow_orphan"))

        raw_text = page_path.read_text(encoding="utf-8")
        fm_lines = markdown.frontmatter_line_count(raw_text)
        stripped = markdown.strip_code(page["body"])

        # Wiki-relative posix dir of THIS page, the base for page-relative
        # (`../`) target resolution. "." for a root-level page.
        linking_page_dir = page_path.relative_to(wiki_root).parent.as_posix()

        for target_stem, body_line in _iter_wikilinks(stripped):
            file_line = body_line + fm_lines
            resolved, status = _resolve_target(
                target_stem, stem_to_page, relpath_to_page, linking_page_dir
            )
            if resolved is None:
                broken_links.append({
                    "page_path": page_path,
                    "line": file_line,
                    "link": target_stem,
                    "reason": status,
                })
                continue
            # Self-link does NOT clear orphan status — only inbound links
            # from OTHER pages count (Obsidian-graph semantics). Track the
            # resolved page IDENTITY (not its stem) so a link to one of two
            # same-stem pages does not falsely clear the other's orphan status.
            if resolved == page_path:
                continue
            inbound_pages.add(resolved)

        page_meta.append({
            "page_path": page_path,
            "allow_orphan": allow_orphan,
        })

    orphans = []
    for meta in page_meta:
        if meta["allow_orphan"]:
            continue
        if meta["page_path"] in inbound_pages:
            continue
        orphans.append({"page_path": meta["page_path"]})

    broken_links.sort(key=lambda f: (
        f["page_path"].relative_to(wiki_root).as_posix(),
        f["line"],
    ))
    orphans.sort(key=lambda f: f["page_path"].relative_to(wiki_root).as_posix())

    content = _build_dashboard_markdown(
        wiki_root, broken_links, orphans, pages_scanned
    )
    dashboard_path = dashboard.write_dashboard(wiki_root, DASHBOARD_RELATIVE, content)

    return {
        "dashboard_path": dashboard_path,
        "broken_links": broken_links,
        "orphans": orphans,
        "pages_scanned": pages_scanned,
    }


def _build_dashboard_markdown(wiki_root, broken_links, orphans, pages_scanned):
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header("Cross-References Dashboard", today=today))
    lines.append("")
    lines.append("# Cross-References — " + today)
    lines.append("")
    lines.append("**Pages scanned:** " + str(pages_scanned))
    n_broken = len(broken_links)
    n_orphan = len(orphans)
    lines.append("**Findings:** {} ({} broken / {} orphan{})".format(
        n_broken + n_orphan,
        n_broken,
        n_orphan,
        "s" if n_orphan != 1 else "",
    ))
    lines.append("")

    if not broken_links and not orphans:
        lines.append("No cross-reference findings.")
        lines.append("")
        return "\n".join(lines)

    if broken_links:
        lines.append("## broken_wikilinks")
        for f in broken_links:
            rel = f["page_path"].relative_to(wiki_root).as_posix()
            # AC4(b) entry-line literal lock-in (Pattern #5). Format:
            #   '- broken: <rel>:<line>: [[<link>]] target not found'
            #   '- broken: <rel>:<line>: [[<link>]] escapes wiki root'
            # The suffix is the resolution reason: the generic 'target not
            # found' for a well-formed-but-missing target, or the distinct
            # 'escapes wiki root' for an over-popped `../` link that walks
            # above the wiki root (a more actionable author signal). The
            # dashboard is rendered as markdown, not machine-parsed, so the
            # second suffix is additive at the consumer surface.
            # Asserted by tests::test_dashboard_entry_line_literal_broken
            # and ::test_dashboard_entry_line_literal_escapes_root.
            # Edit these format strings only with paired test update.
            suffix = (
                "escapes wiki root"
                if f.get("reason") == STATUS_ESCAPES_ROOT
                else "target not found"
            )
            lines.append("- broken: {}:{}: [[{}]] {}".format(
                rel, f["line"], f["link"], suffix
            ))
        lines.append("")
    if orphans:
        lines.append("## orphan_pages")
        for f in orphans:
            rel = f["page_path"].relative_to(wiki_root).as_posix()
            # AC4(b) entry-line literal lock-in (Pattern #5). Format:
            #   '- orphan: <rel>'   (page-level — no :line: segment).
            # Asserted by tests::test_dashboard_entry_line_literal_orphan.
            # Edit this format string only with paired test update.
            lines.append("- orphan: {}".format(rel))
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

    for f in summary["broken_links"]:
        rel = f["page_path"].relative_to(wiki_root).as_posix()
        # Append a terse reason marker only for the distinct escapes-root case;
        # the generic not-found case keeps its bare CLI form (back-compatible).
        marker = (
            " (escapes wiki root)"
            if f.get("reason") == STATUS_ESCAPES_ROOT
            else ""
        )
        print("broken: {}:{}: [[{}]]{}".format(rel, f["line"], f["link"], marker),
              file=stdout)
    for f in summary["orphans"]:
        rel = f["page_path"].relative_to(wiki_root).as_posix()
        print("orphan: {}".format(rel), file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    n_broken = len(summary["broken_links"])
    n_orphan = len(summary["orphans"])
    print("cross_refs: pages_scanned={} findings={} (broken={} orphans={}) -> {}".format(
        summary["pages_scanned"],
        n_broken + n_orphan,
        n_broken,
        n_orphan,
        rel,
    ), file=stdout)
    return 1 if (n_broken + n_orphan) else 0


if __name__ == "__main__":
    WIKI_ROOT = cli.resolve_cli_wiki_root(WIKI_ROOT)
    sys.exit(_main(WIKI_ROOT))
