"""Tests for audit_doc_pairing.py (S002 B6 P0)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

import audit_doc_pairing  # noqa: E402


def _make_project(root: Path, *, automations=(), doc_folders=()):
    """Materialize a synthetic project root with given automations + doc folders."""
    (root / "Biz.Automation").mkdir(parents=True, exist_ok=True)
    for name in automations:
        (root / "Biz.Automation" / name).mkdir(parents=True, exist_ok=True)
    wiki_git = root / "wiki.demo" / "git"
    wiki_git.mkdir(parents=True, exist_ok=True)
    for name in doc_folders:
        (wiki_git / (name + ".doc")).mkdir(parents=True, exist_ok=True)


class TestPairingAuditHappyPath(unittest.TestCase):
    def test_all_paired_returns_empty(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_project(root, automations=["foo", "bar"], doc_folders=["foo", "bar"])
            findings = audit_doc_pairing.audit(root)
            self.assertEqual(findings, [])


class TestPairingAuditFindings(unittest.TestCase):
    def test_unpaired_automation_detected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_project(root, automations=["foo"], doc_folders=[])
            findings = audit_doc_pairing.audit(root)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "unpaired-automation")

    def test_orphan_doc_folder_detected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_project(root, automations=[], doc_folders=["orphan"])
            findings = audit_doc_pairing.audit(root)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].kind, "orphan-doc-folder")

    def test_wikisys_subfolder_not_treated_as_automation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_project(root, automations=[], doc_folders=[])
            (root / "Biz.Automation" / "wikisys.demo").mkdir(parents=True)
            findings = audit_doc_pairing.audit(root)
            self.assertEqual(findings, [])


class TestPairingAuditDashboard(unittest.TestCase):
    def test_render_dashboard_clean(self):
        out = audit_doc_pairing.render_dashboard([], Path("."))
        self.assertIn("All automations paired", out)

    def test_render_dashboard_with_findings(self):
        f = audit_doc_pairing.Finding(
            kind="unpaired-automation",
            path="Biz.Automation/foo",
            suggested_pair="wiki.demo/git/foo.doc",
        )
        out = audit_doc_pairing.render_dashboard([f], Path("."))
        self.assertIn("unpaired-automation", out)
        self.assertIn("foo.doc", out)


if __name__ == "__main__":
    unittest.main()
