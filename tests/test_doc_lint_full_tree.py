"""Real-tree S1-doc smoke test for documents/lattice/*.md (S023-T2-α AC9).

Iterates every .md file under documents/lattice/ in the live working tree
and asserts s1_doc(path).ok == True. Per-file ok flag only — not a deep
diff. Acts as the regression gate for any future doc_lint change AND as
acceptance proof that S023-T2-α AC1+AC3+AC4 fixes leave the real lattice
tree clean (no false-positives surfacing per the sequence-gate clause in
the task body).

Pattern #13 real-tree smoke discipline (lessons.md 2026-05-08): catches
class-of-bug regressions that synthetic per-test fixtures don't exercise
(e.g., escape-pipe in 07-OPERATIONS.md tables, multi-doc cross-ref webs,
heading-depth conventions across 11+ framework docs).

Test-method generation: one TestCase method per .md file, dynamically
attached via setattr loop. This keeps each lattice doc as a distinct
unittest data point so per-file failures are isolated in the runner output.
"""

import unittest
from pathlib import Path

from _lib import doc_lint


REPO_ROOT = Path(__file__).resolve().parent.parent
LATTICE_DOCS = REPO_ROOT / "documents" / "lattice"


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
    """Full-tree S1-doc smoke; one test method per lattice .md file."""


# Generate a test method per lattice .md file at module import time.
if LATTICE_DOCS.is_dir():
    for _md in sorted(LATTICE_DOCS.glob("*.md")):
        _suffix = _normalize_name(_md.stem)
        _name = f"test_lattice_{_suffix}"
        setattr(TestDocLintFullTree, _name, _make_test(_md))


if __name__ == "__main__":
    unittest.main()
