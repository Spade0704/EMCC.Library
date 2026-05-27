"""Shared dashboard primitives — fm header builder + section grouping helper.

Promoted from per-script duplication in P4 (collect_open_questions), P5
(build_completion_dashboard), P6 (validate_terminology), P7
(validate_canon_integrity), P8 (validate_reveal_conceit), P9
(check_cross_refs) per BUILD_DISCIPLINE 3rd-consumer rule. Gates P10
(check_cascade) to import from here rather than duplicating to a 7th
consumer. Mirrors P8.5 `_lib/markdown.py` promotion precedent. Pure stdlib.

Public API:
    render_fm_header(title: str, today: str) -> List[str]
        Build the 7-line fm header shared by every dashboard:
        `---`, `title: "<title>"`, `type: dashboard`,
        `visibility: internal`, `generated: true`,
        `last_updated: <iso-date>`, `---`. `today` is REQUIRED
        (no default) — callers control the date source via explicit
        named-arg to lock the LOCAL-date convention per
        architect-notes #36 + S035 hotfix `a6ce5e1` (which aligned
        all 12 pre-T2 call sites to `today=date.today().isoformat()`
        after a prior UTC-vs-LOCAL drift). Required-arg signature
        mechanically prevents future default-vs-explicit drift
        recurrence. P19 update_dashboards (S037-T2) becomes 13th
        consumer using the same convention.
        Output is byte-identical to the inline implementations it
        replaces (AC3 invariant; pinned by
        tests::RenderFmHeaderTests::test_byte_identical_to_legacy_inline).

    SEVERITY_ORDER: Final[Tuple[str, ...]] = ("error", "warning", "info")
        Canonical severity render order. P6 uses all 3; P8 filters info
        upstream and produces empty info bucket (iteration skips empty
        sections via consumer-side `if not bucket: continue` guard).

    BAND_ORDER: Final[Tuple[str, ...]] = ("ready", "solid", "outlined", "gap")
        Canonical completion-band render order per spec §2.3 status bands
        (R_DATA > D_SCHEMAS).

    group_by_fixed_order(items, order, key_fn) -> Dict[str, List[T]]
        Generic by-class grouping: for each item, append to bucket
        `key_fn(item)`; returns dict keyed by the `order` tuple with
        empty lists for classes that received no items. Covers both
        by-severity (P6/P8) AND by-band (P5) call-sites with one
        helper. Caller controls section render order by iterating
        `order`; empty buckets handled by consumer-side
        `if not bucket: continue` skip.

    strip_finding_bullet(line: str) -> str
        Strip the leading `- ` bullet prefix from a `_render_*_line`
        output via literal slice + `startswith('- ')` prefix-guard.
        Used by P12/P13/P14/P15 stdout-summary printing where the
        bullet prefix appropriate for dashboard markdown is unwanted
        for CLI summary output. Literal slice avoids `.lstrip('- ')`
        char-class strip (which would also strip leading `-` from
        negative numbers in finding text — latent footgun closed by
        S037-T1 5-site SSOT consolidation; promoted per S035 banking
        #5 codification 3rd-consumer-or-more threshold met at 5 sites
        / 4 modules; mirror S034-T6 a7b730f `_lib.dashboard`
        promotion precedent).

    write_dashboard(wiki_root: Path, relative: str, content: str) -> Path
        Build out_path = wiki_root / relative; mkdir parents; UTF-8
        write content; return absolute out_path. SSOT for the
        14-site dashboard-write idiom surfaced by S046-T0a aggregator
        DRY pass. T0a swaps 5 sites (4 aggregators P4/P5/P15/P16 +
        P19 orchestrator health.md emit); remaining 10 validator
        sites (P6-P14) deferred to future cleanup sweep per JP T0a
        scope.
"""

from pathlib import Path
from typing import Callable, Dict, Final, Iterable, List, Tuple, TypeVar


SEVERITY_ORDER: Final[Tuple[str, ...]] = ("error", "warning", "info")
BAND_ORDER: Final[Tuple[str, ...]] = ("ready", "solid", "outlined", "gap")


def render_fm_header(title: str, today: str) -> List[str]:
    """Return the 7-line dashboard fm header as a list of lines (no newlines).

    `today` is REQUIRED (no default). Callers control the date source via
    explicit named-arg — locks the LOCAL-date convention per architect-notes
    #36 + S035 hotfix `a6ce5e1` (UTC-vs-LOCAL drift pre-corrected across all
    12 then-existing call sites; required-arg signature mechanically prevents
    recurrence). Output format is byte-identical to the inline implementations
    across all 6 consumers pre-promotion (AC3 invariant; pinned by unit test).
    Edit this format only with paired test update.
    """
    return [
        "---",
        'title: "{}"'.format(title),
        "type: dashboard",
        "visibility: internal",
        "generated: true",
        "last_updated: " + today,
        "---",
    ]


T = TypeVar("T")


def group_by_fixed_order(
    items: Iterable[T],
    order: Tuple[str, ...],
    key_fn: Callable[[T], str],
) -> Dict[str, List[T]]:
    """Group `items` by `key_fn(item)` into buckets keyed by `order`.

    Returns a dict with one key per `order` entry; classes that received
    zero items stay as empty lists (caller-side `if not bucket: continue`
    skips empty section render). Within-bucket order preserves insertion
    order (Python list append semantics). Items whose key_fn result is
    not in `order` will raise KeyError — by design; callers are expected
    to pre-filter or use only known classes.
    """
    grouped: Dict[str, List[T]] = {name: [] for name in order}
    for item in items:
        grouped[key_fn(item)].append(item)
    return grouped


def strip_finding_bullet(line: str) -> str:
    """Strip the leading `- ` bullet prefix via literal slice.

    Defensive prefix-check guards against silent malformation; the
    invariant is pinned by `_render_*_line` callers always emitting
    a `- ` prefix. Literal slice avoids `.lstrip('- ')` char-class
    strip (which would also strip leading `-` from negative numbers
    in finding text — latent footgun closed by S037-T1 5-site SSOT
    consolidation per S035 banking #5 codification).
    """
    if line.startswith("- "):
        return line[2:]
    return line


def write_dashboard(wiki_root: Path, relative: str, content: str) -> Path:
    """Write `content` to `wiki_root / relative`; create parents; return path.

    SSOT for the dashboard-write idiom (mkdir parents + UTF-8 write_text)
    shared across aggregators + orchestrator. Returns the absolute path
    so callers can include it in their summary dicts without rebuilding.
    """
    out_path = wiki_root / relative
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path
