"""Validate canon-consistency across pages and against `_canon/*.yaml`.

P12 validator. Two-mode design per spec §2.4 row 9:

    Mode 1 — page vs canon (ENFORCED, error-class)
        Page fm contains flat-key claims matching the convention
        `canon_claim_<file>_<entity>: <scalar>`. Each claim is looked up
        in `_canon/<file>.yaml` (loaded via `_lib.config_loader`); a
        mismatch with the canonical value, a missing entity, a missing
        canon file, or an unrecognised canon-file stem all emit an
        error-class finding.

    Mode 2 — page vs page (FLAGGED, warning-class)
        Pages indexed by claim-key; any claim-key asserted by two or
        more pages with disagreeing values emits a warning-class
        finding listing all pages + values. Index-first O(n*k), not
        pairwise O(n²).

Both modes are fm-only — body content is never scanned, so
`_lib.markdown.strip_code` is not consumed. `iter_content_pages` is
used solely for page-walk.

Page fm convention (NEW, not in spec §2.3 — codification deferred to
Backlog item "Spec §2.3 canon_claim_<file>_<entity> fm convention
codification"). Pages without any `canon_claim_*` keys emit zero
findings; convention is ignore-by-absence and backward-compatible.

Canon yaml shapes (T8 validation gate ACTIVE — first NEW consumer of
`_lib.config_loader.load_config_yaml` post-T8 promo `5339eea`):

    _canon/counts.yaml    -> `counts:` list of {name: str, value: int}
    _canon/roster.yaml    -> `entities:` list of {canonical_name: str,
                              aliases?: [flow-list]}
    _canon/taxonomy.yaml  -> `categories:` list of {name: str,
                              parent_name?: str}
    _canon/timeline.yaml  -> `events:` list of {name: str, date: str}

Mode 1 lookup per file (CANON_FILES dict): claim entity matched against
`lookup_key`; claim value compared against `value_field` (None means
existence-check — claim value ignored, missing-entity still error).

Writes a markdown dashboard at `_dashboards/canon_consistency.md` with
the standard 5-field fm contract via `_lib.dashboard.render_fm_header`.

Public API:
    run(wiki_root: Path) -> dict
        Returns:
            {
                "dashboard_path": Path,
                "findings": list[dict],
                "pages_scanned": int,
            }

Exit codes (in __main__):
    0 — clean run, no findings.
    1 — findings present (dashboard still written).
    2 — script-level error (missing wiki, IO error, malformed canon yaml).
"""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from _lib import dashboard
from _lib import frontmatter
from _lib import markdown
from _lib.config_loader import ConfigYamlError, load_config_yaml


WIKI_ROOT = frontmatter.find_wiki_root()
DASHBOARD_RELATIVE = "_dashboards/canon_consistency.md"

CANON_FILES: Dict[str, Dict[str, Any]] = {
    "counts": {
        "wrapper_key": "counts",
        "lookup_key": "name",
        "value_field": "value",
        "required_keys": ("name", "value"),
    },
    "roster": {
        "wrapper_key": "entities",
        "lookup_key": "canonical_name",
        "value_field": None,
        "required_keys": ("canonical_name",),
    },
    "taxonomy": {
        "wrapper_key": "categories",
        "lookup_key": "name",
        "value_field": "parent_name",
        "required_keys": ("name",),
    },
    "timeline": {
        "wrapper_key": "events",
        "lookup_key": "name",
        "value_field": "date",
        "required_keys": ("name", "date"),
    },
}

CLAIM_KEY_RE = re.compile(r"^canon_claim_([a-z][a-z0-9_]*?)_(.+)$")

MODE_PAGE_VS_CANON = "page_vs_canon"
MODE_PAGE_VS_PAGE = "page_vs_page"
MODE_ORDER: Tuple[str, ...] = (MODE_PAGE_VS_CANON, MODE_PAGE_VS_PAGE)

REASON_VALUE_MISMATCH = "claim value contradicts canon"
REASON_ENTITY_NOT_IN_CANON = "claim references entity not in canon file"
REASON_CANON_FILE_MISSING = "claim references canon file that does not exist"
REASON_UNKNOWN_CANON_FILE = "claim references unrecognized canon file"
REASON_PAGE_DISAGREEMENT = "pages disagree on same claim key"


def run(wiki_root: Path) -> Dict[str, Any]:
    """Walk content pages, classify Mode 1+2 findings, write the dashboard."""
    wiki_root = Path(wiki_root)
    if not wiki_root.is_dir():
        raise FileNotFoundError(
            "wiki_root not found or not a directory: {}".format(wiki_root)
        )

    canon = _load_canon(wiki_root)
    findings: List[Dict[str, Any]] = []
    pages_scanned = 0
    # claim_key -> list of (page_rel, page_value)
    claim_index: Dict[str, List[Tuple[str, Any]]] = {}

    for page_path in markdown.iter_content_pages(wiki_root):
        page = frontmatter.load_page(page_path)
        fm = page["frontmatter"]
        if not fm:
            continue
        pages_scanned += 1
        rel = page_path.relative_to(wiki_root).as_posix()
        for key, page_value in fm.items():
            match = CLAIM_KEY_RE.match(str(key))
            if not match:
                continue
            canon_file, entity = _split_claim_key(key, match)
            findings.extend(
                _classify_mode1(rel, key, canon_file, entity, page_value, canon)
            )
            claim_index.setdefault(key, []).append((rel, page_value))

    findings.extend(_classify_mode2(claim_index))
    findings.sort(key=_finding_sort_key)

    content = _build_dashboard_markdown(findings, pages_scanned)
    dashboard_path = wiki_root / DASHBOARD_RELATIVE
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(content, encoding="utf-8")

    return {
        "dashboard_path": dashboard_path,
        "findings": findings,
        "pages_scanned": pages_scanned,
    }


def _load_canon(wiki_root: Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Load each `_canon/<file>.yaml`; return {file_stem: {lookup_value: entry}}.

    Missing canon file -> file_stem maps to empty dict (consumer-side
    distinguishes "file present, entity missing" from "file absent" via
    Path.exists() probe in _classify_mode1).
    """
    canon: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for file_stem, spec in CANON_FILES.items():
        canon_path = wiki_root / "_canon" / "{}.yaml".format(file_stem)
        entries = load_config_yaml(
            canon_path,
            wrapper_key=spec["wrapper_key"],
            required_keys=spec["required_keys"],
            entity_noun="canon entry",
        )
        lookup_key = spec["lookup_key"]
        canon[file_stem] = {
            str(entry[lookup_key]): entry for entry in entries
        }
    return canon


def _split_claim_key(
    key: str, match: "re.Match[str]"
) -> Tuple[str, str]:
    """Extract (canon_file, entity) from a claim-key regex match.

    Prefer the longest canon-file prefix that matches an allowed
    file-stem (CANON_FILES key) so entity names containing underscores
    parse correctly. Falls back to the regex's greedy first-group when
    no known file-stem prefix matches (yields UNKNOWN_CANON_FILE finding
    downstream).
    """
    suffix = key[len("canon_claim_"):]
    for file_stem in CANON_FILES:
        prefix = file_stem + "_"
        if suffix.startswith(prefix) and len(suffix) > len(prefix):
            return file_stem, suffix[len(prefix):]
    return match.group(1), match.group(2)


def _classify_mode1(
    page_rel: str,
    claim_key: str,
    canon_file: str,
    entity: str,
    page_value: Any,
    canon: Dict[str, Dict[str, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Emit Mode 1 findings for one (page, claim) tuple."""
    findings: List[Dict[str, Any]] = []
    if canon_file not in CANON_FILES:
        findings.append({
            "mode": MODE_PAGE_VS_CANON,
            "severity": "error",
            "page": page_rel,
            "claim_key": claim_key,
            "canon_file": canon_file,
            "entity": entity,
            "page_value": page_value,
            "canon_value": None,
            "reason": REASON_UNKNOWN_CANON_FILE,
        })
        return findings

    entries = canon.get(canon_file, {})
    if not entries:
        findings.append({
            "mode": MODE_PAGE_VS_CANON,
            "severity": "error",
            "page": page_rel,
            "claim_key": claim_key,
            "canon_file": canon_file,
            "entity": entity,
            "page_value": page_value,
            "canon_value": None,
            "reason": REASON_CANON_FILE_MISSING,
        })
        return findings

    if entity not in entries:
        findings.append({
            "mode": MODE_PAGE_VS_CANON,
            "severity": "error",
            "page": page_rel,
            "claim_key": claim_key,
            "canon_file": canon_file,
            "entity": entity,
            "page_value": page_value,
            "canon_value": None,
            "reason": REASON_ENTITY_NOT_IN_CANON,
        })
        return findings

    spec = CANON_FILES[canon_file]
    value_field = spec["value_field"]
    if value_field is None:
        return findings
    canon_value = entries[entity].get(value_field)
    if canon_value != page_value:
        findings.append({
            "mode": MODE_PAGE_VS_CANON,
            "severity": "error",
            "page": page_rel,
            "claim_key": claim_key,
            "canon_file": canon_file,
            "entity": entity,
            "page_value": page_value,
            "canon_value": canon_value,
            "reason": REASON_VALUE_MISMATCH,
        })
    return findings


def _classify_mode2(
    claim_index: Dict[str, List[Tuple[str, Any]]],
) -> List[Dict[str, Any]]:
    """Emit Mode 2 findings for each claim-key with >=2 distinct values."""
    findings: List[Dict[str, Any]] = []
    for claim_key in sorted(claim_index):
        page_value_pairs = claim_index[claim_key]
        if len(page_value_pairs) < 2:
            continue
        distinct = {pv[1] for pv in page_value_pairs}
        if len(distinct) < 2:
            continue
        match = CLAIM_KEY_RE.match(claim_key)
        canon_file, entity = _split_claim_key(claim_key, match)
        findings.append({
            "mode": MODE_PAGE_VS_PAGE,
            "severity": "warning",
            "claim_key": claim_key,
            "canon_file": canon_file,
            "entity": entity,
            "pages": [
                {"path": p, "value": v}
                for p, v in page_value_pairs
            ],
            "reason": REASON_PAGE_DISAGREEMENT,
        })
    return findings


def _finding_sort_key(f: Dict[str, Any]) -> Tuple[int, int, str, str]:
    """Sort by (mode, severity, page-or-claim, claim_key)."""
    mode_idx = MODE_ORDER.index(f["mode"])
    sev_idx = dashboard.SEVERITY_ORDER.index(f["severity"])
    if f["mode"] == MODE_PAGE_VS_CANON:
        anchor = f["page"]
    else:
        anchor = f["claim_key"]
    return (mode_idx, sev_idx, anchor, f["claim_key"])


def _build_dashboard_markdown(
    findings: List[Dict[str, Any]], pages_scanned: int
) -> str:
    today = date.today().isoformat()
    lines = list(dashboard.render_fm_header(
        "Canon Consistency Dashboard", today=today
    ))
    lines.append("")
    lines.append("# Canon Consistency - " + today)
    lines.append("")
    lines.append("**Pages scanned:** " + str(pages_scanned))
    sev_counts = {sev: 0 for sev in dashboard.SEVERITY_ORDER}
    for f in findings:
        sev_counts[f["severity"]] += 1
    counts_strs = []
    for sev in dashboard.SEVERITY_ORDER:
        n = sev_counts[sev]
        counts_strs.append("{} {}{}".format(n, sev, "s" if n != 1 else ""))
    lines.append(
        "**Findings:** {} ({})".format(len(findings), " / ".join(counts_strs))
    )
    lines.append("")

    if not findings:
        lines.append("No canon consistency findings.")
        lines.append("")
        return "\n".join(lines)

    by_mode = {mode: [] for mode in MODE_ORDER}
    for f in findings:
        by_mode[f["mode"]].append(f)

    if by_mode[MODE_PAGE_VS_CANON]:
        lines.append("## Mode 1 - Page vs Canon")
        for f in by_mode[MODE_PAGE_VS_CANON]:
            lines.append(_render_mode1_line(f))
        lines.append("")

    if by_mode[MODE_PAGE_VS_PAGE]:
        lines.append("## Mode 2 - Page vs Page")
        for f in by_mode[MODE_PAGE_VS_PAGE]:
            lines.append(_render_mode2_line(f))
        lines.append("")

    return "\n".join(lines)


def _render_mode1_line(f: Dict[str, Any]) -> str:
    if f["reason"] == REASON_VALUE_MISMATCH:
        return (
            "- {sev}: {page}: {claim_key} -> page={page_value!r} "
            "canon={canon_value!r}: {reason}"
        ).format(sev=f["severity"], **f)
    return (
        "- {sev}: {page}: {claim_key}: {reason}"
    ).format(sev=f["severity"], **f)


def _render_mode2_line(f: Dict[str, Any]) -> str:
    pages_text = ", ".join(
        "{}={!r}".format(p["path"], p["value"]) for p in f["pages"]
    )
    return (
        "- {sev}: {claim_key}: {reason} ({pages_text})"
    ).format(sev=f["severity"], pages_text=pages_text, **f)


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
            "error: canon yaml is structurally malformed: {}".format(exc),
            file=stderr,
        )
        return 2
    except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as exc:
        print("error: {}".format(exc), file=stderr)
        return 2

    findings = summary["findings"]
    for f in findings:
        if f["mode"] == MODE_PAGE_VS_CANON:
            print(dashboard.strip_finding_bullet(_render_mode1_line(f)), file=stdout)
        else:
            print(dashboard.strip_finding_bullet(_render_mode2_line(f)), file=stdout)

    rel = summary["dashboard_path"].relative_to(wiki_root).as_posix()
    print("canon_consistency: pages_scanned={} findings={} -> {}".format(
        summary["pages_scanned"],
        len(findings),
        rel,
    ), file=stdout)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(_main(WIKI_ROOT))
