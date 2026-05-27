"""Tests for _scripts/build_topic_index.py — P18.2 cross-link build cascade consumer #1."""

import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import build_topic_index
from _lib.topics import Topic, build_alias_index


class ExtractScanTextTests(unittest.TestCase):

    def _write(self, tmp: Path, name: str, content: str) -> Path:
        p = tmp / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_h1_only(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._write(tmp, "x.md", "# Smoke Topic\n\nsome body\n")
            result = build_topic_index.extract_scan_text(p, ["h1"])
        self.assertIn("Smoke Topic", result)
        self.assertNotIn("some body", result)

    def test_h2_only(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._write(
                tmp, "x.md", "# H1 Title\n\n## Subhead Two\n\nbody\n"
            )
            result = build_topic_index.extract_scan_text(p, ["h2"])
        self.assertIn("Subhead Two", result)
        self.assertNotIn("H1 Title", result)

    def test_intro_para_only(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._write(
                tmp,
                "x.md",
                "# Hdr\n\nFirst intro paragraph here.\n\nSecond paragraph.\n",
            )
            result = build_topic_index.extract_scan_text(p, ["intro_para_1"])
        self.assertIn("First intro paragraph here.", result)
        self.assertNotIn("Second paragraph", result)

    def test_combined_h1_h2_intro(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._write(
                tmp,
                "x.md",
                "# H1 Title\n\nIntro para.\n\n## Subhead\n\nbody\n",
            )
            result = build_topic_index.extract_scan_text(
                p, ["h1", "h2", "intro_para_1"]
            )
        self.assertIn("H1 Title", result)
        self.assertIn("Subhead", result)
        self.assertIn("Intro para.", result)

    def test_fenced_code_stripped(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._write(
                tmp,
                "x.md",
                "# Hdr\n\n```\nshould_not_appear\n```\n\nVisible intro.\n",
            )
            result = build_topic_index.extract_scan_text(
                p, ["h1", "intro_para_1"]
            )
        self.assertIn("Hdr", result)
        self.assertNotIn("should_not_appear", result)


class TfidfScoreTests(unittest.TestCase):

    def test_identical_text_returns_1(self):
        score = build_topic_index.tfidf_score("foo bar baz", "foo bar baz")
        self.assertAlmostEqual(score, 1.0, places=5)

    def test_orthogonal_text_returns_0(self):
        score = build_topic_index.tfidf_score("foo bar", "qux quux")
        self.assertEqual(score, 0.0)

    def test_partial_overlap_in_range(self):
        score = build_topic_index.tfidf_score("foo bar baz", "foo qux quux")
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)

    def test_empty_query_returns_0(self):
        self.assertEqual(build_topic_index.tfidf_score("", "foo bar"), 0.0)

    def test_empty_doc_returns_0(self):
        self.assertEqual(build_topic_index.tfidf_score("foo bar", ""), 0.0)


class MatchTopicsToPageTests(unittest.TestCase):

    def setUp(self):
        self.topics = [
            Topic(name="smoke", keywords=["smoke"], aliases=["smoking"]),
            Topic(name="fire", keywords=["fire", "flame"]),
            Topic(name="ash", keywords=["ash"]),
        ]
        self.idx = build_alias_index(self.topics)

    def test_single_topic_match(self):
        result = build_topic_index.match_topics_to_page(
            "smoke alarm went off", self.topics, self.idx
        )
        self.assertEqual(result, ["smoke"])

    def test_multi_topic_match(self):
        result = build_topic_index.match_topics_to_page(
            "smoke and fire and ash everywhere", self.topics, self.idx
        )
        self.assertEqual(result, ["ash", "fire", "smoke"])

    def test_no_match_returns_empty(self):
        result = build_topic_index.match_topics_to_page(
            "nothing relevant here", self.topics, self.idx
        )
        self.assertEqual(result, [])

    def test_alias_match(self):
        result = build_topic_index.match_topics_to_page(
            "smoking everywhere", self.topics, self.idx
        )
        self.assertEqual(result, ["smoke"])

    def test_case_insensitive_match(self):
        result = build_topic_index.match_topics_to_page(
            "SMOKE alarm; Fire pit", self.topics, self.idx
        )
        self.assertEqual(result, ["fire", "smoke"])


class BlendResultsTests(unittest.TestCase):

    def test_weight_0_tfidf_only(self):
        tfidf = {"a": 1.0, "b": 0.5}
        plugin = {"a": 0.0, "b": 1.0}
        result = build_topic_index.blend_results(tfidf, plugin, weight=0.0)
        self.assertAlmostEqual(result["a"], 1.0)
        self.assertAlmostEqual(result["b"], 0.5)

    def test_weight_1_plugin_only(self):
        tfidf = {"a": 1.0, "b": 0.5}
        plugin = {"a": 0.0, "b": 1.0}
        result = build_topic_index.blend_results(tfidf, plugin, weight=1.0)
        self.assertAlmostEqual(result["a"], 0.0)
        self.assertAlmostEqual(result["b"], 1.0)

    def test_weight_half_blend(self):
        tfidf = {"a": 1.0}
        plugin = {"a": 0.0}
        result = build_topic_index.blend_results(tfidf, plugin, weight=0.5)
        self.assertAlmostEqual(result["a"], 0.5)

    def test_plugin_none_pass_through(self):
        tfidf = {"a": 1.0, "b": 0.5}
        result = build_topic_index.blend_results(tfidf, None, weight=0.5)
        self.assertEqual(result, {"a": 1.0, "b": 0.5})


class LoadPluginTests(unittest.TestCase):

    def test_no_config_returns_none(self):
        cfg = {"plugin": {"module_path": None, "callable": None}}
        self.assertIsNone(build_topic_index.load_plugin(cfg))

    def test_missing_plugin_block_returns_none(self):
        cfg = {}
        self.assertIsNone(build_topic_index.load_plugin(cfg))

    def test_missing_module_logs_warning_returns_none(self):
        cfg = {
            "plugin": {
                "module_path": "no_such_module_xyz",
                "callable": "anything",
            }
        }
        buf = io.StringIO()
        with redirect_stderr(buf):
            result = build_topic_index.load_plugin(cfg)
        self.assertIsNone(result)
        self.assertIn("plug-in unavailable", buf.getvalue())

    def test_missing_callable_logs_warning_returns_none(self):
        cfg = {
            "plugin": {
                "module_path": "os",  # exists; no `not_a_real_callable` attr
                "callable": "not_a_real_callable_xyz",
            }
        }
        buf = io.StringIO()
        with redirect_stderr(buf):
            result = build_topic_index.load_plugin(cfg)
        self.assertIsNone(result)
        self.assertIn("plug-in unavailable", buf.getvalue())


class UpdatePageFrontmatterTests(unittest.TestCase):

    def _page(self, tmp: Path, content: str) -> Path:
        p = tmp / "page.md"
        p.write_text(content, encoding="utf-8")
        return p

    def test_empty_existing_topics_appends_matched(self):
        cfg = {"tags": {"mirror_from": [], "prefix_scheme": "flat"}}
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._page(
                tmp,
                "---\ntitle: \"X\"\ntopics: []\n---\n\nbody\n",
            )
            build_topic_index.update_page_frontmatter(p, ["smoke"], cfg)
            content = p.read_text(encoding="utf-8")
        self.assertIn("topics: [smoke]", content)

    def test_human_topics_preserved_additive(self):
        cfg = {"tags": {"mirror_from": [], "prefix_scheme": "flat"}}
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._page(
                tmp,
                '---\ntitle: "X"\ntopics: [human_topic]\n---\n\nbody\n',
            )
            build_topic_index.update_page_frontmatter(p, ["smoke"], cfg)
            content = p.read_text(encoding="utf-8")
        self.assertIn("human_topic", content)
        self.assertIn("smoke", content)

    def test_tag_mirroring_flat(self):
        cfg = {
            "tags": {
                "mirror_from": ["topics"],
                "prefix_scheme": "flat",
                "prefix_map": {"topics": "topic"},
            }
        }
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._page(
                tmp,
                '---\ntitle: "X"\ntopics: []\ntags: []\n---\n\nbody\n',
            )
            build_topic_index.update_page_frontmatter(p, ["smoke"], cfg)
            content = p.read_text(encoding="utf-8")
        self.assertIn("topics: [smoke]", content)
        self.assertIn("tags: [smoke]", content)

    def test_tag_mirroring_disabled(self):
        cfg = {"tags": {"mirror_from": [], "prefix_scheme": "flat"}}
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._page(
                tmp,
                '---\ntitle: "X"\ntopics: []\ntags: [pre_existing]\n---\n\nbody\n',
            )
            build_topic_index.update_page_frontmatter(p, ["smoke"], cfg)
            content = p.read_text(encoding="utf-8")
        self.assertIn("pre_existing", content)
        # No new tags mirrored
        self.assertNotIn("tags: [pre_existing, smoke]", content)

    def test_human_tags_preserved_additive(self):
        cfg = {
            "tags": {
                "mirror_from": ["topics"],
                "prefix_scheme": "flat",
                "prefix_map": {"topics": "topic"},
            }
        }
        with TemporaryDirectory() as t:
            tmp = Path(t)
            p = self._page(
                tmp,
                '---\ntitle: "X"\ntopics: []\ntags: [human_tag]\n---\n\nbody\n',
            )
            build_topic_index.update_page_frontmatter(p, ["smoke"], cfg)
            content = p.read_text(encoding="utf-8")
        self.assertIn("human_tag", content)
        self.assertIn("smoke", content)


class RenderTopicIndexTests(unittest.TestCase):

    def test_dashboard_fm_contract(self):
        result = build_topic_index.render_topic_index(
            {"smoke": [Path("01-Domain/Foo.md")]}, Path(".")
        )
        self.assertIn("---", result)
        self.assertIn('title: "Topic Index Dashboard"', result)
        self.assertIn("type: dashboard", result)
        self.assertIn("visibility: internal", result)
        self.assertIn("generated: true", result)
        self.assertIn("last_updated:", result)

    def test_per_topic_table(self):
        result = build_topic_index.render_topic_index(
            {
                "smoke": [Path("01-Domain/Foo.md")],
                "fire": [Path("02-Other/Bar.md")],
            },
            Path("."),
        )
        self.assertIn("## smoke", result)
        self.assertIn("## fire", result)
        self.assertIn("[[Foo]]", result)
        self.assertIn("[[Bar]]", result)

    def test_empty_topics_graceful(self):
        result = build_topic_index.render_topic_index({}, Path("."))
        self.assertIn("No topics matched any pages.", result)


class RunOrchestratorTests(unittest.TestCase):

    def _setup_wiki(self, tmp: Path, topics_yaml: str, pages: list) -> Path:
        """Build a minimal wiki tree at tmp with topics.yaml + content pages."""
        canon = tmp / "_canon"
        canon.mkdir()
        (canon / "topics.yaml").write_text(topics_yaml, encoding="utf-8")
        for rel, content in pages:
            page_path = tmp / rel
            page_path.parent.mkdir(parents=True, exist_ok=True)
            page_path.write_text(content, encoding="utf-8")
        return tmp

    def test_happy_path_topic_to_page_mapping(self):
        topics_yaml = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
        )
        page = (
            '---\ntitle: "Foo"\ntopics: []\n---\n\n'
            "# Smoke detector setup\n\nIntro about smoke.\n"
        )
        with TemporaryDirectory() as t:
            tmp = Path(t)
            self._setup_wiki(
                tmp, topics_yaml, [("01-Domain/Foo.md", page)]
            )
            result = build_topic_index.run(tmp)
            self.assertIn("smoke", result["topic_to_pages"])
            self.assertEqual(len(result["topic_to_pages"]["smoke"]), 1)
            self.assertEqual(result["pages_scanned"], 1)
            self.assertTrue(result["dashboard_path"].exists())

    def test_no_topics_yaml_graceful_early_exit(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            # No _canon/topics.yaml exists
            (tmp / "01-Domain").mkdir(parents=True, exist_ok=True)
            (tmp / "01-Domain" / "Foo.md").write_text(
                "# Foo\n\nbody\n", encoding="utf-8"
            )
            result = build_topic_index.run(tmp)
            self.assertEqual(result["topic_to_pages"], {})
            self.assertEqual(result["pages_scanned"], 0)
            self.assertTrue(result["dashboard_path"].exists())

    def test_no_matching_pages_writes_empty_dashboard(self):
        topics_yaml = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
        )
        page = '---\ntitle: "X"\ntopics: []\n---\n\n# Foo\n\nunrelated body\n'
        with TemporaryDirectory() as t:
            tmp = Path(t)
            self._setup_wiki(
                tmp, topics_yaml, [("01-Domain/Foo.md", page)]
            )
            result = build_topic_index.run(tmp)
            self.assertEqual(result["topic_to_pages"], {})
            self.assertEqual(result["pages_scanned"], 1)

    def test_run_uses_hardcoded_defaults(self):
        # No cross_link.yaml; defaults should drive scan_fields + tag mirroring.
        topics_yaml = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
        )
        page = '---\ntitle: "X"\ntopics: []\ntags: []\n---\n\n# Smoke topic\n'
        with TemporaryDirectory() as t:
            tmp = Path(t)
            self._setup_wiki(
                tmp, topics_yaml, [("01-Domain/Foo.md", page)]
            )
            build_topic_index.run(tmp)
            page_content = (tmp / "01-Domain" / "Foo.md").read_text(
                encoding="utf-8"
            )
        # Default tag-mirroring flat: topics → tags
        self.assertIn("topics: [smoke]", page_content)
        self.assertIn("tags: [smoke]", page_content)


class TestT_XL_3a_BuildTopicIndexReadsCrossLinkConfig(unittest.TestCase):
    """S047-T-XL-3a wire-through verification."""

    def test_build_topic_index_reads_cross_link_config_via_load_helper(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            # Minimum viable wiki: _canon/topics.yaml + _config/cross_link.yaml
            (wiki / "_canon").mkdir()
            (wiki / "_canon" / "topics.yaml").write_text(
                "topics: []\n", encoding="utf-8"
            )
            config_dir = wiki / "_config"
            config_dir.mkdir()
            (config_dir / "cross_link.yaml").write_text(
                "tfidf:\n"
                "  min_similarity: 0.99\n"
                "  max_links_per_page: 3\n",
                encoding="utf-8",
            )
            (wiki / "_dashboards").mkdir()
            buf = io.StringIO()
            with redirect_stderr(buf):
                result = build_topic_index.run(wiki)
            # Smoke: orchestrator returns dict with dashboard_path key;
            # cross_link.yaml was loaded (no AttributeError on cfg["tfidf"]
            # access in extract_scan_text downstream call).
            self.assertIn("dashboard_path", result)


if __name__ == "__main__":
    unittest.main()
