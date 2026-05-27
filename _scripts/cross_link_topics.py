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

import sys
from pathlib import Path
from typing import Any, Dict, List

from _lib import frontmatter
from _lib import markdown


WIKI_ROOT = Path(__file__).resolve().parent.parent

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


def render_see_also_block(
    related_files: List[Path],
    page_topics_per_related: Dict[Path, List[str]],
    wiki_root: Path,
) -> str:
    """Render marker-bracketed 'See also' block CONTENT (no markers).

    Per spec §2.7 example format: H2 + bulleted wikilinks with
    topic-annotation italics. Empty related_files → empty string
    (caller appends markers only when content non-empty).
    """
    _ = wiki_root  # wiki_root reserved for future relative-path rendering
    if not related_files:
        return ""
    lines: List[str] = ["## See also", ""]
    for path in related_files:
        topics = page_topics_per_related.get(path, [])
        stem = path.stem
        topics_str = ", ".join(topics)
        if topics_str:
            lines.append("- [[{}]] — *topic: {}*".format(stem, topics_str))
        else:
            lines.append("- [[{}]]".format(stem))
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
) -> bool:
    """Atomic update: fm related_files + body marker block. Idempotent.

    Reads existing page text in single I/O; computes new fm +
    marker-block content in-memory; writes back via single Path.write_text
    only if content differs. Returns True if file was actually written.
    Pages with empty page_topics skip without touching content (caller-
    safety guard; mirrors run() top-level skip behavior).
    """
    if not page_topics:
        return False
    related = compute_related_files(page_path, page_topics, topic_to_pages)
    page_topics_per_related = {p: page_topics_by_path.get(p, []) for p in related}
    see_also_block = render_see_also_block(
        related, page_topics_per_related, wiki_root
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
    """
    wiki_root = Path(wiki_root)

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
    summary = run(WIKI_ROOT)
    print(
        "cross_link_topics: topics={} pages_seen={} updated={} idempotent={}".format(
            len(summary["topic_to_pages"]),
            summary["pages_seen"],
            summary["pages_updated"],
            summary["idempotent_pages"],
        )
    )
