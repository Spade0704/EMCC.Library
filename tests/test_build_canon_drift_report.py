"""Tests for _scripts/build_canon_drift_report.py — P15 canon snapshot+diff."""

import io
import shutil
import unittest
from contextlib import redirect_stderr
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import build_canon_drift_report
from _lib import dashboard


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


def _clone_fixture(dst: Path) -> Path:
    shutil.copytree(FIXTURE_ROOT, dst)
    return dst


def _write_canon(wiki: Path, file_stem: str, body: str) -> Path:
    path = wiki / "_canon" / "{}.yaml".format(file_stem)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _write_snapshot_file(
    wiki: Path, snapshot_id: str, file_stem: str, body: str
) -> Path:
    snap_dir = wiki / "_canon" / ".snapshots" / snapshot_id
    snap_dir.mkdir(parents=True, exist_ok=True)
    path = snap_dir / "{}.yaml".format(file_stem)
    path.write_text(body, encoding="utf-8")
    return path


def _findings_by_class(findings, change_class):
    return [f for f in findings if f.get("change_class") == change_class]


class SnapshotLoaderTests(unittest.TestCase):

    def test_snapshot_dir_missing_first_run_emits_warn_to_stderr(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = build_canon_drift_report._main(
                wiki, argv=[], stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 0)
            self.assertIn(
                "warning: _canon/.snapshots/ empty",
                stderr.getvalue(),
            )

    def test_snapshot_dir_missing_first_run_returns_zero_findings(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            out = build_canon_drift_report.run(wiki)
            self.assertEqual(out["findings"], [])
            self.assertTrue(out["baseline_missing"])

    def test_snapshot_dir_empty_first_run_skeleton_dashboard_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "_canon" / ".snapshots").mkdir(parents=True, exist_ok=True)
            out = build_canon_drift_report.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            lines = body.split("\n")
            expected = dashboard.render_fm_header("Canon Drift Dashboard", today=date.today().isoformat())
            self.assertEqual(lines[:7], expected)
            self.assertIn("No prior snapshot found", body)

    def test_latest_snapshot_selected_by_iso8601_lex_sort(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Three snapshots; the lex-latest is the May-15-19 one.
            for snap_id in (
                "2026-05-10T00-00-00Z",
                "2026-05-15T19-00-00Z",
                "2026-05-12T12-00-00Z",
            ):
                _write_snapshot_file(wiki, snap_id, "counts", (
                    "counts:\n  - name: mechs\n    value: 5\n"
                ))
            out = build_canon_drift_report.run(wiki)
            self.assertEqual(out["baseline_snapshot_id"], "2026-05-15T19-00-00Z")


class SnapshotWriteTests(unittest.TestCase):

    def test_snapshot_flag_writes_new_snapshot_dir(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = build_canon_drift_report._main(
                wiki, argv=["--snapshot"], stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 0)
            snap_base = wiki / "_canon" / ".snapshots"
            subdirs = [p for p in snap_base.iterdir() if p.is_dir()]
            self.assertEqual(len(subdirs), 1)
            # Verify yaml byte-copy: source counts.yaml present in snapshot.
            self.assertTrue((subdirs[0] / "counts.yaml").exists())
            self.assertTrue((subdirs[0] / "roster.yaml").exists())

    def test_run_without_snapshot_flag_does_not_write_snapshot(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Pre-create _canon/.snapshots/ (empty) so we can count its
            # contents stably both before and after the run.
            snap_base = wiki / "_canon" / ".snapshots"
            snap_base.mkdir(parents=True, exist_ok=True)
            before = list(snap_base.iterdir())
            build_canon_drift_report.run(wiki)
            after = list(snap_base.iterdir())
            self.assertEqual(before, after)


class DiffAlgorithmTests(unittest.TestCase):

    def test_add_detection_counts_yaml_entry_added(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Snapshot baseline mirrors fixture canon exactly so the
            # only drift is the new `ships` entry below.
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
            ))
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "roster", (
                "entities:\n"
                "  - canonical_name: Protagonist\n"
                "    aliases: [\"Hero\", \"MC\"]\n"
                "  - canonical_name: Antagonist\n"
            ))
            _write_canon(wiki, "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
                "  - name: ships\n"
                "    value: 7\n"
            ))
            out = build_canon_drift_report.run(wiki)
            adds = _findings_by_class(out["findings"], "add")
            self.assertEqual(len(adds), 1)
            self.assertEqual(adds[0]["canon_file"], "counts")
            self.assertEqual(adds[0]["entity"], "ships")

    def test_remove_detection_counts_yaml_entry_removed(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
                "  - name: phases\n"
                "    value: 3\n"
            ))
            _write_canon(wiki, "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
            ))
            out = build_canon_drift_report.run(wiki)
            removes = _findings_by_class(out["findings"], "remove")
            self.assertEqual(len(removes), 1)
            self.assertEqual(removes[0]["entity"], "phases")

    def test_modify_detection_counts_yaml_value_changed(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
            ))
            _write_canon(wiki, "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 7\n"
            ))
            out = build_canon_drift_report.run(wiki)
            mods = _findings_by_class(out["findings"], "modify")
            self.assertEqual(len(mods), 1)
            self.assertEqual(mods[0]["entity"], "mechs")
            self.assertIn("value", mods[0]["changed_fields"])

    def test_zero_findings_when_identical_to_baseline(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            body = (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
                "  - name: phases\n"
                "    value: 3\n"
            )
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", body)
            _write_canon(wiki, "counts", body)
            out = build_canon_drift_report.run(wiki)
            # roster.yaml unchanged too (fixture includes one). Snapshot only
            # has counts; baseline-state-missing for roster -> all roster
            # entries surface as 'remove' from baseline-empty perspective.
            # To assert zero findings, also snapshot roster.yaml from fixture.
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "roster", (
                "entities:\n"
                "  - canonical_name: Protagonist\n"
                "    aliases: [\"Hero\", \"MC\"]\n"
                "  - canonical_name: Antagonist\n"
            ))
            out = build_canon_drift_report.run(wiki)
            self.assertEqual(out["findings"], [])

    def test_roster_file_change_detected_carries_canon_file_label(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Snapshot has only counts; current has counts + roster.
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n  - name: mechs\n    value: 5\n"
            ))
            # Fixture already provides roster.yaml; ensure it differs from snapshot.
            out = build_canon_drift_report.run(wiki)
            roster_findings = [
                f for f in out["findings"]
                if f["canon_file"] == "roster"
            ]
            self.assertGreater(len(roster_findings), 0)
            self.assertNotEqual(roster_findings[0]["canon_file"], "counts")

    def test_taxonomy_file_change_detected_carries_canon_file_label(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n  - name: mechs\n    value: 5\n"
            ))
            _write_canon(wiki, "taxonomy", (
                "categories:\n"
                "  - name: combat\n"
            ))
            out = build_canon_drift_report.run(wiki)
            taxonomy_findings = [
                f for f in out["findings"]
                if f["canon_file"] == "taxonomy"
            ]
            self.assertEqual(len(taxonomy_findings), 1)
            self.assertEqual(taxonomy_findings[0]["entity"], "combat")

    def test_timeline_file_change_detected_carries_canon_file_label(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n  - name: mechs\n    value: 5\n"
            ))
            _write_canon(wiki, "timeline", (
                "events:\n"
                "  - name: chapter_one\n"
                "    date: 2026-01-01\n"
            ))
            out = build_canon_drift_report.run(wiki)
            timeline_findings = [
                f for f in out["findings"]
                if f["canon_file"] == "timeline"
            ]
            self.assertEqual(len(timeline_findings), 1)
            self.assertEqual(timeline_findings[0]["entity"], "chapter_one")

    def test_modify_lists_all_changed_field_names(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
                "    note: old\n"
            ))
            _write_canon(wiki, "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 7\n"
                "    note: new\n"
            ))
            out = build_canon_drift_report.run(wiki)
            mods = _findings_by_class(out["findings"], "modify")
            self.assertEqual(len(mods), 1)
            self.assertIn("value", mods[0]["changed_fields"])
            self.assertIn("note", mods[0]["changed_fields"])


class DashboardRenderingTests(unittest.TestCase):

    def test_dashboard_fm_5_field_header_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            out = build_canon_drift_report.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            lines = body.split("\n")
            expected = dashboard.render_fm_header("Canon Drift Dashboard", today=date.today().isoformat())
            self.assertEqual(lines[:7], expected)

    def test_dashboard_zero_findings_skeleton_renders_empty_state_line(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Snapshot identical to current canon -> zero findings + present baseline.
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
                "  - name: phases\n"
                "    value: 3\n"
            ))
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "roster", (
                "entities:\n"
                "  - canonical_name: Protagonist\n"
                "    aliases: [\"Hero\", \"MC\"]\n"
                "  - canonical_name: Antagonist\n"
            ))
            out = build_canon_drift_report.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No canon drift detected since baseline.", body)

    def test_dashboard_findings_grouped_by_change_class_in_fixed_order(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
                "  - name: phases\n"
                "    value: 3\n"
            ))
            _write_canon(wiki, "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 7\n"
                "  - name: ships\n"
                "    value: 9\n"
            ))
            out = build_canon_drift_report.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            added_idx = body.index("## Added")
            removed_idx = body.index("## Removed")
            modified_idx = body.index("## Modified")
            self.assertLess(added_idx, removed_idx)
            self.assertLess(removed_idx, modified_idx)


class CliEntryPointTests(unittest.TestCase):

    def test_main_exit_zero_when_no_drift(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
                "  - name: phases\n"
                "    value: 3\n"
            ))
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "roster", (
                "entities:\n"
                "  - canonical_name: Protagonist\n"
                "    aliases: [\"Hero\", \"MC\"]\n"
                "  - canonical_name: Antagonist\n"
            ))
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = build_canon_drift_report._main(
                wiki, argv=[], stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 0)
            self.assertIn("canon_drift:", stdout.getvalue())

    def test_main_exit_one_when_drift_findings_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 5\n"
            ))
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "roster", (
                "entities:\n"
                "  - canonical_name: Protagonist\n"
                "    aliases: [\"Hero\", \"MC\"]\n"
                "  - canonical_name: Antagonist\n"
            ))
            _write_canon(wiki, "counts", (
                "counts:\n"
                "  - name: mechs\n"
                "    value: 7\n"
            ))
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = build_canon_drift_report._main(
                wiki, argv=[], stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 1)
            self.assertIn("mechs", stdout.getvalue())

    def test_main_exit_two_when_current_canon_malformed(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n  - name: mechs\n    value: 5\n"
            ))
            _write_canon(wiki, "counts", "counts: not_a_list_just_scalar\n")
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = build_canon_drift_report._main(
                wiki, argv=[], stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr.getvalue())


class EdgeCaseTests(unittest.TestCase):

    def test_dashboard_write_idempotent_on_rerun(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_snapshot_file(wiki, "2026-05-15T00-00-00Z", "counts", (
                "counts:\n  - name: mechs\n    value: 5\n"
            ))
            out1 = build_canon_drift_report.run(wiki)
            body1 = out1["dashboard_path"].read_text(encoding="utf-8")
            out2 = build_canon_drift_report.run(wiki)
            body2 = out2["dashboard_path"].read_text(encoding="utf-8")
            self.assertEqual(body1, body2)


if __name__ == "__main__":
    unittest.main()
