"""Tests for _scripts/check_framework_briefing_sync.py — P11 staleness validator."""

import io
import os
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import check_framework_briefing_sync


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


def _clone_fixture(dst: Path) -> Path:
    shutil.copytree(FIXTURE_ROOT, dst)
    return dst


def _write_page(wiki: Path, rel: str, fm_lines: list, body: str = "") -> Path:
    """Write a markdown page with the given fm lines + body."""
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body
    path.write_text(content, encoding="utf-8")
    return path


def _set_mtime(p: Path, t: float) -> None:
    os.utime(p, (t, t))


class HappyPathTests(unittest.TestCase):

    def test_no_findings_when_framework_fresh_with_briefing(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            fp = _write_page(wiki, "01-Domain/Framework1.md", [
                'title: "Framework One"',
                "type: framework",
                "visibility: internal",
                'public_pair: "public/Briefing1.md"',
            ], body="# Framework body\n")
            bp = _write_page(wiki, "public/Briefing1.md", [
                'title: "Briefing One"',
                "type: reference",
                "visibility: public",
            ], body="# Briefing body\n")
            # Equal mtimes -> fresh.
            _set_mtime(fp, 1_000_000)
            _set_mtime(bp, 1_000_000)
            out = check_framework_briefing_sync.run(wiki)
            self.assertEqual(out["findings"], [])
            self.assertEqual(out["frameworks_scanned"], 1)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No framework-briefing-sync findings.", body)


class SeverityErrorTests(unittest.TestCase):

    def test_public_pair_path_missing(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/FrameworkX.md", [
                'title: "Framework X"',
                "type: framework",
                "visibility: internal",
                'public_pair: "public/Nonexistent.md"',
            ])
            out = check_framework_briefing_sync.run(wiki)
            self.assertEqual(len(out["findings"]), 1)
            f = out["findings"][0]
            self.assertEqual(f["severity"], "error")
            self.assertEqual(f["framework_path"], "01-Domain/FrameworkX.md")
            self.assertEqual(f["public_pair_path"], "public/Nonexistent.md")
            self.assertEqual(f["reason"], check_framework_briefing_sync.REASON_PAIR_MISSING)


class SeverityWarningTests(unittest.TestCase):

    def test_framework_newer_than_briefing(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            fp = _write_page(wiki, "01-Domain/FrameworkY.md", [
                'title: "Framework Y"',
                "type: framework",
                'public_pair: "public/BriefingY.md"',
            ])
            bp = _write_page(wiki, "public/BriefingY.md", [
                'title: "Briefing Y"',
                "type: reference",
            ])
            # Framework newer -> stale briefing.
            _set_mtime(bp, 1_000_000)
            _set_mtime(fp, 2_000_000)
            out = check_framework_briefing_sync.run(wiki)
            self.assertEqual(len(out["findings"]), 1)
            f = out["findings"][0]
            self.assertEqual(f["severity"], "warning")
            self.assertEqual(f["reason"], check_framework_briefing_sync.REASON_STALE_BRIEFING)


class SeverityInfoTests(unittest.TestCase):

    def test_briefing_newer_than_framework(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            fp = _write_page(wiki, "01-Domain/FrameworkZ.md", [
                'title: "Framework Z"',
                "type: framework",
                'public_pair: "public/BriefingZ.md"',
            ])
            bp = _write_page(wiki, "public/BriefingZ.md", [
                'title: "Briefing Z"',
                "type: reference",
            ])
            # Briefing newer -> reverse cascade.
            _set_mtime(fp, 1_000_000)
            _set_mtime(bp, 2_000_000)
            out = check_framework_briefing_sync.run(wiki)
            self.assertEqual(len(out["findings"]), 1)
            f = out["findings"][0]
            self.assertEqual(f["severity"], "info")
            self.assertEqual(f["reason"], check_framework_briefing_sync.REASON_REVERSE_CASCADE)


class PageWalkFilterTests(unittest.TestCase):

    def test_non_framework_pages_skipped(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/NotFramework.md", [
                'title: "Reference page"',
                "type: reference",
                'public_pair: "public/SomeBriefing.md"',
            ])
            out = check_framework_briefing_sync.run(wiki)
            # Non-framework page must not be scanned; no findings from it.
            self.assertEqual(out["frameworks_scanned"], 0)
            self.assertEqual(out["findings"], [])

    def test_framework_with_null_public_pair_skipped(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/FrameworkNull.md", [
                'title: "Framework Null"',
                "type: framework",
                "public_pair: null",
            ])
            out = check_framework_briefing_sync.run(wiki)
            self.assertEqual(out["frameworks_scanned"], 0)
            self.assertEqual(out["findings"], [])

    def test_framework_with_missing_public_pair_key_skipped(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/FrameworkNoKey.md", [
                'title: "Framework No Key"',
                "type: framework",
            ])
            out = check_framework_briefing_sync.run(wiki)
            self.assertEqual(out["frameworks_scanned"], 0)
            self.assertEqual(out["findings"], [])

    def test_page_with_no_frontmatter_skipped(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "01-Domain" / "NoFm.md").write_text(
                "# Just a body, no frontmatter at all\n", encoding="utf-8"
            )
            out = check_framework_briefing_sync.run(wiki)
            # NoFm.md must not be scanned; fixture pages have type:framework
            # but no public_pair, so they're skipped too -> 0 scanned.
            self.assertEqual(out["frameworks_scanned"], 0)


class EmptyWikiTests(unittest.TestCase):

    def test_zero_framework_pages_returns_empty(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            wiki.mkdir()
            (wiki / "_dashboards").mkdir()
            out = check_framework_briefing_sync.run(wiki)
            self.assertEqual(out["findings"], [])
            self.assertEqual(out["frameworks_scanned"], 0)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No framework-briefing-sync findings.", body)


class CliExitCodesTests(unittest.TestCase):

    def test_exit_zero_clean(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            stdout, stderr = io.StringIO(), io.StringIO()
            rc = check_framework_briefing_sync._main(
                wiki, stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 0)
            self.assertIn("framework_briefing_sync:", stdout.getvalue())

    def test_exit_one_findings(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/FrameworkBroken.md", [
                'title: "Framework Broken"',
                "type: framework",
                'public_pair: "public/Nope.md"',
            ])
            stdout, stderr = io.StringIO(), io.StringIO()
            rc = check_framework_briefing_sync._main(
                wiki, stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 1)
            self.assertIn("error: 01-Domain/FrameworkBroken.md", stdout.getvalue())

    def test_exit_two_script_error(self):
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_such_wiki"
            stdout, stderr = io.StringIO(), io.StringIO()
            rc = check_framework_briefing_sync._main(
                missing, stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr.getvalue())


class DashboardFormatPinTests(unittest.TestCase):

    def test_byte_identical_to_legacy_format(self):
        # Pin fm header + headline format string at unit scope (T6 R1
        # mitigation discipline carry-forward). Edit only with paired
        # check_framework_briefing_sync format change.
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            wiki.mkdir()
            (wiki / "_dashboards").mkdir()
            out = check_framework_briefing_sync.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            lines = body.split("\n")
            self.assertEqual(lines[0], "---")
            self.assertEqual(lines[1], 'title: "Framework ↔ Briefing Sync Dashboard"')
            self.assertEqual(lines[2], "type: dashboard")
            self.assertEqual(lines[3], "visibility: internal")
            self.assertEqual(lines[4], "generated: true")
            self.assertTrue(lines[5].startswith("last_updated: "))
            self.assertEqual(lines[6], "---")
            self.assertEqual(lines[7], "")
            self.assertTrue(lines[8].startswith("# Framework ↔ Briefing Sync — "))


if __name__ == "__main__":
    unittest.main()
