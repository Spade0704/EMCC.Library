"""Tests for _scripts/_lib/markdown.py — P8.5 promoted helpers."""

import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _lib import markdown


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


class StripCodeTests(unittest.TestCase):

    def test_fenced_replaced_with_whitespace(self):
        body = (
            "before\n"
            "```python\n"
            "BadTerm = 1\n"
            "```\n"
            "after\n"
        )
        out = markdown.strip_code(body)
        # The fenced span chars are blanked but newlines preserved.
        self.assertIn("before\n", out)
        self.assertIn("after\n", out)
        self.assertNotIn("BadTerm", out)
        self.assertNotIn("```python", out)

    def test_inline_replaced_with_whitespace(self):
        body = "alpha `BadTerm` beta\n"
        out = markdown.strip_code(body)
        self.assertNotIn("BadTerm", out)
        self.assertTrue(out.startswith("alpha "))
        self.assertTrue(out.endswith(" beta\n"))

    def test_preserves_line_counts_across_multiline_fence(self):
        body = (
            "L1\n"
            "```\n"
            "L3\n"
            "L4\n"
            "```\n"
            "L6\n"
        )
        out = markdown.strip_code(body)
        self.assertEqual(len(body.splitlines()), len(out.splitlines()))

    def test_html_comment_NOT_stripped(self):
        # HTML comments must survive — Codex's see-also markers are comments
        # that cross_link_topics locates via strip_code.
        body = "text\n<!-- codex:see-also:start -->\n- [[X]]\n<!-- codex:see-also:end -->\n"
        out = markdown.strip_code(body)
        self.assertIn("codex:see-also:start", out)
        self.assertIn("codex:see-also:end", out)

    def test_indented_code_block_after_paragraph_stripped(self):
        # CommonMark indented code block (preceded by a blank line, not a
        # list) — example wikilinks inside must NOT be yielded as real links.
        body = (
            "Report template:\n"
            "\n"
            "    ## A. Contradictions\n"
            "    - [[Page-One]] says X. [[Page-Two]] says Y.\n"
            "\n"
            "End.\n"
        )
        out = markdown.strip_code(body)
        self.assertNotIn("Page-One", out)
        self.assertNotIn("Page-Two", out)
        self.assertIn("Report template:", out)
        self.assertIn("End.", out)
        self.assertEqual(len(body.splitlines()), len(out.splitlines()))

    def test_indented_list_continuation_NOT_stripped(self):
        # The Breaker's false-negative guard: a wikilink in an indented list
        # continuation is a REAL link and must survive strip_code so the
        # cross-ref validator still checks it.
        body = (
            "- a list item\n"
            "\n"
            "    [[Real-But-Broken]] continuation of the item\n"
            "\n"
            "next paragraph\n"
        )
        out = markdown.strip_code(body)
        self.assertIn("Real-But-Broken", out)

    def test_indented_block_does_not_interrupt_paragraph(self):
        # No blank line before the indent => lazy paragraph continuation, not
        # a code block; the wikilink must survive.
        body = "a paragraph line\n    [[Still-A-Link]] hanging indent\n"
        out = markdown.strip_code(body)
        self.assertIn("Still-A-Link", out)


class FrontmatterLineCountTests(unittest.TestCase):

    def test_standard_three_line_fm_returns_3(self):
        text = "---\nkey: val\n---\nbody\n"
        self.assertEqual(markdown.frontmatter_line_count(text), 3)

    def test_no_fm_returns_zero(self):
        text = "no frontmatter here\nplain body\n"
        self.assertEqual(markdown.frontmatter_line_count(text), 0)

    def test_unterminated_fm_returns_zero(self):
        text = "---\nkey: val\nno closing marker\n"
        self.assertEqual(markdown.frontmatter_line_count(text), 0)


class IterContentPagesTests(unittest.TestCase):

    def test_yields_md_under_root_in_shipped_fixture(self):
        # Shipped fixture has content pages under 00-Start-Here/, 01-Domain/,
        # 02-Other/, plus Home.md at root. None should be skipped here.
        pages = list(markdown.iter_content_pages(FIXTURE_ROOT))
        rels = [p.relative_to(FIXTURE_ROOT).as_posix() for p in pages]
        self.assertIn("Home.md", rels)
        self.assertTrue(
            any(r.startswith("00-Start-Here/") for r in rels),
            "expected 00-Start-Here/ content pages in shipped fixture",
        )
        self.assertTrue(len(rels) >= 2)

    def test_skips_underscore_prefixed_components(self):
        # Shipped fixture has _config/ which contains forbidden_terms.yaml
        # (no .md), so we extend in TempDir to add representative skip cases
        # across multiple _-prefix folder types per CLAUDE.md fixture-floor lesson.
        with TemporaryDirectory() as td:
            wiki = Path(td) / "wiki"
            shutil.copytree(FIXTURE_ROOT, wiki)
            for under in [
                "_dashboards",
                "_brain_dump",
                "_template",
                "_context",
                "_canon",
            ]:
                folder = wiki / under
                folder.mkdir(parents=True, exist_ok=True)
                (folder / "should_be_skipped.md").write_text(
                    "---\ntitle: skip\n---\nshould not appear\n",
                    encoding="utf-8",
                )
            (wiki / "_config" / "should_be_skipped.md").write_text(
                "---\ntitle: skip\n---\nshould not appear\n",
                encoding="utf-8",
            )
            # S004: canonical v1.1 raw/ source-archive zone also excluded
            (wiki / "raw").mkdir(parents=True, exist_ok=True)
            (wiki / "raw" / "should_be_skipped.md").write_text(
                "---\ntitle: skip\n---\nshould not appear\n",
                encoding="utf-8",
            )
            pages = list(markdown.iter_content_pages(wiki))
            rels = [p.relative_to(wiki).as_posix() for p in pages]
            for under in [
                "_dashboards",
                "_brain_dump",
                "_template",
                "_context",
                "_canon",
                "_config",
                "raw",
            ]:
                self.assertFalse(
                    any(r.startswith(under + "/") for r in rels),
                    f"iter_content_pages must skip {under}/",
                )


class IntegrationTests(unittest.TestCase):

    def test_compose_strip_and_frontmatter_offset_yields_file_relative_line(self):
        # Build a page with fm + body containing a token on a known body line.
        # Verify body-line + frontmatter offset = original file line.
        text = (
            "---\n"          # file line 1
            "title: t\n"     # file line 2
            "---\n"          # file line 3
            "intro line\n"   # file line 4 (body line 1)
            "BadTerm here\n" # file line 5 (body line 2)
            "tail\n"         # file line 6 (body line 3)
        )
        fm_lines = markdown.frontmatter_line_count(text)
        body = text.split("---\n", 2)[2]
        stripped = markdown.strip_code(body)
        # Find the body-relative line number of "BadTerm" in the stripped body.
        body_line = None
        for i, line in enumerate(stripped.splitlines(), start=1):
            if "BadTerm" in line:
                body_line = i
                break
        self.assertIsNotNone(body_line)
        self.assertEqual(fm_lines + body_line, 5)

    def test_module_import_sanity(self):
        from _lib import markdown as m
        self.assertTrue(callable(m.strip_code))
        self.assertTrue(callable(m.frontmatter_line_count))
        self.assertTrue(callable(m.iter_content_pages))


if __name__ == "__main__":
    unittest.main()
