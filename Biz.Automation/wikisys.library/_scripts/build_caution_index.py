"""build_caution_index.py — deterministic tiered caution-index (Cairn-absorption item 2).

A cheap, grep-able ROUTER layer over a wiki's content tree. For every
HIGH-`consequence` page it surfaces, **verbatim**, the page's `cite_anchor`
and any explicitly-marked caution lines, each tagged with the source page
path. The index IS the cheap tier; the full source page is the on-demand tier
(a router row points at the page; the reader loads it). The retriever is the
consumer's existing "grep the index, load 1-3 files" discipline — this script
builds the deterministic, keyword-taggable index that grep operates over; it
NEVER picks for you.

Council: `EMCC/tasks/council/2026-06-13-library-cairn-absorption-track.md`
(build item 2). Charter: `EMCC.Gateway/tasks/plans/cairn-phase0-reframed.md`.
Accuracy contract: `wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md`
§"Accuracy contract" + `…/01-Architecture/Frontmatter-Schema.md`
§"Accuracy fields".

KILL-CONSTRAINTS (council-locked; this module is the safety path):

  (a) DETERMINISTIC ONLY. Pure stdlib (`re`, `pathlib`). No model, no
      embedding, no TF-IDF, no sentiment — nothing non-deterministic enters
      the caution path. A page is HIGH iff the shipped, tested, fail-safe
      `doc_lint.check_consequence` resolver says so. Caution text is extracted
      by an EXPLICIT literal marker (`> [!CAUTION]` / `> [!WARNING]` /
      `> [!DANGER]` by default; tunable per wiki) and copied BYTE-FOR-BYTE —
      never summarised, never paraphrased (respects the shipped verbatim-only
      policy, `d2c7667`).

  (b) AMBIGUITY-REFUSE / ESCALATE is the definition-of-done. The danger the
      council named: a router that silently returns the WRONG caution verbatim
      is MORE dangerous than no router — citable and confident. So the index
      FAILS CLOSED. A HIGH page that cannot be resolved to a verbatim
      caution+cite gets NO confident caution row; it gets an **ESCALATE** row
      that surfaces no caution text and instead points at the full verbatim
      source page. Ambiguity = any of:
        1. HIGH page with no usable `cite_anchor` (can't anchor a caution to a
           verbatim source).
        2. HIGH page declared via a fail-safe path (absent / duplicate /
           unrecognised `consequence`) — HIGH but unverifiable.
        3. HIGH page whose marked caution region is empty / whitespace.
      Where N HIGH pages share a caution keyword, the index lists ALL N rows
      (honest multiplicity) — it never collapses or picks one.

The worst case this index can produce is "load the full source yourself"
(extra verbatim content), never a fabricated or substituted caution — exactly
the fail-safe direction the Gateway Consequence-Routing-Fence locked.

Read-only: never modifies content pages. Mirrors `audit_citations.py`'s
shape (standalone audit, report-only `run()` + `--enforce` CLI opt-in) so it
can never red-bar the orchestrator pass.

CLI:
    python build_caution_index.py [--wiki-root PATH] [--json] [--enforce]

Exit codes:
    0  report-only run (default), OR --enforce run with no ESCALATE rows
    1  --enforce run with one or more ESCALATE (ambiguous / unresolved-HIGH) rows
    2  no content root resolved (malformed/empty tree)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional

from _lib import cli, dashboard, doc_lint, frontmatter, markdown


DASHBOARD_RELATIVE = "_dashboards/caution_index.md"

# Default caution markers — GitHub/Obsidian callout syntax. A line whose
# stripped form starts with one of these (case-insensitive) opens a caution
# block; the marked text is the remainder of that line plus any immediately
# following blockquote-continuation lines (`>` prefixed). DETERMINISTIC: a
# literal prefix match, never an NLP judgement about what "looks dangerous".
#
# Fail-closed-on-format: the match is an exact prefix (after strip+lower), so a
# non-canonical spelling (e.g. `>  [!caution]` with a doubled space) does NOT
# match and the page ESCALATEs to source rather than surfacing. That is the
# safe direction by design — an unrecognised marker yields "load the source",
# never a silently-surfaced caution. Authors normalise to the canonical marker
# (or extend this tuple per wiki) to get the cheap surfaced tier.
DEFAULT_CAUTION_MARKERS = ("> [!CAUTION]", "> [!WARNING]", "> [!DANGER]")
CAUTION_CONFIG_RELATIVE = "_config/caution_index.yaml"

# A blockquote continuation line (`>` possibly indented). Used to extend a
# caution block past its opening marker line, verbatim.
_BLOCKQUOTE_RE = re.compile(r"^\s*>")

# Keyword tokens for the grep/keyword tag column: maximal runs of
# alphanumerics, length >= 3, lowercased — hyphens/underscores/spaces all act
# as token separators so a slug like `torque-limit-msn-a` yields the queryable
# terms `torque`, `limit`, `msn`. Deterministic substring presence only — this
# is a grep convenience, NOT a ranking signal.
_KEYWORD_RE = re.compile(r"[a-z0-9]{3,}")


class CautionRow(NamedTuple):
    path: str              # content-root-relative posix path (the source pointer)
    status: str            # "surfaced" | "escalate"
    consequence: str       # resolved tier (always "high" for emitted rows)
    cite_anchor: str       # verbatim cite_anchor, or "" when absent
    cautions: List[str]    # verbatim caution lines (empty for escalate rows)
    keywords: List[str]    # deterministic grep tags (sorted, deduped)
    reason: str            # why this row escalated (empty for surfaced rows)


def _extract_caution_blocks(body: str, markers: tuple) -> List[str]:
    """Return verbatim caution blocks from a page body.

    A caution block opens on a line whose stripped form starts (case-
    insensitively) with one of `markers`, and extends across immediately
    following blockquote-continuation (`>`) lines. The returned text is a
    BYTE-FOR-BYTE slice of the source lines (joined with the original `\\n`),
    with no normalisation — verbatim is the contract.

    Code fences are stripped first (a `> [!CAUTION]` inside a fenced example is
    documentation, not a live caution) using the same strip-code helper the
    body-scanning validators use; line indices are preserved by strip_code so
    the slice maps back onto the original `body` lines exactly.
    """
    lower_markers = tuple(m.lower() for m in markers)
    scrubbed_lines = markdown.strip_code(body).split("\n")
    raw_lines = body.split("\n")
    blocks: List[str] = []
    i = 0
    n = len(scrubbed_lines)
    while i < n:
        stripped = scrubbed_lines[i].strip().lower()
        if any(stripped.startswith(m) for m in lower_markers):
            start = i
            j = i + 1
            # extend across blockquote-continuation lines (verbatim region)
            while j < n and _BLOCKQUOTE_RE.match(scrubbed_lines[j]):
                j += 1
            # slice the ORIGINAL (un-scrubbed) lines — verbatim
            block = "\n".join(raw_lines[start:j])
            blocks.append(block)
            i = j
        else:
            i += 1
    return blocks


def _has_nonempty_caution(blocks: List[str]) -> bool:
    """True iff at least one block carries text beyond the marker itself.

    A bare `> [!CAUTION]` with no following content is an EMPTY caution — it
    declares danger but surfaces nothing, which is ambiguity (case 3). We
    refuse to treat it as a usable verbatim caution.
    """
    for block in blocks:
        # remove the marker token and blockquote `>` punctuation, see what
        # real text remains
        residue = re.sub(r"\[![a-zA-Z]+\]", "", block)
        residue = re.sub(r"^\s*>", "", residue, flags=re.MULTILINE)
        if residue.strip():
            return True
    return False


def _keywords_from(*texts: str) -> List[str]:
    """Deterministic grep-tag tokens: lowercased word-boundary alphanumerics,
    length >= 3, deduped and sorted. A convenience for grep over the index —
    presence only, never a weight."""
    seen = set()
    for t in texts:
        for m in _KEYWORD_RE.finditer(t.lower()):
            seen.add(m.group(0))
    return sorted(seen)


def build_caution_index(wiki_root: Path) -> List[CautionRow]:
    """Walk content pages; emit one CautionRow per HIGH page (deterministic).

    Pure: returns rows, writes nothing. A page is HIGH iff
    `doc_lint.check_consequence` resolves it HIGH (fail-safe). LOW pages are
    skipped entirely. Each HIGH page yields exactly one row:
      - **surfaced** — has a usable `cite_anchor` AND at least one non-empty
        verbatim caution block. Caution text is copied byte-for-byte.
      - **escalate** — anything ambiguous (no cite / fail-safe-HIGH path /
        empty caution region). Carries NO caution text; points at the source.
    """
    rows: List[CautionRow] = []
    for page in markdown.iter_content_pages(wiki_root):
        cres = doc_lint.check_consequence(page)
        if cres.consequence != "high":
            continue  # LOW pages opt out of the safety path entirely

        rel = page.relative_to(wiki_root).as_posix()
        loaded = frontmatter.load_page(page)
        fm = loaded["frontmatter"]
        body = loaded["body"]
        title = str(fm.get("title", "")) if fm else ""

        cite = cres.cite_anchor or ""
        blocks = _extract_caution_blocks(body, DEFAULT_CAUTION_MARKERS)

        # --- Ambiguity gate (fail-closed). Any trip -> ESCALATE, no caution. ---
        # case 2: HIGH reached via a fail-safe path (absent/dup/unrecognised
        # consequence) — HIGH but the author never affirmed it -> unverifiable.
        if not cres.field_present:
            rows.append(CautionRow(
                path=rel, status="escalate", consequence="high",
                cite_anchor=cite, cautions=[],
                keywords=_keywords_from(title, rel),
                reason=("consequence resolves HIGH via fail-safe (absent / "
                        "duplicate / unrecognised) — unverifiable; load source"),
            ))
            continue
        # case 1: no usable cite_anchor -> can't anchor a caution to a verbatim
        # source.
        if not cite:
            rows.append(CautionRow(
                path=rel, status="escalate", consequence="high",
                cite_anchor="", cautions=[],
                keywords=_keywords_from(title, rel),
                reason="HIGH page has no cite_anchor — cannot anchor a verbatim caution; load source",
            ))
            continue
        # case 3: cite present but no non-empty caution region to surface.
        if not _has_nonempty_caution(blocks):
            rows.append(CautionRow(
                path=rel, status="escalate", consequence="high",
                cite_anchor=cite, cautions=[],
                keywords=_keywords_from(title, cite, rel),
                reason=("HIGH page has a cite_anchor but no non-empty caution "
                        "block to surface verbatim — load source"),
            ))
            continue

        # --- Surfaced: cite + at least one verbatim caution. Copy verbatim. ---
        rows.append(CautionRow(
            path=rel, status="surfaced", consequence="high",
            cite_anchor=cite, cautions=blocks,
            keywords=_keywords_from(title, cite, rel, *blocks),
            reason="",
        ))
    # Stable order by source path so the dashboard is reproducible across
    # filesystems/runs (iter_content_pages uses unsorted rglob). A safety-path
    # artifact reviewed in diffs must not reorder on re-run.
    rows.sort(key=lambda r: r.path)
    return rows


def _md_escape_cell(text: str) -> str:
    """Make a verbatim string safe for a single markdown table cell WITHOUT
    altering its visible characters: escape `|` so it doesn't split the cell,
    and render newlines as `<br>` so multi-line verbatim cautions stay in one
    row. The surfaced text remains byte-recoverable for a reader (the source
    page is the canonical verbatim copy; this is the index view)."""
    return text.replace("|", "\\|").replace("\n", "<br>")


def render_dashboard(rows: List[CautionRow], wiki_root: Path, enforce: bool) -> str:
    """Markdown caution-index. Two tiers: surfaced (verbatim caution + cite +
    grep keywords) and escalate (refuse — load the source). Mirrors the
    fail-safe posture in prose so the index never outruns its own contract."""
    mode = "enforce" if enforce else "report-only"
    surfaced = [r for r in rows if r.status == "surfaced"]
    escalate = [r for r in rows if r.status == "escalate"]
    lines = [
        "# Caution index (tiered, deterministic)",
        "",
        f"Root: `{wiki_root}` · mode: **{mode}** · HIGH pages: **{len(rows)}** "
        f"(surfaced **{len(surfaced)}**, escalate **{len(escalate)}**)",
        "",
        "> **Deterministic router, fail-closed.** Caution text below is a "
        "VERBATIM slice of the source page (grep/keyword retrieval, no neural "
        "picker). When a HIGH page can't be resolved to a verbatim caution+cite "
        "it is **ESCALATEd** — surfaced with NO caution text and a pointer to "
        "load the full source. This index never paraphrases, never substitutes, "
        "and never picks one caution when several match — it lists them all.",
        "",
        "> **Presence-Not-Accuracy.** A surfaced row proves a caution block is "
        "PRESENT and copied verbatim — it does NOT verify the caution is the "
        "correct one for the reader's effectivity/variant. Load the cited source "
        "before acting.",
        "",
    ]

    lines += ["## Escalate — load the full source (do not trust a summary)", ""]
    if not escalate:
        lines += ["_No HIGH page escalated — every HIGH page resolved to a verbatim caution+cite._", ""]
    else:
        lines += ["| Source page | cite_anchor | Why escalated | grep keys |",
                  "|---|---|---|---|"]
        for r in escalate:
            lines.append(
                f"| `{r.path}` | {_md_escape_cell(r.cite_anchor) or '_none_'} "
                f"| {_md_escape_cell(r.reason)} | {' '.join(r.keywords[:12])} |"
            )
        lines.append("")

    lines += ["## Surfaced — verbatim caution + cite (the cheap tier)", ""]
    if not surfaced:
        lines += ["_No HIGH page carries a surfaceable verbatim caution block._", ""]
    else:
        lines += ["| Source page | cite_anchor | Caution (verbatim) | grep keys |",
                  "|---|---|---|---|"]
        for r in surfaced:
            caution_cell = "<hr>".join(_md_escape_cell(c) for c in r.cautions)
            lines.append(
                f"| `{r.path}` | {_md_escape_cell(r.cite_anchor)} "
                f"| {caution_cell} | {' '.join(r.keywords[:12])} |"
            )
        lines.append("")

    return "\n".join(lines) + "\n"


def run(wiki_root: Path) -> Dict[str, Any]:
    """Orchestrator entry-point — report-only caution index.

    Conforms to the `module.run(wiki_root) -> dict` contract
    `update_dashboards.py` invokes. Always report-only (the dashboard render is
    `enforce=False`) so wiring it into the orchestrator can never red-bar the
    dashboard pass — the standalone CLI keeps the `--enforce` opt-in. Writes
    `_dashboards/caution_index.md`, returns a summary dict.
    """
    wiki_root = Path(wiki_root)
    rows = build_caution_index(wiki_root)
    today = date.today().isoformat()
    header = "\n".join(dashboard.render_fm_header("Caution Index", today=today))
    content = header + "\n\n" + render_dashboard(rows, wiki_root, enforce=False)
    out_path = dashboard.write_dashboard(wiki_root, DASHBOARD_RELATIVE, content)
    return {
        "rows": [r._asdict() for r in rows],
        "rows_count": len(rows),
        "surfaced_count": sum(1 for r in rows if r.status == "surfaced"),
        "escalate_count": sum(1 for r in rows if r.status == "escalate"),
        "dashboard_path": out_path,
    }


def main(argv: Optional[List[str]] = None) -> int:
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--json", action="store_true",
                     help="emit rows as JSON instead of the markdown dashboard")
    pre.add_argument("--enforce", action="store_true",
                     help="exit 1 if any HIGH page escalated (ambiguous/unresolved)")
    known, rest = pre.parse_known_args(argv)

    default_root = frontmatter.find_wiki_content_root()
    wiki_root = cli.resolve_cli_wiki_root(default_root, argv=rest,
                                          prog="build_caution_index.py")
    if wiki_root is None or not Path(wiki_root).is_dir():
        sys.stderr.write("build_caution_index: no content root resolved\n")
        return 2

    rows = build_caution_index(Path(wiki_root))

    if known.json:
        print(json.dumps([r._asdict() for r in rows], indent=2))
    else:
        sys.stdout.write(render_dashboard(rows, Path(wiki_root), known.enforce))

    # Report-only never fails. Enforce fails only when a HIGH page escalated —
    # i.e. the index could NOT resolve it to a verbatim caution+cite.
    if known.enforce and any(r.status == "escalate" for r in rows):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
