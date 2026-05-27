"""Tests for _scripts/steel_thread_tracker.py — P14 multi-layer manifest tracker."""

import io
import shutil
import unittest
from contextlib import redirect_stderr
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import steel_thread_tracker
from _lib import dashboard
from _lib.config_loader import ConfigYamlError, load_config_yaml


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


def _clone_fixture(dst: Path) -> Path:
    shutil.copytree(FIXTURE_ROOT, dst)
    return dst


def _write_threads(wiki: Path, body: str) -> Path:
    path = wiki / "_config" / "steel_threads.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _find_by_name(findings, name):
    return [f for f in findings if f.get("name") == name]


class ThreadsLoaderTests(unittest.TestCase):

    def test_threads_load_returns_wrapper_key_list(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: Alpha\n"
                "    layers: [\"Home.md\"]\n"
                "  - name: Beta\n"
                "    layers: [\"01-Domain/Foo.md\"]\n"
                "  - name: Gamma\n"
                "    layers: [\"02-Other/Baz.md\"]\n"
            ))
            entries = load_config_yaml(
                wiki / "_config" / "steel_threads.yaml",
                wrapper_key="threads",
                required_keys=("name", "layers"),
                entity_noun="steel thread",
            )
            self.assertEqual(len(entries), 3)
            self.assertEqual(entries[0]["name"], "Alpha")
            self.assertEqual(entries[0]["layers"], ["Home.md"])

    def test_threads_missing_file_run_returns_zero_findings(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "_config" / "steel_threads.yaml").unlink()
            out = steel_thread_tracker.run(wiki)
            self.assertEqual(out["findings"], [])

    def test_threads_missing_file_dashboard_skeleton_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "_config" / "steel_threads.yaml").unlink()
            out = steel_thread_tracker.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            lines = body.split("\n")
            expected_header = dashboard.render_fm_header("Steel Threads Dashboard", today=date.today().isoformat())
            self.assertEqual(lines[:7], expected_header)
            self.assertIn("No steel thread findings.", body)

    def test_threads_missing_file_stderr_warn_emitted(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "_config" / "steel_threads.yaml").unlink()
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = steel_thread_tracker._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 0)
            self.assertIn(
                "warning: _config/steel_threads.yaml not found",
                stderr.getvalue(),
            )

    def test_threads_malformed_yaml_propagates_config_yaml_error(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, "threads: not_a_list_just_scalar\n")
            with self.assertRaises(ConfigYamlError):
                steel_thread_tracker.run(wiki)


class LayerCoverageDetectionTests(unittest.TestCase):

    def test_single_existing_layer_marks_complete(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: SoloComplete\n"
                "    layers: [\"Home.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            # Complete -> suppressed from findings; verify via threads_scanned + zero findings.
            self.assertEqual(out["findings"], [])
            self.assertEqual(out["threads_scanned"], 1)
            self.assertEqual(out["layers_present"], 1)
            self.assertEqual(out["layers_total"], 1)

    def test_single_missing_layer_marks_incomplete(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: SoloMissing\n"
                "    layers: [\"NoSuchFile.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            findings = _find_by_name(out["findings"], "SoloMissing")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["status"], steel_thread_tracker.STATUS_INCOMPLETE)

    def test_mixed_layers_marks_partial(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: Mixed\n"
                "    layers: [\"Home.md\", \"NoSuchFile.md\", \"01-Domain/Foo.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            findings = _find_by_name(out["findings"], "Mixed")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["status"], steel_thread_tracker.STATUS_PARTIAL)

    def test_zero_declared_layers_marks_incomplete(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: ZeroLayers\n"
                "    layers: []\n"
            ))
            out = steel_thread_tracker.run(wiki)
            findings = _find_by_name(out["findings"], "ZeroLayers")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["status"], steel_thread_tracker.STATUS_INCOMPLETE)

    def test_missing_layers_field_marks_incomplete(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Note: load_config_yaml requires `layers` per required_keys; we pass
            # layers but as null/None via explicit empty flow-list to simulate
            # the "absent layers field" semantics inside classify (auto-derive).
            # parse_config_yaml flow-list `[]` -> [] -> auto-derive incomplete.
            _write_threads(wiki, (
                "threads:\n"
                "  - name: NoLayersField\n"
                "    layers: []\n"
            ))
            out = steel_thread_tracker.run(wiki)
            findings = _find_by_name(out["findings"], "NoLayersField")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["layers_total"], 0)
            self.assertEqual(findings[0]["status"], steel_thread_tracker.STATUS_INCOMPLETE)


class StatusOverrideTests(unittest.TestCase):

    def test_yaml_status_complete_override_wins_when_layers_missing(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: OverrideComplete\n"
                "    status: complete\n"
                "    layers: [\"NoSuchFile.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            # Override-complete -> suppressed from findings.
            self.assertEqual(_find_by_name(out["findings"], "OverrideComplete"), [])

    def test_yaml_status_absent_falls_to_auto_derived(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: AutoPartial\n"
                "    layers: [\"Home.md\", \"NoSuchFile.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            findings = _find_by_name(out["findings"], "AutoPartial")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["status"], steel_thread_tracker.STATUS_PARTIAL)

    def test_yaml_status_invalid_value_falls_to_auto_derived(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: InvalidOverride\n"
                "    status: gibberish\n"
                "    layers: [\"NoSuchFile.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            findings = _find_by_name(out["findings"], "InvalidOverride")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["status"], steel_thread_tracker.STATUS_INCOMPLETE)


class SeverityMappingTests(unittest.TestCase):

    def test_incomplete_emits_warning_severity(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: IncompleteSev\n"
                "    layers: [\"NoSuchFile.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            findings = _find_by_name(out["findings"], "IncompleteSev")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["severity"], "warning")

    def test_partial_emits_info_severity(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: PartialSev\n"
                "    layers: [\"Home.md\", \"NoSuchFile.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            findings = _find_by_name(out["findings"], "PartialSev")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["severity"], "info")

    def test_complete_suppresses_finding(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: CompleteSev\n"
                "    layers: [\"Home.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            self.assertEqual(_find_by_name(out["findings"], "CompleteSev"), [])


class RequiredKeysTests(unittest.TestCase):

    def test_required_keys_missing_warns_stderr_skips_entry(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - layers: [\"Home.md\"]\n"
                "  - name: ValidEntry\n"
                "    layers: [\"NoSuchFile.md\"]\n"
            ))
            stdout = io.StringIO()
            stderr = io.StringIO()
            buf = io.StringIO()
            with redirect_stderr(buf):
                rc = steel_thread_tracker._main(wiki, stdout=stdout, stderr=stderr)
            self.assertIn("warning: skipping malformed steel thread", buf.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("ValidEntry", stdout.getvalue())


class DashboardRenderingTests(unittest.TestCase):

    def test_dashboard_fm_5_field_header_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, "threads:\n")
            out = steel_thread_tracker.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            lines = body.split("\n")
            expected = dashboard.render_fm_header("Steel Threads Dashboard", today=date.today().isoformat())
            self.assertEqual(lines[:7], expected)

    def test_dashboard_zero_findings_skeleton_renders_empty_state_line(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, "threads:\n")
            out = steel_thread_tracker.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No steel thread findings.", body)

    def test_dashboard_findings_sorted_by_severity_then_name(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: ZetaPartial\n"
                "    layers: [\"Home.md\", \"NoSuchFile.md\"]\n"
                "  - name: AlphaIncomplete\n"
                "    layers: [\"NoSuchFile.md\"]\n"
                "  - name: BetaPartial\n"
                "    layers: [\"Home.md\", \"NoSuchFile.md\"]\n"
            ))
            out = steel_thread_tracker.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            alpha_idx = body.index("AlphaIncomplete")
            beta_idx = body.index("BetaPartial")
            zeta_idx = body.index("ZetaPartial")
            # warning (AlphaIncomplete) before info (Beta + Zeta).
            self.assertLess(alpha_idx, beta_idx)
            # Within info bucket, alphabetical Beta before Zeta.
            self.assertLess(beta_idx, zeta_idx)


class CliEntryPointTests(unittest.TestCase):

    def test_main_exit_zero_when_all_threads_complete(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: AllComplete\n"
                "    layers: [\"Home.md\"]\n"
            ))
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = steel_thread_tracker._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 0)
            self.assertIn("steel_threads:", stdout.getvalue())

    def test_main_exit_one_when_findings_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: HasFinding\n"
                "    layers: [\"NoSuchFile.md\"]\n"
            ))
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = steel_thread_tracker._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 1)
            self.assertIn("warning:", stdout.getvalue())

    def test_main_exit_two_when_threads_yaml_malformed(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, "threads: not_a_list_just_scalar\n")
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = steel_thread_tracker._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr.getvalue())


class EdgeCaseTests(unittest.TestCase):

    def test_empty_wiki_no_config_emits_zero_findings(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "empty_wiki"
            wiki.mkdir()
            out = steel_thread_tracker.run(wiki)
            self.assertEqual(out["findings"], [])
            self.assertEqual(out["threads_scanned"], 0)

    def test_dashboard_write_idempotent_on_rerun(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_threads(wiki, (
                "threads:\n"
                "  - name: Idempotent\n"
                "    layers: [\"Home.md\"]\n"
            ))
            out1 = steel_thread_tracker.run(wiki)
            body1 = out1["dashboard_path"].read_text(encoding="utf-8")
            out2 = steel_thread_tracker.run(wiki)
            body2 = out2["dashboard_path"].read_text(encoding="utf-8")
            self.assertEqual(body1, body2)


if __name__ == "__main__":
    unittest.main()
