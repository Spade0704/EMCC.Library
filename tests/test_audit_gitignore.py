"""Tests for audit_gitignore.py (S002 B6 P0)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

import audit_gitignore  # noqa: E402


class TestGitignoreAudit(unittest.TestCase):

    def test_missing_gitignore_returns_error(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "wiki.demo").mkdir()
            findings = audit_gitignore.audit(root)
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].rule, "gitignore-missing")

    def test_wiki_local_excluded_no_finding(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "wiki.demo").mkdir()
            (root / ".gitignore").write_text("wiki.*/local/\n", encoding="utf-8")
            findings = audit_gitignore.audit(root)
            self.assertEqual(findings, [])

    def test_wiki_local_not_excluded_flags_error(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "wiki.demo").mkdir()
            (root / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
            findings = audit_gitignore.audit(root)
            self.assertTrue(
                any(f.rule == "wiki-local-not-excluded" for f in findings)
            )

    def test_local_folder_flags_warning_when_not_excluded(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Local").mkdir()
            (root / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
            findings = audit_gitignore.audit(root)
            self.assertTrue(
                any(f.rule == "local-not-excluded" for f in findings)
            )

    def test_heavy_assets_warn_when_no_pattern(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets").mkdir()
            (root / ".gitignore").write_text("# nothing relevant\n", encoding="utf-8")
            findings = audit_gitignore.audit(root)
            self.assertTrue(
                any(f.rule == "heavy-assets-not-excluded" for f in findings)
            )


if __name__ == "__main__":
    unittest.main()
