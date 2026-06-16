"""Tests for route_inbox.py (S002 B6 P0)."""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

import route_inbox  # noqa: E402


class TestScanPhase(unittest.TestCase):

    def test_empty_inbox_returns_empty(self):
        with TemporaryDirectory() as tmp:
            inbox = Path(tmp) / "0-Inbox"
            inbox.mkdir()
            entries = route_inbox.scan_inbox(inbox)
            self.assertEqual(entries, [])

    def test_scan_emits_metadata_for_each_file(self):
        with TemporaryDirectory() as tmp:
            inbox = Path(tmp) / "0-Inbox"
            inbox.mkdir()
            (inbox / "foo.md").write_text("hello\n", encoding="utf-8")
            (inbox / "bar.pdf").write_bytes(b"%PDF-1.4 dummy")
            entries = route_inbox.scan_inbox(inbox)
            self.assertEqual(len(entries), 2)
            names = {e["filename"] for e in entries}
            self.assertEqual(names, {"foo.md", "bar.pdf"})
            for e in entries:
                self.assertIsNone(e["destination"])
                self.assertIsNone(e["destination_zone"])
                self.assertIsNotNone(e["sha256_first_4kb"])

    def test_gitkeep_skipped(self):
        with TemporaryDirectory() as tmp:
            inbox = Path(tmp) / "0-Inbox"
            inbox.mkdir()
            (inbox / ".gitkeep").write_text("")
            (inbox / "real.md").write_text("real")
            entries = route_inbox.scan_inbox(inbox)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["filename"], "real.md")


class TestExecutePhase(unittest.TestCase):

    def test_execute_moves_files_to_resolved_destinations(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            inbox = tmp_path / "0-Inbox"
            inbox.mkdir()
            src = inbox / "doc.md"
            src.write_text("content")
            dst = tmp_path / "tasks" / "doc.md"
            manifest = tmp_path / "manifest.json"
            entries = route_inbox.scan_inbox(inbox)
            entries[0]["destination"] = str(dst)
            entries[0]["destination_zone"] = "tasks"
            manifest.write_text(json.dumps(entries), encoding="utf-8")
            results = route_inbox.execute_manifest(manifest)
            self.assertEqual(results[0]["status"], "moved")
            self.assertTrue(dst.exists())
            self.assertFalse(src.exists())

    def test_execute_skips_null_destination(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_data = [{
                "filename": "x.md",
                "source_abs": str(tmp_path / "x.md"),
                "destination": None,
                "destination_zone": None,
            }]
            manifest = tmp_path / "manifest.json"
            manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
            results = route_inbox.execute_manifest(manifest)
            self.assertEqual(results[0]["status"], "skipped")


class TestExecuteRootConfinement(unittest.TestCase):
    """Audit B3: destination/source confined to the scan root (fail-closed)."""

    def test_in_root_destination_proceeds(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            inbox = tmp_path / "0-Inbox"
            inbox.mkdir()
            src = inbox / "doc.md"
            src.write_text("content")
            dst = tmp_path / "tasks" / "doc.md"
            manifest = tmp_path / "manifest.json"
            entries = route_inbox.scan_inbox(inbox)
            entries[0]["destination"] = str(dst)
            manifest.write_text(json.dumps(entries), encoding="utf-8")
            results = route_inbox.execute_manifest(manifest, root=tmp_path)
            self.assertEqual(results[0]["status"], "moved")
            self.assertTrue(dst.exists())

    def test_escaping_destination_skipped_and_flagged(self):
        with TemporaryDirectory() as tmp_root, TemporaryDirectory() as tmp_out:
            root = Path(tmp_root)
            inbox = root / "0-Inbox"
            inbox.mkdir()
            src = inbox / "doc.md"
            src.write_text("content")
            # Destination escapes the scan root entirely (a sibling tmp dir).
            escaping_dst = Path(tmp_out) / "stolen.md"
            manifest = root / "manifest.json"
            entries = route_inbox.scan_inbox(inbox)
            entries[0]["destination"] = str(escaping_dst)
            manifest.write_text(json.dumps(entries), encoding="utf-8")
            results = route_inbox.execute_manifest(manifest, root=root)
            self.assertEqual(results[0]["status"], "skipped")
            self.assertIn("escapes root", results[0]["reason"])
            # Fail-closed: no write outside the tree, source untouched.
            self.assertFalse(escaping_dst.exists())
            self.assertTrue(src.exists())

    def test_escaping_via_traversal_skipped(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "project"
            inbox = root / "0-Inbox"
            inbox.mkdir(parents=True)
            src = inbox / "doc.md"
            src.write_text("content")
            # `..` climbs out of the project root to a parent sibling.
            escaping_dst = root / ".." / "escaped.md"
            manifest = root / "manifest.json"
            entries = route_inbox.scan_inbox(inbox)
            entries[0]["destination"] = str(escaping_dst)
            manifest.write_text(json.dumps(entries), encoding="utf-8")
            results = route_inbox.execute_manifest(manifest, root=root)
            self.assertEqual(results[0]["status"], "skipped")
            self.assertIn("escapes root", results[0]["reason"])
            self.assertTrue(src.exists())

    def test_default_root_is_manifest_parent(self):
        # When root is omitted it defaults to the manifest's parent dir,
        # which scan emits as <root>/route_candidates.json — so in-root
        # destinations still proceed without an explicit root arg.
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            inbox = tmp_path / "0-Inbox"
            inbox.mkdir()
            src = inbox / "doc.md"
            src.write_text("content")
            dst = tmp_path / "tasks" / "doc.md"
            manifest = tmp_path / "route_candidates.json"
            entries = route_inbox.scan_inbox(inbox)
            entries[0]["destination"] = str(dst)
            manifest.write_text(json.dumps(entries), encoding="utf-8")
            results = route_inbox.execute_manifest(manifest)
            self.assertEqual(results[0]["status"], "moved")


if __name__ == "__main__":
    unittest.main()
