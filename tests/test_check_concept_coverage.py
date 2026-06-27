"""Tests for _scripts/check_concept_coverage.py — P13 roster-entity coverage scanner."""

import io
import shutil
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import check_concept_coverage
from _lib import dashboard
from _lib.config_loader import ConfigYamlError


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "sample_wiki"


def _clone_fixture(dst: Path) -> Path:
    shutil.copytree(FIXTURE_ROOT, dst)
    return dst


def _write_page(wiki: Path, rel: str, fm_lines, body: str = "") -> Path:
    path = wiki / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if fm_lines:
        content = "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body
    else:
        content = body
    path.write_text(content, encoding="utf-8")
    return path


def _write_config(wiki: Path, body: str) -> Path:
    path = wiki / "_config" / "concept_coverage.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _write_roster(wiki: Path, body: str) -> Path:
    path = wiki / "_canon" / "roster.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _findings_for_entity(findings, entity):
    return [f for f in findings if f.get("entity") == entity]


class RosterLoaderTests(unittest.TestCase):

    def test_roster_load_returns_entities_with_aliases(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            roster = check_concept_coverage._load_roster(wiki)
            self.assertEqual(len(roster), 2)
            self.assertEqual(roster[0]["canonical_name"], "Protagonist")
            self.assertEqual(roster[0]["aliases"], ["Hero", "MC"])
            self.assertEqual(roster[1]["canonical_name"], "Antagonist")

    def test_roster_missing_file_main_exit_2(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "_canon" / "roster.yaml").unlink()
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = check_concept_coverage._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr.getvalue())

    def test_roster_malformed_yaml_propagates_config_yaml_error(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki, "entities: not_a_list_just_scalar\n")
            with self.assertRaises(ConfigYamlError):
                check_concept_coverage.run(wiki)


class ConceptCoverageConfigTests(unittest.TestCase):

    def test_config_absent_file_returns_defaults(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "_config" / "concept_coverage.yaml").unlink()
            cfg = check_concept_coverage._load_concept_coverage_config(wiki)
            # S047-T4 Edit-2: subject_entities key added to DEFAULTS.
            # M001: tier_filter key added to DEFAULTS (default None -> OFF).
            self.assertEqual(
                cfg,
                {"min_mentions": 2, "exclude_folders": [], "exclude_entities": [], "subject_entities": [], "tier_filter": None},
            )

    def test_config_empty_file_returns_defaults(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_config(wiki, "")
            cfg = check_concept_coverage._load_concept_coverage_config(wiki)
            # S047-T4 Edit-2: subject_entities key added to DEFAULTS.
            # M001: tier_filter key added to DEFAULTS (default None -> OFF).
            self.assertEqual(
                cfg,
                {"min_mentions": 2, "exclude_folders": [], "exclude_entities": [], "subject_entities": [], "tier_filter": None},
            )

    def test_config_partial_keys_missing_applies_per_field_defaults(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_config(wiki, "min_mentions: 5\n")
            cfg = check_concept_coverage._load_concept_coverage_config(wiki)
            # S047-T4 Edit-2: subject_entities key added to DEFAULTS.
            # M001: tier_filter key added to DEFAULTS (default None -> OFF).
            self.assertEqual(
                cfg,
                {"min_mentions": 5, "exclude_folders": [], "exclude_entities": [], "subject_entities": [], "tier_filter": None},
            )

    def test_config_override_min_mentions(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_config(wiki, "min_mentions: 5\n")
            cfg = check_concept_coverage._load_concept_coverage_config(wiki)
            self.assertEqual(cfg["min_mentions"], 5)

    def test_config_override_exclude_folders(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_config(wiki, 'exclude_folders: ["03-Lore", "_brain_dump"]\n')
            cfg = check_concept_coverage._load_concept_coverage_config(wiki)
            self.assertEqual(cfg["exclude_folders"], ["03-Lore", "_brain_dump"])

    def test_config_override_exclude_entities(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_config(wiki, 'exclude_entities: ["TestEntity"]\n')
            cfg = check_concept_coverage._load_concept_coverage_config(wiki)
            self.assertEqual(cfg["exclude_entities"], ["TestEntity"])


class MentionDetectionTests(unittest.TestCase):

    def test_canonical_name_match_word_boundary(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/Page1.md",
                ['title: "P1"'],
                "The Protagonist arrives in chapter one.\n",
            )
            _write_page(wiki, "01-Domain/Page2.md",
                ['title: "P2"'],
                "Later, the Protagonist returns.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(len(findings), 1)
            f = findings[0]
            self.assertEqual(f["page_count"], 2)
            self.assertEqual(f["severity"], "info")
            self.assertEqual(f["reason"], check_concept_coverage.REASON_COVERAGE_GAP)

    def test_alias_match_word_boundary(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/AliasA.md",
                ['title: "A"'],
                "Hero saves the day.\n",
            )
            _write_page(wiki, "01-Domain/AliasB.md",
                ['title: "B"'],
                "Hero fights again.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["page_count"], 2)
            self.assertEqual(findings[0]["entity"], "Protagonist")

    def test_case_sensitive_miss_lowercase(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/CaseA.md",
                ['title: "A"'],
                "the protagonist arrives in lowercase.\n",
            )
            _write_page(wiki, "01-Domain/CaseB.md",
                ['title: "B"'],
                "the protagonist arrives again, still lowercase.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(findings, [])

    def test_word_boundary_miss_substring(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/SubA.md",
                ['title: "A"'],
                "Heroic deeds were performed.\n",
            )
            _write_page(wiki, "01-Domain/SubB.md",
                ['title: "B"'],
                "More Heroic exploits.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(findings, [])

    def test_code_block_stripped_before_regex(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/CodeOnly.md",
                ['title: "C"'],
                "Body text without entity.\n\n"
                "```python\n"
                "# Protagonist inside fenced block\n"
                "```\n",
            )
            _write_page(wiki, "01-Domain/PlainOne.md",
                ['title: "P"'],
                "The Protagonist appears here in plain prose.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(findings, [])

    def test_distinct_page_count_not_total_occurrence(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/RepeatOne.md",
                ['title: "R"'],
                "Hero. Hero. Hero. Hero. Hero.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(findings, [])

    def test_at_or_above_threshold_emits_finding_severity_info(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/ThreshA.md",
                ['title: "A"'],
                "The Protagonist enters.\n",
            )
            _write_page(wiki, "01-Domain/ThreshB.md",
                ['title: "B"'],
                "The Protagonist exits.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(len(findings), 1)
            f = findings[0]
            self.assertEqual(f["severity"], "info")
            self.assertEqual(f["entity"], "Protagonist")
            self.assertEqual(f["page_count"], 2)
            self.assertEqual(f["reason"], check_concept_coverage.REASON_COVERAGE_GAP)


class DedicatedPageDetectionTests(unittest.TestCase):

    def test_dedicated_page_present_no_finding_emitted(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/RefA.md",
                ['title: "A"'],
                "The Protagonist enters.\n",
            )
            _write_page(wiki, "01-Domain/RefB.md",
                ['title: "B"'],
                "The Protagonist exits.\n",
            )
            _write_page(wiki, "01-Domain/protagonist.md",
                ['title: "Protagonist Page"'],
                "# Dedicated Protagonist page\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(findings, [])

    def test_dedicated_page_absent_finding_emitted(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/AbsA.md",
                ['title: "A"'],
                "The Protagonist enters.\n",
            )
            _write_page(wiki, "01-Domain/AbsB.md",
                ['title: "B"'],
                "The Protagonist exits.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(len(findings), 1)

    def test_slugify_lowercases_and_hyphenates_multi_word(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki, (
                "entities:\n"
                "  - canonical_name: Iron Soul\n"
            ))
            _write_page(wiki, "01-Domain/MultiA.md",
                ['title: "A"'],
                "The Iron Soul appears.\n",
            )
            _write_page(wiki, "01-Domain/MultiB.md",
                ['title: "B"'],
                "The Iron Soul appears again.\n",
            )
            # With the dedicated page absent, expect a finding.
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Iron Soul")
            self.assertEqual(len(findings), 1)
            # Now add the dedicated `iron-soul.md` page and rerun: finding suppressed.
            _write_page(wiki, "01-Domain/iron-soul.md",
                ['title: "Iron Soul Page"'],
                "# Dedicated Iron Soul page\n",
            )
            out2 = check_concept_coverage.run(wiki)
            findings2 = _findings_for_entity(out2["findings"], "Iron Soul")
            self.assertEqual(findings2, [])


class ExclusionTests(unittest.TestCase):

    def test_exclude_folders_component_aware_skip(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_config(wiki, 'exclude_folders: ["03-Lore"]\n')
            _write_page(wiki, "03-Lore/Skipped.md",
                ['title: "Skipped"'],
                "The Protagonist visits Lore folder.\n",
            )
            _write_page(wiki, "01-Domain/Scanned.md",
                ['title: "Scanned"'],
                "The Protagonist visits Domain folder.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            # Only 1 distinct page after exclude_folders filter -> below threshold 2.
            self.assertEqual(findings, [])

    def test_exclude_entities_canonical_name_exact_match_no_finding(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_config(wiki, 'exclude_entities: ["Protagonist"]\n')
            _write_page(wiki, "01-Domain/X1.md",
                ['title: "1"'],
                "The Protagonist arrives.\n",
            )
            _write_page(wiki, "01-Domain/X2.md",
                ['title: "2"'],
                "The Protagonist arrives again.\n",
            )
            _write_page(wiki, "01-Domain/X3.md",
                ['title: "3"'],
                "The Protagonist returns.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(findings, [])

    def test_exclude_entities_does_not_match_aliases(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            # Exclude an alias name; canonical should still scan.
            _write_config(wiki, 'exclude_entities: ["Hero"]\n')
            _write_page(wiki, "01-Domain/Y1.md",
                ['title: "1"'],
                "The Protagonist arrives.\n",
            )
            _write_page(wiki, "01-Domain/Y2.md",
                ['title: "2"'],
                "The Protagonist arrives again.\n",
            )
            out = check_concept_coverage.run(wiki)
            findings = _findings_for_entity(out["findings"], "Protagonist")
            self.assertEqual(len(findings), 1)


class SubjectEntitiesTests(unittest.TestCase):
    """S047-T4 Edit-3 + Edit-2 — subject_entities exemption per spec §2.5 L586-594."""

    def test_subject_entity_listed_no_finding_emitted_dashboard_annotated(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(
                wiki,
                "entities:\n"
                "  - canonical_name: Codex\n",
            )
            _write_config(wiki, 'subject_entities: ["Codex"]\n')
            _write_page(wiki, "01-Domain/A.md",
                ['title: "A"'],
                "The Codex is the central artifact.\n",
            )
            _write_page(wiki, "01-Domain/B.md",
                ['title: "B"'],
                "The Codex appears again.\n",
            )
            out = check_concept_coverage.run(wiki)
            # No finding emitted — subject_entities exemption fires.
            self.assertEqual(_findings_for_entity(out["findings"], "Codex"), [])
            # subject_entries gains 1 Codex entry with the spec annotation.
            self.assertEqual(len(out["subject_entries"]), 1)
            self.assertEqual(out["subject_entries"][0]["entity"], "Codex")
            self.assertEqual(out["subject_entries"][0]["annotation"], "subject (exempt)")
            # Dashboard renders the Subject Entities section + bullet.
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("## Subject Entities (exempt)", body)
            self.assertIn("Codex", body)

    def test_subject_entity_not_listed_finding_still_fires_default_empty_backward_compat(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(
                wiki,
                "entities:\n"
                "  - canonical_name: Codex\n",
            )
            # No subject_entities key → default empty list → backward-compat.
            _write_config(wiki, "min_mentions: 2\n")
            _write_page(wiki, "01-Domain/A.md",
                ['title: "A"'],
                "The Codex is the central artifact.\n",
            )
            _write_page(wiki, "01-Domain/B.md",
                ['title: "B"'],
                "The Codex appears again.\n",
            )
            out = check_concept_coverage.run(wiki)
            # Warning fires per prior behavior.
            findings = _findings_for_entity(out["findings"], "Codex")
            self.assertEqual(len(findings), 1)
            # subject_entries defaults to empty.
            self.assertEqual(out["subject_entries"], [])
            # Dashboard does NOT render the Subject Entities section.
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertNotIn("## Subject Entities (exempt)", body)


class DashboardRenderingTests(unittest.TestCase):

    def test_dashboard_fm_5_field_header_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            out = check_concept_coverage.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            lines = body.split("\n")
            expected = dashboard.render_fm_header("Concept Coverage Dashboard", today=date.today().isoformat())
            self.assertEqual(lines[:7], expected)

    def test_dashboard_zero_findings_skeleton_render(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            out = check_concept_coverage.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            self.assertIn("No concept coverage findings.", body)
            self.assertNotIn("## Coverage Gaps", body)

    def test_dashboard_findings_sorted_by_entity_name(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki, (
                "entities:\n"
                "  - canonical_name: Charlie\n"
                "  - canonical_name: Alpha\n"
                "  - canonical_name: Beta\n"
            ))
            for entity in ("Alpha", "Beta", "Charlie"):
                for i in (1, 2):
                    _write_page(wiki,
                        "01-Domain/{}_{}.md".format(entity, i),
                        ['title: "{}_{}"'.format(entity, i)],
                        "Mention of {} here.\n".format(entity),
                    )
            out = check_concept_coverage.run(wiki)
            body = out["dashboard_path"].read_text(encoding="utf-8")
            alpha_idx = body.index("- info: Alpha:")
            beta_idx = body.index("- info: Beta:")
            charlie_idx = body.index("- info: Charlie:")
            self.assertLess(alpha_idx, beta_idx)
            self.assertLess(beta_idx, charlie_idx)


class CliEntryPointTests(unittest.TestCase):

    def test_main_exit_zero_clean_run(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = check_concept_coverage._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 0)
            self.assertIn("concept_coverage:", stdout.getvalue())

    def test_main_exit_one_findings_present(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_page(wiki, "01-Domain/CliA.md",
                ['title: "A"'],
                "The Protagonist arrives.\n",
            )
            _write_page(wiki, "01-Domain/CliB.md",
                ['title: "B"'],
                "The Protagonist exits.\n",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = check_concept_coverage._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 1)
            self.assertIn("Protagonist", stdout.getvalue())

    def test_main_exit_two_missing_roster_yaml(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            (wiki / "_canon" / "roster.yaml").unlink()
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = check_concept_coverage._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr.getvalue())


class EdgeCaseTests(unittest.TestCase):

    def test_empty_wiki_no_canon_no_pages(self):
        with TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "empty_wiki"
            wiki.mkdir()
            stdout = io.StringIO()
            stderr = io.StringIO()
            rc = check_concept_coverage._main(wiki, stdout=stdout, stderr=stderr)
            self.assertEqual(rc, 2)
            self.assertIn("error:", stderr.getvalue())

    def test_dashboard_write_idempotent_on_rerun(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            out1 = check_concept_coverage.run(wiki)
            body1 = out1["dashboard_path"].read_text(encoding="utf-8")
            out2 = check_concept_coverage.run(wiki)
            body2 = out2["dashboard_path"].read_text(encoding="utf-8")
            self.assertEqual(body1, body2)


class TierFilterTests(unittest.TestCase):
    """M001 — tier-aware coverage: tier_filter skip predicate.

    Default OFF (byte-identical for non-adopters); when set, skip a roster
    entry whose `tier:` does not match (casefold). Missing / empty / null /
    whitespace-only / non-string tier -> DEFAULT_TIER -> included (fail-OPEN:
    an advisory validator over-reports, never silently drops a gap).
    """

    def _two_pages(self, wiki, name):
        """Two distinct pages mentioning `name`, no dedicated page -> a gap."""
        _write_page(wiki, "01-Domain/{}_A.md".format(name),
            ['title: "A"'], "The {} appears here.\n".format(name))
        _write_page(wiki, "01-Domain/{}_B.md".format(name),
            ['title: "B"'], "The {} appears again here.\n".format(name))

    # T1 — tier-skip: a References-tier entry is excluded under an Authoritative filter.
    def test_t1_tier_skip_references_under_authoritative_filter(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki,
                "entities:\n"
                "  - canonical_name: Widget\n"
                "    tier: References\n")
            _write_config(wiki, 'tier_filter: "Authoritative"\n')
            self._two_pages(wiki, "Widget")
            out = check_concept_coverage.run(wiki)
            self.assertEqual(_findings_for_entity(out["findings"], "Widget"), [])

    # T2 — tier-include: an Authoritative entry still fires under an Authoritative filter.
    def test_t2_tier_include_authoritative_under_authoritative_filter(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki,
                "entities:\n"
                "  - canonical_name: Widget\n"
                "    tier: Authoritative\n")
            _write_config(wiki, 'tier_filter: "Authoritative"\n')
            self._two_pages(wiki, "Widget")
            out = check_concept_coverage.run(wiki)
            self.assertEqual(len(_findings_for_entity(out["findings"], "Widget")), 1)

    # T3 — OFF byte-identical: tier data present but inert == no tier data.
    def test_t3_off_byte_identical_tier_present_but_filter_absent(self):
        def _run(roster_body):
            tmp = TemporaryDirectory()
            wiki = _clone_fixture(Path(tmp.name) / "wiki")
            _write_roster(wiki, roster_body)
            # No tier_filter key in config -> OFF.
            _write_config(wiki, "min_mentions: 2\n")
            self._two_pages(wiki, "Widget")
            body = check_concept_coverage.run(wiki)["dashboard_path"].read_text(encoding="utf-8")
            tmp.cleanup()
            return body

        with_tier = _run(
            "entities:\n"
            "  - canonical_name: Widget\n"
            "    tier: References\n")
        without_tier = _run(
            "entities:\n"
            "  - canonical_name: Widget\n")
        self.assertEqual(with_tier, without_tier)

    # T4 — missing-tier fail-open: an entry with NO tier key is included.
    def test_t4_missing_tier_fail_open_included(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki,
                "entities:\n"
                "  - canonical_name: Widget\n")
            _write_config(wiki, 'tier_filter: "Authoritative"\n')
            self._two_pages(wiki, "Widget")
            out = check_concept_coverage.run(wiki)
            self.assertEqual(len(_findings_for_entity(out["findings"], "Widget")), 1)

    # T5 — union with exclude_entities: both skip predicates independent.
    def test_t5_union_with_exclude_entities(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki,
                "entities:\n"
                "  - canonical_name: RefWidget\n"
                "    tier: References\n"
                "  - canonical_name: ExclWidget\n"
                "    tier: Authoritative\n"
                "  - canonical_name: PlainWidget\n"
                "    tier: Authoritative\n")
            _write_config(wiki,
                'tier_filter: "Authoritative"\n'
                'exclude_entities: ["ExclWidget"]\n')
            self._two_pages(wiki, "RefWidget")
            self._two_pages(wiki, "ExclWidget")
            self._two_pages(wiki, "PlainWidget")
            out = check_concept_coverage.run(wiki)
            self.assertEqual(_findings_for_entity(out["findings"], "RefWidget"), [])    # skipped by tier
            self.assertEqual(_findings_for_entity(out["findings"], "ExclWidget"), [])   # skipped by exclude
            self.assertEqual(len(_findings_for_entity(out["findings"], "PlainWidget")), 1)  # still fires

    # T6 — config parse: tier_filter accepted only as a non-empty string, stripped.
    def test_t6_config_parse_tier_filter(self):
        def _cfg(body):
            with TemporaryDirectory() as tmp:
                wiki = _clone_fixture(Path(tmp) / "wiki")
                _write_config(wiki, body)
                return check_concept_coverage._load_concept_coverage_config(wiki)["tier_filter"]
        self.assertEqual(_cfg('tier_filter: "Authoritative"\n'), "Authoritative")
        self.assertEqual(_cfg('tier_filter: "  Authoritative  "\n'), "Authoritative")  # stripped
        self.assertIsNone(_cfg('tier_filter: ""\n'))        # empty -> OFF
        self.assertIsNone(_cfg('tier_filter: 123\n'))       # non-string -> OFF
        self.assertIsNone(_cfg("min_mentions: 2\n"))        # absent -> OFF

    # T7 — unknown-tier WARN: a present-but-unknown filtered tier emits a stderr WARN.
    def test_t7_unknown_tier_emits_stderr_warning(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki,
                "entities:\n"
                "  - canonical_name: Widget\n"
                "    tier: Bogus\n")
            _write_config(wiki, 'tier_filter: "Authoritative"\n')
            self._two_pages(wiki, "Widget")
            buf = io.StringIO()
            out = check_concept_coverage.run(wiki, stderr=buf)
            warned = buf.getvalue()
            self.assertIn("warning:", warned)
            self.assertIn("Bogus", warned)
            # WARN is advisory: the entry is still tier-skipped (Bogus != Authoritative).
            self.assertEqual(_findings_for_entity(out["findings"], "Widget"), [])

    def test_t7b_known_tier_emits_no_warning(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki,
                "entities:\n"
                "  - canonical_name: Widget\n"
                "    tier: References\n")
            _write_config(wiki, 'tier_filter: "Authoritative"\n')
            self._two_pages(wiki, "Widget")
            buf = io.StringIO()
            check_concept_coverage.run(wiki, stderr=buf)
            self.assertEqual(buf.getvalue(), "")  # References is known -> no WARN

    # T8 — empty/null tier fail-open (regression guard for the silent-drop defect).
    def test_t8_empty_and_null_tier_fail_open_included(self):
        for tier_line in ("    tier:\n", "    tier: null\n", "    tier: ~\n"):
            with self.subTest(tier_line=tier_line):
                with TemporaryDirectory() as tmp:
                    wiki = _clone_fixture(Path(tmp) / "wiki")
                    _write_roster(wiki,
                        "entities:\n"
                        "  - canonical_name: Widget\n" + tier_line)
                    _write_config(wiki, 'tier_filter: "Authoritative"\n')
                    self._two_pages(wiki, "Widget")
                    buf = io.StringIO()
                    out = check_concept_coverage.run(wiki, stderr=buf)
                    # MUST fire — an empty/null tier is treated Authoritative, never dropped.
                    self.assertEqual(
                        len(_findings_for_entity(out["findings"], "Widget")), 1,
                        "empty/null tier {!r} must fail-open to included".format(tier_line),
                    )
                    # And it is a clean default, not an "unknown tier" -> no WARN.
                    self.assertEqual(buf.getvalue(), "")

    # T9 — casefold match: a case-typo'd tier still matches (no silent drop).
    def test_t9_casefold_tier_match(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki,
                "entities:\n"
                "  - canonical_name: Widget\n"
                "    tier: authoritative\n")  # lowercase
            _write_config(wiki, 'tier_filter: "Authoritative"\n')
            self._two_pages(wiki, "Widget")
            buf = io.StringIO()
            out = check_concept_coverage.run(wiki, stderr=buf)
            self.assertEqual(len(_findings_for_entity(out["findings"], "Widget")), 1)
            self.assertEqual(buf.getvalue(), "")  # casefold-known -> no WARN

    # T10 — whitespace-padded tier is stripped before comparison.
    def test_t10_whitespace_padded_tier_stripped(self):
        with TemporaryDirectory() as tmp:
            wiki = _clone_fixture(Path(tmp) / "wiki")
            _write_roster(wiki,
                "entities:\n"
                "  - canonical_name: Widget\n"
                '    tier: "Authoritative "\n')  # trailing space
            _write_config(wiki, 'tier_filter: "Authoritative"\n')
            self._two_pages(wiki, "Widget")
            out = check_concept_coverage.run(wiki)
            self.assertEqual(len(_findings_for_entity(out["findings"], "Widget")), 1)


if __name__ == "__main__":
    unittest.main()
