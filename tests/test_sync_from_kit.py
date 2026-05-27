"""Tests for _scripts/sync_from_kit.py — P20 Sync operation."""

import io
import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import sync_from_kit


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_codex_install(root: Path) -> Path:
    """Synthesize a minimal Codex install with all required sources.

    S002 / Codex v1.1: source roots split — modules under
    `<codex>/Biz.Automation/wikisys.library/_*`; spec docs under
    `<codex>/wiki.codex/git/codex/*`. Mirrors sync_from_kit.WIKISYS_REL
    + SPEC_DOCS_REL.
    """
    root.mkdir(parents=True, exist_ok=True)
    wikisys = root / "Biz.Automation" / "wikisys.library"
    specs = root / "wiki.codex" / "git" / "codex"
    _write(wikisys / "_scripts" / "marker.py", "# codex marker\n")
    _write(wikisys / "_scripts" / "_lib" / "shared.py", "# codex shared\n")
    _write(specs / "PROJECT_WIKI_BUILD_SPEC.md", "# Project Wiki Build Spec (codex)\n")
    _write(specs / "INGEST_PROCEDURE.md", "# Ingest Procedure (codex)\n")
    _write(specs / "SEMANTIC_LINT_PROCEDURE.md", "# Semantic Lint Procedure (codex)\n")
    _write(specs / "CODEX_LIBRARIAN.md", "# Codex Librarian (codex)\n")
    _write(wikisys / "_config" / "example.yaml", "rules: []  # codex default\n")
    _write(wikisys / "_template" / "example.md", "<!-- codex template -->\n")
    return root


def _make_wiki(root: Path, *, git_init: bool = True, clean: bool = True) -> Path:
    """Synthesize a minimal consuming wiki; optionally git-init + commit."""
    root.mkdir(parents=True, exist_ok=True)
    _write(root / "Home.md", "# Home (wiki customized)\n")
    _write(root / "01-Domain" / "Foo.md", "# Foo (wiki customized)\n")
    _write(root / "_context" / "CLAUDE_CONTEXT_RULES.md", "# customized\n")
    _write(root / "README.md", "# Wiki README\n")
    if git_init:
        subprocess.run(["git", "init", "-q"], cwd=str(root), check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(root), check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=str(root), check=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=str(root), check=True)
        if clean:
            subprocess.run(["git", "add", "."], cwd=str(root), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "init", "--no-verify"],
                cwd=str(root),
                check=True,
            )
    return root


def _run_sync(codex: Path, wiki: Path, *flags) -> tuple:
    """Invoke sync_from_kit._main against fixture pair; return (rc, stdout, stderr)."""
    argv = [str(codex)] + list(flags)
    stdout = io.StringIO()
    stderr = io.StringIO()
    rc = sync_from_kit._main(argv=argv, wiki_root=wiki, stdout=stdout, stderr=stderr)
    return rc, stdout.getvalue(), stderr.getvalue()


class TestOverwriteClass(unittest.TestCase):

    def test_scripts_dir_replaced_byte_equiv(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            wiki = _make_wiki(tmp_path / "wiki")
            _write(wiki / "_scripts" / "stale.py", "# wiki-side stale content\n")
            subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "add stale", "--no-verify"],
                cwd=str(wiki),
                check=True,
            )
            rc, _stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            self.assertEqual(
                (wiki / "_scripts" / "marker.py").read_text(encoding="utf-8"),
                "# codex marker\n",
            )
            self.assertEqual(
                (wiki / "_scripts" / "_lib" / "shared.py").read_text(encoding="utf-8"),
                "# codex shared\n",
            )
            self.assertFalse((wiki / "_scripts" / "stale.py").exists())

    def test_procedure_files_overwritten_verbatim(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            wiki = _make_wiki(tmp_path / "wiki")
            _write(wiki / "_context" / "INGEST_PROCEDURE.md", "# stale ingest\n")
            _write(wiki / "_context" / "SEMANTIC_LINT_PROCEDURE.md", "# stale lint\n")
            subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "add stale", "--no-verify"],
                cwd=str(wiki),
                check=True,
            )
            rc, _stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            self.assertEqual(
                (wiki / "_context" / "INGEST_PROCEDURE.md").read_text(encoding="utf-8"),
                "# Ingest Procedure (codex)\n",
            )
            self.assertEqual(
                (wiki / "_context" / "SEMANTIC_LINT_PROCEDURE.md").read_text(encoding="utf-8"),
                "# Semantic Lint Procedure (codex)\n",
            )


class TestMergeNewOnly(unittest.TestCase):

    def test_existing_config_preserved(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            wiki = _make_wiki(tmp_path / "wiki")
            _write(wiki / "_config" / "example.yaml", "rules: [{name: custom}]  # wiki customization\n")
            subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "customize", "--no-verify"],
                cwd=str(wiki),
                check=True,
            )
            rc, stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            self.assertEqual(
                (wiki / "_config" / "example.yaml").read_text(encoding="utf-8"),
                "rules: [{name: custom}]  # wiki customization\n",
            )
            self.assertIn("[SKIP] _config/example.yaml", stdout)

    def test_new_template_added(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            wiki = _make_wiki(tmp_path / "wiki")
            self.assertFalse((wiki / "_template" / "example.md").exists())
            rc, stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            self.assertEqual(
                (wiki / "_template" / "example.md").read_text(encoding="utf-8"),
                "<!-- codex template -->\n",
            )
            self.assertIn("[MERGE-NEW] _template/example.md", stdout)


class TestNeverTouched(unittest.TestCase):

    def test_content_folder_unmodified(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            wiki = _make_wiki(tmp_path / "wiki")
            home_path = wiki / "Home.md"
            foo_path = wiki / "01-Domain" / "Foo.md"
            claude_ctx = wiki / "_context" / "CLAUDE_CONTEXT_RULES.md"
            pre_home = home_path.read_bytes()
            pre_foo = foo_path.read_bytes()
            pre_claude = claude_ctx.read_bytes()
            rc, _stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            self.assertEqual(home_path.read_bytes(), pre_home)
            self.assertEqual(foo_path.read_bytes(), pre_foo)
            self.assertEqual(claude_ctx.read_bytes(), pre_claude)


class TestGuard(unittest.TestCase):

    def test_uncommitted_changes_refused(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            wiki = _make_wiki(tmp_path / "wiki")
            _write(wiki / "Home.md", "# Home (uncommitted edit)\n")
            rc, _stdout, stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 2)
            self.assertIn("uncommitted", stderr)
            self.assertIn("--force", stderr)

    def test_force_overrides_guard(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            wiki = _make_wiki(tmp_path / "wiki")
            _write(wiki / "Home.md", "# Home (uncommitted edit)\n")
            rc, _stdout, stderr = _run_sync(codex, wiki, "--force")
            self.assertEqual(rc, 0)
            self.assertIn("WARN", stderr)


class TestDryRun(unittest.TestCase):

    def test_dry_run_no_writes_planned_actions_surfaced(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            wiki = _make_wiki(tmp_path / "wiki")
            pre_home = (wiki / "Home.md").read_bytes()
            self.assertFalse((wiki / "_template" / "example.md").exists())
            self.assertFalse((wiki / "04-Contributing" / "PROJECT_WIKI_BUILD_SPEC.md").exists())
            rc, stdout, _stderr = _run_sync(codex, wiki, "--dry-run")
            self.assertEqual(rc, 0)
            self.assertIn("[OVERWRITE] _scripts/", stdout)
            self.assertIn("[OVERWRITE] 04-Contributing/PROJECT_WIKI_BUILD_SPEC.md", stdout)
            self.assertIn("[OVERWRITE] _context/INGEST_PROCEDURE.md", stdout)
            self.assertIn("[MERGE-NEW] _template/example.md", stdout)
            self.assertEqual((wiki / "Home.md").read_bytes(), pre_home)
            self.assertFalse((wiki / "_template" / "example.md").exists())
            self.assertFalse((wiki / "04-Contributing" / "PROJECT_WIKI_BUILD_SPEC.md").exists())


class TestSourceMissing(unittest.TestCase):

    def test_missing_source_refused(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            (codex / "Biz.Automation" / "wikisys.library" / "_scripts" / "marker.py").unlink()
            (codex / "Biz.Automation" / "wikisys.library" / "_scripts" / "_lib" / "shared.py").unlink()
            (codex / "Biz.Automation" / "wikisys.library" / "_scripts" / "_lib").rmdir()
            (codex / "Biz.Automation" / "wikisys.library" / "_scripts").rmdir()
            wiki = _make_wiki(tmp_path / "wiki")
            rc, _stdout, stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 3)
            self.assertIn("_scripts/", stderr)
            self.assertIn("missing", stderr)


class TestCrossLinkArtifactSync(unittest.TestCase):
    """T-XL-8 cross-link artifact sync precedence verification per spec v1.3 §4.2.

    Cross-link scripts (T-XL-2..T-XL-5) → OVERWRITE via _scripts/ dir glob.
    Cross-link templates (T-XL-7) → MERGE-NEW-ONLY via _template/ dir iter.
    """

    def test_cross_link_scripts_overwrite_via_scripts_dir(self):
        """4 NEW cross-link scripts land via _scripts/ dir OVERWRITE."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            # Synthesize 4 NEW cross-link scripts in codex install
            _write(codex / "Biz.Automation" / "wikisys.library" / "_scripts" / "build_topic_index.py", "# codex T-XL-3\n")
            _write(codex / "Biz.Automation" / "wikisys.library" / "_scripts" / "cross_link_topics.py", "# codex T-XL-4\n")
            _write(codex / "Biz.Automation" / "wikisys.library" / "_scripts" / "validate_topic_registry.py", "# codex T-XL-5\n")
            wiki = _make_wiki(tmp_path / "wiki")
            # Wiki has stale customized versions
            _write(wiki / "_scripts" / "build_topic_index.py", "# wiki stale T-XL-3\n")
            _write(wiki / "_scripts" / "cross_link_topics.py", "# wiki stale T-XL-4\n")
            _write(wiki / "_scripts" / "validate_topic_registry.py", "# wiki stale T-XL-5\n")
            subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "add stale cross-link", "--no-verify"],
                cwd=str(wiki),
                check=True,
            )
            rc, _stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            # All 3 stale scripts REPLACED by codex source
            self.assertEqual(
                (wiki / "_scripts" / "build_topic_index.py").read_text(encoding="utf-8"),
                "# codex T-XL-3\n",
            )
            self.assertEqual(
                (wiki / "_scripts" / "cross_link_topics.py").read_text(encoding="utf-8"),
                "# codex T-XL-4\n",
            )
            self.assertEqual(
                (wiki / "_scripts" / "validate_topic_registry.py").read_text(encoding="utf-8"),
                "# codex T-XL-5\n",
            )

    def test_cross_link_lib_topics_overwrite_via_scripts_lib_subdir(self):
        """T-XL-2 _lib/topics.py lands via _scripts/_lib/ subdir OVERWRITE."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            _write(codex / "Biz.Automation" / "wikisys.library" / "_scripts" / "_lib" / "topics.py", "# codex T-XL-2 topics\n")
            wiki = _make_wiki(tmp_path / "wiki")
            _write(wiki / "_scripts" / "_lib" / "topics.py", "# wiki stale topics\n")
            subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "add stale lib", "--no-verify"],
                cwd=str(wiki),
                check=True,
            )
            rc, _stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            self.assertEqual(
                (wiki / "_scripts" / "_lib" / "topics.py").read_text(encoding="utf-8"),
                "# codex T-XL-2 topics\n",
            )

    def test_cross_link_templates_merge_new_when_absent(self):
        """T-XL-7 2 NEW templates land via _template/ MERGE-NEW when absent in wiki."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            _write(
                codex / "Biz.Automation" / "wikisys.library" / "_template" / "_canon__SEP__topics.yaml",
                "topics: []  # codex default\n",
            )
            _write(
                codex / "Biz.Automation" / "wikisys.library" / "_template" / "_config__SEP__cross_link.yaml",
                "tfidf:\n  min_similarity: 0.35  # codex default\n",
            )
            wiki = _make_wiki(tmp_path / "wiki")
            # Wiki has NEITHER template
            self.assertFalse((wiki / "_template" / "_canon__SEP__topics.yaml").exists())
            self.assertFalse((wiki / "_template" / "_config__SEP__cross_link.yaml").exists())
            rc, stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            # Both templates ADDED at wiki side
            self.assertEqual(
                (wiki / "_template" / "_canon__SEP__topics.yaml").read_text(
                    encoding="utf-8"
                ),
                "topics: []  # codex default\n",
            )
            self.assertEqual(
                (wiki / "_template" / "_config__SEP__cross_link.yaml").read_text(
                    encoding="utf-8"
                ),
                "tfidf:\n  min_similarity: 0.35  # codex default\n",
            )
            self.assertIn("[MERGE-NEW] _template/_canon__SEP__topics.yaml", stdout)
            self.assertIn("[MERGE-NEW] _template/_config__SEP__cross_link.yaml", stdout)

    def test_cross_link_templates_preserve_existing_when_present(self):
        """T-XL-7 templates already in wiki PRESERVED on sync (project customization)."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            codex = _make_codex_install(tmp_path / "codex")
            _write(
                codex / "Biz.Automation" / "wikisys.library" / "_template" / "_canon__SEP__topics.yaml",
                "topics: []  # codex default\n",
            )
            wiki = _make_wiki(tmp_path / "wiki")
            # Wiki has CUSTOMIZED topics.yaml
            _write(
                wiki / "_template" / "_canon__SEP__topics.yaml",
                "topics: [{name: customized}]  # wiki customization\n",
            )
            subprocess.run(["git", "add", "."], cwd=str(wiki), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "customize topics", "--no-verify"],
                cwd=str(wiki),
                check=True,
            )
            rc, stdout, _stderr = _run_sync(codex, wiki)
            self.assertEqual(rc, 0)
            # Customized topics.yaml PRESERVED
            self.assertEqual(
                (wiki / "_template" / "_canon__SEP__topics.yaml").read_text(
                    encoding="utf-8"
                ),
                "topics: [{name: customized}]  # wiki customization\n",
            )
            self.assertIn("[SKIP] _template/_canon__SEP__topics.yaml", stdout)


if __name__ == "__main__":
    unittest.main()
