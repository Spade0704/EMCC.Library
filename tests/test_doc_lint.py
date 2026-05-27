"""Tests for _scripts/_lib/doc_lint.py — Lattice v0.1.8 §5.7.bis S1-doc helper.

Covers AC1-AC4 of S021-T2-doc-lint-helper per LATTICE_v0.1.8_SCRIBE_SPEC.md
§5.7.bis + S023-T2-α hardening AC1-AC7 (escape-pipe, word-boundary, initial-
heading-skip, indented fence, perf-test rename, persona-class schema, parser-
exception contract).

Test count: 19 (S021-T2 baseline) + 6 net-new (S023-T2-α: AC1, AC2 ×2, AC3,
AC4, AC6) = 25 in this file. AC8 (P1 public name) test lives in
tests/_lib/test_frontmatter.py. AC9 (full-tree smoke) lives in
tests/test_doc_lint_full_tree.py.

Parser-exception contract (S023-T2-α AC7): _scripts/_lib/doc_lint.py assumes
`_lib.frontmatter.parse_frontmatter` is contract-not-to-raise. If a future P1
change introduces an exception path, exceptions propagate uncaught from
s1_doc — tests in this module would fail at the call site. Revisit this
contract if P1 raises: either catch + treat as structural error, or update
parse_frontmatter spec to forbid raises. Currently no caller of doc_lint
shields against P1 exceptions.
"""

import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _lib import doc_lint


REPO_ROOT = Path(__file__).resolve().parent.parent
LATTICE_DOCS = REPO_ROOT / "documents" / "lattice"


def _write(p: Path, content: str) -> None:
    p.write_text(content, encoding="utf-8")


def _well_formed_fm() -> str:
    return (
        "---\n"
        "title: Sample Page\n"
        "type: framework\n"
        "visibility: internal\n"
        "completion: 80\n"
        "status: ready\n"
        "last_updated: 2026-05-08\n"
        "canon_sources: []\n"
        "unverified_claims: []\n"
        "---\n"
        "\n"
        "# Body\n"
    )


# ===== Frontmatter (>=6, AC2) =====

class TestCheckFrontmatter(unittest.TestCase):
    def test_check_frontmatter_no_fm_block_passes_silently(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "no_fm.md"
            _write(p, "# Just a heading\nBody\n")
            r = doc_lint.check_frontmatter(p)
            self.assertTrue(r.ok)
            self.assertEqual(r.errors, [])
            self.assertEqual(r.warnings, [])
            self.assertIsNone(r.parsed)

    def test_check_frontmatter_well_formed_with_all_required_keys(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "good.md"
            _write(p, _well_formed_fm())
            r = doc_lint.check_frontmatter(p)
            self.assertTrue(r.ok)
            self.assertEqual(r.errors, [])
            self.assertEqual(r.warnings, [],
                             "no warnings expected on full required-key set")
            self.assertEqual(r.parsed["title"], "Sample Page")
            self.assertEqual(r.parsed["type"], "framework")

    def test_check_frontmatter_unclosed_block_emits_error(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "unclosed.md"
            _write(p, "---\ntitle: X\n# body without close\n")
            r = doc_lint.check_frontmatter(p)
            self.assertFalse(r.ok)
            self.assertTrue(any("unclosed" in e for e in r.errors),
                            f"errors should mention 'unclosed': {r.errors}")

    def test_check_frontmatter_malformed_line_emits_error(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "malformed.md"
            _write(p, "---\ntitle: X\nthis is not yaml\n---\nBody\n")
            r = doc_lint.check_frontmatter(p)
            self.assertFalse(r.ok)
            self.assertTrue(any("malformed line" in e for e in r.errors))

    def test_check_frontmatter_missing_required_keys_emits_warnings(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "partial.md"
            _write(p, "---\ntitle: X\ntype: framework\n---\nBody\n")
            r = doc_lint.check_frontmatter(p)
            self.assertTrue(r.ok, "missing keys must NOT fail per spec §2.5 permissive")
            self.assertGreaterEqual(len(r.warnings), 6,
                                    "8 required - 2 present = 6 missing warnings")
            self.assertIn("status", r.required_keys_missing)
            self.assertIn("canon_sources", r.required_keys_missing)
            self.assertIn("unverified_claims", r.required_keys_missing)

    def test_check_frontmatter_extra_unknown_keys_emit_warnings(self):
        fm = (
            "---\n"
            "title: X\n"
            "type: framework\n"
            "visibility: internal\n"
            "completion: 80\n"
            "status: ready\n"
            "last_updated: 2026-05-08\n"
            "canon_sources: []\n"
            "unverified_claims: []\n"
            "completely_unknown_key: foo\n"
            "---\n"
            "Body\n"
        )
        with TemporaryDirectory() as td:
            p = Path(td) / "extra.md"
            _write(p, fm)
            r = doc_lint.check_frontmatter(p)
            self.assertTrue(r.ok)
            self.assertTrue(any("unknown key" in w for w in r.warnings))
            self.assertIn("completely_unknown_key", r.unknown_keys)

    def test_check_frontmatter_empty_block_warns_all_required(self):
        # Edge case (d) per task body: '---' line 1 + '---' line 2; empty fm.
        with TemporaryDirectory() as td:
            p = Path(td) / "empty_fm.md"
            _write(p, "---\n---\nBody\n")
            r = doc_lint.check_frontmatter(p)
            self.assertTrue(r.ok, "empty-fm structurally valid; warnings only")
            self.assertEqual(r.errors, [])
            self.assertEqual(len(r.required_keys_missing), 8,
                             "all 8 required keys missing")

    def test_check_frontmatter_persona_class_drop_ins_lint_clean(self):
        # S023-T2-α AC6: persona drop-ins lint with 0 warnings under
        # persona-class schema. Dual-trigger: fm `type: persona` OR path
        # `.claude/personas/CLAUDE.*.md`.
        #
        # S002 / MI-10 (2026-05-27): generalized. Original test
        # hard-asserted >=4 drop-ins expecting the four Lattice 2.0
        # personas (architect/auditor/craftsman/scribe). Library
        # post-Codex-extraction has only 2 (auditor + librarian) per
        # MIGRATION-ISSUES.md MI-10. Test now lints whatever drop-ins
        # ARE present + requires at least one. Existence-of-Lattice-2-
        # specific-personas assertion retired.
        personas_dir = REPO_ROOT / ".claude" / "personas"
        if not personas_dir.is_dir():
            self.skipTest("persona drop-in dir not at expected path")
        drop_ins = sorted(personas_dir.glob("CLAUDE.*.md"))
        self.assertGreater(len(drop_ins), 0,
                           "expected at least one persona drop-in at "
                           ".claude/personas/CLAUDE.*.md")
        for p in drop_ins:
            r = doc_lint.check_frontmatter(p)
            self.assertTrue(r.ok, f"{p.name} fm structurally invalid: {r.errors}")
            self.assertEqual(r.warnings, [],
                             f"{p.name} should lint with 0 warnings under "
                             f"persona-class schema; got: {r.warnings}")


# ===== AllowList spec §2.3 fields (S047-T7) =====

class AllowListSpecFieldsTests(unittest.TestCase):
    """S047-T7 — 7 spec §2.3 optional fields added to _ALLOWED_FM_KEYS
    (phase, public_pair, source, generated, topics, related_files, tags).
    Cluster surfaced at S047-T5 Scribe Loop 5 via public_pair false-positive.
    Each positive fixture asserts the field name is not in r.unknown_keys
    and does NOT trigger an 'unknown key' warning. One negative fixture
    guards the regression path — a truly-unknown key STILL warns.
    """

    _REQUIRED_FM = (
        "title: X\n"
        "type: framework\n"
        "visibility: internal\n"
        "completion: 80\n"
        "status: ready\n"
        "last_updated: 2026-05-08\n"
        "canon_sources: []\n"
        "unverified_claims: []\n"
    )

    def _fm_with(self, extra_line: str) -> str:
        return "---\n" + self._REQUIRED_FM + extra_line + "---\nBody\n"

    def _assert_field_allowed(self, extra_line: str, field_name: str):
        with TemporaryDirectory() as td:
            p = Path(td) / "p.md"
            _write(p, self._fm_with(extra_line))
            r = doc_lint.check_frontmatter(p)
            self.assertNotIn(field_name, r.unknown_keys)
            self.assertFalse(
                any("unknown key" in w and field_name in w for w in r.warnings),
                f"{field_name} should not trigger 'unknown key' warning; got: {r.warnings}",
            )

    def test_phase_field_no_warning(self):
        self._assert_field_allowed("phase: 1\n", "phase")

    def test_public_pair_field_no_warning(self):
        self._assert_field_allowed('public_pair: "public/Briefing.md"\n', "public_pair")

    def test_source_field_no_warning(self):
        self._assert_field_allowed('source: "Some citation"\n', "source")

    def test_generated_field_no_warning(self):
        self._assert_field_allowed("generated: true\n", "generated")

    def test_topics_field_no_warning(self):
        self._assert_field_allowed('topics: ["alpha"]\n', "topics")

    def test_related_files_field_no_warning(self):
        self._assert_field_allowed("related_files: []\n", "related_files")

    def test_tags_field_no_warning(self):
        self._assert_field_allowed("tags: []\n", "tags")

    def test_truly_unknown_key_still_warns(self):
        """Negative regression guard — allow-list extension must NOT
        break the 'unknown key' warning path for genuinely-unknown keys.
        """
        with TemporaryDirectory() as td:
            p = Path(td) / "p.md"
            _write(p, self._fm_with("not_a_real_key: foo\n"))
            r = doc_lint.check_frontmatter(p)
            self.assertTrue(any("unknown key" in w for w in r.warnings))
            self.assertIn("not_a_real_key", r.unknown_keys)

    # ----- S048-T0 SSOT registry drift-impossibility tests -----

    def test_allowed_set_equals_registry_plus_project_extras(self):
        """Snapshot equality: doc_lint._ALLOWED_FM_KEYS derives from
        frontmatter.SPEC_2_3_FM_FIELDS + 3 project-precedent extras.
        Proves derivation correctness at module level.
        """
        from _lib import frontmatter
        expected = frozenset(
            frontmatter.SPEC_2_3_FM_FIELDS + ("version", "role", "audience")
        )
        self.assertEqual(doc_lint._ALLOWED_FM_KEYS, expected)

    def test_drift_impossible_new_field_in_registry_is_honored(self):
        """Add a hypothetical field to the registry, reload doc_lint, and
        confirm the field appears in _ALLOWED_FM_KEYS without a second
        edit to doc_lint. Restores registry + reloads in finally so the
        mutation does not leak to subsequent tests.
        """
        import importlib
        from _lib import frontmatter
        original = frontmatter.SPEC_2_3_FM_FIELDS
        guard_field = "test_field_xyz_drift_guard"
        try:
            frontmatter.SPEC_2_3_FM_FIELDS = original + (guard_field,)
            importlib.reload(doc_lint)
            self.assertIn(guard_field, doc_lint._ALLOWED_FM_KEYS)
        finally:
            frontmatter.SPEC_2_3_FM_FIELDS = original
            importlib.reload(doc_lint)

    def test_t7_7_fields_preserved_via_registry(self):
        """Regression guard against registry extraction dropping a T7
        field (phase / public_pair / source / generated / topics /
        related_files / tags).
        """
        from _lib import frontmatter
        for field_name in (
            "phase",
            "public_pair",
            "source",
            "generated",
            "topics",
            "related_files",
            "tags",
        ):
            self.assertIn(
                field_name, frontmatter.SPEC_2_3_FM_FIELDS,
                f"{field_name} (S047-T7 field) missing from SSOT registry",
            )

    def test_registry_docstring_cites_spec_2_3(self):
        """Documentation-correctness guard: sibling docstring constant
        SPEC_2_3_FM_FIELDS_DOC must cite the canonical spec source so
        future readers can trace the registry back to spec §2.3.
        """
        from _lib import frontmatter
        self.assertIn(
            "CODEX_BUILD_SPEC_v1_3.md §2.3",
            frontmatter.SPEC_2_3_FM_FIELDS_DOC,
        )


# ===== Cross-refs (>=4, AC2) =====

class TestCheckCrossRefs(unittest.TestCase):
    def test_check_cross_refs_valid_internal_link_passes(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            target = root / "target.md"
            _write(target, "# Target\n")
            src = root / "src.md"
            _write(src, "See [link](target.md) here.\n")
            r = doc_lint.check_cross_refs(src, root)
            self.assertTrue(r.ok)
            self.assertEqual(r.refs_checked, 1)
            self.assertEqual(r.dead_refs, [])

    def test_check_cross_refs_dead_internal_link_emits_error(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src.md"
            _write(src, "Broken [link](missing.md) here.\n")
            r = doc_lint.check_cross_refs(src, root)
            self.assertFalse(r.ok)
            self.assertEqual(r.dead_refs, ["missing.md"])
            self.assertTrue(any("dead link" in e for e in r.errors))

    def test_check_cross_refs_external_urls_skipped(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src.md"
            _write(src,
                "External [ext](https://example.com/x.md) and "
                "[m](mailto:x@y.md) and [http](http://nope.invalid/y.md).\n"
            )
            r = doc_lint.check_cross_refs(src, root)
            self.assertTrue(r.ok)
            self.assertEqual(r.refs_checked, 0,
                             "external URLs MUST NOT be validated")

    def test_check_cross_refs_relative_path_traversal_resolves(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            sub = root / "sub"
            sub.mkdir()
            parent_target = root / "parent.md"
            _write(parent_target, "# parent\n")
            self_target = sub / "self.md"
            _write(self_target, "# self\n")
            src = sub / "src.md"
            _write(src,
                "Up [link](../parent.md) and self [s](./self.md#anchor)\n"
            )
            r = doc_lint.check_cross_refs(src, root)
            self.assertTrue(r.ok)
            self.assertEqual(r.refs_checked, 2)
            self.assertEqual(r.dead_refs, [])

    def test_check_cross_refs_documents_lattice_text_form_matched(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "documents" / "lattice").mkdir(parents=True)
            real = root / "documents" / "lattice" / "00-README.md"
            _write(real, "# README\n")
            src = root / "src.md"
            _write(src,
                "See documents/lattice/00-README.md and "
                "documents/lattice/MISSING.md.\n"
            )
            r = doc_lint.check_cross_refs(src, root)
            self.assertFalse(r.ok)
            self.assertEqual(r.refs_checked, 2)
            self.assertIn("documents/lattice/MISSING.md", r.dead_refs)
            self.assertNotIn("documents/lattice/00-README.md", r.dead_refs)

    def test_check_cross_refs_fenced_code_strip_discipline(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src.md"
            _write(src,
                "Real link [x](missing.md)\n"
                "```\n"
                "This is code: [fake](missing-too.md)\n"
                "```\n"
            )
            r = doc_lint.check_cross_refs(src, root)
            self.assertFalse(r.ok)
            self.assertEqual(r.refs_checked, 1,
                             "code-block link MUST NOT be scanned")
            self.assertEqual(r.dead_refs, ["missing.md"])

    def test_check_cross_refs_lattice_text_ref_word_boundary_positive(self):
        # S023-T2-α AC2: bare 'documents/lattice/foo.md' at start-of-string
        # OR after non-word char must match _LATTICE_TEXT_REF_RE (\b prefix).
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "documents" / "lattice").mkdir(parents=True)
            real = root / "documents" / "lattice" / "valid.md"
            _write(real, "# valid\n")
            src = root / "src.md"
            _write(src,
                "See documents/lattice/valid.md and "
                "(parens-prefix)documents/lattice/missing.md.\n"
            )
            r = doc_lint.check_cross_refs(src, root)
            self.assertFalse(r.ok, "missing.md must be flagged as dead")
            self.assertEqual(r.refs_checked, 2,
                             "both word-boundary-anchored refs scanned")
            self.assertIn("documents/lattice/missing.md", r.dead_refs)

    def test_check_cross_refs_lattice_text_ref_word_boundary_negative(self):
        # S023-T2-α AC2: 'xdocuments/lattice/foo.md' (preceded by word char)
        # must NOT match — \b prefix prevents word-internal matches.
        with TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src.md"
            _write(src, "Token-sticky xdocuments/lattice/missing.md noise.\n")
            r = doc_lint.check_cross_refs(src, root)
            self.assertTrue(r.ok,
                            "word-internal pseudo-ref MUST NOT be scanned")
            self.assertEqual(r.refs_checked, 0)
            self.assertEqual(r.dead_refs, [])


# ===== Markdown lint (>=4, AC2) =====

class TestCheckMarkdownLint(unittest.TestCase):
    def test_check_markdown_lint_well_formed_passes(self):
        body = (
            "# Top\n"
            "## Sub\n"
            "### Subsub\n"
            "Some prose.\n"
            "```python\n"
            "x = 1\n"
            "```\n"
            "| col1 | col2 |\n"
            "|------|------|\n"
            "| a    | b    |\n"
        )
        with TemporaryDirectory() as td:
            p = Path(td) / "good.md"
            _write(p, body)
            r = doc_lint.check_markdown_lint(p)
            self.assertTrue(r.ok)
            self.assertEqual(r.errors, [])
            self.assertEqual(r.warnings, [])

    def test_check_markdown_lint_unclosed_fence_emits_error(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "bad_fence.md"
            _write(p, "Body.\n```\nopen forever\n")
            r = doc_lint.check_markdown_lint(p)
            self.assertFalse(r.ok)
            self.assertTrue(any("unclosed" in e for e in r.errors))

    def test_check_markdown_lint_heading_skip_emits_warning(self):
        body = "# Top\n### Skipped H2\n"
        with TemporaryDirectory() as td:
            p = Path(td) / "skip.md"
            _write(p, body)
            r = doc_lint.check_markdown_lint(p)
            self.assertTrue(r.ok, "heading skip is warning, not error")
            self.assertTrue(any("hierarchy skip" in w for w in r.warnings))

    def test_check_markdown_lint_table_column_mismatch_emits_warning(self):
        body = (
            "| col1 | col2 |\n"
            "|------|------|\n"
            "| a    | b    |\n"
            "| onlyOne |\n"
        )
        with TemporaryDirectory() as td:
            p = Path(td) / "table.md"
            _write(p, body)
            r = doc_lint.check_markdown_lint(p)
            self.assertTrue(r.ok, "column mismatch is warning, not error")
            self.assertTrue(any("column-count mismatch" in w for w in r.warnings))

    def test_check_markdown_lint_escape_pipe_no_false_positive(self):
        # S023-T2-α AC1: table cells containing '\|' (literal escape-pipe per
        # markdown spec) must not inflate col-count. Pre-fix: cells like
        # 'foo \\| bar' would count the escaped pipe as a separator,
        # producing false-positive col-mismatch warnings on consistent tables.
        body = (
            "| col1 | col2 |\n"
            "|------|------|\n"
            "| a \\| escaped | b |\n"
            "| c    | d \\| escaped |\n"
        )
        with TemporaryDirectory() as td:
            p = Path(td) / "escape_pipe.md"
            _write(p, body)
            r = doc_lint.check_markdown_lint(p)
            self.assertTrue(r.ok)
            self.assertEqual(r.table_mismatches, [],
                             "escape-pipe cells MUST NOT trigger col-mismatch")
            self.assertEqual(
                [w for w in r.warnings if "column-count" in w], [],
                "escape-pipe content must not produce col-count warnings"
            )

    def test_check_markdown_lint_initial_heading_depth_skip_emits_warning(self):
        # S023-T2-α AC3: doc starting with '### X' (no preceding H1/H2)
        # emits warning. Pre-T2-α: silent. Read B locked.
        body = "### Sub-heading first\n\nBody.\n"
        with TemporaryDirectory() as td:
            p = Path(td) / "deep_first.md"
            _write(p, body)
            r = doc_lint.check_markdown_lint(p)
            self.assertTrue(r.ok, "initial-depth gap is warning, not error")
            self.assertTrue(
                any("initial heading depth" in w for w in r.warnings),
                f"expected initial-heading-depth warning; got: {r.warnings}"
            )

    def test_check_markdown_lint_indented_unclosed_fence_emits_error(self):
        # S023-T2-α AC4: 0-3 space-indented fences detected per CommonMark.
        # 3-space-indented unclosed fence => fence_count odd => error.
        body = (
            "Body.\n"
            "   ```\n"  # 3-space indent; unclosed
            "open forever\n"
        )
        with TemporaryDirectory() as td:
            p = Path(td) / "indent_fence.md"
            _write(p, body)
            r = doc_lint.check_markdown_lint(p)
            self.assertFalse(r.ok)
            self.assertEqual(r.fence_count, 1,
                             "3-space-indented fence MUST count toward "
                             "fence_count per CommonMark")
            self.assertTrue(any("unclosed" in e for e in r.errors))


# ===== Composite + perf (>=2, AC2 + AC3) =====

class TestS1Doc(unittest.TestCase):
    def test_s1_doc_aggregates_sub_check_results(self):
        # Sub-check warning preserves ok=True (frontmatter missing required keys).
        no_err_body = (
            "---\n"
            "title: Aggregate Test\n"
            "type: framework\n"
            "---\n"
            "Some prose.\n"
        )
        with TemporaryDirectory() as td:
            root = Path(td)
            p = root / "agg.md"
            _write(p, no_err_body)
            r = doc_lint.s1_doc(p, root)
            self.assertTrue(r.ok)
            self.assertEqual(r.errors, [])
            self.assertGreater(len(r.warnings), 0,
                               "missing required keys MUST surface as warnings")
            self.assertIsNotNone(r.frontmatter)
            self.assertIsNotNone(r.cross_refs)
            self.assertIsNotNone(r.markdown_lint)
            self.assertGreater(r.elapsed_seconds, 0.0)

        # Sub-check error propagates ok=False (dead cross-ref link).
        with TemporaryDirectory() as td:
            root = Path(td)
            p = root / "err.md"
            _write(p, _well_formed_fm() + "Broken [x](missing.md)\n")
            r = doc_lint.s1_doc(p, root)
            self.assertFalse(r.ok,
                             "sub-check error MUST propagate to composite ok=False")
            self.assertGreater(len(r.errors), 0)
            self.assertTrue(any("dead link" in e for e in r.errors))

    def test_s1_doc_runs_well_under_perf_budget_on_largest_lattice_doc(self):
        # S023-T2-α AC5: renamed from test_s1_doc_runs_under_5s_on_largest_lattice_doc.
        # Spec §2.5 budget 5s; assertion threshold 2s preserved (3 orders of
        # magnitude headroom measured in S021-T2; ~2.5ms typical on Windows).
        target = LATTICE_DOCS / "08-STANDUP-RUNBOOK.md"
        if not target.exists():
            self.skipTest("08-STANDUP-RUNBOOK.md not at expected path")
        start = time.perf_counter()
        r = doc_lint.s1_doc(target, REPO_ROOT)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 2.0,
                        f"s1_doc took {elapsed:.3f}s; threshold 2s "
                        f"(spec §2.5 budget 5s)")
        self.assertIsNotNone(r.frontmatter)
        self.assertIsNotNone(r.cross_refs)
        self.assertIsNotNone(r.markdown_lint)


if __name__ == "__main__":
    unittest.main()
