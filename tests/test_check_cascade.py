"""Tests for _scripts/check_cascade.py — P10 cascade-staleness validator."""

import io
import os
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import check_cascade
from _lib import frontmatter


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


def _clone_fixture(dst: Path) -> Path:
    """Clone the fixture wiki to dst. Returns the cloned wiki root."""
    shutil.copytree(FIXTURE_ROOT, dst)
    return dst


def _write_cascade_map(wiki_root: Path, body: str) -> None:
    """Overwrite the wiki's _config/cascade_map.yaml with `body`."""
    (wiki_root / "_config" / "cascade_map.yaml").write_text(
        body, encoding="utf-8"
    )


def _set_mtime(p: Path, t: float) -> None:
    """Force atime+mtime to `t` (epoch float)."""
    os.utime(p, (t, t))


class HappyPathTests(unittest.TestCase):

    def test_no_findings_when_derived_fresh(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_cascade_map(wiki, (
                "pairs:\n"
                "  - source: 01-Domain/Foo.md\n"
                "    derived: 01-Domain/Bar.md\n"
            ))
            # Force derived newer than source.
            _set_mtime(wiki / "01-Domain" / "Foo.md", 1_000_000)
            _set_mtime(wiki / "01-Domain" / "Bar.md", 2_000_000)
            out = check_cascade.run(wiki)
            self.assertEqual(out["findings"], [])
            self.assertEqual(out["pairs_scanned"], 1)
            self.assertTrue(out["dashboard_path"].exists())
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No cascade staleness findings.", body)


class SeverityErrorTests(unittest.TestCase):

    def test_cascade_map_source_missing(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_cascade_map(wiki, (
                "pairs:\n"
                "  - source: 01-Domain/Nonexistent.md\n"
                "    derived: 01-Domain/Foo.md\n"
            ))
            out = check_cascade.run(wiki)
            self.assertEqual(len(out["findings"]), 1)
            f = out["findings"][0]
            self.assertEqual(f["severity"], "error")
            self.assertEqual(f["source_path"], "01-Domain/Nonexistent.md")
            self.assertEqual(f["derived_path"], "01-Domain/Foo.md")
            self.assertEqual(f["reason"], check_cascade.REASON_SOURCE_MISSING)


class SeverityWarningTests(unittest.TestCase):

    def test_derived_missing_when_source_exists(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_cascade_map(wiki, (
                "pairs:\n"
                "  - source: 01-Domain/Foo.md\n"
                "    derived: 01-Domain/Nonexistent.md\n"
            ))
            out = check_cascade.run(wiki)
            self.assertEqual(len(out["findings"]), 1)
            f = out["findings"][0]
            self.assertEqual(f["severity"], "warning")
            self.assertEqual(f["source_path"], "01-Domain/Foo.md")
            self.assertEqual(f["derived_path"], "01-Domain/Nonexistent.md")
            self.assertEqual(f["reason"], check_cascade.REASON_DERIVED_MISSING)


class SeverityInfoTests(unittest.TestCase):

    def test_stale_derived(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_cascade_map(wiki, (
                "pairs:\n"
                "  - source: 01-Domain/Foo.md\n"
                "    derived: 01-Domain/Bar.md\n"
            ))
            # Force source newer than derived.
            _set_mtime(wiki / "01-Domain" / "Bar.md", 1_000_000)
            _set_mtime(wiki / "01-Domain" / "Foo.md", 2_000_000)
            out = check_cascade.run(wiki)
            self.assertEqual(len(out["findings"]), 1)
            f = out["findings"][0]
            self.assertEqual(f["severity"], "info")
            self.assertEqual(f["source_path"], "01-Domain/Foo.md")
            self.assertEqual(f["derived_path"], "01-Domain/Bar.md")
            self.assertEqual(f["reason"], check_cascade.REASON_STALE)


class MissingConfigTests(unittest.TestCase):

    def test_no_cascade_map_yaml(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "_config" / "cascade_map.yaml").unlink()
            out = check_cascade.run(wiki)
            self.assertEqual(out["findings"], [])
            self.assertEqual(out["pairs_scanned"], 0)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No cascade staleness findings.", body)

    def test_empty_pairs_list(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_cascade_map(wiki, "pairs:\n")
            out = check_cascade.run(wiki)
            self.assertEqual(out["findings"], [])
            self.assertEqual(out["pairs_scanned"], 0)


class MalformedYamlTests(unittest.TestCase):

    def test_config_yaml_error_propagates(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Indented content with no top-level key on the first non-comment
            # line — _parse_config_yaml raises ConfigYamlError per its contract.
            _write_cascade_map(wiki, "  indented_with_no_key: oops\n")
            with self.assertRaises(frontmatter.ConfigYamlError):
                check_cascade.run(wiki)


class CliExitCodesTests(unittest.TestCase):

    def test_exit_zero_clean(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_cascade_map(wiki, "pairs:\n")
            stdout, stderr = io.StringIO(), io.StringIO()
            rc = check_cascade._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 0)
            self.assertIn("cascade:", stdout.getvalue())

    def test_exit_one_findings(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_cascade_map(wiki, (
                "pairs:\n"
                "  - source: 01-Domain/Nonexistent.md\n"
                "    derived: 01-Domain/Foo.md\n"
            ))
            stdout, stderr = io.StringIO(), io.StringIO()
            rc = check_cascade._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 1)
            self.assertIn("error: 01-Domain/Nonexistent.md", stdout.getvalue())

    def test_exit_two_script_error(self):
        with TemporaryDirectory() as tmp:
            # Pass a non-existent wiki_root.
            missing = Path(tmp) / "no_such_wiki"
            stdout, stderr = io.StringIO(), io.StringIO()
            rc = check_cascade._main(missing, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr.getvalue())


class DashboardFormatPinTests(unittest.TestCase):

    def test_byte_identical_to_legacy_format(self):
        # Pin the fm header + headline format string at unit scope.
        # Carry-forward of T6 R1 mitigation discipline. If render_fm_header
        # output OR the headline format string drifts, this test catches
        # it before AC3 runtime golden-compare. Edit only with paired
        # check_cascade format change.
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_cascade_map(wiki, "pairs:\n")
            out = check_cascade.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            lines = body.split("\n")
            self.assertEqual(lines[0], "---")
            self.assertEqual(lines[1], 'title: "Cascade Staleness Dashboard"')
            self.assertEqual(lines[2], "type: dashboard")
            self.assertEqual(lines[3], "visibility: internal")
            self.assertEqual(lines[4], "generated: true")
            self.assertTrue(lines[5].startswith("last_updated: "))
            self.assertEqual(lines[6], "---")
            self.assertEqual(lines[7], "")
            self.assertTrue(lines[8].startswith("# Cascade Staleness — "))


if __name__ == "__main__":
    unittest.main()
