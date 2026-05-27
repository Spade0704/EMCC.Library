---
title: "Automation Scripts (17 + 5 audit scripts)"
type: reference
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-27
dependencies: ["01-Architecture/Configuration-Files", "01-Architecture/Cross-Link-Generation"]
public_pair: null
blocking_questions: []
topics: [codex_architecture, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_architecture, cross_link_generation]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §2.4"]
unverified_claims: []
---

# Automation Scripts (17 + 5 audit scripts)

All pure Python stdlib. No `pip install`. Canonical home post-S002:
`Biz.Automation/wikisys.library/_scripts/` (Library's source-of-truth
location per portfolio spec F6). v1.0-shape consumer wikis receive a
copy at `<wiki>/_scripts/` via `sync_from_kit.py` (MI-16 carry — sync
still on v1.0 contract; see [[Sync]] §"v1.1 known limitation").

## Base scripts (v1.0 + v1.1)

| # | Script | Purpose |
|---|---|---|
| 1 | `update_dashboards.py` | Master orchestrator — runs all aggregators and validators |
| 2 | `build_completion_dashboard.py` | Red/yellow/green completion dashboard |
| 3 | `validate_terminology.py` | Forbidden-terms scan, context-aware |
| 4 | `validate_reveal_conceit.py` | Leak scan on `visibility: public` pages |
| 5 | `validate_canon_integrity.py` | `status: ready` must have `canon_sources`, empty `unverified_claims` |
| 6 | `check_cascade.py` | Source → parallel doc mtime comparison |
| 7 | `check_cross_refs.py` | Broken `[[links]]` + orphan pages |
| 8 | `check_framework_briefing_sync.py` | Framework ↔ public-pair staleness |
| 9 | `check_canon_consistency.py` | Page contradictions vs `_canon/` AND page-to-page |
| 10 | `collect_open_questions.py` | Roll up all `blocking_questions` |
| 11 | `steel_thread_tracker.py` | Multi-layer feature completion |
| 12 | `build_canon_drift_report.py` | Snapshot + diff of `_canon/` over time |
| 13 | `delta_source_docs.py` | Diff two source-doc versions + cascade impact |
| 14 | `sync_from_kit.py` | Pull updated infrastructure from the Codex installation |
| 15 | `check_concept_coverage.py` | Entities in `_canon/roster.yaml` mentioned in pages but lacking a dedicated page (v1.1) |

Plus scaffolds:

| # | Script | Purpose |
|---|---|---|
| + | `scaffold_brain_dump.py` | Create a new brain dump entry |
| + | `scaffold_source.py` | Create a new `_inbox/` entry with frontmatter for ingest (v1.1) |
| + | `scaffold_<type>.py` | Project-specific scaffolds (added per project) |

## v1.3 cross-link additions

| # | Script | Purpose |
|---|---|---|
| 16 | `build_topic_index.py` | Builds topic → pages map from `_canon/topics.yaml` keywords + TF-IDF augmentation. Updates each page's frontmatter `topics: []` additively; mirrors topic-derived `tags:` per config. Writes `_dashboards/topic_index.md`. |
| 17 | `cross_link_topics.py` | For each multi-page topic, writes `related_files: []` in frontmatter AND a marker-bracketed "See also" block in body. Idempotent. Reads index from #16. |
| 18 | `validate_topic_registry.py` | Every page `topics:` value resolves in `_canon/topics.yaml` (error). Every registry topic has ≥1 member page (warning; orphan-topic detection). |

Canonical counts (from `_canon/counts.yaml`): 15 base + 3 cross-link = **17 automation scripts (v1.3 total).** Plus the 5 S002 audit scripts below.

## v1.1 audit scripts (S002, 2026-05-27)

Five new P0/P1 audit scripts shipped in Library S002 Phase B6 alongside the canonical-output `bootstrap.py` rewrite. All live in `Biz.Automation/wikisys.library/_scripts/` and emit dashboard markdown when run against a project tree.

| Script | Purpose |
|---|---|
| `audit_doc_pairing.py` | Audit `Biz.Automation/<automationname>/` paired with `wiki.<name>/git/<automationname>.doc/` per F9 pairing contract. Warns on unpaired automations. |
| `audit_gitignore.py` | Verify `.gitignore` excludes `wiki.*/local/` + heavy-asset patterns. Surfaces missing rules. |
| `route_inbox.py` | Two-phase Librarian helper: scan `0-Inbox/` → emit manifest → Librarian fills destinations → execute moves. |
| `audit_assets.py` | Heavy-file scan + duplicate detection inside `assets/` (or wherever assets live). |
| `audit_local_split.py` | Misclassification suspects in `wiki.*/local/` vs `wiki.*/git/` — flags content in wrong zone. |

All 5 emit 0 findings against Library's own tree (Library is a well-formed canonical-shape project per S002 close verification).

## Orchestrator pipeline (`update_dashboards.py`)

The orchestrator runs:

1. **Aggregators + validators** — the existing v1.0/v1.1/v1.2 pass (scripts #2–#15).
2. **Cross-link stage (v1.3)** — runs #16 → #17 → #18 in order. Pipeline order matters: #17 needs #16's index; #18 validates the post-#17 state.
3. **Health-summary synthesis** — `_dashboards/health.md` written after stages 1 and 2.

**Failure isolation:** #16/#17/#18 failure produces a stderr warning + non-zero exit but does NOT block existing aggregator/validator runs or other dashboard regeneration.

## Health summary (`_dashboards/health.md`)

Synthesized after the aggregator + validator + cross-link pass. Single dashboard rolling up:

- Completion percentage (from `build_completion_dashboard.py`).
- Canon contradictions (from `check_canon_consistency.py` page-vs-canon mode).
- Cascade staleness (from `check_cascade.py`).
- Concept-coverage gaps (from `check_concept_coverage.py`).
- Unverified-claim count (aggregated from page frontmatter `unverified_claims[]` totals).
- Recent ingest entries (most recent N entries from `_sources/raw/`'s ingest log per `INGEST_PROCEDURE.md`).
- **Cross-link coverage** (v1.3) — pages with ≥1 entry in `related_files`.

Health-summary frontmatter follows the standard 5-field dashboard contract:

```yaml
title: "Health"
type: dashboard
visibility: internal
generated: true
last_updated: YYYY-MM-DD
```

## Numbering note (reconciled)

Spec-table `#16/#17/#18` are the scripts' rows in §2.4. Their build-plan phases are **P18.2 / P18.3 / P18.4** respectively (with foundation lib `_lib/topics.py` at **P18.1**). Build-plan `P16` is the already-shipped `delta_source_docs.py` (S037) — a different axis. See [[Build-Workflow]] Phase 3 and [[Cross-Link-Generation]].

<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Glossary]] — *topic: cross_link_generation, framework_durability*
- [[Configuration-Files]] — *topic: canon_discipline, codex_architecture, cross_link_generation*
- [[Cross-Link-Generation]] — *topic: cross_link_generation, framework_durability, frontmatter_schema*
- [[Design-Principles]] — *topic: canon_discipline, codex_architecture, cross_link_generation, framework_durability*
- [[File-Manifest]] — *topic: codex_architecture, cross_link_generation*
- [[Folder-Architecture]] — *topic: codex_architecture, cross_link_generation*
- [[Frontmatter-Schema]] — *topic: cross_link_generation, framework_durability, frontmatter_schema, status_bands*
- [[Overview]] — *topic: codex_architecture, codex_operations, cross_link_generation, iron_soul_reference*
- [[Reference-Implementation]] — *topic: codex_operations, cross_link_generation, ingest_procedure, iron_soul_reference*
- [[Wiki-Structure]] — *topic: codex_architecture, cross_link_generation, ingest_procedure, status_bands*
- [[Bootstrap]] — *topic: codex_operations, cross_link_generation*
- [[Build-Workflow]] — *topic: codex_operations, cross_link_generation*
- [[Claude-Behavior-Rules]] — *topic: codex_operations, cross_link_generation, librarian_persona*
- [[Ingest]] — *topic: codex_operations, cross_link_generation, ingest_procedure*
- [[Quickstart]] — *topic: codex_operations, cross_link_generation*
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
