"""Tests for _scripts/_lib/topics.py::load_cross_link_config (S047-T-XL-3a)."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _lib.topics import load_cross_link_config, _DEFAULT_CROSS_LINK_CONFIG


class TestLoadCrossLinkConfig(unittest.TestCase):
    def test_load_cross_link_config_default_fallback_missing_file(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            cfg = load_cross_link_config(wiki)
            self.assertEqual(
                cfg["tfidf"]["min_similarity"],
                _DEFAULT_CROSS_LINK_CONFIG["tfidf"]["min_similarity"],
            )
            self.assertEqual(
                cfg["plugin"]["module_path"],
                _DEFAULT_CROSS_LINK_CONFIG["plugin"]["module_path"],
            )

    def test_load_cross_link_config_happy_path_parses_nested(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            config_dir = wiki / "_config"
            config_dir.mkdir()
            (config_dir / "cross_link.yaml").write_text(
                "tfidf:\n"
                "  min_similarity: 0.5\n"
                "  max_links_per_page: 12\n"
                "plugin:\n"
                "  module_path: custom_plugin\n"
                "  weight: 0.75\n",
                encoding="utf-8",
            )
            cfg = load_cross_link_config(wiki)
            self.assertEqual(cfg["tfidf"]["min_similarity"], 0.5)
            self.assertEqual(cfg["tfidf"]["max_links_per_page"], 12)
            self.assertEqual(cfg["plugin"]["module_path"], "custom_plugin")
            self.assertEqual(cfg["plugin"]["weight"], 0.75)
            # Missing section keys fall back to defaults.
            self.assertEqual(
                cfg["tfidf"]["scan_fields"],
                _DEFAULT_CROSS_LINK_CONFIG["tfidf"]["scan_fields"],
            )

    def test_load_cross_link_config_malformed_fallback_to_defaults(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            config_dir = wiki / "_config"
            config_dir.mkdir()
            (config_dir / "cross_link.yaml").write_text(
                "not yaml at all just random text { with } brackets [ ]\n"
                "  invalid indented thing\n",
                encoding="utf-8",
            )
            cfg = load_cross_link_config(wiki)
            # Graceful degradation: defaults returned on malformed config.
            self.assertEqual(
                cfg["tfidf"]["min_similarity"],
                _DEFAULT_CROSS_LINK_CONFIG["tfidf"]["min_similarity"],
            )


if __name__ == "__main__":
    unittest.main()
