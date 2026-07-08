"""audit_citations.py — runnable citation-PRESENCE audit (Cairn-absorption item 1).

Wires the existing, tested `_lib/doc_lint.py::check_consequence` lint into a
standalone, report-only entrypoint over the wiki content tree. Surfaces every
HIGH-`consequence` page that lacks a non-empty `cite_anchor`.

Council: `EMCC/tasks/council/2026-06-13-library-cairn-absorption-track.md` (build
item 1). Delta-force: standalone audit over `s1_doc` injection — a report-only
audit *structurally cannot* red-bar the full-tree gate, so coupling a
fail-safe-HIGH check to that green bar is avoided. Canon contract:
`wiki.codex/git/01-Architecture/Frontmatter-Schema.md` §"Accuracy fields".

**Presence-Not-Accuracy:** this proves a citation is *present* on a HIGH page; it
does NOT verify the quote is verbatim, that the anchor resolves, or that a
refusal was correct. A floor, not a guarantee.

Read-only: never modifies content pages.

CLI:
    python audit_citations.py [--wiki-root PATH] [--json] [--enforce]

Exit codes:
    0  report-only run (default), OR enforce run with no errors
    1  --enforce run with one or more HIGH-without-cite errors
    2  no content root resolved (malformed/empty tree)
"""
# @component Codex[validators]
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

from _lib import cli, dashboard, doc_lint, frontmatter, markdown


DASHBOARD_RELATIVE = "_dashboards/citation_audit.md"


class CitationFinding(NamedTuple):
    path: str          # content-root-relative posix path
    consequence: str   # resolved tier: "high" | "low"
    field_present: bool  # True only if a recognized high|low was declared
    message: str       # the lint's report message
    severity: str      # "error" (enforce) | "warning" (report-only)


def audit_citations(wiki_root: Path, enforce: bool = False) -> List[CitationFinding]:
    """Run the citation-presence lint over every content page under `wiki_root`.

    Pure: returns findings, writes nothing. Report-only by default (findings are
    warnings); `enforce=True` promotes HIGH-without-cite to errors.
    """
    findings: List[CitationFinding] = []
    for page in markdown.iter_content_pages(wiki_root):
        res = doc_lint.check_consequence(page, enforce=enforce)
        msgs = res.errors + res.warnings
        if not msgs:
            continue
        rel = page.relative_to(wiki_root).as_posix()
        for msg in msgs:
            findings.append(CitationFinding(
                path=rel,
                consequence=res.consequence,
                field_present=res.field_present,
                message=msg,
                severity="error" if (enforce and res.errors) else "warning",
            ))
    return findings


def render_dashboard(findings: List[CitationFinding], wiki_root: Path,
                     enforce: bool) -> str:
    """Markdown report. Mirrors the Presence-Not-Accuracy caveat so the report
    never outruns the canon."""
    mode = "enforce" if enforce else "report-only"
    lines = [
        "# Citation-presence audit",
        "",
        f"Root: `{wiki_root}` · mode: **{mode}** · findings: **{len(findings)}**",
        "",
        "> **Presence-Not-Accuracy:** this audit confirms a HIGH-`consequence` "
        "page carries a non-empty `cite_anchor`. It does NOT verify the quote is "
        "verbatim, that the anchor resolves, or that a refusal was correct.",
        "",
    ]
    if not findings:
        lines.append("_No HIGH page is missing a cite_anchor._")
        return "\n".join(lines) + "\n"
    lines += ["| Page | Tier | Severity | Finding |", "|---|---|---|---|"]
    for f in findings:
        lines.append(f"| `{f.path}` | {f.consequence} | {f.severity} | {f.message} |")
    return "\n".join(lines) + "\n"


def run(wiki_root: Path) -> Dict[str, Any]:
    """Orchestrator entry-point — report-only citation-presence audit.

    Conforms to the `module.run(wiki_root) -> dict` contract `update_dashboards.py`
    invokes. Always report-only here (never `enforce`) so wiring it into the
    orchestrator can never red-bar the dashboard pass — the standalone CLI keeps
    the `--enforce` opt-in. Writes `_dashboards/citation_audit.md`, returns a
    summary dict. Presence-Not-Accuracy caveat carries through render_dashboard.
    """
    wiki_root = Path(wiki_root)
    findings = audit_citations(wiki_root, enforce=False)
    today = date.today().isoformat()
    header = "\n".join(dashboard.render_fm_header("Citation Audit Dashboard",
                                                 today=today))
    content = header + "\n\n" + render_dashboard(findings, wiki_root, enforce=False)
    out_path = dashboard.write_dashboard(wiki_root, DASHBOARD_RELATIVE, content)
    return {
        "findings": [f._asdict() for f in findings],
        "findings_count": len(findings),
        "dashboard_path": out_path,
    }


def main(argv: Optional[List[str]] = None) -> int:
    # split our own flags from the shared wiki-root resolver's args
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--json", action="store_true",
                     help="emit findings as JSON instead of the markdown dashboard")
    pre.add_argument("--enforce", action="store_true",
                     help="promote HIGH-without-cite findings to errors (exit 1)")
    known, rest = pre.parse_known_args(argv)

    default_root = frontmatter.find_wiki_content_root()
    wiki_root = cli.resolve_cli_wiki_root(default_root, argv=rest,
                                          prog="audit_citations.py")
    if wiki_root is None or not Path(wiki_root).is_dir():
        sys.stderr.write("audit_citations: no content root resolved\n")
        return 2

    findings = audit_citations(Path(wiki_root), enforce=known.enforce)

    if known.json:
        print(json.dumps([f._asdict() for f in findings], indent=2))
    else:
        sys.stdout.write(render_dashboard(findings, Path(wiki_root), known.enforce))

    # Report-only never fails the run; enforce fails only on real errors.
    if known.enforce and any(f.severity == "error" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
