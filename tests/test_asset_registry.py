"""Tests for asset_registry.py (Codex spec §9 v1.4 CORE).

Built per the Delta Force gate
`EMCC.DFDU/tasks/delta-force/2026-07-21-library-asset-registry-core.md`:
tmp-fixture wikis, injected clock, invariant-named tests. The gate-mandated
first test is `test_crash_between_move_and_registry_write_resumes_idempotently`.
"""

import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parent.parent
WIKISYS_SCRIPTS = REPO_ROOT / "Biz.Automation" / "wikisys.library" / "_scripts"
if str(WIKISYS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(WIKISYS_SCRIPTS))

import asset_registry  # noqa: E402
import sync_from_kit  # noqa: E402


CONFIG_TEXT = """\
asset_classes:
  - ugc
  - professional-photo
  - brand
  - credential
  - deliverable

allocator:
  stale_lock_minutes: 15

remote_store:
  enabled: false
  backend: ~
"""

WIKI = "testproj"
T0 = datetime(2026, 7, 21, 12, 0, 0, tzinfo=timezone.utc)


def _make_root(tmp):
    root = Path(tmp).resolve()
    (root / ("wiki." + WIKI) / "git").mkdir(parents=True)
    (root / ("wiki." + WIKI) / "local").mkdir(parents=True)
    (root / "0-Inbox").mkdir()
    config_dir = root / "Biz.Automation" / ("wikisys." + WIKI) / "_config"
    config_dir.mkdir(parents=True)
    (config_dir / "asset_registry.yaml").write_text(CONFIG_TEXT, encoding="utf-8")
    return root


def _config(root):
    return asset_registry.load_registry_config(root)


def _entry(root, filename="photo one.jpg", content=b"jpegdata",
           zone="local", **overrides):
    src = root / "0-Inbox" / filename
    src.write_bytes(content)
    entry = {
        "source": "0-Inbox/" + filename,
        "dest_dir": "wiki.{}/{}/assets".format(WIKI, zone),
        "asset_class": "ugc",
        "name": "Photo One",
        "description": "a test asset",
        "tags": ["t1"],
        "subject": "subject",
        "zone": zone,
        "rights_consent": "unknown",
        "derived_from": [],
        "recipe": {},
        "source_by": "jp",
        "source_date": "2026-07-21",
    }
    entry.update(overrides)
    return entry


def _wiki_root(root):
    return root / ("wiki." + WIKI)


def _records(root, zone):
    reg = asset_registry.registry_dir(_wiki_root(root), zone)
    if not reg.is_dir():
        return []
    return sorted(reg.glob("AST-*.md"))


def _all_record_ids(root):
    ids = []
    for zone in ("git", "local"):
        for path in _records(root, zone):
            ids.append(path.stem)
    return ids


def _counter(root):
    return int(asset_registry.counter_path(_wiki_root(root))
               .read_text(encoding="utf-8").strip())


def _run_batch(root, entries, manifest_path=None, now_fn=None):
    return asset_registry.file_inbox(
        root, entries, _config(root), manifest_path=manifest_path,
        now_fn=now_fn or (lambda: T0))


class TestCrashResume(unittest.TestCase):
    """Gate-mandated crash-consistency matrix (§9.2/§9.3)."""

    def test_crash_between_move_and_registry_write_resumes_idempotently(self):
        # Kill after the file move, before the record commit; the re-run must
        # complete filing with no duplicate mint, no data loss, and
        # counter >= max registered ID.
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            manifest = root / "manifest.json"
            entries = [_entry(root, content=b"payload-bytes")]
            manifest.write_text(json.dumps(entries), encoding="utf-8")
            with mock.patch.object(asset_registry, "write_record_atomic",
                                   side_effect=RuntimeError("simulated crash")):
                with self.assertRaises(RuntimeError):
                    _run_batch(root, entries, manifest_path=manifest)
            dest = root / "wiki.{}/local/assets/photo-one.jpg".format(WIKI)
            self.assertTrue(dest.exists(), "move happened before the crash")
            self.assertEqual(_all_record_ids(root), [], "no record committed")
            self.assertEqual(_counter(root), 1, "ID 1 allocated then burned")
            # Resume: reload the persisted manifest (the uncleared inbox slot).
            resumed = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(resumed[0].get("sha256"),
                            "content hash persisted pre-move for resume")
            report = _run_batch(root, resumed, manifest_path=manifest)
            self.assertEqual(report["filed"], 1)
            self.assertEqual(report["flagged"], 0)
            ids = _all_record_ids(root)
            self.assertEqual(len(ids), 1, "no duplicate mint")
            self.assertEqual(len(set(ids)), len(ids))
            self.assertEqual(dest.read_bytes(), b"payload-bytes", "no data loss")
            max_id = max(int(i.rsplit("-", 1)[-1]) for i in ids)
            self.assertGreaterEqual(_counter(root), max_id)

    def test_crash_after_counter_persist_burns_id_never_duplicates(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            manifest = root / "manifest.json"
            entries = [_entry(root)]
            manifest.write_text(json.dumps(entries), encoding="utf-8")
            with mock.patch.object(asset_registry, "_move_asset",
                                   side_effect=RuntimeError("simulated crash")):
                with self.assertRaises(RuntimeError):
                    _run_batch(root, entries, manifest_path=manifest)
            self.assertEqual(_counter(root), 1, "counter persisted pre-crash")
            self.assertEqual(_all_record_ids(root), [])
            resumed = json.loads(manifest.read_text(encoding="utf-8"))
            report = _run_batch(root, resumed, manifest_path=manifest)
            self.assertEqual(report["filed"], 1)
            ids = _all_record_ids(root)
            self.assertEqual(ids, ["AST-TESTPROJ-00002"],
                             "ID 1 burned, never reused; no duplicate")
            self.assertEqual(_counter(root), 2)

    def test_rerun_of_filed_manifest_mints_nothing_new(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            manifest = root / "manifest.json"
            entries = [_entry(root)]
            report = _run_batch(root, entries, manifest_path=manifest)
            self.assertEqual(report["filed"], 1)
            counter_before = _counter(root)
            resumed = json.loads(manifest.read_text(encoding="utf-8"))
            report2 = _run_batch(root, resumed, manifest_path=manifest)
            self.assertEqual(report2["filed"], 0)
            self.assertEqual(report2["already"], 1)
            self.assertEqual(_counter(root), counter_before)
            self.assertEqual(len(_all_record_ids(root)), 1)


class TestCounterRecovery(unittest.TestCase):
    """§9.2: recovery is scan-based and RECOVERY ONLY, never routine."""

    def _file_one(self, root, **overrides):
        return _run_batch(root, [_entry(root, **overrides)])

    def test_missing_counter_with_records_recovers_max_id(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            self._file_one(root)
            asset_registry.counter_path(_wiki_root(root)).unlink()
            report = self._file_one(root, filename="two.jpg", name="Two",
                                    content=b"2")
            self.assertEqual(report["filed"], 1)
            self.assertTrue(report["recovery_notes"], "recovery surfaced")
            self.assertIn("RECOVERED", report["recovery_notes"][0])
            self.assertIn("AST-TESTPROJ-00002", _all_record_ids(root))
            self.assertEqual(_counter(root), 2)

    def test_empty_partial_and_garbage_counters_recover(self):
        for corrupt in ("", "12abc", "garbage", "  \n"):
            with TemporaryDirectory() as tmp:
                root = _make_root(tmp)
                self._file_one(root)  # counter = 1, one record
                asset_registry.counter_path(_wiki_root(root)).write_text(
                    corrupt, encoding="utf-8")
                report = self._file_one(root, filename="two.jpg", name="Two",
                                        content=b"2")
                self.assertEqual(report["filed"], 1, corrupt)
                self.assertTrue(report["recovery_notes"], corrupt)
                ids = _all_record_ids(root)
                self.assertEqual(len(ids), len(set(ids)), corrupt)
                self.assertEqual(max(int(i.rsplit("-", 1)[-1]) for i in ids),
                                 _counter(root), corrupt)

    def test_fresh_registry_is_init_not_recovery(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            report = self._file_one(root)
            self.assertEqual(report["recovery_notes"], [])
            self.assertEqual(_all_record_ids(root), ["AST-TESTPROJ-00001"])

    def test_recovery_scans_both_zones(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            self._file_one(root, zone="local")
            self._file_one(root, filename="b.png", name="Brand", zone="git",
                           asset_class="brand", content=b"png")
            asset_registry.counter_path(_wiki_root(root)).write_text(
                "0", encoding="utf-8")  # stale-low counter = corruption class
            value, note = asset_registry.read_counter(_wiki_root(root))
            # routine read trusts the (valid-format) counter; corruption
            # recovery is only for missing/unparseable — so force it:
            asset_registry.counter_path(_wiki_root(root)).write_text(
                "not-a-number", encoding="utf-8")
            value, note = asset_registry.read_counter(_wiki_root(root))
            self.assertEqual(value, 2, "max ID scanned across git AND local")
            self.assertIn("RECOVERED", note)


class TestLockDiscipline(unittest.TestCase):
    """§9.2: O_EXCL lock; stale (>15 min) SURFACED with path+age+pid,
    never auto-broken. Clock injected."""

    def test_stale_lock_surfaced_never_broken(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            lock = asset_registry.lock_path(_wiki_root(root))
            lock.parent.mkdir(parents=True, exist_ok=True)
            lock.write_text("4242 {}\n".format(T0.isoformat()),
                            encoding="utf-8")
            later = T0 + timedelta(minutes=20)
            report = _run_batch(root, [_entry(root)],
                                now_fn=lambda: later)
            self.assertEqual(report["filed"], 0)
            self.assertEqual(report["flagged"], 1)
            self.assertEqual(len(report["lock_reports"]), 1)
            lock_report = report["lock_reports"][0]
            self.assertTrue(lock_report["stale"])
            self.assertEqual(lock_report["pid"], "4242")
            self.assertEqual(lock_report["age_minutes"], 20.0)
            self.assertIn(str(lock), lock_report["detail"])
            self.assertIn("never auto-broken", lock_report["detail"])
            self.assertTrue(lock.exists(), "stale lock NOT auto-broken")

    def test_fresh_lock_blocks_without_stale_marking(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            lock = asset_registry.lock_path(_wiki_root(root))
            lock.parent.mkdir(parents=True, exist_ok=True)
            lock.write_text("77 {}\n".format(T0.isoformat()), encoding="utf-8")
            report = _run_batch(root, [_entry(root)],
                                now_fn=lambda: T0 + timedelta(minutes=5))
            self.assertEqual(report["filed"], 0)
            self.assertFalse(report["lock_reports"][0]["stale"])
            self.assertTrue(lock.exists())

    def test_lock_released_after_allocation(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            _run_batch(root, [_entry(root)])
            self.assertFalse(asset_registry.lock_path(_wiki_root(root)).exists())


class TestZoneValidator(unittest.TestCase):
    """§9.4: pre-commit-point predicate; `zone: local` under git/ fails —
    and fails BEFORE the move (a moved file would already be the leak)."""

    def test_local_zone_declared_but_git_destination_rejected_before_move(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, zone="local",
                           dest_dir="wiki.{}/git/assets".format(WIKI))
            report = _run_batch(root, [entry])
            self.assertEqual(report["flagged"], 1)
            self.assertIn("zone validator", entry["reason"])
            self.assertTrue((root / "0-Inbox" / "photo one.jpg").exists(),
                            "asset NOT moved into git/ (leak prevented)")
            self.assertEqual(_all_record_ids(root), [])

    def test_git_zone_declared_but_local_destination_rejected(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, zone="git",
                           dest_dir="wiki.{}/local/assets".format(WIKI))
            report = _run_batch(root, [entry])
            self.assertEqual(report["flagged"], 1)
            self.assertEqual(_all_record_ids(root), [])

    def test_predicate_rejects_record_path_outside_declared_zone(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            wiki_root = _wiki_root(root)
            ok, why = asset_registry.validate_zone(
                wiki_root, "local",
                wiki_root / "local" / "assets" / "a.jpg",
                wiki_root / "git" / "_registry" / "AST-X-00001.md")
            self.assertFalse(ok)
            self.assertIn("does not resolve under the 'local' zone", why)

    def test_predicate_accepts_matching_zone(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            wiki_root = _wiki_root(root)
            ok, why = asset_registry.validate_zone(
                wiki_root, "git",
                wiki_root / "git" / "assets" / "a.jpg",
                wiki_root / "git" / "_registry" / "AST-X-00001.md")
            self.assertTrue(ok, why)

    def test_destination_outside_any_wiki_zone_flagged(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, dest_dir="tasks/assets")
            report = _run_batch(root, [entry])
            self.assertEqual(report["flagged"], 1)
            self.assertIn("not under a wiki zone", entry["reason"])


class TestRequiredExplicit(unittest.TestCase):
    """§9.1 mandatory-or-explicitly-empty via the REQUIRED_EXPLICIT table."""

    def test_missing_required_fields_flagged_before_any_id_is_consumed(self):
        for field in asset_registry.REQUIRED_EXPLICIT:
            with TemporaryDirectory() as tmp:
                root = _make_root(tmp)
                entry = _entry(root)
                del entry[field]
                report = _run_batch(root, [entry])
                self.assertEqual(report["flagged"], 1, field)
                self.assertIn(field, entry["reason"])
                self.assertIn("mandatory-or-explicitly-empty", entry["reason"])
                self.assertFalse(
                    asset_registry.counter_path(_wiki_root(root)).exists(),
                    "structural flag must not consume an ID")

    def test_explicitly_empty_forms_are_accepted(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, rights_consent="", derived_from=[], recipe={})
            report = _run_batch(root, [entry])
            self.assertEqual(report["filed"], 1)
            record = asset_registry.parse_record(_records(root, "local")[0])
            self.assertEqual(record["rights_consent"], "")
            self.assertEqual(record["derived_from"], [])
            self.assertEqual(record["recipe"], {})

    def test_unknown_rights_consent_is_legal_but_explicit(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            report = _run_batch(root, [_entry(root, rights_consent="unknown")])
            self.assertEqual(report["filed"], 1)
            record = asset_registry.parse_record(_records(root, "local")[0])
            self.assertEqual(record["rights_consent"], "unknown")

    def test_asset_class_validated_against_config_vocab(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, asset_class="sprites")  # future Anvil class
            report = _run_batch(root, [entry])
            self.assertEqual(report["flagged"], 1)
            self.assertIn("not in the config vocabulary", entry["reason"])


class TestLineageChaining(unittest.TestCase):
    """Gate change 6: deriving from a skipped batch entry skips the
    dependent with the reason CHAINED (transitively)."""

    def test_lineage_skip_chains_transitively_with_reasons(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            e0 = _entry(root, filename="root.jpg", name="Root", content=b"0")
            del e0["rights_consent"]  # flagged
            e1 = _entry(root, filename="child.jpg", name="Child", content=b"1",
                        derived_from=["batch:0"])
            e2 = _entry(root, filename="grandchild.jpg", name="Grandchild",
                        content=b"2", derived_from=["batch:1"])
            report = _run_batch(root, [e0, e1, e2])
            self.assertEqual(report["flagged"], 1)
            self.assertEqual(report["skipped"], 2)
            self.assertEqual(e1["status"], "skipped-chained")
            self.assertIn("derives from skipped entry #0", e1["reason"])
            self.assertIn("rights_consent", e1["reason"], "reason CHAINED in")
            self.assertEqual(e2["status"], "skipped-chained")
            self.assertIn("derives from skipped entry #1", e2["reason"])
            self.assertEqual(_all_record_ids(root), [])

    def test_intra_batch_lineage_resolves_to_assigned_ids(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            e0 = _entry(root, filename="root.jpg", name="Root", content=b"0")
            e1 = _entry(root, filename="child.jpg", name="Child", content=b"1",
                        derived_from=["batch:0"])
            report = _run_batch(root, [e0, e1])
            self.assertEqual(report["filed"], 2)
            child = asset_registry.parse_record(
                asset_registry.registry_dir(_wiki_root(root), "local")
                / (e1["id"] + ".md"))
            self.assertEqual(child["derived_from"], [e0["id"]])

    def test_bad_batch_ref_flagged_with_prose(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, derived_from=["batch:99"])
            report = _run_batch(root, [entry])
            self.assertEqual(report["flagged"], 1)
            self.assertIn("does not name a batch entry", entry["reason"])


class TestCollisionRefusal(unittest.TestCase):
    """Gate change 2: rename-collision REFUSAL — never overwrite."""

    def test_destination_collision_refused_and_nothing_lost(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            dest_dir = root / "wiki.{}/local/assets".format(WIKI)
            dest_dir.mkdir(parents=True)
            existing = dest_dir / "photo-one.jpg"
            existing.write_bytes(b"pre-existing DIFFERENT content")
            entry = _entry(root, content=b"new content")
            report = _run_batch(root, [entry])
            self.assertEqual(report["flagged"], 1)
            self.assertIn("refusing to overwrite", entry["reason"])
            self.assertEqual(existing.read_bytes(),
                             b"pre-existing DIFFERENT content")
            self.assertTrue((root / "0-Inbox" / "photo one.jpg").exists(),
                            "source stays in the inbox slot")
            self.assertEqual(_all_record_ids(root), [])

    def test_identical_content_at_destination_is_idempotent_done(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            dest_dir = root / "wiki.{}/local/assets".format(WIKI)
            dest_dir.mkdir(parents=True)
            (dest_dir / "photo-one.jpg").write_bytes(b"same bytes")
            entry = _entry(root, content=b"same bytes")
            report = _run_batch(root, [entry])
            self.assertEqual(report["filed"], 1)
            self.assertFalse((root / "0-Inbox" / "photo one.jpg").exists(),
                             "lingering source cleaned up on idempotent move")


class TestOpaqueGitIndex(unittest.TestCase):
    """§9.4 / gate change 3: the committed git-zone index carries ONLY
    opaque rows (count + AST-IDs) for local-zone content."""

    def test_git_index_leaks_no_local_filenames_names_or_descriptions(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            local = _entry(root, filename="secret dish.jpg", zone="local",
                           name="Secret Dish Name",
                           description="confidential guest photo",
                           content=b"local-bytes")
            public = _entry(root, filename="logo.png", zone="git",
                            asset_class="brand", name="Public Logo",
                            dest_dir="wiki.{}/git/assets".format(WIKI),
                            content=b"png-bytes")
            report = _run_batch(root, [local, public])
            self.assertEqual(report["filed"], 2)
            git_index = (asset_registry.registry_dir(_wiki_root(root), "git")
                         / "asset-index.md").read_text(encoding="utf-8")
            self.assertIn(local["id"], git_index, "opaque row: the AST-ID")
            self.assertIn("1 local-zone asset(s)", git_index)
            for leak in ("secret", "Secret Dish Name", "secret-dish",
                         "confidential guest photo"):
                self.assertNotIn(leak, git_index, leak)
            self.assertIn("Public Logo", git_index, "git rows stay item-level")
            local_index = (asset_registry.registry_dir(_wiki_root(root), "local")
                           / "asset-index.md").read_text(encoding="utf-8")
            self.assertIn("Secret Dish Name", local_index)


class TestHostileNamesRoundTrip(unittest.TestCase):
    """Gate change 2: YAML-hostile names escaped/quoted safely within the
    existing frontmatter subset; unrepresentable ones flagged, never mangled."""

    HOSTILE = (
        'Adobo: The Best #1 [draft]',
        "- leading dash {braces} & stuff",
        'He said "hi" once',
        "trailing colon:",
        "0451",
    )

    def test_hostile_names_round_trip_through_the_record(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entries = [
                _entry(root, filename="f{}.jpg".format(i), name=name,
                       content=("c%d" % i).encode())
                for i, name in enumerate(self.HOSTILE)
            ]
            report = _run_batch(root, entries)
            self.assertEqual(report["filed"], len(self.HOSTILE))
            for entry, name in zip(entries, self.HOSTILE):
                record = asset_registry.parse_record(
                    asset_registry.registry_dir(_wiki_root(root), "local")
                    / (entry["id"] + ".md"))
                self.assertEqual(record["name"], name)

    def test_name_with_both_quote_kinds_flagged_not_mangled(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, name="both \" and ' quotes")
            report = _run_batch(root, [entry])
            self.assertEqual(report["flagged"], 1)
            self.assertIn("both quote characters", entry["reason"])
            self.assertEqual(_all_record_ids(root), [])

    def test_nested_recipe_value_refused_as_subset_misfit(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, recipe={"tool": "gen",
                                         "params": {"steps": 30}})
            report = _run_batch(root, [entry])
            self.assertEqual(report["flagged"], 1)
            self.assertIn("do not fit the shared frontmatter subset",
                          entry["reason"])

    def test_scalar_recipe_and_source_round_trip_as_mappings(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, recipe={"tool": "grok-imagine",
                                         "job_ref": "job: #42"})
            report = _run_batch(root, [entry])
            self.assertEqual(report["filed"], 1)
            record = asset_registry.parse_record(_records(root, "local")[0])
            self.assertEqual(record["recipe"],
                             {"tool": "grok-imagine", "job_ref": "job: #42"})
            self.assertEqual(record["source"],
                             {"by": "jp", "date": "2026-07-21"})


class TestRecordSchema(unittest.TestCase):
    """§9.1 field-for-field: every schema field present, spec order."""

    def test_record_carries_every_spec_9_1_field(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            _run_batch(root, [_entry(root)])
            record = asset_registry.parse_record(_records(root, "local")[0])
            for field in asset_registry.RECORD_FIELDS:
                self.assertIn(field, record, field)
            self.assertEqual(len(asset_registry.RECORD_FIELDS), 17)

    def test_deliverable_commits_with_url_pending_and_stub_flags(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry = _entry(root, asset_class="deliverable",
                           rights_consent="owned")
            report = _run_batch(root, [entry])
            self.assertEqual(report["filed"], 1)
            record = asset_registry.parse_record(_records(root, "local")[0])
            self.assertEqual(record["url"], "pending",
                             "url: pending is a VALID committed state")
            self.assertTrue(any("not-configured" in line
                                for line in report["lines"]),
                            "remote-store stub surfaced post-commit")

    def test_non_deliverable_url_is_explicit_empty(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            _run_batch(root, [_entry(root)])
            record = asset_registry.parse_record(_records(root, "local")[0])
            self.assertEqual(record["url"], "")

    def test_ids_are_unique_and_sequential_across_zones(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entries = [
                _entry(root, filename="a.jpg", name="A", content=b"a"),
                _entry(root, filename="b.png", name="B", zone="git",
                       asset_class="brand", content=b"b",
                       dest_dir="wiki.{}/git/assets".format(WIKI)),
                _entry(root, filename="c.jpg", name="C", content=b"c"),
            ]
            report = _run_batch(root, entries)
            self.assertEqual(report["filed"], 3)
            ids = sorted(e["id"] for e in entries)
            self.assertEqual(ids, ["AST-TESTPROJ-00001", "AST-TESTPROJ-00002",
                                   "AST-TESTPROJ-00003"])
            self.assertEqual(_counter(root), 3)


class TestRemoteStoreStub(unittest.TestCase):
    """§9.7 seam: config-gated dead code, zero network imports."""

    def test_stub_not_configured_whether_disabled_or_enabled(self):
        record = {"id": "AST-X-00001"}
        result = asset_registry.remote_store_mint({"remote_store":
                                                   {"enabled": False}}, record)
        self.assertEqual(result["status"], "not-configured")
        result = asset_registry.remote_store_mint({"remote_store":
                                                   {"enabled": True}}, record)
        self.assertEqual(result["status"], "not-configured")
        self.assertIn("no transport", result["detail"])

    def test_module_imports_no_network_modules(self):
        import ast
        source = (WIKISYS_SCRIPTS / "asset_registry.py").read_text(
            encoding="utf-8")
        tree = ast.parse(source)
        banned = {"urllib", "http", "socket", "ssl", "ftplib", "smtplib",
                  "requests", "boto3", "botocore"}
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                self.assertNotIn(name.split(".")[0], banned, name)


class TestCli(unittest.TestCase):
    """route_inbox argparse-verb pattern: prose echoes, no tracebacks."""

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = asset_registry.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_file_batch_echoes_prose_counts_and_reasons(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            good = _entry(root, filename="a.jpg", name="A", content=b"a")
            bad = _entry(root, filename="b.jpg", name="B", content=b"b")
            del bad["rights_consent"]
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([good, bad]), encoding="utf-8")
            code, out, err = self._run(
                ["file", "--root", str(root), "--batch", str(manifest)])
            self.assertEqual(code, 1)
            self.assertIn("1 filed, 1 flagged", out)
            self.assertIn("flagged (missing rights_consent", out)
            self.assertIn("0-Inbox/b.jpg", out)
            self.assertNotIn("Traceback", out + err)

    def test_file_single_entry_verb(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            entry_path = root / "entry.json"
            entry_path.write_text(json.dumps(_entry(root)), encoding="utf-8")
            code, out, err = self._run(
                ["file", "--root", str(root), "--entry", str(entry_path)])
            self.assertEqual(code, 0)
            self.assertIn("1 filed, 0 flagged", out)
            persisted = json.loads(entry_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["status"], "filed")

    def test_malformed_manifest_json_is_prose_not_traceback(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            manifest = root / "manifest.json"
            manifest.write_text("{not json", encoding="utf-8")
            code, out, err = self._run(
                ["file", "--root", str(root), "--batch", str(manifest)])
            self.assertEqual(code, 2)
            self.assertIn("cannot read entries", err)
            self.assertNotIn("Traceback", out + err)

    def test_status_reports_counter_lock_and_zone_counts(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([_entry(root)]), encoding="utf-8")
            self._run(["file", "--root", str(root), "--batch", str(manifest)])
            code, out, err = self._run(["status", "--root", str(root)])
            self.assertEqual(code, 0)
            self.assertIn("wiki.testproj", out)
            self.assertIn("counter: 1", out)
            self.assertIn("lock: free", out)
            self.assertIn("local zone: 1 record(s)", out)

    def test_stale_lock_surfaced_through_cli_exit_3(self):
        with TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            lock = asset_registry.lock_path(_wiki_root(root))
            lock.parent.mkdir(parents=True, exist_ok=True)
            stale_since = (datetime.now(timezone.utc)
                           - timedelta(minutes=45)).isoformat()
            lock.write_text("999 {}\n".format(stale_since), encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([_entry(root)]), encoding="utf-8")
            code, out, err = self._run(
                ["file", "--root", str(root), "--batch", str(manifest)])
            self.assertEqual(code, 3)
            self.assertIn("STALE LOCK surfaced", out)
            self.assertIn("pid=999", out)
            self.assertTrue(lock.exists())


class TestSyncExclusion(unittest.TestCase):
    """Gate change 4: the module is EXCLUDED from sync_from_kit propagation
    this build (explicit wiring decision later)."""

    def test_scripts_lane_copytree_excludes_asset_registry(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / "src_scripts"
            src.mkdir()
            (src / "asset_registry.py").write_text("# excluded", encoding="utf-8")
            (src / "route_inbox.py").write_text("# shipped", encoding="utf-8")
            target = tmp_path / "consumer_scripts"
            action = sync_from_kit.Action(
                kind="OVERWRITE", target="x/_scripts/", source="y/_scripts/",
                target_abs=target, source_abs=src, is_dir=True)
            sync_from_kit._apply_action(action)
            self.assertTrue((target / "route_inbox.py").exists())
            self.assertFalse((target / "asset_registry.py").exists(),
                             "asset_registry.py must not propagate this build")

    def test_config_lane_plan_excludes_asset_registry_yaml(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            library = tmp_path / "library"
            wikisys = library / "Biz.Automation" / "wikisys.library"
            for sub in ("_scripts", "_config", "_template"):
                (wikisys / sub).mkdir(parents=True)
            (wikisys / "_config" / "asset_registry.yaml").write_text(
                "asset_classes:\n  - ugc\n", encoding="utf-8")
            (wikisys / "_config" / "example.yaml").write_text(
                "rules: []\n", encoding="utf-8")
            consumer = tmp_path / "consumer"
            (consumer / "Biz.Automation" / "wikisys.cons").mkdir(parents=True)
            (consumer / "wiki.cons" / "git").mkdir(parents=True)
            actions = sync_from_kit._build_plan(library, consumer, "cons")
            targets = [a.target for a in actions]
            self.assertTrue(any("example.yaml" in t for t in targets))
            self.assertFalse(any("asset_registry.yaml" in t for t in targets),
                             "config exclusion (gate change 4)")

    def test_exclusion_constants_name_the_module_files(self):
        self.assertIn("asset_registry.py", sync_from_kit.SYNC_EXCLUDED_SCRIPTS)
        self.assertIn("asset_registry.yaml", sync_from_kit.SYNC_EXCLUDED_CONFIG)


if __name__ == "__main__":
    unittest.main()
