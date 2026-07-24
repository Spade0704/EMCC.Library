"""Tests for validate_visual_evidence.py (§9.9 visual-evidence sidecar validator).

Stdlib unittest per spec §7 Phase 3. Validates against the SHARED canonical
schema (wiki.codex/git/codex/schemas/visual-evidence.schema.json) — the real
artifact, so a schema drift breaks these tests (intended).
"""

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import validate_visual_evidence as vve  # noqa: E402


def _valid_sidecar():
    """A minimal fully-conforming sidecar (fresh-gen root)."""
    return {
        "asset_path": "assets/sprites/marauder_idle.png",
        "sha256": "0" * 64,
        "format": "png",
        "dimensions": {"width": 128, "height": 128},
        "base_asset_ref": "fresh-gen",
        "prompt": "iron soul marauder, idle pose",
        "seed": 12345,
        "model_id": "grok-imagine-v2",
        "style_bible_ref": {"path": "IRON_SOUL_STYLE.md", "commit_sha": "abc123"},
        "style_tokens_declared": {
            "palette": ["#0a0a0a", "#c8823c"],
            "grid": "16x16",
            "resolution_class": "sprite-128",
        },
        "generated_at": "2026-07-24T06:00:00Z",
        "generator": "grok-imagine",
        "aesthetic_signoff": {
            "name": "JP",
            "date": "2026-07-24",
            "verdict": "on-vibe",
            "note": "clean",
            "reviewed_at_resolution": "128x128",
            "reviewed_on_surface": "game-canvas",
        },
    }


class TestSchemaConformance(unittest.TestCase):
    def setUp(self):
        self.schema = vve.load_schema()

    def test_schema_loads_and_has_no_cert_class_property(self):
        self.assertEqual(len(self.schema["required"]), 13)
        self.assertNotIn("cert_class", self.schema["properties"])

    def test_valid_sidecar_conforms(self):
        self.assertEqual(
            vve.validate_against_schema(_valid_sidecar(), self.schema), [])

    def test_missing_required_key_flagged(self):
        s = _valid_sidecar()
        del s["sha256"]
        errs = vve.validate_against_schema(s, self.schema)
        self.assertTrue(any("missing required key 'sha256'" in e for e in errs))

    def test_wrong_type_flagged(self):
        s = _valid_sidecar()
        s["dimensions"] = "128x128"  # should be object
        errs = vve.validate_against_schema(s, self.schema)
        self.assertTrue(any("dimensions" in e and "expected type" in e for e in errs))

    def test_nested_required_flagged(self):
        s = _valid_sidecar()
        del s["dimensions"]["height"]
        errs = vve.validate_against_schema(s, self.schema)
        self.assertTrue(any("dimensions" in e and "height" in e for e in errs))

    def test_enum_violation_flagged(self):
        s = _valid_sidecar()
        s["aesthetic_signoff"]["verdict"] = "meh"
        errs = vve.validate_against_schema(s, self.schema)
        self.assertTrue(any("verdict" in e and "enum" in e for e in errs))

    def test_union_type_accepts_both_seed_forms(self):
        s = _valid_sidecar()
        s["seed"] = "0xDEADBEEF"  # string form of the union ["string","integer"]
        self.assertEqual(vve.validate_against_schema(s, self.schema), [])

    def test_array_items_typed(self):
        s = _valid_sidecar()
        s["style_tokens_declared"]["palette"] = ["#0a0a0a", 123]  # 123 not string
        errs = vve.validate_against_schema(s, self.schema)
        self.assertTrue(any("palette[1]" in e for e in errs))

    def test_bool_is_not_integer(self):
        # seed union is [string, integer]; a bool must NOT satisfy integer.
        s = _valid_sidecar()
        s["seed"] = True
        errs = vve.validate_against_schema(s, self.schema)
        self.assertTrue(any("seed" in e for e in errs))


class TestRules(unittest.TestCase):
    def test_fresh_gen_string_passes(self):
        self.assertEqual(vve.check_rules(_valid_sidecar()), [])

    def test_unflagged_base_string_fails_r1(self):
        s = _valid_sidecar()
        s["base_asset_ref"] = "something-else"
        errs = vve.check_rules(s)
        self.assertTrue(any(e.startswith("R1") for e in errs))

    def test_object_base_requires_path_and_sha(self):
        s = _valid_sidecar()
        s["base_asset_ref"] = {"ast_id": None, "path": "", "sha256": ""}
        errs = vve.check_rules(s)
        self.assertEqual(sum(e.startswith("R1") for e in errs), 2)

    def test_object_base_with_path_sha_passes_r1(self):
        s = _valid_sidecar()
        s["base_asset_ref"] = {"ast_id": "AST-IRONSOUL-00001",
                               "path": "assets/base/marauder.png",
                               "sha256": "a" * 64}
        self.assertEqual([e for e in vve.check_rules(s) if e.startswith("R1")], [])

    def test_empty_signoff_name_fails_r2(self):
        s = _valid_sidecar()
        s["aesthetic_signoff"]["name"] = "   "
        errs = vve.check_rules(s)
        self.assertTrue(any(e.startswith("R2") for e in errs))

    def test_cert_class_in_sidecar_rejected(self):
        s = _valid_sidecar()
        s["cert_class"] = "mechanical-pass-human-aesthetic"
        errs = vve.check_rules(s)
        self.assertTrue(any("cert_class must NOT appear" in e for e in errs))

    def test_cert_class_nested_rejected(self):
        # anti-self-cert is enforced at ANY depth, not just the root.
        s = _valid_sidecar()
        s["aesthetic_signoff"]["cert_class"] = "mechanical-pass-human-aesthetic"
        errs = vve.check_rules(s)
        self.assertTrue(any("cert_class must NOT appear" in e for e in errs))


class TestMechanical(unittest.TestCase):
    def _write_asset(self, root: Path, rel: str, data: bytes):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return hashlib.sha256(data).hexdigest()

    def test_sha256_match_and_path_binding_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s = _valid_sidecar()
            s["sha256"] = self._write_asset(root, s["asset_path"], b"PNGDATA")
            self.assertEqual(vve.check_mechanical(s, root), [])

    def test_missing_asset_fails_path_binding(self):
        with tempfile.TemporaryDirectory() as td:
            errs = vve.check_mechanical(_valid_sidecar(), Path(td))
            self.assertTrue(any("check-3" in e for e in errs))

    def test_sha_mismatch_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s = _valid_sidecar()
            self._write_asset(root, s["asset_path"], b"REALBYTES")
            s["sha256"] = "f" * 64  # declared != actual
            errs = vve.check_mechanical(s, root)
            self.assertTrue(any("check-1" in e for e in errs))

    def test_dotdot_escaping_path_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "wiki"
            root.mkdir()
            # a real file OUTSIDE root that a '..' path would otherwise re-hash
            (Path(td) / "secret.png").write_bytes(b"OUTSIDE")
            s = _valid_sidecar()
            s["asset_path"] = "../secret.png"
            errs = vve.check_mechanical(s, root)
            self.assertTrue(any("check-3" in e and "refused" in e for e in errs))

    def test_absolute_path_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s = _valid_sidecar()
            s["asset_path"] = str((root / "x.png").resolve())  # absolute
            errs = vve.check_mechanical(s, root)
            self.assertTrue(any("check-3" in e and "refused" in e for e in errs))


class TestSidecarToRecipe(unittest.TestCase):
    def test_style_bible_flattened_to_scalars(self):
        recipe, _ = vve.sidecar_to_recipe(_valid_sidecar())
        self.assertEqual(recipe["style_bible_path"], "IRON_SOUL_STYLE.md")
        self.assertEqual(recipe["style_bible_commit_sha"], "abc123")
        self.assertNotIn("style_bible_ref", recipe)
        # all recipe values are scalars (§9 frontmatter-safe)
        for v in recipe.values():
            self.assertNotIsInstance(v, (dict, list))

    def test_provenance_scalars_and_visual_evidence_sha_ride_recipe(self):
        recipe, _ = vve.sidecar_to_recipe(_valid_sidecar())
        for key in ("prompt", "seed", "model_id", "generator", "generated_at"):
            self.assertIn(key, recipe)
        self.assertEqual(recipe["visual_evidence_sha256"], "0" * 64)

    def test_fresh_gen_maps_to_empty_derived_from(self):
        _, derived = vve.sidecar_to_recipe(_valid_sidecar())
        self.assertEqual(derived, [])

    def test_object_base_with_ast_id_maps_to_derived_from(self):
        s = _valid_sidecar()
        s["base_asset_ref"] = {"ast_id": "AST-IRONSOUL-00001",
                               "path": "p", "sha256": "a" * 64}
        _, derived = vve.sidecar_to_recipe(s)
        self.assertEqual(derived, ["AST-IRONSOUL-00001"])

    def test_object_base_without_ast_id_is_empty_pending(self):
        s = _valid_sidecar()
        s["base_asset_ref"] = {"ast_id": None, "path": "p", "sha256": "a" * 64}
        _, derived = vve.sidecar_to_recipe(s)
        self.assertEqual(derived, [])


class TestValidateSidecarAndCli(unittest.TestCase):
    def _write_sidecar(self, root: Path, sidecar) -> Path:
        p = root / "asset.png.visual-evidence.json"
        p.write_text(json.dumps(sidecar), encoding="utf-8")
        return p

    def test_valid_sidecar_ok_without_asset_root(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write_sidecar(Path(td), _valid_sidecar())
            result = vve.validate_sidecar(path)
            self.assertTrue(result["ok"], result["errors"])

    def test_full_validation_with_asset_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s = _valid_sidecar()
            asset = root / s["asset_path"]
            asset.parent.mkdir(parents=True, exist_ok=True)
            asset.write_bytes(b"BYTES")
            s["sha256"] = hashlib.sha256(b"BYTES").hexdigest()
            path = self._write_sidecar(root, s)
            result = vve.validate_sidecar(path, asset_root=root)
            self.assertTrue(result["ok"], result["errors"])

    def test_malformed_json_raises_valueerror(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                vve.validate_sidecar(p)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            good = self._write_sidecar(root, _valid_sidecar())
            self.assertEqual(vve._cli(["validate", "--sidecar", str(good)]), 0)

            bad = _valid_sidecar()
            del bad["prompt"]
            bad_path = root / "bad.visual-evidence.json"
            bad_path.write_text(json.dumps(bad), encoding="utf-8")
            self.assertEqual(vve._cli(["validate", "--sidecar", str(bad_path)]), 1)

            broken = root / "broken.json"
            broken.write_text("{", encoding="utf-8")
            self.assertEqual(vve._cli(["validate", "--sidecar", str(broken)]), 2)


def _write_base_record(wiki_root: Path, ast_id: str, asset_class: str,
                       rel_path: str):
    """Create a minimal §9.1 base-identity record at git/_registry/<id>.md."""
    reg = wiki_root / "git" / "_registry"
    reg.mkdir(parents=True, exist_ok=True)
    fm = (
        "---\n"
        "id: {}\n".format(ast_id) +
        "asset_class: {}\n".format(asset_class) +
        "name: base\n"
        "zone: git\n"
        "path: {}\n".format(rel_path) +
        "rights_consent: unknown\n"
        "derived_from: []\n"
        "recipe: {}\n"
        "url: \"\"\n"
        "---\n"
        "base record\n"
    )
    (reg / "{}.md".format(ast_id)).write_text(fm, encoding="utf-8")


def _derived_sidecar(ast_id, base_rel, base_sha):
    s = _valid_sidecar()
    s["base_asset_ref"] = {"ast_id": ast_id, "path": base_rel, "sha256": base_sha}
    return s


class TestBaseIdentityBinding(unittest.TestCase):
    def test_fresh_gen_needs_no_binding(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(
                vve.check_base_identity_binding(_valid_sidecar(), Path(td)), [])

    def test_null_ast_id_is_pending_no_binding(self):
        with tempfile.TemporaryDirectory() as td:
            s = _valid_sidecar()
            s["base_asset_ref"] = {"ast_id": None, "path": "p", "sha256": "a" * 64}
            self.assertEqual(vve.check_base_identity_binding(s, Path(td)), [])

    def test_registered_base_matching_sha_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base_rel = "assets/base/marauder.png"
            base = root / base_rel
            base.parent.mkdir(parents=True, exist_ok=True)
            base.write_bytes(b"BASEBYTES")
            sha = hashlib.sha256(b"BASEBYTES").hexdigest()
            _write_base_record(root, "AST-IRONSOUL-00001", "base-identity", base_rel)
            s = _derived_sidecar("AST-IRONSOUL-00001", base_rel, sha)
            self.assertEqual(vve.check_base_identity_binding(s, root), [])

    def test_unregistered_ast_id_fails(self):
        with tempfile.TemporaryDirectory() as td:
            s = _derived_sidecar("AST-IRONSOUL-99999", "p", "a" * 64)
            errs = vve.check_base_identity_binding(s, Path(td))
            self.assertTrue(any("not registered" in e for e in errs))

    def test_wrong_class_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base_rel = "assets/x.png"
            (root / base_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / base_rel).write_bytes(b"X")
            _write_base_record(root, "AST-IRONSOUL-00002", "sprite", base_rel)
            s = _derived_sidecar("AST-IRONSOUL-00002", base_rel,
                                 hashlib.sha256(b"X").hexdigest())
            errs = vve.check_base_identity_binding(s, root)
            self.assertTrue(any("not 'base-identity'" in e for e in errs))

    def test_sha_mismatch_with_registered_base_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base_rel = "assets/base/m.png"
            (root / base_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / base_rel).write_bytes(b"REALBASE")
            _write_base_record(root, "AST-IRONSOUL-00003", "base-identity", base_rel)
            # frame declares a DIFFERENT base sha
            s = _derived_sidecar("AST-IRONSOUL-00003", base_rel, "f" * 64)
            errs = vve.check_base_identity_binding(s, root)
            self.assertTrue(any("hashes to" in e for e in errs))


class TestStyleBible(unittest.TestCase):
    def test_existing_bible_path_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "IRON_SOUL_STYLE.md").write_text("bible", encoding="utf-8")
            self.assertEqual(vve.check_style_bible(_valid_sidecar(), root), [])

    def test_missing_bible_path_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            errs = vve.check_style_bible(_valid_sidecar(), Path(td))
            self.assertTrue(any("style-bible" in e for e in errs))


class TestConfigGameClasses(unittest.TestCase):
    """B3: the game-dev asset classes are in the real config vocabulary."""

    def test_game_classes_present_in_config(self):
        import asset_registry
        cfg_path = (_SCRIPTS.parent / "_config" / "asset_registry.yaml")
        from _lib.frontmatter import parse_config_yaml
        config = parse_config_yaml(cfg_path.read_text(encoding="utf-8"))
        classes = asset_registry.config_asset_classes(config)
        for cls in ("sprite", "base-identity", "pose-anim-frame", "audio-cue"):
            self.assertIn(cls, classes)
        # the v1.4 ratified classes still present
        for cls in ("ugc", "deliverable"):
            self.assertIn(cls, classes)


if __name__ == "__main__":
    unittest.main()
