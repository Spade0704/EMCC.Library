"""Real-tree S1-doc smoke test for Codex spec docs (S023-T2-α AC9).

Iterates every .md file under the Codex spec-docs canonical folder in
the live working tree and asserts s1_doc(path).ok == True. Per-file ok
flag only — not a deep diff. Acts as the regression gate for any
future doc_lint change.

S002 / MI-11 (2026-05-27): originally iterated `documents/lattice/`
(Lattice 2.0 framework docs in project-codex). Library post-Codex-
extraction has no documents/lattice/ — those stayed in project-codex's
archive. v1.1 repoints to `wiki.codex/git/codex/` (Codex's own spec
docs canonical location post-B3 move). See MIGRATION-ISSUES.md MI-11.

Pattern #13 real-tree smoke discipline (lessons.md 2026-05-08): catches
class-of-bug regressions that synthetic per-test fixtures don't exercise
(e.g., escape-pipe in tables, multi-doc cross-ref webs, heading-depth
conventions across the spec doc family).

Test-method generation: one TestCase method per .md file, dynamically
attached via setattr loop. Per-file failures are isolated in the runner.
"""

import unittest
from pathlib import Path

from _lib import doc_lint


REPO_ROOT = Path(__file__).resolve().parent.parent
# S002 / MI-11: repointed from documents/lattice/ (project-codex only)
# to wiki.codex/git/codex/ (Library's Codex spec docs post-B3).
SPEC_DOCS = REPO_ROOT / "wiki.codex" / "git" / "codex"


def _normalize_name(stem: str) -> str:
    """Convert a filename stem into a valid Python test-method suffix."""
    return stem.replace("-", "_").replace(".", "_")


def _make_test(md_path: Path):
    def _test(self):
        result = doc_lint.s1_doc(md_path, REPO_ROOT)
        self.assertTrue(
            result.ok,
            f"{md_path.relative_to(REPO_ROOT)} not ok=True;\n"
            f"  errors={result.errors}\n"
            f"  warnings={result.warnings}"
        )
    _test.__doc__ = f"S1-doc smoke for {md_path.relative_to(REPO_ROOT)}"
    return _test


class TestDocLintFullTree(unittest.TestCase):
    """Full-tree S1-doc smoke; one test method per Codex spec-doc .md file."""


# Generate a test method per spec-doc .md file at module import time.
if SPEC_DOCS.is_dir():
    for _md in sorted(SPEC_DOCS.glob("*.md")):
        _suffix = _normalize_name(_md.stem)
        _name = f"test_codex_spec_{_suffix}"
        setattr(TestDocLintFullTree, _name, _make_test(_md))


if __name__ == "__main__":
    unittest.main()
