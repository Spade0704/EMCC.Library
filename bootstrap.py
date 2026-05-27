#!/usr/bin/env python3
"""Codex wiki bootstrap — folder structure + script copy + template placement.

Phase 5 of CODEX_BUILD_SPEC_v1_2 — bootstraps a new consumer wiki at
<target-wiki-path>. P50a + P50b scope: CLI surface + folder structure per spec
§2.2 + 15-script copy from `_scripts/` (excludes Lattice infrastructure) +
template placement from `_template/` with `__SEP__` → `/` runtime substitution
per spec §4.1. Sync (P53) and full §7 Phase 6 self-test (P54) land later.
Pure stdlib per spec §8 Hard Rule 1.

CLI:
    python bootstrap.py <target-wiki-path>
    python bootstrap.py <target> --dry-run
    python bootstrap.py <target> --yes
"""

import argparse
import fnmatch
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Union


WIKI_FOLDERS = (
    "00-Start-Here",
    "01-Domain-1",
    "02-Domain-2",
    "04-Contributing",
    "Attachments",
    "public",
    "scripts",
    "_dashboards",
    "_decisions",
    "_inbox",
    "_sources",
    "_sources/raw",
    "_brain_dump",
    "_canon",
    "_context",
    "_scripts",
    "_config",
    "_confidential",
)

SCRIPT_IGNORE_PATTERNS = (
    "__pycache__",
    "launchers",
    "lattice_*.py",
    "lattice-bridge.py",
    "*.pyc",
)

TEMPLATE_DIR_NAME = "_template"
TEMPLATE_EXTENSIONS = (".md", ".yaml")
SEP_PLACEHOLDER = "__SEP__"


def _resolve_source_scripts_dir(override=None):
    if override is not None:
        return Path(override)
    return Path(__file__).resolve().parent / "_scripts"


def _ignore_callable(src_dir, names):
    ignored = []
    for name in names:
        for pattern in SCRIPT_IGNORE_PATTERNS:
            if fnmatch.fnmatch(name, pattern):
                ignored.append(name)
                break
    return ignored


def _walk_filtered_source(source):
    files = []

    def _walk(directory):
        if not directory.exists():
            return
        entries = list(directory.iterdir())
        ignored = set(_ignore_callable(str(directory), [e.name for e in entries]))
        for entry in entries:
            if entry.name in ignored:
                continue
            if entry.is_dir():
                _walk(entry)
            elif entry.is_file():
                files.append(entry)

    _walk(source)
    return files


def _confirm_overwrite(target):
    prompt = "Target " + str(target) + " is non-empty. Continue? [y/N]: "
    response = input(prompt).strip().lower()
    return response in ("y", "yes")


def _create_folders(target, dry_run):
    created = []
    for folder in WIKI_FOLDERS:
        folder_path = target / folder
        if not dry_run:
            folder_path.mkdir(parents=True, exist_ok=True)
        created.append(str(folder_path))
    return created


def _resolve_template_dir(override=None):
    if override is not None:
        return Path(override)
    return Path(__file__).resolve().parent / TEMPLATE_DIR_NAME


def _enumerate_templates(template_dir):
    if not template_dir.exists():
        return []
    return sorted(
        p for p in template_dir.iterdir()
        if p.is_file() and p.suffix in TEMPLATE_EXTENSIONS
    )


def _substitute_template_path(target, template_filename):
    rel = template_filename.replace(SEP_PLACEHOLDER, "/")
    return target / rel


def _copy_templates(template_dir, target, dry_run):
    templates = _enumerate_templates(template_dir)
    pairs = []
    for src in templates:
        dst = _substitute_template_path(target, src.name)
        pairs.append((src, dst))
        if dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return pairs


def _copy_scripts(source, target, dry_run):
    target_scripts = target / "_scripts"
    files = _walk_filtered_source(source)
    if not dry_run:
        shutil.copytree(
            source,
            target_scripts,
            dirs_exist_ok=True,
            ignore=_ignore_callable,
        )
    return [str(target_scripts / f.relative_to(source)) for f in files]


def bootstrap(
    target: Union[str, Path],
    dry_run: bool = False,
    yes: bool = False,
    source_override: Optional[Union[str, Path]] = None,
    template_override: Optional[Union[str, Path]] = None,
) -> int:
    """Bootstrap a wiki at target. Returns exit code (0=success, non-zero=error)."""
    source = _resolve_source_scripts_dir(source_override)
    if not source.exists():
        sys.stderr.write(
            "ERROR: source scripts directory not found: " + str(source) + "\n"
        )
        return 1

    template_dir = _resolve_template_dir(template_override)
    if not template_dir.exists():
        sys.stderr.write(
            "ERROR: template directory not found: " + str(template_dir) + "\n"
        )
        return 1

    if not _enumerate_templates(template_dir):
        sys.stderr.write(
            "ERROR: _template/ directory is empty (no .md or .yaml files): "
            + str(template_dir) + "\n"
        )
        return 1

    target = Path(target).resolve()

    if target.exists() and any(target.iterdir()):
        if not yes and not dry_run:
            if not _confirm_overwrite(target):
                sys.stdout.write("Aborted.\n")
                return 0

    try:
        folders = _create_folders(target, dry_run)
    except PermissionError as exc:
        sys.stderr.write(
            "ERROR: permission denied creating folders: " + str(exc) + "\n"
        )
        return 1

    try:
        scripts = _copy_scripts(source, target, dry_run)
    except PermissionError as exc:
        sys.stderr.write(
            "ERROR: permission denied copying scripts: " + str(exc) + "\n"
        )
        return 1

    try:
        templates = _copy_templates(template_dir, target, dry_run)
    except PermissionError as exc:
        sys.stderr.write(
            "ERROR: permission denied copying templates: " + str(exc) + "\n"
        )
        return 1

    mode = "DRY-RUN" if dry_run else "DONE"
    sys.stdout.write(
        "[" + mode + "] Bootstrap target: " + str(target) + "\n"
        "  Folders: " + str(len(folders)) + "\n"
        "  Scripts: " + str(len(scripts)) + "\n"
        "  Templates: " + str(len(templates)) + "\n"
        "  Total operations: "
        + str(len(folders) + len(scripts) + len(templates)) + "\n"
    )
    return 0


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="bootstrap.py",
        description=(
            "Codex wiki bootstrap — creates folder structure + copies scripts "
            "+ places templates with __SEP__ → / substitution at <target-wiki-path>."
        ),
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Target wiki path (created if absent; prompt-on-conflict if non-empty).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mode: list operations without writing.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive confirmation when target exists non-empty.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry-point. Parses argv and delegates to bootstrap(). Returns exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    return bootstrap(args.target, dry_run=args.dry_run, yes=args.yes)


if __name__ == "__main__":
    sys.exit(main())
