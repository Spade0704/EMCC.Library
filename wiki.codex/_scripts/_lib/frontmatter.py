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


WIKI_ROOT = Path(__file__).resolve().parent.parent.parent


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


def _parse_value(s: str) -> Any:
    """Parse a YAML-subset scalar or flow-list value from string `s`."""
    if s == "" or s == "null":
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
              - field_a: value
        Each list item is a flat mapping. The first field's indentation
        sets the continuation indent for the rest of the item; mismatched
        continuation indents raise ConfigYamlError.
      - Nested mapping (2-level; S047-T-XL-3a):
            key:
              child_a: value
              child_b: value
        Indented `key: value` lines (no dash prefix) under a top-level
        empty-value key form a nested mapping. Container type (list vs
        mapping) determined by the first indented line's prefix.

    Out of scope: 3+ level nesting, flow-style mappings inside list
    items, multi-line strings, anchors, references, multi-document
    streams.

    Returns a dict (empty when input is empty or whitespace-only).
    Raises ConfigYamlError on structural malformation.
    """
    result = {}
    pending_key = None     # top-level key whose container type is unresolved
    current_list = None
    current_mapping = None
    current_item = None
    current_item_indent = None

    for idx, raw_line in enumerate(text.split("\n")):
        line_no = idx + 1
        no_comment = _strip_eol_comment(raw_line).rstrip()
        if not no_comment or no_comment.lstrip().startswith("#"):
            continue

        indent = len(no_comment) - len(no_comment.lstrip())
        content = no_comment[indent:]

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
            colon = item_content.find(":")
            if colon == -1:
                raise ConfigYamlError(
                    "line {}: list item must start with 'key: value'".format(line_no)
                )
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
            current_item[key] = _parse_value(value_str)

    # Finalize trailing pending_key (no indented content followed) as
    # empty list per backward-compat default.
    if pending_key is not None:
        result[pending_key] = []

    return result
