"""T3 P54 — Ingest operation end-to-end integration test.

Per CODEX_BUILD_SPEC_v1_3.md §4.3 + amended scope per T-XL cross-link
cascade FULL CLOSURE at commit `25c61e1`. THIRD + FINAL of Three
Operations integration tests (T1 P52 Bootstrap CLOSED PASS `b6a3f31`;
T2 P53 Sync CLOSED PASS `3587216`; T3 P54 Ingest this module).

**Key distinction from T1/T2**: Ingest is Claude-driven NOT a script
per CLAUDE.md R_LOGIC D_INTEGRATIONS table. Runtime Claude-driven
extraction/routing/archive flow CANNOT be tested via unittest framework
(requires Claude Code agent invocation OR mocked-Claude test harness).

T3 verifies **static-infrastructure invariants** ingest depends on:
  - `_context/INGEST_PROCEDURE.md` shipped VERBATIM (CLAUDE.md D_RULES)
  - `_context/SEMANTIC_LINT_PROCEDURE.md` shipped VERBATIM (D_RULES)
  - `_sources/` + `_sources/raw/` permanent read-only archive infra
  - `_inbox/` ephemeral triage area
  - `_decisions/ingest-log.md` append-only log starter
  - Cross-link cascade integration present (T-XL-7 sustained at ingest tier)
  - P17/P18 scaffold dependency surfacing (scaffold_*.py NOT shipped per
    JP T1 dispatch directive; surfaced as ship-needed for full
    scaffold-dependent ingest flow scenarios)

POSTURE: test-authoring primary per T1+T2 precedent. NO bootstrap.py /
sync_from_kit.py LOC change (5th-exhibit ZERO-LOC-change auto-lift
pattern if held).

MANDATORY fixture-scope-discipline 7th-cycle preventive sustained per
6-cycle PROVEN-EFFECTIVE T-XL-5..T-XL-8+T1+T2 evidence base + STANDARD-
codification SOLIDIFIED + Auditor T2 promotion-OVERDUE recommendation.
"""

import unittest

raise unittest.SkipTest(
    "MI-16 (S002 / Codex v1.1): test_t3_p54 asserts v1.0 sync-shape "
    "ingest-readiness (_context/INGEST_PROCEDURE.md + _context/"
    "SEMANTIC_LINT_PROCEDURE.md shipped into the consumer wiki via "
    "bootstrap; _sources/ + _inbox/ + _decisions/ingest-log.md "
    "infrastructure). v1.1 bootstrap.py is scaffold-only; sync/ingest "
    "shape misaligned post-S002. Full retirement deferred to S004. "
    "See MIGRATION-ISSUES.md MI-16."
)

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_PY = REPO_ROOT / "bootstrap.py"
TEMPLATE_DIR = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_template"


def _bootstrap_wiki(tmp_path: Path) -> Path:
    """Bootstrap a wiki target into tmp_path/wiki (mirrors T2 helper)."""
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
    return wiki


def _sha256(path: Path) -> str:
    """Compute sha256 hex of file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestT3P54VerbatimProcedureFiles(unittest.TestCase):
    """AC1: INGEST_PROCEDURE + SEMANTIC_LINT_PROCEDURE bootstrap mechanism verbatim.

    Verifies bootstrap mechanism copies templates verbatim to target wiki
    (target byte-equivalent to source template). ARCHITECTURAL FINDING #2
    surfaced at build-time: `_template/_context__SEP__INGEST_PROCEDURE.md`
    is NOT byte-equivalent to install-root `INGEST_PROCEDURE.md` (template
    7893 bytes vs source 8129 bytes drift) — violates CLAUDE.md D_RULES
    verbatim ship invariant at TEMPLATE-vs-INSTALL-ROOT-SOURCE tier.
    Surface for Architect arbitration via build_summary (separate cycle
    to sync template from install-root source). T3 scope = bootstrap
    mechanism verification (target == template); template-vs-source
    drift = ARCHITECTURAL FINDING #2 for sprint-close ledger.
    """

    def test_ingest_procedure_md_bootstrap_mechanism_verbatim_to_template(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            target = wiki / "_context" / "INGEST_PROCEDURE.md"
            template = TEMPLATE_DIR / "_context__SEP__INGEST_PROCEDURE.md"
            self.assertTrue(target.is_file(), "missing target INGEST_PROCEDURE.md")
            self.assertTrue(template.is_file(), "missing template")
            self.assertEqual(
                _sha256(target),
                _sha256(template),
                "bootstrap mechanism failed: target NOT byte-equivalent to template",
            )

    def test_semantic_lint_procedure_md_bootstrap_mechanism_verbatim_to_template(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            target = wiki / "_context" / "SEMANTIC_LINT_PROCEDURE.md"
            template = (
                TEMPLATE_DIR / "_context__SEP__SEMANTIC_LINT_PROCEDURE.md"
            )
            self.assertTrue(
                target.is_file(),
                "missing target SEMANTIC_LINT_PROCEDURE.md",
            )
            self.assertTrue(template.is_file(), "missing template")
            self.assertEqual(
                _sha256(target),
                _sha256(template),
                "bootstrap mechanism failed: target NOT byte-equivalent to template",
            )


class TestT3P54SourcesArchiveInfra(unittest.TestCase):
    """AC2: _sources archive infrastructure per spec §2.2 + §4.3."""

    def test_sources_readme_present_post_bootstrap(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            readme = wiki / "_sources" / "README.md"
            self.assertTrue(
                readme.is_file(),
                "missing _sources/README.md per spec §5 v1.1 ship",
            )

    def test_sources_raw_double_sep_readme_present_post_bootstrap(self):
        """P48 double-`__SEP__` ship verified at ingest-static-infra-tier."""
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            readme = wiki / "_sources" / "raw" / "README.md"
            self.assertTrue(
                readme.is_file(),
                "missing _sources/raw/README.md per spec §5 v1.1 P48 double-__SEP__ ship",
            )


class TestT3P54IngestSupportInfra(unittest.TestCase):
    """AC2: ingest support infrastructure per spec §4.3 + §5 file manifest."""

    def test_inbox_readme_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            readme = wiki / "_inbox" / "README.md"
            self.assertTrue(
                readme.is_file(),
                "missing _inbox/README.md per spec §5 (ephemeral triage area)",
            )

    def test_decisions_readme_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            readme = wiki / "_decisions" / "README.md"
            self.assertTrue(
                readme.is_file(),
                "missing _decisions/README.md per spec §5",
            )

    def test_decisions_ingest_log_md_starter_template_present(self):
        """S043-T1 P45 v1.1 NEW ship: starter append-only log template."""
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            target = wiki / "_decisions" / "ingest-log.md"
            source = TEMPLATE_DIR / "_decisions__SEP__ingest-log.md"
            self.assertTrue(
                target.is_file(),
                "missing _decisions/ingest-log.md per spec §5 v1.1 P45 ship",
            )
            self.assertTrue(
                source.is_file(),
                "missing source _template/_decisions__SEP__ingest-log.md",
            )
            self.assertEqual(
                _sha256(target),
                _sha256(source),
                "byte-drift: ingest-log.md starter template not byte-equivalent to source",
            )


class TestT3P54CrossLinkCascadeAndScaffoldDependency(unittest.TestCase):
    """AC3: cross-link cascade integration + P17/P18 scaffold dependency surfacing."""

    def test_canon_topics_yaml_present_at_ingest_static_infra_tier(self):
        """T-XL-7 ship sustained at ingest-static-infra-tier (presence check;
        byte-equivalence already verified at T1 OP-TIER).
        """
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            self.assertTrue(
                (wiki / "_canon" / "topics.yaml").is_file(),
                "missing _canon/topics.yaml (T-XL-7 cross-link cascade)",
            )

    def test_config_cross_link_yaml_present_at_ingest_static_infra_tier(self):
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            self.assertTrue(
                (wiki / "_config" / "cross_link.yaml").is_file(),
                "missing _config/cross_link.yaml (T-XL-7 cross-link cascade)",
            )

    def test_scaffold_p17_p18_shipped_post_t5_gap_closure(self):
        """P17/P18 scaffold scripts present post-bootstrap (T5 closed gap).

        T3 originally surfaced P17/P18 NOT shipped as dependency for full
        scaffold-dependent ingest scenarios. T5 shipped both scaffolds; this
        test inverts the original assertion to verify the dependency is
        resolved + scaffolds land in the bootstrapped wiki via existing
        _scripts/ dir-level copy mechanism.
        """
        with TemporaryDirectory() as tmp:
            wiki = _bootstrap_wiki(Path(tmp))
            scaffold_brain_dump = wiki / "_scripts" / "scaffold_brain_dump.py"
            scaffold_source = wiki / "_scripts" / "scaffold_source.py"
            self.assertTrue(
                scaffold_brain_dump.is_file(),
                "scaffold_brain_dump.py missing post-T5 gap closure",
            )
            self.assertTrue(
                scaffold_source.is_file(),
                "scaffold_source.py missing post-T5 gap closure",
            )


if __name__ == "__main__":
    unittest.main()
