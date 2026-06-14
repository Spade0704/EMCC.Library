"""Tests for _scripts/audit_citations.py — the runnable citation-PRESENCE audit.

Pins the WIRING + the edge gaps the delta-force gate flagged (whitespace-only
cite_anchor; duplicate-key fail-safe HIGH in both orderings; report-only never
red-bars; a canon-reference desync guard). The lint's own branch logic
(enforce-flip, low-opt-out, fail-closed) is already covered by
tests/test_consequence_lint.py and is NOT re-tested here.
"""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

import audit_citations  # noqa: E402


def _page(root: Path, name: str, body: str) -> Path:
    p = root / name
    p.write_text(body, encoding="utf-8")
    return p


class TestAuditCitations(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_high_page_missing_cite_anchor_is_flagged(self):
        _page(self.root, "p.md", "---\nconsequence: high\n---\nbody\n")
        findings = audit_citations.audit_citations(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].consequence, "high")
        self.assertEqual(findings[0].severity, "warning")  # report-only default

    def test_high_page_with_cite_anchor_is_clean(self):
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "FCTM AEP §1"\n---\nbody\n')
        self.assertEqual(audit_citations.audit_citations(self.root), [])

    def test_consequence_low_opts_out(self):
        _page(self.root, "p.md", "---\nconsequence: low\n---\nbody\n")
        self.assertEqual(audit_citations.audit_citations(self.root), [])

    def test_whitespace_only_cite_anchor_treated_empty(self):
        # a cite_anchor of only spaces must NOT satisfy the HIGH requirement
        _page(self.root, "p.md",
              '---\nconsequence: high\ncite_anchor: "   "\n---\nbody\n')
        findings = audit_citations.audit_citations(self.root)
        self.assertEqual(len(findings), 1)

    def test_duplicate_consequence_key_failsafe_high_low_then_high(self):
        _page(self.root, "p.md",
              "---\nconsequence: low\nconsequence: high\n---\nbody\n")
        findings = audit_citations.audit_citations(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].consequence, "high")

    def test_duplicate_consequence_key_failsafe_high_high_then_low(self):
        # the dangerous ordering: a trailing `low` must NOT flip a HIGH page
        _page(self.root, "p.md",
              "---\nconsequence: high\nconsequence: low\n---\nbody\n")
        findings = audit_citations.audit_citations(self.root)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].consequence, "high")

    def test_report_only_run_never_red_bars(self):
        _page(self.root, "p.md", "---\nconsequence: high\n---\nbody\n")
        rc = audit_citations.main(["--wiki-root", str(self.root)])
        self.assertEqual(rc, 0)

    def test_enforce_run_exits_1_on_missing_cite(self):
        _page(self.root, "p.md", "---\nconsequence: high\n---\nbody\n")
        rc = audit_citations.main(["--wiki-root", str(self.root), "--enforce"])
        self.assertEqual(rc, 1)

    def test_enforce_run_exits_0_when_clean(self):
        _page(self.root, "p.md",
              '---\nconsequence: low\n---\nbody\n')
        rc = audit_citations.main(["--wiki-root", str(self.root), "--enforce"])
        self.assertEqual(rc, 0)

    def test_underscore_dirs_skipped(self):
        # iter_content_pages skips _-prefixed dirs; a HIGH page there is not audited
        d = self.root / "_archive"
        d.mkdir()
        _page(d, "p.md", "---\nconsequence: high\n---\nbody\n")
        self.assertEqual(audit_citations.audit_citations(self.root), [])


class TestRunWrapper(unittest.TestCase):
    """The orchestrator entry-point: report-only, writes its own dashboard,
    returns a dict, never red-bars."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_run_returns_dict_and_writes_dashboard(self):
        _page(self.root, "high_missing.md",
              "---\nconsequence: high\ncite_anchor: \"\"\n---\nbody\n")
        out = audit_citations.run(self.root)
        self.assertIn("findings", out)
        self.assertIn("dashboard_path", out)
        self.assertEqual(out["findings_count"], len(out["findings"]))
        dash = out["dashboard_path"]
        self.assertTrue(dash.is_file())
        text = dash.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---"))  # 5-field dashboard fm header
        self.assertIn("Presence-Not-Accuracy", text)

    def test_run_is_report_only_findings_are_warnings(self):
        # run() forces enforce=False — a HIGH-without-cite is a warning, never
        # an error, so it can never red-bar the orchestrator pass.
        _page(self.root, "high_missing.md",
              "---\nconsequence: high\ncite_anchor: \"\"\n---\nbody\n")
        out = audit_citations.run(self.root)
        self.assertTrue(out["findings"])
        self.assertTrue(all(f["severity"] == "warning" for f in out["findings"]))


class TestCanonDocumentsTheContract(unittest.TestCase):
    """Desync guard: the canon must name the real fields the lint reads, so a
    future rename can't silently drift the doc away from the code."""

    def test_frontmatter_schema_names_the_fields(self):
        schema = (REPO_ROOT / "wiki.codex" / "git" / "01-Architecture"
                  / "Frontmatter-Schema.md").read_text(encoding="utf-8")
        self.assertIn("consequence", schema)
        self.assertIn("cite_anchor", schema)
        self.assertIn("Presence-Not-Accuracy", schema)


if __name__ == "__main__":
    unittest.main()
