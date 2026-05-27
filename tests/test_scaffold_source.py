"""Tests for P18 _scripts/scaffold_source.py."""

import importlib.util
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD_PY = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts" / "scaffold_source.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "scaffold_source", str(SCAFFOLD_PY)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scaffold = _load_module()


class TestScaffoldSource(unittest.TestCase):
    def test_local_file_creates_inbox_md(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            wiki.mkdir()
            src = Path(tmp) / "incoming.txt"
            src.write_text("hello body\n", encoding="utf-8")
            rc = scaffold._main([str(src)], wiki_root=wiki)
            self.assertEqual(rc, 0)
            target = wiki / "_inbox" / "incoming.md"
            self.assertTrue(target.is_file())

    def test_local_file_copies_content(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            wiki.mkdir()
            src = Path(tmp) / "notes.txt"
            payload = "line-a\nline-b\nline-c\n"
            src.write_text(payload, encoding="utf-8")
            scaffold._main([str(src)], wiki_root=wiki)
            content = (wiki / "_inbox" / "notes.md").read_text(
                encoding="utf-8"
            )
            self.assertIn(payload, content)

    def test_url_creates_placeholder_no_fetch(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            url = "https://example.com/foo/bar"
            rc = scaffold._main([url], wiki_root=wiki)
            self.assertEqual(rc, 0)
            files = list((wiki / "_inbox").glob("*.md"))
            self.assertEqual(len(files), 1)
            content = files[0].read_text(encoding="utf-8")
            self.assertIn(url, content)
            self.assertIn("does not fetch URLs", content)

    def test_url_stdout_paste_instruction(self):
        import io

        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            import sys as _sys

            old_stdout = _sys.stdout
            buf = io.StringIO()
            _sys.stdout = buf
            try:
                scaffold._main(
                    ["http://example.org/x"], wiki_root=wiki
                )
            finally:
                _sys.stdout = old_stdout
            out = buf.getvalue()
            self.assertIn("paste source content", out)

    def test_frontmatter_reduced_shape_pending_triage(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            wiki.mkdir()
            src = Path(tmp) / "doc.md"
            src.write_text("body\n", encoding="utf-8")
            scaffold._main([str(src)], wiki_root=wiki)
            content = (wiki / "_inbox" / "doc.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("source:", content)
            self.assertIn("ingested_date:", content)
            self.assertIn("status: pending_triage", content)

    def test_ingested_date_iso_format(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            wiki.mkdir()
            src = Path(tmp) / "x.md"
            src.write_text("body\n", encoding="utf-8")
            scaffold._main([str(src)], wiki_root=wiki)
            content = (wiki / "_inbox" / "x.md").read_text(
                encoding="utf-8"
            )
            match = re.search(r"ingested_date: (\d{4}-\d{2}-\d{2})", content)
            self.assertIsNotNone(match, "ISO date not found")

    def test_refuses_overwrite_existing(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            wiki.mkdir()
            src = Path(tmp) / "twice.md"
            src.write_text("body\n", encoding="utf-8")
            rc1 = scaffold._main([str(src)], wiki_root=wiki)
            self.assertEqual(rc1, 0)
            rc2 = scaffold._main([str(src)], wiki_root=wiki)
            self.assertEqual(rc2, 1)


if __name__ == "__main__":
    unittest.main()
