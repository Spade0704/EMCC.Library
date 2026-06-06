"""Tests for _scripts/_lib/doc_lint.py::check_consequence — caution-lint spike.

The council-hardened, delta-force-descoped consequence/cite lint
(EMCC/tasks/council/2026-06-06-tiered-caution-index.md +
EMCC.DFDU/tasks/delta-force/2026-06-06-caution-lint.md):

- A per-page `consequence: high|low` frontmatter field; absent OR unrecognized
  resolves to HIGH (fail-safe — never silently LOW).
- A HIGH page must carry a non-empty `cite_anchor`.
- Report-only by default (enforce=False -> WARNING, ok=True) so the lint runs
  across an un-migrated wiki without red-barring it; enforce=True promotes the
  finding to an ERROR (ok=False), opt-in per wiki once migrated.
- Read-only: never modifies the file (so the byte-for-byte survival of
  effectivity variants is trivially preserved — block-level normalization is a
  SEPARATE, out-of-scope experiment).

The `consequence` field name is provisional for the spike; the final contract
is locked at canon promotion (a later, gated step). No canon files touched.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _lib import doc_lint


def _write(p: Path, content: str) -> None:
    p.write_text(content, encoding="utf-8")


def _page(consequence=None, cite=None, body="# Body\n\nText.\n", extra_fm=""):
    """Build a synthetic wiki page with optional consequence + cite_anchor fm."""
    lines = ["---", "title: Sample Page"]
    if consequence is not None:
        lines.append(f"consequence: {consequence}")
    if cite is not None:
        lines.append(f'cite_anchor: "{cite}"')
    if extra_fm:
        lines.append(extra_fm)
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + "\n" + body


# Two byte-identical procedure blocks for two effectivity ranges — the real
# aviation Unreliable_Airspeed shape (the lint must never rewrite/dedupe them).
_TWO_VARIANT = _page(
    consequence="high",
    cite="FCTM PR-AEP-NAV-00019312 / 22 APR 25",
    body=(
        "# Unreliable Airspeed Indications\n\n"
        "Ident.: 0001001 Applicable to: A6-AEB, A6-AEC\n\n"
        "PROCEDURE BLOCK ALPHA — verbatim memory items.\n\n"
        "Ident.: 0002001 Applicable to: A6-AEN, A6-AEO\n\n"
        "PROCEDURE BLOCK ALPHA — verbatim memory items.\n"
    ),
)


class TestCheckConsequenceReportOnly(unittest.TestCase):
    def test_high_missing_cite_reportonly_warns_never_raises(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "page.md"
            _write(p, _page(consequence="high"))
            r = doc_lint.check_consequence(p, enforce=False)  # must not raise
            self.assertTrue(r.ok)               # report-only: still ok
            self.assertEqual(r.consequence, "high")
            self.assertTrue(r.warnings)         # but it warns
            self.assertFalse(r.errors)

    def test_high_missing_cite_enforce_is_error(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "page.md"
            _write(p, _page(consequence="high"))
            r = doc_lint.check_consequence(p, enforce=True)
            self.assertFalse(r.ok)
            self.assertTrue(r.errors)
            self.assertFalse(r.warnings)


class TestCheckConsequenceTierResolution(unittest.TestCase):
    def test_low_passes_both_modes(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "page.md"
            _write(p, _page(consequence="low"))   # no cite needed
            for enforce in (False, True):
                r = doc_lint.check_consequence(p, enforce=enforce)
                self.assertTrue(r.ok)
                self.assertEqual(r.consequence, "low")
                self.assertFalse(r.errors)
                self.assertFalse(r.warnings)

    def test_high_with_cite_passes_both_modes(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "page.md"
            _write(p, _page(consequence="high", cite="FCOM LIM 27-10"))
            for enforce in (False, True):
                r = doc_lint.check_consequence(p, enforce=enforce)
                self.assertTrue(r.ok)
                self.assertEqual(r.consequence, "high")
                self.assertEqual(r.cite_anchor, "FCOM LIM 27-10")
                self.assertFalse(r.errors)
                self.assertFalse(r.warnings)

    def test_absent_field_resolves_high_failsafe(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "page.md"
            _write(p, _page(consequence=None))      # no consequence key at all
            r = doc_lint.check_consequence(p, enforce=True)
            self.assertEqual(r.consequence, "high")  # fail-safe
            self.assertFalse(r.field_present)
            self.assertFalse(r.ok)                    # high + no cite + enforce
            # message must explain the fail-safe so it isn't a silent trap
            self.assertTrue(any("fail-safe" in e.lower() for e in r.errors))

    def test_unrecognized_value_resolves_high_failsafe(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "page.md"
            _write(p, _page(consequence="medium"))   # not high|low
            r = doc_lint.check_consequence(p, enforce=False)
            self.assertEqual(r.consequence, "high")  # fail-safe
            self.assertFalse(r.field_present)
            self.assertTrue(r.warnings)

    def test_case_insensitive_low(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "page.md"
            _write(p, _page(consequence="LOW"))
            r = doc_lint.check_consequence(p, enforce=True)
            self.assertEqual(r.consequence, "low")
            self.assertTrue(r.ok)


class TestCheckConsequenceReadOnly(unittest.TestCase):
    def test_two_variant_blocks_survive_and_file_unchanged(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "unreliable_airspeed.md"
            _write(p, _TWO_VARIANT)
            before = p.read_bytes()
            r = doc_lint.check_consequence(p, enforce=True)
            after = p.read_bytes()
            self.assertEqual(before, after)          # read-only: byte-identical
            # both effectivity variants still present, not deduped
            self.assertEqual(after.decode("utf-8").count("PROCEDURE BLOCK ALPHA"), 2)
            self.assertTrue(r.ok)                     # high + cite present


if __name__ == "__main__":
    unittest.main()
