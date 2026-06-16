"""Tests for _scripts/check_link_graph.py — deeper link-graph integrity layer.

Covers the two graph-integrity finding classes that sit above cross-refs:
    unreachable_pages  no path from the entry page (Home.md) via wikilinks
    dead_end_pages     zero outbound resolvable wikilinks (navigation sink)

Plus the allow_orphan escape-hatch parity, entry-page handling, dashboard
shape, API surface, and exit codes.

Per-test isolation: TempDir + shutil.copytree per test; zero mutations to the
committed fixture under tests/fixtures/sample_wiki/. Mirrors the
test_check_cross_refs.py harness.
"""

import io
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import check_link_graph


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


class CheckLinkGraphTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.wiki = Path(self._tmpdir.name) / "wiki"
        shutil.copytree(FIXTURE_ROOT, self.wiki)

    def tearDown(self):
        self._tmpdir.cleanup()

    # -- helpers --

    def _read_dashboard(self):
        return (self.wiki / "_dashboards" / "link_graph.md").read_text(
            encoding="utf-8"
        )

    def _write_page(self, rel_path, body, allow_orphan=False):
        path = self.wiki / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        fm = (
            "---\n"
            'title: "Test Page"\n'
            "type: reference\n"
            "visibility: internal\n"
            "completion: 0\n"
            "status: outlined\n"
            "last_updated: 2026-05-09\n"
        )
        if allow_orphan:
            fm += "allow_orphan: true\n"
        fm += "---\n\n"
        path.write_text(fm + body, encoding="utf-8")
        return path

    def _rels(self, findings):
        return {
            f["page_path"].relative_to(self.wiki).as_posix() for f in findings
        }

    # -- API surface --------------------------------------------------------

    def test_run_returns_dashboard_path(self):
        summary = check_link_graph.run(self.wiki)
        self.assertEqual(
            summary["dashboard_path"],
            self.wiki / "_dashboards" / "link_graph.md",
        )

    def test_run_keys_present(self):
        summary = check_link_graph.run(self.wiki)
        self.assertEqual(
            set(summary.keys()),
            {"dashboard_path", "unreachable", "dead_ends",
             "pages_scanned", "entry_page"},
        )

    def test_entry_page_resolved_from_home(self):
        summary = check_link_graph.run(self.wiki)
        self.assertEqual(summary["entry_page"], self.wiki / "Home.md")

    # -- Reachability (unreachable_pages) -----------------------------------

    def test_island_cluster_is_unreachable_though_mutually_linked(self):
        # Two pages link ONLY to each other (an island). Each clears the other's
        # orphan status (cross-refs would not flag them), yet neither is
        # reachable from Home → both unreachable here. This is the property
        # cross-refs cannot see.
        self._write_page(Path("isle") / "A.md", "Go to [[B]].\n")
        self._write_page(Path("isle") / "B.md", "Back to [[A]].\n")
        summary = check_link_graph.run(self.wiki)
        unreachable = self._rels(summary["unreachable"])
        self.assertIn("isle/A.md", unreachable)
        self.assertIn("isle/B.md", unreachable)

    def test_page_reachable_from_home_not_unreachable(self):
        # Home links to Hub, Hub links to Leaf → Leaf reachable transitively.
        self._write_page(Path("Home.md"), "Start [[Hub]].\n", allow_orphan=True)
        self._write_page(Path("Hub.md"), "Down to [[Leaf]].\n")
        self._write_page(Path("Leaf.md"), "Leaf links back [[Hub]].\n")
        summary = check_link_graph.run(self.wiki)
        unreachable = self._rels(summary["unreachable"])
        self.assertNotIn("Hub.md", unreachable)
        self.assertNotIn("Leaf.md", unreachable)

    def test_entry_page_itself_never_unreachable(self):
        summary = check_link_graph.run(self.wiki)
        unreachable = self._rels(summary["unreachable"])
        self.assertNotIn("Home.md", unreachable)

    def test_allow_orphan_exempts_from_unreachable(self):
        # An exempted island page is not reported unreachable.
        self._write_page(
            Path("isle") / "Solo.md", "Lonely [[Nowhere]].\n", allow_orphan=True
        )
        summary = check_link_graph.run(self.wiki)
        unreachable = self._rels(summary["unreachable"])
        self.assertNotIn("isle/Solo.md", unreachable)

    def test_missing_entry_page_reports_unreachable(self):
        # With no Home.md and a non-existent entry stem, every non-exempt page
        # is unreachable (loud signal that the wiki has no front door).
        summary = check_link_graph.run(self.wiki, entry_stem="DoesNotExist")
        self.assertIsNone(summary["entry_page"])
        # The default fixture's 5 pages all lack allow_orphan → all unreachable.
        self.assertEqual(len(summary["unreachable"]), summary["pages_scanned"])

    # -- Dead-ends (dead_end_pages) -----------------------------------------

    def test_page_with_no_outbound_is_dead_end(self):
        # The default fixture pages have no wikilinks → all are dead-ends.
        summary = check_link_graph.run(self.wiki)
        dead = self._rels(summary["dead_ends"])
        self.assertIn("Home.md", dead)

    def test_page_with_outbound_is_not_dead_end(self):
        self._write_page(Path("Linker.md"), "Out to [[Foo]].\n", allow_orphan=True)
        summary = check_link_graph.run(self.wiki)
        dead = self._rels(summary["dead_ends"])
        self.assertNotIn("Linker.md", dead)

    def test_self_link_does_not_clear_dead_end(self):
        # A page linking only to itself cannot be left → still a dead-end.
        # (No allow_orphan: the exemption would suppress the dead-end report,
        # so we leave it on to actually exercise the self-link edge rule.)
        self._write_page(Path("Selfish.md"), "Only [[Selfish]].\n")
        summary = check_link_graph.run(self.wiki)
        dead = self._rels(summary["dead_ends"])
        self.assertIn("Selfish.md", dead)

    def test_broken_link_does_not_clear_dead_end(self):
        # A page whose only link is broken has no real out-edge → dead-end.
        self._write_page(Path("Broken.md"), "Bad [[Nowhere]].\n")
        summary = check_link_graph.run(self.wiki)
        dead = self._rels(summary["dead_ends"])
        self.assertIn("Broken.md", dead)

    def test_allow_orphan_exempts_from_dead_end(self):
        self._write_page(Path("Exempt.md"), "No links here.\n", allow_orphan=True)
        summary = check_link_graph.run(self.wiki)
        dead = self._rels(summary["dead_ends"])
        self.assertNotIn("Exempt.md", dead)

    # -- Resolver parity with cross-refs ------------------------------------

    def test_page_relative_edge_counts_for_reachability(self):
        # Home reaches a deep page via a `../`-bearing page-relative link, proving
        # the graph uses the same resolver as cross-refs.
        self._write_page(Path("Home.md"), "Into [[hub/Index]].\n", allow_orphan=True)
        self._write_page(Path("hub") / "Index.md", "Up-over [[../sib/Page]].\n")
        self._write_page(Path("sib") / "Page.md", "Leaf [[hub/Index]].\n")
        summary = check_link_graph.run(self.wiki)
        unreachable = self._rels(summary["unreachable"])
        self.assertNotIn("sib/Page.md", unreachable)

    # -- Dashboard shape ----------------------------------------------------

    def test_dashboard_5_field_fm(self):
        check_link_graph.run(self.wiki)
        dash = self._read_dashboard()
        head = dash.split("---", 2)
        self.assertEqual(head[0], "")
        fm_block = head[1]
        self.assertIn('title: "Link-Graph Dashboard"', fm_block)
        self.assertIn("type: dashboard", fm_block)
        self.assertIn("generated: true", fm_block)

    def test_dashboard_entry_line_literal_unreachable(self):
        self._write_page(Path("isle") / "A.md", "Go to [[B]].\n")
        self._write_page(Path("isle") / "B.md", "Back to [[A]].\n")
        check_link_graph.run(self.wiki)
        dash = self._read_dashboard()
        self.assertIn(
            "- unreachable: isle/A.md (no path from entry page)", dash
        )

    def test_dashboard_entry_line_literal_dead_end(self):
        check_link_graph.run(self.wiki)
        dash = self._read_dashboard()
        self.assertIn("- dead-end: Home.md (no outbound links)", dash)

    def test_dashboard_no_findings_message(self):
        # Exempt every default page AND give each an outbound link so there are
        # neither unreachable nor dead-end findings.
        for rel in ("Home.md", "00-Start-Here/Glossary.md",
                    "01-Domain/Foo.md", "01-Domain/Bar.md", "02-Other/Baz.md"):
            # Re-write each page with allow_orphan + a link to Home (Home links
            # to itself-excluded, so give Home a link to Foo).
            target = "Foo" if rel == "Home.md" else "Home"
            self._write_page(Path(rel), "Link [[{}]].\n".format(target),
                             allow_orphan=True)
        summary = check_link_graph.run(self.wiki)
        self.assertEqual(summary["unreachable"], [])
        self.assertEqual(summary["dead_ends"], [])
        dash = self._read_dashboard()
        self.assertIn("No link-graph findings.", dash)

    # -- Errors + exit codes ------------------------------------------------

    def test_run_raises_filenotfounderror_on_missing_wiki_root(self):
        missing = Path(self._tmpdir.name) / "does_not_exist"
        with self.assertRaises(FileNotFoundError):
            check_link_graph.run(missing)

    def test_main_exit_1_with_findings(self):
        out, err = io.StringIO(), io.StringIO()
        rc = check_link_graph._main(self.wiki, stdout=out, stderr=err)
        # Default fixture: pages are dead-ends → findings → exit 1.
        self.assertEqual(rc, 1)

    def test_main_exit_0_clean(self):
        for rel in ("Home.md", "00-Start-Here/Glossary.md",
                    "01-Domain/Foo.md", "01-Domain/Bar.md", "02-Other/Baz.md"):
            target = "Foo" if rel == "Home.md" else "Home"
            self._write_page(Path(rel), "Link [[{}]].\n".format(target),
                             allow_orphan=True)
        out, err = io.StringIO(), io.StringIO()
        rc = check_link_graph._main(self.wiki, stdout=out, stderr=err)
        self.assertEqual(rc, 0)

    def test_main_exit_2_missing_wiki(self):
        missing = Path(self._tmpdir.name) / "does_not_exist"
        out, err = io.StringIO(), io.StringIO()
        rc = check_link_graph._main(missing, stdout=out, stderr=err)
        self.assertEqual(rc, 2)
        self.assertIn("error:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
