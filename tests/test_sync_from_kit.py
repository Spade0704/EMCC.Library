"""Tests for _scripts/sync_from_kit.py — P20 Sync operation (v1.1 contract).

S004 / MI-16 closure: sync_from_kit was rewritten for v1.1 consumer
layout. Tests synthesize a v1.1-shape consumer fixture with
`Biz.Automation/wikisys.<name>/` + `wiki.<name>/git/` and verify
target paths land at the canonical v1.1 locations.
"""

import io
import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import sync_from_kit


CONSUMER_NAME = "test_consumer"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_library_install(root: Path) -> Path:
    """Synthesize a minimal EMCC.Library install with all required sources.

    Mirrors sync_from_kit.WIKISYS_REL + SPEC_DOCS_REL (v1.1 source paths).
    """
    root.mkdir(parents=True, exist_ok=True)
    wikisys = root / "Biz.Automation" / "wikisys.library"
    specs = root / "wiki.codex" / "git" / "codex"
    _write(wikisys / "_scripts" / "marker.py", "# library marker\n")
    _write(wikisys / "_scripts" / "_lib" / "shared.py", "# library shared\n")
    _write(specs / "PROJECT_WIKI_BUILD_SPEC.md", "# Project Wiki Build Spec (library)\n")
    _write(specs / "INGEST_PROCEDURE.md", "# Ingest Procedure (library)\n")
    _write(specs / "SEMANTIC_LINT_PROCEDURE.md", "# Semantic Lint Procedure (library)\n")
    _write(specs / "CODEX_LIBRARIAN.md", "# Codex Librarian (library)\n")
    _write(wikisys / "_config" / "example.yaml", "rules: []  # library default\n")
    _write(wikisys / "_template" / "example.md", "<!-- library template -->\n")
    return root


def _make_consumer(root: Path, *, name: str = CONSUMER_NAME, git_init: bool = True, clean: bool = True) -> Path:
    """Synthesize a minimal v1.1-shape consumer project.

    Creates `Biz.Automation/wikisys.<name>/` + `wiki.<name>/git/` so
    consumer-name auto-discovery succeeds.
    """
    root.mkdir(parents=True, exist_ok=True)
    wikisys = root / "Biz.Automation" / ("wikisys." + name)
    wiki_git = root / ("wiki." + name) / "git"
    wikisys.mkdir(parents=True, exist_ok=True)
    wiki_git.mkdir(parents=True, exist_ok=True)
    _write(wiki_git / "Home.md", "# Home (consumer customized)\n")
    _write(wiki_git / "01-Authorities" / "Foo.md", "# Foo (consumer customized)\n")
    _write(wikisys / "_context" / "CLAUDE_CONTEXT_RULES.md", "# consumer customized\n")
    _write(root / "README.md", "# Consumer README\n")
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


def _run_sync(library: Path, consumer: Path, *flags) -> tuple:
    """Invoke sync_from_kit._main against fixture pair; return (rc, stdout, stderr)."""
    argv = [str(library)] + list(flags)
    stdout = io.StringIO()
    stderr = io.StringIO()
    rc = sync_from_kit._main(argv=argv, consumer_root=consumer, stdout=stdout, stderr=stderr)
    return rc, stdout.getvalue(), stderr.getvalue()


def _wikisys_target(consumer: Path, *parts) -> Path:
    return consumer / "Biz.Automation" / ("wikisys." + CONSUMER_NAME) / Path(*parts)


def _wiki_codex_target(consumer: Path, *parts) -> Path:
    return consumer / ("wiki." + CONSUMER_NAME) / "git" / "codex" / Path(*parts)


class TestOverwriteClass(unittest.TestCase):

    def test_scripts_dir_replaced_byte_equiv(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            _write(_wikisys_target(consumer, "_scripts", "stale.py"), "# consumer-side stale content\n")
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "add stale", "--no-verify"],
                cwd=str(consumer),
                check=True,
            )
            rc, _stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wikisys_target(consumer, "_scripts", "marker.py").read_text(encoding="utf-8"),
                "# library marker\n",
            )
            self.assertEqual(
                _wikisys_target(consumer, "_scripts", "_lib", "shared.py").read_text(encoding="utf-8"),
                "# library shared\n",
            )
            self.assertFalse(_wikisys_target(consumer, "_scripts", "stale.py").exists())

    def test_procedure_files_overwritten_verbatim(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            _write(_wikisys_target(consumer, "_context", "INGEST_PROCEDURE.md"), "# stale ingest\n")
            _write(_wikisys_target(consumer, "_context", "SEMANTIC_LINT_PROCEDURE.md"), "# stale lint\n")
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "add stale", "--no-verify"],
                cwd=str(consumer),
                check=True,
            )
            rc, _stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wikisys_target(consumer, "_context", "INGEST_PROCEDURE.md").read_text(encoding="utf-8"),
                "# Ingest Procedure (library)\n",
            )
            self.assertEqual(
                _wikisys_target(consumer, "_context", "SEMANTIC_LINT_PROCEDURE.md").read_text(encoding="utf-8"),
                "# Semantic Lint Procedure (library)\n",
            )

    def test_project_wiki_build_spec_lands_at_wiki_codex_path(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            rc, _stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wiki_codex_target(consumer, "PROJECT_WIKI_BUILD_SPEC.md").read_text(encoding="utf-8"),
                "# Project Wiki Build Spec (library)\n",
            )


class TestMergeNewOnly(unittest.TestCase):

    def test_existing_config_preserved(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            _write(_wikisys_target(consumer, "_config", "example.yaml"), "rules: [{name: custom}]  # consumer customization\n")
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "customize", "--no-verify"],
                cwd=str(consumer),
                check=True,
            )
            rc, stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wikisys_target(consumer, "_config", "example.yaml").read_text(encoding="utf-8"),
                "rules: [{name: custom}]  # consumer customization\n",
            )
            self.assertIn("[SKIP]", stdout)
            self.assertIn("_config/example.yaml", stdout)

    def test_new_template_added(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            self.assertFalse(_wikisys_target(consumer, "_template", "example.md").exists())
            rc, stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wikisys_target(consumer, "_template", "example.md").read_text(encoding="utf-8"),
                "<!-- library template -->\n",
            )
            self.assertIn("[MERGE-NEW]", stdout)
            self.assertIn("_template/example.md", stdout)


class TestNeverTouched(unittest.TestCase):

    def test_content_folder_unmodified(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            home_path = consumer / ("wiki." + CONSUMER_NAME) / "git" / "Home.md"
            foo_path = consumer / ("wiki." + CONSUMER_NAME) / "git" / "01-Authorities" / "Foo.md"
            claude_ctx = _wikisys_target(consumer, "_context", "CLAUDE_CONTEXT_RULES.md")
            pre_home = home_path.read_bytes()
            pre_foo = foo_path.read_bytes()
            pre_claude = claude_ctx.read_bytes()
            rc, _stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(home_path.read_bytes(), pre_home)
            self.assertEqual(foo_path.read_bytes(), pre_foo)
            self.assertEqual(claude_ctx.read_bytes(), pre_claude)


class TestGuard(unittest.TestCase):

    def test_uncommitted_changes_refused(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            _write(consumer / ("wiki." + CONSUMER_NAME) / "git" / "Home.md", "# Home (uncommitted edit)\n")
            rc, _stdout, stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 2)
            self.assertIn("uncommitted", stderr)
            self.assertIn("--force", stderr)

    def test_force_overrides_guard(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            _write(consumer / ("wiki." + CONSUMER_NAME) / "git" / "Home.md", "# Home (uncommitted edit)\n")
            rc, _stdout, stderr = _run_sync(library, consumer, "--force")
            self.assertEqual(rc, 0)
            self.assertIn("WARN", stderr)


class TestDryRun(unittest.TestCase):

    def test_dry_run_no_writes_planned_actions_surfaced(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer")
            pre_home = (consumer / ("wiki." + CONSUMER_NAME) / "git" / "Home.md").read_bytes()
            self.assertFalse(_wikisys_target(consumer, "_template", "example.md").exists())
            self.assertFalse(_wiki_codex_target(consumer, "PROJECT_WIKI_BUILD_SPEC.md").exists())
            rc, stdout, _stderr = _run_sync(library, consumer, "--dry-run")
            self.assertEqual(rc, 0)
            self.assertIn("[OVERWRITE] Biz.Automation/wikisys.{}/_scripts/".format(CONSUMER_NAME), stdout)
            self.assertIn("[OVERWRITE] wiki.{}/git/codex/PROJECT_WIKI_BUILD_SPEC.md".format(CONSUMER_NAME), stdout)
            self.assertIn("[OVERWRITE] Biz.Automation/wikisys.{}/_context/INGEST_PROCEDURE.md".format(CONSUMER_NAME), stdout)
            self.assertIn("[MERGE-NEW] Biz.Automation/wikisys.{}/_template/example.md".format(CONSUMER_NAME), stdout)
            self.assertEqual((consumer / ("wiki." + CONSUMER_NAME) / "git" / "Home.md").read_bytes(), pre_home)
            self.assertFalse(_wikisys_target(consumer, "_template", "example.md").exists())
            self.assertFalse(_wiki_codex_target(consumer, "PROJECT_WIKI_BUILD_SPEC.md").exists())


class TestSourceMissing(unittest.TestCase):

    def test_missing_source_refused(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            (library / "Biz.Automation" / "wikisys.library" / "_scripts" / "marker.py").unlink()
            (library / "Biz.Automation" / "wikisys.library" / "_scripts" / "_lib" / "shared.py").unlink()
            (library / "Biz.Automation" / "wikisys.library" / "_scripts" / "_lib").rmdir()
            (library / "Biz.Automation" / "wikisys.library" / "_scripts").rmdir()
            consumer = _make_consumer(tmp_path / "consumer")
            rc, _stdout, stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 3)
            self.assertIn("_scripts/", stderr)
            self.assertIn("missing", stderr)


class TestConsumerDiscovery(unittest.TestCase):
    """v1.1: auto-discover consumer name via Biz.Automation/wikisys.<name>/ glob."""

    def test_zero_matches_refused(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = tmp_path / "consumer"
            (consumer / "Biz.Automation").mkdir(parents=True)
            # No wikisys.<name>/ subdir at all
            subprocess.run(["git", "init", "-q"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=str(consumer), check=True)
            _write(consumer / "README.md", "# Empty\n")
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(["git", "commit", "-q", "-m", "init", "--no-verify"], cwd=str(consumer), check=True)
            rc, _stdout, stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 4)
            self.assertIn("could not discover", stderr)

    def test_multiple_matches_refused_without_override(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer", name="alpha", git_init=False)
            # Add a second matching pair
            (consumer / "Biz.Automation" / "wikisys.beta").mkdir(parents=True)
            (consumer / "wiki.beta" / "git").mkdir(parents=True)
            subprocess.run(["git", "init", "-q"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=str(consumer), check=True)
            _write(consumer / "wiki.beta" / "git" / ".gitkeep", "")
            _write(consumer / "Biz.Automation" / "wikisys.beta" / ".gitkeep", "")
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(["git", "commit", "-q", "-m", "init", "--no-verify"], cwd=str(consumer), check=True)
            rc, _stdout, stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 4)
            self.assertIn("ambiguous", stderr)

    def test_consumer_name_override_resolves_ambiguity(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            consumer = _make_consumer(tmp_path / "consumer", name="alpha", git_init=False)
            (consumer / "Biz.Automation" / "wikisys.beta").mkdir(parents=True)
            (consumer / "wiki.beta" / "git").mkdir(parents=True)
            subprocess.run(["git", "init", "-q"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=str(consumer), check=True)
            subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=str(consumer), check=True)
            _write(consumer / "wiki.beta" / "git" / ".gitkeep", "")
            _write(consumer / "Biz.Automation" / "wikisys.beta" / ".gitkeep", "")
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(["git", "commit", "-q", "-m", "init", "--no-verify"], cwd=str(consumer), check=True)
            rc, _stdout, _stderr = _run_sync(library, consumer, "--consumer-name", "alpha")
            self.assertEqual(rc, 0)
            self.assertEqual(
                (consumer / "Biz.Automation" / "wikisys.alpha" / "_scripts" / "marker.py").read_text(encoding="utf-8"),
                "# library marker\n",
            )


class TestCrossLinkArtifactSync(unittest.TestCase):
    """T-XL-8 cross-link artifact sync precedence verification.

    Cross-link scripts -> OVERWRITE via _scripts/ dir glob.
    Cross-link templates -> MERGE-NEW-ONLY via _template/ dir iter.
    """

    def test_cross_link_scripts_overwrite_via_scripts_dir(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            _write(library / "Biz.Automation" / "wikisys.library" / "_scripts" / "build_topic_index.py", "# library T-XL-3\n")
            _write(library / "Biz.Automation" / "wikisys.library" / "_scripts" / "cross_link_topics.py", "# library T-XL-4\n")
            _write(library / "Biz.Automation" / "wikisys.library" / "_scripts" / "validate_topic_registry.py", "# library T-XL-5\n")
            consumer = _make_consumer(tmp_path / "consumer")
            _write(_wikisys_target(consumer, "_scripts", "build_topic_index.py"), "# consumer stale T-XL-3\n")
            _write(_wikisys_target(consumer, "_scripts", "cross_link_topics.py"), "# consumer stale T-XL-4\n")
            _write(_wikisys_target(consumer, "_scripts", "validate_topic_registry.py"), "# consumer stale T-XL-5\n")
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "add stale cross-link", "--no-verify"],
                cwd=str(consumer),
                check=True,
            )
            rc, _stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wikisys_target(consumer, "_scripts", "build_topic_index.py").read_text(encoding="utf-8"),
                "# library T-XL-3\n",
            )
            self.assertEqual(
                _wikisys_target(consumer, "_scripts", "cross_link_topics.py").read_text(encoding="utf-8"),
                "# library T-XL-4\n",
            )
            self.assertEqual(
                _wikisys_target(consumer, "_scripts", "validate_topic_registry.py").read_text(encoding="utf-8"),
                "# library T-XL-5\n",
            )

    def test_cross_link_lib_topics_overwrite_via_scripts_lib_subdir(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            _write(library / "Biz.Automation" / "wikisys.library" / "_scripts" / "_lib" / "topics.py", "# library T-XL-2 topics\n")
            consumer = _make_consumer(tmp_path / "consumer")
            _write(_wikisys_target(consumer, "_scripts", "_lib", "topics.py"), "# consumer stale topics\n")
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "add stale lib", "--no-verify"],
                cwd=str(consumer),
                check=True,
            )
            rc, _stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wikisys_target(consumer, "_scripts", "_lib", "topics.py").read_text(encoding="utf-8"),
                "# library T-XL-2 topics\n",
            )

    def test_cross_link_templates_merge_new_when_absent(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            _write(
                library / "Biz.Automation" / "wikisys.library" / "_template" / "_canon__SEP__topics.yaml",
                "topics: []  # library default\n",
            )
            _write(
                library / "Biz.Automation" / "wikisys.library" / "_template" / "_config__SEP__cross_link.yaml",
                "tfidf:\n  min_similarity: 0.35  # library default\n",
            )
            consumer = _make_consumer(tmp_path / "consumer")
            self.assertFalse(_wikisys_target(consumer, "_template", "_canon__SEP__topics.yaml").exists())
            self.assertFalse(_wikisys_target(consumer, "_template", "_config__SEP__cross_link.yaml").exists())
            rc, stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wikisys_target(consumer, "_template", "_canon__SEP__topics.yaml").read_text(encoding="utf-8"),
                "topics: []  # library default\n",
            )
            self.assertEqual(
                _wikisys_target(consumer, "_template", "_config__SEP__cross_link.yaml").read_text(encoding="utf-8"),
                "tfidf:\n  min_similarity: 0.35  # library default\n",
            )
            self.assertIn("[MERGE-NEW]", stdout)
            self.assertIn("_template/_canon__SEP__topics.yaml", stdout)
            self.assertIn("_template/_config__SEP__cross_link.yaml", stdout)

    def test_cross_link_templates_preserve_existing_when_present(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = _make_library_install(tmp_path / "library")
            _write(
                library / "Biz.Automation" / "wikisys.library" / "_template" / "_canon__SEP__topics.yaml",
                "topics: []  # library default\n",
            )
            consumer = _make_consumer(tmp_path / "consumer")
            _write(
                _wikisys_target(consumer, "_template", "_canon__SEP__topics.yaml"),
                "topics: [{name: customized}]  # consumer customization\n",
            )
            subprocess.run(["git", "add", "."], cwd=str(consumer), check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "customize topics", "--no-verify"],
                cwd=str(consumer),
                check=True,
            )
            rc, stdout, _stderr = _run_sync(library, consumer)
            self.assertEqual(rc, 0)
            self.assertEqual(
                _wikisys_target(consumer, "_template", "_canon__SEP__topics.yaml").read_text(encoding="utf-8"),
                "topics: [{name: customized}]  # consumer customization\n",
            )
            self.assertIn("[SKIP]", stdout)
            self.assertIn("_template/_canon__SEP__topics.yaml", stdout)


if __name__ == "__main__":
    unittest.main()
