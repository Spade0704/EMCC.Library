"""Tests for _scripts/build_caution_index.py — the deterministic tiered caution-index.

The safety-path script absorbed from EMCC.Gateway (Cairn-absorption item 2).
The council-LOCKED definition-of-done is the ambiguity-refuse/escalate default:
an ambiguous HIGH page MUST escalate (no caution text, point at source) — it
must NEVER guess or substitute a caution. These tests pin that, plus the
verbatim-copy contract and the deterministic-only posture.

The underlying consequence resolver's branch logic (fail-safe HIGH, low-opt-out,
duplicate-key, fail-closed-on-unreadable) is covered by test_consequence_lint.py
and is NOT re-tested here — these pin the caution-index layer over it.
"""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

import build_caution_index as bci  # noqa: E402


def _page(root: Path, name: str, body: str) -> Path:
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


def _rows_by_path(rows):
    return {r.path: r for r in rows}


class TestSurfacing(unittest.TestCase):
    """A HIGH page with a usable cite_anchor AND a non-empty verbatim caution
    block surfaces — caution text copied byte-for-byte."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_high_with_cite_and_caution_is_surfaced(self):
        caution = "> [!CAUTION] Do not exceed 250 KIAS below 10,000 ft."
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "FCTM AEP §1"\n---\n'
              f"intro\n\n{caution}\n")
        rows = bci.build_caution_index(self.root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status, "surfaced")
        self.assertEqual(rows[0].cite_anchor, "FCTM AEP §1")
        self.assertEqual(len(rows[0].cautions), 1)

    def test_surfaced_caution_is_verbatim(self):
        # the surfaced caution must be a byte-for-byte slice of the source line
        caution = "> [!WARNING] Torque limit 100% — MSN 1234 only."
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "ref"\n---\n'
              f"x\n\n{caution}\n")
        rows = bci.build_caution_index(self.root)
        self.assertEqual(rows[0].cautions[0], caution)  # exact, no paraphrase

    def test_multi_line_blockquote_caution_extends_verbatim(self):
        block = ("> [!DANGER] Engine failure before V1:\n"
                 "> reject the takeoff immediately.")
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "ref"\n---\n'
              f"x\n\n{block}\n\nmore prose\n")
        rows = bci.build_caution_index(self.root)
        self.assertEqual(rows[0].status, "surfaced")
        self.assertEqual(rows[0].cautions[0], block)  # both lines, verbatim

    def test_low_page_is_skipped_entirely(self):
        _page(self.root, "p.md",
              "---\nconsequence: low\n---\n> [!CAUTION] ignored on a LOW page\n")
        self.assertEqual(bci.build_caution_index(self.root), [])

    def test_caution_inside_code_fence_is_not_surfaced(self):
        # a marker inside a fenced example is documentation, not a live caution
        body = ("---\nconsequence: high\ncite_anchor: \"ref\"\n---\n"
                "```\n> [!CAUTION] this is an example, not a real caution\n```\n")
        _page(self.root, "p.md", body)
        rows = bci.build_caution_index(self.root)
        # cite present but no REAL caution block -> escalate (case 3)
        self.assertEqual(rows[0].status, "escalate")


class TestAmbiguityRefuse(unittest.TestCase):
    """COUNCIL-LOCKED definition-of-done: ambiguity MUST escalate, never guess."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_high_without_cite_escalates_with_no_caution(self):
        # case 1: a HIGH page with no cite_anchor cannot anchor a verbatim
        # caution -> ESCALATE, and crucially carries NO caution text.
        _page(self.root, "p.md",
              "---\nconsequence: high\n---\n> [!CAUTION] 250 KIAS limit.\n")
        rows = bci.build_caution_index(self.root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status, "escalate")
        self.assertEqual(rows[0].cautions, [])  # refuses to surface caution text
        self.assertIn("cite_anchor", rows[0].reason)

    def test_failsafe_high_escalates(self):
        # case 2: consequence absent -> resolver fail-safes to HIGH, but the
        # author never affirmed it -> unverifiable -> ESCALATE (no caution).
        _page(self.root, "p.md",
              '---\ncite_anchor: "ref"\n---\n> [!CAUTION] surprise.\n')
        rows = bci.build_caution_index(self.root)
        self.assertEqual(rows[0].status, "escalate")
        self.assertEqual(rows[0].cautions, [])

    def test_duplicate_consequence_key_escalates(self):
        # the dangerous ordering: a trailing `low` must NOT flip a HIGH page;
        # the resolver fail-safes HIGH with field_present=False -> ESCALATE.
        _page(self.root, "p.md",
              '---\nconsequence: high\nconsequence: low\ncite_anchor: "ref"\n---\n'
              "> [!CAUTION] x.\n")
        rows = bci.build_caution_index(self.root)
        self.assertEqual(rows[0].status, "escalate")
        self.assertEqual(rows[0].cautions, [])

    def test_noncanonical_marker_format_escalates_not_surfaces(self):
        # fail-closed-on-format: a doubled-space marker `>  [!CAUTION]` is NOT
        # the canonical `> [!CAUTION]` -> the router does NOT recognise it and
        # ESCALATEs (the safe direction) rather than surfacing a caution it is
        # not confident about. Surfacing only happens on an exact marker match.
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "ref"\n---\n'
              ">  [!CAUTION]  flaps limit.\n")
        rows = bci.build_caution_index(self.root)
        self.assertEqual(rows[0].status, "escalate")
        self.assertEqual(rows[0].cautions, [])

    def test_high_with_cite_but_empty_caution_escalates(self):
        # case 3: a bare marker with no following text is an EMPTY caution —
        # declares danger, surfaces nothing -> ESCALATE rather than surface a
        # content-free row that looks authoritative.
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "ref"\n---\n> [!CAUTION]\n')
        rows = bci.build_caution_index(self.root)
        self.assertEqual(rows[0].status, "escalate")
        self.assertEqual(rows[0].cautions, [])

    def test_ambiguous_shared_keyword_lists_all_never_picks_one(self):
        # THE critical council test: when two HIGH pages cover the same hazard
        # ("Torque-Limit" for two MSN ranges), the index lists BOTH as separate
        # rows (honest multiplicity) and NEVER collapses or picks one. Here both
        # are cite-less HIGH -> both escalate to source. The router made no
        # choice; the reader resolves the right variant from the full source.
        _page(self.root, "Torque-Limit-MSN-A.md",
              "---\nconsequence: high\n---\n> [!CAUTION] torque limit 100%.\n")
        _page(self.root, "Torque-Limit-MSN-B.md",
              "---\nconsequence: high\n---\n> [!CAUTION] torque limit 95%.\n")
        rows = bci.build_caution_index(self.root)
        self.assertEqual(len(rows), 2)  # NOT collapsed to one
        self.assertTrue(all(r.status == "escalate" for r in rows))
        self.assertTrue(all(r.cautions == [] for r in rows))  # no caution guessed
        # both are surfaced as distinct source pointers — grep over the index
        # for the shared routing term returns BOTH, never one picked answer.
        for r in rows:
            self.assertIn("torque", r.keywords)  # deterministic key from the page path
            self.assertIn("limit", r.keywords)
        self.assertEqual(
            {r.path for r in rows},
            {"Torque-Limit-MSN-A.md", "Torque-Limit-MSN-B.md"},
        )


class TestDeterminism(unittest.TestCase):
    """No non-deterministic component may enter the safety path. Identical
    input -> byte-identical output, every run."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_repeated_runs_identical(self):
        _page(self.root, "a.md",
              '---\nconsequence: high\ncite_anchor: "r1"\n---\n> [!CAUTION] aaa.\n')
        _page(self.root, "b.md",
              "---\nconsequence: high\n---\n> [!CAUTION] bbb.\n")
        d1 = bci.render_dashboard(bci.build_caution_index(self.root), self.root, False)
        d2 = bci.render_dashboard(bci.build_caution_index(self.root), self.root, False)
        self.assertEqual(d1, d2)


class TestCLIAndRun(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_report_only_run_never_red_bars(self):
        _page(self.root, "p.md", "---\nconsequence: high\n---\n> [!CAUTION] x.\n")
        rc = bci.main(["--wiki-root", str(self.root)])
        self.assertEqual(rc, 0)

    def test_enforce_exits_1_on_escalation(self):
        # an unresolved HIGH (escalate) fails an --enforce run
        _page(self.root, "p.md", "---\nconsequence: high\n---\n> [!CAUTION] x.\n")
        rc = bci.main(["--wiki-root", str(self.root), "--enforce"])
        self.assertEqual(rc, 1)

    def test_enforce_exits_0_when_all_surfaced(self):
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "ref"\n---\n> [!CAUTION] x.\n')
        rc = bci.main(["--wiki-root", str(self.root), "--enforce"])
        self.assertEqual(rc, 0)

    def test_no_content_root_exits_2(self):
        rc = bci.main(["--wiki-root", str(self.root / "does-not-exist")])
        self.assertEqual(rc, 2)

    def test_run_returns_dict_and_writes_dashboard(self):
        _page(self.root, "surf.md",
              '---\nconsequence: high\ncite_anchor: "ref"\n---\n> [!CAUTION] x.\n')
        _page(self.root, "esc.md", "---\nconsequence: high\n---\n> [!CAUTION] y.\n")
        out = bci.run(self.root)
        self.assertEqual(out["rows_count"], 2)
        self.assertEqual(out["surfaced_count"], 1)
        self.assertEqual(out["escalate_count"], 1)
        dash = out["dashboard_path"]
        self.assertTrue(dash.is_file())
        text = dash.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---"))  # dashboard fm header
        self.assertIn("Presence-Not-Accuracy", text)
        self.assertIn("fail-closed", text.lower())

    def test_run_is_report_only_escalate_does_not_raise(self):
        _page(self.root, "esc.md", "---\nconsequence: high\n---\n> [!CAUTION] y.\n")
        out = bci.run(self.root)  # must not raise
        self.assertEqual(out["escalate_count"], 1)

    def test_underscore_dirs_skipped(self):
        d = self.root / "_archive"
        d.mkdir()
        _page(d, "p.md",
              '---\nconsequence: high\ncite_anchor: "r"\n---\n> [!CAUTION] x.\n')
        self.assertEqual(bci.build_caution_index(self.root), [])


class TestTableSafety(unittest.TestCase):
    """A verbatim caution containing a pipe must not break the markdown table
    (the surfaced text stays in one cell, visually intact)."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_pipe_in_caution_is_escaped_not_dropped(self):
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "ref"\n---\n'
              "> [!CAUTION] flaps 1 | 5 | 15 only.\n")
        out = bci.run(self.root)
        text = out["dashboard_path"].read_text(encoding="utf-8")
        self.assertIn("flaps 1 \\| 5 \\| 15 only", text)


class TestCanonDocumentsTheContract(unittest.TestCase):
    """Desync guard: the canon must name the deterministic + fail-closed
    contract so a future change can't silently drift the doc from the code."""

    def test_build_spec_documents_caution_index(self):
        spec = (REPO_ROOT / "wiki.codex" / "git" / "codex"
                / "PROJECT_WIKI_BUILD_SPEC.md").read_text(encoding="utf-8")
        self.assertIn("build_caution_index.py", spec)
        self.assertIn("caution_index.md", spec)
        self.assertIn("Escalate", spec)
        # both kill-constraints must be named in canon
        self.assertIn("no neural picker", spec.lower())
        self.assertIn("ambiguity-refuse", spec.lower())


if __name__ == "__main__":
    unittest.main()
