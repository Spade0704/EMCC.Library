"""Validate reveal-conceit — public-page leak scan.

P8 validator. Walks the wiki for content pages (skipping infrastructure
folders prefixed with `_`), filters to pages with frontmatter
`visibility == "public"` (case-sensitive lowercase per spec §2.3),
strips fenced and inline code spans (replacing with whitespace to
preserve line numbers), and applies regex rules from
`_config/reveal_leak_patterns.yaml`. Severities {error, warning, info};
per spec §2.5, `info` rules document approved-public terms and emit
nothing (filtered before append). Writes a markdown dashboard at
`_dashboards/reveal_conceit.md`.

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
                "severity": "error" | "warning",
                "page_path": Path,
                "line": int,                   # 1-indexed file line
                "message": str,
                "rule": str | None,            # optional name from yaml
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki, structurally malformed
        reveal_leak_patterns.yaml, IO error).

`allow_forbidden_terms: true` frontmatter is a P6-only escape hatch and
is NOT honored here (the page is scanned normally).
"""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict

from _lib import dashboard
from _lib import cli
from _lib import frontmatter
from _lib import markdown
from _lib.config_loader import ConfigYamlError, load_config_yaml


WIKI_ROOT = frontmatter.find_wiki_content_root()
DASHBOARD_RELATIVE = "_dashboards/reveal_conceit.md"
CONFIG_RELATIVE = "_config/reveal_leak_patterns.yaml"
# P8-local render-order subset. `info` rules are filtered upstream in
# `_scan_page` (line ~169) per spec §2.5 (info documents approved-public
# terms; emits nothing). Promoting to `dashboard.SEVERITY_ORDER` 3-tuple
# would render `0 infos` in the counts line, breaking byte-identical
# output. R2-fix in S034-T6.
SEVERITY_ORDER = ("error", "warning")
VALID_SEVERITIES = {"error", "warning", "info"}


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk the wiki, apply reveal-leak rules to public pages, write the dashboard."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )
    rules = _load_rules(wiki_root)
    findings = []
    pages_scanned = 0
    for page_path in markdown.iter_content_pages(wiki_root):
        page_findings = _scan_page(page_path, rules)
        if page_findings is None:
            continue
        pages_scanned += 1
        findings.extend(page_findings)

    findings.sort(key=lambda f: (
        SEVERITY_ORDER.index(f["severity"]),
        f["page_path"].relative_to(wiki_root).as_posix(),
        f["line"],
    ))

    content = _build_dashboard_markdown(wiki_root, findings, pages_scanned)
    dashboard_path = dashboard.write_dashboard(wiki_root, DASHBOARD_RELATIVE, content)

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "pages_scanned": pages_scanned,
    }


def _load_rules(wiki_root):
    """Read _config/reveal_leak_patterns.yaml; return list of compiled rule dicts.

    Missing file -> []. Per-rule malformation (missing keys, invalid severity,
    regex compile error, non-mapping rule) -> skipped with stderr warning;
    valid rules still applied. Structural YAML failure or top-level rules not
    a list propagates ConfigYamlError to the caller.
    """
    # S004 MI-18: discovery via frontmatter.find_config_dir() handles v1.0 +
    # v1.1 layouts.
    try:
        config_dir = frontmatter.find_config_dir(wiki_root)
        config_path = config_dir / "reveal_leak_patterns.yaml"
    except FileNotFoundError:
        config_path = wiki_root / CONFIG_RELATIVE  # sentinel; load -> []
    raw_rules = load_config_yaml(
        config_path,
        wrapper_key="rules",
        required_keys=("pattern", "severity", "message"),
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
            "rule": raw.get("rule"),
        })
    return valid_rules


def _scan_page(page_path, rules):
    """Scan one public page; return list of finding dicts, or None if non-public.

    Public-only filter: visibility must equal the literal string "public"
    (case-sensitive per spec §2.3). Internal, confidential, missing, or
    differently-cased visibility -> page is skipped (not counted in
    pages_scanned). Info-severity rules are filtered before append.
    """
    page = frontmatter.load_page(page_path)
    fm = page["frontmatter"]
    if fm.get("visibility") != "public":
        return None

    raw_text = page_path.read_text(encoding="utf-8")
    fm_lines = markdown.frontmatter_line_count(raw_text)
    stripped = markdown.strip_code(page["body"])

    findings = []
    for rule in rules:
        if rule["severity"] == "info":
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
        findings, SEVERITY_ORDER, lambda f: f["severity"]
    )

    lines = list(dashboard.render_fm_header("Reveal Conceit Dashboard", today=today))
    lines.append("")
    lines.append("# Reveal Conceit — " + today)
    lines.append("")
    lines.append("**Pages scanned:** " + str(pages_scanned))
    counts = []
    for sev in SEVERITY_ORDER:
        n = len(by_severity[sev])
        counts.append("{} {}{}".format(n, sev, "s" if n != 1 else ""))
    lines.append(
        "**Findings:** {} ({})".format(len(findings), " / ".join(counts))
    )
    lines.append("")

    if not findings:
        lines.append("No reveal-conceit findings.")
        lines.append("")
        return "\n".join(lines)

    for sev in SEVERITY_ORDER:
        bucket = by_severity[sev]
        if not bucket:
            continue
        lines.append("## " + sev)
        for f in bucket:
            rel = f["page_path"].relative_to(wiki_root).as_posix()
            lines.append("- {}: {}:{}: {}".format(sev, rel, f["line"], f["message"]))
        lines.append("")
    return "\n".join(lines)


def _main(wiki_root, stdout=None, stderr=None):
    """CLI entry-point body. Returns exit code; lets callers test without subprocess."""
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    wiki_root = Path(wiki_root)
    try:
        summary = run(wiki_root)
    except ConfigYamlError as exc:
        print(
            "error: reveal_leak_patterns.yaml is structurally malformed: {}".format(exc),
            file=stderr,
        )
        return 2
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=stderr)
        return 2

    findings = summary["findings"]
    for f in findings:
        rel = f["page_path"].relative_to(wiki_root).as_posix()
        print("{}: {}:{}: {}".format(f["severity"], rel, f["line"], f["message"]),
              file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    print("reveal_conceit: pages_scanned={} findings={} -> {}".format(
        summary["pages_scanned"],
        len(findings),
        rel,
    ), file=stdout)
    return 1 if findings else 0


if __name__ == "__main__":
    WIKI_ROOT = cli.resolve_cli_wiki_root(WIKI_ROOT)
    sys.exit(_main(WIKI_ROOT))
