"""Tests for bootstrap.py — S045-T1-P50a + S045-T2-P50b bootstrap stages.

S045-T1-P50a (12 tests; floor 573 → 585):
  AC1 — CLI signature + arg parsing (4 tests)
  AC2 — folder structure creation idempotent (3 tests)
  AC3 — 15-script copy from _scripts/ to target _scripts/ (3 tests)
  AC4 — summary print + error handling (2 tests)

S045-T2-P50b (12 tests; floor 585 → 597):
  AC1 — template enumeration (3 tests)
  AC2 — __SEP__ → / runtime substitution + Win32-safe gate (4 tests)
  AC3 — template content byte-equivalence preservation (2 tests)
  AC4 — full template placement + v1.1 additions (3 tests)
"""

import hashlib
import io
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import bootstrap  # noqa: E402


FAKE_SCRIPT_NAMES = (
    "build_canon_drift_report.py",
    "build_completion_dashboard.py",
    "check_canon_consistency.py",
    "check_cascade.py",
    "check_concept_coverage.py",
    "check_cross_refs.py",
    "check_framework_briefing_sync.py",
    "collect_open_questions.py",
    "delta_source_docs.py",
    "steel_thread_tracker.py",
    "sync_from_kit.py",
    "update_dashboards.py",
    "validate_canon_integrity.py",
    "validate_reveal_conceit.py",
    "validate_terminology.py",
)


def _make_fake_source(parent):
    """Create a fake _scripts/ source tree at parent/_scripts for testing.

    15 top-level .py stubs (matches spec §2.4 consumer-wiki ship set) +
    _lib/{__init__.py, frontmatter.py, config_loader.py} subfolder + 3
    excluded Lattice-infra entries (lattice-bridge.py + lattice_*.py +
    launchers/) that the ignore filter must skip.
    """
    source = parent / "_scripts"
    source.mkdir(parents=True)
    for name in FAKE_SCRIPT_NAMES:
        (source / name).write_bytes(b"# stub " + name.encode())
    lib = source / "_lib"
    lib.mkdir()
    (lib / "__init__.py").write_bytes(b"")
    (lib / "frontmatter.py").write_bytes(b"# stub frontmatter")
    (lib / "config_loader.py").write_bytes(b"# stub config_loader")
    (source / "lattice-bridge.py").write_bytes(b"# infra; excluded")
    (source / "lattice_session_start.py").write_bytes(b"# infra; excluded")
    (source / "launchers").mkdir()
    (source / "launchers" / "x.py").write_bytes(b"# excluded")
    return source


FAKE_TEMPLATE_FILES = {
    "Home.md": b"# Home \xe2\x80\x94 <Project Name>\n",
    "_canon__SEP__README.md": b"# Canon README \xe2\x80\x94 <Project Name>\n",
    "_canon__SEP__counts.yaml": b"counts: []\n",
    "00-Start-Here__SEP__Glossary.md": b"# Glossary <placeholder>\n",
    "_sources__SEP__raw__SEP__README.md": b"# Sources raw README (double-SEP)\n",
    "_sources__SEP__README.md": b"# Sources README\n",
    "_decisions__SEP__ingest-log.md": b"# Ingest log \xe2\x80\x94 starter\n",
}


def _make_fake_templates(parent):
    """Construct fake _template/ source w/ representative cases.

    Covers: Home.md no-SEP top-level + single-SEP + double-SEP P48 case +
    v1.1 _sources/ + _sources/raw/ READMEs + _decisions/ingest-log.md.
    """
    template_dir = parent / "_template"
    template_dir.mkdir(parents=True)
    for name, content in FAKE_TEMPLATE_FILES.items():
        (template_dir / name).write_bytes(content)
    return template_dir


WIN32_RESERVED_CHARS = '<>:"|?*'


class TestAC1CLI(unittest.TestCase):
    """AC1 — CLI signature + arg parsing (4 tests)."""

    def test_positional_target_arg_accepted(self):
        parser = bootstrap._build_parser()
        args = parser.parse_args(["/some/path"])
        self.assertEqual(args.target, Path("/some/path"))
        self.assertFalse(args.dry_run)
        self.assertFalse(args.yes)
        args2 = parser.parse_args(["/some/path", "--dry-run", "--yes"])
        self.assertTrue(args2.dry_run)
        self.assertTrue(args2.yes)

    def test_dry_run_no_filesystem_writes(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                rc = bootstrap.bootstrap(target, dry_run=True, source_override=source)
            self.assertEqual(rc, 0)
            self.assertFalse(target.exists())

    def test_yes_flag_skips_interactive_prompt(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            target.mkdir()
            (target / "preexisting.txt").write_text("squatter")
            sentinel = mock.MagicMock(side_effect=AssertionError("should not prompt"))
            with mock.patch("builtins.input", sentinel):
                with mock.patch("sys.stdout", io.StringIO()):
                    rc = bootstrap.bootstrap(target, yes=True, source_override=source)
            self.assertEqual(rc, 0)
            self.assertFalse(sentinel.called)

    def test_default_invocation_prompts_y_n_via_mocked_stdin(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            target.mkdir()
            (target / "preexisting.txt").write_text("squatter")
            with mock.patch("builtins.input", return_value="n"):
                with mock.patch("sys.stdout", io.StringIO()):
                    rc = bootstrap.bootstrap(target, source_override=source)
            self.assertEqual(rc, 0)
            self.assertFalse((target / "_scripts").exists())
            self.assertFalse((target / "00-Start-Here").exists())


class TestAC2Folders(unittest.TestCase):
    """AC2 — folder structure creation idempotent (3 tests)."""

    def test_folder_set_matches_spec_2_2_enumeration(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                rc = bootstrap.bootstrap(target, yes=True, source_override=source)
            self.assertEqual(rc, 0)
            for folder in bootstrap.WIKI_FOLDERS:
                self.assertTrue(
                    (target / folder).is_dir(),
                    "missing folder: " + folder,
                )
            self.assertEqual(len(bootstrap.WIKI_FOLDERS), 18)

    def test_idempotent_rerun_no_double_write_no_errors(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                rc1 = bootstrap.bootstrap(target, yes=True, source_override=source)
                rc2 = bootstrap.bootstrap(target, yes=True, source_override=source)
            self.assertEqual(rc1, 0)
            self.assertEqual(rc2, 0)
            for folder in bootstrap.WIKI_FOLDERS:
                self.assertTrue((target / folder).is_dir())

    def test_dry_run_lists_folders_without_creating(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            captured = io.StringIO()
            with mock.patch("sys.stdout", captured):
                rc = bootstrap.bootstrap(target, dry_run=True, source_override=source)
            self.assertEqual(rc, 0)
            self.assertFalse(target.exists())
            output = captured.getvalue()
            self.assertIn("DRY-RUN", output)
            self.assertIn("Folders: 18", output)


class TestAC3Scripts(unittest.TestCase):
    """AC3 — 15-script copy from _scripts/ to target _scripts/ (3 tests)."""

    def test_15_scripts_copied_byte_equivalent_hash_match(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True, source_override=source)
            target_scripts = target / "_scripts"
            top_pys = sorted(
                p.name for p in target_scripts.iterdir()
                if p.is_file() and p.suffix == ".py"
            )
            self.assertEqual(len(top_pys), 15)
            self.assertEqual(tuple(top_pys), tuple(sorted(FAKE_SCRIPT_NAMES)))
            self.assertFalse((target_scripts / "lattice-bridge.py").exists())
            self.assertFalse((target_scripts / "lattice_session_start.py").exists())
            self.assertFalse((target_scripts / "launchers").exists())
            for name in top_pys:
                src_hash = hashlib.sha256((source / name).read_bytes()).hexdigest()
                dst_hash = hashlib.sha256(
                    (target_scripts / name).read_bytes()
                ).hexdigest()
                self.assertEqual(src_hash, dst_hash, "byte-mismatch: " + name)

    def test_lib_subfolder_preserved_with_all_modules(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True, source_override=source)
            target_lib = target / "_scripts" / "_lib"
            self.assertTrue(target_lib.is_dir())
            self.assertTrue((target_lib / "__init__.py").is_file())
            self.assertTrue((target_lib / "frontmatter.py").is_file())
            self.assertTrue((target_lib / "config_loader.py").is_file())
            self.assertEqual(
                (target_lib / "frontmatter.py").read_bytes(),
                b"# stub frontmatter",
            )

    def test_script_copy_idempotency_identical_source_no_diff(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True, source_override=source)
            target_scripts = target / "_scripts"

            def _hash_tree(root):
                return {
                    str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in root.rglob("*") if p.is_file()
                }

            first_hashes = _hash_tree(target_scripts)
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True, source_override=source)
            second_hashes = _hash_tree(target_scripts)
            self.assertEqual(first_hashes, second_hashes)


class TestAC4SummaryErrors(unittest.TestCase):
    """AC4 — summary print + error handling (2 tests)."""

    def test_success_summary_format_stdout_folders_scripts_target(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            target = tmp_path / "target"
            captured = io.StringIO()
            with mock.patch("sys.stdout", captured):
                rc = bootstrap.bootstrap(target, yes=True, source_override=source)
            self.assertEqual(rc, 0)
            output = captured.getvalue()
            self.assertIn("DONE", output)
            self.assertIn("Folders: 18", output)
            # 15 top-level + 3 _lib/ files = 18 files copied (matches sample fixture).
            self.assertIn("Scripts: 18", output)
            self.assertIn(str(target.resolve()), output)

    def test_error_stderr_format_missing_source(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            missing_source = tmp_path / "does-not-exist"
            target = tmp_path / "target"
            captured_err = io.StringIO()
            with mock.patch("sys.stderr", captured_err):
                rc = bootstrap.bootstrap(
                    target, yes=True, source_override=missing_source
                )
            self.assertEqual(rc, 1)
            err_output = captured_err.getvalue()
            self.assertIn("ERROR", err_output)
            self.assertIn(str(missing_source), err_output)


# ---------------------------------------------------------------------------
# S045-T2-P50b template enumeration + substitution + placement (12 tests)
# ---------------------------------------------------------------------------


class TestP50bAC1Enumeration(unittest.TestCase):
    """P50b AC1 — template enumeration (3 tests)."""

    def test_enumeration_count_matches_real_template_dir_inventory(self):
        # Hybrid integration test: real install-root _template/ + git ls-files.
        result = subprocess.run(
            ["git", "ls-files", "_template/"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            check=True,
        )
        git_files = [
            line for line in result.stdout.splitlines()
            if line.endswith(".md") or line.endswith(".yaml")
        ]
        template_dir = bootstrap._resolve_template_dir(None)
        enumerated = bootstrap._enumerate_templates(template_dir)
        self.assertEqual(len(enumerated), len(git_files),
                         "enumerator count mismatch vs git ls-files")
        self.assertGreaterEqual(len(enumerated), 22)

    def test_enumeration_includes_home_md_no_sep_flat_file(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            template_dir = _make_fake_templates(tmp_path / "src_root")
            enumerated = bootstrap._enumerate_templates(template_dir)
            names = [p.name for p in enumerated]
            self.assertIn("Home.md", names)
            self.assertNotIn(bootstrap.SEP_PLACEHOLDER, "Home.md")

    def test_enumeration_multi_level_sep_path_decode_double_sep_present(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            template_dir = _make_fake_templates(tmp_path / "src_root")
            enumerated = bootstrap._enumerate_templates(template_dir)
            names = [p.name for p in enumerated]
            self.assertIn("_sources__SEP__raw__SEP__README.md", names)
            double_sep_count = sum(
                1 for n in names if n.count(bootstrap.SEP_PLACEHOLDER) == 2
            )
            self.assertGreaterEqual(double_sep_count, 1)


class TestP50bAC2Substitution(unittest.TestCase):
    """P50b AC2 — __SEP__ → / substitution + Win32-safe gate (4 tests)."""

    def test_single_sep_path_substitution_canon_readme_roundtrip(self):
        target = Path("/tmp/wiki")
        dst = bootstrap._substitute_template_path(target, "_canon__SEP__README.md")
        self.assertEqual(dst, target / "_canon" / "README.md")
        self.assertNotIn(bootstrap.SEP_PLACEHOLDER, str(dst))

    def test_double_sep_path_substitution_sources_raw_readme_roundtrip(self):
        target = Path("/tmp/wiki")
        dst = bootstrap._substitute_template_path(
            target, "_sources__SEP__raw__SEP__README.md"
        )
        self.assertEqual(dst, target / "_sources" / "raw" / "README.md")
        self.assertNotIn(bootstrap.SEP_PLACEHOLDER, str(dst))

    def test_no_sep_literal_in_any_output_path_post_bootstrap_walk(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = _make_fake_templates(tmp_path / "tpl_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            for p in target.rglob("*"):
                self.assertNotIn(
                    bootstrap.SEP_PLACEHOLDER,
                    str(p),
                    "__SEP__ residual at " + str(p),
                )

    def test_win32_safe_output_paths_no_9_reserved_chars_basename_scan(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = _make_fake_templates(tmp_path / "tpl_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            for p in target.rglob("*"):
                for component in p.relative_to(target).parts:
                    for ch in WIN32_RESERVED_CHARS:
                        self.assertNotIn(
                            ch,
                            component,
                            "Win32-reserved char `" + ch + "` in " + str(p),
                        )


class TestP50bAC3ContentPreservation(unittest.TestCase):
    """P50b AC3 — template content byte-equivalence preservation (2 tests)."""

    def test_template_content_byte_equivalence_sha256_match_per_file(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = _make_fake_templates(tmp_path / "tpl_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            for src_name in FAKE_TEMPLATE_FILES:
                src = template_dir / src_name
                dst = bootstrap._substitute_template_path(target, src_name)
                self.assertTrue(dst.is_file(), "missing " + str(dst))
                src_hash = hashlib.sha256(src.read_bytes()).hexdigest()
                dst_hash = hashlib.sha256(dst.read_bytes()).hexdigest()
                self.assertEqual(src_hash, dst_hash, "byte-drift: " + src_name)

    def test_placeholder_markers_project_name_and_angle_brackets_preserved(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = _make_fake_templates(tmp_path / "tpl_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            home_md = target / "Home.md"
            self.assertIn(b"<Project Name>", home_md.read_bytes())
            glossary = target / "00-Start-Here" / "Glossary.md"
            self.assertIn(b"<placeholder>", glossary.read_bytes())


class TestP50bAC4FullPlacement(unittest.TestCase):
    """P50b AC4 — full template placement + v1.1 additions (3 tests)."""

    def test_full_template_placement_all_files_at_substituted_destinations(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = _make_fake_templates(tmp_path / "tpl_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            for src_name in FAKE_TEMPLATE_FILES:
                dst = bootstrap._substitute_template_path(target, src_name)
                self.assertTrue(dst.is_file(), "missing dest: " + str(dst))

    def test_v1_1_sources_readme_and_sources_raw_readme_present_at_target(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = _make_fake_templates(tmp_path / "tpl_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            self.assertTrue((target / "_sources" / "README.md").is_file())
            self.assertTrue((target / "_sources" / "raw" / "README.md").is_file())

    def test_v1_1_decisions_ingest_log_template_copied_at_target(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = _make_fake_templates(tmp_path / "tpl_root")
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            ingest_log = target / "_decisions" / "ingest-log.md"
            self.assertTrue(ingest_log.is_file())
            self.assertIn(b"Ingest log", ingest_log.read_bytes())


# ---------------------------------------------------------------------------
# S045-T2-followup AC1 — empty _template/ refuse code path (3 tests)
# ---------------------------------------------------------------------------


class TestP50bAC1EmptyTemplateRefuse(unittest.TestCase):
    """S045-T2-followup AC1 — empty/non-matching _template/ refuse (3 tests)."""

    def test_empty_template_dir_refuses_with_stderr_error_and_exit_1(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = tmp_path / "empty_tpl"
            template_dir.mkdir()
            target = tmp_path / "target"
            captured_err = io.StringIO()
            with mock.patch("sys.stderr", captured_err):
                rc = bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            self.assertEqual(rc, 1)
            err = captured_err.getvalue()
            self.assertIn("ERROR", err)
            self.assertIn("empty", err)
            self.assertFalse(target.exists(), "fail-fast: target should not exist")

    def test_template_dir_with_only_non_matching_extensions_refused(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            template_dir = tmp_path / "txt_only_tpl"
            template_dir.mkdir()
            (template_dir / "notes.txt").write_bytes(b"not a template")
            (template_dir / "readme.rst").write_bytes(b"not a template")
            target = tmp_path / "target"
            captured_err = io.StringIO()
            with mock.patch("sys.stderr", captured_err):
                rc = bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=template_dir,
                )
            self.assertEqual(rc, 1)
            err = captured_err.getvalue()
            self.assertIn("ERROR", err)
            self.assertIn("empty", err)
            self.assertFalse(target.exists())

    def test_missing_template_dir_already_refused_sanity(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = _make_fake_source(tmp_path / "src_root")
            missing_template = tmp_path / "does-not-exist"
            target = tmp_path / "target"
            captured_err = io.StringIO()
            with mock.patch("sys.stderr", captured_err):
                rc = bootstrap.bootstrap(
                    target,
                    yes=True,
                    source_override=source,
                    template_override=missing_template,
                )
            self.assertEqual(rc, 1)
            err = captured_err.getvalue()
            self.assertIn("ERROR", err)
            self.assertIn(str(missing_template), err)


class TestP50bACXLinkTemplatePlacement(unittest.TestCase):
    """T-XL-7 cross-link template placement verification (2 NEW tests).

    Verifies that the 2 new templates shipped by T-XL-7 (cross-link
    cascade infrastructure) land at the substituted target paths with
    byte-equivalent content. Uses real install-root `_template/` via
    `_resolve_template_dir(None)` per existing AC1Enumeration precedent.
    """

    def test_canon_topics_yaml_lands_at_substituted_target_path(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True)
            dst = target / "_canon" / "topics.yaml"
            self.assertTrue(dst.is_file(), "missing " + str(dst))
            src = bootstrap._resolve_template_dir(None) / "_canon__SEP__topics.yaml"
            self.assertTrue(src.is_file(), "missing source " + str(src))
            src_hash = hashlib.sha256(src.read_bytes()).hexdigest()
            dst_hash = hashlib.sha256(dst.read_bytes()).hexdigest()
            self.assertEqual(
                src_hash, dst_hash, "byte-drift: _canon/topics.yaml"
            )

    def test_config_cross_link_yaml_lands_at_substituted_target_path(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True)
            dst = target / "_config" / "cross_link.yaml"
            self.assertTrue(dst.is_file(), "missing " + str(dst))
            src = bootstrap._resolve_template_dir(None) / "_config__SEP__cross_link.yaml"
            self.assertTrue(src.is_file(), "missing source " + str(src))
            src_hash = hashlib.sha256(src.read_bytes()).hexdigest()
            dst_hash = hashlib.sha256(dst.read_bytes()).hexdigest()
            self.assertEqual(
                src_hash, dst_hash, "byte-drift: _config/cross_link.yaml"
            )


class TestP50bACT4aLibrarianPersonaDropIn(unittest.TestCase):
    """T4a bootstrap drop-in: `.claude/personas/CLAUDE.librarian.md`.

    Verifies bootstrap auto-lifts NEW dot-prefix template + 2-level
    `__SEP__` substitution + dot-prefix subdir creation + byte-equivalent
    content + Win32-safe filename per Lesson #22 STANDARD.

    Precedent-establishing cycle (FIRST `_template/.claude__SEP__*` ship):
    5-exhibit T-XL-7+T-XL-8+T1+T2+T3 ZERO-LOC-change auto-lift pattern
    sustained 6th-exhibit if all assertions pass.
    """

    def test_t4a_librarian_template_enumerated(self):
        template_dir = bootstrap._resolve_template_dir(None)
        enumerated = bootstrap._enumerate_templates(template_dir)
        names = [p.name for p in enumerated]
        self.assertIn(
            ".claude__SEP__personas__SEP__CLAUDE.librarian.md",
            names,
            "librarian template not enumerated; dot-prefix Path.iterdir() coverage gap",
        )

    def test_t4a_librarian_drop_in_lands_at_substituted_target_path(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True)
            dst = target / ".claude" / "personas" / "CLAUDE.librarian.md"
            self.assertTrue(
                dst.is_file(),
                "missing target .claude/personas/CLAUDE.librarian.md",
            )

    def test_t4a_librarian_drop_in_byte_equivalent_to_template(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True)
            dst = target / ".claude" / "personas" / "CLAUDE.librarian.md"
            src = (
                bootstrap._resolve_template_dir(None)
                / ".claude__SEP__personas__SEP__CLAUDE.librarian.md"
            )
            self.assertEqual(
                hashlib.sha256(src.read_bytes()).hexdigest(),
                hashlib.sha256(dst.read_bytes()).hexdigest(),
                "byte-drift: .claude/personas/CLAUDE.librarian.md",
            )

    def test_t4a_librarian_2_level_sep_substitution_with_dot_prefix(self):
        target = Path("/tmp/wiki")
        dst = bootstrap._substitute_template_path(
            target,
            ".claude__SEP__personas__SEP__CLAUDE.librarian.md",
        )
        self.assertEqual(
            dst,
            target / ".claude" / "personas" / "CLAUDE.librarian.md",
        )
        self.assertNotIn(bootstrap.SEP_PLACEHOLDER, str(dst))

    def test_t4a_zero_sep_residual_in_dot_claude_subdir(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True)
            dot_claude = target / ".claude"
            self.assertTrue(dot_claude.is_dir())
            for path in dot_claude.rglob("*"):
                self.assertNotIn(
                    bootstrap.SEP_PLACEHOLDER,
                    path.name,
                    "__SEP__ residual in .claude/ subdir: " + path.name,
                )


class TestP50bACT4bCodexLibrarianContextPlacement(unittest.TestCase):
    """T4b bootstrap drop-in: `_context/CODEX_LIBRARIAN.md`.

    Mirrors T4a TestP50bACT4aLibrarianPersonaDropIn pattern with single
    `__SEP__` 1-level path (simpler than T4a 2-level dot-prefix).
    Verifies bootstrap auto-lifts NEW template + 1-level `__SEP__`
    substitution + byte-equivalent content per Option A verbatim ship.
    """

    def test_t4b_codex_librarian_template_enumerated(self):
        template_dir = bootstrap._resolve_template_dir(None)
        enumerated = bootstrap._enumerate_templates(template_dir)
        names = [p.name for p in enumerated]
        self.assertIn(
            "_context__SEP__CODEX_LIBRARIAN.md",
            names,
            "CODEX_LIBRARIAN template not enumerated",
        )

    def test_t4b_codex_librarian_drop_in_lands_at_substituted_target_path(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True)
            dst = target / "_context" / "CODEX_LIBRARIAN.md"
            self.assertTrue(
                dst.is_file(),
                "missing target _context/CODEX_LIBRARIAN.md",
            )

    def test_t4b_codex_librarian_drop_in_byte_equivalent_to_template(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True)
            dst = target / "_context" / "CODEX_LIBRARIAN.md"
            src = (
                bootstrap._resolve_template_dir(None)
                / "_context__SEP__CODEX_LIBRARIAN.md"
            )
            self.assertEqual(
                hashlib.sha256(src.read_bytes()).hexdigest(),
                hashlib.sha256(dst.read_bytes()).hexdigest(),
                "byte-drift: _context/CODEX_LIBRARIAN.md",
            )

    def test_t4b_codex_librarian_single_sep_substitution(self):
        target = Path("/tmp/wiki")
        dst = bootstrap._substitute_template_path(
            target, "_context__SEP__CODEX_LIBRARIAN.md"
        )
        self.assertEqual(dst, target / "_context" / "CODEX_LIBRARIAN.md")
        self.assertNotIn(bootstrap.SEP_PLACEHOLDER, str(dst))

    def test_t4b_zero_sep_residual_in_context_subdir(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target"
            with mock.patch("sys.stdout", io.StringIO()):
                bootstrap.bootstrap(target, yes=True)
            context_dir = target / "_context"
            self.assertTrue(context_dir.is_dir())
            for path in context_dir.rglob("*"):
                self.assertNotIn(
                    bootstrap.SEP_PLACEHOLDER,
                    path.name,
                    "__SEP__ residual in _context/ subdir: " + path.name,
                )


class TestP50bACT4cClaudeContextRulesLibrarianReference(unittest.TestCase):
    """T4c CLAUDE_CONTEXT_RULES.md Librarian reference update.

    EDIT existing _template/_context__SEP__CLAUDE_CONTEXT_RULES.md to ADD
    `## Librarian persona` section while PRESERVING 4 mandated §7 Phase-4
    Q&A rules untouched per JP T4 directive (CRITICAL invariant).

    Tests assert 4-rule preservation via Option A substring match per rule
    (robust to whitespace + clearer failure messages).
    """

    QA_RULE_SUBSTRINGS = [
        "Consult wiki pages before raw sources",
        "Cite specific pages using `[[wikilinks]]`",
        "Flag uncertainty explicitly; never confabulate when canon is silent",
        "For cross-source synthesis, name every page being synthesized",
    ]

    def _bootstrap_and_read_rules(self, tmp_path):
        target = tmp_path / "target"
        with mock.patch("sys.stdout", io.StringIO()):
            bootstrap.bootstrap(target, yes=True)
        rules = target / "_context" / "CLAUDE_CONTEXT_RULES.md"
        return rules.read_text(encoding="utf-8")

    def test_t4c_librarian_section_present(self):
        with TemporaryDirectory() as tmp:
            content = self._bootstrap_and_read_rules(Path(tmp))
            self.assertIn(
                "## Librarian persona",
                content,
                "Librarian persona section absent post-T4c",
            )

    def test_t4c_four_mandated_qa_rules_preserved_zero_deviation(self):
        with TemporaryDirectory() as tmp:
            content = self._bootstrap_and_read_rules(Path(tmp))
            for rule_substring in self.QA_RULE_SUBSTRINGS:
                self.assertIn(
                    rule_substring,
                    content,
                    "Q&A rule violated: " + rule_substring,
                )

    def test_t4c_librarian_section_references_codex_librarian_md(self):
        with TemporaryDirectory() as tmp:
            content = self._bootstrap_and_read_rules(Path(tmp))
            self.assertIn(
                "_context/CODEX_LIBRARIAN.md",
                content,
                "Librarian section missing CODEX_LIBRARIAN.md reference",
            )

    def test_t4c_librarian_section_references_persona_dropin(self):
        with TemporaryDirectory() as tmp:
            content = self._bootstrap_and_read_rules(Path(tmp))
            self.assertIn(
                ".claude/personas/CLAUDE.librarian.md",
                content,
                "Librarian section missing persona drop-in reference",
            )

    def test_t4c_update_protocol_position_preserved_post_librarian_section(self):
        with TemporaryDirectory() as tmp:
            content = self._bootstrap_and_read_rules(Path(tmp))
            librarian_idx = content.find("## Librarian persona")
            update_idx = content.find("## Update protocol")
            self.assertGreater(librarian_idx, 0)
            self.assertGreater(
                update_idx,
                librarian_idx,
                "Update protocol section position violated (must follow Librarian)",
            )


if __name__ == "__main__":
    unittest.main()
