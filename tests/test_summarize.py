"""Tests for _scripts/summarize.py — canonical Librarian summarize() engine.

Covers the council-required guards: abbreviation/version/decimal-aware sentence
splitting, the faithfulness guarantee (every extracted sentence is a verbatim span
of the source prose), determinism, jargon FILTERING (not mutation) for the
entrepreneur audience, developer raw-passthrough, empty input, and the LLM-seam
dispatch (summarize_fn used when present, extractive fallback otherwise).
"""

import io
import unittest

import summarize


class SplitSentencesTests(unittest.TestCase):

    def test_basic_split(self):
        self.assertEqual(
            summarize.split_sentences("One thing. Two things. Three."),
            ["One thing.", "Two things.", "Three."],
        )

    def test_abbreviation_not_split(self):
        out = summarize.split_sentences("Use a tool, e.g. the linter, first. Then ship.")
        self.assertEqual(len(out), 2)
        self.assertIn("e.g. the linter", out[0])

    def test_version_and_decimal_not_split(self):
        out = summarize.split_sentences("It ships v1.3 now. The ratio is 3.14 today.")
        self.assertEqual(len(out), 2)
        self.assertIn("v1.3", out[0])
        self.assertIn("3.14", out[1])

    def test_empty_and_whitespace(self):
        self.assertEqual(summarize.split_sentences(""), [])
        self.assertEqual(summarize.split_sentences("   \n  "), [])

    def test_single_sentence_no_terminator(self):
        self.assertEqual(
            summarize.split_sentences("a lone clause with no period"),
            ["a lone clause with no period"],
        )


class ExtractSummaryTests(unittest.TestCase):

    SAMPLE = (
        "---\n"
        "title: t\n"
        "---\n"
        "# Codex Overview\n"
        "\n"
        "Codex turns project knowledge into a clean, validated wiki for the team.\n"
        "The engine runs in `_scripts/build_topic_index.py` against the `_canon/` files.\n"
        "It saves the owner time because pages stay current automatically.\n"
        "See commit a1b2c3d4e5f for the migration that landed in 02-Operations/Sync.md.\n"
    )

    def test_developer_is_raw_passthrough(self):
        out = summarize.extract_summary(self.SAMPLE, audience="developer")
        self.assertEqual(out, self.SAMPLE.strip())

    def test_entrepreneur_drops_jargon_sentences(self):
        out = summarize.extract_summary(self.SAMPLE, audience="entrepreneur",
                                        max_sentences=2)
        # The path/hash/filename sentences must be filtered out.
        self.assertNotIn("_scripts/build_topic_index.py", out)
        self.assertNotIn("a1b2c3d4e5f", out)
        self.assertNotIn("02-Operations/Sync.md", out)
        # A business-facing sentence survives.
        self.assertIn("clean, validated wiki", out)

    def test_faithfulness_every_sentence_is_verbatim_span(self):
        # The faithfulness guarantee: output sentences are verbatim spans of the
        # normalized source prose (extraction never rewrites or deletes words).
        prose = summarize._to_prose(self.SAMPLE)
        normalized_prose = " ".join(prose.split())
        out = summarize.extract_summary(self.SAMPLE, audience="auditor",
                                        max_sentences=3)
        for sentence in summarize.split_sentences(out):
            self.assertIn(sentence, normalized_prose,
                          "extracted sentence is not a verbatim source span")

    def test_deterministic(self):
        a = summarize.extract_summary(self.SAMPLE, "entrepreneur")
        b = summarize.extract_summary(self.SAMPLE, "entrepreneur")
        self.assertEqual(a, b)

    def test_empty_source_returns_empty(self):
        self.assertEqual(summarize.extract_summary("", "entrepreneur"), "")
        self.assertEqual(summarize.extract_summary("---\nt: 1\n---\n", "entrepreneur"), "")

    def test_all_jargon_falls_back_not_empty(self):
        # Every sentence is technical → entrepreneur must still return something
        # faithful rather than an empty string.
        src = ("Run `_scripts/x.py` now. Edit the _canon/roster.yaml file. "
               "Check commit deadbeef1 today.")
        out = summarize.extract_summary(src, "entrepreneur", max_sentences=1)
        self.assertTrue(out.strip())

    def test_preserves_document_order(self):
        out = summarize.extract_summary(self.SAMPLE, "auditor", max_sentences=2)
        sents = summarize.split_sentences(out)
        prose = " ".join(summarize._to_prose(self.SAMPLE).split())
        positions = [prose.index(s) for s in sents]
        self.assertEqual(positions, sorted(positions))


class SummarizeFacadeTests(unittest.TestCase):

    def test_summarize_fn_used_when_present(self):
        calls = []

        def fake_llm(source, audience):
            calls.append((source, audience))
            return "PLAIN: rewritten for {}".format(audience)

        out = summarize.summarize("Some technical text.", "entrepreneur",
                                  summarize_fn=fake_llm)
        self.assertEqual(out, "PLAIN: rewritten for entrepreneur")
        self.assertEqual(len(calls), 1)

    def test_no_fn_falls_back_to_extractive(self):
        src = "Codex keeps the wiki current for the business owner. It saves time."
        out = summarize.summarize(src, "entrepreneur")
        self.assertEqual(out, summarize.extract_summary(src, "entrepreneur"))

    def test_none_source_returns_empty(self):
        self.assertEqual(summarize.summarize(None), "")


class CliTests(unittest.TestCase):

    def test_main_prints_summary(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "doc.md"
            p.write_text("The wiki stays current for the owner. It saves real time.\n",
                         encoding="utf-8")
            out = io.StringIO()
            rc = summarize._main([str(p), "--audience", "entrepreneur"], stdout=out)
            self.assertEqual(rc, 0)
            self.assertTrue(out.getvalue().strip())


if __name__ == "__main__":
    unittest.main()
