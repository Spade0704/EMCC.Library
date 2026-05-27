"""Tests for _scripts/_lib/dashboard.py — S034-T6 promoted helpers."""

import tempfile
import unittest
from datetime import date
from pathlib import Path

from _lib import dashboard


class SeverityOrderTests(unittest.TestCase):

    def test_severity_order_value(self):
        self.assertEqual(
            dashboard.SEVERITY_ORDER,
            ("error", "warning", "info"),
        )


class BandOrderTests(unittest.TestCase):

    def test_band_order_value(self):
        self.assertEqual(
            dashboard.BAND_ORDER,
            ("ready", "solid", "outlined", "gap"),
        )


class ConstantsAreTuples(unittest.TestCase):

    def test_severity_order_is_tuple(self):
        self.assertIsInstance(dashboard.SEVERITY_ORDER, tuple)

    def test_band_order_is_tuple(self):
        self.assertIsInstance(dashboard.BAND_ORDER, tuple)


class RenderFmHeaderTests(unittest.TestCase):

    def test_today_required_arg(self):
        # S037-T2 signature contract: `today` is REQUIRED (no default).
        # Locks LOCAL-date convention per architect-notes #36 + S035
        # hotfix `a6ce5e1`; mechanically prevents UTC-vs-LOCAL drift
        # recurrence by requiring callers to control the date source.
        with self.assertRaises(TypeError):
            dashboard.render_fm_header("Open Questions")

    def test_explicit_today_with_today_isoformat(self):
        # Covers the now-required-arg variant that was the pre-T2 default
        # branch's effective output. All 12 pre-T2 + P19 13th call sites
        # use `today=date.today().isoformat()`.
        lines = dashboard.render_fm_header(
            "Open Questions", today=date.today().isoformat()
        )
        self.assertEqual(len(lines), 7)
        self.assertEqual(lines[0], "---")
        self.assertEqual(lines[1], 'title: "Open Questions"')
        self.assertEqual(lines[2], "type: dashboard")
        self.assertEqual(lines[3], "visibility: internal")
        self.assertEqual(lines[4], "generated: true")
        self.assertEqual(lines[5], "last_updated: " + date.today().isoformat())
        self.assertEqual(lines[6], "---")

    def test_explicit_today(self):
        lines = dashboard.render_fm_header("Completion Dashboard", today="2026-05-15")
        self.assertEqual(lines[5], "last_updated: 2026-05-15")
        self.assertEqual(lines[1], 'title: "Completion Dashboard"')

    def test_byte_identical_to_legacy_inline(self):
        # AC3 invariant pinning — the legacy 7-line block as it appeared
        # in P4/P5/P6/P7/P8/P9 pre-promotion. If render_fm_header output
        # drifts from this exact sequence, downstream byte-identical
        # golden-compare will fail. Edit this test only with paired
        # render_fm_header format change.
        legacy = [
            "---",
            'title: "Cross-References Dashboard"',
            "type: dashboard",
            "visibility: internal",
            "generated: true",
            "last_updated: 2026-05-15",
            "---",
        ]
        self.assertEqual(
            dashboard.render_fm_header(
                "Cross-References Dashboard", today="2026-05-15"
            ),
            legacy,
        )


class GroupByFixedOrderTests(unittest.TestCase):

    def test_basic(self):
        items = [
            {"severity": "error", "msg": "a"},
            {"severity": "warning", "msg": "b"},
            {"severity": "error", "msg": "c"},
        ]
        out = dashboard.group_by_fixed_order(
            items,
            dashboard.SEVERITY_ORDER,
            lambda f: f["severity"],
        )
        self.assertEqual(list(out.keys()), ["error", "warning", "info"])
        self.assertEqual(len(out["error"]), 2)
        self.assertEqual(len(out["warning"]), 1)
        self.assertEqual(out["info"], [])

    def test_empty_class_returns_empty_list(self):
        out = dashboard.group_by_fixed_order(
            [],
            dashboard.BAND_ORDER,
            lambda f: f["band"],
        )
        self.assertEqual(out, {"ready": [], "solid": [], "outlined": [], "gap": []})

    def test_preserves_within_class_insertion_order(self):
        items = [
            {"band": "ready", "name": "p1"},
            {"band": "ready", "name": "p2"},
            {"band": "ready", "name": "p3"},
        ]
        out = dashboard.group_by_fixed_order(
            items,
            dashboard.BAND_ORDER,
            lambda f: f["band"],
        )
        self.assertEqual([p["name"] for p in out["ready"]], ["p1", "p2", "p3"])


class StripFindingBulletTests(unittest.TestCase):
    """S037-T1 SSOT helper — literal-slice + `startswith('- ')` prefix-guard.

    Consolidates 5 duplicate sites across P12/P13/P14/P15. Sites #1-#3
    (P12/P13) previously used `.lstrip('- ')` char-class strip; the
    closed footgun is pinned by test (d) below.
    """

    def test_strip_bullet_prefix_happy_path(self):
        self.assertEqual(dashboard.strip_finding_bullet("- foo"), "foo")

    def test_no_prefix_passthrough(self):
        self.assertEqual(dashboard.strip_finding_bullet("foo"), "foo")

    def test_single_dash_no_space_must_not_strip(self):
        self.assertEqual(dashboard.strip_finding_bullet("-foo"), "-foo")

    def test_negative_number_in_finding_text_preserved(self):
        # The closed `.lstrip('- ')` char-class footgun: legacy strip
        # at sites #1-#3 (P12/P13) would have produced "count delta: 3"
        # for any finding text containing `- count delta: -3` because
        # char-class strip eats both leading `-` AND ` `. Literal-slice
        # preserves the trailing `-3`.
        self.assertEqual(
            dashboard.strip_finding_bullet("- count delta: -3"),
            "count delta: -3",
        )

    def test_empty_string_passthrough(self):
        self.assertEqual(dashboard.strip_finding_bullet(""), "")


class WriteDashboardTests(unittest.TestCase):
    """S046-T0a SSOT helper — dashboard-write idiom (mkdir parents + UTF-8 write)."""

    def test_creates_parent_dir_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            wiki_root = Path(tmp)
            out_path = dashboard.write_dashboard(
                wiki_root, "_dashboards/sub/nested.md", "hello"
            )
            self.assertTrue(out_path.parent.is_dir())
            self.assertTrue(out_path.exists())

    def test_writes_exact_content_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            wiki_root = Path(tmp)
            content = "# Hdr\n\nbody with unicode: café — naïve\n"
            out_path = dashboard.write_dashboard(
                wiki_root, "_dashboards/x.md", content
            )
            # read_text uses universal newlines on Windows, matching the
            # text-mode write_text round-trip contract that aggregator
            # consumers rely on. Byte-level newline translation is platform
            # default (newline=None) and pre-existed the SSOT extraction.
            self.assertEqual(out_path.read_text(encoding="utf-8"), content)

    def test_returns_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            wiki_root = Path(tmp)
            out_path = dashboard.write_dashboard(
                wiki_root, "_dashboards/x.md", ""
            )
            self.assertTrue(out_path.is_absolute())
            self.assertEqual(out_path, wiki_root / "_dashboards" / "x.md")


if __name__ == "__main__":
    unittest.main()
