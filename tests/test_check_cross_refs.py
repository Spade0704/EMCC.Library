"""Tests for _scripts/check_cross_refs.py — P9 cross-reference validator.

Covers AC1-AC7 from S030-T1 task_assignment plus AC4 dashboard-shape
lock-in (Pattern #5): full-tuple sort + entry-line literal × 2 classes.

Per-test isolation: TempDir + shutil.copytree per test; zero mutations
to the committed fixture under tests/fixtures/sample_wiki/.
"""

import io
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import check_cross_refs


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


class CheckCrossRefsTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.wiki = Path(self._tmpdir.name) / "wiki"
        shutil.copytree(FIXTURE_ROOT, self.wiki)

    def tearDown(self):
        self._tmpdir.cleanup()

    # -- helpers --

    def _read_dashboard(self):
        return (self.wiki / "_dashboards" / "cross_refs.md").read_text(
            encoding="utf-8"
        )

    def _write_page(self, rel_path, body, allow_orphan=False, extra_fm=""):
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
        if extra_fm:
            fm += extra_fm + "\n"
        fm += "---\n\n"
        path.write_text(fm + body, encoding="utf-8")
        return path

    def _set_allow_orphan_on_existing(self, rel_path):
        """Patch a fixture page in-temp to add allow_orphan: true to its fm."""
        path = self.wiki / rel_path
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")
        # Insert allow_orphan: true just before the closing '---' of the fm.
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                lines.insert(i, "allow_orphan: true")
                break
        path.write_text("\n".join(lines), encoding="utf-8")

    # -- AC1: aggregator API ------------------------------------------------

    def test_run_returns_dashboard_path(self):
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(
            summary["dashboard_path"],
            self.wiki / "_dashboards" / "cross_refs.md",
        )

    def test_run_keys_present(self):
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(
            set(summary.keys()),
            {"dashboard_path", "broken_links", "orphans", "pages_scanned"},
        )

    def test_default_fixture_baseline(self):
        """Default shipped fixture has no inbound wikilinks → all 5 content
        pages flag orphan under strict v1.0 definition; 0 broken-links.

        Locks the no-link baseline. If P12 (or any future task) adds
        wikilinks to the fixture pages, this test must be paired-updated
        — re-seed the expectation from the new fixture state before the
        edit lands. AC3 guarantee: per-test in-temp fixture mutation only,
        never shipped fixture.
        """
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(summary["pages_scanned"], 5)
        self.assertEqual(summary["broken_links"], [])
        self.assertEqual(len(summary["orphans"]), 5)

    # -- AC5: dashboard frontmatter + summary -------------------------------

    def test_dashboard_5_field_fm(self):
        check_cross_refs.run(self.wiki)
        dash = self._read_dashboard()
        head = dash.split("---", 2)
        self.assertEqual(head[0], "")
        fm_block = head[1]
        self.assertIn('title: "Cross-References Dashboard"', fm_block)
        self.assertIn("type: dashboard", fm_block)
        self.assertIn("visibility: internal", fm_block)
        self.assertIn("generated: true", fm_block)
        self.assertIn("last_updated: ", fm_block)

    def test_dashboard_summary_bold_label_lines(self):
        # Seed exactly 1 broken + 0 orphans so the bold-label line is
        # deterministic. Make every page link to every other page so no
        # orphans, plus one broken link.
        self._set_allow_orphan_on_existing("Home.md")
        self._set_allow_orphan_on_existing("00-Start-Here/Glossary.md")
        self._set_allow_orphan_on_existing("01-Domain/Foo.md")
        self._set_allow_orphan_on_existing("01-Domain/Bar.md")
        self._set_allow_orphan_on_existing("02-Other/Baz.md")
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "Body line.\n[[Missing]] target here.\n",
            allow_orphan=True,
        )
        check_cross_refs.run(self.wiki)
        dash = self._read_dashboard()
        self.assertIn("**Pages scanned:** 6", dash)
        self.assertIn("**Findings:** 1 (1 broken / 0 orphans)", dash)

    def test_dashboard_omits_empty_broken_band(self):
        # Default fixture: 0 broken, 5 orphans. broken band must be omitted.
        check_cross_refs.run(self.wiki)
        dash = self._read_dashboard()
        self.assertNotIn("## broken_wikilinks", dash)
        self.assertIn("## orphan_pages", dash)

    def test_dashboard_omits_empty_orphan_band(self):
        # Exempt all 5 default pages so 0 orphans; seed 1 broken link.
        for rel in ("Home.md", "00-Start-Here/Glossary.md",
                    "01-Domain/Foo.md", "01-Domain/Bar.md", "02-Other/Baz.md"):
            self._set_allow_orphan_on_existing(rel)
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "[[Missing]] target.\n",
            allow_orphan=True,
        )
        check_cross_refs.run(self.wiki)
        dash = self._read_dashboard()
        self.assertIn("## broken_wikilinks", dash)
        self.assertNotIn("## orphan_pages", dash)

    def test_dashboard_no_findings_message(self):
        for rel in ("Home.md", "00-Start-Here/Glossary.md",
                    "01-Domain/Foo.md", "01-Domain/Bar.md", "02-Other/Baz.md"):
            self._set_allow_orphan_on_existing(rel)
        check_cross_refs.run(self.wiki)
        dash = self._read_dashboard()
        self.assertIn("No cross-reference findings.", dash)
        self.assertNotIn("## broken_wikilinks", dash)
        self.assertNotIn("## orphan_pages", dash)

    # -- Q1: wikilink syntax shapes -----------------------------------------

    def test_broken_wikilink_bare(self):
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "[[Missing]] target.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        targets = [f["link"] for f in summary["broken_links"]]
        self.assertIn("Missing", targets)

    def test_alias_wikilink_resolves_target_stem(self):
        # [[Foo|display]] resolves to Foo.md; Foo.md exists in fixture → not broken.
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "Link [[Foo|see Foo]] here.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        # Foo.md now has inbound from Linker → Foo not orphan; no broken link.
        self.assertEqual(summary["broken_links"], [])
        orphan_stems = {o["page_path"].stem for o in summary["orphans"]}
        self.assertNotIn("Foo", orphan_stems)

    def test_section_wikilink_resolves_target_stem(self):
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "Link [[Foo#section]] here.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(summary["broken_links"], [])
        orphan_stems = {o["page_path"].stem for o in summary["orphans"]}
        self.assertNotIn("Foo", orphan_stems)

    def test_embed_wikilink_resolves_target_stem(self):
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "Embed ![[Foo]] here.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(summary["broken_links"], [])
        orphan_stems = {o["page_path"].stem for o in summary["orphans"]}
        self.assertNotIn("Foo", orphan_stems)

    # -- Q4: code-block stripping -------------------------------------------

    def test_fenced_code_wikilink_ignored(self):
        body = (
            "Real link [[Foo]] here.\n"
            "```\n"
            "[[Missing]]\n"
            "```\n"
        )
        self._write_page(
            Path("01-Domain") / "Linker.md",
            body,
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        # Only Foo (real) processed; Missing inside fence ignored.
        self.assertEqual(summary["broken_links"], [])

    def test_inline_code_wikilink_ignored(self):
        body = "Real link [[Foo]]; example `[[Missing]]` here.\n"
        self._write_page(
            Path("01-Domain") / "Linker.md",
            body,
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(summary["broken_links"], [])

    # -- Q5: file-relative line numbers (fm offset) -------------------------

    def test_line_numbers_after_fenced_block(self):
        body = (
            "Line 1 of body.\n"
            "```\n"
            "fenced line 1\n"
            "fenced line 2\n"
            "```\n"
            "Line 6 of body with [[Missing]] link.\n"
        )
        page_path = self._write_page(
            Path("01-Domain") / "Linker.md",
            body,
            allow_orphan=True,
        )
        # fm uses 9 lines (8 fields + opening ---), closing --- at line 10,
        # blank at line 11; body starts at line 12.
        # Compute actual fm line count from disk.
        raw = page_path.read_text(encoding="utf-8")
        fm_count = 0
        for i, line in enumerate(raw.split("\n")[1:], start=1):
            if line.strip() == "---":
                fm_count = i + 1
                break
        # Body line 6 = file line (fm_count + 6).
        # _write_page inserts a blank line after fm close, so body line 1 of
        # _iter_wikilinks corresponds to file line (fm_count + 2).
        # Actual link is on body-relative line 6 (after blank) → file line
        # = fm_count + 1 (blank) + 6 = fm_count + 7. Adjust per writer.
        summary = check_cross_refs.run(self.wiki)
        broken = [f for f in summary["broken_links"] if f["link"] == "Missing"]
        self.assertEqual(len(broken), 1)
        # The link must report a file-relative line (fm offset applied).
        # Lower bound: > body-relative 6.
        self.assertGreater(broken[0]["line"], 6)

    # -- Q2: orphan strict definition + escape hatch ------------------------

    def test_orphan_strict_definition(self):
        """Page with zero inbound wikilinks → orphan. Self-link does NOT
        clear (a page does not orphan-clear itself). R3 mitigation."""
        body = "Self ref [[Solo]] inside.\n"
        self._write_page(Path("01-Domain") / "Solo.md", body)
        summary = check_cross_refs.run(self.wiki)
        orphan_stems = {o["page_path"].stem for o in summary["orphans"]}
        self.assertIn("Solo", orphan_stems)

    def test_inbound_wikilink_clears_orphan(self):
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "Linking [[Target]] here.\n",
            allow_orphan=True,
        )
        self._write_page(Path("01-Domain") / "Target.md", "Body.\n")
        summary = check_cross_refs.run(self.wiki)
        orphan_stems = {o["page_path"].stem for o in summary["orphans"]}
        self.assertNotIn("Target", orphan_stems)

    def test_allow_orphan_escape_hatch(self):
        # Page with allow_orphan: true and no inbound links → NOT flagged.
        self._write_page(
            Path("01-Domain") / "ExemptedSolo.md",
            "No inbound, no outbound.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        orphan_stems = {o["page_path"].stem for o in summary["orphans"]}
        self.assertNotIn("ExemptedSolo", orphan_stems)

    # -- AC4(a): full-tuple sort lock-in (Pattern #5) -----------------------

    def test_findings_sorted_full_tuple(self):
        """Seeds findings across both classes and across the three sort
        sub-clauses (cross-path same-line broken, same-path cross-line
        broken, cross-path orphan), then asserts the projected
        (class, rel_path, line_or_zero) tuple sequence with full
        list-equality. Locks the within-section sort against any
        sort-key drift (Pattern #5)."""
        # Linker pages (allow_orphan to keep them out of orphan list).
        self._write_page(
            Path("01-Domain") / "LinkerA.md",
            "First [[BadOne]] line one.\nSecond [[BadTwo]] on line two.\n",
            allow_orphan=True,
        )
        self._write_page(
            Path("02-Other") / "LinkerB.md",
            "Body [[BadOne]] here.\n",
            allow_orphan=True,
        )
        # Two strict-orphan pages on distinct paths.
        self._write_page(Path("03-Alpha") / "OrphAlpha.md", "Body.\n")
        self._write_page(Path("03-Alpha") / "OrphBeta.md", "Body.\n")

        summary = check_cross_refs.run(self.wiki)

        tuples = []
        for f in summary["broken_links"]:
            rel = f["page_path"].relative_to(self.wiki).as_posix()
            tuples.append(("broken_wikilinks", rel, f["line"]))
        for f in summary["orphans"]:
            rel = f["page_path"].relative_to(self.wiki).as_posix()
            tuples.append(("orphan_pages", rel, 0))

        # Filter to seeded-only signals (drop default-fixture orphans
        # not relevant to the sort assertion).
        seeded = [t for t in tuples if (
            t[0] == "broken_wikilinks"
            or t[1] in ("03-Alpha/OrphAlpha.md", "03-Alpha/OrphBeta.md")
        )]

        # Compute expected line numbers from disk (fm offset is
        # _write_page-author-dependent).
        linker_a = self.wiki / "01-Domain" / "LinkerA.md"
        linker_b = self.wiki / "02-Other" / "LinkerB.md"
        fm_a = _fm_count(linker_a)
        fm_b = _fm_count(linker_b)
        # _write_page emits fm + "\n\n" before body, so body line N = fm + 1 + N.
        line_a1 = fm_a + 1 + 1   # LinkerA body line 1
        line_a2 = fm_a + 1 + 2   # LinkerA body line 2
        line_b1 = fm_b + 1 + 1   # LinkerB body line 1

        # Within broken-wikilinks: sort by (rel, line). Posix-rel for
        # 01-Domain/LinkerA.md sorts before 02-Other/LinkerB.md.
        # Within orphan-pages: sort by rel only.
        expected = [
            ("broken_wikilinks", "01-Domain/LinkerA.md", line_a1),
            ("broken_wikilinks", "01-Domain/LinkerA.md", line_a2),
            ("broken_wikilinks", "02-Other/LinkerB.md", line_b1),
            ("orphan_pages", "03-Alpha/OrphAlpha.md", 0),
            ("orphan_pages", "03-Alpha/OrphBeta.md", 0),
        ]
        self.assertEqual(seeded, expected)

    # -- AC4(b): entry-line literal lock-in (Pattern #5) --------------------

    def test_dashboard_entry_line_literal_broken(self):
        page_path = self._write_page(
            Path("01-Domain") / "Linker.md",
            "[[Missing]] on line one.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        broken = [f for f in summary["broken_links"] if f["link"] == "Missing"]
        self.assertEqual(len(broken), 1)
        line = broken[0]["line"]
        dash = self._read_dashboard()
        expected = "- broken: 01-Domain/Linker.md:{}: [[Missing]] target not found".format(
            line
        )
        self.assertIn(expected, dash)

    def test_dashboard_entry_line_literal_orphan(self):
        # Use a fresh seeded orphan to avoid coupling to default-fixture pages.
        self._write_page(Path("03-Alpha") / "OrphSeed.md", "Body.\n")
        check_cross_refs.run(self.wiki)
        dash = self._read_dashboard()
        self.assertIn("- orphan: 03-Alpha/OrphSeed.md", dash)

    # -- Path-qualified wikilink resolution (Style-Guide-mandated form) -----

    def test_path_qualified_wikilink_resolves(self):
        # [[01-Domain/Foo]] points at the real fixture page 01-Domain/Foo.md.
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "See [[01-Domain/Foo]] for detail.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(summary["broken_links"], [])
        orphan_stems = {o["page_path"].stem for o in summary["orphans"]}
        self.assertNotIn("Foo", orphan_stems)

    def test_path_qualified_with_md_extension_resolves(self):
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "See [[01-Domain/Foo.md]] here.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(summary["broken_links"], [])

    def test_path_qualified_wrong_folder_is_broken(self):
        # The Breaker's guard: a path-qualified link whose folder does NOT
        # exist must NOT resolve by last segment to a real stem elsewhere.
        # Foo.md lives at 01-Domain/, not ghost/.
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "Broken [[ghost/Foo]] link.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        targets = [f["link"] for f in summary["broken_links"]]
        self.assertIn("ghost/Foo", targets)

    def test_duplicate_stem_path_qualified_does_not_false_clear(self):
        # Two pages share the stem "Setup". [[a/Setup]] must resolve to a/Setup
        # ONLY — it must not clear b/Setup's orphan status via last-segment match.
        self._write_page(Path("a") / "Setup.md", "Page A body.\n")
        self._write_page(Path("b") / "Setup.md", "Page B body.\n")
        self._write_page(
            Path("01-Domain") / "Linker.md",
            "Only [[a/Setup]] is linked.\n",
            allow_orphan=True,
        )
        summary = check_cross_refs.run(self.wiki)
        self.assertEqual(summary["broken_links"], [])
        orphan_rels = {
            o["page_path"].relative_to(self.wiki).as_posix()
            for o in summary["orphans"]
        }
        # a/Setup linked → cleared; b/Setup never linked → still orphan.
        self.assertNotIn("a/Setup.md", orphan_rels)
        self.assertIn("b/Setup.md", orphan_rels)

    # -- AC6: wiki_root.is_dir() precheck (S017 lesson, P7 precedent) -------

    def test_run_raises_filenotfounderror_on_missing_wiki_root(self):
        missing = Path(self._tmpdir.name) / "does_not_exist"
        with self.assertRaises(FileNotFoundError):
            check_cross_refs.run(missing)

    # -- AC7: exit codes ----------------------------------------------------

    def test_main_exit_0_clean(self):
        # Exempt all 5 default pages so 0 orphans, 0 broken → exit 0.
        for rel in ("Home.md", "00-Start-Here/Glossary.md",
                    "01-Domain/Foo.md", "01-Domain/Bar.md", "02-Other/Baz.md"):
            self._set_allow_orphan_on_existing(rel)
        out, err = io.StringIO(), io.StringIO()
        rc = check_cross_refs._main(self.wiki, stdout=out, stderr=err)
        self.assertEqual(rc, 0)

    def test_main_exit_1_with_findings(self):
        # Default fixture has 5 orphans → exit 1.
        out, err = io.StringIO(), io.StringIO()
        rc = check_cross_refs._main(self.wiki, stdout=out, stderr=err)
        self.assertEqual(rc, 1)

    def test_main_exit_2_missing_wiki(self):
        missing = Path(self._tmpdir.name) / "does_not_exist"
        out, err = io.StringIO(), io.StringIO()
        rc = check_cross_refs._main(missing, stdout=out, stderr=err)
        self.assertEqual(rc, 2)
        self.assertIn("error:", err.getvalue())


def _fm_count(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return 0
    for i, line in enumerate(text.split("\n")[1:], start=1):
        if line.strip() == "---":
            return i + 1
    return 0


if __name__ == "__main__":
    unittest.main()
