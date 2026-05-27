"""Tests for _scripts/_lib/frontmatter.py — P1 foundation."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _lib import frontmatter
from _lib.frontmatter import find_frontmatter_close


class FrontmatterParserTests(unittest.TestCase):

    def test_extracts_frontmatter_block(self):
        text = (
            "---\n"
            'title: "Test Page"\n'
            "type: framework\n"
            "visibility: internal\n"
            "completion: 80\n"
            "status: ready\n"
            "---\n"
            "\n"
            "# Body content here.\n"
        )
        fm = frontmatter.parse_frontmatter(text)
        self.assertEqual(fm["title"], "Test Page")
        self.assertEqual(fm["type"], "framework")
        self.assertEqual(fm["visibility"], "internal")
        self.assertEqual(fm["completion"], 80)
        self.assertEqual(fm["status"], "ready")

    def test_parses_all_list_fields(self):
        text = (
            "---\n"
            'dependencies: ["Page-A", "Page-B"]\n'
            'blocking_questions: ["What is X?", "How does Y work?"]\n'
            'canon_sources: ["_sources/raw/spec.md §2.1"]\n'
            "unverified_claims: []\n"
            'migrated_to: ["Path/To/Canon-Page.md"]\n'
            "---\n"
        )
        fm = frontmatter.parse_frontmatter(text)
        self.assertEqual(fm["dependencies"], ["Page-A", "Page-B"])
        self.assertEqual(
            fm["blocking_questions"], ["What is X?", "How does Y work?"]
        )
        self.assertEqual(fm["canon_sources"], ["_sources/raw/spec.md §2.1"])
        self.assertEqual(fm["unverified_claims"], [])
        self.assertEqual(fm["migrated_to"], ["Path/To/Canon-Page.md"])

    def test_handles_file_without_frontmatter(self):
        text = "# Just a heading\n\nSome body text.\n"
        self.assertIsNone(frontmatter.parse_frontmatter(text))

    def test_wiki_root_resolves_correctly(self):
        """WIKI_ROOT must resolve to either Library's install root (CLAUDE.md +
        module.json co-existing) or a bootstrapped wiki's root (Home.md present).

        Pre-S002: hard-coded `parent.parent.parent` + `parent.name == "Project Codex"`
        — the latter was env-hardcoded to the operator's Windows install path and
        failed in any other environment (baseline failure since Session 1).

        Post-S002 (Codex v1.1) restructure: `_lib/` moved to
        `Biz.Automation/wikisys.library/_scripts/_lib/`. The 3-parent walk now
        resolves to `wikisys.library/` instead of Library's repo root, so the
        install case is broken. Marker-based resolution (in
        `frontmatter._find_wiki_root`) handles both Library install + bootstrapped
        wiki correctly; this test verifies the result.
        """
        root = frontmatter.WIKI_ROOT
        has_install_markers = (
            (root / "CLAUDE.md").exists()
            and (root / "module.json").exists()
        )
        has_wiki_marker = (root / "Home.md").exists()
        self.assertTrue(
            has_install_markers or has_wiki_marker,
            f"WIKI_ROOT={root} must contain either (CLAUDE.md + module.json) for "
            f"Library install OR Home.md for bootstrapped wiki. Has neither — "
            f"WIKI_ROOT path math is wrong."
        )

    def test_load_page_returns_body_verbatim(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            with_fm = tmp_path / "with_fm.md"
            with_fm.write_text(
                '---\ntitle: "X"\n---\n# Heading\n\nBody.\n',
                encoding="utf-8",
            )
            page = frontmatter.load_page(with_fm)
            self.assertEqual(page["frontmatter"]["title"], "X")
            self.assertEqual(page["body"], "# Heading\n\nBody.\n")
            self.assertEqual(page["path"], with_fm)

            no_fm = tmp_path / "no_fm.md"
            content = "# Heading\n\nBody only.\n"
            no_fm.write_text(content, encoding="utf-8")
            page = frontmatter.load_page(no_fm)
            self.assertEqual(page["frontmatter"], {})
            self.assertEqual(page["body"], content)
            self.assertEqual(page["path"], no_fm)

    def test_explicit_null_parses_to_none(self):
        text = "---\npublic_pair: null\n---\n"
        fm = frontmatter.parse_frontmatter(text)
        self.assertIn("public_pair", fm)
        self.assertIsNone(fm["public_pair"])

    def test_empty_value_parses_to_none(self):
        text = "---\npublic_pair:\n---\n"
        fm = frontmatter.parse_frontmatter(text)
        self.assertIn("public_pair", fm)
        self.assertIsNone(fm["public_pair"])

    def test_reduced_source_frontmatter(self):
        # Per spec §2.3 reduced schema for _inbox/ and _sources/raw/.
        text = (
            "---\n"
            'source: "https://example.com/article"\n'
            "ingested_date: 2026-04-30\n"
            "status: pending_triage\n"
            "---\n"
            "\n"
            "Source content here.\n"
        )
        fm = frontmatter.parse_frontmatter(text)
        self.assertEqual(fm["source"], "https://example.com/article")
        self.assertEqual(fm["ingested_date"], "2026-04-30")
        self.assertEqual(fm["status"], "pending_triage")

        text_ingested = (
            "---\n"
            'source: "Meeting notes 2026-04-15"\n'
            "ingested_date: 2026-04-30\n"
            "status: ingested\n"
            "---\n"
        )
        fm = frontmatter.parse_frontmatter(text_ingested)
        self.assertEqual(fm["status"], "ingested")

    def test_parses_scalar_types(self):
        text = (
            "---\n"
            'quoted_string: "hello world"\n'
            "unquoted_string: hello\n"
            "integer: 42\n"
            "negative_integer: -5\n"
            "true_bool: true\n"
            "false_bool: false\n"
            "---\n"
        )
        fm = frontmatter.parse_frontmatter(text)
        self.assertEqual(fm["quoted_string"], "hello world")
        self.assertEqual(fm["unquoted_string"], "hello")
        self.assertEqual(fm["integer"], 42)
        self.assertEqual(fm["negative_integer"], -5)
        self.assertIs(fm["true_bool"], True)
        self.assertIs(fm["false_bool"], False)

    def test_handles_comments(self):
        text = (
            "---\n"
            "# Full-line comment at the top\n"
            'title: "Page"      # trailing comment\n'
            "# Another full-line comment\n"
            "type: framework\n"
            "---\n"
        )
        fm = frontmatter.parse_frontmatter(text)
        self.assertEqual(fm["title"], "Page")
        self.assertEqual(fm["type"], "framework")
        self.assertEqual(len(fm), 2)

    def test_parses_empty_list(self):
        text = "---\nunverified_claims: []\n---\n"
        fm = frontmatter.parse_frontmatter(text)
        self.assertEqual(fm["unverified_claims"], [])


class ConfigYamlParserTests(unittest.TestCase):

    def test_parse_config_yaml_minimal_valid(self):
        text = (
            "rules:\n"
            '  - pattern: "Foo"\n'
            "    severity: error\n"
            "    enabled: true\n"
            '  - pattern: "Bar"\n'
            "    severity: warning\n"
            "    priority: 5\n"
        )
        result = frontmatter.parse_config_yaml(text)
        self.assertEqual(set(result.keys()), {"rules"})
        self.assertEqual(len(result["rules"]), 2)
        self.assertEqual(result["rules"][0]["pattern"], "Foo")
        self.assertEqual(result["rules"][0]["severity"], "error")
        self.assertIs(result["rules"][0]["enabled"], True)
        self.assertEqual(result["rules"][1]["pattern"], "Bar")
        self.assertEqual(result["rules"][1]["severity"], "warning")
        self.assertEqual(result["rules"][1]["priority"], 5)

    def test_parse_config_yaml_multiple_list_keys(self):
        text = (
            "version: 1\n"
            "rules:\n"
            '  - pattern: "Foo"\n'
            "    severity: error\n"
            "patterns:\n"
            "  - id: 1\n"
            '    name: "alpha"\n'
        )
        result = frontmatter.parse_config_yaml(text)
        self.assertEqual(result["version"], 1)
        self.assertEqual(len(result["rules"]), 1)
        self.assertEqual(result["rules"][0]["pattern"], "Foo")
        self.assertEqual(result["rules"][0]["severity"], "error")
        self.assertEqual(len(result["patterns"]), 1)
        self.assertEqual(result["patterns"][0]["id"], 1)
        self.assertEqual(result["patterns"][0]["name"], "alpha")

    def test_parse_config_yaml_comments_and_blank_lines_tolerated(self):
        text = (
            "# Top-level comment before any key\n"
            "\n"
            "rules:\n"
            "  # comment between key and items\n"
            '  - pattern: "Foo"   # trailing comment on item start\n'
            "\n"
            "    severity: error\n"
            "    # comment between fields\n"
            '    message: "hello"\n'
            "\n"
            '  - pattern: "Bar"\n'
            "    severity: warning\n"
        )
        result = frontmatter.parse_config_yaml(text)
        self.assertEqual(len(result["rules"]), 2)
        self.assertEqual(result["rules"][0]["pattern"], "Foo")
        self.assertEqual(result["rules"][0]["severity"], "error")
        self.assertEqual(result["rules"][0]["message"], "hello")
        self.assertEqual(result["rules"][1]["pattern"], "Bar")
        self.assertEqual(result["rules"][1]["severity"], "warning")

    def test_parse_config_yaml_empty_or_whitespace_returns_empty_dict(self):
        self.assertEqual(frontmatter.parse_config_yaml(""), {})
        self.assertEqual(frontmatter.parse_config_yaml("   \n  \n\t\n"), {})
        self.assertEqual(
            frontmatter.parse_config_yaml("# only comments\n# more comments\n"),
            {},
        )

    def test_parse_config_yaml_malformed_raises_ConfigYamlError(self):
        # Top-level line without a colon
        with self.assertRaises(frontmatter.ConfigYamlError) as ctx_top:
            frontmatter.parse_config_yaml(
                "no_colon_at_top\nrules:\n  - x: 1\n"
            )
        self.assertIn("line 1", str(ctx_top.exception))

        # (S047-T2 Edit-2 contract relaxation: scalar list items are now accepted; old ctx_item assertion removed.)

        # Indented content with no list-of-mappings key in scope
        with self.assertRaises(frontmatter.ConfigYamlError) as ctx_orphan:
            frontmatter.parse_config_yaml(
                "version: 1\n  - pattern: foo\n"
            )
        self.assertIn("line 2", str(ctx_orphan.exception))


class FindFrontmatterClosePublicAPITests(unittest.TestCase):
    """S023-T2-α AC8: find_frontmatter_close promoted from module-private to
    public API. Closes documented-debt forward pointer from S021-T2 plan_response
    e0d53a29; doc_lint replica deleted, single source of truth restored.
    """

    def test_find_frontmatter_close_public_api(self):
        # Public name (no underscore) directly importable + callable.
        self.assertTrue(callable(find_frontmatter_close))
        self.assertEqual(find_frontmatter_close.__name__, "find_frontmatter_close")
        self.assertFalse(
            hasattr(frontmatter, "_find_frontmatter_close"),
            "private name removed; full rename per Architect lean (no alias)"
        )

    def test_find_frontmatter_close_returns_close_index(self):
        lines = ["---", "title: X", "type: framework", "---", "Body"]
        self.assertEqual(find_frontmatter_close(lines), 3)

    def test_find_frontmatter_close_returns_none_when_unclosed(self):
        lines = ["---", "title: X", "Body"]
        self.assertIsNone(find_frontmatter_close(lines))

    def test_find_frontmatter_close_returns_none_when_no_open(self):
        lines = ["# Heading", "Body", "---"]
        self.assertIsNone(find_frontmatter_close(lines))


class TestT_XL_3a_ParserExtensions(unittest.TestCase):
    """S047-T-XL-3a parser-enhancement coverage."""

    def test_parse_config_yaml_nested_mapping_2_level(self):
        text = (
            "tfidf:\n"
            "  min_similarity: 0.35\n"
            "  max_links_per_page: 8\n"
            "plugin:\n"
            "  module_path: my_module\n"
            "  weight: 0.5\n"
        )
        result = frontmatter.parse_config_yaml(text)
        self.assertEqual(result["tfidf"]["min_similarity"], 0.35)
        self.assertEqual(result["tfidf"]["max_links_per_page"], 8)
        self.assertEqual(result["plugin"]["module_path"], "my_module")
        self.assertEqual(result["plugin"]["weight"], 0.5)

    def test_parse_value_float_literal_basic(self):
        self.assertEqual(frontmatter._parse_value("0.35"), 0.35)
        self.assertEqual(frontmatter._parse_value("1.5"), 1.5)
        self.assertEqual(frontmatter._parse_value("-2.7"), -2.7)
        self.assertEqual(frontmatter._parse_value(".5"), 0.5)
        self.assertEqual(frontmatter._parse_value("5."), 5.0)
        self.assertIsInstance(frontmatter._parse_value("0.35"), float)

    def test_parse_value_float_literal_bool_not_numeric_invariant(self):
        # CRITICAL invariant: bool tokens must NOT coerce to float.
        self.assertIs(frontmatter._parse_value("true"), True)
        self.assertIs(frontmatter._parse_value("false"), False)
        # Pure int strings stay int (not float).
        self.assertEqual(frontmatter._parse_value("5"), 5)
        self.assertIsInstance(frontmatter._parse_value("5"), int)
        # Non-numeric strings stay strings.
        self.assertEqual(frontmatter._parse_value("hello"), "hello")

    def test_parse_config_yaml_block_list_of_scalars(self):
        """S047 dogfood Edit-2: parse_config_yaml accepts block-list
        scalar items alongside `- key: value` mappings."""
        text = (
            "topics:\n"
            '  - "alpha"\n'
            '  - "beta"\n'
        )
        result = frontmatter.parse_config_yaml(text)
        self.assertEqual(result["topics"], ["alpha", "beta"])

    def test_parse_value_tilde_is_null(self):
        """S047 dogfood Edit-3: bare `~` parses as None (standard YAML
        null spelling), alongside `""` and `"null"`."""
        self.assertIsNone(frontmatter._parse_value("~"))
        # Round-trip via parse_frontmatter for end-to-end coverage.
        text = (
            "---\n"
            "module_path: ~\n"
            "---\n"
        )
        fm = frontmatter.parse_frontmatter(text)
        self.assertIsNone(fm["module_path"])


class TestCanonAndDecisionsLookup(unittest.TestCase):
    """S004 MI-18: canon-lookup marker-walk handles v1.0 + v1.1 layouts."""

    def test_find_canon_dir_v1_0_layout_returns_direct_child(self):
        """v1.0 wiki: <wiki>/_canon/ exists directly under start_path."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            wiki = tmp_path / "wiki"
            canon = wiki / "_canon"
            canon.mkdir(parents=True)
            (canon / "roster.yaml").write_text("entities: []\n", encoding="utf-8")
            result = frontmatter.find_canon_dir(wiki)
            self.assertEqual(result, canon)

    def test_find_canon_dir_v1_1_consumer_layout(self):
        """v1.1 consumer: <root>/Biz.Automation/wikisys.<name>/_canon/."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            consumer = tmp_path / "consumer"
            wiki_git = consumer / "wiki.mentor" / "git"
            wiki_git.mkdir(parents=True)
            (wiki_git / "Home.md").write_text("# Home\n", encoding="utf-8")
            (consumer / "CLAUDE.md").write_text("# C\n", encoding="utf-8")
            (consumer / "emcc.modules.json").write_text("{}\n", encoding="utf-8")
            canon = consumer / "Biz.Automation" / "wikisys.mentor" / "_canon"
            canon.mkdir(parents=True)
            (canon / "roster.yaml").write_text("entities: []\n", encoding="utf-8")
            # Start from wiki_git (the v1.1 WIKI_ROOT for a consumer)
            result = frontmatter.find_canon_dir(wiki_git)
            self.assertEqual(result, canon)

    def test_find_canon_dir_v1_1_library_install_layout(self):
        """v1.1 Library install: <root>/Biz.Automation/wikisys.library/_canon/."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            install = tmp_path / "library"
            wiki_git = install / "wiki.codex" / "git"
            wiki_git.mkdir(parents=True)
            (wiki_git / "Home.md").write_text("# Home\n", encoding="utf-8")
            (install / "CLAUDE.md").write_text("# C\n", encoding="utf-8")
            (install / "module.json").write_text("{}\n", encoding="utf-8")
            canon = install / "Biz.Automation" / "wikisys.library" / "_canon"
            canon.mkdir(parents=True)
            (canon / "roster.yaml").write_text("entities: []\n", encoding="utf-8")
            result = frontmatter.find_canon_dir(wiki_git)
            self.assertEqual(result, canon)

    def test_find_canon_dir_missing_raises_file_not_found(self):
        """No canon anywhere -> FileNotFoundError."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            wiki = tmp_path / "wiki"
            wiki.mkdir(parents=True)
            with self.assertRaises(FileNotFoundError):
                frontmatter.find_canon_dir(wiki)

    def test_find_config_dir_v1_0_layout_returns_direct_child(self):
        """v1.0 wiki: <wiki>/_config/ exists directly under start_path."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            wiki = tmp_path / "wiki"
            cfg = wiki / "_config"
            cfg.mkdir(parents=True)
            (cfg / "concept_coverage.yaml").write_text("min_mentions: 2\n", encoding="utf-8")
            result = frontmatter.find_config_dir(wiki)
            self.assertEqual(result, cfg)

    def test_find_config_dir_v1_1_consumer_layout(self):
        """v1.1 consumer: <root>/Biz.Automation/wikisys.<name>/_config/."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            consumer = tmp_path / "consumer"
            wiki_git = consumer / "wiki.mentor" / "git"
            wiki_git.mkdir(parents=True)
            (wiki_git / "Home.md").write_text("# Home\n", encoding="utf-8")
            (consumer / "CLAUDE.md").write_text("# C\n", encoding="utf-8")
            (consumer / "emcc.modules.json").write_text("{}\n", encoding="utf-8")
            cfg = consumer / "Biz.Automation" / "wikisys.mentor" / "_config"
            cfg.mkdir(parents=True)
            (cfg / "concept_coverage.yaml").write_text("min_mentions: 2\n", encoding="utf-8")
            result = frontmatter.find_config_dir(wiki_git)
            self.assertEqual(result, cfg)

    def test_find_config_dir_missing_raises_file_not_found(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            wiki = tmp_path / "wiki"
            wiki.mkdir(parents=True)
            with self.assertRaises(FileNotFoundError):
                frontmatter.find_config_dir(wiki)

    def test_find_decisions_dir_v1_0_layout_returns_direct_child(self):
        """v1.0 wiki: <wiki>/_decisions/ exists directly under start_path."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            wiki = tmp_path / "wiki"
            decisions = wiki / "_decisions"
            decisions.mkdir(parents=True)
            (decisions / "ingest-log.md").write_text("# log\n", encoding="utf-8")
            result = frontmatter.find_decisions_dir(wiki)
            self.assertEqual(result, decisions)

    def test_find_decisions_dir_v1_1_consumer_layout(self):
        """v1.1 consumer: <root>/Biz.Automation/wikisys.<name>/_decisions/."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            consumer = tmp_path / "consumer"
            wiki_git = consumer / "wiki.mentor" / "git"
            wiki_git.mkdir(parents=True)
            (wiki_git / "Home.md").write_text("# Home\n", encoding="utf-8")
            (consumer / "CLAUDE.md").write_text("# C\n", encoding="utf-8")
            (consumer / "emcc.modules.json").write_text("{}\n", encoding="utf-8")
            decisions = consumer / "Biz.Automation" / "wikisys.mentor" / "_decisions"
            decisions.mkdir(parents=True)
            (decisions / "ingest-log.md").write_text("# log\n", encoding="utf-8")
            result = frontmatter.find_decisions_dir(wiki_git)
            self.assertEqual(result, decisions)

    def test_find_install_root_recognizes_consumer_emcc_modules_json(self):
        """v1.1 consumer marker: CLAUDE.md + emcc.modules.json co-exist."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            consumer = tmp_path / "consumer"
            consumer.mkdir(parents=True)
            (consumer / "CLAUDE.md").write_text("# C\n", encoding="utf-8")
            (consumer / "emcc.modules.json").write_text("{}\n", encoding="utf-8")
            result = frontmatter._find_install_root(consumer)
            self.assertEqual(result, consumer)

    def test_find_install_root_recognizes_library_module_json(self):
        """v1.1 Library marker: CLAUDE.md + module.json co-exist."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            install = tmp_path / "library"
            install.mkdir(parents=True)
            (install / "CLAUDE.md").write_text("# C\n", encoding="utf-8")
            (install / "module.json").write_text("{}\n", encoding="utf-8")
            result = frontmatter._find_install_root(install)
            self.assertEqual(result, install)

    def test_find_install_root_returns_none_when_no_marker(self):
        """No CLAUDE.md or no module-json companion -> None."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            empty = tmp_path / "empty"
            empty.mkdir(parents=True)
            self.assertIsNone(frontmatter._find_install_root(empty))


if __name__ == "__main__":
    unittest.main()
