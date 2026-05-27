"""Tests for _scripts/_lib/config_loader.py — S034-T8 promoted helpers."""

import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory

from _lib import frontmatter
from _lib import config_loader
from _lib.config_loader import ConfigYamlError, load_config_yaml


class MissingFileTests(unittest.TestCase):

    def test_missing_file_returns_empty_list(self):
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does_not_exist.yaml"
            out = load_config_yaml(missing, "rules")
            self.assertEqual(out, [])


class WrapperKeyTests(unittest.TestCase):

    def test_wrapper_key_missing_returns_empty(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.yaml"
            p.write_text("other_key: value\n", encoding="utf-8")
            out = load_config_yaml(p, "rules")
            self.assertEqual(out, [])

    def test_wrapper_value_not_list_raises_ConfigYamlError(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.yaml"
            p.write_text("rules: not_a_list\n", encoding="utf-8")
            with self.assertRaises(ConfigYamlError) as ctx:
                load_config_yaml(p, "rules")
            self.assertIn("'rules'", str(ctx.exception))
            self.assertIn("list-of-mappings", str(ctx.exception))


class HappyPathTests(unittest.TestCase):

    def test_returns_all_valid_entries(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.yaml"
            p.write_text(
                "rules:\n"
                "  - pattern: foo\n"
                "    severity: error\n"
                "    message: bar\n"
                "  - pattern: baz\n"
                "    severity: warning\n"
                "    message: qux\n",
                encoding="utf-8",
            )
            out = load_config_yaml(
                p, "rules", required_keys=("pattern", "severity", "message")
            )
            self.assertEqual(len(out), 2)
            self.assertEqual(out[0]["pattern"], "foo")
            self.assertEqual(out[1]["severity"], "warning")


class PerEntryWarnSkipTests(unittest.TestCase):

    def test_non_mapping_entry_warn_skipped(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.yaml"
            # parse_config_yaml supports flow-list values at top level.
            p.write_text("rules: [oops]\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stderr(buf):
                out = load_config_yaml(p, "rules", entity_noun="rule")
            self.assertEqual(out, [])
            self.assertIn("warning: skipping malformed rule 1: not a mapping",
                          buf.getvalue())

    def test_missing_required_keys_warn_skipped(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.yaml"
            p.write_text(
                "pairs:\n"
                "  - source: only_source.md\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stderr(buf):
                out = load_config_yaml(
                    p, "pairs",
                    required_keys=("source", "derived"),
                    entity_noun="pair",
                )
            self.assertEqual(out, [])
            self.assertIn(
                "warning: skipping malformed pair 1: missing keys ['derived']",
                buf.getvalue(),
            )

    def test_required_keys_empty_tuple_skips_validation(self):
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.yaml"
            p.write_text(
                "rules:\n"
                "  - any_field: any_value\n",
                encoding="utf-8",
            )
            out = load_config_yaml(p, "rules")
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0], {"any_field": "any_value"})


class ConfigYamlErrorReexportTests(unittest.TestCase):

    def test_reexport_identity(self):
        # Same class object via assignment-style re-export — `except` on either
        # spelling catches the same exception.
        self.assertIs(config_loader.ConfigYamlError, frontmatter.ConfigYamlError)


class WarnByteIdenticalPinTests(unittest.TestCase):

    def test_warn_message_format_pin(self):
        # AC4 invariant pin. The WARN strings are how P6/P8/P10 pre-refactor
        # consumers emitted stderr. Drift here breaks byte-identical stderr
        # scrollback fidelity. Edit only with paired pre-refactor format
        # change (which would itself be a behavioral regression).
        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.yaml"
            p.write_text(
                "rules: [oops, also_bad]\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stderr(buf):
                load_config_yaml(p, "rules", entity_noun="rule")
            warns = buf.getvalue().splitlines()
            self.assertEqual(
                warns[0],
                "warning: skipping malformed rule 1: not a mapping",
            )
            self.assertEqual(
                warns[1],
                "warning: skipping malformed rule 2: not a mapping",
            )

        with TemporaryDirectory() as tmp:
            p = Path(tmp) / "config.yaml"
            p.write_text(
                "pairs:\n"
                "  - source: only_source.md\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stderr(buf):
                load_config_yaml(
                    p, "pairs",
                    required_keys=("source", "derived"),
                    entity_noun="pair",
                )
            self.assertIn(
                "warning: skipping malformed pair 1: missing keys ['derived']",
                buf.getvalue(),
            )


if __name__ == "__main__":
    unittest.main()
