"""Tests for _scripts/collect_open_questions.py — P4 aggregator."""

import shutil
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import collect_open_questions
from _lib import frontmatter


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


class CollectOpenQuestionsTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.wiki = Path(self._tmpdir.name) / "wiki"
        shutil.copytree(FIXTURE_ROOT, self.wiki)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _read_dashboard(self):
        return (self.wiki / "_dashboards" / "open_questions.md").read_text(
            encoding="utf-8"
        )

    def test_writes_dashboard_to_correct_path(self):
        collect_open_questions.run(self.wiki)
        self.assertTrue(
            (self.wiki / "_dashboards" / "open_questions.md").exists()
        )

    def test_run_returns_correct_summary(self):
        summary = collect_open_questions.run(self.wiki)
        self.assertEqual(summary["pages_with_questions"], 3)
        self.assertEqual(summary["total_questions"], 5)
        self.assertEqual(
            summary["dashboard_path"],
            self.wiki / "_dashboards" / "open_questions.md",
        )

    def test_dashboard_frontmatter(self):
        # Five fields exactly: title, type, visibility, generated, last_updated.
        # Matches SEMANTIC_LINT_PROCEDURE.md precedent for generated dashboards.
        collect_open_questions.run(self.wiki)
        content = self._read_dashboard()
        fm = frontmatter.parse_frontmatter(content)
        self.assertEqual(fm["title"], "Open Questions")
        self.assertEqual(fm["type"], "dashboard")
        self.assertEqual(fm["visibility"], "internal")
        self.assertIs(fm["generated"], True)
        self.assertEqual(fm["last_updated"], date.today().isoformat())
        self.assertEqual(
            set(fm.keys()),
            {"title", "type", "visibility", "generated", "last_updated"},
        )

    def test_summary_lines_present(self):
        # Note 1 — bold-label summary lines are the precedent for P5+ aggregators.
        collect_open_questions.run(self.wiki)
        content = self._read_dashboard()
        self.assertIn("**Pages with open questions:** 3", content)
        self.assertIn("**Total questions:** 5", content)

    def test_pages_sorted_alphabetically_by_path(self):
        # 01-Domain/Bar.md < 01-Domain/Foo.md < 02-Other/Baz.md
        collect_open_questions.run(self.wiki)
        content = self._read_dashboard()
        bar_pos = content.index("[[Bar]]")
        foo_pos = content.index("[[Foo]]")
        baz_pos = content.index("[[Baz]]")
        self.assertLess(bar_pos, foo_pos)
        self.assertLess(foo_pos, baz_pos)

    def test_page_without_blocking_questions_field_excluded(self):
        # Q4 case 1: Home.md has no blocking_questions field at all.
        collect_open_questions.run(self.wiki)
        content = self._read_dashboard()
        self.assertNotIn("[[Home]]", content)
        self.assertNotIn("[[Sample Wiki Home]]", content)

    def test_page_with_empty_blocking_questions_excluded(self):
        # Q4 case 2: Glossary.md has blocking_questions: [].
        collect_open_questions.run(self.wiki)
        content = self._read_dashboard()
        self.assertNotIn("[[Glossary]]", content)

    def test_paths_use_forward_slashes(self):
        # Per lessons.md style-note bullet 5: even on Windows, no backslash.
        collect_open_questions.run(self.wiki)
        content = self._read_dashboard()
        self.assertIn("(01-Domain/Foo.md)", content)
        self.assertIn("(01-Domain/Bar.md)", content)
        self.assertIn("(02-Other/Baz.md)", content)
        self.assertNotIn("\\", content)

    def test_wikilink_uses_filename_stem(self):
        # [[Foo]], not [[01-Domain/Foo]], not [[Foo Framework]] (the title).
        collect_open_questions.run(self.wiki)
        content = self._read_dashboard()
        self.assertIn("[[Foo]]", content)
        self.assertNotIn("[[01-Domain/Foo]]", content)
        self.assertNotIn("[[Foo Framework]]", content)
        self.assertNotIn("[[Baz Framework]]", content)

    def test_empty_wiki_writes_empty_dashboard(self):
        """Note 2 — reuse the canonical fixture; in the temp copy, replace each
        page's `blocking_questions: [...]` line with `blocking_questions: []`
        before calling run(). Same walking logic, same fixture, but every
        question is stripped — exercises the empty-case branch.
        """
        for rel in ("01-Domain/Foo.md", "01-Domain/Bar.md", "02-Other/Baz.md"):
            page = self.wiki / rel
            text = page.read_text(encoding="utf-8")
            new_lines = []
            for line in text.split("\n"):
                if line.startswith("blocking_questions:"):
                    new_lines.append("blocking_questions: []")
                else:
                    new_lines.append(line)
            page.write_text("\n".join(new_lines), encoding="utf-8")
        summary = collect_open_questions.run(self.wiki)
        self.assertEqual(summary["pages_with_questions"], 0)
        self.assertEqual(summary["total_questions"], 0)
        content = self._read_dashboard()
        self.assertIn("**Pages with open questions:** 0", content)
        self.assertIn("**Total questions:** 0", content)
        self.assertIn("No open questions found.", content)

    def test_dashboards_folder_created(self):
        # Note 3 — fresh wiki has no _dashboards/; run() creates it.
        dashboards_dir = self.wiki / "_dashboards"
        self.assertFalse(
            dashboards_dir.exists(),
            "fixture should not pre-create _dashboards/",
        )
        collect_open_questions.run(self.wiki)
        self.assertTrue(dashboards_dir.exists())
        self.assertTrue(dashboards_dir.is_dir())


if __name__ == "__main__":
    unittest.main()
