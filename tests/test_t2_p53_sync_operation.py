"""T2 P53 — Sync operation end-to-end integration test.

Per CODEX_BUILD_SPEC_v1_3.md §4.2 + amended scope per T-XL cross-link
cascade FULL CLOSURE at commit `25c61e1` (T-XL-8 ZERO sync-logic LOC
change auto-lift verified at unit-tier; T2 verifies at op-tier e2e).

Verifies the Sync operation end-to-end:
  - Subprocess invocation of sync_from_kit.py on bootstrapped wiki
  - Spec §4.2 precedence map fidelity:
      OVERWRITE _scripts/ + 3 procedure files
      MERGE-NEW-ONLY _config/ + _template/
      NEVER-TOUCHED content folders + _context/CLAUDE_CONTEXT_RULES.md
  - Cross-link artifact precedence:
      4 cross-link scripts (T-XL-2..T-XL-5) → OVERWRITE
      2 cross-link templates (T-XL-7) → MERGE-NEW-ONLY
  - Idempotency + --dry-run + --force coverage
  - ZERO `__SEP__` residual at OP-TIER post-sync per Lesson #22 STANDARD

POSTURE: test-authoring primary per T1 precedent. NO sync_from_kit.py
LOC change this cycle (T-XL-8 + T1 ZERO-LOC-change auto-lift precedent
sustained; if sync fails precedence map, surface via build_summary
`failures[]` for Architect arbitration; NO silent scope widening).

MANDATORY fixture-scope-discipline 6th-cycle preventive sustained per
5-cycle PROVEN-EFFECTIVE T-XL-5..T-XL-8+T1 evidence base + STANDARD-
codification SOLIDIFIED + Auditor T1 promotion-NOW-OVERDUE recommendation.
"""

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_PY = REPO_ROOT / "bootstrap.py"
SYNC_FROM_KIT_PY = REPO_ROOT / "_scripts" / "sync_from_kit.py"


def _bootstrap_wiki(tmp_path: Path) -> Path:
    """Bootstrap a wiki target into tmp_path/wiki + git init + commit.

    Returns the wiki path. Clean git state lets sync_from_kit run without
    --force (per existing TestGuard precedent + spec §4.2 guard).
    """
    wiki = tmp_path / "wiki"
    bootstrap_result = subprocess.run(
        [sys.executable, str(BOOTSTRAP_PY), str(wiki), "--yes"],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    if bootstrap_result.returncode != 0:
        raise RuntimeError(
            "fixture bootstrap failed: rc={} stderr={!r}".format(
                bootstrap_result.returncode, bootstrap_result.stderr
            )
        )
    # git init + commit for clean state (sync guard satisfied)
    subprocess.run(["git", "init", "-q"], cwd=str(wiki), check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=str(wiki),
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"], cwd=str(wiki), check=True
    )
    subprocess.run(
        ["git", "config", "commit.gpgsign", "false"],
        cwd=str(wiki),
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial bootstrap", "--no-verify"],
        cwd=str(wiki),
        check=True,
    )
    return wiki


def _run_sync(wiki: Path, *flags: str) -> subprocess.CompletedProcess:
    """Invoke sync_from_kit.py via subprocess; codex=REPO_ROOT."""
    return subprocess.run(
        [sys.executable, str(SYNC_FROM_KIT_PY), str(REPO_ROOT), *flags],
        cwd=str(wiki),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def _git_commit_all(wiki: Path, message: str = "customize") -> None:
    """Stage + commit all changes in wiki (re-enable clean state for sync)."""
    subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", message, "--no-verify"],
        cwd=str(wiki),
        check=True,
    )


def _sha256(path: Path) -> str:
    """Compute sha256 hex of file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_state(root: Path) -> dict:
    """Snapshot relative-path → sha256 for all files under root (excluding .git)."""
    state = {}
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            rel = path.relative_to(root).as_posix()
            state[rel] = _sha256(path)
    return state


class TestT2P53SyncE2E(unittest.TestCase):
    """e2e sync subprocess + exit + ZERO __SEP__ OP-TIER + idempotency."""

    def test_e2e_sync_exit_zero_summary(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            result = _run_sync(wiki)
            self.assertEqual(
                result.returncode,
                0,
                "sync exit non-zero; stderr={!r}".format(result.stderr),
            )
            # Summary stdout markers per existing sync_from_kit convention
            self.assertTrue(
                "[OVERWRITE]" in result.stdout
                or "[MERGE-NEW]" in result.stdout
                or "[SKIP]" in result.stdout,
                "missing precedence markers in summary",
            )

    def test_e2e_zero_sep_residual_op_tier_post_sync_excluding_template_subdir(self):
        """AC3 Lesson #22 STANDARD sustained at sync-tier with `_template/` carve-out.

        ARCHITECTURAL FINDING #1: sync_from_kit copies `_template/<filename>`
        PRESERVING `__SEP__` by design (templates remain as templates for
        future bootstrap operations on derived wikis). Lesson #22 STANDARD
        at OP-TIER scoped to EXCLUDE `_template/` subdir per spec §4.2
        sync semantic.
        """
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            for path in wiki.rglob("*"):
                if ".git" in path.parts:
                    continue
                if "_template" in path.parts:
                    continue
                rel_str = str(path.relative_to(wiki))
                self.assertNotIn(
                    "__SEP__",
                    path.name,
                    "__SEP__ residual in filename post-sync: " + path.name,
                )
                self.assertNotIn(
                    "__SEP__",
                    rel_str,
                    "__SEP__ residual in path post-sync: " + rel_str,
                )

    def test_e2e_idempotent_re_run_sha256_byte_equivalent(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            first = _run_sync(wiki)
            self.assertEqual(first.returncode, 0)
            # Commit post-1st-sync changes so guard satisfied for 2nd run
            _git_commit_all(wiki, "post 1st sync")
            state_1 = _tree_state(wiki)
            second = _run_sync(wiki)
            self.assertEqual(
                second.returncode,
                0,
                "idempotent re-run failed; stderr={!r}".format(second.stderr),
            )
            state_2 = _tree_state(wiki)
            self.assertEqual(
                state_1, state_2, "tree state differs after idempotent re-run"
            )


class TestT2P53PrecedenceMap(unittest.TestCase):
    """Spec §4.2 precedence map fidelity end-to-end."""

    def test_overwrite_scripts_replaced(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Customize wiki-side script (stale content)
            target_script = wiki / "_scripts" / "build_completion_dashboard.py"
            target_script.write_text(
                "# wiki-side stale content\n", encoding="utf-8"
            )
            _git_commit_all(wiki, "customize script")
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            # Sync REPLACES with codex source byte-equivalent
            self.assertEqual(
                _sha256(target_script),
                _sha256(REPO_ROOT / "_scripts" / "build_completion_dashboard.py"),
                "OVERWRITE failed: script not replaced",
            )

    def test_overwrite_procedure_files_replaced(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            target_ingest = wiki / "_context" / "INGEST_PROCEDURE.md"
            target_ingest.write_text("# stale ingest\n", encoding="utf-8")
            _git_commit_all(wiki, "customize ingest")
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                _sha256(target_ingest),
                _sha256(REPO_ROOT / "INGEST_PROCEDURE.md"),
                "OVERWRITE failed: INGEST_PROCEDURE.md not replaced",
            )

    def test_merge_new_only_existing_preserved(self):
        """ARCHITECTURAL FINDING #1: sync iterates codex's `_config/<filename>`
        directly (NOT `_template/_config__SEP__*` substituted). Test uses
        codex `_config/forbidden_terms.yaml` (actual codex _config file)
        rather than `_config/cross_link.yaml` (bootstrap-only target;
        not in codex's `_config/` source).
        """
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Customize wiki-side _config file that codex's _config/ has
            existing_config = wiki / "_config" / "forbidden_terms.yaml"
            customized_content = "rules: [{name: wiki_customization}]\n"
            existing_config.write_text(customized_content, encoding="utf-8")
            _git_commit_all(wiki, "customize forbidden_terms")
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                existing_config.read_text(encoding="utf-8"),
                customized_content,
                "MERGE-NEW-ONLY failed: existing _config not preserved",
            )
            self.assertIn(
                "[SKIP] _config/forbidden_terms.yaml", result.stdout
            )

    def test_never_touched_content_and_claude_context_rules_unchanged(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Customize content folder + CLAUDE_CONTEXT_RULES
            home = wiki / "Home.md"
            home.write_text("# Wiki Home customized\n", encoding="utf-8")
            claude_ctx = wiki / "_context" / "CLAUDE_CONTEXT_RULES.md"
            claude_ctx.write_text("# CTX customized\n", encoding="utf-8")
            _git_commit_all(wiki, "customize content+ctx")
            home_pre = _sha256(home)
            ctx_pre = _sha256(claude_ctx)
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            # Both UNCHANGED post-sync
            self.assertEqual(
                _sha256(home), home_pre, "NEVER-TOUCHED: Home.md modified"
            )
            self.assertEqual(
                _sha256(claude_ctx),
                ctx_pre,
                "NEVER-TOUCHED: CLAUDE_CONTEXT_RULES.md modified",
            )


class TestT2P53CrossLinkArtifactPrecedence(unittest.TestCase):
    """T-XL cascade amended-scope artifact precedence end-to-end at op-tier."""

    def test_cross_link_scripts_overwrite_at_e2e_tier(self):
        """4 cross-link scripts (T-XL-2..T-XL-5) → OVERWRITE at e2e tier."""
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Customize wiki-side cross-link script (stale)
            target = wiki / "_scripts" / "build_topic_index.py"
            target.write_text(
                "# wiki stale build_topic_index\n", encoding="utf-8"
            )
            _git_commit_all(wiki, "customize cross-link script")
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            # Sync REPLACES with codex source
            self.assertEqual(
                _sha256(target),
                _sha256(REPO_ROOT / "_scripts" / "build_topic_index.py"),
                "OVERWRITE failed: cross-link script not replaced",
            )
            # _lib/topics.py subdir replacement
            lib_topics = wiki / "_scripts" / "_lib" / "topics.py"
            self.assertEqual(
                _sha256(lib_topics),
                _sha256(REPO_ROOT / "_scripts" / "_lib" / "topics.py"),
                "OVERWRITE failed: _lib/topics.py not byte-equivalent",
            )

    def test_cross_link_templates_merge_new_when_absent_at_e2e_tier(self):
        """T-XL-7 cross-link templates → MERGE-NEW-ONLY when absent at e2e tier.

        ARCHITECTURAL FINDING #1 scope: sync iterates codex's `_template/`
        and writes to wiki's `_template/<filename>` preserving `__SEP__`.
        Bootstrap-time substitution does NOT create wiki/_template/* —
        sync does. Pre-sync: wiki/_template/ MAY OR MAY NOT have these
        files depending on prior sync. Test creates fresh wiki (no prior
        sync to _template/), verifies sync ADDS the templates with
        preserved `__SEP__` filenames.
        """
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Bootstrap does NOT populate wiki/_template/; sync does.
            # Verify pre-sync absence:
            topics_template = (
                wiki / "_template" / "_canon__SEP__topics.yaml"
            )
            cross_link_template = (
                wiki / "_template" / "_config__SEP__cross_link.yaml"
            )
            self.assertFalse(topics_template.is_file())
            self.assertFalse(cross_link_template.is_file())
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            # MERGE-NEW added both (preserving __SEP__ filenames per design)
            self.assertTrue(topics_template.is_file())
            self.assertTrue(cross_link_template.is_file())
            self.assertEqual(
                _sha256(topics_template),
                _sha256(REPO_ROOT / "_template" / "_canon__SEP__topics.yaml"),
                "MERGE-NEW failed: topics template byte-drift",
            )


class TestT2P53DryRunAndForce(unittest.TestCase):
    """--dry-run + --force flags per spec §4.2."""

    def test_dry_run_no_writes_preview_stdout(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Customize a script to verify NO writes during --dry-run
            target = wiki / "_scripts" / "build_completion_dashboard.py"
            pre_content = "# dry-run-preserve\n"
            target.write_text(pre_content, encoding="utf-8")
            _git_commit_all(wiki, "customize for dry-run")
            result = _run_sync(wiki, "--dry-run")
            self.assertEqual(result.returncode, 0)
            # File UNCHANGED post-dry-run
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                pre_content,
                "--dry-run wrote file",
            )

    def test_dirty_wiki_refused_without_force(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Introduce uncommitted change → dirty state
            (wiki / "_scripts" / "build_completion_dashboard.py").write_text(
                "# uncommitted change\n", encoding="utf-8"
            )
            result = _run_sync(wiki)
            # Sync refuses on dirty state (exit 2 per existing TestGuard)
            self.assertEqual(
                result.returncode, 2, "expected guard refusal exit 2"
            )

    def test_force_override_dirty_wiki_proceeds(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Introduce uncommitted change → dirty state
            (wiki / "_scripts" / "build_completion_dashboard.py").write_text(
                "# uncommitted change\n", encoding="utf-8"
            )
            result = _run_sync(wiki, "--force")
            self.assertEqual(
                result.returncode,
                0,
                "--force did not override guard; stderr={!r}".format(
                    result.stderr
                ),
            )


class TestT2P53LibrarianClassSyncPrecedence(unittest.TestCase):
    """T4d Librarian-class sync precedence verification (3 artifacts).

    Per Architect arbitration `item_1_codex_librarian_option_a_overwrite_approved`:
      - CODEX_LIBRARIAN.md → OVERWRITE (5th OVERWRITE artifact per Option A)
      - CLAUDE.librarian.md → MERGE-NEW-ONLY (via _template/ dir-level glob)
      - CLAUDE_CONTEXT_RULES.md → NEVER-TOUCHED (per spec §4.2)

    Extends T2 P53 sync e2e pattern with Librarian-class assertions.
    """

    def test_t4d_codex_librarian_overwrite_byte_replaced(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            target = wiki / "_context" / "CODEX_LIBRARIAN.md"
            target.write_text("# stale librarian\n", encoding="utf-8")
            _git_commit_all(wiki, "customize CODEX_LIBRARIAN")
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                _sha256(target),
                _sha256(REPO_ROOT / "CODEX_LIBRARIAN.md"),
                "OVERWRITE failed: CODEX_LIBRARIAN.md not replaced",
            )

    def test_t4d_codex_librarian_overwrite_constant_present_in_sync_module(self):
        sync_text = (REPO_ROOT / "_scripts" / "sync_from_kit.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'CODEX_LIBRARIAN_FILE = "CODEX_LIBRARIAN.md"',
            sync_text,
            "CODEX_LIBRARIAN_FILE constant absent from sync_from_kit.py",
        )

    def test_t4d_codex_librarian_overwrite_summary_marker(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            self.assertIn(
                "[OVERWRITE] _context/CODEX_LIBRARIAN.md",
                result.stdout,
                "OVERWRITE marker absent from sync summary",
            )

    def test_t4d_claude_librarian_dropin_merge_new_when_absent_added(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            template_target = (
                wiki
                / "_template"
                / ".claude__SEP__personas__SEP__CLAUDE.librarian.md"
            )
            self.assertFalse(template_target.is_file())
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(template_target.is_file())
            self.assertEqual(
                _sha256(template_target),
                _sha256(
                    REPO_ROOT
                    / "_template"
                    / ".claude__SEP__personas__SEP__CLAUDE.librarian.md"
                ),
                "MERGE-NEW added librarian drop-in template byte-drift",
            )

    def test_t4d_claude_librarian_dropin_merge_new_existing_preserved(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            template_target = (
                wiki
                / "_template"
                / ".claude__SEP__personas__SEP__CLAUDE.librarian.md"
            )
            template_target.parent.mkdir(parents=True, exist_ok=True)
            customized = "# wiki-customized librarian drop-in\n"
            template_target.write_text(customized, encoding="utf-8")
            _git_commit_all(wiki, "customize librarian drop-in")
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                template_target.read_text(encoding="utf-8"),
                customized,
                "MERGE-NEW-ONLY failed: customized librarian drop-in not preserved",
            )

    def test_t4d_claude_context_rules_never_touched_when_customized(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            ctx_rules = wiki / "_context" / "CLAUDE_CONTEXT_RULES.md"
            customized = "# wiki-customized CTX rules\n"
            ctx_rules.write_text(customized, encoding="utf-8")
            _git_commit_all(wiki, "customize CTX rules")
            pre_sha = _sha256(ctx_rules)
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                _sha256(ctx_rules),
                pre_sha,
                "NEVER-TOUCHED violated: CLAUDE_CONTEXT_RULES.md modified",
            )

    def test_t4d_codex_librarian_overwrite_dry_run_no_writes(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            target = wiki / "_context" / "CODEX_LIBRARIAN.md"
            pre_content = "# dry-run-preserve librarian\n"
            target.write_text(pre_content, encoding="utf-8")
            _git_commit_all(wiki, "pre-dry-run")
            result = _run_sync(wiki, "--dry-run")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                pre_content,
                "--dry-run wrote CODEX_LIBRARIAN.md",
            )

    def test_t4d_codex_librarian_force_overrides_dirty(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            (wiki / "_context" / "CODEX_LIBRARIAN.md").write_text(
                "# uncommitted\n", encoding="utf-8"
            )
            result = _run_sync(wiki, "--force")
            self.assertEqual(
                result.returncode,
                0,
                "--force did not override on CODEX_LIBRARIAN dirty wiki",
            )


if __name__ == "__main__":
    unittest.main()
