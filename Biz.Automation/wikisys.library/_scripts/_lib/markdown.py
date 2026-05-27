"""Shared markdown content-traversal and content-rewriting helpers.

Promoted from per-script duplication in P6 (validate_terminology) and P8
(validate_reveal_conceit) per BUILD_DISCIPLINE 3rd-consumer rule, ahead of
P9 (check_cross_refs) which would otherwise have triggered a third in-line
copy. Pure stdlib.

Public API:
    strip_code(text: str) -> str
        Replace fenced (```...``` or ~~~...~~~) and inline (`...`) code
        spans with whitespace. Preserves line counts so post-strip line
        numbers reference the same lines as the input.

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


def strip_code(text: str) -> str:
    """Replace fenced and inline code spans with whitespace, preserving line counts.

    Each char in a stripped span becomes a space except '\\n', which passes
    through. Line numbers in scan results therefore reference the original
    body line (and ultimately, after fm offset, the original file line).
    """
    text = _FENCED_RE.sub(_blank, text)
    text = _INLINE_RE.sub(_blank, text)
    return text


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
