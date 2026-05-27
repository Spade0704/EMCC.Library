"""P17 scaffold_brain_dump.py — Create a new _brain_dump/ entry.

Per CLAUDE.md R_LOGIC D_SERVICES + CODEX_BUILD_SPEC_v1_3.md §2.3:
the entry is a `type: brain_dump` page with `dump_status: exploring`
as the initial state. Promotion to canon is always explicit (Principle
#9 — brain dump is quarantine).

Usage:
    python _scripts/scaffold_brain_dump.py "<title or slug>"

Creates `_brain_dump/<slug>.md` relative to the current working directory
(typically the wiki root). Refuses to overwrite an existing file.

Pure stdlib per spec §8 Hard Rule 1.
"""

import argparse
import sys
from datetime import date
from pathlib import Path


BRAIN_DUMP_DIR = "_brain_dump"


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


def _render_frontmatter(title: str) -> str:
    """Emit YAML-subset frontmatter + minimal body for a new brain dump."""
    today = date.today().isoformat()
    return (
        "---\n"
        'title: "' + title + '"\n'
        "type: brain_dump\n"
        "visibility: internal\n"
        "completion: 0\n"
        "status: outlined\n"
        "last_updated: " + today + "\n"
        "dependencies: []\n"
        "blocking_questions: []\n"
        "canon_sources: []\n"
        "unverified_claims: []\n"
        "dump_status: exploring\n"
        "migrated_to: []\n"
        "---\n"
        "\n"
        "# " + title + "\n"
        "\n"
        "<!-- exploring brain dump; promotion to canon is always explicit "
        "(spec Principle #9). When promoting, set dump_status and migrated_to. -->\n"
    )


def _main(argv=None, wiki_root=None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a new brain dump entry under _brain_dump/."
    )
    parser.add_argument("title", help="Title or slug for the brain dump")
    args = parser.parse_args(argv)

    if wiki_root is None:
        wiki_root = Path.cwd()

    slug = _slugify(args.title)
    target = wiki_root / BRAIN_DUMP_DIR / (slug + ".md")

    if target.exists():
        sys.stderr.write(
            "error: file already exists: "
            + target.relative_to(wiki_root).as_posix()
            + "\n"
        )
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render_frontmatter(args.title), encoding="utf-8")
    sys.stdout.write(
        "created: " + target.relative_to(wiki_root).as_posix() + "\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(_main())
