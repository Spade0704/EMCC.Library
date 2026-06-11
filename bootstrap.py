#!/usr/bin/env python3
"""Codex v1.1 bootstrap — canonical portfolio scaffold (spec section c).

Generates the canonical portfolio folder layout per
`tasks/plans/portfolio-folder-structure-spec.md` section (c). Bootstrap
is SCAFFOLD-ONLY — emits the skeleton (folders + `.gitkeep` markers +
root stub files) but does NOT copy Codex's `_scripts/` / `_template/` /
`_config/` contents into the consumer — with ONE deliberate carve-out
(CARTO-06 / M-A component 5, C2-council convention lock
"materialize-then-link"): the 6 ToC-advertised boilerplate wiki pages
(How-to-Use-This-Wiki, Glossary, Terminology-Rules, Update-Cascade,
File-Routing, Style-Guide) are materialized into `wiki.<name>/git/` as
real content so new wikis are never born with dead Home links. Sync
(`sync_from_kit.py`) remains the separate operation that pulls Codex
kit content into a consuming wiki.

CLI:

    python bootstrap.py <projectname> [--full | --minimal | --code | --website]
                                      [--dry-run] [--yes]

Modes:
    --full     (default) Canonical tree: 0-Inbox/ + Biz.Automation/
               + wiki.<name>/{local,git}/ + tasks/ + assets/ + root
               files (Index.md, CLAUDE.md, Cheatsheet.md,
               reorganization-instructions.<name>.md, .gitignore).
    --minimal  Thin braindump (aviation-career style): 0-Inbox/ +
               wiki.<name>/{local,git}/ + tasks/ + root files. No
               Biz.Automation/, no assets/, no Cheatsheet.md, no
               reorganization-instructions.<name>.md.
    --code     --full + <product-code-root>/.gitkeep placeholder +
               code-aware .gitignore additions.
    --website  --full + website/.gitkeep + web-aware .gitignore
               additions.

Idempotency + safety (spec c §"Idempotency + safety rules"):
    1. Refuse to overwrite non-empty `<projectname>/` unless --yes.
    2. Refuse outside cwd: only writes into a child of the current
       directory.
    3. No `git init` — first commit is operator's call.
    4. No `.claude/` creation — operator wires Claude Code per project.
    5. No network calls.

Pure stdlib per `CODEX_BUILD_SPEC_v1_3.md` §8 Hard Rule 1.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# Canonical folder lists per spec section (c).
# Each entry is a folder path RELATIVE to the project root. `.gitkeep`
# files are added to each so git tracks the empty folder.
# ---------------------------------------------------------------------------

CANONICAL_FOLDERS_FULL: Tuple[str, ...] = (
    "0-Inbox",
    "Biz.Automation",
    "Biz.Automation/wikisys.{projectname}/_scripts",
    "Biz.Automation/wikisys.{projectname}/_template",
    "Biz.Automation/wikisys.{projectname}/_config",
    "Biz.Automation/wikisys.{projectname}/_canon",
    "wiki.{projectname}/local",
    "wiki.{projectname}/git/raw",
    "wiki.{projectname}/git/ideas",
    "tasks",
    "assets/logos",
    "assets/brand",
    "assets/photos",
    "assets/videos",
    "assets/designs",
    "assets/generated",
)

CANONICAL_FOLDERS_MINIMAL: Tuple[str, ...] = (
    "0-Inbox",
    "wiki.{projectname}/local",
    "wiki.{projectname}/git",
    "tasks",
)


# --website adds a `website/.gitkeep` placeholder. --code does NOT emit
# a `<product-code-root>/.gitkeep` placeholder because the spec
# placeholder name `<product-code-root>` contains Win32-illegal chars
# (`<`, `>`); operators name + create the actual code folder themselves
# (Flutter `lib/`, Python `src/`, etc.). --code's contribution is the
# code-aware .gitignore additions (node_modules/, __pycache__/, build/,
# dist/, target/, *.egg-info/).
WEBSITE_ROOT = "website"


# Tasks markdown stub filenames (canonical four per spec a).
TASK_FILES: Tuple[str, ...] = ("todo.md", "sessions.md", "lessons.md", "archive.md")


# ---------------------------------------------------------------------------
# Stub content per spec section (c) §"File stubs".
# ---------------------------------------------------------------------------


def _stub_claude_md(projectname: str) -> str:
    return (
        "# CLAUDE.md — {name}\n"
        "\n"
        "[One-line description of what this project is.]\n"
        "\n"
        "## Read order (every new conversation)\n"
        "\n"
        "1. **`Index.md`** — file map + routing table.\n"
        "2. **`tasks/todo.md`** — current sprint.\n"
        "3. **`tasks/lessons.md`** — rules. Re-read before any code change.\n"
        "\n"
        "## Hard rules\n"
        "\n"
        "- [Project-specific non-negotiables.]\n"
        "- Do not delete anything. Move to `tasks/archive.md` or `0-Inbox/`.\n"
        "- Confidential content goes in `wiki.{name}/local/`. Public content "
        "goes in `wiki.{name}/git/`. Never confuse.\n"
        "\n"
        "## Memory architecture\n"
        "\n"
        "[R_* drawer pattern. Copy from tat_app or isommelier as starting point.]\n"
    ).format(name=projectname)


def _stub_index_md(projectname: str) -> str:
    return (
        "# INDEX\n"
        "\n"
        "Route lookups via this file. Read BEFORE searching the project.\n"
        "\n"
        "## Top-level\n"
        "\n"
        "| Folder / file | Purpose |\n"
        "|---|---|\n"
        "| `0-Inbox/` | Files awaiting Librarian sort. |\n"
        "| `Biz.Automation/` | Project automations. |\n"
        "| `Biz.Automation/wikisys.{name}/` | Wiki-system engine. |\n"
        "| `wiki.{name}/local/` | Confidential wiki content (gitignored). |\n"
        "| `wiki.{name}/git/` | Public wiki content. |\n"
        "| `tasks/` | Workflow tracking. |\n"
        "| `assets/` | Logos, brand, photos, videos, designs. |\n"
        "| `Index.md` | This file. |\n"
        "| `CLAUDE.md` | Operating rules + memory. |\n"
        "| `Cheatsheet.md` | Quick reference. |\n"
        "\n"
        "## Wiki topics\n"
        "\n"
        "[One row per topic as the wiki grows. Note local vs git per row.]\n"
        "\n"
        "## Automations\n"
        "\n"
        "[One row per automation. Pair each with its `<name>.doc/` folder "
        "under `wiki.{name}/git/`.]\n"
    ).format(name=projectname)


def _stub_todo_md() -> str:
    return (
        "# Todo\n"
        "\n"
        "## Active\n"
        "\n"
        "- [ ] Bootstrap'd. Replace with actual work.\n"
        "\n"
        "## Backlog\n"
        "\n"
        "(empty)\n"
    )


def _stub_sessions_md() -> str:
    return (
        "# Sessions\n"
        "\n"
        "Newest at top. Markers: ✓ verified | Δ changed | ! blocker | "
        "Next pointer.\n"
        "\n"
        "## Bootstrap\n"
        "\n"
        "- ✓ Project initialized via `bootstrap.py <projectname>`.\n"
        "- Next: define hard rules in CLAUDE.md, populate Index.md.\n"
    )


def _stub_lessons_md() -> str:
    return (
        "# Lessons\n"
        "\n"
        "Rules extracted from work in this project. Re-read before any "
        "code change.\n"
        "\n"
        "(empty — add rules as learned)\n"
    )


def _stub_archive_md() -> str:
    return (
        "# Archive\n"
        "\n"
        "Completed work. Newest at top.\n"
        "\n"
        "(empty)\n"
    )


def _stub_cheatsheet_md(projectname: str) -> str:
    return (
        "# Cheatsheet — {name}\n"
        "\n"
        "## Paths\n"
        "\n"
        "- Repo: [local path]\n"
        "- GitHub: [url]\n"
        "\n"
        "## Commands\n"
        "\n"
        "[Add as automations land.]\n"
    ).format(name=projectname)


def _stub_reorganization_md(projectname: str) -> str:
    return (
        "# reorganization-instructions.{name}.md\n"
        "\n"
        "> **Scope:** Per-project path-migration manifest for **{name}** only.\n"
        "> Cross-repo patterns (P1–P8), audit-hook contract, and the master index\n"
        "> of per-project files live in `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md`.\n"
        "> Read the master first for pattern definitions; come here for the concrete\n"
        "> {name}-side moves.\n"
        "\n"
        "> **Audience:** the Librarian agent in this repo, audit scripts, and any\n"
        "> Claude Code session that hits a \"file not found\" error referencing an\n"
        "> old path.\n"
        "\n"
        "> **Pair docs:** `EMCC.Library/tasks/plans/portfolio-folder-structure-spec.md`\n"
        "> (canonical layout decisions).\n"
        "\n"
        "---\n"
        "\n"
        "## {name} — per-project moves\n"
        "\n"
        "**Pre-migration state:** [describe the on-disk shape before the canonical\n"
        "layout was adopted — e.g., `wiki/` at root, custom builder output dirs,\n"
        "Title-Case task files, etc. If this project is greenfield (bootstrap-only),\n"
        "write \"Greenfield — no pre-migration content\" and skip the move tables.]\n"
        "\n"
        "**Migration moves** — [branch + commit range + date]\n"
        "\n"
        "| Old path | New path | Pattern | Status |\n"
        "|---|---|---|---|\n"
        "| _(add rows as moves land. Pattern column: P1–P8 per master, or `—` if no pattern applies.)_ | | | |\n"
        "\n"
        "## Internal callers updated\n"
        "\n"
        "[List scripts, configs, or docs whose path literals had to be rewritten\n"
        "after the moves above. Reference commit SHAs for traceability.]\n"
        "\n"
        "---\n"
        "\n"
        "## See also\n"
        "\n"
        "- `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md` (master) — patterns P1–P8,\n"
        "  audit hooks contract, per-project file index.\n"
        "- `EMCC.Library/tasks/plans/portfolio-folder-structure-spec.md` — canonical\n"
        "  layout decisions.\n"
    ).format(name=projectname)


def _stub_gitignore(mode: str) -> str:
    base = (
        "# OS\n"
        ".DS_Store\n"
        "Thumbs.db\n"
        "\n"
        "# Secrets\n"
        ".env\n"
        ".env.local\n"
        "*.key\n"
        "*.pem\n"
        "\n"
        "# Editor\n"
        ".vscode/\n"
        ".idea/\n"
        "\n"
        "# Wiki — private zone (gitignored)\n"
        "wiki.*/local/\n"
        "\n"
        "# Project-root private zone (uncomment if using eddyandwolff-style zoning)\n"
        "# Local/\n"
        "\n"
        "# Assets — heavy patterns (uncomment as needed)\n"
        "# assets/**/*.mp4\n"
        "# assets/**/*.mov\n"
        "# assets/**/*.psd\n"
        "# assets/photos/\n"
        "# assets/videos/\n"
    )
    if mode == "code":
        base += (
            "\n"
            "# Code build artifacts\n"
            "node_modules/\n"
            "__pycache__/\n"
            "build/\n"
            "dist/\n"
            "target/\n"
            "*.egg-info/\n"
        )
    elif mode == "website":
        base += (
            "\n"
            "# Website build artifacts\n"
            "node_modules/\n"
            ".next/\n"
            "dist/\n"
            "build/\n"
            ".vercel/\n"
        )
    return base


# ---------------------------------------------------------------------------
# Bootstrap engine.
# ---------------------------------------------------------------------------


def _materialize_folder_list(mode: str, projectname: str) -> List[str]:
    """Resolve the per-mode folder list, interpolating {projectname}."""
    if mode == "minimal":
        base = list(CANONICAL_FOLDERS_MINIMAL)
    else:  # full, code, website all start from --full
        base = list(CANONICAL_FOLDERS_FULL)
    if mode == "website":
        base.append(WEBSITE_ROOT)
    # --code intentionally adds no folder placeholder; operator names
    # and creates the actual code root (see comment on WEBSITE_ROOT).
    return [p.format(projectname=projectname) for p in base]


def _refuse_outside_cwd(target: Path, cwd: Path) -> Optional[str]:
    """Return error string if target is not a child of cwd, else None."""
    try:
        target.resolve().relative_to(cwd.resolve())
    except ValueError:
        return (
            "target {} is not a child of cwd {}; bootstrap refuses to write "
            "outside the current working directory (spec c §Idempotency rule #2)"
        ).format(target, cwd)
    return None


def _refuse_non_empty(target: Path, yes: bool) -> Optional[str]:
    """Return error string if target exists and is non-empty without --yes."""
    if target.exists() and any(target.iterdir()) and not yes:
        return (
            "target {} exists and is non-empty; pass --yes to override "
            "(spec c §Idempotency rule #1)"
        ).format(target)
    return None


def _emit_folders(target: Path, folder_rels: List[str], dry_run: bool) -> List[str]:
    """Create folders + .gitkeep markers. Returns list of created paths."""
    created = []
    for rel in folder_rels:
        folder = target / rel
        gitkeep = folder / ".gitkeep"
        if not dry_run:
            folder.mkdir(parents=True, exist_ok=True)
            if not gitkeep.exists():
                gitkeep.write_text("", encoding="utf-8")
        created.append(str(folder))
        created.append(str(gitkeep))
    return created


def _emit_root_stubs(
    target: Path,
    projectname: str,
    mode: str,
    dry_run: bool,
) -> List[str]:
    """Emit root stub files per spec (c). Returns list of created paths."""
    files: List[Tuple[Path, str]] = [
        (target / "CLAUDE.md", _stub_claude_md(projectname)),
        (target / "Index.md", _stub_index_md(projectname)),
        (target / ".gitignore", _stub_gitignore(mode)),
    ]
    # --minimal omits Cheatsheet.md + reorganization-instructions.<name>.md
    # per spec c (thin braindump projects don't need a migration manifest).
    if mode != "minimal":
        files.append((target / "Cheatsheet.md", _stub_cheatsheet_md(projectname)))
        files.append((
            target / "reorganization-instructions.{}.md".format(projectname),
            _stub_reorganization_md(projectname),
        ))
    created = []
    for path, content in files:
        if not dry_run and not path.exists():
            path.write_text(content, encoding="utf-8")
        created.append(str(path))
    return created


def _emit_task_stubs(target: Path, dry_run: bool) -> List[str]:
    """Emit tasks/{todo,sessions,lessons,archive}.md stubs."""
    tasks_dir = target / "tasks"
    stubs = {
        "todo.md": _stub_todo_md(),
        "sessions.md": _stub_sessions_md(),
        "lessons.md": _stub_lessons_md(),
        "archive.md": _stub_archive_md(),
    }
    created = []
    for fname, content in stubs.items():
        path = tasks_dir / fname
        if not dry_run:
            tasks_dir.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(content, encoding="utf-8")
        created.append(str(path))
    return created


def _emit_boilerplate_pages(target: Path, projectname: str, dry_run: bool) -> List[str]:
    """Materialize the 6 boilerplate wiki pages (CARTO-06 / M-A component 5).

    Materialize-then-link (C2 council convention lock: "every advertised hop
    resolves; the generator owns consistency") — new wikis are born with the
    six ToC-advertised boilerplate pages as real content, not dead links.
    Sourced from LIBRARY's own `_template/` (at bootstrap time the consumer
    has no vendored kit yet). Delegates to the kit's
    `materialize_boilerplate.py` (the same code the existing-wiki one-off
    loop runs); existing pages are always SKIPPED.
    """
    scripts_dir = Path(__file__).resolve().parent / "Biz.Automation" / "wikisys.library" / "_scripts"
    template_dir = scripts_dir.parent / "_template"
    sys.path.insert(0, str(scripts_dir))
    try:
        from materialize_boilerplate import materialize_boilerplate
    finally:
        sys.path.remove(str(scripts_dir))
    wiki_git = target / "wiki.{}".format(projectname) / "git"
    actions = materialize_boilerplate(
        wiki_git, template_dir, projectname, dry_run=dry_run
    )
    return ["{} {}".format(action, rel) for action, rel in actions]


def _post_bootstrap_checklist(projectname: str, mode: str) -> str:
    """Build the post-bootstrap stdout per spec (c)."""
    lines = [
        "Created {}/ with the canonical portfolio frame (mode={}).".format(projectname, mode),
        "",
        "Next steps:",
        "  1. cd {}".format(projectname),
        "  2. Edit CLAUDE.md: one-line description + hard rules.",
        "  3. Edit Index.md: rows for any non-stub folders you add.",
        "  4. Edit reorganization-instructions.{}.md: fill in the move table".format(projectname),
        "     once any pre-canonical content is migrated. Greenfield projects can",
        "     leave the stub intact or write \"Greenfield — no pre-migration content\".",
        "  5. Initialize Claude Code: copy a sibling project's .claude/ or run claude init.",
        "  6. git init && git add -A && git commit -m \"bootstrap\"",
        "  7. First real session: populate tasks/todo.md with the actual first task.",
        "",
        "Notes:",
        "  - wiki.{}/local/ is gitignored. Use it for confidential content.".format(projectname),
        "  - assets/ has heavy-file patterns commented in .gitignore — uncomment as needed.",
        "  - If your project ships a public website, use the --website flag (or add website/ manually).",
        "  - If your project ships product code (mobile app, CLI, library), use --code (or add <product-code-root>/ manually).",
    ]
    return "\n".join(lines) + "\n"


def bootstrap(
    projectname: str,
    mode: str = "full",
    dry_run: bool = False,
    yes: bool = False,
    cwd_override: Optional[Path] = None,
) -> int:
    """Bootstrap a project scaffold at <cwd>/<projectname>/.

    Returns 0 on success, non-zero on error.

    `cwd_override` is for tests; defaults to Path.cwd().
    """
    cwd = (cwd_override or Path.cwd()).resolve()
    target = (cwd / projectname).resolve()

    err = _refuse_outside_cwd(target, cwd)
    if err:
        sys.stderr.write("ERROR: " + err + "\n")
        return 1

    err = _refuse_non_empty(target, yes)
    if err:
        sys.stderr.write("ERROR: " + err + "\n")
        return 1

    folder_rels = _materialize_folder_list(mode, projectname)
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    folders = _emit_folders(target, folder_rels, dry_run)
    root_stubs = _emit_root_stubs(target, projectname, mode, dry_run)
    task_stubs = _emit_task_stubs(target, dry_run)
    boilerplate = _emit_boilerplate_pages(target, projectname, dry_run)

    mode_label = "DRY-RUN" if dry_run else "DONE"
    sys.stdout.write(
        "[{}] Bootstrap: {} (mode={})\n".format(mode_label, target, mode)
    )
    sys.stdout.write("  Folders: {}\n".format(len(folder_rels)))
    sys.stdout.write("  Root stubs: {}\n".format(len(root_stubs)))
    sys.stdout.write("  Task stubs: {}\n".format(len(task_stubs)))
    sys.stdout.write("  Boilerplate pages: {}\n".format(len(boilerplate)))
    sys.stdout.write(
        "  Total ops: {}\n".format(
            len(folders) + len(root_stubs) + len(task_stubs) + len(boilerplate)
        )
    )

    if not dry_run:
        sys.stdout.write("\n" + _post_bootstrap_checklist(projectname, mode))
    return 0


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bootstrap.py",
        description=(
            "Codex v1.1 bootstrap — scaffold a project per the canonical "
            "portfolio folder layout (tasks/plans/portfolio-folder-structure-spec.md "
            "section c)."
        ),
    )
    parser.add_argument(
        "projectname",
        help=(
            "Project name; used as folder name + suffix for wikisys.<name>/ "
            "and wiki.<name>/. Filesystem-safe characters only."
        ),
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--full",
        dest="mode",
        action="store_const",
        const="full",
        default="full",
        help="(default) Full canonical tree.",
    )
    mode_group.add_argument(
        "--minimal",
        dest="mode",
        action="store_const",
        const="minimal",
        help="Thin braindump scaffold.",
    )
    mode_group.add_argument(
        "--code",
        dest="mode",
        action="store_const",
        const="code",
        help="Full + <product-code-root>/ + code-aware .gitignore.",
    )
    mode_group.add_argument(
        "--website",
        dest="mode",
        action="store_const",
        const="website",
        help="Full + website/ + web-aware .gitignore.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without writing.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation if <projectname>/ exists non-empty.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return bootstrap(
        args.projectname,
        mode=args.mode,
        dry_run=args.dry_run,
        yes=args.yes,
    )


if __name__ == "__main__":
    sys.exit(main())
