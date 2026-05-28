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


class TestStalePathSweep(unittest.TestCase):
    """OBS-1: AC12 stale-path sweep with explicit allow-list."""

    def _project(self, root):
        (root / "Biz.Automation" / "wikisys.demo").mkdir(parents=True, exist_ok=True)
        (root / "wiki.demo" / "git").mkdir(parents=True, exist_ok=True)

    def test_detects_stale_pattern_in_non_allowlisted_file(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root)
            page = root / "wiki.demo" / "git" / "page.md"
            page.write_text("see Sources/Raw/foo.md for details\n", encoding="utf-8")
            findings = audit_doc_pairing.audit_stale_paths(root)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].pattern, "Sources/Raw")
            self.assertEqual(findings[0].path, "wiki.demo/git/page.md")
            self.assertEqual(findings[0].line, 1)

    def test_allowlisted_file_is_skipped(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root)
            (root / "MIGRATION-ISSUES.md").write_text(
                "documents/codex/ moved\n", encoding="utf-8")
            self.assertEqual(audit_doc_pairing.audit_stale_paths(root), [])

    def test_clean_tree_returns_empty(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root)
            (root / "wiki.demo" / "git" / "ok.md").write_text(
                "wiki.codex/git/raw is current\n", encoding="utf-8")
            self.assertEqual(audit_doc_pairing.audit_stale_paths(root), [])

    def test_skip_dirs_excluded(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root)
            gen = root / "wiki.demo" / "git" / "_dashboards"
            gen.mkdir(parents=True)
            (gen / "old.md").write_text("Sources/Raw\n", encoding="utf-8")
            local = root / "wiki.demo" / "local"
            local.mkdir(parents=True)
            (local / "note.md").write_text("Sources/Raw\n", encoding="utf-8")
            self.assertEqual(audit_doc_pairing.audit_stale_paths(root), [])

    def test_config_override_honored(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._project(root)
            cfg = root / "Biz.Automation" / "wikisys.demo" / "_config"
            cfg.mkdir(parents=True)
            (cfg / "stale_paths.yaml").write_text(
                "patterns:\n  - \"OLD_THING\"\nallowlist:\n  - \"safe.md\"\n",
                encoding="utf-8")
            (root / "wiki.demo" / "git" / "p.md").write_text(
                "OLD_THING here; Sources/Raw not flagged now\n", encoding="utf-8")
            (root / "safe.md").write_text("OLD_THING\n", encoding="utf-8")
            findings = audit_doc_pairing.audit_stale_paths(root)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].pattern, "OLD_THING")

    def test_render_stale_dashboard_clean_and_findings(self):
        clean = audit_doc_pairing.render_stale_dashboard([])
        self.assertIn("No stale path references", clean)
        f = audit_doc_pairing.StalePathFinding(
            path="x.md", line=3, pattern="Sources/Raw", snippet="see Sources/Raw")
        out = audit_doc_pairing.render_stale_dashboard([f])
        self.assertIn("Sources/Raw", out)
        self.assertIn("x.md", out)


class TestStalePathRepoGuard(unittest.TestCase):
    """The committed repo must have 0 un-allowlisted stale-path references."""

    def test_repo_is_clean(self):
        findings = audit_doc_pairing.audit_stale_paths(REPO_ROOT)
        self.assertEqual(
            findings, [],
            "stale path reference(s) outside the allow-list: {}".format(
                [(f.path, f.line, f.pattern) for f in findings]))


if __name__ == "__main__":
    unittest.main()
