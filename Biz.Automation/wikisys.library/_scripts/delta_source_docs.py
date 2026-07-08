"""P16 delta_source_docs.py — source-doc version diff (2-cycle COMPLETE).

Per spec v1.2 §2.4 row 13 (`Diff two source-doc versions + cascade impact`).
2-cycle split per S035 sprint-close note:
    T4  -- diff core: structured findings + stdout report (shipped)
    T5  -- cascade impact via `_config/cascade_map.yaml` lookup
           + `_dashboards/source_delta.md` synthesis (shipped)

EXPLICIT OUT-OF-SCOPE (post-T5):
    - Multi-file batch diff (single-pair invocation only)
    - Git-rev input mode (`--rev-a HEAD~1`)
    - HTML / JSON output formats (markdown dashboard only)
    - Performance optimization for large source-docs (>10K lines)
    - Per-pair dashboard variant (single-path overwrite convention)

Usage:
    python _scripts/delta_source_docs.py <version_a> <version_b>

Public API:
    run(version_a: Path, version_b: Path, wiki_root: Path,
        stderr: Optional[IO] = None) -> Dict[str, Any]
        Returns structured diff + cascade impact + written dashboard path:
        {
            "version_a_path": Path,              # absolute
            "version_b_path": Path,              # absolute
            "section_changes": [                 # T4
                {
                    "type": "added" | "removed" | "modified" | "unchanged",
                    "section_title": str,        # H2 text WITHOUT leading "## "
                    "added_lines": int,          # 0 for removed/unchanged
                    "removed_lines": int,        # 0 for added/unchanged
                    "line_diff": [str],          # difflib unified_diff lines (empty for unchanged)
                },
                ...
            ],
            "frontmatter_changes": {             # T4
                "added_keys": [str],             # sorted
                "removed_keys": [str],           # sorted
                "modified_keys": [str],          # sorted
            },
            "summary": {                         # T4
                "sections_added": int,
                "sections_removed": int,
                "sections_modified": int,
                "sections_unchanged": int,
                "total_lines_added": int,
                "total_lines_removed": int,
            },
            "cascade_impact": [                  # T5; empty list when no impact
                {
                    "source_path": str,          # wiki-root-relative; matched cascade_map source
                    "derived_path": str,         # wiki-root-relative; affected derived doc
                    "affected_by_sections": [str],  # changed section_titles (excludes unchanged)
                },
                ...
            ],
            "dashboard_path": Path,              # T5; always-written; absolute
        }

Diff semantics (T4):
    - Frontmatter via `_lib.frontmatter.load_page()`. Modified detection
      uses Python `!=` (list values: order-sensitive; v0.2+ refinement
      candidate if user feedback materializes).
    - Body split on `^## ` H2 boundary regex.
    - Pre-first-H2 content (non-whitespace-only) captured as implicit
      section with literal `section_title = "<intro>"` (angle brackets
      prevent collision with a real H2 titled "intro").
    - Section pairing by section_title string match.
    - Duplicate section titles within one version: pairs via per-title
      FIFO queue (first-A pairs with first-B, second-A with second-B,
      etc.). Single-side leftovers classified added/removed.
      Operator-actionable: rename one of the duplicate sections to
      disambiguate.
    - Section-body byte-equiv short-circuit -> `unchanged`; otherwise
      line-level diff via `difflib.unified_diff(a, b, n=3)`.
    - Line classification: `+` prefix (not `+++`) = added; `-` prefix
      (not `---`) = removed.

Cascade impact semantics (T5):
    - Load `_config/cascade_map.yaml` via `_lib.config_loader.load_config_yaml()`
      mirroring `_scripts/check_cascade.py:_load_cascade_map`.
    - Per pair: if pair['source'] matches either version's wiki-relative
      path (exact string match), emit a cascade_impact entry for the
      pair's derived_path. Operator-actionable for path-canonicalization
      mismatches: edit cascade_map entries to use the canonical source-path.
    - Aggregation: one entry per matching derived_path (dict-keyed-by-
      derived collapses rare shared-derived duplicates).
    - `affected_by_sections` = section_titles where type in
      {'added','removed','modified'} (excludes 'unchanged'); includes
      `<intro>` sentinel when intro is in the changed set.
    - Short-circuit: when there are no section changes AND no
      frontmatter changes, `cascade_impact = []` returned BEFORE
      cascade_map load (operator-friendly: no nag about cascade_map
      errors when no impact possible).
    - cascade_map.yaml absent OR no matching source -> `cascade_impact = []`
      + stderr WARN routed via the `stderr` keyword arg.

Dashboard synthesis (T5):
    - Always-written at `<wiki_root>/_dashboards/source_delta.md`.
    - Single-path overwrite convention per `check_cascade.py` + `health.md`.
    - Frontmatter = 5-field dashboard contract via
      `dashboard.render_fm_header('Source-Doc Delta Dashboard',
      today=date.today().isoformat())` (required-`today`-arg signature
      per S037-T2; P16 = 14th call site).
    - Body sections in order: ## Summary -> ## Frontmatter Changes ->
      ## Section Changes -> ## Cascade Impact (each w/ content OR
      `_No ..._` placeholder).

CLI exit codes:
    0 = clean run, diff produced + reported + dashboard written
    2 = input error (file missing, parse error, malformed cascade_map,
        IO error)
"""
# @component Codex[ingest]

import difflib
import re
import sys
from collections import deque
from datetime import date
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, TextIO, Tuple

from _lib import dashboard
from _lib import frontmatter
from _lib.config_loader import ConfigYamlError, load_config_yaml


WIKI_ROOT = frontmatter.find_wiki_content_root()
INTRO_SECTION_TITLE = "<intro>"
H2_BOUNDARY_RE = re.compile(r"^## ", re.MULTILINE)
DASHBOARD_RELATIVE = "_dashboards/source_delta.md"
DASHBOARD_TITLE = "Source-Doc Delta Dashboard"
CASCADE_CONFIG_RELATIVE = "_config/cascade_map.yaml"


def run(
    version_a: Path,
    version_b: Path,
    wiki_root: Path,
    stderr: Optional[TextIO] = None,
) -> Dict[str, Any]:
    """Diff two source-doc versions; return structured diff per module docstring.

    `stderr` (optional file-like): destination for cascade-impact WARN
    messages. None (default) = warnings suppressed (T4-consumer-friendly
    noop). `_main()` threads its own stderr through.
    """
    wiki_root = Path(wiki_root).resolve()
    version_a_abs = _resolve(version_a, wiki_root)
    version_b_abs = _resolve(version_b, wiki_root)

    page_a = _load_source_doc(version_a_abs)
    page_b = _load_source_doc(version_b_abs)

    sections_a = _split_sections(page_a["body"])
    sections_b = _split_sections(page_b["body"])

    section_changes = _diff_sections(sections_a, sections_b)
    frontmatter_changes = _diff_frontmatter(
        page_a["frontmatter"], page_b["frontmatter"]
    )
    summary = _summarize(section_changes)

    cascade_impact = _compute_cascade_impact(
        version_a_abs,
        version_b_abs,
        section_changes,
        frontmatter_changes,
        wiki_root,
        stderr,
    )

    result: Dict[str, Any] = {
        "version_a_path": version_a_abs,
        "version_b_path": version_b_abs,
        "section_changes": section_changes,
        "frontmatter_changes": frontmatter_changes,
        "summary": summary,
        "cascade_impact": cascade_impact,
    }

    dashboard_path = dashboard.write_dashboard(
        wiki_root,
        DASHBOARD_RELATIVE,
        _render_dashboard_markdown(result, wiki_root),
    )
    result["dashboard_path"] = dashboard_path

    return result


def _resolve(version: Path, wiki_root: Path) -> Path:
    """Resolve `version` against `wiki_root` if relative; absolutize."""
    version = Path(version)
    if version.is_absolute():
        return version.resolve()
    return (Path(wiki_root) / version).resolve()


def _load_source_doc(path: Path) -> Dict[str, Any]:
    """Wrap `frontmatter.load_page()` with friendlier missing-file error."""
    if not path.is_file():
        raise FileNotFoundError("source doc not found: {}".format(path))
    return frontmatter.load_page(path)


def _split_sections(body: str) -> List[Tuple[str, str]]:
    """Split `body` into (section_title, section_body) tuples on H2 boundary.

    Pre-first-H2 content (non-whitespace-only) emits as implicit
    `<intro>` section. Section titles strip leading `## ` and trailing
    newline; internal whitespace preserved verbatim.
    """
    if not body:
        return []
    matches = list(H2_BOUNDARY_RE.finditer(body))
    sections: List[Tuple[str, str]] = []

    if matches:
        intro = body[: matches[0].start()]
        if intro.strip():
            sections.append((INTRO_SECTION_TITLE, intro.rstrip("\n")))
    else:
        if body.strip():
            sections.append((INTRO_SECTION_TITLE, body.rstrip("\n")))
        return sections

    for i, match in enumerate(matches):
        title_start = match.end()
        title_end = body.find("\n", title_start)
        if title_end == -1:
            title = body[title_start:]
            section_body = ""
        else:
            title = body[title_start:title_end]
            section_start = title_end + 1
            section_end = (
                matches[i + 1].start() if i + 1 < len(matches) else len(body)
            )
            section_body = body[section_start:section_end].rstrip("\n")
        sections.append((title, section_body))

    return sections


def _diff_frontmatter(
    fm_a: Dict[str, Any], fm_b: Dict[str, Any]
) -> Dict[str, List[str]]:
    """Compute added/removed/modified key sets between two frontmatter dicts."""
    keys_a = set(fm_a or {})
    keys_b = set(fm_b or {})
    added = sorted(keys_b - keys_a)
    removed = sorted(keys_a - keys_b)
    modified = sorted(k for k in (keys_a & keys_b) if fm_a[k] != fm_b[k])
    return {
        "added_keys": added,
        "removed_keys": removed,
        "modified_keys": modified,
    }


def _diff_sections(
    sections_a: List[Tuple[str, str]],
    sections_b: List[Tuple[str, str]],
) -> List[Dict[str, Any]]:
    """Pair sections by title (FIFO per duplicate) and classify each pairing.

    Encounter order preserved in returned list: A's sections first, then
    B's leftover added sections in original B-encounter order.
    """
    queue_b: Dict[str, Deque[int]] = {}
    for idx, (title, _body) in enumerate(sections_b):
        queue_b.setdefault(title, deque()).append(idx)

    paired_b: set = set()
    changes: List[Dict[str, Any]] = []
    for title, body_a in sections_a:
        dq = queue_b.get(title)
        if dq:
            idx = dq.popleft()
            paired_b.add(idx)
            body_b = sections_b[idx][1]
            changes.append(_classify_pair(title, body_a, body_b))
        else:
            changes.append(_make_change("removed", title, body_a, ""))

    for idx, (title, body_b) in enumerate(sections_b):
        if idx not in paired_b:
            changes.append(_make_change("added", title, "", body_b))

    return changes


def _classify_pair(title: str, body_a: str, body_b: str) -> Dict[str, Any]:
    """Classify a both-sides section pairing as `unchanged` or `modified`."""
    if body_a == body_b:
        return _make_change("unchanged", title, body_a, body_b)
    return _make_change("modified", title, body_a, body_b)


def _make_change(
    change_type: str, title: str, body_a: str, body_b: str
) -> Dict[str, Any]:
    """Build a section_changes entry per the public-API schema."""
    if change_type == "unchanged":
        return {
            "type": "unchanged",
            "section_title": title,
            "added_lines": 0,
            "removed_lines": 0,
            "line_diff": [],
        }
    a_lines = body_a.split("\n") if body_a else []
    b_lines = body_b.split("\n") if body_b else []
    line_diff = list(
        difflib.unified_diff(
            a_lines, b_lines, fromfile="a", tofile="b", lineterm="", n=3
        )
    )
    added = sum(
        1 for ln in line_diff if ln.startswith("+") and not ln.startswith("+++")
    )
    removed = sum(
        1 for ln in line_diff if ln.startswith("-") and not ln.startswith("---")
    )
    return {
        "type": change_type,
        "section_title": title,
        "added_lines": added,
        "removed_lines": removed,
        "line_diff": line_diff,
    }


def _summarize(section_changes: List[Dict[str, Any]]) -> Dict[str, int]:
    """Tally section_changes into the summary dict per public-API schema."""
    summary = {
        "sections_added": 0,
        "sections_removed": 0,
        "sections_modified": 0,
        "sections_unchanged": 0,
        "total_lines_added": 0,
        "total_lines_removed": 0,
    }
    for change in section_changes:
        key = "sections_" + change["type"]
        summary[key] += 1
        summary["total_lines_added"] += change["added_lines"]
        summary["total_lines_removed"] += change["removed_lines"]
    return summary


def _load_cascade_map(wiki_root: Path) -> List[Dict[str, str]]:
    """Read `_config/cascade_map.yaml`; return validated pair dict list.

    Missing file -> []. Per-pair malformation skipped w/ stderr WARN
    (delegated to `load_config_yaml`). Structural YAML failure or
    top-level `pairs` not a list propagates `ConfigYamlError` to caller.
    Mirrors `_scripts/check_cascade.py:_load_cascade_map` semantics.
    """
    # S004 MI-18: discovery via frontmatter.find_config_dir() handles v1.0 +
    # v1.1 layouts.
    try:
        config_dir = frontmatter.find_config_dir(wiki_root)
        config_path = config_dir / "cascade_map.yaml"
    except FileNotFoundError:
        config_path = wiki_root / CASCADE_CONFIG_RELATIVE  # sentinel; load -> []
    raw_pairs = load_config_yaml(
        config_path,
        wrapper_key="pairs",
        required_keys=("source", "derived"),
        entity_noun="pair",
    )
    return [
        {"source": str(raw["source"]), "derived": str(raw["derived"])}
        for raw in raw_pairs
    ]


def _compute_cascade_impact(
    version_a_path: Path,
    version_b_path: Path,
    section_changes: List[Dict[str, Any]],
    fm_changes: Dict[str, List[str]],
    wiki_root: Path,
    stderr,
) -> List[Dict[str, Any]]:
    """Per-derived-path cascade impact entries; empty when no impact applies.

    Short-circuits to [] when there are no changed sections AND no
    changed frontmatter keys (operator-friendly: no cascade-map nag
    when no impact possible).
    """
    notable_section_titles = [
        s["section_title"]
        for s in section_changes
        if s["type"] in {"added", "removed", "modified"}
    ]
    fm_has_changes = bool(
        fm_changes["added_keys"]
        or fm_changes["removed_keys"]
        or fm_changes["modified_keys"]
    )
    if not notable_section_titles and not fm_has_changes:
        return []

    # S004 MI-18: resolve the cascade_map.yaml location via the same discovery
    # _load_cascade_map() uses (frontmatter.find_config_dir), so this works for
    # both the v1.0 layout (config under the wiki content root) and the v1.1
    # layout (config at the wikisys module root). The previous hardcoded
    # `wiki_root / CASCADE_CONFIG_RELATIVE` guard returned [] before
    # _load_cascade_map() ever ran, silently disabling cascade impact on every
    # v1.1 install. Warn only when the config is genuinely absent everywhere.
    try:
        cascade_map_path = (
            frontmatter.find_config_dir(wiki_root) / "cascade_map.yaml"
        )
    except FileNotFoundError:
        cascade_map_path = wiki_root / CASCADE_CONFIG_RELATIVE
    if not cascade_map_path.is_file():
        if stderr is not None:
            print(
                "WARN: cascade_map.yaml not found; cascade_impact empty.",
                file=stderr,
            )
        return []

    pairs = _load_cascade_map(wiki_root)
    relpath_a = _display_path(version_a_path, wiki_root)
    relpath_b = _display_path(version_b_path, wiki_root)
    candidates = {relpath_a, relpath_b}

    per_derived: Dict[str, Dict[str, Any]] = {}
    matched_sources: List[str] = []
    for pair in pairs:
        if pair["source"] in candidates:
            matched_sources.append(pair["source"])
            # setdefault keeps the FIRST source_path encountered for a given
            # derived (R2 aggregation semantics); the return value is unused.
            per_derived.setdefault(
                pair["derived"],
                {
                    "source_path": pair["source"],
                    "derived_path": pair["derived"],
                    "affected_by_sections": list(notable_section_titles),
                },
            )

    if not per_derived:
        if stderr is not None:
            print(
                "WARN: no cascade_map.yaml entries match {} or {}; "
                "cascade_impact empty.".format(relpath_a, relpath_b),
                file=stderr,
            )
        return []

    return [per_derived[k] for k in sorted(per_derived)]


def _render_dashboard_markdown(diff_result: Dict[str, Any], wiki_root: Path) -> str:
    """Render the `_dashboards/source_delta.md` body (fm + 4 sections)."""
    today = date.today().isoformat()
    lines: List[str] = list(
        dashboard.render_fm_header(DASHBOARD_TITLE, today=today)
    )
    lines.append("")

    a_rel = _display_path(diff_result["version_a_path"], wiki_root)
    b_rel = _display_path(diff_result["version_b_path"], wiki_root)
    s = diff_result["summary"]
    fm = diff_result["frontmatter_changes"]
    section_changes = diff_result["section_changes"]
    cascade_impact = diff_result["cascade_impact"]

    lines.append("## Summary")
    lines.append("")
    lines.append("- Versions: `{}` -> `{}`".format(a_rel, b_rel))
    lines.append(
        "- Sections: added={} | removed={} | modified={} | unchanged={}".format(
            s["sections_added"],
            s["sections_removed"],
            s["sections_modified"],
            s["sections_unchanged"],
        )
    )
    lines.append(
        "- Total lines: +{} -{}".format(
            s["total_lines_added"], s["total_lines_removed"]
        )
    )
    lines.append(
        "- Frontmatter keys: added={} | removed={} | modified={}".format(
            len(fm["added_keys"]), len(fm["removed_keys"]), len(fm["modified_keys"])
        )
    )
    lines.append("")

    lines.append("## Frontmatter Changes")
    lines.append("")
    if not (fm["added_keys"] or fm["removed_keys"] or fm["modified_keys"]):
        lines.append("_No frontmatter changes._")
    else:
        for key in fm["added_keys"]:
            lines.append("- `+{}`".format(key))
        for key in fm["removed_keys"]:
            lines.append("- `-{}`".format(key))
        for key in fm["modified_keys"]:
            lines.append("- `~{}`".format(key))
    lines.append("")

    lines.append("## Section Changes")
    lines.append("")
    notable = [c for c in section_changes if c["type"] != "unchanged"]
    if not notable:
        lines.append("_No section changes._")
    else:
        for change in notable:
            symbol = {"added": "+", "removed": "-", "modified": "~"}[change["type"]]
            if change["type"] == "added":
                detail = "added (+{} lines)".format(change["added_lines"])
            elif change["type"] == "removed":
                detail = "removed (-{} lines)".format(change["removed_lines"])
            else:
                detail = "modified (+{} -{} lines)".format(
                    change["added_lines"], change["removed_lines"]
                )
            lines.append(
                "- `{} {}` — {}".format(symbol, change["section_title"], detail)
            )
    lines.append("")

    lines.append("## Cascade Impact")
    lines.append("")
    if not cascade_impact:
        lines.append("_No cascade impact._")
    else:
        for entry in cascade_impact:
            lines.append("- `{}`".format(entry["derived_path"]))
            lines.append(
                "  - Source: `{}`".format(entry["source_path"])
            )
            if entry["affected_by_sections"]:
                lines.append(
                    "  - Affected by sections: {}".format(
                        ", ".join(
                            "`{}`".format(t) for t in entry["affected_by_sections"]
                        )
                    )
                )
    lines.append("")
    return "\n".join(lines)


def _render_stdout_report(diff_result: Dict[str, Any], wiki_root: Path) -> str:
    """Render `run()` result as the operator-facing stdout text report."""
    wiki_root = Path(wiki_root).resolve()
    a_rel = _display_path(diff_result["version_a_path"], wiki_root)
    b_rel = _display_path(diff_result["version_b_path"], wiki_root)

    lines: List[str] = []
    lines.append("=== Source-doc diff: {} -> {} ===".format(a_rel, b_rel))
    lines.append("")
    lines.append("Frontmatter changes:")
    fm = diff_result["frontmatter_changes"]
    if not (fm["added_keys"] or fm["removed_keys"] or fm["modified_keys"]):
        lines.append("  (none)")
    else:
        for key in fm["added_keys"]:
            lines.append("  +{}".format(key))
        for key in fm["removed_keys"]:
            lines.append("  -{}".format(key))
        for key in fm["modified_keys"]:
            lines.append("  ~{}".format(key))
    lines.append("")
    lines.append("Section changes:")
    notable = [s for s in diff_result["section_changes"] if s["type"] != "unchanged"]
    if not notable:
        lines.append("  (no section changes)")
    else:
        for change in notable:
            symbol = {"added": "+", "removed": "-", "modified": "~"}[change["type"]]
            if change["type"] == "added":
                detail = "added (+{} lines)".format(change["added_lines"])
            elif change["type"] == "removed":
                detail = "removed (-{} lines)".format(change["removed_lines"])
            else:
                detail = "modified (+{} -{} lines)".format(
                    change["added_lines"], change["removed_lines"]
                )
            lines.append(
                "  {} {}          # {}".format(symbol, change["section_title"], detail)
            )
    lines.append("")
    s = diff_result["summary"]
    lines.append(
        "Summary: {} added, {} removed, {} modified, {} unchanged sections; "
        "+{} -{} total lines.".format(
            s["sections_added"],
            s["sections_removed"],
            s["sections_modified"],
            s["sections_unchanged"],
            s["total_lines_added"],
            s["total_lines_removed"],
        )
    )
    lines.append("")
    lines.append("Cascade Impact:")
    cascade_impact = diff_result.get("cascade_impact", [])
    if not cascade_impact:
        lines.append("  (no cascade impact)")
    else:
        for entry in cascade_impact:
            lines.append("  -> {}".format(entry["derived_path"]))
    dashboard_path = diff_result.get("dashboard_path")
    if dashboard_path is not None:
        lines.append("")
        lines.append(
            "Dashboard written: {}".format(_display_path(dashboard_path, wiki_root))
        )
    return "\n".join(lines)


def _display_path(path: Path, wiki_root: Path) -> str:
    """Show wiki-relative path if possible; else absolute."""
    path = Path(path).resolve()
    try:
        return path.relative_to(wiki_root).as_posix()
    except ValueError:
        return path.as_posix()


def _main(argv=None, wiki_root=None, stdout=None, stderr=None) -> int:
    """CLI entry-point. Returns exit code."""
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    if argv is None:
        argv = sys.argv[1:]
    if wiki_root is None:
        wiki_root = WIKI_ROOT
    wiki_root = Path(wiki_root).resolve()

    if len(argv) != 2:
        print(
            "usage: delta_source_docs.py <version_a> <version_b>",
            file=stderr,
        )
        return 2

    try:
        diff_result = run(
            Path(argv[0]), Path(argv[1]), wiki_root, stderr=stderr
        )
    except FileNotFoundError as exc:
        print("error: {}".format(exc), file=stderr)
        return 2
    except ConfigYamlError as exc:
        print(
            "error: cascade_map.yaml is structurally malformed: {}".format(exc),
            file=stderr,
        )
        return 2
    except (IsADirectoryError, PermissionError, OSError, UnicodeDecodeError) as exc:
        print("error: input error: {}".format(exc), file=stderr)
        return 2

    print(_render_stdout_report(diff_result, wiki_root), file=stdout)
    return 0


if __name__ == "__main__":
    sys.exit(_main())
