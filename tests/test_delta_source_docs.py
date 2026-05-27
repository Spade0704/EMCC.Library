"""Tests for _scripts/delta_source_docs.py — P16 (diff core + cascade + dashboard)."""

import io
import shutil
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import delta_source_docs
from _lib import frontmatter


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures" / "source_delta"


def _diff(case: str):
    """Run delta against a fixture pair using a throwaway tempdir wiki_root.

    Tempdir wrap (S037-T5 R8) prevents the always-written dashboard at
    `wiki_root/_dashboards/source_delta.md` from polluting the fixture
    subdir post-T5 extension. T4 test semantics unchanged — asserts run
    against the returned `run()` dict; dashboard side-effect auto-cleaned.
    """
    case_dir = FIXTURES_ROOT / case
    with TemporaryDirectory() as tmp:
        return delta_source_docs.run(
            case_dir / "a.md",
            case_dir / "b.md",
            wiki_root=Path(tmp),
        )


class TestSectionChanges(unittest.TestCase):

    def test_identical_versions_no_changes(self):
        result = _diff("identical")
        types = [c["type"] for c in result["section_changes"]]
        self.assertTrue(all(t == "unchanged" for t in types))
        s = result["summary"]
        self.assertEqual(s["sections_added"], 0)
        self.assertEqual(s["sections_removed"], 0)
        self.assertEqual(s["sections_modified"], 0)
        self.assertEqual(s["sections_unchanged"], len(types))
        self.assertEqual(s["total_lines_added"], 0)
        self.assertEqual(s["total_lines_removed"], 0)
        fm = result["frontmatter_changes"]
        self.assertEqual(fm["added_keys"], [])
        self.assertEqual(fm["removed_keys"], [])
        self.assertEqual(fm["modified_keys"], [])

    def test_section_added(self):
        result = _diff("section_added")
        added = [c for c in result["section_changes"] if c["type"] == "added"]
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]["section_title"], "New Section")
        self.assertGreater(added[0]["added_lines"], 0)
        self.assertEqual(added[0]["removed_lines"], 0)
        self.assertEqual(result["summary"]["sections_added"], 1)

    def test_section_removed(self):
        result = _diff("section_removed")
        removed = [c for c in result["section_changes"] if c["type"] == "removed"]
        self.assertEqual(len(removed), 1)
        self.assertEqual(removed[0]["section_title"], "Doomed Section")
        self.assertGreater(removed[0]["removed_lines"], 0)
        self.assertEqual(removed[0]["added_lines"], 0)
        self.assertEqual(result["summary"]["sections_removed"], 1)

    def test_section_modified_line_level(self):
        result = _diff("section_modified")
        modified = [c for c in result["section_changes"] if c["type"] == "modified"]
        self.assertEqual(len(modified), 1)
        self.assertEqual(modified[0]["section_title"], "Changeable Section")
        self.assertGreater(modified[0]["added_lines"], 0)
        self.assertGreater(modified[0]["removed_lines"], 0)
        self.assertTrue(modified[0]["line_diff"])
        self.assertEqual(result["summary"]["sections_modified"], 1)


class TestFrontmatterChanges(unittest.TestCase):

    def test_fm_key_added(self):
        result = _diff("fm_key_added")
        fm = result["frontmatter_changes"]
        self.assertEqual(fm["added_keys"], ["new_key"])
        self.assertEqual(fm["removed_keys"], [])
        self.assertEqual(fm["modified_keys"], [])

    def test_fm_value_modified(self):
        result = _diff("fm_value_modified")
        fm = result["frontmatter_changes"]
        self.assertEqual(fm["modified_keys"], ["version"])
        self.assertEqual(fm["added_keys"], [])
        self.assertEqual(fm["removed_keys"], [])


class TestIntroContent(unittest.TestCase):

    def test_intro_content_pre_first_h2(self):
        result = _diff("intro_content")
        titles = [c["section_title"] for c in result["section_changes"]]
        self.assertIn(delta_source_docs.INTRO_SECTION_TITLE, titles)
        intro = next(
            c for c in result["section_changes"]
            if c["section_title"] == delta_source_docs.INTRO_SECTION_TITLE
        )
        self.assertEqual(intro["type"], "unchanged")


class TestDuplicateTitles(unittest.TestCase):

    def test_duplicate_titles_first_pair_quirk(self):
        # Fixture: 2x "Notes" in A and 2x "Notes" in B with differing bodies.
        # FIFO pairing per R5: first-A pairs with first-B (both modified);
        # second-A pairs with second-B (both modified). No added/removed.
        result = _diff("duplicate_titles")
        changes = result["section_changes"]
        self.assertEqual(len(changes), 2)
        for change in changes:
            self.assertEqual(change["section_title"], "Notes")
            self.assertEqual(change["type"], "modified")
        self.assertEqual(result["summary"]["sections_added"], 0)
        self.assertEqual(result["summary"]["sections_removed"], 0)
        self.assertEqual(result["summary"]["sections_modified"], 2)


class TestInputErrors(unittest.TestCase):

    def test_missing_version_a_rc2(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        rc = delta_source_docs._main(
            argv=[
                str(FIXTURES_ROOT / "nonexistent" / "missing.md"),
                str(FIXTURES_ROOT / "identical" / "b.md"),
            ],
            wiki_root=FIXTURES_ROOT,
            stdout=stdout,
            stderr=stderr,
        )
        self.assertEqual(rc, 2)
        self.assertIn("not found", stderr.getvalue())


def _copy_pair_into(wiki: Path, case: str):
    """Copy a fixture-pair into wiki root so version paths resolve under wiki_root."""
    case_dir = FIXTURES_ROOT / case
    (wiki / "a.md").write_bytes((case_dir / "a.md").read_bytes())
    (wiki / "b.md").write_bytes((case_dir / "b.md").read_bytes())
    return wiki / "a.md", wiki / "b.md"


def _write_cascade_map(wiki: Path, body: str):
    """Write `_config/cascade_map.yaml` under wiki root."""
    cfg = wiki / "_config" / "cascade_map.yaml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(body, encoding="utf-8")
    return cfg


class TestCascadeImpact(unittest.TestCase):

    def test_cascade_impact_populated_when_map_matches(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            version_a, version_b = _copy_pair_into(wiki, "section_modified")
            _write_cascade_map(wiki, (
                "pairs:\n"
                "  - source: a.md\n"
                "    derived: 01-Domain/Derived.md\n"
            ))
            stderr = io.StringIO()
            result = delta_source_docs.run(
                version_a, version_b, wiki_root=wiki, stderr=stderr
            )
            self.assertEqual(len(result["cascade_impact"]), 1)
            entry = result["cascade_impact"][0]
            self.assertEqual(entry["source_path"], "a.md")
            self.assertEqual(entry["derived_path"], "01-Domain/Derived.md")
            self.assertIn("Changeable Section", entry["affected_by_sections"])
            self.assertEqual(stderr.getvalue(), "")

    def test_cascade_impact_empty_when_no_cascade_map(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            version_a, version_b = _copy_pair_into(wiki, "section_modified")
            stderr = io.StringIO()
            result = delta_source_docs.run(
                version_a, version_b, wiki_root=wiki, stderr=stderr
            )
            self.assertEqual(result["cascade_impact"], [])
            self.assertIn("cascade_map.yaml not found", stderr.getvalue())

    def test_cascade_impact_empty_when_map_no_match(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            version_a, version_b = _copy_pair_into(wiki, "section_modified")
            _write_cascade_map(wiki, (
                "pairs:\n"
                "  - source: unrelated/other.md\n"
                "    derived: derived/something.md\n"
            ))
            stderr = io.StringIO()
            result = delta_source_docs.run(
                version_a, version_b, wiki_root=wiki, stderr=stderr
            )
            self.assertEqual(result["cascade_impact"], [])
            self.assertIn("no cascade_map.yaml entries match", stderr.getvalue())


class TestDashboard(unittest.TestCase):

    def test_dashboard_written_at_expected_path(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            version_a, version_b = _copy_pair_into(wiki, "section_modified")
            result = delta_source_docs.run(
                version_a, version_b, wiki_root=wiki
            )
            expected = wiki / "_dashboards" / "source_delta.md"
            self.assertTrue(expected.exists())
            self.assertEqual(result["dashboard_path"], expected)

    def test_dashboard_fm_5_field_contract(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            version_a, version_b = _copy_pair_into(wiki, "section_modified")
            delta_source_docs.run(version_a, version_b, wiki_root=wiki)
            page = frontmatter.load_page(wiki / "_dashboards" / "source_delta.md")
            fm = page["frontmatter"]
            self.assertEqual(set(fm.keys()), {
                "title", "type", "visibility", "generated", "last_updated"
            })
            self.assertEqual(fm["title"], "Source-Doc Delta Dashboard")
            self.assertEqual(fm["type"], "dashboard")
            self.assertEqual(fm["visibility"], "internal")
            self.assertEqual(fm["generated"], True)
            self.assertEqual(fm["last_updated"], date.today().isoformat())

    def test_dashboard_body_4_sections_in_order(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            version_a, version_b = _copy_pair_into(wiki, "section_modified")
            delta_source_docs.run(version_a, version_b, wiki_root=wiki)
            body = (wiki / "_dashboards" / "source_delta.md").read_text(encoding="utf-8")
            h2s = [
                line[3:].strip()
                for line in body.split("\n")
                if line.startswith("## ")
            ]
            self.assertEqual(h2s, [
                "Summary",
                "Frontmatter Changes",
                "Section Changes",
                "Cascade Impact",
            ])


if __name__ == "__main__":
    unittest.main()
