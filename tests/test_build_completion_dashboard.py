"""Tests for _scripts/build_completion_dashboard.py — P5 aggregator."""

import shutil
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import build_completion_dashboard
from _lib import frontmatter


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


class BuildCompletionDashboardTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.wiki = Path(self._tmpdir.name) / "wiki"
        shutil.copytree(FIXTURE_ROOT, self.wiki)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _read_dashboard(self):
        return (self.wiki / "_dashboards" / "completion.md").read_text(
            encoding="utf-8"
        )

    def _set_completion(self, rel_path, value):
        page = self.wiki / rel_path
        text = page.read_text(encoding="utf-8")
        new_lines = []
        for line in text.split("\n"):
            if line.startswith("completion:"):
                new_lines.append("completion: " + str(value))
            else:
                new_lines.append(line)
        page.write_text("\n".join(new_lines), encoding="utf-8")

    def _strip_completion(self, rel_path):
        page = self.wiki / rel_path
        text = page.read_text(encoding="utf-8")
        new_lines = [
            line for line in text.split("\n")
            if not line.startswith("completion:")
        ]
        page.write_text("\n".join(new_lines), encoding="utf-8")

    def _band_for_page(self, content, page_stem):
        """Return the band name whose section contains [[page_stem]], or None."""
        sections = {}
        current = None
        for line in content.split("\n"):
            if line.startswith("## "):
                current = line[3:].strip()
                sections[current] = []
            elif current is not None:
                sections[current].append(line)
        needle = "[[" + page_stem + "]]"
        for band, body in sections.items():
            if any(needle in line for line in body):
                return band
        return None

    def test_writes_dashboard_to_correct_path(self):
        build_completion_dashboard.run(self.wiki)
        self.assertTrue(
            (self.wiki / "_dashboards" / "completion.md").exists()
        )

    def test_run_returns_correct_summary(self):
        # Fixture: Home 50, Glossary 30, Foo 60, Bar 40, Baz 70 → avg 50.
        summary = build_completion_dashboard.run(self.wiki)
        self.assertEqual(summary["pages_tracked"], 5)
        self.assertEqual(summary["average_completion"], 50)
        self.assertEqual(
            summary["dashboard_path"],
            self.wiki / "_dashboards" / "completion.md",
        )

    def test_dashboard_frontmatter(self):
        # Five fields exactly: title, type, visibility, generated, last_updated.
        # Matches SEMANTIC_LINT_PROCEDURE.md precedent for generated dashboards.
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        fm = frontmatter.parse_frontmatter(content)
        self.assertEqual(fm["title"], "Completion Dashboard")
        self.assertEqual(fm["type"], "dashboard")
        self.assertEqual(fm["visibility"], "internal")
        self.assertIs(fm["generated"], True)
        self.assertEqual(fm["last_updated"], date.today().isoformat())
        self.assertEqual(
            set(fm.keys()),
            {"title", "type", "visibility", "generated", "last_updated"},
        )

    def test_summary_lines_present(self):
        # Bold-label summary lines — P5's Q4 wording.
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        self.assertIn("**Pages with completion data:** 5", content)
        self.assertIn("**Average completion:** 50%", content)

    def test_pages_grouped_by_band_unmutated_fixture(self):
        # Bands: ready ≥ 80, solid 55–79, outlined 30–54, gap < 30.
        # Solid: Foo (60), Baz (70). Outlined: Glossary (30), Home (50), Bar (40).
        # Empty bands (ready, gap) must NOT render headers.
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        self.assertEqual(self._band_for_page(content, "Foo"), "solid")
        self.assertEqual(self._band_for_page(content, "Baz"), "solid")
        self.assertEqual(self._band_for_page(content, "Glossary"), "outlined")
        self.assertEqual(self._band_for_page(content, "Home"), "outlined")
        self.assertEqual(self._band_for_page(content, "Bar"), "outlined")
        self.assertNotIn("## ready", content)
        self.assertNotIn("## gap", content)

    def test_band_section_order_ready_solid_outlined_gap(self):
        # Move Home → ready (90) and Bar → gap (10) so all four bands render.
        # Verify the section headers appear in fixed order.
        self._set_completion("Home.md", 90)
        self._set_completion("01-Domain/Bar.md", 10)
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        ready_pos = content.index("## ready")
        solid_pos = content.index("## solid")
        outlined_pos = content.index("## outlined")
        gap_pos = content.index("## gap")
        self.assertLess(ready_pos, solid_pos)
        self.assertLess(solid_pos, outlined_pos)
        self.assertLess(outlined_pos, gap_pos)

    def test_pages_sorted_alphabetically_within_band(self):
        # Sort key: relative_to(wiki_root).as_posix().
        # ASCII '0' (48) < 'H' (72) — digits sort before uppercase letters.
        # Within solid (Foo 60, Baz 70):
        #   "01-Domain/Foo.md" < "02-Other/Baz.md" → Foo, Baz
        # Within outlined (Glossary 30, Home 50, Bar 40):
        #   "00-Start-Here/Glossary.md" < "01-Domain/Bar.md" < "Home.md"
        #   → Glossary, Bar, Home
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        foo_pos = content.index("[[Foo]]")
        baz_pos = content.index("[[Baz]]")
        glossary_pos = content.index("[[Glossary]]")
        bar_pos = content.index("[[Bar]]")
        home_pos = content.index("[[Home]]")
        # Within solid:
        self.assertLess(foo_pos, baz_pos)
        # Within outlined:
        self.assertLess(glossary_pos, bar_pos)
        self.assertLess(bar_pos, home_pos)

    def test_band_threshold_boundaries(self):
        # Mutate Home's completion across each band boundary; verify placement.
        cases = [
            (80, "ready"),
            (79, "solid"),
            (55, "solid"),
            (54, "outlined"),
            (30, "outlined"),
            (29, "gap"),
        ]
        for value, expected_band in cases:
            with self.subTest(completion=value, expected=expected_band):
                self._set_completion("Home.md", value)
                build_completion_dashboard.run(self.wiki)
                content = self._read_dashboard()
                self.assertEqual(
                    self._band_for_page(content, "Home"), expected_band
                )

    def test_page_without_completion_field_excluded(self):
        # Q1: absent `completion` field → page excluded entirely.
        self._strip_completion("Home.md")
        summary = build_completion_dashboard.run(self.wiki)
        self.assertEqual(summary["pages_tracked"], 4)
        content = self._read_dashboard()
        self.assertNotIn("[[Home]]", content)

    def test_out_of_band_values_placed_in_extreme_bands(self):
        # Q2: no clamping. 150 lands in ready, -10 lands in gap by threshold.
        self._set_completion("Home.md", 150)
        self._set_completion("01-Domain/Bar.md", -10)
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        self.assertEqual(self._band_for_page(content, "Home"), "ready")
        self.assertEqual(self._band_for_page(content, "Bar"), "gap")

    def test_entry_format_includes_percent(self):
        # Per-entry format: `- [[<stem>]] (<rel>) — <N>%` with U+2014 em-dash.
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        self.assertIn("- [[Foo]] (01-Domain/Foo.md) — 60%", content)
        self.assertIn("- [[Bar]] (01-Domain/Bar.md) — 40%", content)

    def test_paths_use_forward_slashes(self):
        # Per lessons.md style-note bullet 5: even on Windows, no backslash.
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        self.assertIn("(01-Domain/Foo.md)", content)
        self.assertIn("(00-Start-Here/Glossary.md)", content)
        self.assertIn("(02-Other/Baz.md)", content)
        self.assertNotIn("\\", content)

    def test_wikilink_uses_filename_stem(self):
        # [[Foo]], not [[01-Domain/Foo]], not [[Foo Framework]] (the title).
        build_completion_dashboard.run(self.wiki)
        content = self._read_dashboard()
        self.assertIn("[[Foo]]", content)
        self.assertNotIn("[[01-Domain/Foo]]", content)
        self.assertNotIn("[[Foo Framework]]", content)
        self.assertNotIn("[[Baz Framework]]", content)
        self.assertNotIn("[[Sample Wiki Home]]", content)

    def test_empty_wiki_writes_empty_dashboard(self):
        # Q3: strip `completion` from every page → "No completion data found."
        # Average becomes None → rendered as em-dash placeholder.
        for rel in (
            "Home.md",
            "00-Start-Here/Glossary.md",
            "01-Domain/Foo.md",
            "01-Domain/Bar.md",
            "02-Other/Baz.md",
        ):
            self._strip_completion(rel)
        summary = build_completion_dashboard.run(self.wiki)
        self.assertEqual(summary["pages_tracked"], 0)
        self.assertIsNone(summary["average_completion"])
        content = self._read_dashboard()
        self.assertIn("**Pages with completion data:** 0", content)
        self.assertIn("**Average completion:** —", content)
        self.assertIn("No completion data found.", content)
        self.assertNotIn("## ready", content)
        self.assertNotIn("## solid", content)
        self.assertNotIn("## outlined", content)
        self.assertNotIn("## gap", content)

    def test_dashboards_folder_created(self):
        # Fresh fixture has no `_dashboards/`; run() creates it.
        dashboards_dir = self.wiki / "_dashboards"
        self.assertFalse(
            dashboards_dir.exists(),
            "fixture should not pre-create _dashboards/",
        )
        build_completion_dashboard.run(self.wiki)
        self.assertTrue(dashboards_dir.exists())
        self.assertTrue(dashboards_dir.is_dir())


if __name__ == "__main__":
    unittest.main()
