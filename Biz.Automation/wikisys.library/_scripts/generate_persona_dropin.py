"""Generate the project-root Librarian persona drop-in from the canonical spec.

OBS-4 closure (build-time generation; S002 Auditor info observation). The
drop-in at `.claude/personas/CLAUDE.librarian.md` used to be a hand-maintained
*summary* of the canonical `wiki.<name>/git/codex/CODEX_LIBRARIAN.md` — free to
drift as the canonical evolved. This script makes the drop-in a GENERATED
reflection of the canonical: a generated frontmatter + a DO-NOT-EDIT banner
followed by the canonical body verbatim. Drift becomes structurally impossible
— edit the canonical, regenerate; the drift guard test fails CI if the on-disk
drop-in diverges from the canonical.

Determinism note: the generated `last_updated` is taken from the *canonical's*
frontmatter, NOT today's date, so regeneration is a pure function of the
canonical (the `--check` drift guard is stable across days).

Usage:
    python generate_persona_dropin.py            # regenerate in place
    python generate_persona_dropin.py --check    # exit 1 if on-disk has drifted
    python generate_persona_dropin.py --canonical PATH --target PATH

Exit codes:
    0  wrote (or --check: in sync)
    1  --check: on-disk drop-in drifted from canonical
    2  canonical or target could not be resolved

Pure stdlib.
"""

import argparse
import sys
from pathlib import Path

from _lib import frontmatter


_LOADED_VIA = (
    "declared; not loaded by lattice_session_start.py — VALID_ROLES enumerates "
    "the Nexus four only. Librarian operates inside consumed wikis bootstrapped "
    "by Codex, not inside Project Codex itself."
)


def _banner(canonical_rel):
    return (
        "<!-- GENERATED FILE — DO NOT EDIT BY HAND.\n"
        "     Source of truth: {rel}\n"
        "     Regenerate: python Biz.Automation/wikisys.library/_scripts/"
        "generate_persona_dropin.py\n"
        "     Drift guard: tests/test_persona_dropin.py -->"
    ).format(rel=canonical_rel)


def _strip_frontmatter(text):
    """Return the markdown body with any leading frontmatter block removed."""
    lines = text.split("\n")
    close = frontmatter.find_frontmatter_close(lines)
    if close is None:
        return text.lstrip("\n")
    return "\n".join(lines[close + 1:]).lstrip("\n")


def render_dropin(canonical_text, canonical_rel):
    """Render the generated drop-in content from the canonical doc text.

    Pure function of (canonical_text, canonical_rel) — deterministic. The
    `last_updated` is sourced from the canonical's own frontmatter so the
    output never depends on wall-clock time.
    """
    parsed = frontmatter.parse_frontmatter(canonical_text) or {}
    last_updated = parsed.get("last_updated", "")
    body = _strip_frontmatter(canonical_text)
    header = "\n".join([
        "---",
        'title: "CLAUDE.librarian — Librarian persona drop-in (generated)"',
        'canonical_source: "{}"'.format(canonical_rel),
        'loaded_via: "{}"'.format(_LOADED_VIA),
        "last_updated: {}".format(last_updated),
        "---",
        "",
        _banner(canonical_rel),
        "",
        "",
    ])
    out = header + body
    if not out.endswith("\n"):
        out += "\n"
    return out


def _canonical_rel(canonical):
    """Stable posix rel-path for the canonical (for the banner + fm pointer).

    Prefer the path from the `wiki.*` ancestor down (e.g.
    `wiki.codex/git/codex/CODEX_LIBRARIAN.md`) so the value is independent of
    where the install root sits on disk — keeps generation deterministic for
    explicit `--canonical` overrides and fixtures alike. Falls back to the
    basename if no `wiki.*` component is present.
    """
    parts = canonical.parts
    for i, part in enumerate(parts):
        if part.startswith("wiki."):
            return "/".join(parts[i:])
    return canonical.name


def _resolve_paths(args):
    """Resolve (canonical, target). Raises FileNotFoundError if undiscoverable."""
    install = frontmatter._find_install_root(Path(__file__).resolve())

    if args.canonical is not None:
        canonical = Path(args.canonical).resolve()
    elif install is not None:
        canonical = next(
            iter(sorted(install.glob("wiki.*/git/codex/CODEX_LIBRARIAN.md"))),
            None,
        )
        if canonical is None:
            raise FileNotFoundError(
                "no wiki.*/git/codex/CODEX_LIBRARIAN.md under {}".format(install)
            )
    else:
        raise FileNotFoundError("could not locate install root from script path")

    if args.target is not None:
        target = Path(args.target).resolve()
    elif install is not None:
        target = install / ".claude" / "personas" / "CLAUDE.librarian.md"
    else:
        raise FileNotFoundError("could not locate install root from script path")

    return canonical, target


def main(argv=None):
    parser = argparse.ArgumentParser(prog="generate_persona_dropin.py")
    parser.add_argument("--check", action="store_true",
                        help="verify on-disk drop-in matches canonical; exit 1 on drift")
    parser.add_argument("--canonical", default=None,
                        help="path to CODEX_LIBRARIAN.md (default: auto-detected)")
    parser.add_argument("--target", default=None,
                        help="path to write the drop-in (default: .claude/personas/CLAUDE.librarian.md)")
    args = parser.parse_args(argv)

    try:
        canonical, target = _resolve_paths(args)
    except FileNotFoundError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2

    if not canonical.is_file():
        print("error: canonical not found: {}".format(canonical), file=sys.stderr)
        return 2

    canonical_rel = _canonical_rel(canonical)
    expected = render_dropin(canonical.read_text(encoding="utf-8"), canonical_rel)

    if args.check:
        if not target.is_file():
            print("drift: target missing: {}".format(target), file=sys.stderr)
            return 1
        actual = target.read_text(encoding="utf-8")
        if actual != expected:
            print(
                "drift: {} is out of sync with {} — run "
                "generate_persona_dropin.py".format(
                    target.name, canonical_rel
                ),
                file=sys.stderr,
            )
            return 1
        print("in sync: {} matches {}".format(target.name, canonical_rel))
        return 0

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(expected, encoding="utf-8")
    print("wrote {} from {}".format(target, canonical_rel))
    return 0


if __name__ == "__main__":
    sys.exit(main())
