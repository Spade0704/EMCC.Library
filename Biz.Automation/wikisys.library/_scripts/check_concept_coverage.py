"""Validate concept-coverage for roster entities.

P13 validator (v1.1 NEW; no v1.0 precedent). Reads `_canon/roster.yaml`,
counts mentions of each canonical name + aliases across all content
pages (word-boundary case-sensitive; frontmatter + fenced + inline
code stripped before matching), and reports entities mentioned on
>= min_mentions distinct pages that lack a dedicated page.

Spec contract: CODEX_BUILD_SPEC_v1_2.md §2.4 row 15 + line 444 (full
algorithmic detail). Severity: single info-class band (advisory per
spec phrasing 'lacking a dedicated page' — non-enforced).

Dedicated-page detection per CODEX_BUILD_SPEC_v1_3.md §2.5 L584
(pinned v1.3, S047-T3 commit `0f1c5e6`): "A dedicated page for an
entity is a content page whose slug (filename stem, slugified)
equals the slugified canonical name of that entity." Both sides
slugified via the same `_slugify` helper (S047-T4 symmetry fix).
Subject-entity exemption per spec L586-594 — entities listed in
`_config/concept_coverage.yaml` subject_entities are excluded from
the no-dedicated-page warning but appear in the dashboard
annotated `subject (exempt)`.

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "findings": list[dict],
                "subject_entries": list[dict],
                "entities_scanned": int,
                "pages_scanned": int,
            }
        where each finding is:
            {
                "severity": "info",
                "entity": str,        # canonical_name
                "pages": list[str],   # sorted wiki-root-relative
                "page_count": int,
                "reason": str,
            }
        and each subject_entry is:
            {
                "entity": str,        # canonical_name
                "pages": list[str],   # sorted wiki-root-relative
                "page_count": int,
                "annotation": "subject (exempt)",
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki, missing required
        `_canon/roster.yaml`, IO error, malformed canon yaml).

Config files:
    _canon/roster.yaml         REQUIRED — wrapper_key 'entities',
                               items {canonical_name, aliases?};
                               loaded via _lib.config_loader.
    _config/concept_coverage.yaml  OPTIONAL — scalar-key shape:
                               min_mentions (int, default 2),
                               exclude_folders (list, default []),
                               exclude_entities (list, default []),
                               subject_entities (list, default []),
                               tier_filter (str, default None/OFF).
                               Loaded via direct parse_config_yaml
                               (load_config_yaml is wrapper-key-only
                               and does not fit the scalar shape).

    tier_filter (M001): when set (e.g. "Authoritative"), each roster
    entry is skipped unless its `tier:` matches (casefold, after strip).
    A missing/empty/null `tier:` is treated as DEFAULT_TIER -> included
    (fail-OPEN: advisory tools over-report, never silently drop). UNION
    with exclude_entities (independent skip predicates). Absent / empty /
    non-string tier_filter -> OFF (no tier gating) -> dashboard output
    byte-identical to pre-M001 (load-bearing: _scripts/ OVERWRITE-ships
    to the whole portfolio before any consumer opts in).
"""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Set

from _lib import dashboard
from _lib import cli
from _lib import frontmatter
from _lib import markdown
from _lib.config_loader import ConfigYamlError, load_config_yaml


WIKI_ROOT = frontmatter.find_wiki_content_root()
DASHBOARD_RELATIVE = "_dashboards/concept_coverage.md"
ROSTER_RELATIVE = "_canon/roster.yaml"
CONFIG_RELATIVE = "_config/concept_coverage.yaml"

DEFAULTS: Dict[str, Any] = {
    "min_mentions": 2,
    "exclude_folders": [],
    "exclude_entities": [],
    "subject_entities": [],
    "tier_filter": None,
}

REASON_COVERAGE_GAP = "entity mentioned in N pages but no dedicated page"

# M001: tier-aware coverage. A roster entry with no `tier:` key (or an empty /
# null / whitespace-only value) is treated as DEFAULT_TIER — i.e. INCLUDED under
# any active tier_filter. This is the fail-OPEN-to-inclusion direction: an
# advisory validator must over-report (a visible, dismissable gap) rather than
# under-report (a silently hidden gap). Never change this default to fail-closed.
DEFAULT_TIER = "Authoritative"

# Known tier vocabulary (casefolded), used ONLY to emit a stderr WARN on a
# present-but-unknown tier value that gets filtered out — surfaces a misspelled
# tier (e.g. `Authoritativ`) that would otherwise be silently dropped. This set
# never enforces: an unknown tier is still filtered per the comparison below, the
# WARN is advisory only. Casefold comparison handles case-typos structurally; this
# set catches the residual misspellings the casefold can't.
KNOWN_TIERS = frozenset({"authoritative", "references"})


def run(wiki_root: Path, stderr=None) -> Dict[str, Any]:
    """Walk content pages, scan roster entities, write the dashboard.

    `stderr` (M001): stream for the unknown-tier WARN; defaults to sys.stderr.
    Injectable so tests can assert the WARN without capturing the process stream.
    """
    if stderr is None:
        stderr = sys.stderr
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )

    roster = _load_roster(wiki_root)
    config = _load_concept_coverage_config(wiki_root)

    exclude_folders = set(config["exclude_folders"])
    exclude_entities = set(config["exclude_entities"])
    subject_entities = set(config["subject_entities"])
    min_mentions = config["min_mentions"]
    tier_filter = config["tier_filter"]

    all_pages = list(markdown.iter_content_pages(wiki_root))
    dedicated_stems: Set[str] = {_slugify(p.stem) for p in all_pages}

    scan_pages = []
    for p in all_pages:
        rel_parts = p.relative_to(wiki_root).parts
        if any(part in exclude_folders for part in rel_parts):
            continue
        scan_pages.append(p)

    page_texts = []
    for p in scan_pages:
        loaded = frontmatter.load_page(p)
        stripped_body = markdown.strip_code(loaded["body"])
        page_texts.append((p, stripped_body))

    findings: List[Dict[str, Any]] = []
    subject_entries: List[Dict[str, Any]] = []
    for entry in roster:
        canonical = str(entry["canonical_name"])
        if canonical in exclude_entities:
            continue
        # M001: tier gating — independent UNION with exclude_entities (neither
        # supersedes the other). Resolve the entry tier fail-OPEN: missing /
        # empty / null / whitespace-only -> DEFAULT_TIER -> included. Casefold
        # the comparison (tier is a controlled-vocabulary label, not prose, so
        # the script's prose case-sensitivity does not transfer) — this kills
        # the case-typo silent-drop class structurally.
        if tier_filter is not None:
            # Fail-OPEN: a tier is honoured ONLY when it is a non-empty string.
            # The Codex YAML-subset parser renders an empty `tier:` inside a list
            # item as [] (not None), and `tier: null`/`~` as None — the isinstance
            # guard funnels every non-string form (None, [], empty, whitespace) to
            # DEFAULT_TIER -> included, so an empty/typo'd tier never silently drops.
            raw_tier = entry.get("tier")
            entry_tier = (
                raw_tier.strip()
                if isinstance(raw_tier, str) and raw_tier.strip()
                else DEFAULT_TIER
            )
            if entry_tier.casefold() not in KNOWN_TIERS:
                print(
                    "warning: roster entry {!r} has unknown tier {!r} "
                    "(known: {}); filtering against tier_filter {!r}".format(
                        canonical, entry_tier, sorted(KNOWN_TIERS), tier_filter
                    ),
                    file=stderr,
                )
            if entry_tier.casefold() != tier_filter.casefold():
                continue
        names = [canonical] + _alias_list(entry)
        regexes = [
            re.compile(r"\b" + re.escape(n) + r"\b") for n in names
        ]
        matched_pages: Set[Path] = set()
        for page_path, text in page_texts:
            for rx in regexes:
                if rx.search(text):
                    matched_pages.add(page_path)
                    break
        if len(matched_pages) < min_mentions:
            continue
        slug = _slugify(canonical)
        if slug in dedicated_stems:
            continue
        page_rels = sorted(
            p.relative_to(wiki_root).as_posix() for p in matched_pages
        )
        if canonical in subject_entities:
            subject_entries.append({
                "entity": canonical,
                "pages": page_rels,
                "page_count": len(page_rels),
                "annotation": "subject (exempt)",
            })
            continue
        findings.append({
            "severity": "info",
            "entity": canonical,
            "pages": page_rels,
            "page_count": len(page_rels),
            "reason": REASON_COVERAGE_GAP,
        })

    findings.sort(key=lambda f: f["entity"])
    subject_entries.sort(key=lambda s: s["entity"])

    content = _build_dashboard_markdown(
        findings, len(roster), len(scan_pages), subject_entries
    )
    dashboard_path = dashboard.write_dashboard(wiki_root, DASHBOARD_RELATIVE, content)

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "subject_entries": subject_entries,
        "entities_scanned": len(roster),
        "pages_scanned": len(scan_pages),
    }


def _load_roster(wiki_root: Path) -> List[Dict[str, Any]]:
    """Read `_canon/roster.yaml`; required.

    Missing file -> raises FileNotFoundError (caught by _main, exit 2).
    Malformed yaml or wrapper-not-list -> ConfigYamlError propagates.

    S004 MI-18: discovery via frontmatter.find_canon_dir() handles v1.0
    (wiki_root/_canon/) AND v1.1 (install/Biz.Automation/wikisys.*/_canon/).
    """
    canon_dir = frontmatter.find_canon_dir(wiki_root)
    roster_path = canon_dir / "roster.yaml"
    if not roster_path.exists():
        raise FileNotFoundError(
            "required canon file missing: {}".format(roster_path)
        )
    return load_config_yaml(
        roster_path,
        wrapper_key="entities",
        required_keys=("canonical_name",),
        entity_noun="roster entry",
    )


def _load_concept_coverage_config(wiki_root: Path) -> Dict[str, Any]:
    """Read `_config/concept_coverage.yaml`; OPTIONAL.

    Missing file -> defaults dict verbatim. Empty / partial-keys
    file -> defaults merged per-field. load_config_yaml does NOT fit
    the scalar-key shape; direct parse_config_yaml call used here.
    """
    # S004 MI-18: discovery via frontmatter.find_config_dir() handles v1.0 +
    # v1.1 layouts. Missing config dir -> defaults verbatim.
    try:
        config_dir = frontmatter.find_config_dir(wiki_root)
        config_path = config_dir / "concept_coverage.yaml"
    except FileNotFoundError:
        config_path = wiki_root / CONFIG_RELATIVE  # sentinel; will fail .exists()
    merged = dict(DEFAULTS)
    merged["exclude_folders"] = list(DEFAULTS["exclude_folders"])
    merged["exclude_entities"] = list(DEFAULTS["exclude_entities"])
    merged["subject_entities"] = list(DEFAULTS["subject_entities"])
    if not config_path.exists():
        return merged
    text = config_path.read_text(encoding="utf-8")
    parsed = frontmatter.parse_config_yaml(text)
    if "min_mentions" in parsed and isinstance(parsed["min_mentions"], int):
        merged["min_mentions"] = parsed["min_mentions"]
    if "exclude_folders" in parsed and isinstance(parsed["exclude_folders"], list):
        merged["exclude_folders"] = [str(x) for x in parsed["exclude_folders"]]
    if "exclude_entities" in parsed and isinstance(parsed["exclude_entities"], list):
        merged["exclude_entities"] = [str(x) for x in parsed["exclude_entities"]]
    if "subject_entities" in parsed and isinstance(parsed["subject_entities"], list):
        merged["subject_entities"] = [str(x) for x in parsed["subject_entities"]]
    # M001: tier_filter accepted only as a non-empty string; stored stripped.
    # Anything else (absent / empty / list / non-string) leaves the default None
    # -> OFF, never crashes, never half-applies.
    if (
        "tier_filter" in parsed
        and isinstance(parsed["tier_filter"], str)
        and parsed["tier_filter"].strip()
    ):
        merged["tier_filter"] = parsed["tier_filter"].strip()
    return merged


def _alias_list(entry: Dict[str, Any]) -> List[str]:
    raw = entry.get("aliases")
    if not isinstance(raw, list):
        return []
    return [str(a) for a in raw]


def _slugify(s: str) -> str:
    """Canonical slug per spec §2.5 L584 (S047-T4 symmetry fix).

    Lowercase + space-to-hyphen. Both the page-stem index and the
    roster canonical-name slug compute via this helper so the
    "dedicated page" comparison is symmetric (spec L584 'identical
    algorithm'). No additional substitutions (punctuation, underscore,
    etc.) — defer until a real consumer surfaces.
    """
    return s.lower().replace(" ", "-")


def _build_dashboard_markdown(
    findings: List[Dict[str, Any]],
    entities_scanned: int,
    pages_scanned: int,
    subject_entries: List[Dict[str, Any]] = None,
) -> str:
    if subject_entries is None:
        subject_entries = []
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header(
        "Concept Coverage Dashboard", today=today
    ))
    lines.append("")
    lines.append("# Concept Coverage - " + today)
    lines.append("")
    lines.append("**Entities scanned:** " + str(entities_scanned))
    lines.append("**Pages scanned:** " + str(pages_scanned))
    lines.append("**Findings:** " + str(len(findings)))
    lines.append("")

    if not findings and not subject_entries:
        lines.append("No concept coverage findings.")
        lines.append("")
        return "\n".join(lines)

    if findings:
        lines.append("## Coverage Gaps")
        for f in findings:
            lines.append(_render_finding_line(f))
        lines.append("")

    if subject_entries:
        lines.append("## Subject Entities (exempt)")
        for s in subject_entries:
            lines.append(
                "- **{entity}** — mentioned in {page_count} pages "
                "(subject; exempt from no-dedicated-page signal)".format(
                    entity=s["entity"],
                    page_count=s["page_count"],
                )
            )
        lines.append("")
    return "\n".join(lines)


def _render_finding_line(f: Dict[str, Any]) -> str:
    pages_text = ", ".join(f["pages"])
    return (
        "- {severity}: {entity}: mentioned in {page_count} pages "
        "but no dedicated page ({pages_text})"
    ).format(
        severity=f["severity"],
        entity=f["entity"],
        page_count=f["page_count"],
        pages_text=pages_text,
    )


def _main(wiki_root, stdout=None, stderr=None):
    """CLI entry-point body. Returns exit code; lets callers test without subprocess."""
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr
    wiki_root = Path(wiki_root)
    try:
        summary = run(wiki_root, stderr=stderr)
    except ConfigYamlError as exc:
        print(
            "error: roster yaml is structurally malformed: {}".format(exc),
            file=stderr,
        )
        return 2
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=stderr)
        return 2

    findings = summary["findings"]
    for f in findings:
        print(dashboard.strip_finding_bullet(_render_finding_line(f)), file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    print(
        "concept_coverage: entities_scanned={} pages_scanned={} findings={} -> {}".format(
            summary["entities_scanned"],
            summary["pages_scanned"],
            len(findings),
            rel,
        ),
        file=stdout,
    )
    return 1 if findings else 0


if __name__ == "__main__":
    WIKI_ROOT = cli.resolve_cli_wiki_root(WIKI_ROOT)
    sys.exit(_main(WIKI_ROOT))
