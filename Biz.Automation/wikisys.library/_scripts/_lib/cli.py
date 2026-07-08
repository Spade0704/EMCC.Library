"""Shared CLI helper for the `--wiki-root` content-root override.

MI-17 full closure (post-S004 carry). Before this, only `update_dashboards.py`
accepted an explicit root (via a bare positional). Every other P-script relied
solely on the module-level `frontmatter.find_wiki_content_root()` default, so an
operator could not point a single script at an arbitrary wiki (e.g. a sibling
consumer's `wiki.mentor/git/`) without `cd`-ing or editing the module. This
helper standardises the override across all standalone P-script `__main__`
blocks. Pure stdlib.
"""
# @component Library-infra[cli]

import argparse
from pathlib import Path


def resolve_cli_wiki_root(default, argv=None, prog=None):
    """Return the effective content root for a standalone P-script run.

    Accepts the override either as `--wiki-root PATH` or as a bare positional
    argument (back-compat with `update_dashboards.py`'s prior positional
    contract). The named form wins if both are supplied. Falls back to
    `default` (the module-level `frontmatter.find_wiki_content_root()` result)
    when no override is given.
    """
    parser = argparse.ArgumentParser(prog=prog, add_help=True)
    parser.add_argument(
        "wiki_root",
        nargs="?",
        default=None,
        help="content root to operate on (default: auto-detected)",
    )
    parser.add_argument(
        "--wiki-root",
        dest="wiki_root_opt",
        default=None,
        help="content root (named form; overrides the positional form)",
    )
    args = parser.parse_args(argv)
    chosen = args.wiki_root_opt if args.wiki_root_opt is not None else args.wiki_root
    if chosen is None:
        return default
    return Path(chosen).resolve()
