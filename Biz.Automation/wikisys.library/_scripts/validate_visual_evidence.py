"""validate_visual_evidence.py — §9.9 visual-evidence sidecar validator (v0.1).

Validates a `<asset>.visual-evidence.json` sidecar against the SHARED canonical
schema (`wiki.codex/git/codex/schemas/visual-evidence.schema.json`, council SHIP
v0.1) — the SAME artifact iron-soul-anvil's `pnpm anvil test --strict-assets`
consumes. Two validators, one schema, zero divergence (spec §9.9).

Registry-side scope (stdlib-only, no `jsonschema` pip):
    - SCHEMA conformance: a hand-rolled draft-07 walker over the stdlib-safe
      subset the schema is authored in — type (incl. union type-lists),
      required, enum, nested objects (properties/required), arrays (items).
      NO $ref/allOf/oneOf/if-then/regex (the schema never uses them).
    - RULE R1: `base_asset_ref` XOR fresh-gen — string form MUST equal the
      literal "fresh-gen"; object form MUST carry path+sha256; a bare/unflagged
      value is a FAIL (a settable pass with no base is the failure §9.9 fights).
    - RULE R2: `aesthetic_signoff.name` MUST be non-empty (no name = no pass).
    - CHECK 1 (sha256): re-hash the asset on disk, compare to declared `sha256`.
    - CHECK 3 (path-binding): the declared `asset_path` must exist on disk.

Checks 2/4/6 (format+dimensions on-disk, palette-subset, legal/likeness) need
pixel tooling and are the Anvil `--strict-assets` floor — NOT re-run here; the
registry validates the DECLARED sidecar values structurally + records the
attestation (spec §9.9 / v0.1 check-6 disposition).

`cert_class` is NOT a sidecar field (rejected structurally if present) — it is
set POST-facto on the cert-handoff only; a sidecar-declared cert_class would let
a generator self-declare a pass before any gate runs.

Public API:
    load_schema(schema_path=None) -> dict
    validate_against_schema(instance, schema, where="") -> list[str]
    check_rules(sidecar) -> list[str]                     # R1 + R2
    check_mechanical(sidecar, asset_root) -> list[str]    # check 1 + 3
    validate_sidecar(sidecar_path, asset_root=None, schema_path=None) -> dict
    sidecar_to_recipe(sidecar) -> tuple[dict, list]       # §9 ingest mapping

CLI (asset_registry.py argparse-verb pattern):
    python validate_visual_evidence.py validate --sidecar <f.json>
        [--asset-root <dir>] [--schema <schema.json>]

Exit codes:
    0  sidecar valid (schema + rules [+ mechanical, if --asset-root given])
    1  one or more validation findings
    2  malformed input (unreadable/!JSON sidecar or schema)

Pure stdlib per spec §8 Hard Rule 1.
"""
# @component Codex[validators]

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Canonical schema location, relative to the repo root (this file lives at
# Biz.Automation/wikisys.library/_scripts/; the schema at wiki.codex/git/codex/
# schemas/). Resolved lazily so the module imports without the file present.
_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA_PATH = (
    _REPO_ROOT / "wiki.codex" / "git" / "codex" / "schemas"
    / "visual-evidence.schema.json"
)

FRESH_GEN = "fresh-gen"

# JSON-Schema draft-07 primitive type -> Python isinstance predicate. `integer`
# excludes bool (bool is an int subclass in Python; a JSON integer is not a
# boolean). `number` accepts int or float but not bool.
_TYPE_PREDICATES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def load_schema(schema_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load + parse the canonical schema JSON. Raises ValueError on a
    missing/unparseable schema (a build-environment error, not a finding)."""
    path = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError("schema not found: {}".format(path)) from exc
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError("schema unreadable ({}): {}".format(path, exc)) from exc


def _type_ok(value: Any, type_spec: Any) -> bool:
    """draft-07 `type` may be a string or a list of strings (union)."""
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    return any(_TYPE_PREDICATES.get(t, lambda v: True)(value) for t in types)


def validate_against_schema(instance: Any, schema: Dict[str, Any],
                            where: str = "") -> List[str]:
    """Walk `instance` against `schema` (stdlib-safe draft-07 subset).

    Returns a list of prose finding strings ([] = conforms). Recurses into
    object `properties` and array `items`. Only keywords the canonical schema
    actually uses are honored: type, enum, required, properties, items.
    """
    errors: List[str] = []
    loc = where or "(root)"

    type_spec = schema.get("type")
    if type_spec is not None and not _type_ok(instance, type_spec):
        errors.append("{}: expected type {}, got {}".format(
            loc, type_spec, type(instance).__name__))
        # Type mismatch — deeper checks would be noise; stop this branch.
        return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append("{}: value {!r} not in enum {}".format(
            loc, instance, schema["enum"]))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("{}: missing required key '{}'".format(loc, key))
        props = schema.get("properties", {})
        for key, subschema in props.items():
            if key in instance:
                child = "{}.{}".format(where, key) if where else key
                errors.extend(
                    validate_against_schema(instance[key], subschema, child))

    if isinstance(instance, list) and "items" in schema:
        for idx, element in enumerate(instance):
            child = "{}[{}]".format(loc, idx)
            errors.extend(
                validate_against_schema(element, schema["items"], child))

    return errors


def check_rules(sidecar: Dict[str, Any]) -> List[str]:
    """R1 (base_asset_ref XOR fresh-gen) + R2 (signoff name non-empty).

    Code-enforced because they are not expressible in the stdlib-safe schema
    subset (they need XOR / conditional-required). Both validators (this one +
    Anvil `--strict-assets`) hard-code them identically (spec §9.9)."""
    errors: List[str] = []

    ref = sidecar.get("base_asset_ref")
    if isinstance(ref, str):
        if ref != FRESH_GEN:
            errors.append(
                "R1: base_asset_ref string form must be the literal "
                "{!r} (got {!r}) — an unflagged root gen is a FAIL".format(
                    FRESH_GEN, ref))
    elif isinstance(ref, dict):
        for key in ("path", "sha256"):
            if not ref.get(key):
                errors.append(
                    "R1: base_asset_ref object form must carry a non-empty "
                    "'{}'".format(key))
    elif ref is not None:
        errors.append(
            "R1: base_asset_ref must be the string {!r} or an object "
            "{{ast_id, path, sha256}} (got {})".format(
                FRESH_GEN, type(ref).__name__))

    signoff = sidecar.get("aesthetic_signoff")
    if isinstance(signoff, dict):
        name = signoff.get("name")
        if not (isinstance(name, str) and name.strip()):
            errors.append(
                "R2: aesthetic_signoff.name must be non-empty "
                "(no name = no pass)")

    # cert_class must never appear in a sidecar AT ANY DEPTH (post-facto
    # cert-handoff field only). Checked recursively, not just at the root — a
    # nested cert_class is still a generator self-declaring a pass before any
    # gate runs, the exact failure this standard fights.
    if _contains_key(sidecar, "cert_class"):
        errors.append(
            "cert_class must NOT appear in a sidecar (at any depth) — it is set "
            "post-facto on the cert-handoff only (a sidecar cert_class "
            "self-declares a pass before any gate runs)")

    return errors


def _contains_key(node: Any, target: str) -> bool:
    """True if `target` appears as a mapping key anywhere in `node` (dicts +
    lists, recursively)."""
    if isinstance(node, dict):
        if target in node:
            return True
        return any(_contains_key(v, target) for v in node.values())
    if isinstance(node, list):
        return any(_contains_key(v, target) for v in node)
    return False


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_mechanical(sidecar: Dict[str, Any], asset_root: Path) -> List[str]:
    """Check 1 (sha256 re-hash) + check 3 (path-binding). `asset_path` is
    resolved relative to `asset_root`. Findings are prose strings."""
    errors: List[str] = []
    asset_path = sidecar.get("asset_path")
    if not isinstance(asset_path, str) or not asset_path:
        # Structural validation already flags a bad asset_path; nothing to bind.
        return errors

    # Path-binding is a REPO-RELATIVE lookup under asset_root. An absolute path
    # or one that escapes asset_root (`..`) would re-hash a file outside the
    # registry — refuse it rather than bind/hash an unintended target.
    root = Path(asset_root).resolve()
    candidate = Path(asset_path)
    resolved = (root / candidate).resolve()
    if candidate.is_absolute() or root not in resolved.parents and resolved != root:
        errors.append(
            "check-3 (path-binding): asset_path '{}' must be a relative path "
            "within {} (absolute or '..'-escaping paths are refused)".format(
                asset_path, root))
        return errors

    if not resolved.is_file():
        errors.append(
            "check-3 (path-binding): asset_path '{}' does not exist under "
            "{}".format(asset_path, asset_root))
        return errors  # can't re-hash a file that isn't there

    declared = sidecar.get("sha256")
    actual = _sha256_file(resolved)
    if declared != actual:
        errors.append(
            "check-1 (sha256): declared {!r} != on-disk {!r} for '{}'".format(
                declared, actual, asset_path))

    return errors


def sidecar_to_recipe(sidecar: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """§9 ingest mapping (spec §9.9): fold the sidecar into an EXISTING §9.1
    record's `recipe:` (freeform scalar mapping) + `derived_from` (list).

    - Provenance scalars ride recipe 1:1; `style_bible_ref {path, commit_sha}`
      flattens to `style_bible_path` + `style_bible_commit_sha` (recipe values
      must be scalars — a nested object is refused by parse_config_yaml).
    - The sidecar pointer rides recipe as `visual_evidence_sha256` + (the caller
      sets `visual_evidence_path` to the sidecar's own path at write time).
    - `base_asset_ref` -> `derived_from`: fresh-gen -> []; object -> [ast_id] if
      resolved, else [] (base backfilled on base-identity registration).
    NO RECORD_FIELDS change — everything lands in the generic record.
    """
    recipe: Dict[str, Any] = {}
    for key in ("prompt", "seed", "model_id", "generator", "generated_at",
                "format"):
        if key in sidecar:
            recipe[key] = sidecar[key]

    bible = sidecar.get("style_bible_ref")
    if isinstance(bible, dict):
        if "path" in bible:
            recipe["style_bible_path"] = bible["path"]
        if "commit_sha" in bible:
            recipe["style_bible_commit_sha"] = bible["commit_sha"]

    if "sha256" in sidecar:
        recipe["visual_evidence_sha256"] = sidecar["sha256"]

    derived_from: List[str] = []
    ref = sidecar.get("base_asset_ref")
    if isinstance(ref, dict):
        ast_id = ref.get("ast_id")
        if isinstance(ast_id, str) and ast_id:
            derived_from = [ast_id]
    # string "fresh-gen" (or unresolved base) -> [] (verified root / pending).

    return recipe, derived_from


def validate_sidecar(sidecar_path: Path, asset_root: Optional[Path] = None,
                     schema_path: Optional[Path] = None) -> Dict[str, Any]:
    """Full validation of one sidecar file. Returns
    {"ok": bool, "errors": [str], "sidecar": dict}. Raises ValueError on a
    malformed sidecar/schema (exit-2 class, not a finding)."""
    try:
        with open(sidecar_path, "r", encoding="utf-8") as handle:
            sidecar = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError("sidecar not found: {}".format(sidecar_path)) from exc
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(
            "sidecar unreadable ({}): {}".format(sidecar_path, exc)) from exc
    if not isinstance(sidecar, dict):
        raise ValueError("sidecar must be a JSON object, got {}".format(
            type(sidecar).__name__))

    schema = load_schema(schema_path)
    errors = validate_against_schema(sidecar, schema)
    errors.extend(check_rules(sidecar))
    if asset_root is not None:
        errors.extend(check_mechanical(sidecar, Path(asset_root)))

    return {"ok": not errors, "errors": errors, "sidecar": sidecar}


def _cli(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_visual_evidence.py",
        description="Validate a visual-evidence sidecar (spec §9.9).")
    sub = parser.add_subparsers(dest="verb", required=True)
    val = sub.add_parser("validate", help="validate one sidecar file")
    val.add_argument("--sidecar", required=True, help="path to *.visual-evidence.json")
    val.add_argument("--asset-root", default=None,
                     help="root to resolve asset_path against (enables checks 1+3)")
    val.add_argument("--schema", default=None,
                     help="override schema path (default: §9 canonical)")
    args = parser.parse_args(argv)

    try:
        result = validate_sidecar(
            Path(args.sidecar),
            Path(args.asset_root) if args.asset_root else None,
            Path(args.schema) if args.schema else None)
    except ValueError as exc:
        print("malformed: {}".format(exc))
        return 2

    if result["ok"]:
        mode = "schema+rules+mechanical" if args.asset_root else "schema+rules"
        print("OK ({}) -- {}".format(mode, args.sidecar))
        return 0
    print("INVALID -- {} ({} finding(s)):".format(args.sidecar, len(result["errors"])))
    for err in result["errors"]:
        print("  - {}".format(err))
    return 1


if __name__ == "__main__":
    sys.exit(_cli())
