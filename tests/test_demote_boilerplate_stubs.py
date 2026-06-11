"""Tests for _scripts/demote_boilerplate_stubs.py — boilerplate-location migration.

Convention (Operator-RATIFIED 2026-06-11): the 4 protocol pages live once
upstream in wiki.codex; consumers carry stubs. Gate revisions under test
(EMCC.DFDU tasks/delta-force/2026-06-11-boilerplate-stub-build.md):
R1 body-only comparison (frontmatter — incl. cross_link-injected keys and the
materialization date — excluded), R2 structural refusal on the canonical wiki,
R3 stub frontmatter parity, R4 modified copies SKIPped, never clobbered.
"""
import io
import subprocess
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import demote_boilerplate_stubs as dbs

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_TEMPLATES = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_template"

OLD_BODY = (
    "\n# <Project Name> — How to Use This Wiki\n\n"
    "This page explains how the `<Project Name>` wiki is organized.\n"
)
OLD_FRONTMATTER = (
    '---\ntitle: "<Project Name> — How to Use This Wiki"\ntype: guide\n'
    "last_updated: 2026-06-11\n---\n"
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


OLDER_BODY = (
    "\n# <Project Name> — How to Use This Wiki\n\n"
    "An earlier template vintage of this page.\n"
)


def _old_body_fn(name):
    return [OLD_BODY, OLDER_BODY]


class DemoteGuardTests(unittest.TestCase):
    """Hermetic: old-template baseline injected via old_body_fn."""

    PAGE = "00-Start-Here/How-to-Use-This-Wiki.md"

    def _run(self, page_content, **kw):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        wiki = Path(tmp.name) / "git"
        if page_content is not None:
            _write(wiki / self.PAGE, page_content)
        actions = dbs.demote_boilerplate_stubs(
            wiki, REPO_ROOT, "Demo", today=date(2026, 6, 11),
            old_body_fn=_old_body_fn, **kw)
        return wiki, dict((rel, a) for a, rel in actions)

    def test_unmodified_page_demoted_to_stub(self):
        content = OLD_FRONTMATTER.replace("<Project Name>", "Demo") + \
            OLD_BODY.replace("<Project Name>", "Demo")
        wiki, acts = self._run(content)
        self.assertEqual(acts[self.PAGE], "DEMOTE")
        new = (wiki / self.PAGE).read_text(encoding="utf-8")
        self.assertIn("deliberate stub", new)
        self.assertIn("wiki.codex/git/00-Start-Here/How-to-Use-This-Wiki.md", new)
        self.assertIn("Demo", new)
        self.assertIn("2026-06-11", new)
        self.assertNotIn("<Project Name>", new)
        self.assertNotIn("<YYYY-MM-DD>", new)

    def test_injected_frontmatter_tolerated(self):
        # cross_link_topics rewrites frontmatter (topics/tags/related_files);
        # the guard compares the BODY only, so injection must not block demotion.
        content = (
            '---\ntitle: "Demo — How to Use This Wiki"\ntype: guide\n'
            "last_updated: 2026-06-13\ntopics: [a, b]\nrelated_files: [Home.md]\n---\n"
            + OLD_BODY.replace("<Project Name>", "Demo"))
        _, acts = self._run(content)
        self.assertEqual(acts[self.PAGE], "DEMOTE")

    def test_modified_body_skipped_never_clobbered(self):
        content = OLD_FRONTMATTER.replace("<Project Name>", "Demo") + \
            OLD_BODY.replace("<Project Name>", "Demo") + "\nConsumer curation.\n"
        wiki, acts = self._run(content)
        self.assertEqual(acts[self.PAGE], "SKIP-MODIFIED")
        self.assertIn("Consumer curation.",
                      (wiki / self.PAGE).read_text(encoding="utf-8"))

    def test_missing_page_reported_not_created(self):
        wiki, acts = self._run(None)
        self.assertEqual(acts[self.PAGE], "MISSING")
        self.assertFalse((wiki / self.PAGE).exists())

    def test_earlier_template_vintage_demoted(self):
        # R5: a page materialized from an OLDER shipped template version is
        # still unmodified — any-historical-version match demotes.
        content = OLD_FRONTMATTER.replace("<Project Name>", "Demo") + \
            OLDER_BODY.replace("<Project Name>", "Demo")
        _, acts = self._run(content)
        self.assertEqual(acts[self.PAGE], "DEMOTE")

    def test_no_baseline_untouched(self):
        content = OLD_FRONTMATTER + OLD_BODY
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        wiki = Path(tmp.name) / "git"
        _write(wiki / self.PAGE, content)
        actions = dbs.demote_boilerplate_stubs(
            wiki, REPO_ROOT, "Demo", old_body_fn=lambda n: [])
        self.assertEqual(actions[0][0], "NO-BASELINE")
        self.assertEqual((wiki / self.PAGE).read_text(encoding="utf-8"), content)

    def test_dry_run_writes_nothing(self):
        content = OLD_FRONTMATTER.replace("<Project Name>", "Demo") + \
            OLD_BODY.replace("<Project Name>", "Demo")
        wiki, acts = self._run(content, dry_run=True)
        self.assertEqual(acts[self.PAGE], "DEMOTE")
        self.assertEqual((wiki / self.PAGE).read_text(encoding="utf-8"), content)


class StructuralExclusionTests(unittest.TestCase):

    def test_cli_refuses_the_codex_wiki(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Biz.Automation" / "wikisys.codex").mkdir(parents=True)
            (root / "wiki.codex" / "git").mkdir(parents=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = dbs.main([str(REPO_ROOT)], consumer_root=root)
            self.assertEqual(rc, 3)

    def test_cli_refuses_when_root_is_the_library(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Biz.Automation" / "wikisys.demo").mkdir(parents=True)
            (root / "wiki.demo" / "git").mkdir(parents=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = dbs.main([str(root)], consumer_root=root)
            self.assertEqual(rc, 3)


class ShippedStubTemplateTests(unittest.TestCase):
    """Welded to the shipped templates: the 4 protocol templates are stubs with
    a canonical pointer; the 2 project templates remain full pages."""

    def test_protocol_templates_are_stubs_with_canonical_pointer(self):
        for name in dbs.PROTOCOL_TEMPLATES:
            text = (KIT_TEMPLATES / name).read_text(encoding="utf-8")
            self.assertIn("deliberate stub", text, name)
            self.assertIn("wiki.codex/git/", text, name)
            page = dbs.decode_sep(name).as_posix()
            self.assertIn(page, text, name)
            # R3 frontmatter parity with the full templates
            for key in ("title:", "type: guide", "visibility: internal",
                        "status: gap", "last_updated: <YYYY-MM-DD>"):
                self.assertIn(key, text, name)

    def test_project_templates_stay_full_pages(self):
        for name in ("00-Start-Here__SEP__Glossary.md",
                     "00-Start-Here__SEP__Terminology-Rules.md"):
            text = (KIT_TEMPLATES / name).read_text(encoding="utf-8")
            self.assertNotIn("deliberate stub", text, name)

    def test_canonical_pages_exist_and_are_marked(self):
        for rel in ("00-Start-Here/How-to-Use-This-Wiki.md",
                    "04-Contributing/Style-Guide.md",
                    "04-Contributing/Update-Cascade.md",
                    "04-Contributing/File-Routing.md"):
            page = REPO_ROOT / "wiki.codex" / "git" / rel
            self.assertTrue(page.is_file(), rel)
            self.assertIn("Canonical copy.", page.read_text(encoding="utf-8"), rel)


class GitBaselineIntegrationTests(unittest.TestCase):
    """The real git-history baseline (skipped on shallow clones where the
    pre-stub template versions are unreachable, e.g. CI fetch-depth=1)."""

    def test_historical_bodies_include_the_full_template(self):
        bodies = dbs._historical_template_bodies(
            REPO_ROOT, "00-Start-Here__SEP__How-to-Use-This-Wiki.md")
        if len(bodies) < 2:
            self.skipTest("template history unreachable (shallow clone)")
        joined = "\n".join(bodies)
        self.assertIn("This page explains how", joined)


if __name__ == "__main__":
    unittest.main()
