"""Tests for _scripts/validate_canon_integrity.py — P7 fm-only validator."""

import io
import shutil
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import validate_canon_integrity
from _lib import frontmatter


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


# Default fixture has no status:ready pages (Home solid, Glossary outlined,
# Foo solid, Bar outlined, Baz solid). Default run therefore yields 0 scanned
# / 0 findings. Tests requiring scanned pages add fixtures in-test, never
# mutating the canonical fixture on disk (per P6 TempDir+copytree precedent).


def _make_page(path, *, status="ready", canon_sources=None,
               unverified_claims=None, title="Test Page",
               extra_fm_lines=()):
    """Write a minimal content page with the requested fm shape."""
    fm_lines = ['---', 'title: "' + title + '"',
                "type: reference", "visibility: internal"]
    if status is not _STATUS_OMIT:
        if status is None:
            fm_lines.append("status: null")
        elif isinstance(status, int):
            fm_lines.append("status: " + str(status))
        else:
            fm_lines.append("status: " + status)
    if canon_sources is not None:
        fm_lines.append("canon_sources: " + _flow_list(canon_sources))
    if unverified_claims is not None:
        fm_lines.append("unverified_claims: " + _flow_list(unverified_claims))
    fm_lines.extend(extra_fm_lines)
    fm_lines.append("---")
    fm_lines.append("")
    fm_lines.append("# " + title)
    fm_lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(fm_lines), encoding="utf-8")


_STATUS_OMIT = object()


def _flow_list(items):
    return "[" + ", ".join('"' + i + '"' for i in items) + "]"


def _make_page_block_canon(path, items, *, status="ready", title="Block Page"):
    """Write a content page whose canon_sources uses BLOCK-style list form.

    The `_make_page` helper above only emits inline flow-list canon_sources
    (`[a, b]`). This variant emits the block-style form:

        canon_sources:
          - "a"
          - "b"

    so the parser->validator seam can be regression-tested against the form
    that previously parsed to None (dir-20260614qq; fixed in frontmatter.py
    commit cf9a834). An empty `items` list emits a bare `canon_sources:`
    (which now also stays None — the no-source case the validator must flag).
    """
    fm_lines = ['---', 'title: "' + title + '"',
                "type: reference", "visibility: internal",
                "status: " + status, "canon_sources:"]
    for item in items:
        fm_lines.append('  - "' + item + '"')
    fm_lines.append("unverified_claims: []")
    fm_lines.append("---")
    fm_lines.append("")
    fm_lines.append("# " + title)
    fm_lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(fm_lines), encoding="utf-8")


class ValidateCanonIntegrityTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.wiki = Path(self._tmpdir.name) / "wiki"
        shutil.copytree(FIXTURE_ROOT, self.wiki)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _read_dashboard(self):
        return (self.wiki / "_dashboards" / "canon_integrity.md").read_text(
            encoding="utf-8"
        )

    # --- Return contract (2) -------------------------------------------------

    def test_run_returns_dict_with_required_keys_and_types(self):
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(
            set(summary.keys()),
            {"dashboard_path", "findings", "pages_scanned"},
        )
        self.assertIsInstance(summary["dashboard_path"], Path)
        self.assertIsInstance(summary["findings"], list)
        self.assertIsInstance(summary["pages_scanned"], int)
        self.assertEqual(
            summary["dashboard_path"],
            self.wiki / "_dashboards" / "canon_integrity.md",
        )
        self.assertTrue(summary["dashboard_path"].exists())

    def test_finding_dict_shape_explicit(self):
        # Architect minor-note 1: lock the contract via explicit shape assert.
        _make_page(self.wiki / "01-Domain" / "Ready1.md")
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(len(summary["findings"]), 1)
        f = summary["findings"][0]
        self.assertEqual(set(f.keys()), {"page", "category", "reason"})
        self.assertIsInstance(f["page"], str)
        self.assertIsInstance(f["category"], str)
        self.assertIsInstance(f["reason"], str)

    # --- Exit codes (3) ------------------------------------------------------

    def test_exit_0_when_no_findings(self):
        _make_page(
            self.wiki / "01-Domain" / "Clean.md",
            canon_sources=["_sources/raw/x.md"],
        )
        rc = validate_canon_integrity._main(
            self.wiki, stdout=io.StringIO(), stderr=io.StringIO()
        )
        self.assertEqual(rc, 0)

    def test_exit_1_when_findings(self):
        _make_page(self.wiki / "01-Domain" / "Empty.md")
        rc = validate_canon_integrity._main(
            self.wiki, stdout=io.StringIO(), stderr=io.StringIO()
        )
        self.assertEqual(rc, 1)

    def test_exit_2_when_wiki_missing(self):
        nonexistent = self.wiki / "no_such_subdir" / "deeper"
        # Force OS-level failure by passing a path under a missing parent
        # while also removing the wiki to ensure rglob can't materialize.
        shutil.rmtree(self.wiki)
        rc = validate_canon_integrity._main(
            nonexistent, stdout=io.StringIO(), stderr=io.StringIO()
        )
        self.assertEqual(rc, 2)

    # --- Finding categories (5) ----------------------------------------------

    def test_finding_missing_canon_sources_when_field_absent(self):
        _make_page(self.wiki / "01-Domain" / "NoSources.md")
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(len(summary["findings"]), 1)
        self.assertEqual(
            summary["findings"][0]["category"], "missing_canon_sources"
        )
        self.assertEqual(summary["pages_scanned"], 1)

    def test_finding_missing_canon_sources_when_field_empty_list(self):
        _make_page(
            self.wiki / "01-Domain" / "EmptySources.md",
            canon_sources=[],
        )
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(len(summary["findings"]), 1)
        self.assertEqual(
            summary["findings"][0]["category"], "missing_canon_sources"
        )

    def test_no_finding_when_canon_sources_nonempty_and_unverified_empty(self):
        _make_page(
            self.wiki / "01-Domain" / "Clean.md",
            canon_sources=["_sources/raw/x.md"],
            unverified_claims=[],
        )
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(summary["findings"], [])
        self.assertEqual(summary["pages_scanned"], 1)

    def test_finding_unverified_claims_present(self):
        _make_page(
            self.wiki / "01-Domain" / "WithUnverified.md",
            canon_sources=["_sources/raw/x.md"],
            unverified_claims=["claim about Y"],
        )
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(len(summary["findings"]), 1)
        self.assertEqual(
            summary["findings"][0]["category"], "unverified_claims_present"
        )

    def test_both_violations_same_page_emit_two_findings(self):
        _make_page(
            self.wiki / "01-Domain" / "Both.md",
            canon_sources=[],
            unverified_claims=["pending"],
        )
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(len(summary["findings"]), 2)
        cats = sorted(f["category"] for f in summary["findings"])
        self.assertEqual(
            cats,
            ["missing_canon_sources", "unverified_claims_present"],
        )
        # Same page in both findings.
        pages = {f["page"] for f in summary["findings"]}
        self.assertEqual(pages, {"01-Domain/Both.md"})
        self.assertEqual(summary["pages_scanned"], 1)

    # --- Block-list canon_sources seam (dir-20260614qq regression) -----------

    def test_block_list_canon_sources_honored_at_ready(self):
        # The parser->validator seam: a status:ready page whose canon_sources
        # uses BLOCK-style list form (`canon_sources:` then indented `- item`
        # lines) must be HONORED — i.e. produce NO missing_canon_sources
        # finding. Before the frontmatter parser fix (cf9a834) a block-list
        # canon_sources parsed to None, so the validator silently treated a
        # well-sourced page as missing-sources on promotion to ready. This
        # locks that the populated block-list value reaches the validator.
        _make_page_block_canon(
            self.wiki / "01-Domain" / "BlockSourced.md",
            ["_sources/raw/x.md", "_sources/raw/y.md"],
        )
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(summary["pages_scanned"], 1)
        self.assertEqual(
            summary["findings"], [],
            "block-list canon_sources on a ready page must be honored, "
            "not flagged as missing",
        )

    def test_empty_block_canon_sources_flagged_at_ready(self):
        # Companion negative: a bare `canon_sources:` (block form with no
        # items) still parses to None, so a ready page carrying it MUST be
        # flagged missing_canon_sources — the no-source case the gate exists
        # to catch.
        _make_page_block_canon(
            self.wiki / "01-Domain" / "BlockEmpty.md", [],
        )
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(len(summary["findings"]), 1)
        self.assertEqual(
            summary["findings"][0]["category"], "missing_canon_sources"
        )

    # --- Negative-assertion exclusions (2) -----------------------------------

    def test_status_not_ready_excluded_from_both_counters(self):
        # Plant a page with each non-ready status value AND empty canon_sources
        # — they would each trigger a missing_canon_sources finding if scanned.
        for status in ("solid", "outlined", "gap", "draft"):
            _make_page(
                self.wiki / "01-Domain" / (status.capitalize() + "Page.md"),
                status=status,
                canon_sources=[],
                unverified_claims=["x"],
                title=status,
            )
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(
            summary["findings"], [],
            "non-ready pages with empty canon_sources must NOT produce findings",
        )
        self.assertEqual(
            summary["pages_scanned"], 0,
            "pages_scanned must exclude non-ready pages",
        )

    def test_status_missing_or_non_string_excluded_from_both_counters(self):
        # Three exclusion variants: status field omitted, status: null,
        # status: <int>. None should be scanned or flagged.
        _make_page(
            self.wiki / "01-Domain" / "NoStatus.md",
            status=_STATUS_OMIT,
            canon_sources=[],
            unverified_claims=["x"],
        )
        _make_page(
            self.wiki / "01-Domain" / "NullStatus.md",
            status=None,
            canon_sources=[],
            unverified_claims=["x"],
        )
        _make_page(
            self.wiki / "01-Domain" / "IntStatus.md",
            status=5,
            canon_sources=[],
            unverified_claims=["x"],
        )
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(summary["findings"], [])
        self.assertEqual(summary["pages_scanned"], 0)

    # --- Dashboard rendering (7) ---------------------------------------------

    def test_dashboard_fm_shape_five_fields(self):
        validate_canon_integrity.run(self.wiki)
        text = self._read_dashboard()
        fm = frontmatter.parse_frontmatter(text)
        self.assertEqual(fm["title"], "Canon Integrity Dashboard")
        self.assertEqual(fm["type"], "dashboard")
        self.assertEqual(fm["visibility"], "internal")
        self.assertIs(fm["generated"], True)
        self.assertEqual(fm["last_updated"], date.today().isoformat())

    def test_dashboard_summary_lines_use_bold_labels(self):
        _make_page(self.wiki / "01-Domain" / "Empty.md")
        _make_page(
            self.wiki / "01-Domain" / "Clean.md",
            canon_sources=["_sources/raw/x.md"],
        )
        validate_canon_integrity.run(self.wiki)
        text = self._read_dashboard()
        self.assertIn("**Pages scanned:** 2", text)
        self.assertIn("**Findings:** 1", text)

    def test_dashboard_category_grouping_fixed_order(self):
        # Both categories populated → missing_canon_sources H2 must appear
        # before unverified_claims_present H2.
        _make_page(self.wiki / "01-Domain" / "Empty.md")
        _make_page(
            self.wiki / "01-Domain" / "Unver.md",
            canon_sources=["_sources/raw/x.md"],
            unverified_claims=["x"],
        )
        validate_canon_integrity.run(self.wiki)
        text = self._read_dashboard()
        idx_missing = text.find("## missing_canon_sources")
        idx_unver = text.find("## unverified_claims_present")
        self.assertNotEqual(idx_missing, -1)
        self.assertNotEqual(idx_unver, -1)
        self.assertLess(idx_missing, idx_unver)

    def test_empty_category_omitted(self):
        # Only unverified_claims_present populated → missing_canon_sources H2 absent.
        _make_page(
            self.wiki / "01-Domain" / "Unver.md",
            canon_sources=["_sources/raw/x.md"],
            unverified_claims=["x"],
        )
        validate_canon_integrity.run(self.wiki)
        text = self._read_dashboard()
        self.assertIn("## unverified_claims_present", text)
        self.assertNotIn("## missing_canon_sources", text)

    def test_within_category_sort_by_relpath(self):
        _make_page(self.wiki / "02-Other" / "Z_late.md")
        _make_page(self.wiki / "01-Domain" / "A_early.md")
        _make_page(self.wiki / "01-Domain" / "M_mid.md")
        validate_canon_integrity.run(self.wiki)
        text = self._read_dashboard()
        # Each finding bullet starts with "- [[stem]] (rel)"; extract bullet
        # lines under ## missing_canon_sources and check rel order.
        section = text.split("## missing_canon_sources", 1)[1]
        bullets = [ln for ln in section.split("\n") if ln.startswith("- ")]
        rels = []
        for ln in bullets:
            # "- [[<stem>]] (<rel>) — <reason>"
            start = ln.index("(") + 1
            end = ln.index(")", start)
            rels.append(ln[start:end])
        self.assertEqual(
            rels,
            ["01-Domain/A_early.md", "01-Domain/M_mid.md", "02-Other/Z_late.md"],
        )

    def test_dashboard_uses_fwd_slash_paths(self):
        _make_page(self.wiki / "01-Domain" / "Empty.md")
        validate_canon_integrity.run(self.wiki)
        text = self._read_dashboard()
        self.assertIn("01-Domain/Empty.md", text)
        for line in text.split("\n"):
            if line.startswith("- "):
                self.assertNotIn("\\", line)

    def test_dashboard_uses_stem_wikilinks_with_em_dash(self):
        _make_page(self.wiki / "01-Domain" / "Ready1.md")
        validate_canon_integrity.run(self.wiki)
        text = self._read_dashboard()
        self.assertIn(
            "- [[Ready1]] (01-Domain/Ready1.md) — "
            "status:ready page has no canon_sources",
            text,
        )

    # --- Empty body (1) ------------------------------------------------------

    def test_empty_findings_body_line(self):
        # Default fixture has 0 ready pages → 0 findings.
        summary = validate_canon_integrity.run(self.wiki)
        self.assertEqual(summary["pages_scanned"], 0)
        self.assertEqual(summary["findings"], [])
        text = self._read_dashboard()
        self.assertIn("No canon-integrity findings.", text)
        self.assertIn("**Pages scanned:** 0", text)
        self.assertIn("**Findings:** 0", text)


if __name__ == "__main__":
    unittest.main()
