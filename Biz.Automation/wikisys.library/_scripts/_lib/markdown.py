"""Shared markdown content-traversal and content-rewriting helpers.

Promoted from per-script duplication in P6 (validate_terminology) and P8
(validate_reveal_conceit) per BUILD_DISCIPLINE 3rd-consumer rule, ahead of
P9 (check_cross_refs) which would otherwise have triggered a third in-line
copy. Pure stdlib.

Public API:
    strip_code(text: str) -> str
        Replace fenced (```...``` or ~~~...~~~), indented (4-space / tab)
        and inline (`...`) code spans with whitespace. Preserves line counts
        so post-strip line numbers reference the same lines as the input.
        Indented-code detection is CommonMark-aligned and list-aware: a run of
        indented lines counts as a code block only when it follows a blank line
        AND the last non-blank line before it is not a list item — so a wikilink
        in an indented list continuation is NOT stripped (it is a real link, not
        example code). HTML comments are NOT stripped (Codex's see-also markers
        are HTML comments located via this helper).

    frontmatter_line_count(text: str) -> int
        Return the line count of a leading `---...---` frontmatter block,
        including both delimiter lines. Returns 0 when the input has no
        frontmatter or the block is unterminated.

    iter_content_pages(wiki_root: Path) -> Iterator[Path]
        Yield content-page *.md paths under wiki_root, skipping any path
        whose components start with `_` (e.g. _dashboards/, _config/,
        _canon/, _brain_dump/, _sources/, _inbox/, _template/, _context/,
        _scripts/).
"""

import re
from pathlib import Path
from typing import Iterator


_FENCED_RE = re.compile(
    r"^(?P<fence>```|~~~)[^\n]*\n.*?^(?P=fence)\s*$",
    re.MULTILINE | re.DOTALL,
)
_INLINE_RE = re.compile(r"`[^`\n]*`")
# A list item: optional indent, then a bullet (-, *, +) or ordered marker
# (1. / 1)), then whitespace. Used to keep indented list continuations out
# of the indented-code path (a wikilink in a list continuation is real).
_LIST_ITEM_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s")


def strip_code(text: str) -> str:
    """Replace fenced, indented and inline code spans with whitespace.

    Each char in a stripped span becomes a space except '\\n', which passes
    through, so line counts (and therefore scan line numbers) are preserved.
    Order: fenced fences first (their bodies may be indented), then indented
    code blocks, then inline spans. HTML comments are deliberately NOT
    stripped — Codex's own `<!-- codex:see-also:start/end -->` markers are
    HTML comments that `cross_link_topics` locates via this helper.
    """
    text = _FENCED_RE.sub(_blank, text)
    text = _strip_indented_code(text)
    text = _INLINE_RE.sub(_blank, text)
    return text


def _is_indented(line: str) -> bool:
    return line.startswith("    ") or line.startswith("\t")


def _strip_indented_code(text: str) -> str:
    """Blank CommonMark indented code blocks, list-aware, line-count-preserving.

    An indented code block is a maximal run of indented (4-space / tab) lines,
    possibly with interior blank lines, that (a) follows a blank line (or the
    start of the text) — indented code cannot interrupt a paragraph — and
    (b) is not a list-item continuation (the last non-blank line before the run
    is not a list marker). Only the indented lines in the run are blanked;
    interior/trailing blank lines pass through unchanged.
    """
    lines = text.split("\n")
    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        if not _is_indented(line):
            i += 1
            continue
        preceding_blank = (i == 0) or (lines[i - 1].strip() == "")
        if not preceding_blank:
            i += 1
            continue
        # Last non-blank line before this run: a list marker means the indent
        # is list content, not a code block.
        k = i - 1
        while k >= 0 and lines[k].strip() == "":
            k -= 1
        last_nonblank = lines[k] if k >= 0 else ""
        if _LIST_ITEM_RE.match(last_nonblank):
            i += 1
            continue
        # Extend the run across indented + interior blank lines; remember the
        # last indented index so trailing blanks are not consumed.
        j = i
        last_indented = i
        while j < n and (_is_indented(lines[j]) or lines[j].strip() == ""):
            if _is_indented(lines[j]):
                last_indented = j
            j += 1
        for m in range(i, last_indented + 1):
            if _is_indented(lines[m]):
                lines[m] = " " * len(lines[m])
        i = last_indented + 1
    return "\n".join(lines)


def _blank(match):
    return "".join(" " if c != "\n" else "\n" for c in match.group(0))


def frontmatter_line_count(text: str) -> int:
    """Count lines occupied by frontmatter (including both --- markers).

    Returns 0 if no frontmatter is present or the block is unterminated.
    """
    if not text.startswith("---"):
        return 0
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return i + 1
    return 0


def iter_content_pages(wiki_root: Path) -> Iterator[Path]:
    """Yield content-page Paths.

    Skips any path containing a `_`-prefixed component (legacy convention:
    `_canon/`, `_dashboards/`, `_archive/`, etc.), AND the canonical
    v1.1 `raw/` source archive at wiki content root (S004 extension —
    `raw/` is read-only source material per portfolio spec P3, never
    content pages).
    """
    for md in wiki_root.rglob("*.md"):
        rel_parts = md.relative_to(wiki_root).parts
        if any(part.startswith("_") for part in rel_parts):
            continue
        if rel_parts and rel_parts[0] == "raw":
            continue
        yield md
