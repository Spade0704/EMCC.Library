"""Tests for bootstrap.py v1.1 canonical-output rewrite (S002 / B5b).

Per CODEX_BUILD_SPEC_v1_3.md + tasks/plans/portfolio-folder-structure-spec.md
section (c). v1.1 bootstrap is SCAFFOLD-ONLY (no script copy, no template
substitution); emits the canonical portfolio frame per spec (c):

    <projectname>/
    ├── 0-Inbox/.gitkeep
    ├── Biz.Automation/
    │   ├── wikisys.<name>/{_scripts,_template,_config,_canon}/.gitkeep
    │   └── .gitkeep
    ├── wiki.<name>/{local,git/raw,git/ideas}/.gitkeep
    ├── tasks/{todo,sessions,lessons,archive}.md
    ├── assets/{logos,brand,photos,videos,designs,generated}/.gitkeep
    ├── Index.md, CLAUDE.md, Cheatsheet.md, .gitignore

Modes covered: --full (default), --minimal, --code, --website.
Plus: idempotency (refuse-non-empty + --yes override), refuse-outside-cwd,
--dry-run no-writes.

DEPRECATED v1.0 tests (test_bootstrap, test_t1_p52, test_t2_p53,
test_t3_p54, test_phase6_full_chain_e2e) retired as MI-16; see
MIGRATION-ISSUES.md.
"""

import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import bootstrap  # noqa: E402


def _run_bootstrap(target_cwd: Path, projectname: str, mode: str = "full",
                   yes: bool = False, dry_run: bool = False) -> int:
    """Invoke bootstrap.bootstrap() with cwd_override (tests use tmp dirs)."""
    return bootstrap.bootstrap(
        projectname,
        mode=mode,
        dry_run=dry_run,
        yes=yes,
        cwd_override=target_cwd,
    )


class TestCanonicalFullTree(unittest.TestCase):
    """Spec (c) canonical full tree per `bootstrap.py <projectname> --full`."""

    def test_full_emits_all_canonical_top_level_entries(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            rc = _run_bootstrap(cwd, "mentor", mode="full")
            self.assertEqual(rc, 0)
            target = cwd / "mentor"
            expected_top = {
                "0-Inbox", "Biz.Automation", "wiki.mentor", "tasks",
                "assets", "Index.md", "CLAUDE.md", "Cheatsheet.md",
                ".gitignore",
            }
            actual_top = set(p.name for p in target.iterdir())
            self.assertTrue(expected_top.issubset(actual_top),
                            "missing top-level entries: {}".format(expected_top - actual_top))

    def test_full_emits_wikisys_underscore_folders(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            wikisys = cwd / "mentor" / "Biz.Automation" / "wikisys.mentor"
            for sub in ("_scripts", "_template", "_config", "_canon"):
                self.assertTrue(
                    (wikisys / sub / ".gitkeep").is_file(),
                    "missing {}/.gitkeep".format(sub),
                )

    def test_full_emits_wiki_git_local_split(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            wiki = cwd / "mentor" / "wiki.mentor"
            self.assertTrue((wiki / "local" / ".gitkeep").is_file())
            self.assertTrue((wiki / "git" / "raw" / ".gitkeep").is_file())
            self.assertTrue((wiki / "git" / "ideas" / ".gitkeep").is_file())

    def test_full_emits_task_stubs_lowercase_four(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            tasks = cwd / "mentor" / "tasks"
            for fname in ("todo.md", "sessions.md", "lessons.md", "archive.md"):
                self.assertTrue((tasks / fname).is_file(),
                                "missing tasks/{}".format(fname))
                content = (tasks / fname).read_text(encoding="utf-8")
                self.assertGreater(len(content), 0)

    def test_full_emits_assets_six_subfolders(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            assets = cwd / "mentor" / "assets"
            for sub in ("logos", "brand", "photos", "videos", "designs", "generated"):
                self.assertTrue(
                    (assets / sub / ".gitkeep").is_file(),
                    "missing assets/{}/.gitkeep".format(sub),
                )

    def test_full_root_stub_files_have_projectname_interpolated(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            target = cwd / "mentor"
            claude_md = (target / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("mentor", claude_md)
            self.assertIn("wiki.mentor/local", claude_md)
            self.assertIn("wiki.mentor/git", claude_md)
            index_md = (target / "Index.md").read_text(encoding="utf-8")
            self.assertIn("wikisys.mentor", index_md)
            cheat = (target / "Cheatsheet.md").read_text(encoding="utf-8")
            self.assertIn("mentor", cheat)

    def test_full_emits_reorganization_instructions_stub(self):
        """v1.1 post-2026-05-28: bootstrap emits a per-project reorg manifest stub."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            target = cwd / "mentor"
            reorg = target / "reorganization-instructions.mentor.md"
            self.assertTrue(reorg.is_file(), "missing reorganization-instructions.mentor.md")
            content = reorg.read_text(encoding="utf-8")
            # Projectname interpolated in title + scope blurb
            self.assertIn("reorganization-instructions.mentor.md", content)
            self.assertIn("mentor", content)
            # Points to master in EMCC.Library
            self.assertIn("EMCC.Library/REORGANIZATION-INSTRUCTIONS.md", content)
            # Has the move-table scaffold
            self.assertIn("Old path", content)
            self.assertIn("New path", content)
            self.assertIn("Pattern", content)

    def test_full_gitignore_excludes_wiki_local(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            gi = (cwd / "mentor" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("wiki.*/local/", gi)


class TestCanonicalMinimalTree(unittest.TestCase):
    """--minimal emits thin braindump scaffold per spec (c)."""

    def test_minimal_omits_biz_automation_and_assets(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "thin", mode="minimal")
            target = cwd / "thin"
            self.assertFalse((target / "Biz.Automation").exists())
            self.assertFalse((target / "assets").exists())
            self.assertFalse((target / "Cheatsheet.md").exists())
            self.assertFalse(
                (target / "reorganization-instructions.thin.md").exists(),
                "minimal mode should omit per-project reorg manifest",
            )

    def test_minimal_emits_required_core(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "thin", mode="minimal")
            target = cwd / "thin"
            self.assertTrue((target / "0-Inbox").is_dir())
            self.assertTrue((target / "wiki.thin" / "local").is_dir())
            self.assertTrue((target / "wiki.thin" / "git").is_dir())
            self.assertTrue((target / "tasks" / "todo.md").is_file())
            self.assertTrue((target / "CLAUDE.md").is_file())
            self.assertTrue((target / "Index.md").is_file())
            self.assertTrue((target / ".gitignore").is_file())


class TestCanonicalCodeMode(unittest.TestCase):
    """--code emits --full + code-aware .gitignore.

    No `<product-code-root>/.gitkeep` is emitted: the spec placeholder
    `<product-code-root>` contains Win32-illegal chars; operators name +
    create the actual code folder themselves (Flutter `lib/`, Python
    `src/`, etc.). --code's contribution is the .gitignore additions.
    """

    def test_code_gitignore_includes_python_node_patterns(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "myproj", mode="code")
            gi = (cwd / "myproj" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("node_modules/", gi)
            self.assertIn("__pycache__/", gi)
            self.assertIn("build/", gi)

    def test_code_emits_same_canonical_tree_as_full(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "myproj", mode="code")
            target = cwd / "myproj"
            # Full canonical entries present
            self.assertTrue((target / "Biz.Automation" / "wikisys.myproj").is_dir())
            self.assertTrue((target / "wiki.myproj" / "git" / "raw").is_dir())
            self.assertTrue((target / "assets" / "logos").is_dir())


class TestCanonicalWebsiteMode(unittest.TestCase):
    """--website emits --full + website/ + web-aware .gitignore."""

    def test_website_adds_website_placeholder(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "myweb", mode="website")
            self.assertTrue((cwd / "myweb" / "website" / ".gitkeep").is_file())

    def test_website_gitignore_includes_next_vercel_patterns(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "myweb", mode="website")
            gi = (cwd / "myweb" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".next/", gi)
            self.assertIn(".vercel/", gi)


class TestIdempotencyAndSafety(unittest.TestCase):
    """Spec (c) §Idempotency + safety rules."""

    def test_refuse_outside_cwd(self):
        with TemporaryDirectory() as tmp_a, TemporaryDirectory() as tmp_b:
            # tmp_a is cwd; pass an absolute path pointing into tmp_b — error
            cwd = Path(tmp_a)
            other_abs = Path(tmp_b).resolve()
            # Use the absolute other path as the projectname (will be
            # resolved to outside cwd)
            rc = bootstrap.bootstrap(
                str(other_abs),
                cwd_override=cwd,
            )
            self.assertEqual(rc, 1)

    def test_refuse_non_empty_without_yes(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            # First bootstrap succeeds
            rc1 = _run_bootstrap(cwd, "proj", mode="full")
            self.assertEqual(rc1, 0)
            # Second invocation without --yes — refuse
            rc2 = _run_bootstrap(cwd, "proj", mode="full", yes=False)
            self.assertEqual(rc2, 1)

    def test_yes_overrides_non_empty(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "proj", mode="full")
            rc = _run_bootstrap(cwd, "proj", mode="full", yes=True)
            self.assertEqual(rc, 0)

    def test_dry_run_no_filesystem_writes(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            rc = _run_bootstrap(cwd, "preview", mode="full", dry_run=True)
            self.assertEqual(rc, 0)
            self.assertFalse((cwd / "preview").exists())

    def test_no_git_init_or_claude_dir(self):
        """Spec c rules #3 + #4: no `git init`; no `.claude/`."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "proj", mode="full")
            target = cwd / "proj"
            self.assertFalse((target / ".git").exists())
            self.assertFalse((target / ".claude").exists())


class TestCLIParser(unittest.TestCase):
    """argparse signature per v1.1 contract."""

    def test_projectname_positional_required(self):
        parser = bootstrap._build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([])

    def test_mode_flags_mutually_exclusive(self):
        parser = bootstrap._build_parser()
        args = parser.parse_args(["mentor"])
        self.assertEqual(args.mode, "full")
        args = parser.parse_args(["mentor", "--minimal"])
        self.assertEqual(args.mode, "minimal")
        args = parser.parse_args(["mentor", "--code"])
        self.assertEqual(args.mode, "code")
        args = parser.parse_args(["mentor", "--website"])
        self.assertEqual(args.mode, "website")
        with self.assertRaises(SystemExit):
            parser.parse_args(["mentor", "--minimal", "--code"])

    def test_dry_run_and_yes_flags(self):
        parser = bootstrap._build_parser()
        args = parser.parse_args(["mentor", "--dry-run", "--yes"])
        self.assertTrue(args.dry_run)
        self.assertTrue(args.yes)


if __name__ == "__main__":
    unittest.main()
