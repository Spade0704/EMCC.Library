"""Tests for _scripts/backfill_topics.py — bulk topic backfill for pre-existing wikis."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import backfill_topics
from backfill_topics import (
    build_revmap,
    keyword_topics,
    merge_topics_fm,
    path_topics,
    slug,
    stub_stamp,
)
from collections import Counter


def _write(wiki: Path, rel: str, body: str):
    p = wiki / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


CONFIG = """strip_numeric_prefix: true
stub_unstamped: true
use_keywords_yaml: false
skip: [DSC, PRO, ABN]
systems:
  flight-controls: [F_CTL, FCTL]
  electrical: [ELEC]
crosscutting:
  smoke: [SMOKE, CRG_SMOKE]
"""


def _write_config(wiki: Path, body: str = CONFIG):
    (wiki / "_config").mkdir(parents=True, exist_ok=True)
    (wiki / "_config" / "topic_backfill.yaml").write_text(body, encoding="utf-8")


class SlugTests(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(slug("Flight_Controls"), "flight-controls")
        self.assertEqual(slug("ICE & RAIN"), "ice-rain")


class RevmapTests(unittest.TestCase):
    def test_build_revmap_uppercases(self):
        cfg = {"systems": {"flight-controls": ["F_CTL", "FCTL"]},
               "crosscutting": {"smoke": ["SMOKE"]}}
        rev = build_revmap(cfg)
        self.assertEqual(rev["F_CTL"], "flight-controls")
        self.assertEqual(rev["FCTL"], "flight-controls")
        self.assertEqual(rev["SMOKE"], "smoke")


class PathTopicsTests(unittest.TestCase):
    def setUp(self):
        self.rev = {"F_CTL": "flight-controls", "FCTL": "flight-controls", "SMOKE": "smoke"}
        self.skip = {"DSC", "PRO", "ABN", "FCOM", "QRH"}

    def test_ata_numeric_prefix_stripped(self):
        unmapped = Counter()
        out = path_topics(("FCOM", "DSC", "27_Flight_Controls", "X.md"),
                          self.rev, self.skip, True, unmapped)
        self.assertIn("flight-controls", out)

    def test_abbrev_unifies_with_ata(self):
        unmapped = Counter()
        a = path_topics(("FCOM", "DSC", "27_Flight_Controls", "X.md"), self.rev, self.skip, True, unmapped)
        b = path_topics(("QRH", "FCTL", "Y.md"), self.rev, self.skip, True, unmapped)
        self.assertEqual(a & b, {"flight-controls"})

    def test_skip_tokens_not_tagged(self):
        unmapped = Counter()
        out = path_topics(("FCOM", "DSC", "X.md"), self.rev, self.skip, True, unmapped)
        self.assertEqual(out, set())

    def test_unknown_token_reported(self):
        unmapped = Counter()
        path_topics(("FCOM", "WOBBLE", "X.md"), self.rev, self.skip, True, unmapped)
        self.assertEqual(unmapped["WOBBLE"], 1)


class KeywordTopicsTests(unittest.TestCase):
    def test_matches_title_and_filename(self):
        terms = [("engine fire", "engine-fire"), ("smoke", "smoke")]
        out = keyword_topics("Engine_Fire.md", '---\ntitle: "Engine Fire"\n---\n# Engine Fire\n', terms)
        self.assertIn("engine-fire", out)


class FrontmatterTests(unittest.TestCase):
    def test_merge_additive(self):
        text = '---\ntitle: "X"\ntopics: [smoke]\n---\nbody\n'
        out, changed = merge_topics_fm(text, ["smoke", "fire"])
        self.assertTrue(changed)
        self.assertIn("topics: [fire, smoke]", out)

    def test_merge_idempotent(self):
        text = '---\ntitle: "X"\ntopics: [fire, smoke]\n---\nbody\n'
        out, changed = merge_topics_fm(text, ["smoke"])
        self.assertFalse(changed)

    def test_merge_adds_field_when_absent(self):
        text = '---\ntitle: "X"\n---\nbody\n'
        out, changed = merge_topics_fm(text, ["smoke"])
        self.assertTrue(changed)
        self.assertIn("topics: [smoke]", out)

    def test_merge_block_list_form_not_dropped(self):
        # Auditor 2026-06-13: a block-list topics field must not lose its
        # existing entries on merge, and must leave no orphan "- " lines.
        text = '---\ntitle: "X"\ntopics:\n  - fire\n  - hydraulic\n---\nbody\n'
        out, changed = merge_topics_fm(text, ["smoke"])
        self.assertTrue(changed)
        self.assertIn("topics: [fire, hydraulic, smoke]", out)
        # old block-list lines removed (no orphan dash items in frontmatter)
        fm = out.split("---")[1]
        self.assertNotIn("- fire", fm)
        self.assertNotIn("- hydraulic", fm)

    def test_merge_block_list_idempotent(self):
        text = '---\ntitle: "X"\ntopics:\n  - fire\n  - smoke\n---\nbody\n'
        out, changed = merge_topics_fm(text, ["smoke"])
        # all incoming topics already present → still rewrites to canonical
        # inline form once; a second pass is a no-op.
        out2, changed2 = merge_topics_fm(out, ["smoke"])
        self.assertFalse(changed2)

    def test_stub_preserves_body_verbatim(self):
        body = "# Title Here\n\nProcedure text.\n"
        out = stub_stamp(body, ["smoke"])
        self.assertTrue(out.endswith(body))
        self.assertIn("status: stub-unstamped", out)
        self.assertIn('title: "Title Here"', out)


class RunTests(unittest.TestCase):
    def test_no_config_noop(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write(wiki, "FCOM/DSC/27_Flight_Controls/X.md", '---\ntitle: "X"\n---\n# X\n')
            summary = backfill_topics.run(wiki, apply=True)
        self.assertFalse(summary["configured"])
        self.assertEqual(summary["merged"], 0)

    def test_apply_merges_and_stubs(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_config(wiki)
            a = _write(wiki, "FCOM/DSC/27_Flight_Controls/X.md", '---\ntitle: "X"\n---\n# X\n')
            b = _write(wiki, "QRH/FCTL/Y.md", "# Y no frontmatter\n")
            summary = backfill_topics.run(wiki, apply=True)
            self.assertTrue(summary["configured"])
            self.assertIn("topics: [flight-controls]", a.read_text(encoding="utf-8"))
            bt = b.read_text(encoding="utf-8")
            self.assertIn("status: stub-unstamped", bt)
            self.assertIn("flight-controls", bt)

    def test_idempotent(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_config(wiki)
            _write(wiki, "FCOM/DSC/27_Flight_Controls/X.md", '---\ntitle: "X"\n---\n# X\n')
            backfill_topics.run(wiki, apply=True)
            first = {p: p.read_text(encoding="utf-8") for p in wiki.rglob("*.md")}
            backfill_topics.run(wiki, apply=True)
            second = {p: p.read_text(encoding="utf-8") for p in wiki.rglob("*.md")}
        self.assertEqual(first, second)

    def test_dry_run_no_writes(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_config(wiki)
            a = _write(wiki, "FCOM/DSC/27_Flight_Controls/X.md", '---\ntitle: "X"\n---\n# X\n')
            before = a.read_text(encoding="utf-8")
            summary = backfill_topics.run(wiki, apply=False)
            self.assertEqual(a.read_text(encoding="utf-8"), before)
            self.assertGreater(summary["matched"], 0)


if __name__ == "__main__":
    unittest.main()
