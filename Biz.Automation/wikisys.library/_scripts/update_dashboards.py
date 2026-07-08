"""P19 update_dashboards.py — master orchestrator + health.md synthesis.

Per spec v1.3 §2.4 #1 + orchestrator note. Runs all 12 currently-shipped
agg+val sub-scripts in-process via each module's `run(wiki_root) -> Dict`
entry point. After agg+val pass, runs cross-link pipeline (#16 → #17 → #18)
per spec v1.3 §2.4 orchestrator note, then synthesizes
`_dashboards/health.md` with 7 signals:
    1. completion percentage (from P5 build_completion_dashboard)
    2. canon contradictions (from P12 check_canon_consistency, page-vs-canon mode)
    3. cascade staleness (from P10 check_cascade, severity=info)
    4. concept coverage gaps (from P13 check_concept_coverage)
    5. unverified-claim count (aggregated from page frontmatter
       `unverified_claims[]` totals across content folders)
    6. recent ingest entries (most recent N entries from
       `_decisions/ingest-log.md` per INGEST_PROCEDURE.md line 83)
    7. cross_link_coverage (v1.3 NEW): pages with ≥1 entry in
       `related_files` / total content pages, per spec §2.4 #1 v1.3
       update.

P-priority sub-script order:
    P4  collect_open_questions
    P5  build_completion_dashboard
    P6  validate_terminology
    P7  validate_canon_integrity
    P8  validate_reveal_conceit
    P9  check_cross_refs
    P10 check_cascade
    P11 check_framework_briefing_sync
    P12 check_canon_consistency
    P13 check_concept_coverage
    P14 steel_thread_tracker
    P15 build_canon_drift_report
    # P16 delta_source_docs -- DEFER: S037-T4/T5
    AC  audit_citations (report-only citation-presence; own dashboard, not health.md)

Failure handling: per-script try/except catches Exception; orchestrator
continues; health.md synthesized against partial outputs (sentinel `?`
for missing signals from failed sub-scripts). Exit code 0 if all
sub-scripts clean; 1 if any raised.

Sub-script invocation uses `run()` direct call (NOT `_main()`) — structured
dict return needed for health.md signal extraction. Each sub-script's
`_main()` is for standalone CLI; orchestrator generates its own aggregate
CLI summary from the 12 `run()` returns.

Render conventions: `dashboard.render_fm_header` called with required
`today=date.today().isoformat()` named-arg (P19 = 13th consumer per
S037-T2 sig-tightening + S035 hotfix a6ce5e1 LOCAL-date lock).
"""
# @component Codex[dashboards]

import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

import audit_citations
import build_caution_index
import build_canon_drift_report
import build_completion_dashboard
import build_topic_index
import check_canon_consistency
import check_cascade
import check_concept_coverage
import check_cross_refs
import check_framework_briefing_sync
import collect_open_questions
import cross_link_topics
import steel_thread_tracker
import validate_canon_integrity
import validate_reveal_conceit
import validate_terminology
import validate_topic_registry

from _lib import cli
from _lib import dashboard
from _lib import frontmatter
from _lib import markdown


WIKI_ROOT = frontmatter.find_wiki_content_root()
HEALTH_DASHBOARD_RELATIVE = "_dashboards/health.md"
INGEST_LOG_RELATIVE = "_decisions/ingest-log.md"
TOP_N_DEFAULT = 5
SENTINEL = "?"


SUBSCRIPTS: List[Tuple[int, Any, str]] = [
    (4, collect_open_questions, "P4 collect_open_questions"),
    (5, build_completion_dashboard, "P5 build_completion_dashboard"),
    (6, validate_terminology, "P6 validate_terminology"),
    (7, validate_canon_integrity, "P7 validate_canon_integrity"),
    (8, validate_reveal_conceit, "P8 validate_reveal_conceit"),
    (9, check_cross_refs, "P9 check_cross_refs"),
    (10, check_cascade, "P10 check_cascade"),
    (11, check_framework_briefing_sync, "P11 check_framework_briefing_sync"),
    (12, check_canon_consistency, "P12 check_canon_consistency"),
    (13, check_concept_coverage, "P13 check_concept_coverage"),
    (14, steel_thread_tracker, "P14 steel_thread_tracker"),
    (15, build_canon_drift_report, "P15 build_canon_drift_report"),
    # DEFER: S037-T4/T5 P16 delta_source_docs wiring goes here once shipped.
    # Citation-presence audit (2026-06-13 accuracy track) — report-only stage,
    # failure-isolated like every other; never red-bars (run() forces enforce=False).
    # NOT wired into health.md (the 7-signal contract is frozen); emits its own
    # _dashboards/citation_audit.md.
    (21, audit_citations, "AC audit_citations"),
    # Tiered caution-index (2026-06-13 accuracy track, item 2) — deterministic
    # grep/keyword router over HIGH pages; report-only stage, failure-isolated,
    # never red-bars (run() forces enforce=False). NOT wired into health.md (the
    # 7-signal contract is frozen); emits its own _dashboards/caution_index.md.
    # Fail-closed by construction: an ambiguous HIGH page ESCALATEs to source
    # rather than surfacing a guessed caution.
    (22, build_caution_index, "CI build_caution_index"),
]


# Cross-link pipeline per spec v1.3 §2.4 orchestrator note: runs AFTER
# existing aggregator/validator pass, BEFORE health-summary synthesis.
# Sequence #16 → #17 → #18 matters: #17 needs #16's index; #18 validates
# the post-#17 state. Failure isolation: any step failure → stderr warning
# + non-zero exit BUT does NOT block existing pipeline OR other regenerate.
CROSS_LINK_PIPELINE: List[Tuple[int, Any, str]] = [
    (16, build_topic_index, "#16 build_topic_index"),
    (17, cross_link_topics, "#17 cross_link_topics"),
    (18, validate_topic_registry, "#18 validate_topic_registry"),
]


def run(wiki_root: Path) -> Dict[str, Any]:
    """Orchestrator entry-point.

    Invokes each sub-script's `run(wiki_root)` in P-priority order; catches
    per-script exceptions and continues; synthesizes health.md from
    accumulated signals (sentinel for failed sub-scripts).

    Returns:
        dict with keys:
            results -- {p_num: sub_script_return_dict OR None}
            failures -- list of {p_num, label, exc_type, exc_msg}
            health_path -- Path to written health.md
    """
    wiki_root = Path(wiki_root)
    results: Dict[int, Any] = {}
    failures: List[Dict[str, str]] = []

    for p_num, module, label in SUBSCRIPTS:
        try:
            results[p_num] = module.run(wiki_root)
        except Exception as exc:
            failures.append({
                "p_num": p_num,
                "label": label,
                "exc_type": type(exc).__name__,
                "exc_msg": str(exc),
            })
            results[p_num] = None

    # Cross-link pipeline (#16 → #17 → #18) per spec v1.3 §2.4
    # orchestrator note. Failure isolation per spec: each step
    # try/except + stderr warning + continue pipeline; aggregate to
    # orchestrator failures list. Existing aggregator/validator runs
    # already complete above; their dashboard regeneration NOT blocked
    # by cross-link failures.
    for p_num, module, label in CROSS_LINK_PIPELINE:
        try:
            results[p_num] = module.run(wiki_root)
        except Exception as exc:
            print(
                "WARN: cross-link pipeline step {} failed: {}: {}".format(
                    label, type(exc).__name__, exc
                ),
                file=sys.stderr,
            )
            failures.append({
                "p_num": p_num,
                "label": label,
                "exc_type": type(exc).__name__,
                "exc_msg": str(exc),
            })
            results[p_num] = None

    health_path = _synthesize_health(wiki_root, results)

    return {
        "results": results,
        "failures": failures,
        "health_path": health_path,
    }


def _synthesize_health(wiki_root: Path, results: Dict[int, Any]) -> Path:
    """Build `_dashboards/health.md` with 7 sections per spec v1.3 §2.4 #1."""
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header("Health Dashboard", today=today))
    lines.append("")
    lines.extend(_section_completion(results.get(5)))
    lines.append("")
    lines.extend(_section_canon_contradictions(results.get(12)))
    lines.append("")
    lines.extend(_section_cascade_staleness(results.get(10)))
    lines.append("")
    lines.extend(_section_concept_coverage(results.get(13)))
    lines.append("")
    lines.extend(_section_unverified_claims(wiki_root))
    lines.append("")
    lines.extend(_section_recent_ingest(wiki_root))
    lines.append("")
    lines.extend(_section_cross_link_coverage(wiki_root))
    lines.append("")

    return dashboard.write_dashboard(
        wiki_root, HEALTH_DASHBOARD_RELATIVE, "\n".join(lines)
    )


def _section_completion(result) -> List[str]:
    lines = ["## Completion", ""]
    if result is None:
        lines.append("- Average completion: {} (sub-script failed)".format(SENTINEL))
    else:
        avg = result.get("average_completion")
        tracked = result.get("pages_tracked", 0)
        if avg is None:
            lines.append(
                "- Average completion: n/a (no pages with `completion` field; tracked={})".format(tracked)
            )
        else:
            lines.append(
                "- Average completion: {}% (across {} pages)".format(avg, tracked)
            )
    lines.append("- Source: `_dashboards/completion.md`")
    return lines


def _section_canon_contradictions(result) -> List[str]:
    lines = ["## Canon Contradictions", ""]
    if result is None:
        lines.append("- Page-vs-canon contradictions: {} (sub-script failed)".format(SENTINEL))
    else:
        findings = result.get("findings", [])
        page_vs_canon = [f for f in findings if f.get("mode") == "page_vs_canon"]
        lines.append("- Page-vs-canon contradictions: {}".format(len(page_vs_canon)))
        if page_vs_canon:
            top = page_vs_canon[:TOP_N_DEFAULT]
            for f in top:
                page = f.get("page", "<unknown>")
                lines.append("  - {}".format(page))
    lines.append("- Source: `_dashboards/canon_consistency.md`")
    return lines


def _section_cascade_staleness(result) -> List[str]:
    lines = ["## Cascade Staleness", ""]
    if result is None:
        lines.append("- Stale derived docs: {} (sub-script failed)".format(SENTINEL))
    else:
        findings = result.get("findings", [])
        # "info" severity = stale (source newer than derived); "warning" =
        # derived missing; "error" = source missing. Staleness signal is
        # info-only per `_classify_pair` (`REASON_STALE`).
        stale = [f for f in findings if f.get("severity") == "info"]
        lines.append("- Stale derived docs: {}".format(len(stale)))
    lines.append("- Source: `_dashboards/cascade.md`")
    return lines


def _section_concept_coverage(result) -> List[str]:
    lines = ["## Concept Coverage Gaps", ""]
    if result is None:
        lines.append("- Coverage gaps: {} (sub-script failed)".format(SENTINEL))
    else:
        findings = result.get("findings", [])
        lines.append("- Coverage gaps: {}".format(len(findings)))
    lines.append("- Source: `_dashboards/concept_coverage.md`")
    return lines


def _section_unverified_claims(wiki_root: Path) -> List[str]:
    lines = ["## Unverified Claims", ""]
    per_page: List[Tuple[str, int]] = []
    grand_total = 0
    try:
        for page_path in markdown.iter_content_pages(wiki_root):
            page = frontmatter.load_page(page_path)
            claims = page["frontmatter"].get("unverified_claims") or []
            count = len(claims) if isinstance(claims, list) else 0
            if count > 0:
                per_page.append((page_path.relative_to(wiki_root).as_posix(), count))
            grand_total += count
    except Exception:
        lines.append("- Total: {} (aggregator failed)".format(SENTINEL))
        return lines

    lines.append("- Total: {}".format(grand_total))
    if per_page:
        per_page.sort(key=lambda t: (-t[1], t[0]))
        for path, count in per_page[:TOP_N_DEFAULT]:
            lines.append("  - {} ({})".format(path, count))
    return lines


def _section_recent_ingest(wiki_root: Path) -> List[str]:
    lines = ["## Recent Ingest", ""]
    # S004 MI-18: discovery via frontmatter.find_decisions_dir() handles
    # v1.0 (wiki_root/_decisions/) AND v1.1 (install/Biz.Automation/
    # wikisys.*/_decisions/). Pre-S004 health.md showed empty Recent
    # Ingest for Library because the v1.0 lookup couldn't find _decisions/
    # after S002 split.
    try:
        decisions_dir = frontmatter.find_decisions_dir(wiki_root)
        log_path = decisions_dir / "ingest-log.md"
    except FileNotFoundError:
        log_path = wiki_root / INGEST_LOG_RELATIVE  # sentinel; will fail .exists()
    if not log_path.exists():
        lines.append("_No ingest entries yet._")
        return lines
    try:
        text = log_path.read_text(encoding="utf-8")
    except Exception:
        lines.append("- Status: {} (ingest log read failed)".format(SENTINEL))
        return lines

    entries = _parse_ingest_entries(text)
    if not entries:
        lines.append("_No ingest entries yet._")
        return lines

    for entry in entries[:TOP_N_DEFAULT]:
        lines.append("- {}".format(entry))
    return lines


def _section_cross_link_coverage(wiki_root: Path) -> List[str]:
    """Pages with ≥1 entry in `related_files` / total content pages.

    Spec v1.3 §2.4 #1 NEW signal. Counts via _lib.markdown.iter_content_pages
    + _lib.frontmatter.load_page fm read + filter for non-empty
    `related_files` list. Sentinel emit on aggregator failure.
    """
    lines = ["## Cross-link Coverage", ""]
    try:
        total = 0
        with_links = 0
        for page_path in markdown.iter_content_pages(wiki_root):
            total += 1
            page = frontmatter.load_page(page_path)
            related = page["frontmatter"].get("related_files") or []
            if isinstance(related, list) and related:
                with_links += 1
    except Exception:
        lines.append(
            "- Pages with cross-links: {} (aggregator failed)".format(SENTINEL)
        )
        return lines

    if total == 0:
        lines.append("- Pages with cross-links: 0 (no content pages)")
    else:
        pct = round(with_links * 100 / total)
        lines.append(
            "- Pages with cross-links: {}/{} ({}%)".format(
                with_links, total, pct
            )
        )
    lines.append("- Source: cross_link_topics + frontmatter `related_files`")
    return lines


def _parse_ingest_entries(text: str) -> List[str]:
    """Parse most-recent-first list of `## ` H2 header titles from ingest log.

    INGEST_PROCEDURE.md line 83 pins the log path but does not fix entry
    format. Simplest heuristic: collect all `## ` H2 headers in order of
    encounter. Procedure convention places newest entries at the top of
    the log (operator appends new entries by adding a new H2 block); the
    parsed list therefore reads newest-first as encountered. If the log
    diverges from this convention, parser is lossy but never throws.
    """
    entries: List[str] = []
    for line in text.split("\n"):
        if line.startswith("## "):
            entries.append(line[3:].strip())
    return entries


def _print_summary(wiki_root: Path, summary: Dict[str, Any], stdout) -> None:
    """Print orchestrator CLI summary to `stdout`."""
    results = summary["results"]
    failures = summary["failures"]
    print("update_dashboards orchestrator -> {}".format(wiki_root), file=stdout)
    print("", file=stdout)
    for p_num, _module, label in list(SUBSCRIPTS) + list(CROSS_LINK_PIPELINE):
        if results.get(p_num) is None:
            fail = next((f for f in failures if f["p_num"] == p_num), None)
            if fail:
                print(
                    "  {} -- FAILED: {}: {}".format(
                        label, fail["exc_type"], fail["exc_msg"]
                    ),
                    file=stdout,
                )
            else:
                print("  {} -- SKIPPED".format(label), file=stdout)
        else:
            print("  {} -- OK".format(label), file=stdout)
    print("", file=stdout)
    rel = summary["health_path"].relative_to(wiki_root).as_posix()
    print("health.md -> {}".format(rel), file=stdout)
    if failures:
        print(
            "orchestrator: {} sub-script(s) failed; exit 1".format(len(failures)),
            file=stdout,
        )


def _main(wiki_root, stdout=None, stderr=None) -> int:
    """CLI entry-point body. Returns exit code; lets callers test without subprocess."""
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    wiki_root = Path(wiki_root)
    summary = run(wiki_root)
    _print_summary(wiki_root, summary, stdout)
    return 1 if summary["failures"] else 0


if __name__ == "__main__":
    # MI-17 full closure: accept an explicit content root via --wiki-root or a
    # bare positional (e.g. wiki.mentor/git/) regardless of where the
    # orchestrator script lives. Defaults to the module-level content root.
    sys.exit(_main(cli.resolve_cli_wiki_root(WIKI_ROOT)))
