"""P20 sync_from_kit.py — Sync operation per spec v1.3 §4.2.

Pulls updated infrastructure from a Codex installation into the consuming
wiki invoked from. Three file-classes per spec lines 275-279:

    OVERWRITE (full replacement, byte-equiv):
      - `_scripts/`                                      <- <codex>/_scripts/
      - `04-Contributing/PROJECT_WIKI_BUILD_SPEC.md`     <- <codex>/PROJECT_WIKI_BUILD_SPEC.md
      - `_context/INGEST_PROCEDURE.md`                   <- <codex>/INGEST_PROCEDURE.md
      - `_context/SEMANTIC_LINT_PROCEDURE.md`            <- <codex>/SEMANTIC_LINT_PROCEDURE.md
      - `_context/CODEX_LIBRARIAN.md`                    <- <codex>/CODEX_LIBRARIAN.md

    MERGE-NEW-ONLY (preserve existing wiki-side customization):
      - `_config/<filename>`                             <- <codex>/_config/<filename>
      - `_template/<filename>`                           <- <codex>/_template/<filename>

    NEVER TOUCHED (operator-customized; sync silently skips):
      - All content folders: 00-Start-Here/, 01-*/, _canon/, _sources/raw/,
        _confidential/, _decisions/, _brain_dump/, _dashboards/, _inbox/,
        public/, Home.md, README.md
      - `_context/CLAUDE_CONTEXT_RULES.md` (project-customized)

Usage (from inside the consuming wiki):
    python _scripts/sync_from_kit.py <path-to-Codex-installation>
        [--dry-run] [--force]

Flags:
    --dry-run    Preview planned actions without touching the filesystem.
    --force      Override the uncommitted-changes guard (spec line 281).

Exit codes:
    0  success (real-run or dry-run)
    1  any per-action FAILED during real-run
    2  uncommitted-changes guard refused (--force overrides)
    3  source-missing at Codex install path (operator-actionable error)

Notes:
    - Pure stdlib (argparse + shutil + subprocess + pathlib).
    - `__pycache__` dirs filtered out at copy time AND wiped post-copy
      under `_scripts/` (dual defense per S037-T3 R3).
    - `git status --porcelain` invoked in wiki cwd; non-empty output OR
      git error (no-git-binary / not-a-repo) trips the guard.
    - Sync is CLI-only; not designed for in-process invocation.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, NamedTuple, Optional, Tuple


SCRIPTS_DIR = "_scripts"
CONTEXT_DIR = "_context"
CONFIG_DIR = "_config"
TEMPLATE_DIR = "_template"

PROJECT_WIKI_BUILD_SPEC_FILE = "PROJECT_WIKI_BUILD_SPEC.md"
WIKI_BUILD_SPEC_TARGET = "04-Contributing/PROJECT_WIKI_BUILD_SPEC.md"
INGEST_PROCEDURE_FILE = "INGEST_PROCEDURE.md"
SEMANTIC_LINT_PROCEDURE_FILE = "SEMANTIC_LINT_PROCEDURE.md"
CODEX_LIBRARIAN_FILE = "CODEX_LIBRARIAN.md"


class Action(NamedTuple):
    kind: str  # 'OVERWRITE' | 'MERGE-NEW' | 'SKIP'
    target: str  # wiki-relative path (display)
    source: str  # codex-relative path (display)
    target_abs: Path
    source_abs: Path
    is_dir: bool  # True for the _scripts/ dir replacement; False for single-file ops


def _required_sources(codex: Path) -> List[Tuple[str, Path, bool]]:
    """Enumerate (label, path, is_dir) tuples for the AC10 pre-flight check."""
    return [
        (SCRIPTS_DIR, codex / SCRIPTS_DIR, True),
        (PROJECT_WIKI_BUILD_SPEC_FILE, codex / PROJECT_WIKI_BUILD_SPEC_FILE, False),
        (INGEST_PROCEDURE_FILE, codex / INGEST_PROCEDURE_FILE, False),
        (SEMANTIC_LINT_PROCEDURE_FILE, codex / SEMANTIC_LINT_PROCEDURE_FILE, False),
        (CODEX_LIBRARIAN_FILE, codex / CODEX_LIBRARIAN_FILE, False),
        (CONFIG_DIR, codex / CONFIG_DIR, True),
        (TEMPLATE_DIR, codex / TEMPLATE_DIR, True),
    ]


def _check_sources(codex: Path) -> List[str]:
    """Return list of missing-source labels; empty if all present."""
    missing = []
    for label, path, is_dir in _required_sources(codex):
        if is_dir:
            if not path.is_dir():
                missing.append(label + "/")
        else:
            if not path.is_file():
                missing.append(label)
    return missing


def _check_guard(wiki: Path) -> Optional[str]:
    """Return guard-trip reason string, or None if wiki is clean.

    Non-clean conditions: uncommitted git changes, missing git binary,
    not-a-git-repo. All trip the guard; `--force` overrides.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(wiki),
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return "git binary not found in PATH"
    if result.returncode != 0:
        return "git error (not a git repository or other failure): " + result.stderr.strip()
    if result.stdout.strip():
        return "uncommitted changes:\n" + result.stdout.rstrip()
    return None


def _build_plan(codex: Path, wiki: Path) -> List[Action]:
    """Enumerate per-file actions in execution order."""
    actions: List[Action] = []

    actions.append(Action(
        kind="OVERWRITE",
        target=SCRIPTS_DIR + "/",
        source=SCRIPTS_DIR + "/",
        target_abs=wiki / SCRIPTS_DIR,
        source_abs=codex / SCRIPTS_DIR,
        is_dir=True,
    ))
    actions.append(Action(
        kind="OVERWRITE",
        target=WIKI_BUILD_SPEC_TARGET,
        source=PROJECT_WIKI_BUILD_SPEC_FILE,
        target_abs=wiki / WIKI_BUILD_SPEC_TARGET,
        source_abs=codex / PROJECT_WIKI_BUILD_SPEC_FILE,
        is_dir=False,
    ))
    actions.append(Action(
        kind="OVERWRITE",
        target=CONTEXT_DIR + "/" + INGEST_PROCEDURE_FILE,
        source=INGEST_PROCEDURE_FILE,
        target_abs=wiki / CONTEXT_DIR / INGEST_PROCEDURE_FILE,
        source_abs=codex / INGEST_PROCEDURE_FILE,
        is_dir=False,
    ))
    actions.append(Action(
        kind="OVERWRITE",
        target=CONTEXT_DIR + "/" + SEMANTIC_LINT_PROCEDURE_FILE,
        source=SEMANTIC_LINT_PROCEDURE_FILE,
        target_abs=wiki / CONTEXT_DIR / SEMANTIC_LINT_PROCEDURE_FILE,
        source_abs=codex / SEMANTIC_LINT_PROCEDURE_FILE,
        is_dir=False,
    ))
    actions.append(Action(
        kind="OVERWRITE",
        target=CONTEXT_DIR + "/" + CODEX_LIBRARIAN_FILE,
        source=CODEX_LIBRARIAN_FILE,
        target_abs=wiki / CONTEXT_DIR / CODEX_LIBRARIAN_FILE,
        source_abs=codex / CODEX_LIBRARIAN_FILE,
        is_dir=False,
    ))

    for class_dir in (CONFIG_DIR, TEMPLATE_DIR):
        src_root = codex / class_dir
        for src in sorted(src_root.iterdir()):
            if not src.is_file():
                continue
            target_rel = class_dir + "/" + src.name
            target_abs = wiki / class_dir / src.name
            kind = "SKIP" if target_abs.exists() else "MERGE-NEW"
            actions.append(Action(
                kind=kind,
                target=target_rel,
                source=class_dir + "/" + src.name,
                target_abs=target_abs,
                source_abs=src,
                is_dir=False,
            ))

    return actions


def _format_action_line(action: Action, suffix: str = "") -> str:
    """Format an action for stdout."""
    if action.kind == "SKIP":
        body = "[SKIP] {} (existing customization preserved)".format(action.target)
    else:
        body = "[{}] {} <- {}".format(action.kind, action.target, action.source)
    if suffix:
        body = body + " " + suffix
    return body


def _apply_action(action: Action) -> None:
    """Execute one action against the filesystem. Raises on failure."""
    if action.kind == "SKIP":
        return
    if action.is_dir:
        if action.target_abs.exists():
            shutil.rmtree(action.target_abs)
        action.target_abs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            action.source_abs,
            action.target_abs,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        _wipe_pycache(action.target_abs)
    else:
        action.target_abs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(action.source_abs, action.target_abs)


def _wipe_pycache(root: Path) -> None:
    """Walk `root` and rmtree any `__pycache__` dirs (defense in depth)."""
    for path in root.rglob("__pycache__"):
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)


def _print_summary(actions: List[Action], stdout) -> None:
    """Print Overwrites/Merge-new/Skipped counts footer."""
    n_over = sum(1 for a in actions if a.kind == "OVERWRITE")
    n_merge = sum(1 for a in actions if a.kind == "MERGE-NEW")
    n_skip = sum(1 for a in actions if a.kind == "SKIP")
    print(
        "Overwrites: {} | Merge-new: {} | Skipped: {}".format(
            n_over, n_merge, n_skip
        ),
        file=stdout,
    )


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="sync_from_kit.py",
        description="Pull updated infrastructure from a Codex install into the consuming wiki (run from inside the wiki).",
    )
    parser.add_argument(
        "codex_install_path",
        help="Path to the Codex installation root.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview planned actions without touching the filesystem.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Override the uncommitted-changes guard.",
    )
    return parser.parse_args(argv)


def _main(argv=None, wiki_root=None, stdout=None, stderr=None) -> int:
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    args = _parse_args(argv)
    codex = Path(args.codex_install_path).resolve()
    wiki = Path(wiki_root).resolve() if wiki_root is not None else Path.cwd().resolve()

    missing = _check_sources(codex)
    if missing:
        print(
            "error: refusing to sync; required source(s) missing at Codex install path {}:".format(codex),
            file=stderr,
        )
        for label in missing:
            print("  - " + label, file=stderr)
        return 3

    guard_reason = _check_guard(wiki)
    if guard_reason is not None:
        if not args.force:
            print(
                "error: refusing to sync; wiki has " + guard_reason,
                file=stderr,
            )
            print("use --force to override.", file=stderr)
            return 2
        print(
            "WARN: --force passed; proceeding despite: " + guard_reason.split("\n", 1)[0],
            file=stderr,
        )

    actions = _build_plan(codex, wiki)

    if args.dry_run:
        for action in actions:
            print(_format_action_line(action), file=stdout)
        _print_summary(actions, stdout)
        return 0

    any_failed = False
    for action in actions:
        try:
            _apply_action(action)
            print(_format_action_line(action, "[OK]"), file=stdout)
        except Exception as exc:
            any_failed = True
            print(
                _format_action_line(
                    action,
                    "[FAILED: {}: {}]".format(type(exc).__name__, exc),
                ),
                file=stdout,
            )
    _print_summary(actions, stdout)
    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(_main())
