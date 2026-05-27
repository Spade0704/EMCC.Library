"""Tests for _scripts/_lib/topics.py — P18.1 foundation."""

import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory

from _lib import topics
from _lib.topics import (
    Topic,
    build_alias_index,
    load_topics,
    parse_topics,
    resolve_topic,
)


class TopicDataclassTests(unittest.TestCase):

    def test_topic_full_construction(self):
        t = Topic(
            name="smoke",
            keywords=["smoke", "smokes"],
            aliases=["smoking"],
            cross_manual=True,
            min_similarity=0.35,
        )
        self.assertEqual(t.name, "smoke")
        self.assertEqual(t.keywords, ["smoke", "smokes"])
        self.assertEqual(t.aliases, ["smoking"])
        self.assertTrue(t.cross_manual)
        self.assertEqual(t.min_similarity, 0.35)

    def test_topic_defaults(self):
        t = Topic(name="minimal", keywords=["a"])
        self.assertEqual(t.aliases, [])
        self.assertFalse(t.cross_manual)
        self.assertIsNone(t.min_similarity)

    def test_topic_immutable_frozen(self):
        t = Topic(name="x", keywords=["k"])
        with self.assertRaises(FrozenInstanceError):
            t.name = "y"


class ParseTopicsValidTests(unittest.TestCase):

    def test_single_topic(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
        )
        result = parse_topics(text)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "smoke")
        self.assertEqual(result[0].keywords, ["smoke"])

    def test_multi_topic(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
            "  - name: fire\n"
            '    keywords: ["fire", "flame"]\n'
        )
        result = parse_topics(text)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "smoke")
        self.assertEqual(result[1].name, "fire")
        self.assertEqual(result[1].keywords, ["fire", "flame"])

    def test_minimal_required_only(self):
        text = (
            "topics:\n"
            "  - name: minimal\n"
            '    keywords: ["x"]\n'
        )
        result = parse_topics(text)
        self.assertEqual(result[0].name, "minimal")
        self.assertEqual(result[0].aliases, [])
        self.assertFalse(result[0].cross_manual)
        self.assertIsNone(result[0].min_similarity)

    def test_full_optional(self):
        text = (
            "topics:\n"
            "  - name: full_topic\n"
            '    keywords: ["fx", "fy"]\n'
            '    aliases: ["fulla", "fullb"]\n'
            "    cross_manual: true\n"
            "    min_similarity: 0.35\n"
        )
        result = parse_topics(text)
        t = result[0]
        self.assertEqual(t.aliases, ["fulla", "fullb"])
        self.assertTrue(t.cross_manual)
        self.assertEqual(t.min_similarity, 0.35)

    def test_empty_topics_list(self):
        text = "topics:\n"
        result = parse_topics(text)
        self.assertEqual(result, [])


class ParseTopicsMalformedTests(unittest.TestCase):

    def test_missing_required_name(self):
        text = (
            "topics:\n"
            '  - keywords: ["x"]\n'
        )
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        self.assertIn("missing required key 'name'", str(cm.exception))

    def test_missing_required_keywords(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
        )
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        self.assertIn("missing required key 'keywords'", str(cm.exception))

    def test_unknown_key(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["x"]\n'
            '    badkey: "value"\n'
        )
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        msg = str(cm.exception)
        self.assertIn("unknown keys", msg)
        self.assertIn("badkey", msg)

    def test_wrong_type_name_not_str(self):
        text = (
            "topics:\n"
            "  - name: 42\n"
            '    keywords: ["x"]\n'
        )
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        self.assertIn("'name' must be str", str(cm.exception))

    def test_wrong_type_keywords_not_list(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: "scalar"\n'
        )
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        self.assertIn("'keywords' must be List[str]", str(cm.exception))

    def test_wrong_type_aliases_not_list(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["x"]\n'
            '    aliases: "single"\n'
        )
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        self.assertIn("'aliases' must be List[str]", str(cm.exception))

    def test_wrong_type_cross_manual_not_bool(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["x"]\n'
            "    cross_manual: 42\n"
        )
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        self.assertIn("'cross_manual' must be bool", str(cm.exception))

    def test_wrong_type_min_similarity_not_float(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["x"]\n'
            '    min_similarity: "high"\n'
        )
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        self.assertIn(
            "'min_similarity' must be float or None", str(cm.exception)
        )

    def test_top_level_topics_not_list(self):
        text = 'topics: "not a list"\n'
        with self.assertRaises(ValueError) as cm:
            parse_topics(text)
        self.assertIn(
            "top-level 'topics' must be a list", str(cm.exception)
        )

    def test_entry_not_mapping(self):
        # parse_config_yaml enforces `- key: value` shape; entry-not-mapping
        # path is defensive-only. Test via direct private call to cover the
        # guard in _validate_topic_entry.
        from _lib.topics import _validate_topic_entry
        with self.assertRaises(ValueError) as cm:
            _validate_topic_entry("not a dict", 1)
        self.assertIn("entry must be a mapping", str(cm.exception))


class LoadTopicsTests(unittest.TestCase):

    def test_load_topics_reads_file(self):
        text = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "topics.yaml"
            path.write_text(text, encoding="utf-8")
            result = load_topics(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "smoke")


class BuildAliasIndexTests(unittest.TestCase):

    def test_canonical_keys_in_index(self):
        topics_list = [Topic(name="smoke", keywords=["x"])]
        idx = build_alias_index(topics_list)
        self.assertIn("smoke", idx)
        self.assertIs(idx["smoke"], topics_list[0])

    def test_alias_keys_in_index(self):
        topics_list = [
            Topic(name="smoke", keywords=["x"], aliases=["smoking"])
        ]
        idx = build_alias_index(topics_list)
        self.assertIn("smoking", idx)
        self.assertIs(idx["smoking"], topics_list[0])

    def test_case_insensitive_keys(self):
        topics_list = [
            Topic(name="Smoke", keywords=["x"], aliases=["Smoking"])
        ]
        idx = build_alias_index(topics_list)
        self.assertIn("smoke", idx)
        self.assertIn("smoking", idx)

    def test_alias_canonical_collision_raises(self):
        topics_list = [
            Topic(name="smoke", keywords=["x"]),
            Topic(name="other", keywords=["y"], aliases=["smoke"]),
        ]
        with self.assertRaises(ValueError) as cm:
            build_alias_index(topics_list)
        self.assertIn("collision", str(cm.exception))

    def test_empty_topics(self):
        self.assertEqual(build_alias_index([]), {})

    def test_case_preserved_in_topic_fields(self):
        topics_list = [
            Topic(name="SmokeX", keywords=["x"], aliases=["AltSmoke"])
        ]
        idx = build_alias_index(topics_list)
        # Lookup keys are case-folded
        self.assertIn("smokex", idx)
        self.assertIn("altsmoke", idx)
        # Topic record fields preserve original case
        t = idx["smokex"]
        self.assertEqual(t.name, "SmokeX")
        self.assertEqual(t.aliases, ["AltSmoke"])


class ResolveTopicTests(unittest.TestCase):

    def setUp(self):
        self.topics_list = [
            Topic(name="Smoke", keywords=["x"], aliases=["Smoking"])
        ]
        self.idx = build_alias_index(self.topics_list)

    def test_resolve_lower_case(self):
        result = resolve_topic("smoke", self.idx)
        self.assertIs(result, self.topics_list[0])

    def test_resolve_upper_case(self):
        result = resolve_topic("SMOKE", self.idx)
        self.assertIs(result, self.topics_list[0])

    def test_resolve_mixed_case(self):
        result = resolve_topic("Smoke", self.idx)
        self.assertIs(result, self.topics_list[0])

    def test_resolve_alias(self):
        result = resolve_topic("smoking", self.idx)
        self.assertIs(result, self.topics_list[0])

    def test_resolve_unknown_returns_none(self):
        result = resolve_topic("unknown", self.idx)
        self.assertIsNone(result)


class AggregatorUsageTests(unittest.TestCase):

    def test_full_workflow_load_index_resolve(self):
        text = (
            "topics:\n"
            "  - name: Smoke\n"
            '    keywords: ["smoke"]\n'
            '    aliases: ["smoking"]\n'
            "  - name: Fire\n"
            '    keywords: ["fire"]\n'
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "topics.yaml"
            path.write_text(text, encoding="utf-8")
            topics_list = load_topics(path)
            idx = build_alias_index(topics_list)
        self.assertEqual(len(topics_list), 2)
        smoke = resolve_topic("SMOKING", idx)
        self.assertIsNotNone(smoke)
        self.assertEqual(smoke.name, "Smoke")
        fire = resolve_topic("fire", idx)
        self.assertIsNotNone(fire)
        self.assertEqual(fire.name, "Fire")


if __name__ == "__main__":
    unittest.main()
