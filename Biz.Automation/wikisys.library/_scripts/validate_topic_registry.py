"""P18.4 validate_topic_registry — page-topic-resolution + registry-orphan validator.

Per CODEX_BUILD_SPEC_v1_3.md §2.4 #18 + §7 P18.4. Two checks:
    (a) Every page `topics:` value resolves in `_canon/topics.yaml` (error).
    (b) Every registry topic has ≥1 member page (warning; orphan-topic
        detection).

Read-only validator (NO writes to content pages). Emits findings dashboard
at `_dashboards/topic_registry_validation.md` via _lib.dashboard.write_dashboard
SSOT. Mirrors existing validator pattern (P6-P14 family).

Public API:
    run(wiki_root: Path) -> Dict[str, Any]
    check_page_topics_resolve(page_path, page_topics, alias_index) -> List[Dict]
    check_orphan_topics(topics, topic_to_pages) -> List[Dict]
    build_topic_to_pages_index(wiki_root) -> Dict[str, List[Path]]
    render_validation_report(findings, wiki_root) -> str

Pure stdlib per spec §8 Hard Rule 1.
"""

import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

from _lib import dashboard
from _lib import cli
from _lib import frontmatter
from _lib import markdown
from _lib.topics import Topic, build_alias_index, load_topics, resolve_topic


WIKI_ROOT = frontmatter.find_wiki_content_root()
DASHBOARD_RELATIVE = "_dashboards/topic_registry_validation.md"
TOPICS_RELATIVE = "_canon/topics.yaml"

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


def build_topic_to_pages_index(wiki_root: Path) -> Dict[str, List[Path]]:
    """Re-derive topic → [pages] from page fm `topics:` fields.

    Mirrors T-XL-4 cross_link_topics.build_topic_to_pages_index pattern
    (2nd-consumer per Architect arbitration; _lib promotion deferred to
    T-XL-6 P19 orchestrator 3rd-consumer per S035 numerical-3rd-consumer
    threshold).
    """
    index: Dict[str, List[Path]] = {}
    for page_path in markdown.iter_content_pages(wiki_root):
        page = frontmatter.load_page(page_path)
        topics = page["frontmatter"].get("topics") or []
        if not isinstance(topics, list):
            continue
        for topic in topics:
            if not isinstance(topic, str):
                continue
            index.setdefault(topic, []).append(page_path)
    return index


def check_page_topics_resolve(
    page_path: Path,
    page_topics: List[str],
    alias_index: Dict[str, Topic],
) -> List[Dict[str, Any]]:
    """Spec §2.4 #18 (a): emit error finding per unresolved page topic.

    For each page topic, check resolution via _lib.topics.resolve_topic
    (case-insensitive alias lookup). Unresolved values emit error finding.
    """
    findings: List[Dict[str, Any]] = []
    for topic in page_topics:
        if not isinstance(topic, str):
            continue
        if resolve_topic(topic, alias_index) is None:
            findings.append({
                "page_path": page_path,
                "topic": topic,
                "severity": SEVERITY_ERROR,
                "message": "page topic {!r} does not resolve in _canon/topics.yaml".format(
                    topic
                ),
            })
    return findings


def check_orphan_topics(
    topics: List[Topic],
    topic_to_pages: Dict[str, List[Path]],
) -> List[Dict[str, Any]]:
    """Spec §2.4 #18 (b): emit warning finding per registry-orphan topic.

    Registry topic with 0 member pages → warning finding.
    """
    findings: List[Dict[str, Any]] = []
    for topic in topics:
        members = topic_to_pages.get(topic.name, [])
        if not members:
            findings.append({
                "topic": topic.name,
                "severity": SEVERITY_WARNING,
                "message": "registry topic {!r} has no member pages".format(
                    topic.name
                ),
            })
    return findings


def render_validation_report(
    findings: List[Dict[str, Any]], wiki_root: Path
) -> str:
    """Render dashboard markdown with standard 5-field fm + per-severity findings."""
    today = date.today().isoformat()
    lines: List[str] = list(
        dashboard.render_fm_header(
            "Topic Registry Validation Dashboard", today=today
        )
    )
    lines.append("")
    lines.append("# Topic Registry Validation — " + today)
    lines.append("")

    errors = [f for f in findings if f.get("severity") == SEVERITY_ERROR]
    warnings = [f for f in findings if f.get("severity") == SEVERITY_WARNING]

    lines.append("**Errors:** " + str(len(errors)))
    lines.append("**Warnings:** " + str(len(warnings)))
    lines.append("")

    if not findings:
        lines.append("All topic-registry checks passed.")
        lines.append("")
        return "\n".join(lines)

    if errors:
        lines.append("## Errors")
        lines.append("")
        for f in errors:
            page = f.get("page_path")
            if page is not None:
                try:
                    rel = page.relative_to(wiki_root).as_posix()
                except ValueError:
                    rel = page.as_posix()
                lines.append(
                    "- {} (topic {!r}): {}".format(
                        rel, f["topic"], f["message"]
                    )
                )
            else:
                lines.append("- {}: {}".format(f.get("topic", "?"), f["message"]))
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for f in warnings:
            lines.append(
                "- topic {!r}: {}".format(f.get("topic", "?"), f["message"])
            )
        lines.append("")

    return "\n".join(lines)


def run(wiki_root: Path) -> Dict[str, Any]:
    """Orchestrator entry-point — run both checks + emit dashboard."""
    wiki_root = Path(wiki_root)

    # S004 MI-18: discovery via frontmatter.find_canon_dir() handles v1.0 +
    # v1.1 layouts. Missing canon dir -> graceful early-exit.
    try:
        canon_dir = frontmatter.find_canon_dir(wiki_root)
        topics_path = canon_dir / "topics.yaml"
    except FileNotFoundError:
        topics_path = wiki_root / TOPICS_RELATIVE  # sentinel; will fail is_file()
    if not topics_path.is_file():
        # Graceful early-exit: emit empty dashboard, return zero-summary.
        content = render_validation_report([], wiki_root)
        out_path = dashboard.write_dashboard(
            wiki_root, DASHBOARD_RELATIVE, content
        )
        print(
            "info: _canon/topics.yaml not found; topic registry validation skipped.",
            file=sys.stderr,
        )
        return {
            "pages_seen": 0,
            "registry_topics": 0,
            "errors_count": 0,
            "warnings_count": 0,
            "dashboard_path": out_path,
        }

    topics_list = load_topics(topics_path)
    alias_index = build_alias_index(topics_list)
    topic_to_pages = build_topic_to_pages_index(wiki_root)

    findings: List[Dict[str, Any]] = []
    pages_seen = 0
    for page_path in markdown.iter_content_pages(wiki_root):
        pages_seen += 1
        page = frontmatter.load_page(page_path)
        page_topics = page["frontmatter"].get("topics") or []
        if not isinstance(page_topics, list):
            continue
        page_topic_strs = [t for t in page_topics if isinstance(t, str)]
        findings.extend(
            check_page_topics_resolve(page_path, page_topic_strs, alias_index)
        )

    findings.extend(check_orphan_topics(topics_list, topic_to_pages))

    errors_count = sum(1 for f in findings if f.get("severity") == SEVERITY_ERROR)
    warnings_count = sum(
        1 for f in findings if f.get("severity") == SEVERITY_WARNING
    )

    content = render_validation_report(findings, wiki_root)
    out_path = dashboard.write_dashboard(
        wiki_root, DASHBOARD_RELATIVE, content
    )

    return {
        "pages_seen": pages_seen,
        "registry_topics": len(topics_list),
        "errors_count": errors_count,
        "warnings_count": warnings_count,
        "dashboard_path": out_path,
    }


if __name__ == "__main__":
    WIKI_ROOT = cli.resolve_cli_wiki_root(WIKI_ROOT)
    summary = run(WIKI_ROOT)
    print(
        "topic_registry_validation: pages={} topics={} errors={} warnings={}".format(
            summary["pages_seen"],
            summary["registry_topics"],
            summary["errors_count"],
            summary["warnings_count"],
        )
    )
