#!/usr/bin/env python3
"""Materialize the 6 boilerplate wiki pages from templates (CARTO-06, M-A component 5).

Convention lock (C2 council, 2026-06-10, chairman resolution 2): "every advertised
hop resolves; the GENERATOR owns consistency" — materialize-then-link. The wiki
Home ToCs ship links to six boilerplate pages that previously existed only as
`_template/` `__SEP__` files, so every bootstrapped wiki was born with dead links.

The six pages:
    00-Start-Here/How-to-Use-This-Wiki.md
    00-Start-Here/Glossary.md
    00-Start-Here/Terminology-Rules.md
    04-Contributing/Update-Cascade.md
    04-Contributing/File-Routing.md
    04-Contributing/Style-Guide.md

Behavior:
    - Decodes `__SEP__` template names to real paths under the wiki content root.
    - Substitutes ONLY `<Project Name>` and `<YYYY-MM-DD>`; all other angle-bracket
      tokens are example content inside the templates and ship verbatim.
    - IDEMPOTENT + consumer-safe: an existing page is always SKIPPED (materialized
      pages become consumer content the moment they land — re-running never
      clobbers curation; upstream template improvements propagate to NEW wikis
      only, per the same MERGE-NEW philosophy as Sync's `_template/` lane).
    - Used two ways: imported by EMCC.Library `bootstrap.py` (new wikis are born
      with resolving ToCs) and run standalone from a consumer root for the
      one-off existing-wiki loop (M-A component 5/6).

Standalone CLI (from inside the consumer project root):
    python <kit>/_scripts/materialize_boilerplate.py [--dry-run]
        [--consumer-name X] [--template-dir PATH] [--project-name X]

Pure stdlib per `CODEX_BUILD_SPEC_v1_3.md` §8 Hard Rule 1.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

BOILERPLATE_TEMPLATES = (
    "00-Start-Here__SEP__How-to-Use-This-Wiki.md",
    "00-Start-Here__SEP__Glossary.md",
    "00-Start-Here__SEP__Terminology-Rules.md",
    "04-Contributing__SEP__Update-Cascade.md",
    "04-Contributing__SEP__File-Routing.md",
    "04-Contributing__SEP__Style-Guide.md",
)

SEP = "__SEP__"


def decode_sep(template_name: str) -> Path:
    """`00-Start-Here__SEP__Glossary.md` -> Path('00-Start-Here/Glossary.md')."""
    return Path(*template_name.split(SEP))


def materialize_boilerplate(
    wiki_git_root: Path,
    template_dir: Path,
    project_name: str,
    today: Optional[date] = None,
    dry_run: bool = False,
) -> List[Tuple[str, str]]:
    """Write the six boilerplate pages into `wiki_git_root`; return action tuples.

    Returns a list of (action, relpath) where action is one of:
      CREATE  — page written (placeholders substituted)
      SKIP    — page already exists (consumer content; never clobbered)
      MISSING — template absent at `template_dir` (reported, not fatal)
    """
    today = today or date.today()
    actions: List[Tuple[str, str]] = []
    for tname in BOILERPLATE_TEMPLATES:
        rel = decode_sep(tname)
        src = template_dir / tname
        dest = wiki_git_root / rel
        if not src.is_file():
            actions.append(("MISSING", rel.as_posix()))
            continue
        if dest.exists():
            actions.append(("SKIP", rel.as_posix()))
            continue
        content = (
            src.read_text(encoding="utf-8")
            .replace("<Project Name>", project_name)
            .replace("<YYYY-MM-DD>", today.isoformat())
        )
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
        actions.append(("CREATE", rel.as_posix()))
    return actions


def _discover(consumer_root: Path, override: Optional[str]) -> Optional[str]:
    """Consumer-name discovery, mirroring sync_from_kit (wikisys.* + wiki.*/git pair)."""
    if override:
        return override
    biz = consumer_root / "Biz.Automation"
    if not biz.is_dir():
        return None
    matches = []
    for entry in sorted(biz.iterdir()):
        if entry.is_dir() and entry.name.startswith("wikisys."):
            name = entry.name[len("wikisys."):]
            if (consumer_root / ("wiki." + name) / "git").is_dir():
                matches.append(name)
    return matches[0] if len(matches) == 1 else None


def main(argv=None, consumer_root: Optional[Path] = None) -> int:
    p = argparse.ArgumentParser(prog="materialize_boilerplate.py")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--consumer-name", default=None)
    p.add_argument("--template-dir", default=None,
                   help="Defaults to the consumer's vendored wikisys.<name>/_template/.")
    p.add_argument("--project-name", default=None,
                   help="Defaults to the discovered consumer name.")
    args = p.parse_args(argv)

    root = (consumer_root or Path.cwd()).resolve()
    name = _discover(root, args.consumer_name)
    if name is None:
        print("error: could not discover consumer name; pass --consumer-name",
              file=sys.stderr)
        return 2
    template_dir = (Path(args.template_dir) if args.template_dir
                    else root / "Biz.Automation" / ("wikisys." + name) / "_template")
    wiki_git = root / ("wiki." + name) / "git"
    actions = materialize_boilerplate(
        wiki_git, template_dir, args.project_name or name, dry_run=args.dry_run)
    for action, rel in actions:
        print(f"[{action}] wiki.{name}/git/{rel}")
    created = sum(1 for a, _ in actions if a == "CREATE")
    print(f"Materialized: {created} | Skipped: {sum(1 for a, _ in actions if a == 'SKIP')} "
          f"| Missing templates: {sum(1 for a, _ in actions if a == 'MISSING')}"
          + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
