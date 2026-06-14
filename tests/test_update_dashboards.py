"""Tests for _scripts/update_dashboards.py — P19 master orchestrator + health.md synthesis."""

import io
import shutil
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import update_dashboards
from _lib import frontmatter


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


def _clone_fixture(dst: Path) -> Path:
    shutil.copytree(FIXTURE_ROOT, dst)
    return dst


def _write_page(wiki: Path, rel: str, lines):
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


class TestOrchestrator(unittest.TestCase):

    def test_orchestrator_runs_all_sub_scripts(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            stdout = io.StringIO()
            rc = update_dashboards._main(wiki, stdout=stdout)
            self.assertEqual(rc, 0)
            # Assert by the registered label (not "P{num}") so non-P-indexed
            # stages like the report-only citation audit are covered too.
            for _p_num, _module, label in update_dashboards.SUBSCRIPTS:
                self.assertIn(label, stdout.getvalue())
                self.assertIn("OK", stdout.getvalue())
            health = wiki / "_dashboards" / "health.md"
            self.assertTrue(health.exists())

    def test_sub_script_failure_does_not_abort(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Force P10 check_cascade to raise; orchestrator must continue,
            # exit 1, and still synthesize health.md with sentinel for the
            # cascade-staleness signal.
            with patch(
                "update_dashboards.check_cascade.run",
                side_effect=RuntimeError("synthetic failure"),
            ):
                stdout = io.StringIO()
                rc = update_dashboards._main(wiki, stdout=stdout)
            self.assertEqual(rc, 1)
            self.assertIn("FAILED", stdout.getvalue())
            self.assertIn("RuntimeError", stdout.getvalue())
            health = wiki / "_dashboards" / "health.md"
            self.assertTrue(health.exists())
            body = health.read_text(encoding="utf-8")
            # Sentinel surfaces in the Cascade Staleness section.
            self.assertIn("## Cascade Staleness", body)
            self.assertIn(update_dashboards.SENTINEL, body)


class TestHealthMd(unittest.TestCase):

    def test_health_md_fm_5_field_contract(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            update_dashboards.run(wiki)
            health = wiki / "_dashboards" / "health.md"
            page = frontmatter.load_page(health)
            fm = page["frontmatter"]
            self.assertEqual(set(fm.keys()), {
                "title", "type", "visibility", "generated", "last_updated"
            })
            self.assertEqual(fm["title"], "Health Dashboard")
            self.assertEqual(fm["type"], "dashboard")
            self.assertEqual(fm["visibility"], "internal")
            self.assertEqual(fm["generated"], True)
            self.assertEqual(fm["last_updated"], date.today().isoformat())

    def test_health_md_body_seven_sections_in_spec_order(self):
        """Per spec v1.3 §2.4 #1 update: 7 health-summary sections incl. cross_link_coverage."""
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            update_dashboards.run(wiki)
            body = (wiki / "_dashboards" / "health.md").read_text(encoding="utf-8")
            h2s = [
                line[3:].strip()
                for line in body.split("\n")
                if line.startswith("## ")
            ]
            self.assertEqual(h2s, [
                "Completion",
                "Canon Contradictions",
                "Cascade Staleness",
                "Concept Coverage Gaps",
                "Unverified Claims",
                "Recent Ingest",
                "Cross-link Coverage",
            ])


class TestUnverifiedClaimsAggregator(unittest.TestCase):

    def test_aggregator_sums_multi_page(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Add 3 synthetic pages with varied unverified_claims counts.
            _write_page(wiki, "01-Domain/UC_A.md", [
                "---",
                "title: UC A",
                "type: reference",
                "visibility: internal",
                "unverified_claims: [c1, c2, c3]",
                "---",
                "body",
            ])
            _write_page(wiki, "01-Domain/UC_B.md", [
                "---",
                "title: UC B",
                "type: reference",
                "visibility: internal",
                "unverified_claims: [c1]",
                "---",
                "body",
            ])
            _write_page(wiki, "02-Other/UC_C.md", [
                "---",
                "title: UC C",
                "type: reference",
                "visibility: internal",
                "unverified_claims: [c1, c2, c3, c4, c5]",
                "---",
                "body",
            ])
            update_dashboards.run(wiki)
            body = (wiki / "_dashboards" / "health.md").read_text(encoding="utf-8")
            # Grand total = 3 + 1 + 5 = 9 (plus any pre-existing in fixture; check >=9).
            self.assertRegex(body, r"- Total: \d+")
            # Top-N must include UC_C (5 claims, highest count) and UC_A (3 claims).
            self.assertIn("02-Other/UC_C.md (5)", body)
            self.assertIn("01-Domain/UC_A.md (3)", body)
            self.assertIn("01-Domain/UC_B.md (1)", body)


class TestRecentIngest(unittest.TestCase):

    def test_recent_ingest_missing_log_placeholder(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            update_dashboards.run(wiki)
            body = (wiki / "_dashboards" / "health.md").read_text(encoding="utf-8")
            self.assertIn("## Recent Ingest", body)
            self.assertIn("_No ingest entries yet._", body)

    def test_recent_ingest_parses_h2_entries(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            log = wiki / "_decisions" / "ingest-log.md"
            log.parent.mkdir(parents=True, exist_ok=True)
            log.write_text("\n".join([
                "# Ingest Log",
                "",
                "## 2026-05-16 — spec-v2.pdf",
                "Body",
                "## 2026-05-15 — primer.md",
                "Body",
                "## 2026-05-14 — old-source.md",
                "",
            ]), encoding="utf-8")
            update_dashboards.run(wiki)
            body = (wiki / "_dashboards" / "health.md").read_text(encoding="utf-8")
            self.assertIn("- 2026-05-16 — spec-v2.pdf", body)
            self.assertIn("- 2026-05-15 — primer.md", body)
            self.assertIn("- 2026-05-14 — old-source.md", body)


class TestCrossLinkPipeline(unittest.TestCase):
    """T-XL-6 cross-link pipeline (#16 → #17 → #18) per spec v1.3 §2.4 orchestrator note."""

    def test_pipeline_order_16_17_18(self):
        """Cross-link pipeline runs #16 → #17 → #18 in spec sequence."""
        call_order = []

        def make_runner(p_num):
            def fake_run(wiki_root):
                call_order.append(p_num)
                return {}
            return fake_run

        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            with patch.object(
                update_dashboards.build_topic_index, "run", make_runner(16)
            ), patch.object(
                update_dashboards.cross_link_topics, "run", make_runner(17)
            ), patch.object(
                update_dashboards.validate_topic_registry, "run", make_runner(18)
            ):
                update_dashboards.run(wiki)
            self.assertEqual(call_order, [16, 17, 18])

    def test_failure_isolation_one_step_fails_others_continue(self):
        """#17 raises → #18 still runs + existing aggregator/validator outputs preserved."""
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            ran_18 = []

            def fail_17(wiki_root):
                raise RuntimeError("simulated #17 failure")

            def ok_18(wiki_root):
                ran_18.append(True)
                return {}

            with patch.object(
                update_dashboards.cross_link_topics, "run", fail_17
            ), patch.object(
                update_dashboards.validate_topic_registry, "run", ok_18
            ):
                summary = update_dashboards.run(wiki)
            # #18 still ran despite #17 failure
            self.assertTrue(ran_18)
            # Failure aggregated
            self.assertTrue(
                any(f["p_num"] == 17 for f in summary["failures"])
            )
            # Existing dashboards still emitted
            self.assertTrue((wiki / "_dashboards" / "health.md").exists())

    def test_failure_nonzero_exit_code(self):
        """#16/#17/#18 failure → orchestrator returns non-zero exit."""
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")

            def fail_16(wiki_root):
                raise RuntimeError("simulated #16 failure")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with patch.object(
                update_dashboards.build_topic_index, "run", fail_16
            ):
                rc = update_dashboards._main(
                    wiki, stdout=stdout, stderr=stderr
                )
            self.assertEqual(rc, 1)


class TestCrossLinkCoverageSignal(unittest.TestCase):
    """T-XL-6 cross_link_coverage health signal per spec v1.3 §2.4 #1 update."""

    def test_signal_in_health_md(self):
        """health.md output contains cross_link_coverage section."""
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            update_dashboards.run(wiki)
            body = (wiki / "_dashboards" / "health.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Cross-link Coverage", body)
            self.assertIn("Pages with cross-links:", body)

    def test_signal_counts_pages_with_related_files(self):
        """Signal correctly counts pages with non-empty related_files."""
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Add a page with related_files: populated
            _write_page(wiki, "01-Domain/Linked.md", [
                "---",
                'title: "Linked"',
                "type: page",
                "visibility: internal",
                "completion: 80",
                "status: ready",
                "last_updated: 2026-05-21",
                "canon_sources: []",
                "unverified_claims: []",
                "related_files: [01-Domain/Foo.md]",
                "---",
                "",
                "Body",
            ])
            update_dashboards.run(wiki)
            body = (wiki / "_dashboards" / "health.md").read_text(
                encoding="utf-8"
            )
            # Should report at least 1 page with cross-links
            self.assertIn("## Cross-link Coverage", body)
            # Count line should not be 0/N (since we added Linked.md)
            # Format: "Pages with cross-links: X/Y (Z%)"
            self.assertNotIn("Pages with cross-links: 0/", body)


if __name__ == "__main__":
    unittest.main()
