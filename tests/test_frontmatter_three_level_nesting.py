"""Tests for parse_config_yaml block-list-under-continuation (FINDING #1).

S002 / Codex v1.1 (2026-05-27): Mentor wiki report findings included
FINDING #1 — `_scripts/_lib/frontmatter.py::parse_config_yaml` crashes
on 3-level nesting reproducible with Mentor's topics.yaml template
form (block-style sub-list under a continuation field):

    topics:
      - name: example_topic
        keywords:
          - "example"
          - "examples"

Pre-fix: parser raised ConfigYamlError("inconsistent indentation in
list item") on the `- "example"` line because it didn't recognize
sub-list collection state.

Post-fix: parser tracks `pending_subkey` after every empty-value
continuation field; subsequent `- ` lines at greater indent get
collected as scalar items into current_item[pending_subkey].

These tests guard the fix + adjacent invariants (existing 2-level
parsing stays intact; mixed sub-list + scalar continuation works;
indent consistency enforced inside the sub-list).
"""

import unittest
from pathlib import Path

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

from _lib.frontmatter import parse_config_yaml, ConfigYamlError  # noqa: E402


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "yaml"


class TestMentorTopicsBlockSublist(unittest.TestCase):
    """FINDING #1 reproducer: Mentor topics.yaml block-style sub-list."""

    def test_mentor_topics_yaml_parses_clean(self):
        text = (FIXTURE_DIR / "mentor_topics.yaml").read_text(encoding="utf-8")
        result = parse_config_yaml(text)
        self.assertIn("topics", result)
        topics = result["topics"]
        self.assertEqual(len(topics), 3)

    def test_first_entry_keywords_collected_as_list(self):
        text = (FIXTURE_DIR / "mentor_topics.yaml").read_text(encoding="utf-8")
        result = parse_config_yaml(text)
        first = result["topics"][0]
        self.assertEqual(first["name"], "example_topic")
        self.assertEqual(first["keywords"], ["example", "examples"])

    def test_aliases_after_sub_list_parsed_correctly(self):
        text = (FIXTURE_DIR / "mentor_topics.yaml").read_text(encoding="utf-8")
        result = parse_config_yaml(text)
        first = result["topics"][0]
        # Flow-style aliases AFTER the block sub-list must still parse
        self.assertEqual(first["aliases"], ["exemplar", "illustration"])
        self.assertEqual(first["cross_manual"], False)
        self.assertEqual(first["min_similarity"], 0.35)

    def test_third_entry_flow_style_keywords_still_work(self):
        text = (FIXTURE_DIR / "mentor_topics.yaml").read_text(encoding="utf-8")
        result = parse_config_yaml(text)
        third = result["topics"][2]
        self.assertEqual(third["name"], "scalar_only")
        self.assertEqual(third["keywords"], ["inline", "flow-style"])


class TestBlockSublistEdgeCases(unittest.TestCase):
    """Edge cases for the FINDING #1 fix."""

    def test_inline_sublist_minimal(self):
        text = (
            "items:\n"
            "  - name: foo\n"
            "    tags:\n"
            "      - alpha\n"
            "      - beta\n"
        )
        result = parse_config_yaml(text)
        self.assertEqual(result["items"][0]["tags"], ["alpha", "beta"])

    def test_sublist_with_quoted_items(self):
        text = (
            "items:\n"
            "  - name: foo\n"
            "    tags:\n"
            "      - \"with: colon\"\n"
            "      - 'single quoted'\n"
        )
        result = parse_config_yaml(text)
        self.assertEqual(result["items"][0]["tags"], ["with: colon", "single quoted"])

    def test_inconsistent_sublist_indent_raises(self):
        text = (
            "items:\n"
            "  - name: foo\n"
            "    tags:\n"
            "      - alpha\n"
            "        - misindented\n"
        )
        # The "        - misindented" line has indent 8 (vs sub-list 6);
        # the parser raises on the unexpected indent.
        with self.assertRaises(ConfigYamlError):
            parse_config_yaml(text)

    def test_continuation_field_after_sublist_terminates_sublist(self):
        text = (
            "items:\n"
            "  - name: foo\n"
            "    tags:\n"
            "      - alpha\n"
            "      - beta\n"
            "    other_field: 42\n"
        )
        result = parse_config_yaml(text)
        item = result["items"][0]
        self.assertEqual(item["tags"], ["alpha", "beta"])
        self.assertEqual(item["other_field"], 42)

    def test_two_consecutive_items_with_sublists(self):
        text = (
            "items:\n"
            "  - name: first\n"
            "    tags:\n"
            "      - a1\n"
            "      - a2\n"
            "  - name: second\n"
            "    tags:\n"
            "      - b1\n"
        )
        result = parse_config_yaml(text)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0]["tags"], ["a1", "a2"])
        self.assertEqual(result["items"][1]["tags"], ["b1"])


class TestBackwardCompatibility(unittest.TestCase):
    """Pre-fix supported patterns must still parse identically."""

    def test_flow_style_list_in_continuation_field(self):
        text = (
            "items:\n"
            "  - name: foo\n"
            "    tags: [a, b, c]\n"
        )
        result = parse_config_yaml(text)
        self.assertEqual(result["items"][0]["tags"], ["a", "b", "c"])

    def test_2level_nested_mapping_still_works(self):
        text = (
            "config:\n"
            "  key_a: value_a\n"
            "  key_b: 42\n"
        )
        result = parse_config_yaml(text)
        self.assertEqual(result["config"], {"key_a": "value_a", "key_b": 42})

    def test_top_level_scalar_unchanged(self):
        text = "name: foo\nversion: 2\n"
        result = parse_config_yaml(text)
        self.assertEqual(result, {"name": "foo", "version": 2})


if __name__ == "__main__":
    unittest.main()
