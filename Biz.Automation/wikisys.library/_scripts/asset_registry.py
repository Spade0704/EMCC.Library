"""asset_registry.py — Codex asset registry v1.4 CORE (spec §9).

Implements CODEX_BUILD_SPEC_v1_4.md §9 per the Delta Force gate
`EMCC.DFDU/tasks/delta-force/2026-07-21-library-asset-registry-core.md`
(chairman scope items 1-5; retro_ingest / reconcile / snapshot DEFERRED to a
follow-up build per the same gate). Directive:
`dir-20260721-library-asset-registry-core`.

GLOSSARY (load-bearing terms; read before editing)
    commit point   The REGISTRY WRITE — the atomic write of the per-asset
                   frontmatter record at `wiki.<name>/{git|local}/_registry/
                   <AST-ID>.md` (§9.3 step 5). NOT a git commit. Everything
                   before it is preparatory and recoverable; everything after
                   it (index regen, remote-store mint, inbox-slot clear) is
                   post-commit bookkeeping whose drift the §9.6 sweeps catch.
    burned ID      An allocated counter value with no record behind it. A crash
                   between counter persist and record write burns the ID — a
                   permanent, harmless gap. IDs are never reused (§9.2).
    zone           `git` (committed/public) or `local` (gitignored/
                   confidential) under a `wiki.<name>/` root. Records live in
                   the SAME zone as their asset (§9.4); files never change
                   zones during registration.
    inbox slot     The caller-side manifest entry describing one inbox asset.
                   Marked `filed` LAST (§9.3 step 8) — after the commit point
                   and index regen — so a crash anywhere mid-loop leaves the
                   slot uncleared and the re-run resumes it.
    manifest       The JSON file the Librarian populates (route_inbox.py
                   two-phase pattern): semantic fields (class, zone, home,
                   rights, lineage) are the agent's job; this script does the
                   mechanics. The script persists per-entry bookkeeping
                   (sha256, status) back into the manifest; that is working
                   state, NOT the registry.

Filing loop (§9.3; the gate's hardened ordering):

    1. assign ID          (counter persisted BEFORE any record write — §9.2)
    2. resolve intra-batch lineage   (`batch:<index>` refs -> assigned IDs;
                                      deriving from a skipped entry skips the
                                      dependent with the reason CHAINED)
    3. normalize-rename   (readable filename; identity stays on the ID)
    4. ONE move to the role-determined home
       [the §9.4 zone predicate runs BEFORE the move: moving a `zone: local`
        asset under `git/` would itself be the leak the validator exists to
        prevent ("a post-commit check would already be a leak" — §9.4). The
        predicate runs again pre-write as the commit-point gate.]
       Idempotent on retry: destination already holding the identical
       content-hash means the move is done.
    5. REGISTRY WRITE     = the commit point (`url: pending` for deliverables)
    6. per-zone asset-index regen (atomic; git-zone index carries ONLY opaque
       rows — count + AST-IDs — for local-zone content)
    7. remote-store stub  (post-commit; config-gated; not-configured in v1.4
       core — record stays `url: pending`)
    8. inbox slot cleared LAST

Malformed entries flag-and-skip with prose reasons; the batch never chokes.

YAML-subset note (gate change 5 — surfaced, not hidden): record frontmatter is
read/written via the shared `_lib/frontmatter.py` ONLY (no second parser, no
extension). The flat `parse_frontmatter` subset cannot represent the §9.1
nested `source:`/`recipe:` mappings, so records are parsed with the same
module's richer `parse_config_yaml` (2-level nested mappings — fits §9.1).
Residual misfit: recipe VALUES must be scalars; a recipe containing a nested
mapping/list value (e.g. a structured `params:` sub-mapping) does not fit the
shared subset and is REFUSED (flag-and-skip), never silently flattened.
Explicit-empty `recipe: {}` is written inline and normalized to `{}` on read.

CLI (route_inbox.py argparse-verb pattern):

    python asset_registry.py file --root <root> --entry <entry.json>
    python asset_registry.py file --root <root> --batch <manifest.json>
    python asset_registry.py status --root <root>

Exit codes:
    0  all entries filed (or already filed) / status printed
    1  one or more entries flagged or skipped
    2  malformed input (unparseable manifest/entry JSON, wrong shape)
    3  allocator lock unavailable (held or stale — stale is surfaced with
       path + age + pid and NEVER auto-broken)
"""
# @component Codex[asset-registry]

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_LIB = Path(__file__).resolve().parent / "_lib"
if str(_LIB.parent) not in sys.path:
    sys.path.insert(0, str(_LIB.parent))

from _lib.frontmatter import (  # noqa: E402
    find_frontmatter_close,
    parse_config_yaml,
)


# =========================================================================
# Section: constants + schema (§9.1 — field-for-field, verbatim names)
# =========================================================================

# §9.1 record schema, in spec order. Diffed field-for-field against
# CODEX_BUILD_SPEC_v1_4.md §9.1 (17 fields; names verbatim).
RECORD_FIELDS = (
    "id",
    "asset_class",
    "name",
    "description",
    "tags",
    "subject",
    "zone",
    "path",
    "source",
    "rights_consent",
    "derived_from",
    "recipe",
    "version",
    "supersedes",
    "url",
    "created_at",
    "updated_at",
)

# §9.1: mandatory-or-explicitly-empty. A record/entry missing any of these
# keys is malformed (flagged, not written). The tuple per field enumerates
# the EXPLICIT-EMPTY forms; any other present value is a populated value.
# Single source of truth — the validator and the docs both read this table.
REQUIRED_EXPLICIT = {
    "rights_consent": ("", "unknown"),
    "derived_from": ([],),
    "recipe": ({},),
}

ZONES = ("git", "local")

REGISTRY_DIR = "_registry"
COUNTER_FILE = "_counter"
LOCK_FILE = "_counter.lock"
INDEX_FILE = "asset-index.md"

DEFAULT_STALE_LOCK_MINUTES = 15
ID_WIDTH = 5

# Entry statuses persisted into the manifest (the "inbox slot").
STATUS_FILED = "filed"
STATUS_FLAGGED = "flagged"
STATUS_SKIPPED_CHAINED = "skipped-chained"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class EntryError(Exception):
    """Per-entry refusal (flag-and-skip). Message is the prose reason."""


class LockUnavailable(Exception):
    """Allocator lock is held. Carries a LockReport dict as .report."""

    def __init__(self, report: Dict[str, Any]):
        super().__init__(report.get("detail", "lock unavailable"))
        self.report = report


# =========================================================================
# Section: atomic write primitive (temp -> fsync -> os.replace)
# =========================================================================

def atomic_write_text(path: Path, text: str) -> None:
    """Write `text` to `path` atomically: temp file in the same directory,
    flush + fsync, then os.replace. Used for the counter, every record,
    and every index regen (gate: records/indexes are a durability surface
    too, not just the counter)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, str(path))
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


# =========================================================================
# Section: config (_config/asset_registry.yaml via parse_config_yaml)
# =========================================================================

def load_registry_config(root: Path, override: Optional[Path] = None) -> Dict[str, Any]:
    """Resolve + parse `_config/asset_registry.yaml`.

    Resolution order: explicit override -> consumer-side
    `<root>/Biz.Automation/wikisys.*/_config/` (audit-script glob pattern)
    -> the kit copy next to this script. Missing everywhere -> EntryError
    (the vocabulary is config-only per §9.1; there is no code fallback)."""
    candidates: List[Path] = []
    if override is not None:
        candidates.append(override)
    else:
        for wikisys in sorted(root.glob("Biz.Automation/wikisys.*")):
            candidates.append(wikisys / "_config" / "asset_registry.yaml")
        candidates.append(
            Path(__file__).resolve().parent.parent / "_config" / "asset_registry.yaml"
        )
    for candidate in candidates:
        if candidate.is_file():
            config = parse_config_yaml(candidate.read_text(encoding="utf-8"))
            config["_config_path"] = str(candidate)
            return config
    raise EntryError(
        "asset_registry.yaml not found (looked at: {})".format(
            ", ".join(str(c) for c in candidates)
        )
    )


def config_asset_classes(config: Dict[str, Any]) -> List[str]:
    classes = config.get("asset_classes")
    if not isinstance(classes, list) or not classes:
        raise EntryError(
            "asset_classes missing/empty in {} — the asset_class vocabulary "
            "is config-only (spec §9.1)".format(config.get("_config_path", "config"))
        )
    return [str(c) for c in classes]


def config_stale_minutes(config: Dict[str, Any]) -> int:
    allocator = config.get("allocator")
    if isinstance(allocator, dict):
        value = allocator.get("stale_lock_minutes")
        if isinstance(value, int) and value > 0:
            return value
    return DEFAULT_STALE_LOCK_MINUTES


# =========================================================================
# Section: wiki/zone geometry
# =========================================================================

def split_wiki_dest(root: Path, dest_dir: str) -> Tuple[Path, str, str, Path]:
    """Resolve a root-relative destination dir to (wiki_root, wiki_name,
    zone, abs_dest_dir). The destination must be `wiki.<name>/{git|local}/...`.
    Raises EntryError otherwise (prose reason)."""
    parts = Path(dest_dir).parts
    if len(parts) < 2 or not parts[0].startswith("wiki."):
        raise EntryError(
            "destination '{}' is not under a wiki zone "
            "(expected wiki.<name>/git/... or wiki.<name>/local/...)".format(dest_dir)
        )
    if parts[1] not in ZONES:
        raise EntryError(
            "destination '{}' zone segment '{}' is not one of {}".format(
                dest_dir, parts[1], "/".join(ZONES)
            )
        )
    wiki_root = root / parts[0]
    abs_dest = root / Path(dest_dir)
    if not _within(abs_dest, root):
        raise EntryError("destination '{}' escapes root {}".format(dest_dir, root))
    return wiki_root, parts[0][len("wiki."):], parts[1], abs_dest


def _within(candidate: Path, root: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def project_slug(wiki_name: str) -> str:
    """§9.2: the wiki's project slug, uppercased. Characters outside
    [A-Z0-9.] map to '-' so the slug stays filename- and ID-safe."""
    out = []
    for ch in wiki_name.upper():
        out.append(ch if (ch.isalnum() or ch == ".") else "-")
    return "".join(out)


def zone_of(wiki_root: Path, path: Path) -> Optional[str]:
    """The actual on-disk zone of `path` under `wiki_root`, or None."""
    try:
        rel = path.resolve().relative_to(wiki_root.resolve())
    except ValueError:
        return None
    if rel.parts and rel.parts[0] in ZONES:
        return rel.parts[0]
    return None


def validate_zone(wiki_root: Path, zone: str, asset_path: Path,
                  record_path: Path) -> Tuple[bool, str]:
    """§9.4 pre-commit-point predicate. The record's declared `zone` must
    equal the asset's actual on-disk zone AND the record path must resolve
    under that same zone. `zone: local` under `git/` fails the entry."""
    if zone not in ZONES:
        return False, "zone '{}' is not one of {}".format(zone, "/".join(ZONES))
    actual_asset_zone = zone_of(wiki_root, asset_path)
    if actual_asset_zone != zone:
        return False, (
            "declared zone '{}' does not match the asset's actual on-disk "
            "zone '{}' for {}".format(zone, actual_asset_zone, asset_path)
        )
    actual_record_zone = zone_of(wiki_root, record_path)
    if actual_record_zone != zone:
        return False, (
            "record path {} does not resolve under the '{}' zone".format(
                record_path, zone
            )
        )
    return True, ""


# =========================================================================
# Section: allocator (§9.2, hardened per gate change 1)
# =========================================================================

def registry_dir(wiki_root: Path, zone: str) -> Path:
    return wiki_root / zone / REGISTRY_DIR


def counter_path(wiki_root: Path) -> Path:
    return registry_dir(wiki_root, "git") / COUNTER_FILE


def lock_path(wiki_root: Path) -> Path:
    return registry_dir(wiki_root, "git") / LOCK_FILE


def describe_lock(wiki_root: Path, now: datetime,
                  stale_minutes: int) -> Optional[Dict[str, Any]]:
    """Inspect the lockfile. None when free; else a report dict with
    path / pid / age_minutes / stale / detail. Stale locks are SURFACED,
    never auto-broken (§9.2)."""
    lock = lock_path(wiki_root)
    if not lock.exists():
        return None
    pid: Any = "unknown"
    age_minutes: Any = "unknown"
    stale = False
    try:
        fields = lock.read_text(encoding="utf-8").split()
        if fields:
            pid = fields[0]
        if len(fields) > 1:
            held_since = datetime.fromisoformat(fields[1])
            if held_since.tzinfo is None:
                held_since = held_since.replace(tzinfo=timezone.utc)
            age_minutes = round((now - held_since).total_seconds() / 60.0, 1)
            stale = age_minutes > stale_minutes
    except (OSError, ValueError):
        pass  # unreadable lock -> reported with unknown age; still never broken
    if stale:
        detail = (
            "STALE LOCK surfaced (never auto-broken): {} age={}min pid={}. "
            "If the owning process is dead, the operator removes the lockfile "
            "manually.".format(lock, age_minutes, pid)
        )
    else:
        detail = "allocator lock held: {} age={}min pid={}".format(
            lock, age_minutes, pid
        )
    return {
        "path": str(lock),
        "pid": pid,
        "age_minutes": age_minutes,
        "stale": stale,
        "detail": detail,
    }


def acquire_lock(wiki_root: Path, now: datetime, stale_minutes: int) -> Path:
    """O_EXCL-create the lockfile (contents: pid + ISO timestamp). If it
    already exists, raise LockUnavailable carrying the surfaced report —
    stale or not, this function NEVER breaks an existing lock."""
    lock = lock_path(wiki_root)
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        report = describe_lock(wiki_root, now, stale_minutes)
        if report is None:  # released between exists-check and read
            report = {"path": str(lock), "pid": "unknown",
                      "age_minutes": "unknown", "stale": False,
                      "detail": "allocator lock contended: {}".format(lock)}
        raise LockUnavailable(report)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write("{} {}\n".format(os.getpid(), now.isoformat()))
        handle.flush()
        os.fsync(handle.fileno())
    return lock


def release_lock(wiki_root: Path) -> None:
    try:
        lock_path(wiki_root).unlink()
    except FileNotFoundError:
        pass


def _scan_max_id(wiki_root: Path) -> int:
    """RECOVERY ONLY (§9.2 / gate change 1): scan both zones' `_registry/
    AST-*.md` for the max numeric suffix. Routine allocation reads the
    counter; this runs only when the counter is missing or corrupt."""
    highest = 0
    for zone in ZONES:
        directory = registry_dir(wiki_root, zone)
        if not directory.is_dir():
            continue
        for record in directory.glob("AST-*.md"):
            tail = record.stem.rsplit("-", 1)[-1]
            if tail.isdigit():
                highest = max(highest, int(tail))
    return highest


def read_counter(wiki_root: Path) -> Tuple[int, Optional[str]]:
    """Read the high-water counter. Returns (value, recovery_note).
    recovery_note is None on the routine path; on a missing/corrupt counter
    the value comes from the registry scan and the note says so."""
    path = counter_path(wiki_root)
    if not path.exists():
        recovered = _scan_max_id(wiki_root)
        if recovered == 0:
            return 0, None  # fresh registry init, not a recovery
        return recovered, (
            "counter missing at {} — RECOVERED high-water {} by scanning both "
            "zones' _registry/AST-*.md (recovery only, never routine)".format(
                path, recovered
            )
        )
    text = path.read_text(encoding="utf-8").strip()
    if not text.isdigit():
        recovered = _scan_max_id(wiki_root)
        return recovered, (
            "counter corrupt at {} (contents {!r}) — RECOVERED high-water {} "
            "by scanning both zones' _registry/AST-*.md".format(
                path, text[:40], recovered
            )
        )
    return int(text), None


def allocate_ids(wiki_root: Path, wiki_name: str, count: int, now: datetime,
                 stale_minutes: int) -> Tuple[List[str], Optional[str]]:
    """Allocate `count` IDs under the lock. Assign-then-commit (§9.2): the
    counter is persisted (atomic temp->fsync->replace) BEFORE this returns,
    hence before any record write. A crash after this burns the IDs — it can
    never duplicate one. Returns (ids, recovery_note)."""
    acquire_lock(wiki_root, now, stale_minutes)
    try:
        value, recovery_note = read_counter(wiki_root)
        new_value = value + count
        atomic_write_text(counter_path(wiki_root), "{}\n".format(new_value))
        slug = project_slug(wiki_name)
        ids = [
            "AST-{}-{:0{}d}".format(slug, value + offset + 1, ID_WIDTH)
            for offset in range(count)
        ]
        return ids, recovery_note
    finally:
        release_lock(wiki_root)


# =========================================================================
# Section: record store (§9.1 via shared _lib/frontmatter.py; gate change 2)
# =========================================================================

def _fm_scalar(value: Any, field: str) -> str:
    """Serialize one scalar for record frontmatter, safely within the shared
    parser's subset. Strings are always quoted (hostile names: colons,
    hashes, brackets, leading dashes all survive inside quotes). A string
    holding BOTH quote characters, or a newline, is not representable in
    the subset -> EntryError (flag, never mangle)."""
    if value is None:
        return "~"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if "\n" in text or "\r" in text:
        raise EntryError(
            "field '{}' contains a newline — not representable in the "
            "frontmatter subset".format(field)
        )
    if '"' not in text:
        return '"{}"'.format(text)
    if "'" not in text:
        return "'{}'".format(text)
    raise EntryError(
        "field '{}' contains both quote characters — not representable in "
        "the frontmatter subset".format(field)
    )


def _fm_bare(value: str, field: str) -> str:
    """Serialize an enum-ish bare scalar (id / zone / url / asset_class).
    An empty string must be quoted — a bare `key:` would parse as an empty
    list under the shared config parser, not an empty string."""
    text = str(value)
    if text == "":
        return '""'
    for hostile in (":", "#", '"', "'", "\n", "[", "]", "{", "}"):
        if hostile in text:
            return _fm_scalar(text, field)
    return text


def _fm_list(values: List[Any], field: str) -> str:
    return "[{}]".format(", ".join(_fm_scalar(v, field) for v in values))


def _fm_mapping_lines(key: str, mapping: Dict[str, Any]) -> List[str]:
    """Serialize a §9.1 mapping field (`source`, `recipe`) as a 2-level
    block mapping — the shape the shared `parse_config_yaml` supports.
    Empty mapping -> inline `key: {}` (explicit-empty form, normalized back
    to {} on read). A nested mapping/list VALUE does not fit the shared
    subset -> EntryError (the surfaced residual misfit; module docstring)."""
    if not mapping:
        return ["{}: {{}}".format(key)]
    lines = ["{}:".format(key)]
    for subkey, subvalue in mapping.items():
        if isinstance(subvalue, (dict, list)):
            raise EntryError(
                "field '{}.{}' is a nested {} — structured sub-values do not "
                "fit the shared frontmatter subset (v1.4-core restriction; "
                "flagged, never flattened)".format(
                    key, subkey, type(subvalue).__name__
                )
            )
        lines.append("  {}: {}".format(subkey, _fm_scalar(subvalue, key + "." + subkey)))
    return lines


def render_record(record: Dict[str, Any]) -> str:
    """Render a §9.1 record (frontmatter + human-readable stub body).
    Every RECORD_FIELDS key is emitted, in spec order."""
    missing = [f for f in RECORD_FIELDS if f not in record]
    if missing:
        raise EntryError("record missing schema fields: {}".format(", ".join(missing)))
    lines = ["---"]
    for field in RECORD_FIELDS:
        value = record[field]
        if field in ("source", "recipe"):
            lines.extend(_fm_mapping_lines(field, value or {}))
        elif field in ("tags", "derived_from"):
            lines.append("{}: {}".format(field, _fm_list(value or [], field)))
        elif field in ("id", "zone", "url", "asset_class"):
            lines.append("{}: {}".format(field, _fm_bare(value, field)))
        elif field == "version":
            lines.append("{}: {}".format(field, int(value)))
        else:
            lines.append("{}: {}".format(field, _fm_scalar(value, field)))
    lines.append("---")
    lines.append("")
    lines.append("# {}".format(record["id"]))
    lines.append("")
    lines.append(
        "Asset record (CODEX_BUILD_SPEC_v1_4 §9.1). The frontmatter above is "
        "the authoritative ledger entry; this body is a human-readable stub. "
        "Written by asset_registry.py — the Librarian is the sole writer."
    )
    lines.append("")
    return "\n".join(lines)


def parse_record(path: Path) -> Dict[str, Any]:
    """Parse a record file via the shared lib (parse_config_yaml on the
    frontmatter block; module docstring explains why not parse_frontmatter).
    Normalizes the explicit-empty forms: '{}' -> {}, missing-block None -> {}."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    close = find_frontmatter_close(lines)
    if close is None:
        raise EntryError("record {} has no frontmatter block".format(path))
    data = parse_config_yaml("\n".join(lines[1:close]))
    for field in ("source", "recipe"):
        value = data.get(field)
        if value == "{}" or value is None or value == []:
            data[field] = {}
    for field in ("tags", "derived_from"):
        if data.get(field) is None:
            data[field] = []
    return data


def write_record_atomic(record_path: Path, record: Dict[str, Any]) -> None:
    """THE COMMIT POINT (§9.3 step 5). Atomic temp->fsync->replace write of
    the record. Refuses to overwrite an existing record (fresh IDs never
    collide; an existing file means something is wrong — surfaced, not
    clobbered)."""
    if record_path.exists():
        raise EntryError(
            "record path {} already exists — refusing to overwrite".format(record_path)
        )
    atomic_write_text(record_path, render_record(record))


def load_zone_records(wiki_root: Path, zone: str) -> List[Dict[str, Any]]:
    records = []
    directory = registry_dir(wiki_root, zone)
    if not directory.is_dir():
        return records
    for path in sorted(directory.glob("AST-*.md")):
        try:
            records.append(parse_record(path))
        except (EntryError, OSError):
            continue  # index regen never chokes on one bad record
    return records


# =========================================================================
# Section: per-zone index regen (opaque git-zone pointer rows; gate change 3)
# =========================================================================

def render_index(zone: str, records: List[Dict[str, Any]],
                 local_ids: Optional[List[str]] = None,
                 wiki_dir_name: str = "") -> str:
    lines = [
        "# Asset Index — {} zone".format(zone),
        "",
        "Generated by `asset_registry.py` (spec §9). Do not hand-edit.",
        "",
    ]
    if records:
        lines.append("| ID | Class | Name | Path |")
        lines.append("|---|---|---|---|")
        for record in records:
            lines.append("| {} | {} | {} | `{}` |".format(
                record.get("id", "?"),
                record.get("asset_class", "?"),
                str(record.get("name", "")).replace("|", "\\|"),
                str(record.get("path", "")).replace("|", "\\|"),
            ))
        lines.append("")
    else:
        lines.append("No {}-zone records.".format(zone))
        lines.append("")
    if zone == "git":
        # §9.4: the committed index references local content ONLY as opaque
        # pointer rows — count + AST-IDs. NO filenames, names, descriptions.
        lines.append("## Local-zone assets (opaque pointer rows)")
        lines.append("")
        ids = local_ids or []
        lines.append(
            "{} local-zone asset(s) — item-level metadata lives in "
            "`{}/local/_registry/{}` (gitignored).".format(
                len(ids), wiki_dir_name or "wiki.<name>", INDEX_FILE
            )
        )
        for asset_id in ids:
            lines.append("- {}".format(asset_id))
        lines.append("")
    return "\n".join(lines)


def regenerate_indexes(wiki_root: Path) -> None:
    """Regenerate both zones' `_registry/asset-index.md` atomically.
    Post-commit bookkeeping (§9.3 step 6)."""
    git_records = load_zone_records(wiki_root, "git")
    local_records = load_zone_records(wiki_root, "local")
    local_ids = [str(r.get("id", "?")) for r in local_records]
    atomic_write_text(
        registry_dir(wiki_root, "git") / INDEX_FILE,
        render_index("git", git_records, local_ids=local_ids,
                     wiki_dir_name=wiki_root.name),
    )
    if local_records or registry_dir(wiki_root, "local").is_dir():
        atomic_write_text(
            registry_dir(wiki_root, "local") / INDEX_FILE,
            render_index("local", local_records),
        )


# =========================================================================
# Section: remote_store stub (§9.7 — config-gated dead code, ZERO network
# imports; the transport decision belongs to a later build gate / OP-5)
# =========================================================================

def remote_store_mint(config: Dict[str, Any],
                      record: Dict[str, Any]) -> Dict[str, str]:
    """Config-gated stub. v1.4 core ships NO transport (and imports no
    network module); the record legitimately stays at `url: pending`
    (§9.3 step 7 is post-commit + skippable-with-flag)."""
    remote = config.get("remote_store")
    if not isinstance(remote, dict) or not remote.get("enabled"):
        return {
            "status": "not-configured",
            "detail": "remote_store disabled in config; {} stays url: pending".format(
                record.get("id", "?")
            ),
        }
    return {
        "status": "not-configured",
        "detail": (
            "remote_store enabled in config but v1.4 core ships no transport "
            "(deferred to the implementing build gate / Herald OP-5); {} stays "
            "url: pending".format(record.get("id", "?"))
        ),
    }


# =========================================================================
# Section: filing loop (§9.3; gate changes 1/2/6)
# =========================================================================

def normalize_filename(name: str, source: Path) -> str:
    """§9.3 step 3 normalize-rename: readable filename from the human name
    (identity stays on the ID). Lowercase, alnum + dash, source extension
    preserved. Falls back to the source stem when the name yields nothing."""
    base = str(name or "")
    out = []
    previous_dash = True
    for ch in base.lower():
        if ch.isalnum():
            out.append(ch)
            previous_dash = False
        elif not previous_dash:
            out.append("-")
            previous_dash = True
    slug = "".join(out).strip("-")
    if not slug:
        fallback = []
        for ch in source.stem.lower():
            fallback.append(ch if ch.isalnum() else "-")
        slug = "".join(fallback).strip("-") or "asset"
    return slug + source.suffix.lower()


def _entry_structural_reason(entry: Dict[str, Any],
                             classes: List[str]) -> Optional[str]:
    """Prose reason an entry is malformed, or None. REQUIRED_EXPLICIT is
    enforced here: the key must be PRESENT; explicit-empty forms are legal."""
    if not isinstance(entry, dict):
        return "entry is not a JSON object"
    if not entry.get("source"):
        return "missing source path"
    if not entry.get("dest_dir"):
        return "missing dest_dir (the role-determined home)"
    asset_class = entry.get("asset_class")
    if not asset_class:
        return "missing asset_class"
    if asset_class not in classes:
        return "asset_class '{}' not in the config vocabulary ({})".format(
            asset_class, ", ".join(classes)
        )
    if entry.get("zone") not in ZONES:
        return "zone '{}' is not one of {}".format(entry.get("zone"), "/".join(ZONES))
    for field in REQUIRED_EXPLICIT:
        if field not in entry:
            return (
                "missing {} — mandatory-or-explicitly-empty (§9.1); explicit "
                "empty form(s): {!r}".format(field, REQUIRED_EXPLICIT[field])
            )
    if not isinstance(entry.get("derived_from"), list):
        return "derived_from must be a list ([] = verified root asset)"
    if not isinstance(entry.get("recipe"), dict):
        return "recipe must be a mapping ({} = no known generation data)"
    return None


def _move_asset(source: Path, dest: Path, expected_sha: str) -> str:
    """§9.3 step 4: ONE move, idempotent on retry.

    - dest holds identical content-hash -> move already done (a lingering
      source copy is removed); returns 'already-moved'.
    - dest holds DIFFERENT content -> collision REFUSAL (EntryError; never
      overwrite).
    - else copy temp->fsync->replace into dest, then remove source.
    """
    if dest.exists():
        if _sha256_file(dest) == expected_sha:
            if source.exists():
                source.unlink()
            return "already-moved"
        raise EntryError(
            "destination {} already holds different content — refusing to "
            "overwrite (rename collision)".format(dest)
        )
    if not source.exists():
        raise EntryError(
            "source {} missing and destination {} absent — nothing to move "
            "(possible partial state; see §9.6 sweeps)".format(source, dest)
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=dest.name + ".", suffix=".tmp",
                                    dir=str(dest.parent))
    os.close(fd)
    try:
        shutil.copyfile(str(source), tmp_name)
        with open(tmp_name, "rb") as handle:
            os.fsync(handle.fileno())
        os.replace(tmp_name, str(dest))
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
    source.unlink()
    return "moved"


def _persist_manifest(manifest_path: Optional[Path],
                      entries: List[Dict[str, Any]], single: bool) -> None:
    if manifest_path is None:
        return
    cleaned = [
        {k: v for k, v in entry.items() if not k.startswith("_")}
        for entry in entries
    ]
    payload: Any = cleaned[0] if single else cleaned
    atomic_write_text(manifest_path, json.dumps(payload, indent=2) + "\n")


def file_inbox(root: Path, entries: List[Dict[str, Any]],
               config: Dict[str, Any],
               manifest_path: Optional[Path] = None,
               single: bool = False,
               now_fn=None) -> Dict[str, Any]:
    """The §9.3 filing loop over a batch of inbox-slot entries.

    Returns a report dict: {filed, flagged, skipped, already, lock_reports,
    lines, recovery_notes}. Mutates `entries` in place with per-slot status
    and persists them back to `manifest_path` (slot cleared LAST per entry).
    `now_fn` is injectable for tests (lock staleness / timestamps)."""
    now_fn = now_fn or _now_utc
    classes = config_asset_classes(config)
    stale_minutes = config_stale_minutes(config)
    report: Dict[str, Any] = {
        "filed": 0, "flagged": 0, "skipped": 0, "already": 0,
        "lock_reports": [], "lines": [], "recovery_notes": [],
    }

    def flag(entry: Dict[str, Any], reason: str, chained: bool = False) -> None:
        entry["status"] = STATUS_SKIPPED_CHAINED if chained else STATUS_FLAGGED
        entry["reason"] = reason
        key = "skipped" if chained else "flagged"
        report[key] += 1
        label = "skipped (chained)" if chained else "flagged"
        report["lines"].append("  {} ({}): {}".format(
            label, reason, entry.get("source", "?")))

    # ---- pre-pass: statuses + structural validation (no IDs consumed) ----
    active: List[int] = []
    for index, entry in enumerate(entries):
        if entry.get("status") == STATUS_FILED:
            report["already"] += 1
            report["lines"].append("  already filed as {}: {}".format(
                entry.get("id", "?"), entry.get("source", "?")))
            continue
        entry.pop("status", None)
        entry.pop("reason", None)
        reason = _entry_structural_reason(entry, classes)
        if reason is not None:
            flag(entry, reason)
            continue
        try:
            wiki_root, wiki_name, zone, abs_dest_dir = split_wiki_dest(
                root, str(entry["dest_dir"]))
        except EntryError as exc:
            flag(entry, str(exc))
            continue
        entry["_wiki_root"] = wiki_root
        entry["_wiki_name"] = wiki_name
        entry["_abs_dest_dir"] = abs_dest_dir
        active.append(index)

    # ---- step 1: assign IDs per wiki group (assign-then-commit) ----
    groups: Dict[Path, List[int]] = {}
    for index in active:
        groups.setdefault(entries[index]["_wiki_root"], []).append(index)
    allocated: List[int] = []
    for wiki_root, indexes in groups.items():
        try:
            ids, recovery_note = allocate_ids(
                wiki_root, entries[indexes[0]]["_wiki_name"], len(indexes),
                now_fn(), stale_minutes)
        except LockUnavailable as exc:
            report["lock_reports"].append(exc.report)
            for index in indexes:
                flag(entries[index],
                     "allocator unavailable — " + exc.report["detail"])
            continue
        if recovery_note:
            report["recovery_notes"].append(recovery_note)
        for index, asset_id in zip(indexes, ids):
            entries[index]["id"] = asset_id
            allocated.append(index)

    # ---- step 2: resolve intra-batch lineage (chained skip; gate change 6) ----
    for index in sorted(allocated):
        entry = entries[index]
        resolved: List[str] = []
        for ref in entry.get("derived_from", []):
            ref_str = str(ref)
            if ref_str.startswith("batch:"):
                tail = ref_str[len("batch:"):]
                if not tail.isdigit() or int(tail) >= len(entries):
                    flag(entry, "derived_from ref '{}' does not name a batch "
                                "entry".format(ref_str))
                    break
                target = entries[int(tail)]
                if target.get("status") in (STATUS_FLAGGED, STATUS_SKIPPED_CHAINED):
                    flag(entry,
                         "derives from skipped entry #{} (its reason: {})".format(
                             tail, target.get("reason", "unknown")),
                         chained=True)
                    break
                if not target.get("id"):
                    flag(entry, "derives from entry #{} which has no assigned "
                                "ID".format(tail), chained=True)
                    break
                resolved.append(str(target["id"]))
            else:
                resolved.append(ref_str)
        else:
            entry["derived_from"] = resolved
            continue

    # ---- steps 3-8 per entry ----
    for index in sorted(allocated):
        entry = entries[index]
        if entry.get("status") in (STATUS_FLAGGED, STATUS_SKIPPED_CHAINED):
            continue
        wiki_root: Path = entry["_wiki_root"]
        zone = str(entry["zone"])
        try:
            source = (root / str(entry["source"])).resolve()
            if not _within(source, root):
                raise EntryError("source '{}' escapes root {}".format(
                    entry["source"], root))
            # step 3: normalize-rename
            filename = normalize_filename(str(entry.get("name", "")), source)
            dest = entry["_abs_dest_dir"] / filename
            record_path = registry_dir(wiki_root, zone) / (entry["id"] + ".md")
            # §9.4 predicate BEFORE the move (leak prevention; module docstring)
            ok, why = validate_zone(wiki_root, zone, dest, record_path)
            if not ok:
                raise EntryError("zone validator: " + why)
            # bookkeeping: persist content hash into the slot pre-move so a
            # crash between move and commit point resumes verifiably
            if source.exists():
                entry["sha256"] = _sha256_file(source)
                _persist_manifest(manifest_path, entries, single)
            expected_sha = entry.get("sha256")
            if not expected_sha:
                raise EntryError(
                    "source {} missing and no recorded sha256 to verify a "
                    "prior move against".format(source))
            # step 4: ONE move (idempotent on retry)
            _move_asset(source, dest, expected_sha)
            # §9.4 predicate again as the commit-point gate
            ok, why = validate_zone(wiki_root, zone, dest, record_path)
            if not ok:
                raise EntryError("zone validator (pre-commit): " + why)
            # step 5: REGISTRY WRITE = COMMIT POINT
            timestamp = now_fn().isoformat()
            record = {
                "id": entry["id"],
                "asset_class": entry["asset_class"],
                "name": str(entry.get("name", "")),
                "description": str(entry.get("description", "")),
                "tags": list(entry.get("tags", []) or []),
                "subject": str(entry.get("subject", "")),
                "zone": zone,
                "path": dest.relative_to(root).as_posix(),
                "source": {
                    "by": str(entry.get("source_by", "")),
                    "date": str(entry.get("source_date", "")),
                },
                "rights_consent": entry["rights_consent"],
                "derived_from": list(entry.get("derived_from", [])),
                "recipe": dict(entry.get("recipe", {}) or {}),
                "version": int(entry.get("version", 1) or 1),
                "supersedes": str(entry.get("supersedes", "")),
                "url": "pending" if entry["asset_class"] == "deliverable" else "",
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            write_record_atomic(record_path, record)
            # step 6: index regen (post-commit bookkeeping)
            regenerate_indexes(wiki_root)
            # step 7: remote-store stub (post-commit; skippable-with-flag)
            if entry["asset_class"] == "deliverable":
                mint = remote_store_mint(config, record)
                report["lines"].append("  remote-store ({}): {}".format(
                    mint["status"], mint["detail"]))
            # step 8: inbox slot cleared LAST
            entry["status"] = STATUS_FILED
            entry["reason"] = ""
            report["filed"] += 1
            report["lines"].append("  {} <- {} -> {}".format(
                entry["id"], entry.get("source", "?"),
                dest.relative_to(root).as_posix()))
            _persist_manifest(manifest_path, entries, single)
        except EntryError as exc:
            flag(entry, str(exc))
            _persist_manifest(manifest_path, entries, single)

    for entry in entries:  # drop private working keys before final persist
        for key in ("_wiki_root", "_wiki_name", "_abs_dest_dir"):
            entry.pop(key, None)
    _persist_manifest(manifest_path, entries, single)
    return report


# =========================================================================
# Section: CLI (route_inbox.py argparse-verb pattern; prose echoes,
# no tracebacks to users)
# =========================================================================

def _load_entries(path: Path) -> Tuple[List[Dict[str, Any]], bool]:
    """Load a single-entry JSON object or a batch list. Returns
    (entries, single). Raises ValueError with a prose reason on bad shape."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return [data], True
    if isinstance(data, list):
        if not all(isinstance(item, dict) for item in data):
            raise ValueError("batch manifest items must all be JSON objects")
        return data, False
    raise ValueError("manifest must be a JSON object (single) or list (batch)")


def _cmd_file(args) -> int:
    root = args.root.resolve()
    manifest_path = (args.entry or args.batch).resolve()
    try:
        entries, single = _load_entries(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write("error: cannot read entries from {}: {}\n".format(
            manifest_path, exc))
        return 2
    try:
        config = load_registry_config(root, args.config)
    except EntryError as exc:
        sys.stderr.write("error: {}\n".format(exc))
        return 2
    report = file_inbox(root, entries, config, manifest_path=manifest_path,
                        single=single)
    for note in report["recovery_notes"]:
        sys.stdout.write("note: {}\n".format(note))
    for lock in report["lock_reports"]:
        sys.stdout.write("{}\n".format(lock["detail"]))
    summary = "{} filed, {} flagged, {} skipped (chained), {} already filed".format(
        report["filed"], report["flagged"], report["skipped"], report["already"])
    sys.stdout.write(summary + "\n")
    for line in report["lines"]:
        sys.stdout.write(line + "\n")
    if report["lock_reports"] and report["filed"] == 0:
        return 3
    return 1 if (report["flagged"] or report["skipped"]) else 0


def _cmd_status(args) -> int:
    root = args.root.resolve()
    try:
        config = load_registry_config(root, args.config)
    except EntryError:
        config = {}
    stale_minutes = config_stale_minutes(config) if config else DEFAULT_STALE_LOCK_MINUTES
    wikis = [w for w in sorted(root.glob("wiki.*")) if w.is_dir()]
    if not wikis:
        sys.stdout.write("no wiki.*/ under {}\n".format(root))
        return 0
    now = _now_utc()
    for wiki_root in wikis:
        counter_file = counter_path(wiki_root)
        if not counter_file.exists() and not any(
                registry_dir(wiki_root, z).is_dir() for z in ZONES):
            continue  # wiki without a registry: stay quiet
        value, recovery_note = read_counter(wiki_root)
        sys.stdout.write("{}:\n".format(wiki_root.name))
        sys.stdout.write("  counter: {}{}\n".format(
            value, "  [RECOVERED — see note]" if recovery_note else ""))
        if recovery_note:
            sys.stdout.write("  note: {}\n".format(recovery_note))
        lock = describe_lock(wiki_root, now, stale_minutes)
        sys.stdout.write("  lock: {}\n".format(
            lock["detail"] if lock else "free"))
        for zone in ZONES:
            records = load_zone_records(wiki_root, zone)
            pending = sum(1 for r in records if r.get("url") == "pending")
            sys.stdout.write("  {} zone: {} record(s), {} pending mint(s)\n".format(
                zone, len(records), pending))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="asset_registry.py")
    sub = parser.add_subparsers(dest="verb", required=True)

    file_p = sub.add_parser(
        "file", help="File inbox asset(s) into the registry (§9.3 loop).")
    file_p.add_argument("--root", type=Path, default=Path.cwd())
    file_p.add_argument("--config", type=Path, default=None)
    group = file_p.add_mutually_exclusive_group(required=True)
    group.add_argument("--entry", type=Path, help="Single-asset entry JSON.")
    group.add_argument("--batch", type=Path, help="Batch manifest JSON list.")

    status_p = sub.add_parser(
        "status", help="Report counter / lock / record counts per wiki.")
    status_p.add_argument("--root", type=Path, default=Path.cwd())
    status_p.add_argument("--config", type=Path, default=None)

    args = parser.parse_args(argv)
    try:
        if args.verb == "file":
            return _cmd_file(args)
        return _cmd_status(args)
    except Exception as exc:  # no tracebacks to users
        sys.stderr.write("error: {}: {}\n".format(type(exc).__name__, exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
