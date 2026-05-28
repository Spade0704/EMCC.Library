"""Drift guard for the generated Librarian persona drop-in (OBS-4 closure).

The drop-in at `.claude/personas/CLAUDE.librarian.md` is generated from the
canonical `wiki.<name>/git/codex/CODEX_LIBRARIAN.md`. These tests pin
generation determinism and fail CI if the on-disk drop-in drifts from the
canonical (the structural cure for OBS-4).
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import generate_persona_dropin
from _lib import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent

_CANONICAL_FIXTURE = (
    "---\n"
    'title: "Codex — Librarian Persona"\n'
    "type: framework\n"
    "last_updated: 2026-05-25\n"
    "---\n"
    "\n"
    "# Codex — Librarian Persona\n"
    "\n"
    "## Identity\n"
    "Body content here.\n"
)


class RenderDropinTests(unittest.TestCase):
    def test_render_is_deterministic(self):
        a = generate_persona_dropin.render_dropin(_CANONICAL_FIXTURE, "x/CODEX_LIBRARIAN.md")
        b = generate_persona_dropin.render_dropin(_CANONICAL_FIXTURE, "x/CODEX_LIBRARIAN.md")
        self.assertEqual(a, b)

    def test_render_uses_canonical_last_updated_not_today(self):
        out = generate_persona_dropin.render_dropin(_CANONICAL_FIXTURE, "x/CODEX_LIBRARIAN.md")
        self.assertIn("last_updated: 2026-05-25", out)

    def test_render_strips_canonical_frontmatter_keeps_body(self):
        out = generate_persona_dropin.render_dropin(_CANONICAL_FIXTURE, "x/CODEX_LIBRARIAN.md")
        self.assertIn("# Codex — Librarian Persona", out)
        self.assertIn("Body content here.", out)
        # type: framework was canonical-only; must not leak into the drop-in fm
        self.assertNotIn("type: framework", out)

    def test_render_includes_generated_banner_and_canonical_source(self):
        out = generate_persona_dropin.render_dropin(_CANONICAL_FIXTURE, "x/CODEX_LIBRARIAN.md")
        self.assertIn("GENERATED FILE — DO NOT EDIT BY HAND", out)
        self.assertIn('canonical_source: "x/CODEX_LIBRARIAN.md"', out)


class OnDiskDriftGuardTests(unittest.TestCase):
    """The committed drop-in must equal a regeneration from the committed canonical."""

    def _canonical(self):
        return next(iter(sorted(
            REPO_ROOT.glob("wiki.*/git/codex/CODEX_LIBRARIAN.md"))))

    def test_ondisk_dropin_matches_canonical(self):
        canonical = self._canonical()
        canonical_rel = canonical.relative_to(REPO_ROOT).as_posix()
        expected = generate_persona_dropin.render_dropin(
            canonical.read_text(encoding="utf-8"), canonical_rel)
        actual = (REPO_ROOT / ".claude" / "personas"
                  / "CLAUDE.librarian.md").read_text(encoding="utf-8")
        self.assertEqual(
            actual, expected,
            "drop-in has drifted from the canonical; "
            "run generate_persona_dropin.py to regenerate.")

    def test_check_mode_returns_zero_when_in_sync(self):
        self.assertEqual(generate_persona_dropin.main(["--check"]), 0)


class CheckModeFixtureTests(unittest.TestCase):
    def test_check_detects_drift(self):
        with TemporaryDirectory() as tmp:
            install = Path(tmp)
            (install / "CLAUDE.md").write_text("# C\n", encoding="utf-8")
            (install / "module.json").write_text("{}\n", encoding="utf-8")
            codex = install / "wiki.codex" / "git" / "codex"
            codex.mkdir(parents=True)
            canonical = codex / "CODEX_LIBRARIAN.md"
            canonical.write_text(_CANONICAL_FIXTURE, encoding="utf-8")
            target = install / ".claude" / "personas" / "CLAUDE.librarian.md"
            target.parent.mkdir(parents=True)
            target.write_text("stale hand-edited content\n", encoding="utf-8")

            rc = generate_persona_dropin.main(
                ["--check", "--canonical", str(canonical), "--target", str(target)])
            self.assertEqual(rc, 1)

    def test_generate_then_check_roundtrip(self):
        with TemporaryDirectory() as tmp:
            install = Path(tmp)
            codex = install / "wiki.codex" / "git" / "codex"
            codex.mkdir(parents=True)
            canonical = codex / "CODEX_LIBRARIAN.md"
            canonical.write_text(_CANONICAL_FIXTURE, encoding="utf-8")
            target = install / ".claude" / "personas" / "CLAUDE.librarian.md"

            self.assertEqual(
                generate_persona_dropin.main(
                    ["--canonical", str(canonical), "--target", str(target)]), 0)
            self.assertEqual(
                generate_persona_dropin.main(
                    ["--check", "--canonical", str(canonical), "--target", str(target)]), 0)


if __name__ == "__main__":
    unittest.main()
