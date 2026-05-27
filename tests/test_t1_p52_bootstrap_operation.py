"""T1 P52 — Bootstrap operation end-to-end integration test.

Per CODEX_BUILD_SPEC_v1_3.md §4.1 + amended scope per T-XL cross-link
cascade FULL CLOSURE at commit `25c61e1` (8 of 8 T-XL cycles complete).

Verifies the Bootstrap operation end-to-end:
  - Subprocess invocation of bootstrap.py on temp target
  - 18 top-level entries per spec §2.2 wiki folder structure
  - 25 cross-link-cascade-inclusive scripts copied (HEAD-verified count per
    ARCHITECTURAL FINDING #1 anchor-verify directive; NOT stale Architect
    dispatch 19 estimate which under-counted _lib subdir files)
  - Cross-link artifact placement: _canon/topics.yaml + _config/cross_link.yaml
    present at target with byte-equivalence vs source templates per spec §2.5
  - ZERO `__SEP__` residual across `target.rglob('*')` per Lesson #22 STANDARD
    runtime-substitution-verify gate at OP-TIER (recursive tree walk)
  - Idempotency: re-run produces zero diff + no partial state (.bak / .tmp)

POSTURE: test-authoring primary. If bootstrap fails to place/substitute
any cross-link artifact, surface via build_summary `failures[]` for
Architect arbitration; NO silent scope widening.

MANDATORY fixture-scope-discipline: ALL `read_text()` / `read_bytes()` /
`.exists()` / `.is_file()` / `.is_dir()` ops against
TemporaryDirectory-managed paths MUST occur INSIDE `with` block scope per
5-cycle PROVEN-EFFECTIVE T-XL-5..T-XL-8 + T1 STANDARD-codification
SOLIDIFIED evidence base.
"""

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_PY = REPO_ROOT / "bootstrap.py"
TEMPLATE_DIR = REPO_ROOT / "_template"
CODEX_SCRIPTS = REPO_ROOT / "_scripts"

# HEAD-verified count per ARCHITECTURAL FINDING #1 anchor-verify directive.
# T-XL cascade FULL CLOSURE @ 25c61e1: 7 _lib + 18 _scripts = 25 scripts.
# S046-T5 pre-SHIP gap closure ships P17 scaffold_brain_dump.py +
# P18 scaffold_source.py = +2 scripts; new total 27 (7 _lib + 20 _scripts).
# Excludes 3 operational-infra (lattice-bridge.py + lattice_session_start.py
# + lattice_valid_roles_audit.py per SCRIPT_IGNORE_PATTERNS in bootstrap.py).
EXPECTED_SCRIPT_COUNT = 27

# Top-level entries per spec §2.2 wiki folder structure. WIKI_FOLDERS in
# bootstrap.py has 18 entries but `_sources/raw` nests under `_sources`,
# so unique top-level folders = 17 + Home.md file = 18 top-level entries
# total expected at target root.
EXPECTED_TOP_LEVEL_FOLDERS = {
    "00-Start-Here",
    "01-Domain-1",
    "02-Domain-2",
    "04-Contributing",
    "Attachments",
    "public",
    "scripts",
    "_dashboards",
    "_decisions",
    "_inbox",
    "_sources",
    "_brain_dump",
    "_canon",
    "_context",
    "_scripts",
    "_config",
    "_confidential",
}


def _run_bootstrap(target: Path) -> subprocess.CompletedProcess:
    """Invoke bootstrap.py via subprocess; return CompletedProcess.

    Uses sys.executable for interpreter + --yes flag for non-interactive +
    capture_output=True + check=False (per-test assertEqual on rc to
    surface failure messages cleanly) + timeout=60 per S045-T1 P50a S5
    precedent.
    """
    return subprocess.run(
        [sys.executable, str(BOOTSTRAP_PY), str(target), "--yes"],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def _sha256(path: Path) -> str:
    """Compute sha256 hex of file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_state(root: Path) -> dict:
    """Snapshot relative-path → sha256 for all files under root."""
    state = {}
    for path in root.rglob("*"):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            state[rel] = _sha256(path)
    return state


class TestT1P52BootstrapE2E(unittest.TestCase):
    """e2e bootstrap subprocess + folder structure + script count + summary + SEP gate."""

    def test_e2e_bootstrap_exit_zero_summary_format(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(
                result.returncode,
                0,
                "bootstrap exit non-zero; stderr={!r}".format(result.stderr),
            )
            self.assertIn("Folders:", result.stdout)
            self.assertIn("Scripts:", result.stdout)
            self.assertIn("Templates:", result.stdout)
            self.assertIn(str(target), result.stdout)

    def test_e2e_folder_structure_top_level(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(result.returncode, 0)
            for folder in EXPECTED_TOP_LEVEL_FOLDERS:
                folder_path = target / folder
                self.assertTrue(
                    folder_path.is_dir(),
                    "missing top-level folder: " + folder,
                )
            # Nested _sources/raw verified per spec §2.2
            self.assertTrue((target / "_sources" / "raw").is_dir())

    def test_e2e_script_copy_count_HEAD_verified(self):
        """Per ARCHITECTURAL FINDING #1: HEAD-verified 25 (NOT stale 19)."""
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(result.returncode, 0)
            scripts_dir = target / "_scripts"
            copied = [
                p for p in scripts_dir.rglob("*.py") if p.is_file()
            ]
            self.assertEqual(
                len(copied),
                EXPECTED_SCRIPT_COUNT,
                "expected {} scripts; got {}".format(
                    EXPECTED_SCRIPT_COUNT, len(copied)
                ),
            )

    def test_e2e_summary_line_correctness(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(result.returncode, 0)
            # Summary line includes counts + target + mode marker
            self.assertIn("[DONE]", result.stdout)
            self.assertIn("Bootstrap target:", result.stdout)
            self.assertIn("Total operations:", result.stdout)

    def test_e2e_zero_sep_residual_op_tier(self):
        """AC3 Lesson #22 STANDARD elevation to OP-TIER: recursive tree walk."""
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(result.returncode, 0)
            for path in target.rglob("*"):
                rel_str = str(path.relative_to(target))
                self.assertNotIn(
                    "__SEP__",
                    path.name,
                    "__SEP__ residual in filename: " + path.name,
                )
                self.assertNotIn(
                    "__SEP__",
                    rel_str,
                    "__SEP__ residual in path: " + rel_str,
                )


class TestT1P52CrossLinkArtifactPlacement(unittest.TestCase):
    """T-XL cascade amended-scope artifact placement assertions."""

    def test_e2e_canon_topics_yaml_byte_equivalent(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(result.returncode, 0)
            target_topics = target / "_canon" / "topics.yaml"
            source_topics = TEMPLATE_DIR / "_canon__SEP__topics.yaml"
            self.assertTrue(
                target_topics.is_file(),
                "missing target _canon/topics.yaml",
            )
            self.assertTrue(
                source_topics.is_file(),
                "missing source _template/_canon__SEP__topics.yaml",
            )
            self.assertEqual(
                _sha256(target_topics),
                _sha256(source_topics),
                "byte-drift: _canon/topics.yaml",
            )

    def test_e2e_config_cross_link_yaml_byte_equivalent(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(result.returncode, 0)
            target_cross_link = target / "_config" / "cross_link.yaml"
            source_cross_link = (
                TEMPLATE_DIR / "_config__SEP__cross_link.yaml"
            )
            self.assertTrue(
                target_cross_link.is_file(),
                "missing target _config/cross_link.yaml",
            )
            self.assertTrue(
                source_cross_link.is_file(),
                "missing source _template/_config__SEP__cross_link.yaml",
            )
            self.assertEqual(
                _sha256(target_cross_link),
                _sha256(source_cross_link),
                "byte-drift: _config/cross_link.yaml",
            )

    def test_e2e_4_cross_link_scripts_byte_equivalent(self):
        """T-XL-2..T-XL-5 cross-link scripts byte-equivalence vs codex source."""
        cross_link_scripts = [
            ("_scripts/_lib/topics.py", "_lib/topics.py"),
            ("_scripts/build_topic_index.py", "build_topic_index.py"),
            ("_scripts/cross_link_topics.py", "cross_link_topics.py"),
            (
                "_scripts/validate_topic_registry.py",
                "validate_topic_registry.py",
            ),
        ]
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(result.returncode, 0)
            for rel_path, _label in cross_link_scripts:
                target_path = target / rel_path
                source_path = REPO_ROOT / rel_path
                self.assertTrue(
                    target_path.is_file(),
                    "missing target " + rel_path,
                )
                self.assertEqual(
                    _sha256(target_path),
                    _sha256(source_path),
                    "byte-drift: " + rel_path,
                )


class TestT1P52IdempotencyAndPartialState(unittest.TestCase):
    """Re-run idempotency + partial-state-absence per spec §7 Phase 6."""

    def test_e2e_idempotent_re_run_exit_zero(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            first = _run_bootstrap(target)
            self.assertEqual(first.returncode, 0)
            # 2nd invocation with same target (now non-empty); --yes skips prompt
            second = _run_bootstrap(target)
            self.assertEqual(
                second.returncode,
                0,
                "idempotent re-run failed; stderr={!r}".format(second.stderr),
            )

    def test_e2e_idempotent_per_file_sha256_byte_equivalent(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            _run_bootstrap(target)
            state_1 = _tree_state(target)
            _run_bootstrap(target)
            state_2 = _tree_state(target)
            self.assertEqual(
                state_1,
                state_2,
                "tree state differs after idempotent re-run",
            )

    def test_e2e_no_partial_state_no_bak_files(self):
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            result = _run_bootstrap(target)
            self.assertEqual(result.returncode, 0)
            bak_files = list(target.rglob("*.bak"))
            tmp_files = list(target.rglob("*.tmp"))
            partial_files = list(target.rglob("*.partial"))
            self.assertEqual(bak_files, [], "found .bak partial-state files")
            self.assertEqual(tmp_files, [], "found .tmp partial-state files")
            self.assertEqual(
                partial_files, [], "found .partial partial-state files"
            )


if __name__ == "__main__":
    unittest.main()
