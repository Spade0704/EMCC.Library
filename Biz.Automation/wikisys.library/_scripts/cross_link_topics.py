"""P18.3 cross_link_topics — marker-block 'See also' writer + idempotent.

Per CODEX_BUILD_SPEC_v1_3.md §2.4 #17 + §2.7 marker contract + §3
Principle #13. For each multi-page topic, writes frontmatter
`related_files: []` (script-managed full replacement) + body
marker-bracketed 'See also' block. Idempotent: re-run with identical
inputs produces zero diffs per spec §2.7 idempotency requirement.

Marker contract (spec §2.7 byte-exact):
    <!-- codex:see-also:start -->
    ## See also
    - [[OtherPageStem]] — *topic: smoke*
    <!-- codex:see-also:end -->

Human edits OUTSIDE markers PRESERVED. Human edits BETWEEN markers
OVERWRITTEN by design (content is rendered view; frontmatter
`related_files:` is canonical source per spec §2.7).

T-XL-3 build_topic_index sets fm `topics:` additively; T-XL-4 reads
those topics + computes related-page graph + writes the rendered
view. Re-derives topic→pages from page fm (stateless-orchestrator
discipline per Architect arbitration) rather than consuming T-XL-3
runtime state directly.

Public API:
    run(wiki_root: Path) -> Dict[str, Any]
    build_topic_to_pages_index(wiki_root: Path) -> Dict[str, List[Path]]
    compute_related_files(page_path, page_topics, topic_to_pages) -> List[Path]
    render_see_also_block(related_files, page_topics_per_related, wiki_root) -> str
    update_page_related_files_fm(page_text, related_files, wiki_root) -> str
    replace_or_append_marker_block(page_text, see_also_block) -> str
    process_page(page_path, page_topics, topic_to_pages, page_topics_by_path, wiki_root) -> bool

Pure stdlib per spec §8 Hard Rule 1.
"""

from pathlib import Path
from typing import Any, Dict, List

from _lib import cli
from _lib import frontmatter
from _lib import markdown
from _lib.topics import load_cross_link_config


WIKI_ROOT = frontmatter.find_wiki_content_root()

# Byte-exact marker constants per spec §2.7 marker contract.
MARKER_START = "<!-- codex:see-also:start -->"
MARKER_END = "<!-- codex:see-also:end -->"


def build_topic_to_pages_index(wiki_root: Path) -> Dict[str, List[Path]]:
    """Re-derive topic → [pages] mapping from page frontmatter `topics:` fields.

    Iterates content pages via _lib.markdown.iter_content_pages; reads
    each page's fm topics: list; accumulates the inverted mapping. Pages
    with absent/empty topics: skipped. Non-string topic values skipped
    defensively.
    """
    index: Dict[str, List[Path]] = {}
    for page_path in markdown.iter_content_pages(wiki_root):
        page = frontmatter.load_page(page_path)
        topics = page["frontmatter"].get("topics") or []
        if not isinstance(topics, list):
            continue
        for topic in topics:
            if not isinstance(topic, str):
                continue
            index.setdefault(topic, []).append(page_path)
    return index


def compute_related_files(
    page_path: Path,
    page_topics: List[str],
    topic_to_pages: Dict[str, List[Path]],
) -> List[Path]:
    """Union all pages sharing ≥1 topic with this page (excluding self).

    Returns sorted+deduped list of related page paths.
    """
    related: set = set()
    for topic in page_topics:
        for other in topic_to_pages.get(topic, []):
            if other != page_path:
                related.add(other)
    return sorted(related, key=lambda p: p.as_posix())


def _container_of(path: Path, wiki_root: Path) -> str:
    """Top-level content folder a page lives under (manual/section), or '' .

    Used for cross-container ranking + duplicate-stem disambiguation labels.
    Handles both absolute (run-time) and already-relative (unit-test) paths.
    """
    try:
        parts = path.relative_to(wiki_root).parts
    except ValueError:
        parts = path.parts
    return parts[0] if parts else ""


def _link_target(path: Path, wiki_root: Path, ambiguous_stems) -> str:
    """Render the wikilink body for one related page.

    Default (spec §2.7): bare `[[Stem]]`. When the stem is ambiguous
    (occurs in >1 content page wiki-wide — passed via `ambiguous_stems`),
    emit a path-qualified link `[[rel/path|Stem (Container)]]` so Obsidian
    resolves it unambiguously. `ambiguous_stems` None/empty → always bare
    (byte-identical to pre-2026-06-13 behavior).
    """
    stem = path.stem
    if not ambiguous_stems or stem not in ambiguous_stems:
        return "[[{}]]".format(stem)
    try:
        rel = path.relative_to(wiki_root).with_suffix("")
    except ValueError:
        rel = path.with_suffix("")
    return "[[{}|{} ({})]]".format(rel.as_posix(), stem, _container_of(path, wiki_root))


def rank_related(
    page_path: Path,
    related: List[Path],
    page_topics: List[str],
    page_topics_by_path: Dict[Path, List[str]],
    wiki_root: Path,
) -> List[Path]:
    """Order related pages by relevance for capping.

    Key: (shared-topic-count desc, cross-container first, path asc). A page
    sharing more topics ranks higher; ties broken by preferring a DIFFERENT
    top-level container (surfaces cross-manual jumps); final tiebreak path
    for stable/idempotent output.
    """
    page_topic_set = set(page_topics)
    page_container = _container_of(page_path, wiki_root)

    def key(c: Path):
        shared = len(page_topic_set & set(page_topics_by_path.get(c, [])))
        cross = 1 if _container_of(c, wiki_root) != page_container else 0
        return (-shared, -cross, c.as_posix())

    return sorted(related, key=key)


def build_ambiguous_stems(wiki_root: Path) -> set:
    """Stems shared by >1 content page wiki-wide (need path-qualified links)."""
    by_stem: Dict[str, int] = {}
    for p in markdown.iter_content_pages(wiki_root):
        by_stem[p.stem] = by_stem.get(p.stem, 0) + 1
    return {stem for stem, n in by_stem.items() if n > 1}


def render_see_also_block(
    related_files: List[Path],
    page_topics_per_related: Dict[Path, List[str]],
    wiki_root: Path,
    ambiguous_stems=None,
) -> str:
    """Render marker-bracketed 'See also' block CONTENT (no markers).

    Per spec §2.7 example format: H2 + bulleted wikilinks with
    topic-annotation italics. Empty related_files → empty string
    (caller appends markers only when content non-empty).

    `ambiguous_stems` (optional set): stems that collide across the wiki get
    path-qualified links per the §2.7 disambiguation clause; None preserves
    the bare `[[Stem]]` default.
    """
    if not related_files:
        return ""
    lines: List[str] = ["## See also", ""]
    for path in related_files:
        topics = page_topics_per_related.get(path, [])
        link = _link_target(path, wiki_root, ambiguous_stems)
        topics_str = ", ".join(topics)
        if topics_str:
            lines.append("- {} — *topic: {}*".format(link, topics_str))
        else:
            lines.append("- {}".format(link))
    return "\n".join(lines)


def update_page_related_files_fm(
    page_text: str, related_files: List[Path], wiki_root: Path
) -> str:
    """Update fm `related_files:` SCRIPT-MANAGED full-replacement.

    Per spec §2.7 frontmatter-as-source-of-truth + §3 Principle #13.
    Replaces existing related_files: value with sorted+deduped computed
    value; adds field at end of fm block if absent. Pages without
    frontmatter skipped (no fm synthesis).
    """
    lines = page_text.split("\n")
    close = frontmatter.find_frontmatter_close(lines)
    if close is None:
        return page_text

    rel_paths: List[str] = []
    for p in related_files:
        if p.is_absolute():
            try:
                rel_paths.append(p.relative_to(wiki_root).as_posix())
            except ValueError:
                rel_paths.append(p.as_posix())
        else:
            rel_paths.append(p.as_posix())
    rel_paths = sorted(set(rel_paths))
    new_value = "[]" if not rel_paths else "[" + ", ".join(rel_paths) + "]"
    new_field = "related_files: " + new_value

    fm_lines = lines[1:close]
    out_fm: List[str] = []
    saw = False
    for line in fm_lines:
        if line.lstrip().startswith("related_files:"):
            out_fm.append(new_field)
            saw = True
        else:
            out_fm.append(line)
    if not saw:
        out_fm.append(new_field)

    return "\n".join(["---"] + out_fm + ["---"] + lines[close + 1:])


def replace_or_append_marker_block(
    page_text: str, see_also_block: str
) -> str:
    """Replace existing marker-bracketed block OR append at end-of-file.

    Per spec §2.7: locates byte-exact MARKER_START/MARKER_END pair;
    replaces content between (preserving markers + their position); if
    absent, appends marker_start + block + marker_end at end-of-file
    before trailing trivia. Human prose OUTSIDE markers PRESERVED
    zero-deviation; human edits BETWEEN markers OVERWRITTEN by design.
    """
    # S047 dogfood Edit-1: scan for markers in code-stripped text so
    # markers documented inside fenced/inline code blocks are not
    # mistaken for live ones. strip_code substitutes space-for-char
    # (markdown.py _blank) preserving byte offsets, so positions found
    # in scan_text are byte-identical in page_text. Branch falls through
    # to append when no unfenced pair (or only one of {start,end}
    # unfenced) — mirrors pre-fix start_idx/end_idx == -1 semantics.
    scan_text = markdown.strip_code(page_text)
    start_idx = scan_text.find(MARKER_START)
    end_idx = scan_text.find(MARKER_END)

    if start_idx >= 0 and end_idx >= 0 and end_idx > start_idx:
        before = page_text[: start_idx + len(MARKER_START)]
        after = page_text[end_idx:]
        if see_also_block:
            return before + "\n" + see_also_block + "\n" + after
        return before + "\n" + after

    if not see_also_block:
        return page_text
    stripped = page_text.rstrip()
    return (
        stripped + "\n\n" + MARKER_START + "\n"
        + see_also_block + "\n" + MARKER_END + "\n"
    )


def process_page(
    page_path: Path,
    page_topics: List[str],
    topic_to_pages: Dict[str, List[Path]],
    page_topics_by_path: Dict[Path, List[str]],
    wiki_root: Path,
    max_links: int = 0,
    ambiguous_stems=None,
) -> bool:
    """Atomic update: fm related_files + body marker block. Idempotent.

    Reads existing page text in single I/O; computes new fm +
    marker-block content in-memory; writes back via single Path.write_text
    only if content differs. Returns True if file was actually written.
    Pages with empty page_topics skip without touching content (caller-
    safety guard; mirrors run() top-level skip behavior).

    `max_links` > 0 caps the related set to the top-N by `rank_related`
    (default 0 = uncapped, original behavior). `ambiguous_stems` is forwarded
    to rendering for duplicate-stem disambiguation. Both `related_files:` fm
    and the see-also block reflect the same (possibly capped) set.
    """
    if not page_topics:
        return False
    related = compute_related_files(page_path, page_topics, topic_to_pages)
    if max_links and max_links > 0 and len(related) > max_links:
        related = rank_related(
            page_path, related, page_topics, page_topics_by_path, wiki_root
        )[:max_links]
    page_topics_per_related = {p: page_topics_by_path.get(p, []) for p in related}
    see_also_block = render_see_also_block(
        related, page_topics_per_related, wiki_root, ambiguous_stems
    )

    existing_text = page_path.read_text(encoding="utf-8")
    new_text = update_page_related_files_fm(existing_text, related, wiki_root)
    new_text = replace_or_append_marker_block(new_text, see_also_block)

    if new_text == existing_text:
        return False
    page_path.write_text(new_text, encoding="utf-8")
    return True


def run(wiki_root: Path) -> Dict[str, Any]:
    """Orchestrator entry-point — build topic index + write related_files + see-also blocks.

    Returns summary dict with pages_seen + pages_updated + idempotent_pages counts.

    Reads `_config/cross_link.yaml` `see_also` section for opt-in behavior:
    `max_links_per_page` (0 = uncapped default) and
    `disambiguate_duplicate_stems` (False default). Both defaults reproduce
    pre-2026-06-13 output byte-for-byte; consumers opt in.
    """
    wiki_root = Path(wiki_root)

    cfg = load_cross_link_config(wiki_root)
    see_cfg = cfg.get("see_also", {})
    try:
        max_links = int(see_cfg.get("max_links_per_page", 0) or 0)
    except (TypeError, ValueError):
        max_links = 0
    disambiguate = bool(see_cfg.get("disambiguate_duplicate_stems", False))
    ambiguous_stems = build_ambiguous_stems(wiki_root) if disambiguate else None

    topic_to_pages = build_topic_to_pages_index(wiki_root)

    page_topics_by_path: Dict[Path, List[str]] = {}
    for page_path in markdown.iter_content_pages(wiki_root):
        page = frontmatter.load_page(page_path)
        topics = page["frontmatter"].get("topics") or []
        if isinstance(topics, list):
            page_topics_by_path[page_path] = [
                t for t in topics if isinstance(t, str)
            ]

    pages_seen = 0
    pages_updated = 0
    idempotent_pages = 0

    for page_path in markdown.iter_content_pages(wiki_root):
        pages_seen += 1
        page_topics = page_topics_by_path.get(page_path, [])
        if not page_topics:
            continue
        changed = process_page(
            page_path,
            page_topics,
            topic_to_pages,
            page_topics_by_path,
            wiki_root,
            max_links,
            ambiguous_stems,
        )
        if changed:
            pages_updated += 1
        else:
            idempotent_pages += 1

    return {
        "topic_to_pages": topic_to_pages,
        "pages_seen": pages_seen,
        "pages_updated": pages_updated,
        "idempotent_pages": idempotent_pages,
    }


if __name__ == "__main__":
    WIKI_ROOT = cli.resolve_cli_wiki_root(WIKI_ROOT)
    summary = run(WIKI_ROOT)
    print(
        "cross_link_topics: topics={} pages_seen={} updated={} idempotent={}".format(
            len(summary["topic_to_pages"]),
            summary["pages_seen"],
            summary["pages_updated"],
            summary["idempotent_pages"],
        )
    )
