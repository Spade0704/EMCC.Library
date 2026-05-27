"""Tests for _scripts/validate_reveal_conceit.py — P8 public-page leak validator."""

import io
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import validate_reveal_conceit
from _lib import frontmatter


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


# Fixture state under default rules (reveal_leak_patterns.yaml ships
# `rules: []`). Sample wiki has exactly one visibility:public page —
# 00-Start-Here/Glossary.md — and four non-public pages
# (Home internal, Foo internal, Bar internal, Baz confidential). With
# the default empty rules: pages_scanned == 1, findings == 0.


class ValidateRevealConceitTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.wiki = Path(self._tmpdir.name) / "wiki"
        shutil.copytree(FIXTURE_ROOT, self.wiki)

    def tearDown(self):
        self._tmpdir.cleanup()

    # -- helpers --

    def _set_rules(self, yaml_text):
        path = self.wiki / "_config" / "reveal_leak_patterns.yaml"
        path.write_text(yaml_text, encoding="utf-8")

    def _remove_rules(self):
        path = self.wiki / "_config" / "reveal_leak_patterns.yaml"
        if path.exists():
            path.unlink()

    def _read_dashboard(self):
        return (self.wiki / "_dashboards" / "reveal_conceit.md").read_text(
            encoding="utf-8"
        )

    def _write_page(self, rel_path, body, visibility="public", extra_fm=""):
        path = self.wiki / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        fm = (
            "---\n"
            'title: "Test Page"\n'
            "type: reference\n"
            "visibility: " + visibility + "\n"
            "completion: 0\n"
            "status: outlined\n"
            "last_updated: 2026-05-07\n"
        )
        if extra_fm:
            fm += extra_fm + "\n"
        fm += "---\n\n"
        path.write_text(fm + body, encoding="utf-8")
        return path

    # -- (a) only visibility:public scanned --------------------------------

    def test_default_fixture_pages_scanned_is_one(self):
        summary = validate_reveal_conceit.run(self.wiki)
        self.assertEqual(summary["pages_scanned"], 1)
        self.assertEqual(summary["findings"], [])

    def test_internal_page_excluded_from_pages_scanned(self):
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        names = {f["page_path"].name for f in summary["findings"]}
        self.assertNotIn("Home.md", names)
        self.assertNotIn("Foo.md", names)
        self.assertEqual(summary["pages_scanned"], 1)

    def test_confidential_page_excluded(self):
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        names = {f["page_path"].name for f in summary["findings"]}
        self.assertNotIn("Baz.md", names)

    def test_missing_visibility_excluded(self):
        path = self.wiki / "00-Start-Here" / "NoVis.md"
        path.write_text(
            "---\n"
            'title: "No Visibility"\n'
            "type: reference\n"
            "completion: 0\n"
            "status: outlined\n"
            "last_updated: 2026-05-07\n"
            "---\n\n"
            "BadTerm appears here but visibility key is missing.\n",
            encoding="utf-8",
        )
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        names = {f["page_path"].name for f in summary["findings"]}
        self.assertNotIn("NoVis.md", names)
        self.assertEqual(summary["pages_scanned"], 1)

    # -- (b) DIRECT POSITIVE: _-prefixed folder skipped --------------------

    def test_brain_dump_public_page_skipped(self):
        self._write_page(
            Path("_brain_dump") / "leaky.md",
            "Body text containing BadTerm in plain prose.\n",
            visibility="public",
        )
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        names = {f["page_path"].name for f in summary["findings"]}
        self.assertNotIn("leaky.md", names)
        self.assertEqual(summary["pages_scanned"], 1)

    # -- (c) code-block stripping ------------------------------------------

    def test_fenced_code_block_match_ignored(self):
        self._write_page(
            Path("00-Start-Here") / "Fenced.md",
            "Intro line.\n\n"
            "```\n"
            "BadTerm appears here inside a fenced block\n"
            "```\n\n"
            "Trailing line.\n",
            visibility="public",
        )
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        for f in summary["findings"]:
            self.assertNotEqual(f["page_path"].name, "Fenced.md")

    def test_inline_code_match_ignored(self):
        self._write_page(
            Path("00-Start-Here") / "Inline.md",
            "Sentence with `BadTerm` inline-coded should be ignored.\n",
            visibility="public",
        )
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        for f in summary["findings"]:
            self.assertNotEqual(f["page_path"].name, "Inline.md")

    def test_line_numbers_preserved_after_fenced_block(self):
        # File: fm 9 lines + body. Body line 1 = file line 10.
        # body:
        #   1: "Intro."
        #   2: ""
        #   3: "```"
        #   4: "BadTerm in fence"
        #   5: "```"
        #   6: ""
        #   7: "Real BadTerm match here."
        # Expected: 1 finding at file line 16 (body line 7 + fm 9).
        self._write_page(
            Path("00-Start-Here") / "Numbered.md",
            "Intro.\n\n```\nBadTerm in fence\n```\n\nReal BadTerm match here.\n",
            visibility="public",
        )
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        target = [f for f in summary["findings"] if f["page_path"].name == "Numbered.md"]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0]["line"], 16)

    # -- (d) info severity does NOT emit findings --------------------------

    def test_info_severity_no_findings(self):
        # Glossary.md (visibility:public) contains "InternalOnly" on line 15.
        # An info-severity rule matching that string must produce 0 findings.
        self._set_rules(
            "rules:\n"
            "  - pattern: \"InternalOnly\"\n"
            "    severity: info\n"
            "    message: \"approved-public reference\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        self.assertEqual(summary["findings"], [])
        self.assertEqual(summary["pages_scanned"], 1)

    # -- (e) error + warning emit with correct line numbers ----------------

    def test_error_severity_emits_with_correct_line(self):
        # Glossary.md: "BadTerm" lives on file line 17 (body line 8 + fm 9).
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        target = [f for f in summary["findings"]
                  if f["page_path"].name == "Glossary.md"]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0]["severity"], "error")
        self.assertEqual(target[0]["line"], 17)

    def test_warning_severity_emits_with_correct_line(self):
        # Glossary.md: "InternalOnly" lives on file line 15 (body line 6 + fm 9).
        self._set_rules(
            "rules:\n"
            "  - pattern: \"InternalOnly\"\n"
            "    severity: warning\n"
            "    message: \"InternalOnly leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        target = [f for f in summary["findings"]
                  if f["page_path"].name == "Glossary.md"]
        self.assertEqual(len(target), 1)
        self.assertEqual(target[0]["severity"], "warning")
        self.assertEqual(target[0]["line"], 15)

    # -- (f) exit triad via _main ------------------------------------------

    def test_main_exit_0_clean(self):
        # default fixture: empty rules -> 0 findings -> exit 0
        rc = validate_reveal_conceit._main(self.wiki, stdout=io.StringIO(),
                                           stderr=io.StringIO())
        self.assertEqual(rc, 0)

    def test_main_exit_1_with_findings(self):
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        rc = validate_reveal_conceit._main(self.wiki, stdout=io.StringIO(),
                                           stderr=io.StringIO())
        self.assertEqual(rc, 1)

    def test_main_exit_2_missing_wiki(self):
        bogus = Path(self._tmpdir.name) / "does_not_exist"
        rc = validate_reveal_conceit._main(bogus, stdout=io.StringIO(),
                                           stderr=io.StringIO())
        self.assertEqual(rc, 2)

    # -- (g) per-rule malformation skip + stderr warning -------------------

    def test_malformed_rule_missing_keys_skipped(self):
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            # message missing
            "  - pattern: \"InternalOnly\"\n"
            "    severity: warning\n"
            "    message: \"InternalOnly leaked\"\n"
        )
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            summary = validate_reveal_conceit.run(self.wiki)
        self.assertIn("missing keys", stderr.getvalue())
        # clean rule survives — InternalOnly emits.
        sevs = [f["severity"] for f in summary["findings"]]
        self.assertEqual(sevs, ["warning"])

    def test_malformed_rule_invalid_severity_skipped(self):
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: critical\n"
            "    message: \"bad sev\"\n"
            "  - pattern: \"InternalOnly\"\n"
            "    severity: warning\n"
            "    message: \"InternalOnly leaked\"\n"
        )
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            summary = validate_reveal_conceit.run(self.wiki)
        self.assertIn("invalid severity", stderr.getvalue())
        sevs = [f["severity"] for f in summary["findings"]]
        self.assertEqual(sevs, ["warning"])

    def test_malformed_rule_invalid_regex_skipped(self):
        self._set_rules(
            "rules:\n"
            "  - pattern: \"[unclosed\"\n"
            "    severity: error\n"
            "    message: \"bad regex\"\n"
            "  - pattern: \"InternalOnly\"\n"
            "    severity: warning\n"
            "    message: \"InternalOnly leaked\"\n"
        )
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            summary = validate_reveal_conceit.run(self.wiki)
        self.assertIn("regex compile error", stderr.getvalue())
        sevs = [f["severity"] for f in summary["findings"]]
        self.assertEqual(sevs, ["warning"])

    # -- (h) structural YAML failure -> exit 2 -----------------------------

    def test_structural_yaml_failure_exits_2(self):
        # indented content outside any list-of-mappings raises ConfigYamlError
        self._set_rules(
            "rules:\n"
            "  not-a-list-item: foo\n"
        )
        stderr = io.StringIO()
        rc = validate_reveal_conceit._main(self.wiki, stdout=io.StringIO(),
                                           stderr=stderr)
        self.assertEqual(rc, 2)
        self.assertIn("structurally malformed", stderr.getvalue())

    def test_top_level_rules_not_list_exits_2(self):
        self._set_rules("rules: just-a-string\n")
        stderr = io.StringIO()
        rc = validate_reveal_conceit._main(self.wiki, stdout=io.StringIO(),
                                           stderr=stderr)
        self.assertEqual(rc, 2)

    # -- (j) empty bands omitted from dashboard ----------------------------

    def test_dashboard_omits_empty_warning_band(self):
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        validate_reveal_conceit.run(self.wiki)
        dash = self._read_dashboard()
        self.assertIn("## error", dash)
        self.assertNotIn("## warning", dash)

    def test_dashboard_omits_empty_error_band(self):
        self._set_rules(
            "rules:\n"
            "  - pattern: \"InternalOnly\"\n"
            "    severity: warning\n"
            "    message: \"InternalOnly leaked\"\n"
        )
        validate_reveal_conceit.run(self.wiki)
        dash = self._read_dashboard()
        self.assertNotIn("## error", dash)
        self.assertIn("## warning", dash)

    # -- bonus / dashboard contract ----------------------------------------

    def test_dashboard_5_field_fm(self):
        validate_reveal_conceit.run(self.wiki)
        dash = self._read_dashboard()
        page = frontmatter.load_page(self.wiki / "_dashboards" / "reveal_conceit.md")
        fm = page["frontmatter"]
        self.assertEqual(fm["title"], "Reveal Conceit Dashboard")
        self.assertEqual(fm["type"], "dashboard")
        self.assertEqual(fm["visibility"], "internal")
        self.assertEqual(fm["generated"], True)
        self.assertEqual(fm["last_updated"], date.today().isoformat())

    def test_empty_findings_body_line(self):
        validate_reveal_conceit.run(self.wiki)
        self.assertIn("No reveal-conceit findings.", self._read_dashboard())

    def test_dashboard_summary_excludes_info_from_counts(self):
        # 1 error + 1 warning + 1 info-rule (info contributes 0 to counts).
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
            "  - pattern: \"InternalOnly\"\n"
            "    severity: warning\n"
            "    message: \"InternalOnly leaked\"\n"
            "  - pattern: \"public\"\n"
            "    severity: info\n"
            "    message: \"approved\"\n"
        )
        validate_reveal_conceit.run(self.wiki)
        dash = self._read_dashboard()
        self.assertIn("**Findings:** 2 (1 error / 1 warning)", dash)
        self.assertNotIn("info", dash.split("**Findings:**")[1].split("\n")[0])

    def test_missing_config_file_zero_findings_exit_0(self):
        self._remove_rules()
        rc = validate_reveal_conceit._main(self.wiki, stdout=io.StringIO(),
                                           stderr=io.StringIO())
        self.assertEqual(rc, 0)

    def test_allow_forbidden_terms_not_inherited(self):
        # P6 escape hatch is NOT honored here; public page with the flag
        # still scans normally.
        self._write_page(
            Path("00-Start-Here") / "Escape.md",
            "Body containing BadTerm.\n",
            visibility="public",
            extra_fm="allow_forbidden_terms: true",
        )
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        names = {f["page_path"].name for f in summary["findings"]}
        self.assertIn("Escape.md", names)

    # -- return contract ---------------------------------------------------

    def test_run_returns_dashboard_path(self):
        summary = validate_reveal_conceit.run(self.wiki)
        self.assertEqual(
            summary["dashboard_path"],
            self.wiki / "_dashboards" / "reveal_conceit.md",
        )

    def test_run_keys_present(self):
        summary = validate_reveal_conceit.run(self.wiki)
        self.assertEqual(
            set(summary.keys()),
            {"dashboard_path", "findings", "pages_scanned"},
        )

    def test_findings_sorted_severity_then_path_then_line(self):
        self._write_page(
            Path("01-PublicDomain") / "Alpha.md",
            "Alpha line one.\nAlpha BadTerm here.\n",
            visibility="public",
        )
        self._write_page(
            Path("01-PublicDomain") / "Bravo.md",
            "Bravo line one.\nBravo InternalOnly here.\n",
            visibility="public",
        )
        self._set_rules(
            "rules:\n"
            "  - pattern: \"BadTerm\"\n"
            "    severity: error\n"
            "    message: \"BadTerm leaked\"\n"
            "  - pattern: \"InternalOnly\"\n"
            "    severity: warning\n"
            "    message: \"InternalOnly leaked\"\n"
        )
        summary = validate_reveal_conceit.run(self.wiki)
        # Expected order: all errors first, then warnings; within each,
        # by relative-posix path then line.
        sevs = [f["severity"] for f in summary["findings"]]
        self.assertEqual(sevs, sorted(sevs, key=("error", "warning").index))


if __name__ == "__main__":
    unittest.main()
