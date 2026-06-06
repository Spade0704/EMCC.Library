"""S1-doc check helper for Lattice v0.1.8 Scribe persona Loop §3c.

Frontmatter parseability + cross-ref integrity + markdown lint validation for
doc-class file edits. Permissive stringency per LATTICE_v0.1.8_SCRIBE_SPEC.md
§2.5: only structural errors fail (ok=False); warnings preserve ok=True for
audit-trail visibility without blocking the atomic batch commit.

Public API:
    check_frontmatter(path: Path) -> FrontmatterResult
    check_cross_refs(path: Path, repo_root: Path) -> CrossRefResult
    check_markdown_lint(path: Path) -> MarkdownLintResult
    s1_doc(path: Path, repo_root: Path) -> S1DocResult

Result types are dataclasses; each carries ok: bool + errors: list[str] +
warnings: list[str] + check-specific diagnostic fields. S1DocResult composite
aggregates: ok = all sub-checks ok; errors and warnings concatenated; per-check
sub-fields retained for downstream inspection.

Reference: spec §2.5 (S1-doc semantics), §2.3 (Codex content-page schema for
required-key warnings), §5.7.bis (this module's contract).

Behavioral contracts:
- Initial-heading-skip (S023-T2-α AC3): a doc whose first heading is at depth
  > 1 (e.g. starts with `### X` with no preceding H1/H2) emits a heading-
  hierarchy warning. Pre-T2-α behavior was silent on this case; Read B locked.
- Persona-class fm schema (S023-T2-α AC6): files identified as persona-class
  (either fm `type: persona` OR path under `.claude/personas/CLAUDE.*.md`)
  use a leaner schema — required={title}, allow-list adds {type, role,
  visibility, canonical_source, loaded_via, last_updated} on top of the
  Codex-default allowed set. AC6 ships structural-not-schematic; canonical
  schema reconciliation tracked in arch-notes for B3.
- P1 contract: this module assumes `_lib.frontmatter.parse_frontmatter` does
  not raise. If a future P1 change introduces an exception path, callers of
  s1_doc will see it propagate uncaught; revisit then.
"""

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from _lib import frontmatter as _frontmatter
from _lib.frontmatter import find_frontmatter_close
from _lib.markdown import strip_code


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Required keys per CODEX_BUILD_SPEC_v1_1.md §2.3 content-page schema. Files
# that opt in by opening a frontmatter block must carry these keys; missing
# keys produce warnings (NOT errors per spec §2.5 permissive stringency).
_REQUIRED_FM_KEYS = (
    "title",
    "type",
    "visibility",
    "completion",
    "status",
    "last_updated",
    "canon_sources",
    "unverified_claims",
)

# Allow-list of fm keys that don't trigger 'unknown key' warning.
# Derived from `_lib.frontmatter.SPEC_2_3_FM_FIELDS` (SSOT registry per
# CODEX_BUILD_SPEC_v1_3.md §2.3) + project-precedent extras (version /
# role / audience — not spec §2.3 fields but accepted by Codex by
# convention). Drift-impossible by construction: spec §2.3 changes
# → registry updates → this set auto-updates without a second edit.
# S048-T0 structural cure (supersedes S047-T7 advisory cadence note).
_ALLOWED_FM_KEYS = frozenset(
    _frontmatter.SPEC_2_3_FM_FIELDS + ("version", "role", "audience")
)

# Persona-class schema variant per S023-T2-α AC6. Triggered by either fm
# `type: persona` OR file path matches `.claude/personas/CLAUDE.*.md`.
# Required-set deliberately {title} only — schema fragmentation across the 4
# persona drop-ins (Architect/Auditor/Craftsman use type+role+visibility;
# Scribe uses loaded_via, lacks type+visibility) precludes a stricter common
# floor. Allow-list extends Architect plan_response GO 6-key set with
# `last_updated` (universally present in all 4 drop-ins) — Craftsman
# judgment to satisfy AC6 'lint with 0 warnings' acceptance test;
# documented in build_summary surprises[] for canonical reconciliation in B3.
_PERSONA_REQUIRED_FM_KEYS = ("title",)
_PERSONA_ALLOWED_FM_KEYS = frozenset((
    "title",
    "type",
    "role",
    "visibility",
    "canonical_source",
    "loaded_via",
    "last_updated",
))

# Strict per-line shape inside a frontmatter block. Accepts: blank, comment,
# key (simple identifier followed by colon), block-style list-continuation
# (- value). Rejects free-prose lines per spec §2.5 'parseable YAML (error
# if not)'.
_FM_LINE_SHAPE_RE = re.compile(
    r"^(?:\s*$|\s*#|[A-Za-z_][A-Za-z0-9_]*\s*:|\s*-\s)"
)

# Markdown link with relative .md path, optional anchor: [text](path.md#anchor).
# Captures the path-with-optional-anchor in group 1. Rejects whitespace or
# closing paren in URL portion (defensive against accidental neighbours).
_MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\s]+\.md(?:#[^)\s]*)?)\)")

# Bare text-form reference to documents/lattice/<...>.md — text mention not
# inside markdown link syntax. Matches after strip_code() so code-block
# documented examples don't false-positive. Word-boundary prefix (\b) per
# S023-T2-α AC2 — rejects 'xdocuments/lattice/foo.md' false-positive.
_LATTICE_TEXT_REF_RE = re.compile(r"\bdocuments/lattice/[\w.-]+\.md")

# Standalone code fence marker (``` or ~~~ optionally followed by language tag,
# nothing else on the line). Used for unclosed-fence detection on raw text;
# strip_code() handles paired-fence stripping for downstream lint scans.
# 0-3 leading spaces tolerated per CommonMark + S023-T2-α AC4 (4+ spaces
# becomes indented-code, outside fence syntax).
_FENCE_LINE_RE = re.compile(r"^[ ]{0,3}(?:```|~~~)\s*[\w-]*\s*$")

# Heading line: 1-6 #'s + space + non-whitespace content. Per markdown spec,
# `#foo` (no space) is NOT a heading.
_HEADING_RE = re.compile(r"^(#{1,6})\s+\S")


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class FrontmatterResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    parsed: Optional[dict] = None
    required_keys_missing: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)


@dataclass
class CrossRefResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    refs_checked: int = 0
    dead_refs: List[str] = field(default_factory=list)


@dataclass
class MarkdownLintResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fence_count: int = 0
    heading_skips: List[str] = field(default_factory=list)
    table_mismatches: List[str] = field(default_factory=list)


@dataclass
class S1DocResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    frontmatter: Optional[FrontmatterResult] = None
    cross_refs: Optional[CrossRefResult] = None
    markdown_lint: Optional[MarkdownLintResult] = None
    elapsed_seconds: float = 0.0


@dataclass
class ConsequenceResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    consequence: str = "high"          # resolved tier: "high" | "low"
    cite_anchor: Optional[str] = None
    field_present: bool = False         # True only if a recognized high|low was declared
    enforced: bool = False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_persona_class(path: Path, parsed_fm: Optional[Dict[str, Any]]) -> bool:
    """Detect persona-class file via fm `type: persona` OR path `.claude/personas/CLAUDE.*.md`.

    Dual-trigger per S023-T2-α AC6 — covers Architect/Auditor/Craftsman drop-ins
    via fm type AND covers Scribe (no type field) via path. Returns True if
    either signal matches.
    """
    if parsed_fm is not None and parsed_fm.get("type") == "persona":
        return True
    parts = Path(path).parts
    if ".claude" in parts and "personas" in parts:
        name = Path(path).name
        if name.startswith("CLAUDE.") and name.endswith(".md"):
            return True
    return False


def _strict_frontmatter_check(text: str) -> Tuple[List[str], List[str]]:
    """Strict shape pre-check; runs BEFORE delegating to P1 parse_frontmatter.

    Returns (errors: list[str], warnings: list[str]).
    Errors: unclosed block; per-line shape violation.
    Warnings: none from this helper (required-key + unknown-key warnings flow
    from check_frontmatter after dict-extraction).
    """
    errors = []
    warnings = []
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return errors, warnings
    close = find_frontmatter_close(lines)
    if close is None:
        errors.append("frontmatter: unclosed block (--- on line 1, no later ---)")
        return errors, warnings
    for idx in range(1, close):
        line = lines[idx]
        if not _FM_LINE_SHAPE_RE.match(line):
            errors.append(f"frontmatter: malformed line {idx + 1}: {line!r}")
    return errors, warnings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_frontmatter(path: Path) -> FrontmatterResult:
    """Validate frontmatter parseability + key set per spec §2.3.

    Files without a frontmatter block (line 1 != '---') pass silently —
    README.md / CHANGELOG.md / tasks/* don't opt in. Files that DO open a
    block must close cleanly + match shape; required keys warn; unknown keys
    warn.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    errors, warnings = _strict_frontmatter_check(text)
    if errors:
        return FrontmatterResult(ok=False, errors=errors, warnings=warnings)

    parsed = _frontmatter.parse_frontmatter(text)
    if parsed is None:
        # Persona-class detection still runs without fm — pure path-trigger
        # case (e.g., a malformed persona file with no fm). Currently returns
        # ok=True with no warnings since required-set check requires opt-in.
        return FrontmatterResult(ok=True, parsed=None)

    if _is_persona_class(path, parsed):
        required = _PERSONA_REQUIRED_FM_KEYS
        allowed = _PERSONA_ALLOWED_FM_KEYS
    else:
        required = _REQUIRED_FM_KEYS
        allowed = _ALLOWED_FM_KEYS

    missing = [k for k in required if k not in parsed]
    if missing:
        warnings.extend(
            f"frontmatter: missing required key {k!r}" for k in missing
        )
    unknown = [k for k in parsed.keys() if k not in allowed]
    if unknown:
        warnings.extend(
            f"frontmatter: unknown key {k!r} (not in allow-list)" for k in unknown
        )
    return FrontmatterResult(
        ok=True,
        errors=errors,
        warnings=warnings,
        parsed=parsed,
        required_keys_missing=missing,
        unknown_keys=unknown,
    )


def _count_frontmatter_key(text: str, key: str) -> int:
    """Count top-level (column-0) occurrences of ``key:`` in the frontmatter block.

    Detects an ambiguous duplicate declaration: the subset parser keeps
    last-wins, so a trailing duplicate could silently flip a resolved tier.
    Returns 0 when there is no frontmatter block.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return 0
    close = find_frontmatter_close(lines)
    if close is None:
        return 0
    pat = re.compile(rf"^{re.escape(key)}\s*:")
    return sum(1 for idx in range(1, close) if pat.match(lines[idx]))


def check_consequence(path: Path, enforce: bool = False) -> ConsequenceResult:
    """Consequence/cite lint (caution-lint spike) — read-only.

    Resolves a page's consequence tier from frontmatter and, for HIGH pages,
    requires a non-empty ``cite_anchor`` so accuracy-critical content is always
    traceable to a verbatim source.

    Fail-safe: a missing OR unrecognized ``consequence`` value resolves to HIGH
    (never silently LOW). Only an explicit ``consequence: low`` opts out.

    Report-only by default (``enforce=False`` -> WARNING, ``ok=True``) so the
    lint can run across an un-migrated wiki without red-barring it.
    ``enforce=True`` promotes the finding to an ERROR (``ok=False``) — opt-in
    per wiki once migrated.

    The field name ``consequence`` is provisional for this spike; the final
    contract (``consequence`` vs ``verbatim``) is locked at canon promotion —
    it is the cross-module class the Gateway compression fence also reads. No
    canon file is touched here. This function only READS the file (block-level
    effectivity-normalization is a separate, out-of-scope experiment).
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        # Fail-closed: an unreadable page must NEVER raise. A raise in a build
        # gate is fail-OPEN — it would abort the caller's loop and skip every
        # page after the poison file. Treat unreadable as HIGH-unverified and
        # route through the same enforce/report-only finding logic.
        result = ConsequenceResult(
            ok=True, consequence="high", field_present=False, enforced=enforce,
        )
        msg = (f"consequence: file unreadable ({type(exc).__name__}) -> treated as "
               "HIGH-unverified (cannot confirm cite_anchor)")
        if enforce:
            result.ok = False
            result.errors.append(msg)
        else:
            result.warnings.append(msg)
        return result

    parsed = _frontmatter.parse_frontmatter(text)

    raw = parsed.get("consequence") if parsed is not None else None
    norm = raw.strip().lower() if isinstance(raw, str) else None
    # A duplicate top-level `consequence:` key is ambiguous (parser is
    # last-wins, so a trailing `consequence: low` could flip a HIGH page).
    duplicate = _count_frontmatter_key(text, "consequence") > 1

    if duplicate:
        tier, field_present = "high", False  # ambiguous -> fail-safe HIGH
    elif norm == "low":
        tier, field_present = "low", True
    elif norm == "high":
        tier, field_present = "high", True
    else:
        tier, field_present = "high", False  # absent / non-str / unrecognized -> fail-safe HIGH

    cite = None
    if parsed is not None:
        c = parsed.get("cite_anchor")
        if isinstance(c, str) and c.strip():
            cite = c.strip()

    result = ConsequenceResult(
        ok=True,
        consequence=tier,
        cite_anchor=cite,
        field_present=field_present,
        enforced=enforce,
    )

    if tier == "low" or cite is not None:
        return result

    # HIGH page with no cite_anchor — the finding.
    if not field_present:
        if duplicate:
            msg = ("consequence: duplicate `consequence` key -> treated as HIGH "
                   "(fail-safe); declare it exactly once as high|low")
        elif raw is None:
            msg = ("consequence: no `consequence` field -> treated as HIGH "
                   "(fail-safe); add a cite_anchor, or set consequence: low to opt out")
        else:
            msg = (f"consequence: unrecognized value {raw!r} -> treated as HIGH "
                   "(fail-safe); use high|low, add a cite_anchor, or set consequence: low")
    else:
        msg = ("consequence: HIGH page missing required cite_anchor "
               "(add a verbatim source ref, or set consequence: low)")

    if enforce:
        result.ok = False
        result.errors.append(msg)
    else:
        result.warnings.append(msg)
    return result


def check_cross_refs(path: Path, repo_root: Path) -> CrossRefResult:
    """Validate internal markdown links + bare text-form lattice refs.

    Markdown links to .md files (with optional anchor) must resolve under
    repo_root. External URLs (http/https/mailto) and anchors-only (#sec) are
    skipped per spec §2.5. Bare 'documents/lattice/<...>.md' text mentions
    also validated. Refs inside fenced/inline code blocks are stripped before
    scan via _lib.markdown.strip_code.
    """
    path = Path(path)
    repo_root = Path(repo_root).resolve()
    text = path.read_text(encoding="utf-8")
    scrubbed = strip_code(text)

    errors = []
    warnings = []
    refs_checked = 0
    dead_refs = []
    seen = set()

    for m in _MD_LINK_RE.finditer(scrubbed):
        ref = m.group(1)
        if ref.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = ref.split("#", 1)[0]
        key = ("md", target)
        if key in seen:
            continue
        seen.add(key)
        refs_checked += 1
        if target.startswith("/"):
            resolved = (repo_root / target.lstrip("/")).resolve()
        else:
            resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"cross_refs: dead link {ref!r} (resolved {resolved})")
            dead_refs.append(ref)

    for m in _LATTICE_TEXT_REF_RE.finditer(scrubbed):
        ref = m.group(0)
        key = ("text", ref)
        if key in seen:
            continue
        seen.add(key)
        refs_checked += 1
        resolved = (repo_root / ref).resolve()
        if not resolved.exists():
            errors.append(
                f"cross_refs: dead text reference {ref!r} (resolved {resolved})"
            )
            dead_refs.append(ref)

    return CrossRefResult(
        ok=not errors,
        errors=errors,
        warnings=warnings,
        refs_checked=refs_checked,
        dead_refs=dead_refs,
    )


def check_markdown_lint(path: Path) -> MarkdownLintResult:
    """Validate code-fence pairing + heading hierarchy + table column count.

    Unclosed fence: error (counted on raw text). Heading skip: warning (depth
    jump > 1; runs on stripped text). Table column-count mismatch: warning
    (contiguous |-prefixed rows; stripped).
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    raw_lines = text.split("\n")
    errors = []
    warnings = []
    heading_skips = []
    table_mismatches = []

    fence_lines = sum(1 for line in raw_lines if _FENCE_LINE_RE.match(line))
    if fence_lines % 2 != 0:
        errors.append(
            f"markdown_lint: unclosed code fence (standalone-fence-line count "
            f"{fence_lines}, expected even)"
        )

    scrubbed_lines = strip_code(text).split("\n")
    last_depth = 0
    in_table = False
    table_first_col_count = None
    table_start_line = None

    for idx, line in enumerate(scrubbed_lines, start=1):
        m = _HEADING_RE.match(line)
        if m:
            depth = len(m.group(1))
            if last_depth == 0 and depth > 1:
                # S023-T2-α AC3: initial heading at depth > 1 (no preceding
                # H1) is now a warning. Pre-T2-α: silent.
                msg = (
                    f"markdown_lint: initial heading depth H{depth} at line "
                    f"{idx} (no H1 preceding)"
                )
                warnings.append(msg)
                heading_skips.append(msg)
            elif last_depth and depth > last_depth + 1:
                msg = (
                    f"markdown_lint: heading hierarchy skip at line {idx} "
                    f"(H{last_depth} -> H{depth})"
                )
                warnings.append(msg)
                heading_skips.append(msg)
            last_depth = depth
            in_table = False
            table_first_col_count = None
            continue
        stripped = line.strip()
        if (stripped.startswith("|") and stripped.endswith("|")
                and len(stripped) > 1):
            # S023-T2-α AC1: strip escape-pipe `\|` before counting separators.
            # Otherwise table cells containing literal `\|` (used to escape a
            # pipe within markdown table syntax) inflate the col-count and
            # produce false-positive col-mismatch warnings.
            cols = stripped.replace(r"\|", "").count("|") - 1
            if not in_table:
                in_table = True
                table_first_col_count = cols
                table_start_line = idx
            elif cols != table_first_col_count:
                msg = (
                    f"markdown_lint: table column-count mismatch at line {idx} "
                    f"(table starts line {table_start_line} with "
                    f"{table_first_col_count} cols; this row has {cols})"
                )
                warnings.append(msg)
                table_mismatches.append(msg)
        else:
            in_table = False
            table_first_col_count = None

    return MarkdownLintResult(
        ok=not errors,
        errors=errors,
        warnings=warnings,
        fence_count=fence_lines,
        heading_skips=heading_skips,
        table_mismatches=table_mismatches,
    )


def s1_doc(path: Path, repo_root: Path) -> S1DocResult:
    """Composite S1-doc check: aggregates frontmatter + cross_refs + markdown_lint.

    ok = all 3 sub-checks ok. errors / warnings = concatenation of sub-check
    errors / warnings (sub-check breakdown retained in result fields).
    """
    start = time.perf_counter()
    fm_result = check_frontmatter(path)
    cr_result = check_cross_refs(path, repo_root)
    ml_result = check_markdown_lint(path)
    elapsed = time.perf_counter() - start

    all_errors = list(fm_result.errors) + list(cr_result.errors) + list(ml_result.errors)
    all_warnings = (
        list(fm_result.warnings) + list(cr_result.warnings) + list(ml_result.warnings)
    )

    return S1DocResult(
        ok=fm_result.ok and cr_result.ok and ml_result.ok,
        errors=all_errors,
        warnings=all_warnings,
        frontmatter=fm_result,
        cross_refs=cr_result,
        markdown_lint=ml_result,
        elapsed_seconds=elapsed,
    )
