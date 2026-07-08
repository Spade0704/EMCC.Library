"""audit_doc_pairing.py (S002 P0) — detect unpaired automations / orphan doc folders.

Per `tasks/plans/portfolio-folder-structure-spec.md` section (d) "New
scripts" and `wiki.codex/git/codex/CODEX_LIBRARIAN.md` Pairing-Audit
operation (S002 B7 extension).

Pairing contract:
    For every `Biz.Automation/<automationname>/` folder, there should be
    a paired `wiki.<projectname>/git/<automationname>.doc/` folder.
    Names match modulo the `.doc` suffix.

Findings:
    - **Unpaired automation:** `Biz.Automation/foo/` exists but no
      `wiki.<name>/git/foo.doc/` partner.
    - **Orphan doc folder:** `wiki.<name>/git/bar.doc/` exists but no
      `Biz.Automation/bar/` partner.

Output:
    A markdown dashboard at `<rootpath>/Biz.Automation/wikisys.<name>/_dashboards/doc-pairing.md`
    (or wherever the project's dashboards root resolves).

Stale-path sweep (OBS-1 / AC12 structural enforcement):
    `--stale-paths` runs an additional audit that scans the corpus for
    old-layout path fragments (pre-S002/S004 migration) and fails on any hit
    in a file NOT covered by an explicit allow-list. Patterns + allow-list are
    config-driven via `_config/stale_paths.yaml` (built-in defaults otherwise).
    Replaces the manual `git grep` sweep that under-counted (S002 Auditor OBS-1).

CLI:
    python audit_doc_pairing.py --root <projectroot>
        [--dashboard <path>] [--json]
    python audit_doc_pairing.py --root <projectroot> --stale-paths
        [--dashboard <path>] [--json]

Exit codes:
    0  no findings
    1  one or more findings emitted (pairing OR stale-path, per mode)
    2  malformed tree (e.g. no Biz.Automation/, no wiki.*/)
"""
# @component Codex[validators]

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import List, NamedTuple, Optional

from _lib import frontmatter


class Finding(NamedTuple):
    kind: str          # "unpaired-automation" | "orphan-doc-folder"
    path: str          # display path
    suggested_pair: str  # what the partner should be


class StalePathFinding(NamedTuple):
    path: str          # repo-relative posix path of the offending file
    line: int          # 1-indexed line number
    pattern: str       # the stale pattern matched
    snippet: str       # trimmed line text for context


# OBS-1 closure (AC12 structural enforcement). Defaults used when no
# _config/stale_paths.yaml is present; the config file overrides both lists.
_DEFAULT_STALE_PATTERNS = (
    "wiki.codex/_brain_dump",
    "wiki.codex/_dashboards",
    "Sources/Raw",
    "documents/codex/",
)
_DEFAULT_STALE_ALLOWLIST = (
    "MIGRATION-ISSUES.md",
    "REORGANIZATION-INSTRUCTIONS.md",
    "SOURCE-HISTORY.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "Index.md",
    "tasks/*.md",
    "tasks/plans/*.md",
    "tests/*.py",
)

# Always exempt, even when a config overrides the allow-list: these files
# DEFINE the patterns, so flagging them is nonsensical.
_STALE_ALWAYS_ALLOWLIST = (
    "Biz.Automation/wikisys.*/_config/stale_paths.yaml",
    "Biz.Automation/wikisys.*/_scripts/audit_doc_pairing.py",
)
_STALE_SCAN_SUFFIXES = (".md", ".py", ".yaml", ".yml", ".ps1")
# Directory name components that are never scanned (vcs, caches, generated,
# private/local zones, snapshot stores).
_STALE_SKIP_DIR_PARTS = frozenset((
    ".git", "__pycache__", ".snapshots", "_dashboards", "local",
))


def _find_biz_automation_dirs(root: Path) -> List[Path]:
    """Return automation folder paths under Biz.Automation/.

    Skips wikisys.<name>/ (system folder, not an automation) and any
    folder starting with `_` (private) or `.` (hidden).
    """
    biz = root / "Biz.Automation"
    if not biz.is_dir():
        return []
    out = []
    for entry in sorted(biz.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(("wikisys.", "_", ".")):
            continue
        out.append(entry)
    return out


def _find_doc_folders(root: Path) -> List[Path]:
    """Return `<name>.doc/` folders under any wiki.*/git/."""
    out = []
    for wiki in sorted(root.glob("wiki.*/git")):
        if not wiki.is_dir():
            continue
        for entry in sorted(wiki.iterdir()):
            if entry.is_dir() and entry.name.endswith(".doc"):
                out.append(entry)
    return out


def audit(root: Path) -> List[Finding]:
    """Run the pairing audit; return list of findings (empty = clean)."""
    findings: List[Finding] = []
    automations = _find_biz_automation_dirs(root)
    doc_folders = _find_doc_folders(root)
    doc_names = {p.name[:-4] for p in doc_folders}  # strip ".doc"
    auto_names = {p.name for p in automations}

    for auto_path in automations:
        if auto_path.name not in doc_names:
            # Suggest the most-likely pair location: the first wiki.*/git/
            wiki_git = next(root.glob("wiki.*/git"), None)
            suggested = (
                str(wiki_git / (auto_path.name + ".doc")) if wiki_git
                else "wiki.<projectname>/git/" + auto_path.name + ".doc"
            )
            findings.append(Finding(
                kind="unpaired-automation",
                path=str(auto_path.relative_to(root)),
                suggested_pair=suggested,
            ))

    for doc_path in doc_folders:
        bare = doc_path.name[:-4]
        if bare not in auto_names:
            suggested = str(root / "Biz.Automation" / bare)
            findings.append(Finding(
                kind="orphan-doc-folder",
                path=str(doc_path.relative_to(root)),
                suggested_pair=suggested,
            ))

    return findings


def _load_stale_config(root: Path):
    """Return (patterns, allowlist) — config-overridden or built-in defaults.

    Looks for `Biz.Automation/wikisys.*/_config/stale_paths.yaml` under `root`.
    Missing file or empty key falls back to the module defaults.
    """
    patterns = list(_DEFAULT_STALE_PATTERNS)
    allowlist = list(_DEFAULT_STALE_ALLOWLIST)
    config = next(root.glob("Biz.Automation/wikisys.*/_config/stale_paths.yaml"), None)
    if config is not None and config.is_file():
        parsed = frontmatter.parse_config_yaml(config.read_text(encoding="utf-8"))
        if parsed.get("patterns"):
            patterns = [str(p) for p in parsed["patterns"]]
        if parsed.get("allowlist"):
            allowlist = [str(a) for a in parsed["allowlist"]]
    return patterns, list(_STALE_ALWAYS_ALLOWLIST) + allowlist


def _iter_scan_files(root: Path):
    """Yield text files under `root` eligible for the stale-path scan."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in _STALE_SCAN_SUFFIXES:
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in _STALE_SKIP_DIR_PARTS for part in rel_parts):
            continue
        yield path


def _is_allowlisted(rel_posix: str, allowlist) -> bool:
    return any(fnmatch.fnmatch(rel_posix, pat) for pat in allowlist)


def audit_stale_paths(root: Path, patterns=None, allowlist=None) -> List[StalePathFinding]:
    """Scan the corpus for stale old-layout path fragments (AC12 enforcement).

    Returns findings for each (file, line) where a stale pattern appears in a
    file NOT covered by the allow-list. Empty list = clean.
    """
    if patterns is None or allowlist is None:
        cfg_patterns, cfg_allowlist = _load_stale_config(root)
        patterns = patterns if patterns is not None else cfg_patterns
        allowlist = allowlist if allowlist is not None else cfg_allowlist

    findings: List[StalePathFinding] = []
    for path in _iter_scan_files(root):
        rel_posix = path.relative_to(root).as_posix()
        if _is_allowlisted(rel_posix, allowlist):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pat in patterns:
                if pat in line:
                    findings.append(StalePathFinding(
                        path=rel_posix,
                        line=line_no,
                        pattern=pat,
                        snippet=line.strip()[:120],
                    ))
    return findings


def render_stale_dashboard(findings: List[StalePathFinding]) -> str:
    """Emit stale-path findings as a markdown dashboard."""
    lines = [
        "# Stale Path Sweep",
        "",
        "Generated by `audit_doc_pairing.py --stale-paths`. OBS-1 closure: "
        "AC12 structural enforcement of the old-path migration sweep with an "
        "explicit allow-list (`_config/stale_paths.yaml`).",
        "",
    ]
    if not findings:
        lines.extend(["**Status:** ✓ No stale path references outside the allow-list.", ""])
        return "\n".join(lines)

    lines.append("**Status:** {} stale reference(s).".format(len(findings)))
    lines.append("")
    lines.append("| File | Line | Stale pattern | Snippet |")
    lines.append("|---|---|---|---|")
    for f in findings:
        lines.append("| `{}` | {} | `{}` | {} |".format(
            f.path, f.line, f.pattern, f.snippet.replace("|", "\\|")
        ))
    lines.append("")
    return "\n".join(lines)


def render_dashboard(findings: List[Finding], root: Path) -> str:
    """Emit findings as a markdown dashboard."""
    lines = [
        "# Doc Pairing Audit",
        "",
        "Generated by `audit_doc_pairing.py`. Per spec (d) "
        "Pairing-Audit operation.",
        "",
        "Contract: every `Biz.Automation/<name>/` pairs with "
        "`wiki.<projectname>/git/<name>.doc/`.",
        "",
    ]
    if not findings:
        lines.extend(["**Status:** ✓ All automations paired. No orphan doc folders.", ""])
        return "\n".join(lines)

    lines.append("**Status:** {} finding(s).".format(len(findings)))
    lines.append("")
    lines.append("| Finding | Path | Suggested pair |")
    lines.append("|---|---|---|")
    for f in findings:
        lines.append("| {} | `{}` | `{}` |".format(
            f.kind, f.path, f.suggested_pair
        ))
    lines.append("")
    return "\n".join(lines)


def _resolve_dashboard_path(root: Path, override: Optional[Path]) -> Path:
    if override is not None:
        return override
    # Default: Biz.Automation/wikisys.<projectname>/_dashboards/doc-pairing.md
    wikisys = next(root.glob("Biz.Automation/wikisys.*"), None)
    if wikisys is None:
        # Library-internal case (no Biz.Automation/) — fallback at root
        return root / "doc-pairing.md"
    return wikisys / "_dashboards" / "doc-pairing.md"


def _run_stale_paths(root: Path, args) -> int:
    """--stale-paths mode: AC12 sweep + dashboard/JSON emit + exit code."""
    findings = audit_stale_paths(root)
    if args.json:
        sys.stdout.write(json.dumps(
            [{"path": f.path, "line": f.line, "pattern": f.pattern,
              "snippet": f.snippet} for f in findings],
            indent=2,
        ) + "\n")
    else:
        if args.dashboard is not None:
            dashboard_path = args.dashboard
        else:
            wikisys = next(root.glob("Biz.Automation/wikisys.*"), None)
            dashboard_path = (
                wikisys / "_dashboards" / "stale-paths.md" if wikisys
                else root / "stale-paths.md"
            )
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        dashboard_path.write_text(render_stale_dashboard(findings), encoding="utf-8")
        sys.stdout.write("Dashboard written: {}\n".format(dashboard_path))
        sys.stdout.write("Stale references: {}\n".format(len(findings)))
    return 0 if not findings else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="audit_doc_pairing.py")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="Project root (default cwd).")
    parser.add_argument("--dashboard", type=Path, default=None,
                        help="Override dashboard output path.")
    parser.add_argument("--json", action="store_true",
                        help="Emit findings as JSON to stdout instead of dashboard.")
    parser.add_argument("--stale-paths", action="store_true",
                        help="Run the AC12 stale-path sweep instead of the pairing audit.")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not (root / "Biz.Automation").is_dir() and not any(root.glob("wiki.*")):
        sys.stderr.write(
            "error: {} does not look like a canonical project root "
            "(missing both Biz.Automation/ and wiki.*/)\n".format(root)
        )
        return 2

    if args.stale_paths:
        return _run_stale_paths(root, args)

    findings = audit(root)

    if args.json:
        sys.stdout.write(json.dumps(
            [{"kind": f.kind, "path": f.path, "suggested_pair": f.suggested_pair}
             for f in findings],
            indent=2,
        ) + "\n")
    else:
        dashboard_path = _resolve_dashboard_path(root, args.dashboard)
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        dashboard_path.write_text(render_dashboard(findings, root), encoding="utf-8")
        sys.stdout.write("Dashboard written: {}\n".format(dashboard_path))
        sys.stdout.write("Findings: {}\n".format(len(findings)))

    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
