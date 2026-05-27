"""P18 scaffold_source.py — Create a new _inbox/ entry for ingest (v1.1).

Per CODEX_BUILD_SPEC_v1_3.md §2.4 + L581 + L173-178:
  - Accepts a local file path or URL argument.
  - Local file: copy the content into `_inbox/<basename>.md` with the
    reduced source-file frontmatter (source / ingested_date / status).
  - URL: NO HTTP fetch (Codex is offline-only + dependency-free).
    Create placeholder `_inbox/<slug>.md` with frontmatter; stdout
    instructs the operator to paste source content before ingest.

Reduced source-file frontmatter (spec L173-178):
    source: "<citation>"
    ingested_date: YYYY-MM-DD     # date scaffolded, not date ingested
    status: pending_triage         # ingest flips to `ingested` on archive

Usage:
    python _scripts/scaffold_source.py <path-or-url>

URL detection is prefix-based: `http://` or `https://` -> URL path;
anything else is treated as a local file path. Refuses to overwrite an
existing file.

Pure stdlib per spec §8 Hard Rule 1.
"""

import argparse
import sys
from datetime import date
from pathlib import Path


INBOX_DIR = "_inbox"
URL_PREFIXES = ("http://", "https://")


def _slugify(text: str) -> str:
    """Lowercase + alphanumeric+dash; collapse non-alphanumeric runs; strip."""
    out = []
    prev_dash = True
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).rstrip("-") or "untitled"


def _is_url(arg: str) -> bool:
    """Prefix-based URL detection (offline-safe; no filesystem probe)."""
    return arg.startswith(URL_PREFIXES)


def _render_frontmatter(source: str, body: str = "") -> str:
    """Emit reduced source-file frontmatter per spec L173-178."""
    today = date.today().isoformat()
    fm = (
        "---\n"
        'source: "' + source + '"\n'
        "ingested_date: " + today + "\n"
        "status: pending_triage\n"
        "---\n"
        "\n"
    )
    return fm + body


def _main(argv=None, wiki_root=None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a new _inbox/ entry for ingest."
    )
    parser.add_argument(
        "path_or_url",
        help="Local file path or URL (http:// or https://)",
    )
    args = parser.parse_args(argv)

    if wiki_root is None:
        wiki_root = Path.cwd()

    inbox = wiki_root / INBOX_DIR
    inbox.mkdir(parents=True, exist_ok=True)

    if _is_url(args.path_or_url):
        slug = _slugify(args.path_or_url)
        target = inbox / (slug + ".md")
        if target.exists():
            sys.stderr.write(
                "error: file already exists: "
                + target.relative_to(wiki_root).as_posix()
                + "\n"
            )
            return 1
        body = (
            "<!-- paste the source content below this line. This script "
            "does not fetch URLs (Codex is offline-only + dependency-free). "
            "-->\n"
        )
        target.write_text(
            _render_frontmatter(args.path_or_url, body), encoding="utf-8"
        )
        rel = target.relative_to(wiki_root).as_posix()
        sys.stdout.write("created placeholder: " + rel + "\n")
        sys.stdout.write(
            "next step: paste source content into "
            + rel
            + " before running ingest.\n"
        )
        return 0

    src = Path(args.path_or_url)
    if not src.is_file():
        sys.stderr.write(
            "error: not a file or recognized URL: " + str(src) + "\n"
        )
        return 1
    target = inbox / (src.stem + ".md")
    if target.exists():
        sys.stderr.write(
            "error: file already exists: "
            + target.relative_to(wiki_root).as_posix()
            + "\n"
        )
        return 1
    body = src.read_text(encoding="utf-8", errors="replace")
    target.write_text(
        _render_frontmatter(str(src), body), encoding="utf-8"
    )
    sys.stdout.write(
        "created: " + target.relative_to(wiki_root).as_posix() + "\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(_main())
