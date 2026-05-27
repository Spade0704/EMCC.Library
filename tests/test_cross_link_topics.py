"""Tests for _scripts/cross_link_topics.py — P18.3 cross-link build cascade consumer #2."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import cross_link_topics
from cross_link_topics import (
    MARKER_END,
    MARKER_START,
    build_topic_to_pages_index,
    compute_related_files,
    process_page,
    render_see_also_block,
    replace_or_append_marker_block,
    update_page_related_files_fm,
)


def _write_page(
    wiki_root: Path, rel: str, topics_list, body: str = "body"
) -> Path:
    """Helper: write a content page under wiki_root with given topics."""
    path = wiki_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if topics_list is None:
        fm = '---\ntitle: "X"\n---\n'
    else:
        topics_str = "[" + ", ".join(topics_list) + "]"
        fm = '---\ntitle: "X"\ntopics: {}\n---\n'.format(topics_str)
    path.write_text(fm + "\n" + body + "\n", encoding="utf-8")
    return path


class MarkerConstantsTests(unittest.TestCase):

    def test_marker_start_byte_exact(self):
        self.assertEqual(MARKER_START, "<!-- codex:see-also:start -->")

    def test_marker_end_byte_exact(self):
        self.assertEqual(MARKER_END, "<!-- codex:see-also:end -->")


class BuildTopicToPagesIndexTests(unittest.TestCase):

    def test_empty_wiki(self):
        with TemporaryDirectory() as t:
            result = build_topic_to_pages_index(Path(t))
        self.assertEqual(result, {})

    def test_single_topic_multi_page(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            _write_page(wiki, "01-Domain/B.md", ["smoke"])
            result = build_topic_to_pages_index(wiki)
        self.assertIn("smoke", result)
        self.assertEqual(len(result["smoke"]), 2)

    def test_multi_topic_overlap(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["smoke", "fire"])
            _write_page(wiki, "01-Domain/B.md", ["fire"])
            result = build_topic_to_pages_index(wiki)
        self.assertEqual(len(result["smoke"]), 1)
        self.assertEqual(len(result["fire"]), 2)

    def test_pages_without_topics_skipped(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            _write_page(wiki, "01-Domain/B.md", None)
            result = build_topic_to_pages_index(wiki)
        # Only A contributes
        self.assertEqual(len(result["smoke"]), 1)


class ComputeRelatedFilesTests(unittest.TestCase):

    def test_no_overlap_returns_empty(self):
        idx = {"smoke": [Path("A.md")], "fire": [Path("B.md")]}
        result = compute_related_files(
            Path("A.md"), ["smoke"], idx
        )
        self.assertEqual(result, [])

    def test_single_overlap(self):
        idx = {"smoke": [Path("A.md"), Path("B.md")]}
        result = compute_related_files(
            Path("A.md"), ["smoke"], idx
        )
        self.assertEqual(result, [Path("B.md")])

    def test_multi_overlap_dedup(self):
        idx = {
            "smoke": [Path("A.md"), Path("B.md")],
            "fire": [Path("A.md"), Path("B.md"), Path("C.md")],
        }
        result = compute_related_files(
            Path("A.md"), ["smoke", "fire"], idx
        )
        self.assertEqual(result, [Path("B.md"), Path("C.md")])

    def test_self_excluded(self):
        idx = {"smoke": [Path("A.md")]}
        result = compute_related_files(
            Path("A.md"), ["smoke"], idx
        )
        self.assertEqual(result, [])


class RenderSeeAlsoBlockTests(unittest.TestCase):

    def test_empty_related(self):
        result = render_see_also_block({}, {}, Path("."))
        self.assertEqual(result, "")

    def test_single_related(self):
        related = [Path("01-Domain/Foo.md")]
        topics = {Path("01-Domain/Foo.md"): ["smoke"]}
        result = render_see_also_block(related, topics, Path("."))
        self.assertIn("## See also", result)
        self.assertIn("[[Foo]]", result)
        self.assertIn("*topic: smoke*", result)

    def test_multi_related(self):
        related = [Path("A.md"), Path("B.md")]
        topics = {Path("A.md"): ["smoke"], Path("B.md"): ["fire"]}
        result = render_see_also_block(related, topics, Path("."))
        self.assertIn("[[A]]", result)
        self.assertIn("[[B]]", result)

    def test_topic_annotation_format(self):
        related = [Path("A.md")]
        topics = {Path("A.md"): ["smoke", "fire"]}
        result = render_see_also_block(related, topics, Path("."))
        self.assertIn("*topic: smoke, fire*", result)


class UpdatePageRelatedFilesFmTests(unittest.TestCase):

    def test_empty_existing_replaced(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            text = '---\ntitle: "X"\nrelated_files: []\n---\n\nbody\n'
            other = wiki / "01-Domain" / "Other.md"
            result = update_page_related_files_fm(
                text, [other], wiki
            )
        self.assertIn("related_files: [01-Domain/Other.md]", result)

    def test_pre_existing_script_managed_replaced(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            text = (
                '---\ntitle: "X"\n'
                "related_files: [stale/path.md]\n"
                "---\n\nbody\n"
            )
            new = wiki / "fresh.md"
            result = update_page_related_files_fm(text, [new], wiki)
        self.assertNotIn("stale/path.md", result)
        self.assertIn("related_files: [fresh.md]", result)

    def test_fm_field_absent_added(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            text = '---\ntitle: "X"\n---\n\nbody\n'
            other = wiki / "A.md"
            result = update_page_related_files_fm(text, [other], wiki)
        self.assertIn("related_files: [A.md]", result)


class ReplaceOrAppendMarkerBlockTests(unittest.TestCase):

    def test_no_existing_marker_appends(self):
        text = '---\ntitle: "X"\n---\n\n# Header\n\nbody\n'
        block = "## See also\n\n- [[A]]"
        result = replace_or_append_marker_block(text, block)
        self.assertIn(MARKER_START, result)
        self.assertIn(MARKER_END, result)
        self.assertIn("[[A]]", result)
        # Original prose preserved
        self.assertIn("# Header", result)
        self.assertIn("body", result)

    def test_existing_marker_replaces(self):
        text = (
            "# Hdr\n\nbody\n\n"
            + MARKER_START
            + "\n## See also\n\n- [[OLD]]\n"
            + MARKER_END
            + "\n"
        )
        new_block = "## See also\n\n- [[NEW]]"
        result = replace_or_append_marker_block(text, new_block)
        self.assertNotIn("[[OLD]]", result)
        self.assertIn("[[NEW]]", result)

    def test_human_prose_outside_preserved(self):
        text = (
            "Pre-marker human prose.\n\n"
            + MARKER_START
            + "\nold\n"
            + MARKER_END
            + "\n\nPost-marker human prose.\n"
        )
        result = replace_or_append_marker_block(text, "## See also\n- [[X]]")
        self.assertIn("Pre-marker human prose.", result)
        self.assertIn("Post-marker human prose.", result)

    def test_human_edits_between_overwritten(self):
        text = (
            MARKER_START
            + "\nHUMAN_EDIT_INSIDE\n"
            + MARKER_END
            + "\n"
        )
        result = replace_or_append_marker_block(text, "## See also\n- [[X]]")
        self.assertNotIn("HUMAN_EDIT_INSIDE", result)
        self.assertIn("[[X]]", result)

    def test_position_preserved_when_mid_file(self):
        text = (
            "header\n\n"
            + MARKER_START
            + "\nold\n"
            + MARKER_END
            + "\n\nfooter\n"
        )
        result = replace_or_append_marker_block(text, "## See also\n- [[X]]")
        # Marker position preserved (still mid-file with footer after)
        self.assertIn("footer", result)
        end_idx = result.find(MARKER_END)
        footer_idx = result.find("footer")
        self.assertLess(end_idx, footer_idx)

    def test_skips_fenced_markers(self):
        """S047 dogfood Edit-1: markers inside fenced code blocks are
        not detected as live markers. Sub-case (a) fenced-only pair →
        preserved verbatim, new block appended at EOF; sub-case (b)
        real unfenced pair + in-fence documenting pair → real pair
        replaced, in-fence pair byte-preserved.
        """
        # Sub-case (a): in-fence marker pair ONLY → preserved + append.
        fenced_only = (
            "# Docs page documenting marker syntax\n\n"
            "Use these markers:\n\n"
            "```\n"
            + MARKER_START + "\n"
            "## See also\n"
            "- [[Example]]\n"
            + MARKER_END + "\n"
            "```\n\n"
            "End of docs.\n"
        )
        result_a = replace_or_append_marker_block(
            fenced_only, "## See also\n- [[Real]]"
        )
        # In-fence block preserved byte-identical.
        self.assertIn(
            "```\n" + MARKER_START + "\n## See also\n- [[Example]]\n"
            + MARKER_END + "\n```",
            result_a,
        )
        # New real block appended AFTER the fenced documentation block.
        self.assertIn("[[Real]]", result_a)
        fenced_close = result_a.find("End of docs.")
        real_block_idx = result_a.find("[[Real]]")
        self.assertGreater(real_block_idx, fenced_close)

        # Sub-case (b): real unfenced pair AFTER in-fence pair → real
        # pair replaced, in-fence pair preserved byte-identical.
        mixed = (
            "# Docs page\n\n"
            "Syntax example:\n\n"
            "```\n"
            + MARKER_START + "\n"
            "DOCUMENTATION_BLOCK\n"
            + MARKER_END + "\n"
            "```\n\n"
            "Real block below:\n\n"
            + MARKER_START + "\n"
            "## See also\n"
            "- [[OLD]]\n"
            + MARKER_END + "\n"
        )
        result_b = replace_or_append_marker_block(
            mixed, "## See also\n- [[NEW]]"
        )
        # Real pair replaced.
        self.assertNotIn("[[OLD]]", result_b)
        self.assertIn("[[NEW]]", result_b)
        # In-fence DOCUMENTATION_BLOCK preserved byte-identical.
        self.assertIn(
            "```\n" + MARKER_START + "\nDOCUMENTATION_BLOCK\n"
            + MARKER_END + "\n```",
            result_b,
        )


class ProcessPageTests(unittest.TestCase):

    def test_empty_no_topics_skipped(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            p = _write_page(wiki, "A.md", [])
            existing = p.read_text(encoding="utf-8")
            changed = process_page(p, [], {}, {}, wiki)
            self.assertFalse(changed)
            self.assertEqual(p.read_text(encoding="utf-8"), existing)

    def test_single_update_writes(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            a = _write_page(wiki, "01-Domain/A.md", ["smoke"])
            b = _write_page(wiki, "01-Domain/B.md", ["smoke"])
            idx = {"smoke": [a, b]}
            topics_by_path = {a: ["smoke"], b: ["smoke"]}
            changed = process_page(
                a, ["smoke"], idx, topics_by_path, wiki
            )
            self.assertTrue(changed)
            content = a.read_text(encoding="utf-8")
            self.assertIn("[[B]]", content)
            self.assertIn(MARKER_START, content)
            self.assertIn(MARKER_END, content)

    def test_write_back_byte_equivalent_after_replay(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            a = _write_page(wiki, "01-Domain/A.md", ["smoke"])
            b = _write_page(wiki, "01-Domain/B.md", ["smoke"])
            idx = {"smoke": [a, b]}
            topics_by_path = {a: ["smoke"], b: ["smoke"]}
            process_page(a, ["smoke"], idx, topics_by_path, wiki)
            first = a.read_text(encoding="utf-8")
            # 2nd call: same inputs → no write
            changed = process_page(
                a, ["smoke"], idx, topics_by_path, wiki
            )
            self.assertFalse(changed)
            self.assertEqual(a.read_text(encoding="utf-8"), first)

    def test_no_overlap_no_block_added(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            a = _write_page(wiki, "01-Domain/A.md", ["smoke"])
            idx = {"smoke": [a]}
            topics_by_path = {a: ["smoke"]}
            process_page(a, ["smoke"], idx, topics_by_path, wiki)
            content = a.read_text(encoding="utf-8")
            # related is empty (self-excluded) — no see_also block
            self.assertNotIn(MARKER_START, content)
            # But fm related_files: [] still written
            self.assertIn("related_files: []", content)


class IdempotencyTests(unittest.TestCase):
    """MANDATORY per spec §2.7 idempotency requirement."""

    def test_identical_state_re_run_zero_diffs(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            _write_page(wiki, "01-Domain/B.md", ["smoke"])
            cross_link_topics.run(wiki)
            after_first = {
                p: p.read_text(encoding="utf-8")
                for p in (wiki / "01-Domain").iterdir()
            }
            # 2nd run with identical state
            summary2 = cross_link_topics.run(wiki)
            after_second = {
                p: p.read_text(encoding="utf-8")
                for p in (wiki / "01-Domain").iterdir()
            }
        self.assertEqual(after_first, after_second)
        self.assertEqual(summary2["pages_updated"], 0)
        self.assertEqual(summary2["idempotent_pages"], 2)

    def test_fm_changed_only_block_regenerates(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            a = _write_page(wiki, "01-Domain/A.md", ["smoke"])
            _write_page(wiki, "01-Domain/B.md", ["smoke"])
            cross_link_topics.run(wiki)
            # Add a 3rd page sharing topic — fm of A+B changes
            _write_page(wiki, "01-Domain/C.md", ["smoke"])
            summary = cross_link_topics.run(wiki)
            self.assertGreater(summary["pages_updated"], 0)
            a_content = a.read_text(encoding="utf-8")
            self.assertIn("[[C]]", a_content)

    def test_block_changed_only_fm_takes_precedence(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            a = _write_page(wiki, "01-Domain/A.md", ["smoke"])
            _write_page(wiki, "01-Domain/B.md", ["smoke"])
            cross_link_topics.run(wiki)
            # Tamper with A's body block between markers
            tampered = a.read_text(encoding="utf-8").replace(
                "[[B]]", "[[TAMPER]]"
            )
            a.write_text(tampered, encoding="utf-8")
            cross_link_topics.run(wiki)
            content = a.read_text(encoding="utf-8")
            # Frontmatter related_files: drives block; tamper overwritten
            self.assertIn("[[B]]", content)
            self.assertNotIn("[[TAMPER]]", content)


class RunOrchestratorTests(unittest.TestCase):

    def test_happy_path(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["smoke"])
            _write_page(wiki, "01-Domain/B.md", ["smoke"])
            summary = cross_link_topics.run(wiki)
            self.assertEqual(summary["pages_seen"], 2)
            self.assertEqual(summary["pages_updated"], 2)

    def test_empty_wiki_graceful(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            summary = cross_link_topics.run(wiki)
            self.assertEqual(summary["pages_seen"], 0)
            self.assertEqual(summary["pages_updated"], 0)

    def test_pages_with_no_topics_handled(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", None)
            summary = cross_link_topics.run(wiki)
            self.assertEqual(summary["pages_seen"], 1)
            self.assertEqual(summary["pages_updated"], 0)

    def test_single_topic_no_other_pages(self):
        with TemporaryDirectory() as t:
            wiki = Path(t)
            _write_page(wiki, "01-Domain/A.md", ["solo"])
            summary = cross_link_topics.run(wiki)
            self.assertEqual(summary["pages_seen"], 1)
            # A is the only page with topic 'solo' — related is empty
            # but fm related_files: [] still written → counts as update
            a = wiki / "01-Domain" / "A.md"
            content = a.read_text(encoding="utf-8")
            self.assertIn("related_files: []", content)


if __name__ == "__main__":
    unittest.main()
