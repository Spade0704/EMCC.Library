"""Tests for _scripts/materialize_boilerplate.py — CARTO-06 / M-A component 5.

Convention lock (C2 council): materialize-then-link — the generator owns ToC
consistency. Constraints under test: the exact 6 pages, __SEP__ decoding,
placeholder substitution limited to <Project Name> + <YYYY-MM-DD>, idempotent
SKIP of existing pages (consumer content is never clobbered), MISSING-template
honesty, dry-run writes nothing.
"""
import io
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import materialize_boilerplate as mb

KIT_TEMPLATES = (
    Path(__file__).resolve().parents[1]
    / "Biz.Automation" / "wikisys.library" / "_template"
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class MaterializeBoilerplateTests(unittest.TestCase):

    def test_six_pages_created_from_real_kit_templates(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "git"
            actions = mb.materialize_boilerplate(
                wiki, KIT_TEMPLATES, "Demo Project", today=date(2026, 6, 11))
            self.assertEqual([a for a, _ in actions], ["CREATE"] * 6)
            self.assertTrue((wiki / "00-Start-Here" / "Glossary.md").is_file())
            self.assertTrue((wiki / "04-Contributing" / "Style-Guide.md").is_file())
            text = (wiki / "00-Start-Here" / "Glossary.md").read_text(encoding="utf-8")
            self.assertIn("Demo Project", text)
            self.assertIn("2026-06-11", text)
            self.assertNotIn("<Project Name>", text)
            self.assertNotIn("<YYYY-MM-DD>", text)

    def test_other_angle_tokens_ship_verbatim(self):
        # Example tokens inside templates (e.g. <forbidden-term>) are content,
        # not placeholders — they must survive materialization.
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "git"
            mb.materialize_boilerplate(wiki, KIT_TEMPLATES, "X", today=date(2026, 6, 11))
            terminology = (wiki / "00-Start-Here" / "Terminology-Rules.md").read_text(
                encoding="utf-8")
            self.assertIn("<forbidden-term>", terminology)

    def test_existing_page_skipped_never_clobbered(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "git"
            curated = "---\ntitle: curated\n---\n\nConsumer-curated content.\n"
            _write(wiki / "00-Start-Here" / "Glossary.md", curated)
            actions = dict(
                (rel, a) for a, rel in mb.materialize_boilerplate(
                    wiki, KIT_TEMPLATES, "X"))
            self.assertEqual(actions["00-Start-Here/Glossary.md"], "SKIP")
            self.assertEqual(
                (wiki / "00-Start-Here" / "Glossary.md").read_text(encoding="utf-8"),
                curated)

    def test_idempotent_second_run_all_skip(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "git"
            mb.materialize_boilerplate(wiki, KIT_TEMPLATES, "X")
            actions = mb.materialize_boilerplate(wiki, KIT_TEMPLATES, "X")
            self.assertEqual([a for a, _ in actions], ["SKIP"] * 6)

    def test_missing_template_reported_not_fatal(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "git"
            empty_templates = Path(tmp) / "templates"
            empty_templates.mkdir()
            actions = mb.materialize_boilerplate(wiki, empty_templates, "X")
            self.assertEqual([a for a, _ in actions], ["MISSING"] * 6)

    def test_dry_run_writes_nothing(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "git"
            actions = mb.materialize_boilerplate(
                wiki, KIT_TEMPLATES, "X", dry_run=True)
            self.assertEqual([a for a, _ in actions], ["CREATE"] * 6)
            self.assertFalse(wiki.exists())

    def test_cli_discovers_consumer_and_materializes(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            wikisys = root / "Biz.Automation" / "wikisys.demo"
            (root / "wiki.demo" / "git").mkdir(parents=True)
            tdir = wikisys / "_template"
            tdir.mkdir(parents=True)
            for tname in mb.BOILERPLATE_TEMPLATES:
                _write(tdir / tname, "# <Project Name> page\n")
            out = io.StringIO()
            with redirect_stdout(out):
                rc = mb.main([], consumer_root=root)
            self.assertEqual(rc, 0)
            self.assertIn("Materialized: 6", out.getvalue())
            self.assertIn(
                "demo page",
                (root / "wiki.demo" / "git" / "00-Start-Here" /
                 "How-to-Use-This-Wiki.md").read_text(encoding="utf-8"))


class BootstrapBoilerplateIntegrationTests(unittest.TestCase):
    """bootstrap() births new wikis with the 6 pages (no dead Home links)."""

    def test_bootstrap_materializes_six_pages(self):
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        try:
            import bootstrap as bs
        finally:
            _sys.path.pop(0)
        with TemporaryDirectory() as tmp:
            out = io.StringIO()
            with redirect_stdout(out):
                rc = bs.bootstrap("demo", cwd_override=Path(tmp))
            self.assertEqual(rc, 0)
            self.assertIn("Boilerplate pages: 6", out.getvalue())
            wiki = Path(tmp) / "demo" / "wiki.demo" / "git"
            for rel in ("00-Start-Here/How-to-Use-This-Wiki.md",
                        "00-Start-Here/Glossary.md",
                        "00-Start-Here/Terminology-Rules.md",
                        "04-Contributing/Update-Cascade.md",
                        "04-Contributing/File-Routing.md",
                        "04-Contributing/Style-Guide.md"):
                self.assertTrue((wiki / rel).is_file(), rel)

    def test_bootstrap_dry_run_writes_no_pages(self):
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        try:
            import bootstrap as bs
        finally:
            _sys.path.pop(0)
        with TemporaryDirectory() as tmp:
            out = io.StringIO()
            with redirect_stdout(out):
                rc = bs.bootstrap("demo", dry_run=True, cwd_override=Path(tmp))
            self.assertEqual(rc, 0)
            self.assertFalse((Path(tmp) / "demo").exists())

    def test_minimal_mode_skips_boilerplate(self):
        # Audit M-A-5 finding 2: minimal mode ships no kit + no Home ToC.
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        try:
            import bootstrap as bs
        finally:
            _sys.path.pop(0)
        with TemporaryDirectory() as tmp:
            out = io.StringIO()
            with redirect_stdout(out):
                bs.bootstrap("demo", mode="minimal", cwd_override=Path(tmp))
            self.assertIn("Boilerplate pages: 0", out.getvalue())
            self.assertFalse(
                (Path(tmp) / "demo" / "wiki.demo" / "git" / "00-Start-Here"
                 / "Glossary.md").exists())

    def test_summary_counts_create_only_not_skip(self):
        # Audit M-A-5 finding 1: a rerun (all SKIP) must report 0 pages written.
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        try:
            import bootstrap as bs
        finally:
            _sys.path.pop(0)
        with TemporaryDirectory() as tmp:
            bs.bootstrap("demo", yes=True, cwd_override=Path(tmp))
            out = io.StringIO()
            with redirect_stdout(out):
                bs.bootstrap("demo", yes=True, cwd_override=Path(tmp))
            self.assertIn("Boilerplate pages: 0", out.getvalue())


if __name__ == "__main__":
    unittest.main()
