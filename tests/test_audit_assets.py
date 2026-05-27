"""Tests for audit_assets.py (S002 B6 P1)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

import audit_assets  # noqa: E402


class TestAssetsAudit(unittest.TestCase):

    def test_no_heavy_files_no_findings(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets" / "logos").mkdir(parents=True)
            (root / "assets" / "logos" / "small.svg").write_text("<svg/>", encoding="utf-8")
            (root / ".gitignore").write_text("", encoding="utf-8")
            findings = audit_assets.audit(root, threshold=1024)
            self.assertEqual(findings, [])

    def test_heavy_file_above_threshold_detected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets" / "videos").mkdir(parents=True)
            heavy = root / "assets" / "videos" / "big.mp4"
            heavy.write_bytes(b"x" * 2048)
            (root / ".gitignore").write_text("", encoding="utf-8")
            findings = audit_assets.audit(root, threshold=1024)
            self.assertEqual(len(findings), 1)
            self.assertFalse(findings[0].excluded)

    def test_heavy_file_excluded_by_gitignore(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets" / "videos").mkdir(parents=True)
            heavy = root / "assets" / "videos" / "big.mp4"
            heavy.write_bytes(b"x" * 2048)
            (root / ".gitignore").write_text("assets/**/*.mp4\n", encoding="utf-8")
            findings = audit_assets.audit(root, threshold=1024)
            self.assertEqual(len(findings), 1)
            self.assertTrue(findings[0].excluded)


if __name__ == "__main__":
    unittest.main()
