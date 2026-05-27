"""Validate terminology — forbidden-terms scan, context-aware.

P6 validator. Walks the wiki for content pages (skipping infrastructure
folders prefixed with `_`), strips fenced and inline code spans (replacing
them with whitespace to preserve line numbers), applies context-filtered
rules from `_config/forbidden_terms.yaml`, and writes a markdown dashboard
at `_dashboards/terminology.md` plus per-finding lines to stdout.

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "findings": list[dict],
                "pages_scanned": int,
            }
        where each finding is:
            {
                "severity": "error" | "warning" | "info",
                "page_path": Path,
                "line": int,                   # 1-indexed file line
                "message": str,
                "rule": str | None,            # optional name from yaml
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki, structurally malformed
        forbidden_terms.yaml, IO error).

Pages with `allow_forbidden_terms: true` in frontmatter are skipped
entirely (no scan, no findings, not counted in pages_scanned).
"""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict

from _lib import dashboard
from _lib import frontmatter
from _lib import markdown
from _lib.config_loader import ConfigYamlError, load_config_yaml


WIKI_ROOT = frontmatter.find_wiki_root()
DASHBOARD_RELATIVE = "_dashboards/terminology.md"
CONFIG_RELATIVE = "_config/forbidden_terms.yaml"
VALID_SEVERITIES = set(dashboard.SEVERITY_ORDER)
VALID_CONTEXTS = {"all", "audience", "internal"}


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk the wiki, apply forbidden-term rules, write the dashboard."""
    wiki_root = Path(wiki_root)
    rules = _load_rules(wiki_root)
    findings = []
    pages_scanned = 0
    for page_path in markdown.iter_content_pages(wiki_root):
        page_findings = _scan_page(page_path, rules, wiki_root)
        if page_findings is None:
            continue
        pages_scanned += 1
        findings.extend(page_findings)

    findings.sort(key=lambda f: (
        dashboard.SEVERITY_ORDER.index(f["severity"]),
        f["page_path"].relative_to(wiki_root).as_posix(),
        f["line"],
    ))

    content = _build_dashboard_markdown(wiki_root, findings, pages_scanned)
    dashboard_path = wiki_root / DASHBOARD_RELATIVE
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(content, encoding="utf-8")

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "pages_scanned": pages_scanned,
    }


def _load_rules(wiki_root):
    """Read _config/forbidden_terms.yaml; return list of compiled rule dicts.

    Missing file -> []. Malformed individual rule -> skipped with a stderr
    warning; valid rules still applied. Structural YAML failure (raises
    ConfigYamlError) is propagated to the caller.
    """
    raw_rules = load_config_yaml(
        wiki_root / CONFIG_RELATIVE,
        wrapper_key="rules",
        required_keys=("pattern", "severity", "message", "context"),
        entity_noun="rule",
    )

    valid_rules = []
    for idx, raw in enumerate(raw_rules, start=1):
        if raw["severity"] not in VALID_SEVERITIES:
            print(
                "warning: skipping malformed rule {}: invalid severity {!r}".format(
                    idx, raw["severity"]),
                file=sys.stderr,
            )
            continue
        if raw["context"] not in VALID_CONTEXTS:
            print(
                "warning: skipping malformed rule {}: invalid context {!r}".format(
                    idx, raw["context"]),
                file=sys.stderr,
            )
            continue
        try:
            compiled = re.compile(raw["pattern"])
        except re.error as exc:
            print(
                "warning: skipping malformed rule {}: regex compile error: {}".format(
                    idx, exc),
                file=sys.stderr,
            )
            continue
        valid_rules.append({
            "compiled": compiled,
            "severity": raw["severity"],
            "message": raw["message"],
            "context": raw["context"],
            "rule": raw.get("rule"),
        })
    return valid_rules


def _context_applies(rule_context, page_visibility):
    """Decide whether a rule's context filter applies to this page's visibility.

    - all       -> always applies
    - audience  -> only when visibility == "public"
    - internal  -> only when visibility == "internal"
    Confidential pages match only context: all rules.
    """
    if rule_context == "all":
        return True
    if rule_context == "audience":
        return page_visibility == "public"
    if rule_context == "internal":
        return page_visibility == "internal"
    return False


def _scan_page(page_path, rules, wiki_root):
    """Scan one page; return list of finding dicts, or None if escape-hatch skipped."""
    page = frontmatter.load_page(page_path)
    fm = page["frontmatter"]
    if fm.get("allow_forbidden_terms"):
        return None
    visibility = fm.get("visibility")

    raw_text = page_path.read_text(encoding="utf-8")
    fm_lines = markdown.frontmatter_line_count(raw_text)
    stripped = markdown.strip_code(page["body"])

    findings = []
    for rule in rules:
        if not _context_applies(rule["context"], visibility):
            continue
        for match in rule["compiled"].finditer(stripped):
            body_line = stripped[:match.start()].count("\n") + 1
            findings.append({
                "severity": rule["severity"],
                "page_path": page_path,
                "line": body_line + fm_lines,
                "message": rule["message"],
                "rule": rule.get("rule"),
            })
    return findings


def _build_dashboard_markdown(wiki_root, findings, pages_scanned):
    today = date.today().isoformat()
    by_severity = dashboard.group_by_fixed_order(
        findings, dashboard.SEVERITY_ORDER, lambda f: f["severity"]
    )

    lines = list(dashboard.render_fm_header("Terminology Dashboard", today=today))
    lines.append("")
    lines.append("# Terminology — " + today)
    lines.append("")
    lines.append("**Pages scanned:** " + str(pages_scanned))
    counts = []
    for sev in dashboard.SEVERITY_ORDER:
        n = len(by_severity[sev])
        counts.append("{} {}{}".format(n, sev, "s" if n != 1 else ""))
    lines.append(
        "**Findings:** {} ({})".format(len(findings), " / ".join(counts))
    )
    lines.append("")

    if not findings:
        lines.append("No terminology findings.")
        lines.append("")
        return "\n".join(lines)

    for sev in dashboard.SEVERITY_ORDER:
        bucket = by_severity[sev]
        if not bucket:
            continue
        lines.append("## " + sev)
        for f in bucket:
            rel = f["page_path"].relative_to(wiki_root).as_posix()
            lines.append("- {}: {}:{}: {}".format(sev, rel, f["line"], f["message"]))
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    try:
        summary = run(WIKI_ROOT)
    except ConfigYamlError as exc:
        print(
            "error: forbidden_terms.yaml is structurally malformed: {}".format(exc),
            file=sys.stderr,
        )
        sys.exit(2)
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        sys.exit(2)

    findings = summary["findings"]
    for f in findings:
        rel = f["page_path"].relative_to(WIKI_ROOT).as_posix()
        print("{}: {}:{}: {}".format(f["severity"], rel, f["line"], f["message"]))

    rel = summary["dashboard_path"].relative_to(WIKI_ROOT).as_posix()
    print("terminology: pages_scanned={} findings={} -> {}".format(
        summary["pages_scanned"],
        len(findings),
        rel,
    ))
    sys.exit(1 if findings else 0)
