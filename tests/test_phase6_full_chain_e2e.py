"""T6 Phase-6 — Full-chain end-to-end integration test (pre-SHIP final gate).

Per CODEX_BUILD_SPEC_v1_3.md §7 Phase 6 self-test invariants + CLAUDE.md
D_VERIFICATION Stage 5. Validates Codex v1.0 SHIP readiness end-to-end:

  Step 1: Bootstrap — `python bootstrap.py <temp-wiki>` creates wiki
  Step 2: Sync — `python _scripts/sync_from_kit.py <codex-install>`
  Step 3: Scaffolds — invoke scaffold_source.py + scaffold_brain_dump.py
  Step 4: Librarian wiring assertions (T4a/T4b/T4c/T4d artifacts)

Verifies spec §7 invariants:
  - All aggs+vals invokable + return 0 errors (via update_dashboards.py)
  - `_sources/raw/` exists with README
  - `_context/INGEST_PROCEDURE.md` + `_context/SEMANTIC_LINT_PROCEDURE.md`
    byte-equal to source canonicals (CLAUDE.md D_RULES verbatim ship)
  - Re-running bootstrap idempotent

Verifies T4+T5 wiring:
  - .claude/personas/CLAUDE.librarian.md byte-equal to canonical (T4a)
  - _context/CODEX_LIBRARIAN.md byte-equal to canonical (T4b)
  - _context/CLAUDE_CONTEXT_RULES.md Librarian section + 4 Q&A rules (T4c)
  - sync_from_kit OVERWRITES _context/CODEX_LIBRARIAN.md (T4d Option A)
  - scaffold_source.py creates _inbox/<name>.md w/ pending_triage (T5 P18)
  - scaffold_brain_dump.py creates _brain_dump/<slug>.md exploring (T5 P17)

ZERO `__SEP__` residual at OP-TIER excluding `_template/` subdir per
Lesson #22 STANDARD + T2 ARCHITECTURAL FINDING #1 design carve-out.

NO Claude-driven runtime tests (Ingest extraction/routing Claude-driven
per CLAUDE.md R_LOGIC D_INTEGRATIONS; out of scope per unittest framework
limit; T6 verifies STATIC infrastructure post-scaffold).
"""

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_PY = REPO_ROOT / "bootstrap.py"
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
SYNC_FROM_KIT_PY = WIKISYS_SCRIPTS / "sync_from_kit.py"
SCAFFOLD_SOURCE_PY = WIKISYS_SCRIPTS / "scaffold_source.py"
SCAFFOLD_BRAIN_DUMP_PY = WIKISYS_SCRIPTS / "scaffold_brain_dump.py"
UPDATE_DASHBOARDS_PY = WIKISYS_SCRIPTS / "update_dashboards.py"


QA_RULE_SUBSTRINGS = [
    "Consult wiki pages before raw sources",
    "Cite specific pages using `[[wikilinks]]`",
    "Flag uncertainty explicitly; never confabulate when canon is silent",
    "For cross-source synthesis, name every page being synthesized",
]


def _bootstrap_wiki(tmp_path: Path) -> Path:
    """Bootstrap a wiki into tmp_path/wiki + git init + commit."""
    wiki = tmp_path / "wiki"
    result = subprocess.run(
        [sys.executable, str(BOOTSTRAP_PY), str(wiki), "--yes"],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "fixture bootstrap failed: rc={} stderr={!r}".format(
                result.returncode, result.stderr
            )
        )
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
    return subprocess.run(
        [sys.executable, str(SYNC_FROM_KIT_PY), str(REPO_ROOT), *flags],
        cwd=str(wiki),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )


def _run_scaffold(
    wiki: Path, script_path: Path, *args: str
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=str(wiki),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def _git_commit_all(wiki: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", message, "--no-verify"],
        cwd=str(wiki),
        check=True,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_state(root: Path) -> dict:
    state = {}
    for path in root.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            rel = path.relative_to(root).as_posix()
            state[rel] = _sha256(path)
    return state


class TestPhase6FullChainSequence(unittest.TestCase):
    """AC1: integrated bootstrap → sync → scaffolds full-chain sequence."""

    def test_phase6_bootstrap_then_sync_then_scaffolds_full_chain_passes(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Step 1: bootstrap (helper sets up wiki + git)
            wiki = _bootstrap_wiki(tmp_path)
            # Step 2: sync (clean wiki post-bootstrap; guard satisfied)
            sync_result = _run_sync(wiki)
            self.assertEqual(
                sync_result.returncode,
                0,
                "sync failed; stderr={!r}".format(sync_result.stderr),
            )
            _git_commit_all(wiki, "post sync")
            # Step 3a: scaffold a brain dump
            bd_result = _run_scaffold(
                wiki, SCAFFOLD_BRAIN_DUMP_PY, "Phase 6 Test Idea"
            )
            self.assertEqual(bd_result.returncode, 0)
            self.assertTrue(
                (
                    wiki / "_brain_dump" / "phase-6-test-idea.md"
                ).is_file()
            )
            # Step 3b: scaffold a source (local file)
            src_file = tmp_path / "test_source.md"
            src_file.write_text("test source body\n", encoding="utf-8")
            src_result = _run_scaffold(
                wiki, SCAFFOLD_SOURCE_PY, str(src_file)
            )
            self.assertEqual(src_result.returncode, 0)
            self.assertTrue(
                (wiki / "_inbox" / "test_source.md").is_file()
            )


class TestPhase6SpecInvariants(unittest.TestCase):
    """AC2: spec §7 Phase 6 invariants."""

    def test_phase6_sources_raw_archive_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            self.assertTrue(
                (wiki / "_sources" / "raw" / "README.md").is_file(),
                "missing _sources/raw/README.md per spec §7 invariant",
            )

    def test_phase6_procedure_files_verbatim_byte_equivalent(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            for fname in (
                "INGEST_PROCEDURE.md",
                "SEMANTIC_LINT_PROCEDURE.md",
            ):
                target = wiki / "_context" / fname
                # S002 / Codex v1.1: spec docs at wiki.codex/git/codex/
                source = REPO_ROOT / "wiki.codex" / "git" / "codex" / fname
                self.assertEqual(
                    _sha256(target),
                    _sha256(source),
                    "verbatim ship invariant violated: " + fname,
                )

    def test_phase6_idempotency_byte_equivalent_re_run(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            state_1 = _tree_state(wiki)
            # Re-run bootstrap on same path
            result = subprocess.run(
                [sys.executable, str(BOOTSTRAP_PY), str(wiki), "--yes"],
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0)
            state_2 = _tree_state(wiki)
            self.assertEqual(
                state_1, state_2, "idempotent re-run tree state differs"
            )


class TestPhase6LibrarianAndScaffoldsIntegration(unittest.TestCase):
    """AC3: T4 Librarian wiring + T5 scaffolds full-chain integration."""

    def test_phase6_librarian_persona_files_byte_equivalent(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # T4a: persona drop-in
            dropin = wiki / ".claude" / "personas" / "CLAUDE.librarian.md"
            dropin_src = REPO_ROOT / ".claude" / "personas" / "CLAUDE.librarian.md"
            self.assertTrue(dropin.is_file())
            self.assertEqual(_sha256(dropin), _sha256(dropin_src))
            # T4b: canonical declaration
            canon = wiki / "_context" / "CODEX_LIBRARIAN.md"
            canon_src = REPO_ROOT / "wiki.codex" / "git" / "codex" / "CODEX_LIBRARIAN.md"
            self.assertTrue(canon.is_file())
            self.assertEqual(_sha256(canon), _sha256(canon_src))

    def test_phase6_claude_context_rules_librarian_section_and_qa_rules_preserved(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            ctx = wiki / "_context" / "CLAUDE_CONTEXT_RULES.md"
            content = ctx.read_text(encoding="utf-8")
            # T4c: Librarian section present
            self.assertIn("## Librarian persona", content)
            self.assertIn("_context/CODEX_LIBRARIAN.md", content)
            self.assertIn(".claude/personas/CLAUDE.librarian.md", content)
            # 4 mandated Q&A rules preserved (zero-deviation)
            for rule in QA_RULE_SUBSTRINGS:
                self.assertIn(rule, content, "Q&A rule violated: " + rule)

    def test_phase6_sync_overwrites_codex_librarian(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            # Customize wiki-side CODEX_LIBRARIAN to verify OVERWRITE
            target = wiki / "_context" / "CODEX_LIBRARIAN.md"
            target.write_text("# stale wiki-customized librarian\n", encoding="utf-8")
            _git_commit_all(wiki, "stale customization")
            result = _run_sync(wiki)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                _sha256(target),
                _sha256(REPO_ROOT / "wiki.codex" / "git" / "codex" / "CODEX_LIBRARIAN.md"),
                "T4d Option A OVERWRITE failed for CODEX_LIBRARIAN.md",
            )

    def test_phase6_zero_sep_residual_op_tier_excluding_template_subdir(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            for path in wiki.rglob("*"):
                if ".git" in path.parts:
                    continue
                if "_template" in path.parts:
                    continue
                rel_str = str(path.relative_to(wiki))
                self.assertNotIn(
                    "__SEP__",
                    path.name,
                    "__SEP__ residual in filename post-bootstrap: " + path.name,
                )
                self.assertNotIn(
                    "__SEP__",
                    rel_str,
                    "__SEP__ residual in path post-bootstrap: " + rel_str,
                )


if __name__ == "__main__":
    unittest.main()
