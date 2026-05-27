"""P20 sync_from_kit.py — Sync operation per spec v1.3 §4.2 (v1.1 contract).

Pulls updated infrastructure from a Codex installation into the consuming
project (v1.1 canonical-layout consumers only; v1.0-shape support retired
in S004 — MI-16 closure).

The script is invoked from the consumer's project ROOT (not from inside
a wiki.<name>/ subfolder). It auto-discovers the consumer name by globbing
`Biz.Automation/wikisys.*` and `wiki.*/git`; if multiple or zero matches
are found, sync refuses with an actionable error.

Per spec v1.1 / S004:

    OVERWRITE (full replacement, byte-equiv):
      - `Biz.Automation/wikisys.<consumer>/_scripts/`
                                                <- <library>/Biz.Automation/wikisys.library/_scripts/
      - `Biz.Automation/wikisys.<consumer>/_context/INGEST_PROCEDURE.md`
                                                <- <library>/wiki.codex/git/codex/INGEST_PROCEDURE.md
      - `Biz.Automation/wikisys.<consumer>/_context/SEMANTIC_LINT_PROCEDURE.md`
                                                <- <library>/wiki.codex/git/codex/SEMANTIC_LINT_PROCEDURE.md
      - `Biz.Automation/wikisys.<consumer>/_context/CODEX_LIBRARIAN.md`
                                                <- <library>/wiki.codex/git/codex/CODEX_LIBRARIAN.md
      - `wiki.<consumer>/git/codex/PROJECT_WIKI_BUILD_SPEC.md`
                                                <- <library>/wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md

    MERGE-NEW-ONLY (preserve existing consumer-side customization):
      - `Biz.Automation/wikisys.<consumer>/_config/<filename>`
                                                <- <library>/Biz.Automation/wikisys.library/_config/<filename>
      - `Biz.Automation/wikisys.<consumer>/_template/<filename>`
                                                <- <library>/Biz.Automation/wikisys.library/_template/<filename>

    NEVER TOUCHED (operator-customized; sync silently skips):
      - All content folders under `wiki.<consumer>/git/`:
        `Home.md`, `00-Start-Here/`, `01-Authorities/`, `02-References/`,
        `03-Topics/`, `04-Contributing/`, `_archive/`, `raw/`, `README.md`
      - All content under `wiki.<consumer>/local/` (gitignored zone)
      - `Biz.Automation/wikisys.<consumer>/_canon/` (consumer's canon YAML)
      - `Biz.Automation/wikisys.<consumer>/_decisions/` (consumer's ingest log)
      - `Biz.Automation/wikisys.<consumer>/_dashboards/` (generated)
      - `Biz.Automation/wikisys.<consumer>/_context/CLAUDE_CONTEXT_RULES.md`
        (consumer-customized; the OVERWRITE list above covers only Library's
        verbatim-shipped procedure docs)
      - All root files: `CLAUDE.md`, `Index.md`, `Cheatsheet.md`,
        `emcc.modules.json`, `.gitignore`
      - `tasks/*.md`
      - `assets/*`, `0-Inbox/*`, `.claude/*`

Usage (from inside the consumer project root):
    python <library>/Biz.Automation/wikisys.library/_scripts/sync_from_kit.py <library>
        [--dry-run] [--force]

Flags:
    --dry-run    Preview planned actions without touching the filesystem.
    --force      Override the uncommitted-changes guard.

Exit codes:
    0  success (real-run or dry-run)
    1  any per-action FAILED during real-run
    2  uncommitted-changes guard refused (--force overrides)
    3  source-missing at Codex install path (operator-actionable error)
    4  consumer-discovery ambiguous (zero or multiple matches; --consumer-name overrides)

Notes:
    - Pure stdlib (argparse + shutil + subprocess + pathlib).
    - `__pycache__` dirs filtered out at copy time AND wiped post-copy
      under `_scripts/` (dual defense per S037-T3 R3).
    - `git status --porcelain` invoked in consumer cwd; non-empty output OR
      git error (no-git-binary / not-a-repo) trips the guard.
    - Sync is CLI-only; not designed for in-process invocation.
    - S004 closure of MI-16: v1.0-shape sync (writing to <wiki>/_scripts/
      etc. at wiki root) is no longer supported. Pre-S004 consumers must
      either (a) migrate to v1.1 first via the S004 Mentor-pattern playbook
      or (b) freeze at v1.0 and run a pre-S004 build of sync_from_kit.py.
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
CODEX_DIR = "codex"

# Library source-side path roots (v1.1).
WIKISYS_REL = "Biz.Automation/wikisys.library"
SPEC_DOCS_REL = "wiki.codex/git/codex"

# Spec doc filenames (delivered verbatim into consumer's wikisys + wiki).
PROJECT_WIKI_BUILD_SPEC_FILE = "PROJECT_WIKI_BUILD_SPEC.md"
INGEST_PROCEDURE_FILE = "INGEST_PROCEDURE.md"
SEMANTIC_LINT_PROCEDURE_FILE = "SEMANTIC_LINT_PROCEDURE.md"
CODEX_LIBRARIAN_FILE = "CODEX_LIBRARIAN.md"


class Action(NamedTuple):
    kind: str  # 'OVERWRITE' | 'MERGE-NEW' | 'SKIP'
    target: str  # consumer-relative path (display)
    source: str  # library-relative path (display)
    target_abs: Path
    source_abs: Path
    is_dir: bool  # True for the _scripts/ dir replacement; False for single-file ops


def _required_sources(library: Path) -> List[Tuple[str, Path, bool]]:
    """Enumerate (label, path, is_dir) tuples for the AC10 pre-flight check."""
    wikisys = library / WIKISYS_REL
    specs = library / SPEC_DOCS_REL
    return [
        (SCRIPTS_DIR, wikisys / SCRIPTS_DIR, True),
        (PROJECT_WIKI_BUILD_SPEC_FILE, specs / PROJECT_WIKI_BUILD_SPEC_FILE, False),
        (INGEST_PROCEDURE_FILE, specs / INGEST_PROCEDURE_FILE, False),
        (SEMANTIC_LINT_PROCEDURE_FILE, specs / SEMANTIC_LINT_PROCEDURE_FILE, False),
        (CODEX_LIBRARIAN_FILE, specs / CODEX_LIBRARIAN_FILE, False),
        (CONFIG_DIR, wikisys / CONFIG_DIR, True),
        (TEMPLATE_DIR, wikisys / TEMPLATE_DIR, True),
    ]


def _check_sources(library: Path) -> List[str]:
    """Return list of missing-source labels; empty if all present."""
    missing = []
    for label, path, is_dir in _required_sources(library):
        if is_dir:
            if not path.is_dir():
                missing.append(label + "/")
        else:
            if not path.is_file():
                missing.append(label)
    return missing


def _discover_consumer_name(consumer_root: Path, override: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """Return (consumer_name, error_reason). `consumer_name` is None on error.

    Discovery: glob `<consumer_root>/Biz.Automation/wikisys.*` and require
    exactly one matching dir name (minus the `wikisys.` prefix). If `override`
    is provided, validate it instead of globbing.
    """
    if override is not None:
        wikisys_dir = consumer_root / "Biz.Automation" / ("wikisys." + override)
        wiki_dir = consumer_root / ("wiki." + override) / "git"
        if not wikisys_dir.is_dir():
            return None, "consumer-name override '{}' did not match an existing Biz.Automation/wikisys.{}/ directory".format(override, override)
        if not wiki_dir.is_dir():
            return None, "consumer-name override '{}' did not match an existing wiki.{}/git/ directory".format(override, override)
        return override, None

    biz_root = consumer_root / "Biz.Automation"
    if not biz_root.is_dir():
        return None, "consumer is not at v1.1 canonical layout: missing Biz.Automation/ at {}".format(consumer_root)

    matches = []
    for entry in sorted(biz_root.iterdir()):
        if entry.is_dir() and entry.name.startswith("wikisys."):
            name = entry.name[len("wikisys."):]
            wiki_git = consumer_root / ("wiki." + name) / "git"
            if wiki_git.is_dir():
                matches.append(name)

    if not matches:
        return None, "could not discover consumer name: no matching pair Biz.Automation/wikisys.<name>/ + wiki.<name>/git/ at {}".format(consumer_root)
    if len(matches) > 1:
        return None, "consumer-discovery ambiguous: multiple wikisys.<name>/ matches found ({}). Use --consumer-name to disambiguate.".format(", ".join(matches))
    return matches[0], None


def _check_guard(consumer: Path) -> Optional[str]:
    """Return guard-trip reason string, or None if consumer tree is clean.

    Non-clean conditions: uncommitted git changes, missing git binary,
    not-a-git-repo. All trip the guard; `--force` overrides.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(consumer),
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


def _build_plan(library: Path, consumer: Path, consumer_name: str) -> List[Action]:
    """Enumerate per-file actions in execution order (v1.1 target paths)."""
    wikisys_src = library / WIKISYS_REL
    specs_src = library / SPEC_DOCS_REL

    consumer_wikisys = consumer / "Biz.Automation" / ("wikisys." + consumer_name)
    consumer_wiki_codex = consumer / ("wiki." + consumer_name) / "git" / CODEX_DIR

    actions: List[Action] = []

    actions.append(Action(
        kind="OVERWRITE",
        target="Biz.Automation/wikisys.{}/{}/".format(consumer_name, SCRIPTS_DIR),
        source=WIKISYS_REL + "/" + SCRIPTS_DIR + "/",
        target_abs=consumer_wikisys / SCRIPTS_DIR,
        source_abs=wikisys_src / SCRIPTS_DIR,
        is_dir=True,
    ))
    actions.append(Action(
        kind="OVERWRITE",
        target="wiki.{}/git/{}/{}".format(consumer_name, CODEX_DIR, PROJECT_WIKI_BUILD_SPEC_FILE),
        source=SPEC_DOCS_REL + "/" + PROJECT_WIKI_BUILD_SPEC_FILE,
        target_abs=consumer_wiki_codex / PROJECT_WIKI_BUILD_SPEC_FILE,
        source_abs=specs_src / PROJECT_WIKI_BUILD_SPEC_FILE,
        is_dir=False,
    ))
    for spec_file in (INGEST_PROCEDURE_FILE, SEMANTIC_LINT_PROCEDURE_FILE, CODEX_LIBRARIAN_FILE):
        actions.append(Action(
            kind="OVERWRITE",
            target="Biz.Automation/wikisys.{}/{}/{}".format(consumer_name, CONTEXT_DIR, spec_file),
            source=SPEC_DOCS_REL + "/" + spec_file,
            target_abs=consumer_wikisys / CONTEXT_DIR / spec_file,
            source_abs=specs_src / spec_file,
            is_dir=False,
        ))

    for class_dir in (CONFIG_DIR, TEMPLATE_DIR):
        src_root = wikisys_src / class_dir
        for src in sorted(src_root.iterdir()):
            if not src.is_file():
                continue
            target_rel = "Biz.Automation/wikisys.{}/{}/{}".format(consumer_name, class_dir, src.name)
            target_abs = consumer_wikisys / class_dir / src.name
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
        description="Pull updated infrastructure from a Codex (EMCC.Library) install into the consuming project (run from inside the consumer root).",
    )
    parser.add_argument(
        "library_install_path",
        help="Path to the EMCC.Library installation root.",
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
    parser.add_argument(
        "--consumer-name",
        default=None,
        help="Override consumer-name auto-discovery (e.g., 'mentor', 'tat'). Required only if multiple wikisys.*/ matches exist at consumer root.",
    )
    return parser.parse_args(argv)


def _main(argv=None, consumer_root=None, stdout=None, stderr=None) -> int:
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    args = _parse_args(argv)
    library = Path(args.library_install_path).resolve()
    consumer = Path(consumer_root).resolve() if consumer_root is not None else Path.cwd().resolve()

    missing = _check_sources(library)
    if missing:
        print(
            "error: refusing to sync; required source(s) missing at Library install path {}:".format(library),
            file=stderr,
        )
        for label in missing:
            print("  - " + label, file=stderr)
        return 3

    consumer_name, discover_err = _discover_consumer_name(consumer, args.consumer_name)
    if discover_err is not None:
        print("error: " + discover_err, file=stderr)
        return 4

    guard_reason = _check_guard(consumer)
    if guard_reason is not None:
        if not args.force:
            print(
                "error: refusing to sync; consumer has " + guard_reason,
                file=stderr,
            )
            print("use --force to override.", file=stderr)
            return 2
        print(
            "WARN: --force passed; proceeding despite: " + guard_reason.split("\n", 1)[0],
            file=stderr,
        )

    actions = _build_plan(library, consumer, consumer_name)

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
