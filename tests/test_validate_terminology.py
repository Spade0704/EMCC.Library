"""Tests for _scripts/validate_terminology.py — P6 first validator."""

import io
import shutil
import sys
import unittest
from contextlib import redirect_stderr
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import validate_terminology
from _lib import frontmatter


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


# Fixture state under default rules (forbidden_terms.yaml shipped with the
# fixture has 3 rules: BadTerm/error/all, InternalOnly/warning/audience,
# PublicOnly/info/internal). Pages: Home (internal), Glossary (public),
# Foo (internal), Bar (internal+allow_forbidden_terms), Baz (confidential).
#
# Default expected findings (sorted by severity, then relpath, then line):
#   error   00-Start-Here/Glossary.md  line 17  BadTerm
#   error   01-Domain/Foo.md           line 15  BadTerm  (plain prose)
#   error   01-Domain/Foo.md           line 28  BadTerm  (post-fences)
#   error   02-Other/Baz.md            line 15  BadTerm
#   error   Home.md                    line 14  BadTerm
#   warning 00-Start-Here/Glossary.md  line 15  InternalOnly
#   info    Home.md                    line 16  PublicOnly
# Total: 7 findings, 4 pages_scanned (Bar excluded).


class ValidateTerminologyTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.wiki = Path(self._tmpdir.name) / "wiki"
        shutil.copytree(FIXTURE_ROOT, self.wiki)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _read_dashboard(self):
        return (self.wiki / "_dashboards" / "terminology.md").read_text(
            encoding="utf-8"
        )

    def _set_rules(self, yaml_text):
        path = self.wiki / "_config" / "forbidden_terms.yaml"
        path.write_text(yaml_text, encoding="utf-8")

    def _remove_rules(self):
        path = self.wiki / "_config" / "forbidden_terms.yaml"
        if path.exists():
            path.unlink()

    def _set_visibility(self, rel_path, value):
        page = self.wiki / rel_path
        text = page.read_text(encoding="utf-8")
        new_lines = []
        for line in text.split("\n"):
            if line.startswith("visibility:"):
                new_lines.append("visibility: " + value)
            else:
                new_lines.append(line)
        page.write_text("\n".join(new_lines), encoding="utf-8")

    def _findings_for(self, summary, page_name):
        return [f for f in summary["findings"]
                if f["page_path"].name == page_name]

    # --- Return contract (4) -------------------------------------------------

    def test_run_returns_dashboard_path(self):
        summary = validate_terminology.run(self.wiki)
        self.assertEqual(
            summary["dashboard_path"],
            self.wiki / "_dashboards" / "terminology.md",
        )
        self.assertTrue(summary["dashboard_path"].exists())

    def test_summary_dict_has_findings_and_pages_scanned(self):
        summary = validate_terminology.run(self.wiki)
        self.assertIn("findings", summary)
        self.assertIn("pages_scanned", summary)
        self.assertEqual(summary["pages_scanned"], 4)
        self.assertEqual(len(summary["findings"]), 7)
        # finding-dict shape
        first = summary["findings"][0]
        self.assertEqual(
            set(first.keys()),
            {"severity", "page_path", "line", "message", "rule"},
        )

    def test_dashboard_frontmatter_has_5_canonical_fields(self):
        validate_terminology.run(self.wiki)
        text = self._read_dashboard()
        fm = frontmatter.parse_frontmatter(text)
        self.assertEqual(fm["title"], "Terminology Dashboard")
        self.assertEqual(fm["type"], "dashboard")
        self.assertEqual(fm["visibility"], "internal")
        self.assertIs(fm["generated"], True)
        self.assertEqual(fm["last_updated"], date.today().isoformat())

    def test_dashboard_summary_lines_use_bold_labels(self):
        validate_terminology.run(self.wiki)
        text = self._read_dashboard()
        self.assertIn("**Pages scanned:** 4", text)
        self.assertIn(
            "**Findings:** 7 (5 errors / 1 warning / 1 info)",
            text,
        )

    # --- Severity (3) --------------------------------------------------------

    def test_severity_error_rule_fires_on_BadTerm(self):
        summary = validate_terminology.run(self.wiki)
        errors = [f for f in summary["findings"] if f["severity"] == "error"]
        self.assertTrue(all("BadTerm" in f["message"] for f in errors))
        self.assertEqual(len(errors), 5)

    def test_severity_warning_rule_fires_on_InternalOnly(self):
        summary = validate_terminology.run(self.wiki)
        warnings = [f for f in summary["findings"] if f["severity"] == "warning"]
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["page_path"].name, "Glossary.md")
        self.assertIn("InternalOnly", warnings[0]["message"])

    def test_severity_info_rule_fires_on_PublicOnly(self):
        summary = validate_terminology.run(self.wiki)
        infos = [f for f in summary["findings"] if f["severity"] == "info"]
        self.assertEqual(len(infos), 1)
        self.assertEqual(infos[0]["page_path"].name, "Home.md")
        self.assertIn("PublicOnly", infos[0]["message"])

    # --- Context (4) ---------------------------------------------------------

    def test_context_all_matches_internal_public_and_confidential(self):
        # BadTerm (context: all) should fire on Home (internal), Glossary
        # (public), Foo (internal), and Baz (confidential).
        summary = validate_terminology.run(self.wiki)
        badterm_pages = sorted({
            f["page_path"].name for f in summary["findings"]
            if "BadTerm" in f["message"]
        })
        self.assertEqual(
            badterm_pages,
            ["Baz.md", "Foo.md", "Glossary.md", "Home.md"],
        )

    def test_context_audience_only_matches_public_visibility(self):
        # InternalOnly is planted in both Glossary (public) and Baz
        # (confidential); audience context fires only on Glossary.
        summary = validate_terminology.run(self.wiki)
        internalonly_pages = {
            f["page_path"].name for f in summary["findings"]
            if "InternalOnly" in f["message"]
        }
        self.assertEqual(internalonly_pages, {"Glossary.md"})

    def test_context_internal_only_matches_internal_visibility(self):
        # PublicOnly is planted in Home (internal). It should fire there
        # only — not in any non-internal pages (we add a public planted copy
        # for this test to be sure context filtering excludes public).
        self._set_visibility("00-Start-Here/Glossary.md", "public")
        page = self.wiki / "00-Start-Here" / "Glossary.md"
        page.write_text(
            page.read_text(encoding="utf-8") + "\nPublicOnly here.\n",
            encoding="utf-8",
        )
        summary = validate_terminology.run(self.wiki)
        publiconly_pages = {
            f["page_path"].name for f in summary["findings"]
            if "PublicOnly" in f["message"]
        }
        self.assertEqual(publiconly_pages, {"Home.md"})

    def test_visibility_confidential_matches_only_context_all_rules(self):
        # Baz is confidential. Of the 3 rules, only BadTerm (context: all)
        # should fire on Baz; InternalOnly (audience) and PublicOnly
        # (internal) must not.
        summary = validate_terminology.run(self.wiki)
        baz_findings = self._findings_for(summary, "Baz.md")
        self.assertEqual(len(baz_findings), 1)
        self.assertIn("BadTerm", baz_findings[0]["message"])

    # --- Escape hatch + counts (1) -------------------------------------------

    def test_allow_forbidden_terms_skips_page_and_excludes_from_pages_scanned(self):
        summary = validate_terminology.run(self.wiki)
        # Bar.md has allow_forbidden_terms: true and contains BadTerm in body;
        # no findings should reference it.
        bar_findings = self._findings_for(summary, "Bar.md")
        self.assertEqual(bar_findings, [])
        # And pages_scanned excludes Bar (4 scanned, not 5).
        self.assertEqual(summary["pages_scanned"], 4)

    # --- Code-block stripping (4) --------------------------------------------

    def test_fenced_backtick_block_not_matched(self):
        # Foo.md lines 17–20 are a ```python fenced block with BadTerm inside.
        summary = validate_terminology.run(self.wiki)
        foo_findings = self._findings_for(summary, "Foo.md")
        forbidden_lines = {18, 19, 20}
        for f in foo_findings:
            self.assertNotIn(
                f["line"], forbidden_lines,
                "fenced ```block should be stripped; got finding at line {}".format(f["line"]),
            )

    def test_fenced_tilde_block_not_matched(self):
        # Foo.md lines 22–24 are a ~~~text fenced block with BadTerm inside.
        summary = validate_terminology.run(self.wiki)
        foo_findings = self._findings_for(summary, "Foo.md")
        forbidden_lines = {22, 23, 24}
        for f in foo_findings:
            self.assertNotIn(
                f["line"], forbidden_lines,
                "fenced ~~~ block should be stripped; got finding at line {}".format(f["line"]),
            )

    def test_inline_backtick_span_not_matched(self):
        # Foo.md line 26 has `BadTerm` inside a single-backtick span.
        summary = validate_terminology.run(self.wiki)
        foo_findings = self._findings_for(summary, "Foo.md")
        for f in foo_findings:
            self.assertNotEqual(
                f["line"], 26,
                "inline `BadTerm` should be stripped; got finding at line 26",
            )

    def test_line_numbers_preserved_after_strip(self):
        # The post-fences plain-prose BadTerm in Foo.md sits at file line 28.
        # If strip deleted instead of replacing-with-whitespace, the body
        # would be shorter and this match would land at a lower line.
        summary = validate_terminology.run(self.wiki)
        foo_findings = self._findings_for(summary, "Foo.md")
        post_fence_lines = [f["line"] for f in foo_findings if f["line"] > 24]
        self.assertEqual(post_fence_lines, [28])

    # --- File-relative line numbers (1, NEW per push-back) -------------------

    def test_finding_line_is_file_relative_not_body_relative(self):
        # Foo.md frontmatter is 9 lines (lines 1–9). The first BadTerm match
        # sits at body line 6 — body-relative would be 6, file-relative is
        # 6 + 9 = 15. Findings must report file-relative.
        summary = validate_terminology.run(self.wiki)
        foo_findings = self._findings_for(summary, "Foo.md")
        self.assertEqual(len(foo_findings), 2)
        # First finding (sorted by line) is the pre-fence prose match.
        first = sorted(foo_findings, key=lambda f: f["line"])[0]
        self.assertEqual(
            first["line"], 15,
            "expected file-relative 15; body-relative would be 6, got {}"
            .format(first["line"]),
        )

    # --- Multiple matches (1) ------------------------------------------------

    def test_multiple_matches_per_rule_per_page_reported_separately(self):
        summary = validate_terminology.run(self.wiki)
        foo_badterm = [
            f for f in summary["findings"]
            if f["page_path"].name == "Foo.md" and "BadTerm" in f["message"]
        ]
        self.assertEqual(len(foo_badterm), 2)
        self.assertEqual(
            sorted(f["line"] for f in foo_badterm),
            [15, 28],
        )

    # --- Walker (1) ----------------------------------------------------------

    def test_walker_skips_underscore_prefixed_paths(self):
        # Plant a forbidden term inside _config/ — walker must not find it.
        leak = self.wiki / "_config" / "leak_page.md"
        leak.write_text(
            "---\nvisibility: internal\n---\n\nThis BadTerm must not be scanned.\n",
            encoding="utf-8",
        )
        summary = validate_terminology.run(self.wiki)
        for f in summary["findings"]:
            self.assertNotEqual(f["page_path"].name, "leak_page.md")

    # --- Config edge cases (3) -----------------------------------------------

    def test_missing_config_file_yields_zero_findings_exit_zero(self):
        self._remove_rules()
        summary = validate_terminology.run(self.wiki)
        self.assertEqual(summary["findings"], [])
        # Pages still walked + counted (escape-hatch page still excluded).
        self.assertEqual(summary["pages_scanned"], 4)

    def test_malformed_severity_rule_skipped_with_stderr_warning(self):
        self._set_rules(
            "rules:\n"
            '  - pattern: "BadTerm"\n'
            "    severity: catastrophic\n"
            '    message: "bad sev"\n'
            "    context: all\n"
            '  - pattern: "BadTerm"\n'
            "    severity: error\n"
            '    message: "good rule"\n'
            "    context: all\n"
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            summary = validate_terminology.run(self.wiki)
        self.assertIn("invalid severity", buf.getvalue())
        self.assertIn("catastrophic", buf.getvalue())
        # Valid rule still applied — BadTerm matches still reported.
        self.assertGreater(len(summary["findings"]), 0)
        for f in summary["findings"]:
            self.assertEqual(f["severity"], "error")

    def test_uncompilable_regex_rule_skipped_with_stderr_warning(self):
        self._set_rules(
            "rules:\n"
            '  - pattern: "(unclosed_group"\n'
            "    severity: error\n"
            '    message: "bad regex"\n'
            "    context: all\n"
            '  - pattern: "BadTerm"\n'
            "    severity: error\n"
            '    message: "good rule"\n'
            "    context: all\n"
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            summary = validate_terminology.run(self.wiki)
        self.assertIn("regex compile error", buf.getvalue())
        # Valid rule still applied.
        self.assertGreater(len(summary["findings"]), 0)

    # --- Dashboard rendering (3) ---------------------------------------------

    def test_findings_grouped_by_severity_order_empty_severities_omitted(self):
        # All three severities populated under default rules.
        validate_terminology.run(self.wiki)
        text = self._read_dashboard()
        idx_error = text.find("## error")
        idx_warning = text.find("## warning")
        idx_info = text.find("## info")
        self.assertNotEqual(idx_error, -1)
        self.assertNotEqual(idx_warning, -1)
        self.assertNotEqual(idx_info, -1)
        self.assertLess(idx_error, idx_warning)
        self.assertLess(idx_warning, idx_info)

        # Now restrict to error-only rules — warning/info sections must be omitted.
        self._set_rules(
            "rules:\n"
            '  - pattern: "BadTerm"\n'
            "    severity: error\n"
            '    message: "BadTerm forbidden"\n'
            "    context: all\n"
        )
        validate_terminology.run(self.wiki)
        text = self._read_dashboard()
        self.assertIn("## error", text)
        self.assertNotIn("## warning", text)
        self.assertNotIn("## info", text)

    def test_empty_findings_dashboard_body_message(self):
        # No-op rules → no findings.
        self._set_rules(
            "rules:\n"
            '  - pattern: "ZZZ_NEVER_MATCHES_ZZZ"\n'
            "    severity: error\n"
            '    message: "n/a"\n'
            "    context: all\n"
        )
        summary = validate_terminology.run(self.wiki)
        self.assertEqual(summary["findings"], [])
        text = self._read_dashboard()
        self.assertIn("No terminology findings.", text)
        self.assertIn("**Pages scanned:** 4", text)
        self.assertIn("**Findings:** 0", text)

    def test_relative_paths_use_forward_slashes_in_dashboard_and_findings(self):
        summary = validate_terminology.run(self.wiki)
        # Findings have Path objects; rendered relpath uses as_posix().
        text = self._read_dashboard()
        self.assertIn("00-Start-Here/Glossary.md", text)
        self.assertIn("01-Domain/Foo.md", text)
        self.assertIn("02-Other/Baz.md", text)
        # Sanity: no backslash separators in any rendered rel path bullet.
        for line in text.split("\n"):
            if line.startswith("- "):
                self.assertNotIn("\\", line)


if __name__ == "__main__":
    unittest.main()
