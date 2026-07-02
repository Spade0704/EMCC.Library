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
    ├── Index.md, CLAUDE.md, Cheatsheet.md, .gitignore

assets/{logos,brand,photos,videos,designs,generated}/.gitkeep is OPT-IN
(2026-07-02 ruling): no mode emits it by default; the independent
--assets flag (composable with any mode) adds the six subfolders.

Modes covered: --full (default), --minimal, --code, --website; plus the
orthogonal --assets flag.
Plus: idempotency (refuse-non-empty + --yes override), refuse-outside-cwd,
--dry-run no-writes.

DEPRECATED v1.0 tests (test_bootstrap, test_t1_p52, test_t2_p53,
test_t3_p54, test_phase6_full_chain_e2e) retired as MI-16; see
MIGRATION-ISSUES.md.
"""

import os
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import bootstrap  # noqa: E402


def _run_bootstrap(target_cwd: Path, projectname: str, mode: str = "full",
                   yes: bool = False, dry_run: bool = False,
                   assets: bool = False) -> int:
    """Invoke bootstrap.bootstrap() with cwd_override (tests use tmp dirs)."""
    return bootstrap.bootstrap(
        projectname,
        mode=mode,
        dry_run=dry_run,
        yes=yes,
        assets=assets,
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
                "Index.md", "CLAUDE.md", "Cheatsheet.md",
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

    def test_no_assets_flag_omits_assets(self):
        """assets/ is opt-in (2026-07-02 ruling): --full alone emits NO assets/."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            self.assertFalse(
                (cwd / "mentor" / "assets").exists(),
                "--full without --assets must not emit assets/",
            )

    def test_assets_flag_composes_with_full(self):
        """--full --assets adds the six assets/* subfolders."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            rc = _run_bootstrap(cwd, "mentor", mode="full", assets=True)
            self.assertEqual(rc, 0)
            assets = cwd / "mentor" / "assets"
            for sub in ("logos", "brand", "photos", "videos", "designs", "generated"):
                self.assertTrue(
                    (assets / sub / ".gitkeep").is_file(),
                    "missing assets/{}/.gitkeep".format(sub),
                )

    def test_full_omits_numbered_section_stubs(self):
        """Anti-regression (Candidate A ban): --full emits NO empty numbered
        section stubs (01-*/02-*/03-*) under wiki.<name>/git/. Section numbers
        are reserved semantic slots created only when content earns them
        (Delta Force 2026-07-02-wiki-section-numbering-scheme, 5/5 → B).
        00-Start-Here/ and 04-Contributing/ exist only because the six
        materialized boilerplate pages live there."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            wiki_git = cwd / "mentor" / "wiki.mentor" / "git"
            self.assertTrue(wiki_git.is_dir())
            numbered = [
                child.name for child in wiki_git.iterdir()
                if child.is_dir() and re.match(r"^0[123]-", child.name)
            ]
            self.assertEqual(
                numbered, [],
                "--full must not emit numbered section stubs: {}".format(numbered),
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

    def test_full_index_md_has_framework18_three_zone_skeleton(self):
        """Index.md emits the framework/18 Wiki-as-Memory 3-zone skeleton
        (dir-20260613e SLICE 1b), with safe-default token substitution and
        no literal 'None'."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            index_md = (cwd / "mentor" / "Index.md").read_text(encoding="utf-8")
            # Three zones present, in order
            i_z1 = index_md.find("## Zone 1")
            i_z2 = index_md.find("## Zone 2")
            i_z3 = index_md.find("## Zone 3")
            self.assertNotEqual(i_z1, -1, "missing Zone 1 heading")
            self.assertNotEqual(i_z2, -1, "missing Zone 2 heading")
            self.assertNotEqual(i_z3, -1, "missing Zone 3 heading")
            self.assertTrue(i_z1 < i_z2 < i_z3, "zones out of order")
            # Routing contract + 'expand one hop' rule stated
            self.assertIn("Routing contract", index_md)
            self.assertIn("expand one hop", index_md)
            # Zone 1 routes to the wiki router with the safe-default router path
            self.assertIn("wiki.mentor/git/Home.md", index_md)
            # Catalog-don't-crawl guardrail: Zone 1 does NOT re-list wiki pages
            self.assertIn("does NOT duplicate the wiki page list", index_md)
            # Zone 3 stays a Phase-2 stub
            self.assertIn("Phase 2", index_md)
            # Safe-default substitution: never a literal 'None'
            self.assertNotIn("None", index_md)
            self.assertNotIn("{{", index_md)

    def test_full_emits_empty_valid_canon_roster(self):
        """dir-20260613h-canon-scaffold: bootstrap seeds an empty-but-valid
        `_canon/roster.yaml` so the P13 check_concept_coverage validator
        (which hard-requires the file) passes on a fresh project. Delta Force
        verdict: tasks/delta-force/2026-06-13-canon-roster-scaffold.md."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "mentor", mode="full")
            roster = (cwd / "mentor" / "Biz.Automation" / "wikisys.mentor"
                      / "_canon" / "roster.yaml")
            self.assertTrue(roster.is_file(), "missing _canon/roster.yaml")
            text = roster.read_text(encoding="utf-8")
            # Explicit empty-list form (not a bare `entities:`) + operator note.
            self.assertIn("entities: []", text)
            self.assertIn("SAFE TO EDIT", text)
            # Parses to an empty entities list via the SAME loader P13 uses.
            scripts_dir = (REPO_ROOT / "Biz.Automation" / "wikisys.library"
                           / "_scripts")
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            from _lib.config_loader import load_config_yaml  # noqa: E402
            entries = load_config_yaml(
                roster, wrapper_key="entities",
                required_keys=("canonical_name",), entity_noun="roster entry")
            self.assertEqual(entries, [])
            # Validator-side pin: once the project is wired as a consumer
            # (emcc.modules.json present so find_canon_dir resolves the
            # wikisys _canon/), P13 exits 0 on the scaffolded empty roster.
            # Bootstrap does not emit emcc.modules.json itself (added at
            # consumer-hookup time per the post-bootstrap checklist); the
            # two existing consumers already have it, so the scaffold fixes
            # them. Simulate that wired state here.
            (cwd / "mentor" / "emcc.modules.json").write_text(
                "{}\n", encoding="utf-8")
            import check_concept_coverage  # noqa: E402
            wiki_root = cwd / "mentor" / "wiki.mentor" / "git"
            rc = check_concept_coverage._main(wiki_root)
            self.assertEqual(rc, 0, "P13 check_concept_coverage should pass on "
                                    "a freshly bootstrapped empty roster")

    def test_minimal_omits_canon_roster(self):
        """--minimal ships no Biz.Automation/ kit, hence no _canon/roster.yaml."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            _run_bootstrap(cwd, "thin", mode="minimal")
            roster = (cwd / "thin" / "Biz.Automation" / "wikisys.thin"
                      / "_canon" / "roster.yaml")
            self.assertFalse(roster.exists(),
                             "minimal mode should not emit a canon roster")

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

    def test_minimal_composes_with_assets_flag(self):
        """--minimal --assets is legal: the orthogonal flag simply adds
        the six assets/* folders on top of the thin tree."""
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            rc = _run_bootstrap(cwd, "thin", mode="minimal", assets=True)
            self.assertEqual(rc, 0)
            target = cwd / "thin"
            self.assertFalse((target / "Biz.Automation").exists())
            for sub in ("logos", "brand", "photos", "videos", "designs", "generated"):
                self.assertTrue(
                    (target / "assets" / sub / ".gitkeep").is_file(),
                    "missing assets/{}/.gitkeep".format(sub),
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
            # assets/ no longer default under --code (opt-in via --assets).
            self.assertFalse((target / "assets").exists())


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

    def test_assets_flag_independent_of_mode_group(self):
        """--assets is an orthogonal boolean, NOT a mode: default off,
        composable with every mode flag."""
        parser = bootstrap._build_parser()
        args = parser.parse_args(["mentor"])
        self.assertFalse(args.assets)
        args = parser.parse_args(["mentor", "--assets"])
        self.assertTrue(args.assets)
        self.assertEqual(args.mode, "full")
        for mode_flag, mode in (("--minimal", "minimal"), ("--code", "code"),
                                ("--website", "website"), ("--full", "full")):
            args = parser.parse_args(["mentor", mode_flag, "--assets"])
            self.assertTrue(args.assets)
            self.assertEqual(args.mode, mode)


class TestProjectnameValidation(unittest.TestCase):
    """Audit B4: filesystem-safe projectname allowlist (fail-closed)."""

    def test_valid_name_proceeds(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            rc = _run_bootstrap(cwd, "my-proj_2.0", mode="full")
            self.assertEqual(rc, 0)
            self.assertTrue((cwd / "my-proj_2.0").is_dir())

    def test_separator_name_exits_nonzero(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            rc = _run_bootstrap(cwd, "foo/bar", mode="full")
            self.assertNotEqual(rc, 0)
            # No partial scaffold written for the rejected name.
            self.assertFalse((cwd / "foo").exists())

    def test_traversal_token_exits_nonzero(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            self.assertNotEqual(_run_bootstrap(cwd, "..", mode="full"), 0)
            self.assertNotEqual(_run_bootstrap(cwd, ".", mode="full"), 0)

    def test_traversal_path_exits_nonzero(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            rc = _run_bootstrap(cwd, "../escape", mode="full")
            self.assertNotEqual(rc, 0)

    def test_illegal_char_exits_nonzero(self):
        with TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            for bad in ("bad name", "weird*name", "tab\tname"):
                self.assertNotEqual(
                    _run_bootstrap(cwd, bad, mode="full"), 0,
                    "expected non-zero exit for {!r}".format(bad),
                )


class TestSectionNumberingCanonicalNote(unittest.TestCase):
    """Item-1 guard: the canonical upstream How-to-Use-This-Wiki page states
    the semantic-slot section-numbering contract (sparse-by-design gaps,
    never renumber). Guards the self-explaining policy against silent
    removal. Ruling: tasks/delta-force/2026-07-02-wiki-section-numbering-scheme.md."""

    CANONICAL_PAGE = (REPO_ROOT / "wiki.codex" / "git" / "00-Start-Here"
                      / "How-to-Use-This-Wiki.md")

    def test_canonical_page_states_semantic_slot_contract(self):
        self.assertTrue(self.CANONICAL_PAGE.is_file(),
                        "canonical page missing: {}".format(self.CANONICAL_PAGE))
        text = self.CANONICAL_PAGE.read_text(encoding="utf-8")
        self.assertIn("Section numbering", text)
        self.assertIn("semantic slot", text)
        self.assertIn("sparse by design", text)
        self.assertIn("never renumber", text)


if __name__ == "__main__":
    unittest.main()
