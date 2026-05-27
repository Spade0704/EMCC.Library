"""Tests for audit_local_split.py (S002 B6 P1)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

import audit_local_split  # noqa: E402


def _make_wiki(root: Path, *, git_pages=None, local_pages=None,
               forbidden_terms=None):
    """Materialize a synthetic wiki + wikisys with optional forbidden terms."""
    git_pages = git_pages or {}
    local_pages = local_pages or {}
    forbidden_terms = forbidden_terms or []
    wiki_git = root / "wiki.demo" / "git"
    wiki_local = root / "wiki.demo" / "local"
    wiki_git.mkdir(parents=True, exist_ok=True)
    wiki_local.mkdir(parents=True, exist_ok=True)
    for name, content in git_pages.items():
        (wiki_git / name).write_text(content, encoding="utf-8")
    for name, content in local_pages.items():
        (wiki_local / name).write_text(content, encoding="utf-8")
    if forbidden_terms:
        cfg = root / "Biz.Automation" / "wikisys.demo" / "_config"
        cfg.mkdir(parents=True, exist_ok=True)
        body = "forbidden_terms:\n"
        for t in forbidden_terms:
            body += "  - term: " + t + "\n    severity: warn\n"
        (cfg / "forbidden_terms.yaml").write_text(body, encoding="utf-8")


class TestLocalSplitAudit(unittest.TestCase):

    def test_no_wiki_no_findings(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            findings = audit_local_split.audit(root)
            self.assertEqual(findings, [])

    def test_forbidden_term_in_git_flags_leak(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_wiki(
                root,
                git_pages={"page.md": "This mentions ScoriaPrime in body"},
                local_pages={},
                forbidden_terms=["ScoriaPrime"],
            )
            findings = audit_local_split.audit(root)
            self.assertTrue(any(
                f.suspect_type == "private-leak-in-git" for f in findings
            ))

    def test_no_forbidden_term_no_leak(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_wiki(
                root,
                git_pages={"clean.md": "Public content only"},
                local_pages={},
                forbidden_terms=["ScoriaPrime"],
            )
            leak_findings = [
                f for f in audit_local_split.audit(root)
                if f.suspect_type == "private-leak-in-git"
            ]
            self.assertEqual(leak_findings, [])


if __name__ == "__main__":
    unittest.main()
