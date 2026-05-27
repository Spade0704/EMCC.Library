"""YAML-subset parser and frontmatter loader for Codex.

Foundation module — every Codex script imports this. Pure stdlib.
Handles the YAML subset that spec §2.3 frontmatter uses: flat mapping
with scalar values (string, int, bool, null) and flow-style lists.
Comments (#) and quoted strings supported.

Out of scope (per tasks/lessons.md 2026-05-01 — Codex script conventions):
block-style lists, nested mappings, multi-line strings, YAML anchors,
multi-document streams, datetime parsing, capitalised booleans, ~ as null.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def find_wiki_root():
    """Walk up from this file looking for a marker that identifies the WIKI_ROOT.

    Three resolution cases (checked in priority order):

    1. **Ancestor IS a wiki** — `Home.md` present at an ancestor dir. This is
       the v1.0-shape bootstrapped wiki layout: `<wiki>/_scripts/_lib/frontmatter.py`,
       walk up, find `<wiki>/Home.md`. Used by Mentor + any v1.0-shape consumer.

    2. **Ancestor is a v1.1 install/consumer** — has `CLAUDE.md` AND a
       `wiki.<name>/git/Home.md` subpath. This is Codex v1.1's canonical
       layout where `_scripts/` lives at `Biz.Automation/wikisys.<name>/_scripts/`
       and the wiki content is at `<root>/wiki.<name>/git/`. Used by Library's
       dogfood wiki (`wiki.codex/git/`) and future v1.1 consumer projects
       (`wiki.aviation/git/`, etc.).

    3. **Ancestor is a Library install without dogfood wiki** — has `CLAUDE.md`
       AND `module.json` co-existing but no `wiki.<name>/git/Home.md`. Fallback
       to return the install root itself; this is rare (Library always has a
       dogfood wiki) but kept for resilience.

    Resolves MI-17: pre-fix, all 17 scripts in `_scripts/` used
    `WIKI_ROOT = Path(__file__).resolve().parent.parent` which only worked for
    case 1; post-S002 restructure put Library scripts at 4 levels deep instead
    of 2, breaking dashboard generation against Library's own dogfood wiki.

    Note on `__file__` semantics: this function's `Path(__file__)` always
    resolves to `_lib/frontmatter.py`'s location regardless of which script
    imports + calls it. That's fine — the marker-walk reaches the right
    ancestor regardless of starting point, just takes one extra hop up from
    scripts at `_scripts/<script>.py` vs `_scripts/_lib/<module>.py`.
    """
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        # Case 1: ancestor IS a wiki (v1.0-shape consumer)
        if (ancestor / "Home.md").exists():
            return ancestor
        # Case 2: ancestor is a v1.1 install/consumer with a wiki.<name>/git/ content side
        if (ancestor / "CLAUDE.md").exists():
            for wiki_content in ancestor.glob("wiki.*/git"):
                if (wiki_content / "Home.md").exists():
                    return wiki_content
            # Case 3: Library install fallback (CLAUDE.md + module.json, no dogfood wiki)
            if (ancestor / "module.json").exists():
                return ancestor
    raise RuntimeError(
        "WIKI_ROOT cannot be resolved — no marker found in any ancestor of "
        f"{here}. Expected one of: Home.md (v1.0-shape wiki), "
        "CLAUDE.md + wiki.<name>/git/Home.md (v1.1 install/consumer), or "
        "CLAUDE.md + module.json (Library install without dogfood wiki)."
    )


# Back-compat alias — keep `_find_wiki_root` for any callers that imported the
# private name from the PR #4 era. Public `find_wiki_root` is the canonical
# name post-MI-17 fix (used by all 17 scripts).
_find_wiki_root = find_wiki_root


WIKI_ROOT = find_wiki_root()


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
    """Parse the YAML subset Codex frontmatter uses. Returns a dict."""
    result = {}
    for raw_line in text.split("\n"):
        line = _strip_eol_comment(raw_line).rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        colon = line.find(":")
        if colon == -1:
            continue
        key = line[:colon].strip()
        value_str = line[colon + 1:].strip()
        result[key] = _parse_value(value_str)
    return result


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
