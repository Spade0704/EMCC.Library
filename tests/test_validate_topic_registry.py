"""Tests for _scripts/validate_topic_registry.py — P18.4 cross-link build cascade consumer #3.

MANDATORY discipline per Architect arbitration `fixture_scope_discipline_pre_emit_mandatory`:
ALL read_text() / Path operations against TemporaryDirectory-managed paths
MUST occur INSIDE `with` block scope per 2-exhibit banking-watch threshold
prevention (T-XL-3 + T-XL-4 prior exhibits; 3rd-exhibit triggers S035
codification).
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import validate_topic_registry
from _lib.topics import Topic, build_alias_index
from validate_topic_registry import (
    SEVERITY_ERROR,
    SEVERITY_WARNING,
    build_topic_to_pages_index,
    check_orphan_topics,
    check_page_topics_resolve,
    render_validation_report,
)


def _write_page(
    wiki_root: Path, rel: str, topics_list, body: str = "body"
) -> Path:
    """Helper: write content page under wiki_root with given topics."""
    path = wiki_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if topics_list is None:
        fm = '---\ntitle: "X"\n---\n'
    else:
        topics_str = "[" + ", ".join(topics_list) + "]"
        fm = '---\ntitle: "X"\ntopics: {}\n---\n'.format(topics_str)
    path.write_text(fm + "\n" + body + "\n", encoding="utf-8")
    return path


def _write_topics_yaml(wiki_root: Path, topics_yaml: str) -> Path:
    """Helper: write _canon/topics.yaml fixture."""
    canon = wiki_root / "_canon"
    canon.mkdir(exist_ok=True)
    path = canon / "topics.yaml"
    path.write_text(topics_yaml, encoding="utf-8")
    return path


class CheckPageTopicsResolveTests(unittest.TestCase):

    def setUp(self):
        self.topics = [
            Topic(name="smoke", keywords=["smoke"], aliases=["smoking"]),
            Topic(name="fire", keywords=["fire"]),
        ]
        self.idx = build_alias_index(self.topics)

    def test_all_resolve_no_findings(self):
        findings = check_page_topics_resolve(
            Path("A.md"), ["smoke", "fire"], self.idx
        )
        self.assertEqual(findings, [])

    def test_one_unresolved_error(self):
        findings = check_page_topics_resolve(
            Path("A.md"), ["smoke", "unknown_topic"], self.idx
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["severity"], SEVERITY_ERROR)
        self.assertEqual(findings[0]["topic"], "unknown_topic")

    def test_two_unresolved_two_errors(self):
        findings = check_page_topics_resolve(
            Path("A.md"), ["bogus_a", "bogus_b"], self.idx
        )
        self.assertEqual(len(findings), 2)
        for f in findings:
            self.assertEqual(f["severity"], SEVERITY_ERROR)

    def test_alias_resolves_no_finding(self):
        # 'smoking' is alias of canonical 'smoke'
        findings = check_page_topics_resolve(
            Path("A.md"), ["smoking"], self.idx
        )
        self.assertEqual(findings, [])


class CheckOrphanTopicsTests(unittest.TestCase):

    def setUp(self):
        self.topics = [
            Topic(name="smoke", keywords=["smoke"]),
            Topic(name="fire", keywords=["fire"]),
        ]

    def test_all_topics_have_members_no_findings(self):
        idx = {"smoke": [Path("A.md")], "fire": [Path("B.md")]}
        findings = check_orphan_topics(self.topics, idx)
        self.assertEqual(findings, [])

    def test_one_orphan_warning(self):
        idx = {"smoke": [Path("A.md")]}
        findings = check_orphan_topics(self.topics, idx)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["severity"], SEVERITY_WARNING)
        self.assertEqual(findings[0]["topic"], "fire")

    def test_two_orphans_two_warnings(self):
        idx: dict = {}
        findings = check_orphan_topics(self.topics, idx)
        self.assertEqual(len(findings), 2)
        for f in findings:
            self.assertEqual(f["severity"], SEVERITY_WARNING)


class BuildTopicToPagesIndexTests(unittest.TestCase):

    def test_empty_wiki(self):
        with TemporaryDirectory() as t:
            result = build_topic_to_pages_index(Path(t))
            self.assertEqual(result, {})

    def test_pages_with_topics_grouped(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            _write_page(wiki, "01-Domain/B.md", ["smoke", "fire"])
            result = build_topic_to_pages_index(wiki)
            self.assertEqual(len(result["smoke"]), 2)
            self.assertEqual(len(result["fire"]), 1)

    def test_pages_without_topics_skipped(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            _write_page(wiki, "01-Domain/B.md", None)
            result = build_topic_to_pages_index(wiki)
            self.assertEqual(len(result["smoke"]), 1)


class RenderValidationReportTests(unittest.TestCase):

    def test_no_findings_graceful(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            result = render_validation_report([], wiki)
            self.assertIn("All topic-registry checks passed.", result)
            # Dashboard fm contract
            self.assertIn('title: "Topic Registry Validation Dashboard"', result)
            self.assertIn("type: dashboard", result)
            self.assertIn("visibility: internal", result)
            self.assertIn("generated: true", result)

    def test_errors_only_grouped(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            findings = [
                {
                    "page_path": wiki / "01-Domain/A.md",
                    "topic": "bogus",
                    "severity": SEVERITY_ERROR,
                    "message": "test error",
                },
            ]
            result = render_validation_report(findings, wiki)
            self.assertIn("## Errors", result)
            self.assertNotIn("## Warnings", result)
            self.assertIn("'bogus'", result)

    def test_errors_plus_warnings_grouped(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            findings = [
                {
                    "page_path": wiki / "01-Domain/A.md",
                    "topic": "bogus",
                    "severity": SEVERITY_ERROR,
                    "message": "test error",
                },
                {
                    "topic": "orphan_t",
                    "severity": SEVERITY_WARNING,
                    "message": "orphan",
                },
            ]
            result = render_validation_report(findings, wiki)
            self.assertIn("## Errors", result)
            self.assertIn("## Warnings", result)
            self.assertIn("'bogus'", result)
            self.assertIn("'orphan_t'", result)


class RunOrchestratorTests(unittest.TestCase):

    def test_happy_path_clean_no_findings(self):
        topics_yaml = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
        )
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_topics_yaml(wiki, topics_yaml)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            summary = validate_topic_registry.run(wiki)
            self.assertEqual(summary["errors_count"], 0)
            self.assertEqual(summary["warnings_count"], 0)
            self.assertEqual(summary["registry_topics"], 1)
            self.assertEqual(summary["pages_seen"], 1)
            self.assertTrue(summary["dashboard_path"].exists())

    def test_unresolved_page_topic_error(self):
        topics_yaml = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
        )
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_topics_yaml(wiki, topics_yaml)
            _write_page(wiki, "01-Domain/A.md", ["smoke", "bogus_topic"])
            summary = validate_topic_registry.run(wiki)
            self.assertEqual(summary["errors_count"], 1)

    def test_orphan_topic_warning(self):
        topics_yaml = (
            "topics:\n"
            "  - name: smoke\n"
            '    keywords: ["smoke"]\n'
            "  - name: orphan_topic\n"
            '    keywords: ["orphan_topic"]\n'
        )
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_topics_yaml(wiki, topics_yaml)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            summary = validate_topic_registry.run(wiki)
            self.assertEqual(summary["warnings_count"], 1)
            self.assertEqual(summary["registry_topics"], 2)

    def test_topics_yaml_absent_graceful(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            summary = validate_topic_registry.run(wiki)
            self.assertEqual(summary["registry_topics"], 0)
            self.assertEqual(summary["errors_count"], 0)
            self.assertEqual(summary["warnings_count"], 0)
            self.assertTrue(summary["dashboard_path"].exists())


if __name__ == "__main__":
    unittest.main()
