#!/usr/bin/env python3
"""Demote the 4 protocol boilerplate pages to stubs (boilerplate-location migration).

Convention (Operator-RATIFIED 2026-06-11; proposal at EMCC.Library
`tasks/plans/boilerplate-location-spec-proposal.md`; gate transcript
`EMCC.DFDU/tasks/delta-force/2026-06-11-boilerplate-stub-build.md`): the four
PROTOCOL boilerplate pages (How-to-Use-This-Wiki, Style-Guide, Update-Cascade,
File-Routing) live ONCE in the canonical Codex wiki (`wiki.codex/git/`);
consumer wikis carry generated stubs. Glossary + Terminology-Rules are PROJECT
content and stay per-repo full pages — this script never touches them.

One-off migration for wikis materialized before the convention. Guard (gate
revision R1 — the unmodified test): a page is demoted IFF its BODY (content
after the closing frontmatter fence) equals the OLD full template's body with
`<Project Name>` substituted. Frontmatter is excluded from the comparison
entirely, so cross_link-injected keys (`topics`/`tags`/`related_files`) and the
materialization date can never false-positive a modification. Any body
difference means consumer content: SKIP and report — never clobber (R4).

The OLD template bytes are read from Library git history at the pinned pre-stub
commit (the templates were byte-stable from the M-A wave kit `019168f` through
`08d87ac`, verified at the gate), so the comparison works even after the
templates in the working tree became stubs.

Structural exclusion (gate revision R2): refuses to run against EMCC.Library /
the `codex` wiki — the canonical copies must never be demoted.

Standalone CLI (from inside the consumer project root):
    python <library>/Biz.Automation/wikisys.library/_scripts/demote_boilerplate_stubs.py
        <library-path> [--dry-run] [--consumer-name X] [--project-name X]

Pure stdlib per `CODEX_BUILD_SPEC_v1_3.md` §8 Hard Rule 1.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

from materialize_boilerplate import SEP, decode_sep, _discover

# The 4 protocol pages (NOT Glossary / Terminology-Rules — those stay per-repo).
PROTOCOL_TEMPLATES = (
    "00-Start-Here__SEP__How-to-Use-This-Wiki.md",
    "04-Contributing__SEP__Update-Cascade.md",
    "04-Contributing__SEP__File-Routing.md",
    "04-Contributing__SEP__Style-Guide.md",
)

# Last Library commit carrying the FULL templates (pre-stub). Byte-stable for
# these 4 files from the M-A wave kit 019168f through this SHA (gate-verified).
OLD_TEMPLATE_SHA = "08d87ace40c870798877cc8cb2558cc205bbfac7"

_TEMPLATE_REL = "Biz.Automation/wikisys.library/_template/"


def _body(text: str) -> str:
    """Content after the closing frontmatter fence (whole text if no fence)."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + len("\n---\n"):]
    return text


def _old_template_body(library: Path, template_name: str) -> Optional[str]:
    """The pre-stub template body from Library git history (None if unreadable)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(library), "show",
             f"{OLD_TEMPLATE_SHA}:{_TEMPLATE_REL}{template_name}"],
            capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return _body(out.stdout)


def demote_boilerplate_stubs(
    wiki_git_root: Path,
    library: Path,
    project_name: str,
    today: Optional[date] = None,
    dry_run: bool = False,
    old_body_fn=None,
) -> List[Tuple[str, str]]:
    """Demote unmodified protocol pages under `wiki_git_root` to stubs.

    Returns (action, relpath) tuples; action is one of:
      DEMOTE         — body matched the old full template; stub written
      SKIP-MODIFIED  — body differs (consumer content; untouched, a finding)
      MISSING        — page absent (nothing to demote; materialize owns creation)
      NO-BASELINE    — old template unreadable from git history (untouched)
    """
    today = today or date.today()
    stub_dir = library / "Biz.Automation" / "wikisys.library" / "_template"
    if old_body_fn is None:
        old_body_fn = lambda name: _old_template_body(library, name)  # noqa: E731
    actions: List[Tuple[str, str]] = []
    for name in PROTOCOL_TEMPLATES:
        rel = decode_sep(name)
        page = wiki_git_root / rel
        if not page.is_file():
            actions.append(("MISSING", rel.as_posix()))
            continue
        old_body = old_body_fn(name)
        if old_body is None:
            actions.append(("NO-BASELINE", rel.as_posix()))
            continue
        expected = old_body.replace("<Project Name>", project_name)
        if _body(page.read_text(encoding="utf-8")) != expected:
            actions.append(("SKIP-MODIFIED", rel.as_posix()))
            continue
        stub = (
            (stub_dir / name).read_text(encoding="utf-8")
            .replace("<Project Name>", project_name)
            .replace("<YYYY-MM-DD>", today.isoformat())
        )
        if not dry_run:
            page.write_text(stub, encoding="utf-8")
        actions.append(("DEMOTE", rel.as_posix()))
    return actions


def main(argv=None, consumer_root: Optional[Path] = None) -> int:
    p = argparse.ArgumentParser(prog="demote_boilerplate_stubs.py")
    p.add_argument("library", help="path to the EMCC.Library clone")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--consumer-name", default=None)
    p.add_argument("--project-name", default=None,
                   help="Defaults to the discovered consumer name.")
    args = p.parse_args(argv)

    root = (consumer_root or Path.cwd()).resolve()
    library = Path(args.library).resolve()
    name = _discover(root, args.consumer_name)
    if name is None:
        print("error: could not discover consumer name; pass --consumer-name",
              file=sys.stderr)
        return 2
    # R2 structural exclusion: never demote the canonical copies.
    if name == "codex" or (library != root and (root / "wiki.codex" / "git").is_dir()) \
            or library == root:
        print("error: refusing to demote the canonical Codex wiki (EMCC.Library)",
              file=sys.stderr)
        return 3
    wiki_git = root / ("wiki." + name) / "git"
    actions = demote_boilerplate_stubs(
        wiki_git, library, args.project_name or name, dry_run=args.dry_run)
    for action, rel in actions:
        print(f"[{action}] wiki.{name}/git/{rel}")
    counts = {k: sum(1 for a, _ in actions if a == k)
              for k in ("DEMOTE", "SKIP-MODIFIED", "MISSING", "NO-BASELINE")}
    print("Demoted: {DEMOTE} | Skipped (modified): {SKIP-MODIFIED} | "
          "Missing: {MISSING} | No-baseline: {NO-BASELINE}".format(**counts)
          + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
