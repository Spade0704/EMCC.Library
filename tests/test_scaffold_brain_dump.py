"""Tests for P17 _scripts/scaffold_brain_dump.py."""

import importlib.util
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD_PY = REPO_ROOT / "_scripts" / "scaffold_brain_dump.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "scaffold_brain_dump", str(SCAFFOLD_PY)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scaffold = _load_module()


class TestScaffoldBrainDump(unittest.TestCase):
    def test_creates_brain_dump_file(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            rc = scaffold._main(["Reactor Cascade Theory"], wiki_root=wiki)
            self.assertEqual(rc, 0)
            target = wiki / "_brain_dump" / "reactor-cascade-theory.md"
            self.assertTrue(target.is_file())

    def test_frontmatter_dump_status_exploring(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            scaffold._main(["My Idea"], wiki_root=wiki)
            content = (wiki / "_brain_dump" / "my-idea.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("dump_status: exploring", content)
            self.assertIn("type: brain_dump", content)

    def test_frontmatter_required_fields_present(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            scaffold._main(["Field Check"], wiki_root=wiki)
            content = (wiki / "_brain_dump" / "field-check.md").read_text(
                encoding="utf-8"
            )
            for field in (
                "title:",
                "type: brain_dump",
                "visibility: internal",
                "completion: 0",
                "status: outlined",
                "last_updated: ",
                "dependencies: []",
                "canon_sources: []",
                "unverified_claims: []",
                "dump_status: exploring",
                "migrated_to: []",
            ):
                self.assertIn(field, content, "missing: " + field)

    def test_slug_normalization(self):
        cases = [
            ("Hello World!", "hello-world"),
            ("  Already-Dashed  ", "already-dashed"),
            ("CamelCase_Snake", "camelcase-snake"),
            ("###", "untitled"),
            ("multiple   spaces", "multiple-spaces"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(scaffold._slugify(raw), expected)

    def test_refuses_overwrite_existing(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            scaffold._main(["Same Title"], wiki_root=wiki)
            rc = scaffold._main(["Same Title"], wiki_root=wiki)
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
