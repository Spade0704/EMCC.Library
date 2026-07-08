"""YAML-subset parser and frontmatter loader for Codex.

Foundation module — every Codex script imports this. Pure stdlib.
Handles the YAML subset that spec §2.3 frontmatter uses: flat mapping
with scalar values (string, int, bool, null), flow-style lists
(`key: [a, b]`), and block-style scalar lists (`key:` then indented
`- item` lines — added dir-20260614qq; both list forms are equivalent,
inline is the canonical/preferred form per spec §2.3). Comments (#),
quoted strings, and `~` as null supported.

Out of scope: nested mappings, list-of-mappings (block items that are
themselves mappings), multi-line strings, YAML anchors, multi-document
streams, datetime parsing, capitalised booleans. (The richer
`parse_config_yaml` below — for `_config/*.yaml` — handles list-of-mappings
+ sub-lists; frontmatter intentionally stays flat.) Block-style scalar
lists were previously out of scope (tasks/lessons.md 2026-05-01) but caused
silent data loss — a block `canon_sources:` parsed to None — so flat scalar
block lists are now supported; structured block items still are not.
"""
# @component Codex[frontmatter]

from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def find_wiki_root():
    """Walk up from this file looking for a marker that identifies the WIKI_ROOT.

    Post-S002 (Codex v1.1) restructure: `_lib/frontmatter.py` lives at
    `Biz.Automation/wikisys.<name>/_scripts/_lib/frontmatter.py` in any v1.1
    install (Library OR consumer), but at `<wiki>/_scripts/_lib/frontmatter.py`
    in a v1.0-shape bootstrapped consuming-project wiki.

    Marker-based search handles three contexts:
    - v1.0 bootstrapped wiki: `Home.md` at the wiki root (per spec §2.2).
    - v1.1 Library install: `CLAUDE.md` + `module.json` co-existing.
    - v1.1 consumer install: `CLAUDE.md` + `emcc.modules.json` co-existing
      (consumer-side equivalent of `module.json`; added S004 MI-18 closure).

    See MIGRATION-ISSUES.md MI-17 (partial fix; this function) and MI-18
    (canon-lookup; companion `find_canon_dir()` + `find_decisions_dir()`
    below). Marker priority is loop-order: Home.md check fires first per
    ancestor iteration, so a v1.0-shape wiki always wins over a v1.1 install
    marker at a deeper ancestor. (For Library itself — a v1.1 install — the
    `wiki.codex/git/Home.md` is NOT an ancestor of `_lib/frontmatter.py`, so
    case 2 fires and returns the install root. Companion `find_*_dir()`
    helpers handle the system/content split from the install root.)
    """
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        # Case 1: ancestor IS a wiki (v1.0-shape consumer)
        if (ancestor / "Home.md").exists():
            return ancestor  # v1.0 bootstrapped wiki (or Library's wiki.codex/git/)
        if (ancestor / "CLAUDE.md").exists() and (ancestor / "module.json").exists():
            return ancestor  # v1.1 Library install
        if (ancestor / "CLAUDE.md").exists() and (ancestor / "emcc.modules.json").exists():
            return ancestor  # v1.1 consumer install
    raise RuntimeError(
        "WIKI_ROOT cannot be resolved — no marker found in any ancestor of "
        f"{here}. Expected either Home.md (v1.0 bootstrapped wiki), "
        "CLAUDE.md + module.json (v1.1 Library install), or "
        "CLAUDE.md + emcc.modules.json (v1.1 consumer install)."
    )


# Back-compat alias — keep `_find_wiki_root` for any callers that imported the
# private name from the PR #4 era. Public `find_wiki_root` is the canonical
# name post-MI-17 fix (used by all 17 scripts).
_find_wiki_root = find_wiki_root


WIKI_ROOT = find_wiki_root()


def _find_install_root(start_path):
    """Walk up from `start_path` to find a v1.1 install root.

    Install root markers (v1.1):
    - `CLAUDE.md` + `module.json` (Library install)
    - `CLAUDE.md` + `emcc.modules.json` (consumer install)

    Returns the install root Path, or None if no marker is reachable.
    Companion to `_find_wiki_root()` for MI-18 canon/decisions lookup.
    """
    start = Path(start_path).resolve()
    for ancestor in [start] + list(start.parents):
        if (ancestor / "CLAUDE.md").exists():
            if (ancestor / "module.json").exists() or (ancestor / "emcc.modules.json").exists():
                return ancestor
    return None


def _find_layout_dir(start_path, subdir, func_name):
    """Shared v1.0-wiki / v1.1-install discovery for a system-side `<subdir>/`.

    Backs `find_canon_dir` / `find_config_dir` / `find_decisions_dir` (S004
    MI-18): each of those dirs moved from `<wiki_root>/<subdir>/` to
    `<install>/Biz.Automation/wikisys.<name>/<subdir>/` in v1.1. Discovery:
    (1) `<start>/<subdir>/` if it exists (v1.0 direct child); else (2) walk up
    to an install root and return the first `wikisys.*/<subdir>/` match.

    Returns the dir Path. Raises `FileNotFoundError` (message keyed by
    `func_name`/`subdir`) if no dir is discoverable.
    """
    if start_path is None:
        start_path = WIKI_ROOT
    start = Path(start_path).resolve()

    direct = start / subdir
    if direct.is_dir():
        return direct

    install = _find_install_root(start)
    if install is not None:
        biz_root = install / "Biz.Automation"
        if biz_root.is_dir():
            for entry in sorted(biz_root.iterdir()):
                if entry.is_dir() and entry.name.startswith("wikisys."):
                    candidate = entry / subdir
                    if candidate.is_dir():
                        return candidate

    raise FileNotFoundError(
        f"{func_name}: no {subdir}/ at v1.0 path {direct} or any v1.1 "
        f"wikisys.*/{subdir}/ relative to start={start}."
    )


def find_canon_dir(start_path=None):
    """Find `_canon/` dir whether layout is v1.0 wiki or v1.1 install/consumer.

    S004 MI-18 closure. After S002 restructure, `_canon/` is no longer
    inside the wiki root for v1.1 consumers — it moves to the system-side
    zone at `<install>/Biz.Automation/wikisys.<name>/_canon/`. Scripts
    that hard-code `WIKI_ROOT/_canon/` (P13 check_concept_coverage,
    P7 validate_canon_integrity, P15 build_canon_drift_report, P12
    check_canon_consistency, validate_topic_registry, etc.) silently
    find no canon in v1.1 consumers and emit false-empty validators.

    Discovery (in order):
    1. `<start>/_canon/` if it exists (v1.0 wiki layout — direct child).
    2. Walk up from `start` to find an install root marker (per
       `_find_install_root()`), then glob
       `<install>/Biz.Automation/wikisys.*/_canon/` and return the first match.

    `start_path` defaults to `WIKI_ROOT` (per `_find_wiki_root()`).

    Raises `FileNotFoundError` if no canon dir is discoverable.
    """
    return _find_layout_dir(start_path, "_canon", "find_canon_dir")


def find_config_dir(start_path=None):
    """Find `_config/` dir whether layout is v1.0 wiki or v1.1 install/consumer.

    S004 MI-18 closure (companion to find_canon_dir + find_decisions_dir).
    `_config/` moves alongside `_canon/` and `_decisions/` to system-side
    `<install>/Biz.Automation/wikisys.<name>/_config/` in v1.1. Scripts
    reading `<wiki_root>/_config/<name>.yaml` (e.g.,
    check_concept_coverage::_load_concept_coverage_config) silently miss
    consumer customization post-migration.

    Returns the config dir Path. Raises FileNotFoundError if no _config/
    is discoverable.
    """
    return _find_layout_dir(start_path, "_config", "find_config_dir")


def find_decisions_dir(start_path=None):
    """Find `_decisions/` dir whether layout is v1.0 wiki or v1.1 install/consumer.

    Same discovery pattern as `find_canon_dir()`. Used by the dashboard
    orchestrator's `health.md` "Recent Ingest" section which reads
    `_decisions/ingest-log.md` — currently empty in Library's `health.md`
    because the generator couldn't find `_decisions/` post-S002 split
    (MI-18 surface).
    """
    return _find_layout_dir(start_path, "_decisions", "find_decisions_dir")


def _resolve_root(start_path):
    """Walk up from `start_path` (inclusive) to the nearest wiki/install root.

    Same marker set as `find_wiki_root()` but from an arbitrary start (the
    public function walks from `__file__`). Returns the first ancestor that
    is either a v1.0 wiki root (`Home.md`), a v1.1 Library install
    (`CLAUDE.md` + `module.json`), or a v1.1 consumer install
    (`CLAUDE.md` + `emcc.modules.json`). Raises RuntimeError if none found.
    """
    start = Path(start_path).resolve()
    for ancestor in [start] + list(start.parents):
        if (ancestor / "Home.md").exists():
            return ancestor
        if (ancestor / "CLAUDE.md").exists() and (ancestor / "module.json").exists():
            return ancestor
        if (ancestor / "CLAUDE.md").exists() and (ancestor / "emcc.modules.json").exists():
            return ancestor
    raise RuntimeError(
        "no wiki/install root marker found in any ancestor of "
        f"{start} (expected Home.md, CLAUDE.md+module.json, or "
        "CLAUDE.md+emcc.modules.json)."
    )


def find_wiki_content_root(start_path=None):
    """Return the wiki CONTENT root (where content pages + `_dashboards/` live).

    Distinct from `find_wiki_root()` for v1.1 installs. `find_wiki_root()`
    returns the *install* root for Library/consumer layouts (so the
    `find_*_dir()` helpers can reach the system-side `wikisys.*/_canon/` etc.).
    But content pages and generated dashboards live on the *content* side at
    `<install>/wiki.<name>/git/`. Scripts that scan pages or write
    `_dashboards/<name>.md` must target the content root, NOT the install
    root — otherwise dashboards leak to `<install>/_dashboards/` and the
    page-walk scans the whole repo (the MI-17 dashboard-relocation surface).

    Discovery:
    - v1.0 bootstrapped wiki: the resolved root has `Home.md` and IS the
      content root — return it unchanged.
    - v1.1 install: the resolved root is the install root; descend to the
      first `wiki.*/git/` content dir and return it.

    `start_path` defaults to walking from this file (matches `find_wiki_root`).
    Raises `FileNotFoundError` if no content root is discoverable.
    """
    if start_path is None:
        base = find_wiki_root()
    else:
        base = _resolve_root(start_path)

    if (base / "Home.md").exists():
        return base

    for entry in sorted(base.glob("wiki.*")):
        git_dir = entry / "git"
        if git_dir.is_dir():
            return git_dir

    raise FileNotFoundError(
        f"find_wiki_content_root: base {base} is neither a v1.0 wiki root "
        "(no Home.md) nor a v1.1 install with a wiki.*/git/ content dir."
    )


SPEC_2_3_FM_FIELDS_DOC = """SSOT registry of fm field names defined by CODEX_BUILD_SPEC_v1_3.md §2.3.

Coverage:
  - L140-167: content-page schema (15 fields — title/type/visibility/completion/
    status/phase/last_updated/dependencies/public_pair/blocking_questions/
    canon_sources/unverified_claims/source/allow_forbidden_terms/generated)
  - L158-160: brain-dump-only extra fields (dump_status/migrated_to)
  - L168-176: source-file reduced schema (source overlaps; ingested_date is unique
    to source-file class; status overlaps)
  - L183-186: v1.3 cross-link additions (topics/related_files/tags)

Consumers derive their per-class allow-lists by intersecting/uniting this tuple
with project-precedent extras. Drift-impossible by construction: spec §2.3
changes → this tuple updates → consumers (e.g. _lib/doc_lint.py
_ALLOWED_FM_KEYS) auto-update without a second edit.

S048-T0 structural cure (supersedes S047-T7 advisory cadence note).
"""

SPEC_2_3_FM_FIELDS = (
    # Content-page schema (spec §2.3 L142-156)
    "title",
    "type",
    "visibility",
    "completion",
    "status",
    "phase",
    "last_updated",
    "dependencies",
    "public_pair",
    "blocking_questions",
    "canon_sources",
    "unverified_claims",
    "source",
    "allow_forbidden_terms",
    "generated",
    # Brain-dump-only extras (spec §2.3 L158-160)
    "dump_status",
    "migrated_to",
    # Source-file reduced schema unique field (spec §2.3 L173)
    "ingested_date",
    # v1.3 cross-link additions (spec §2.3 L183-185)
    "topics",
    "related_files",
    "tags",
)


def parse_frontmatter(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse the YAML-subset frontmatter from markdown text.

    Returns the parsed dict, or None if no frontmatter block is present.
    A frontmatter block opens with `---` on the first line and closes
    with `---` on its own line later in the file.
    """
    lines = text.split("\n")
    close = find_frontmatter_close(lines)
    if close is None:
        return None
    return _parse_yaml_subset("\n".join(lines[1:close]))


def load_page(path: Union[str, Path]) -> Dict[str, Any]:
    """Read a markdown file and return its frontmatter, body, and path.

    Returns a dict with three keys:
      - "frontmatter": parsed frontmatter dict, or {} if absent
      - "body": post-frontmatter content (or the entire file when
        frontmatter is absent), verbatim
      - "path": the input Path
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    close = find_frontmatter_close(lines)
    if close is None:
        return {"frontmatter": {}, "body": text, "path": path}
    fm = _parse_yaml_subset("\n".join(lines[1:close]))
    body = "\n".join(lines[close + 1:])
    return {"frontmatter": fm, "body": body, "path": path}


def find_frontmatter_close(lines: List[str]) -> Optional[int]:
    """Return the index of the closing `---` line, or None if absent."""
    if len(lines) < 2 or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i
    return None


def _parse_yaml_subset(text: str) -> Dict[str, Any]:
    """Parse the YAML subset Codex frontmatter uses. Returns a dict.

    Flat mapping of scalar values (string / int / float / bool / null),
    flow-style lists (`key: [a, b]`), AND block-style scalar lists:

        canon_sources:
          - "a.md"
          - "b.md"

    A block list is collected only when a `key:` has an empty inline value and
    is followed by consecutive indented `- item` lines (see `_collect_block_list`).
    A bare `key:` with nothing after stays `None` (back-compat). Nested mappings
    and list-of-mappings remain out of scope — frontmatter is flat.
    """
    result = {}
    lines = text.split("\n")
    n = len(lines)
    i = 0
    while i < n:
        raw_line = lines[i]
        line = _strip_eol_comment(raw_line).rstrip()
        if not line or line.lstrip().startswith("#"):
            i += 1
            continue
        colon = line.find(":")
        if colon == -1:
            i += 1
            continue
        key = line[:colon].strip()
        value_str = line[colon + 1:].strip()
        if value_str == "":
            # Empty inline value: a block-style scalar list may follow as
            # consecutive indented `- item` lines (spec §2.3). Collect them;
            # if none follow, keep the scalar None (a bare `key:` stays None).
            items, i = _collect_block_list(lines, i + 1)
            result[key] = items if items is not None else _parse_value(value_str)
        else:
            result[key] = _parse_value(value_str)
            i += 1
    return result


def _collect_block_list(lines: List[str], start: int):
    """Collect a block-style scalar list beginning at line index `start`.

    Returns `(items, next_index)`. `items` is the list of parsed scalars, or
    `None` when no block-list item line follows (the caller then keeps the
    scalar `None`, preserving the bare-`key:` → None back-compat). A block-list
    item is an INDENTED line whose stripped content starts with `- `; each item
    is routed through `_parse_value` (so quotes/ints/etc. parse as elsewhere).
    Full-comment lines interleaved between items are skipped; a blank line or
    any non-item content line terminates the list (and is left for the caller
    to process — the cursor is not advanced past it). Only flat scalar items
    are supported; nested mappings / list-of-mappings are not.
    """
    items = None
    j = start
    n = len(lines)
    while j < n:
        raw = lines[j]
        stripped_raw = raw.strip()
        if stripped_raw == "":
            break  # blank line terminates a block list
        if stripped_raw.startswith("#"):
            j += 1  # full-comment line between items: skip, keep scanning
            continue
        cleaned = _strip_eol_comment(raw).rstrip()
        content = cleaned.lstrip()
        indent = len(cleaned) - len(content)
        if indent > 0 and content.startswith("- "):
            if items is None:
                items = []
            items.append(_parse_value(content[2:].strip()))
            j += 1
        else:
            break  # non-indented or non-dash line ends the block list
    return items, j


def _strip_eol_comment(line: str) -> str:
    """Strip an end-of-line `#` comment, respecting quoted strings."""
    if "#" not in line:
        return line
    if "'" not in line and '"' not in line:
        return line.split("#", 1)[0]
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return line[:i]
    return line


def _find_unquoted_colon(line: str) -> int:
    """Return index of first ':' outside single/double quotes, or -1 if none.

    S047 dogfood Edit-2 helper: parse_config_yaml `- ` branch needs
    quote-aware colon detection to distinguish `- "x:y"` (scalar) from
    `- key: value` (mapping).
    """
    in_single = False
    in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == ":" and not in_single and not in_double:
            return i
    return -1


def _parse_value(s: str) -> Any:
    """Parse a YAML-subset scalar or flow-list value from string `s`."""
    # S047 dogfood Edit-3: bare `~` accepted as null alongside `""`/`"null"`.
    if s == "" or s == "null" or s == "~":
        return None
    if s == "true":
        return True
    if s == "false":
        return False
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_value(item) for item in _split_flow_list(inner)]
    if len(s) >= 2 and (
        (s.startswith('"') and s.endswith('"'))
        or (s.startswith("'") and s.endswith("'"))
    ):
        return s[1:-1]
    if s.lstrip("-").isdigit():
        return int(s)
    # Float literal detection (S047-T-XL-3a): try float() after int branch
    # fails. Bool literals `true`/`false` already handled above; numeric
    # strings only reach here. Reject pure-alpha + symbol-only strings via
    # float()'s own ValueError; preserve string return for non-numeric.
    if any(ch.isdigit() for ch in s):
        try:
            return float(s)
        except ValueError:
            pass
    return s


def _split_flow_list(inner: str) -> List[str]:
    """Split a flow-list inner string by comma, respecting quotes."""
    items = []
    current = []
    in_single = False
    in_double = False
    for ch in inner:
        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
        elif ch == "," and not in_single and not in_double:
            items.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        items.append("".join(current).strip())
    return items


class ConfigYamlError(Exception):
    """Structural malformation in a config YAML file parse_config_yaml can't handle.

    The message includes a 1-indexed line number where the problem was detected.
    """


def parse_config_yaml(text: str) -> Dict[str, Any]:
    """Parse a YAML-subset config file used by `_config/*.yaml` (P6+).

    Supports three top-level shapes that may appear together:
      - Scalar key: `key: value` — value parsed via _parse_value (string,
        int, float, bool, null, flow-style list).
      - Block-style list-of-mappings key:
            key:
              - field_a: value
                field_b: value
                field_with_sublist:
                  - sub_a
                  - sub_b
              - field_a: value
        Each list item is a flat mapping. The first field's indentation
        sets the continuation indent for the rest of the item; mismatched
        continuation indents raise ConfigYamlError. Continuation fields
        with empty value followed by `- ` lines at greater indent collect
        a sub-list of scalars (S002 FINDING #1 — Mentor topics.yaml form).
      - Nested mapping (2-level; S047-T-XL-3a):
            key:
              child_a: value
              child_b: value
        Indented `key: value` lines (no dash prefix) under a top-level
        empty-value key form a nested mapping. Container type (list vs
        mapping) determined by the first indented line's prefix.

    Out of scope: nested mappings inside list items (only sub-list
    scalars), flow-style mappings inside list items, multi-line strings,
    anchors, references, multi-document streams.

    Returns a dict (empty when input is empty or whitespace-only).
    Raises ConfigYamlError on structural malformation.
    """
    result = {}
    pending_key = None     # top-level key whose container type is unresolved
    current_list = None
    current_mapping = None
    current_item = None
    current_item_indent = None
    pending_subkey = None        # S002 FINDING #1: empty-value continuation
                                 # field name whose sub-list (block-style
                                 # scalars at greater indent) we're collecting
    pending_subkey_indent = None  # indent expected for sub-list `- ` lines

    for idx, raw_line in enumerate(text.split("\n")):
        line_no = idx + 1
        no_comment = _strip_eol_comment(raw_line).rstrip()
        if not no_comment or no_comment.lstrip().startswith("#"):
            continue

        indent = len(no_comment) - len(no_comment.lstrip())
        content = no_comment[indent:]

        # S002 FINDING #1: sub-list collection under a continuation field
        # with empty value (e.g. Mentor topics.yaml block-style keywords:
        # \n  - foo\n  - bar). When pending_subkey is set, lines at greater
        # indent than current_item_indent starting with `- ` get appended
        # as scalars to current_item[pending_subkey].
        if pending_subkey is not None:
            if indent > (current_item_indent or 0) and content.startswith("- "):
                if pending_subkey_indent is None:
                    pending_subkey_indent = indent
                elif indent != pending_subkey_indent:
                    raise ConfigYamlError(
                        "line {}: inconsistent indent in sub-list under '{}' "
                        "(expected {}, got {})".format(
                            line_no, pending_subkey, pending_subkey_indent, indent
                        )
                    )
                current_item[pending_subkey].append(
                    _parse_value(content[2:])
                )
                continue
            # Indent dropped back to current_item_indent (or less) or line
            # doesn't start with `- ` — sub-list collection ends; fall through.
            pending_subkey = None
            pending_subkey_indent = None

        if indent == 0:
            # Finalize prior pending_key (no indented content followed) as
            # empty list per backward-compat default.
            if pending_key is not None:
                result[pending_key] = []
                pending_key = None
            colon = content.find(":")
            if colon == -1:
                raise ConfigYamlError(
                    "line {}: expected 'key:' or 'key: value' at top level".format(line_no)
                )
            key = content[:colon].strip()
            value_str = content[colon + 1:].strip()
            if value_str == "":
                pending_key = key
                current_list = None
                current_mapping = None
                current_item = None
                current_item_indent = None
            else:
                result[key] = _parse_value(value_str)
                current_list = None
                current_mapping = None
                current_item = None
                current_item_indent = None
            continue

        # Indented content: resolve container type on first indented line
        # under a pending_key, or continue existing container.
        if pending_key is not None:
            if content.startswith("- "):
                current_list = []
                result[pending_key] = current_list
            elif content.startswith("-"):
                raise ConfigYamlError(
                    "line {}: list-item dash must be followed by a space then 'key: value'".format(line_no)
                )
            else:
                current_mapping = {}
                result[pending_key] = current_mapping
            pending_key = None

        if current_mapping is not None:
            if content.startswith("-"):
                raise ConfigYamlError(
                    "line {}: dash-prefix inside nested mapping (mixing container types)".format(line_no)
                )
            colon = content.find(":")
            if colon == -1:
                raise ConfigYamlError(
                    "line {}: expected 'key: value' in nested mapping".format(line_no)
                )
            key = content[:colon].strip()
            value_str = content[colon + 1:].strip()
            current_mapping[key] = _parse_value(value_str)
            continue

        if current_list is None:
            raise ConfigYamlError(
                "line {}: indented content outside any list-of-mappings or nested-mapping key".format(line_no)
            )

        if content.startswith("- "):
            item_content = content[2:]
            # S047 dogfood Edit-2: accept block-list scalar items
            # (`- "x"`, `- bar`) alongside `- key: value`. Quoted item
            # OR no unquoted colon → scalar path via _parse_value.
            colon = _find_unquoted_colon(item_content)
            if item_content.startswith(('"', "'")) or colon == -1:
                current_list.append(_parse_value(item_content))
                current_item = None
                current_item_indent = None
            else:
                key = item_content[:colon].strip()
                value_str = item_content[colon + 1:].strip()
                current_item = {key: _parse_value(value_str)}
                current_list.append(current_item)
                current_item_indent = indent + 2
        elif content.startswith("-"):
            raise ConfigYamlError(
                "line {}: list-item dash must be followed by a space then 'key: value'".format(line_no)
            )
        else:
            if current_item is None:
                raise ConfigYamlError(
                    "line {}: continuation field outside any list item".format(line_no)
                )
            if indent != current_item_indent:
                raise ConfigYamlError(
                    "line {}: inconsistent indentation in list item "
                    "(expected {}, got {})".format(line_no, current_item_indent, indent)
                )
            colon = content.find(":")
            if colon == -1:
                raise ConfigYamlError(
                    "line {}: expected 'key: value' in continuation field".format(line_no)
                )
            key = content[:colon].strip()
            value_str = content[colon + 1:].strip()
            if value_str == "":
                # S002 FINDING #1: empty-value continuation field opens
                # a sub-list collection. Subsequent `- ` lines at greater
                # indent are appended as scalars to current_item[key].
                pending_subkey = key
                pending_subkey_indent = None
                current_item[key] = []
            else:
                current_item[key] = _parse_value(value_str)

    # Finalize trailing pending_key (no indented content followed) as
    # empty list per backward-compat default.
    if pending_key is not None:
        result[pending_key] = []

    return result
