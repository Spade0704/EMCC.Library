"""Tests for _lib/cli.py — the --wiki-root content-root override (MI-17)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent
        / "Biz.Automation" / "wikisys.library" / "_scripts"),
)

from _lib import cli  # noqa: E402


class ResolveCliWikiRootTests(unittest.TestCase):
    def setUp(self):
        self.default = Path("/tmp/default-root")

    def test_no_args_returns_default(self):
        self.assertEqual(cli.resolve_cli_wiki_root(self.default, argv=[]), self.default)

    def test_named_flag_overrides(self):
        result = cli.resolve_cli_wiki_root(self.default, argv=["--wiki-root", "/tmp/other"])
        self.assertEqual(result, Path("/tmp/other").resolve())

    def test_positional_overrides(self):
        result = cli.resolve_cli_wiki_root(self.default, argv=["/tmp/pos"])
        self.assertEqual(result, Path("/tmp/pos").resolve())

    def test_named_wins_over_positional(self):
        result = cli.resolve_cli_wiki_root(
            self.default, argv=["/tmp/pos", "--wiki-root", "/tmp/named"]
        )
        self.assertEqual(result, Path("/tmp/named").resolve())

    def test_override_is_resolved_to_absolute(self):
        result = cli.resolve_cli_wiki_root(self.default, argv=["--wiki-root", "."])
        self.assertTrue(result.is_absolute())


if __name__ == "__main__":
    unittest.main()
