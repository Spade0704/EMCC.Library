"""Tests for _scripts/check_canon_consistency.py — P12 two-mode canon validator."""

import io
import shutil
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import check_canon_consistency
from _lib import dashboard
from _lib.config_loader import ConfigYamlError, load_config_yaml


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


def _clone_fixture(dst: Path) -> Path:
    shutil.copytree(FIXTURE_ROOT, dst)
    return dst


def _write_page(wiki: Path, rel: str, fm_lines, body: str = "") -> Path:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body
    path.write_text(content, encoding="utf-8")
    return path


def _write_canon(wiki: Path, file_stem: str, body: str) -> Path:
    canon_dir = wiki / "_canon"
    canon_dir.mkdir(parents=True, exist_ok=True)
    path = canon_dir / "{}.yaml".format(file_stem)
    path.write_text(body, encoding="utf-8")
    return path


def _findings_for_page(findings, page_rel):
    return [f for f in findings if f.get("page") == page_rel]


class ConfigLoaderIntegrationTests(unittest.TestCase):

    def test_load_canon_counts_yaml_returns_flat_entries(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            entries = load_config_yaml(
                wiki / "_canon" / "counts.yaml",
                wrapper_key="counts",
                required_keys=("name", "value"),
                entity_noun="canon entry",
            )
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0], {"name": "mechs", "value": 5})
            self.assertEqual(entries[1], {"name": "phases", "value": 3})

    def test_load_canon_roster_yaml_returns_flat_entries(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            entries = load_config_yaml(
                wiki / "_canon" / "roster.yaml",
                wrapper_key="entities",
                required_keys=("canonical_name",),
                entity_noun="canon entry",
            )
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0]["canonical_name"], "Protagonist")
            self.assertEqual(entries[0]["aliases"], ["Hero", "MC"])
            self.assertEqual(entries[1]["canonical_name"], "Antagonist")

    def test_missing_canon_file_returns_empty_list(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # roster + counts present; taxonomy + timeline absent in fixture.
            entries = load_config_yaml(
                wiki / "_canon" / "taxonomy.yaml",
                wrapper_key="categories",
                required_keys=("name",),
                entity_noun="canon entry",
            )
            self.assertEqual(entries, [])

    def test_malformed_canon_yaml_propagates_config_yaml_error(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_canon(wiki, "counts", "counts: not_a_list_just_scalar\n")
            with self.assertRaises(ConfigYamlError):
                check_canon_consistency.run(wiki)


class Mode1PageVsCanonTests(unittest.TestCase):

    def test_mode1_no_findings_when_page_claim_matches_canon(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/ClaimA.md", [
                'title: "Claim A"',
                "type: framework",
                "canon_claim_counts_mechs: 5",
            ])
            out = check_canon_consistency.run(wiki)
            self.assertEqual(
                _findings_for_page(out["findings"], "01-Domain/ClaimA.md"),
                [],
            )

    def test_mode1_error_when_value_mismatches_canon(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/ClaimB.md", [
                'title: "Claim B"',
                "type: framework",
                "canon_claim_counts_mechs: 7",
            ])
            out = check_canon_consistency.run(wiki)
            findings = _findings_for_page(out["findings"], "01-Domain/ClaimB.md")
            self.assertEqual(len(findings), 1)
            f = findings[0]
            self.assertEqual(f["mode"], check_canon_consistency.MODE_PAGE_VS_CANON)
            self.assertEqual(f["severity"], "error")
            self.assertEqual(f["canon_file"], "counts")
            self.assertEqual(f["entity"], "mechs")
            self.assertEqual(f["page_value"], 7)
            self.assertEqual(f["canon_value"], 5)
            self.assertEqual(f["reason"], check_canon_consistency.REASON_VALUE_MISMATCH)

    def test_mode1_error_when_entity_not_in_canon_file(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/ClaimC.md", [
                'title: "Claim C"',
                "type: framework",
                "canon_claim_counts_ships: 3",
            ])
            out = check_canon_consistency.run(wiki)
            findings = _findings_for_page(out["findings"], "01-Domain/ClaimC.md")
            self.assertEqual(len(findings), 1)
            f = findings[0]
            self.assertEqual(f["severity"], "error")
            self.assertEqual(f["entity"], "ships")
            self.assertEqual(
                f["reason"],
                check_canon_consistency.REASON_ENTITY_NOT_IN_CANON,
            )

    def test_mode1_error_when_canon_file_does_not_exist(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # taxonomy.yaml is NOT in the fixture; reference triggers
            # REASON_CANON_FILE_MISSING.
            _write_page(wiki, "01-Domain/ClaimD.md", [
                'title: "Claim D"',
                "type: framework",
                "canon_claim_taxonomy_combat: melee",
            ])
            out = check_canon_consistency.run(wiki)
            findings = _findings_for_page(out["findings"], "01-Domain/ClaimD.md")
            self.assertEqual(len(findings), 1)
            f = findings[0]
            self.assertEqual(f["severity"], "error")
            self.assertEqual(f["canon_file"], "taxonomy")
            self.assertEqual(
                f["reason"],
                check_canon_consistency.REASON_CANON_FILE_MISSING,
            )

    def test_mode1_skip_when_page_has_no_claim_fm_keys(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/Plain.md", [
                'title: "Plain"',
                "type: framework",
                "visibility: internal",
            ])
            out = check_canon_consistency.run(wiki)
            self.assertEqual(
                _findings_for_page(out["findings"], "01-Domain/Plain.md"),
                [],
            )

    def test_mode1_skip_pages_without_frontmatter(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "01-Domain" / "NoFm.md").write_text(
                "# Page with no frontmatter at all\n", encoding="utf-8"
            )
            out = check_canon_consistency.run(wiki)
            self.assertEqual(
                _findings_for_page(out["findings"], "01-Domain/NoFm.md"),
                [],
            )


class Mode2PageVsPageTests(unittest.TestCase):

    def test_mode2_no_findings_when_all_pages_agree(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/AgreeA.md", [
                'title: "A"',
                "canon_claim_counts_mechs: 5",
            ])
            _write_page(wiki, "01-Domain/AgreeB.md", [
                'title: "B"',
                "canon_claim_counts_mechs: 5",
            ])
            out = check_canon_consistency.run(wiki)
            mode2 = [
                f for f in out["findings"]
                if f["mode"] == check_canon_consistency.MODE_PAGE_VS_PAGE
            ]
            self.assertEqual(mode2, [])

    def test_mode2_warning_when_two_pages_disagree_on_same_claim_key(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/DisagreeA.md", [
                'title: "A"',
                "canon_claim_counts_mechs: 5",
            ])
            _write_page(wiki, "01-Domain/DisagreeB.md", [
                'title: "B"',
                "canon_claim_counts_mechs: 7",
            ])
            out = check_canon_consistency.run(wiki)
            mode2 = [
                f for f in out["findings"]
                if f["mode"] == check_canon_consistency.MODE_PAGE_VS_PAGE
            ]
            self.assertEqual(len(mode2), 1)
            f = mode2[0]
            self.assertEqual(f["severity"], "warning")
            self.assertEqual(f["claim_key"], "canon_claim_counts_mechs")
            self.assertEqual(f["canon_file"], "counts")
            self.assertEqual(f["entity"], "mechs")
            paths = {p["path"] for p in f["pages"]}
            self.assertEqual(
                paths,
                {"01-Domain/DisagreeA.md", "01-Domain/DisagreeB.md"},
            )
            self.assertEqual(
                f["reason"],
                check_canon_consistency.REASON_PAGE_DISAGREEMENT,
            )

    def test_mode2_no_finding_when_only_one_page_makes_claim(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/Single.md", [
                'title: "Single"',
                "canon_claim_counts_mechs: 5",
            ])
            out = check_canon_consistency.run(wiki)
            mode2 = [
                f for f in out["findings"]
                if f["mode"] == check_canon_consistency.MODE_PAGE_VS_PAGE
            ]
            self.assertEqual(mode2, [])

    def test_mode2_groups_three_or_more_pages_per_disagreement(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/TripleA.md", [
                'title: "A"',
                "canon_claim_counts_mechs: 5",
            ])
            _write_page(wiki, "01-Domain/TripleB.md", [
                'title: "B"',
                "canon_claim_counts_mechs: 7",
            ])
            _write_page(wiki, "01-Domain/TripleC.md", [
                'title: "C"',
                "canon_claim_counts_mechs: 5",
            ])
            out = check_canon_consistency.run(wiki)
            mode2 = [
                f for f in out["findings"]
                if f["mode"] == check_canon_consistency.MODE_PAGE_VS_PAGE
            ]
            self.assertEqual(len(mode2), 1)
            f = mode2[0]
            paths = {p["path"] for p in f["pages"]}
            self.assertEqual(
                paths,
                {
                    "01-Domain/TripleA.md",
                    "01-Domain/TripleB.md",
                    "01-Domain/TripleC.md",
                },
            )
            self.assertEqual(len(f["pages"]), 3)


class DashboardRenderingTests(unittest.TestCase):

    def test_dashboard_fm_5_field_header_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            out = check_canon_consistency.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            lines = body.split("\n")
            expected = dashboard.render_fm_header("Canon Consistency Dashboard", today=date.today().isoformat())
            self.assertEqual(lines[:7], expected)

    def test_dashboard_sections_by_mode_with_severity_ordering(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Mode 1 error: value mismatch.
            _write_page(wiki, "01-Domain/M1.md", [
                'title: "M1"',
                "canon_claim_counts_mechs: 9",
            ])
            # Mode 2 warning: two pages disagree on a different claim key.
            _write_page(wiki, "01-Domain/M2a.md", [
                'title: "M2a"',
                "canon_claim_counts_phases: 3",
            ])
            _write_page(wiki, "01-Domain/M2b.md", [
                'title: "M2b"',
                "canon_claim_counts_phases: 4",
            ])
            out = check_canon_consistency.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            mode1_idx = body.index("## Mode 1 - Page vs Canon")
            mode2_idx = body.index("## Mode 2 - Page vs Page")
            self.assertLess(mode1_idx, mode2_idx)
            self.assertIn("01-Domain/M1.md", body)
            self.assertIn("canon_claim_counts_phases", body)

    def test_dashboard_zero_findings_skeleton_render(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            out = check_canon_consistency.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No canon consistency findings.", body)
            self.assertNotIn("## Mode 1", body)
            self.assertNotIn("## Mode 2", body)


class CliEntryPointTests(unittest.TestCase):

    def test_main_exit_zero_clean_run(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = check_canon_consistency._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 0)
            self.assertIn("canon_consistency:", stdout.getvalue())

    def test_main_exit_one_findings_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/Bad.md", [
                'title: "Bad"',
                "canon_claim_counts_mechs: 99",
            ])
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = check_canon_consistency._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 1)
            out = stdout.getvalue()
            self.assertIn("01-Domain/Bad.md", out)
            self.assertIn(check_canon_consistency.REASON_VALUE_MISMATCH, out)

    def test_main_exit_two_script_error(self):
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no_such_wiki"
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = check_canon_consistency._main(
                missing, stdout=stdout, stderr=stderr
            )
            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr.getvalue())


class EdgeCaseTests(unittest.TestCase):

    def test_empty_wiki_no_canon_no_pages(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "empty_wiki"
            wiki.mkdir()
            out = check_canon_consistency.run(wiki)
            self.assertEqual(out["findings"], [])
            self.assertEqual(out["pages_scanned"], 0)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No canon consistency findings.", body)

    def test_dashboard_write_idempotent_on_rerun(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            out1 = check_canon_consistency.run(wiki)
            body1 = out1["dashboard_path"].read_text(encoding="utf-8")
            out2 = check_canon_consistency.run(wiki)
            body2 = out2["dashboard_path"].read_text(encoding="utf-8")
            self.assertEqual(body1, body2)


if __name__ == "__main__":
    unittest.main()
