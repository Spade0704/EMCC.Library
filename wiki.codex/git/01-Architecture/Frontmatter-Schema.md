---
title: "Frontmatter Schema"
type: framework
visibility: internal
completion: 45
status: outlined
last_updated: 2026-05-27
dependencies: ["01-Architecture/Design-Principles", "01-Architecture/Cross-Link-Generation"]
public_pair: null
blocking_questions: []
topics: [cross_link_generation, framework_durability, frontmatter_schema, status_bands]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [cross_link_generation, framework_durability, frontmatter_schema, status_bands]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §2.3"]
unverified_claims: []
---

# Frontmatter Schema

The YAML header on every content page. Codex's scripts read frontmatter as the API (Design Principle #5 — see [[Design-Principles]]). Hard-coding metadata in body text is an anti-pattern.

## Content-page schema (v1.3)

```yaml
---
title: "Human-Readable Page Title"
type: framework | reference | guide | overview | episode | dashboard | profile | brain_dump | decision | context_rules
visibility: internal | public | confidential
completion: 0-100
status: gap | outlined | solid | ready
phase: 0-N                                 # optional
last_updated: YYYY-MM-DD
dependencies: ["Other-Page"]
public_pair: "public/Briefing.md" | null
blocking_questions: ["What is X?"]
canon_sources: ["_sources/raw/<file>.md §2.1"]   # required for status: ready
unverified_claims: []                      # must be empty for status: ready
source: "Free-text citation (legacy)"
allow_forbidden_terms: true | false        # optional escape hatch
generated: true                            # auto-gen dashboards only

# v1.3 additions (optional, all default to []):
topics: []              # list of topic names; human-curated + script-augmented (additive)
related_files: []       # repo-relative paths; SCRIPT-MANAGED — do not hand-edit
tags: []                # Obsidian tags; HUMAN-OWNED, optional script-mirroring from topics

# Accuracy tier (optional; see "Accuracy fields" below):
consequence: high | low                    # absent/unrecognized/duplicate -> fail-safe HIGH
cite_anchor: "verbatim source ref"         # required (non-empty) when consequence resolves HIGH

# Brain dump entries only:
dump_status: exploring | validated | migrated | superseded | rejected
migrated_to: ["Path/To/Canon-Page.md"]
---
```

## Status bands (page-completion enum — Codex meta-schema)

| Band | Completion | Meaning |
|---|---|---|
| `gap` | < 30 | Placeholder, stub, or empty scaffolding. No load-bearing content yet. |
| `outlined` | 30–54 | Sketch present. Sections named; key claims may be unsourced. |
| `solid` | 55–79 | Substantive draft. Most claims cited; structure stable. |
| `ready` | ≥ 80 | Production-grade. `canon_sources` populated; `unverified_claims: []`. |

A page with `status: ready` MUST have at least one entry in `canon_sources` AND an empty `unverified_claims` list (`validate_canon_integrity.py` enforces this).

## `type` enum (page-type — Codex meta-schema)

| Value | Purpose |
|---|---|
| `framework` | Load-bearing structural rules. **Durability tier 1** — mirror to external durable storage (see Principle #12). |
| `reference` | Inventory derived from frameworks + sources. **Durability tier 2** — only as durable as the wiki itself. |
| `guide` | Operational how-to. |
| `overview` | High-level orientation; landing pages, domain indexes. |
| `episode` | Inventory entry (per project use). |
| `dashboard` | Auto-generated. `generated: true` set. |
| `profile` | Confidential or public profile pages. |
| `brain_dump` | Quarantined speculation. NOT canon. See Principle #9. |
| `decision` | Append-only decision-log entries. |
| `context_rules` | Claude operating rules (`_context/*`). |

## `visibility` enum (Codex meta-schema)

| Value | Meaning |
|---|---|
| `internal` | Internal collaborator scope. Default for new content. |
| `public` | Shareable. Subject to `validate_reveal_conceit.py` and forbidden-term scanning. |
| `confidential` | Project secrets, business strategy, Claude behavior rules. Never publish. |

Direction is one-way: `internal → public`, never reverse. See [[Design-Principles]] #3.

## Accuracy fields — `consequence` / `cite_anchor` (Codex canon)

The accuracy contract behind verbatim-only / cite-always / correct-refusal. Two optional content-page fields lock when a page must carry a source citation:

| Field | Type | Meaning |
|---|---|---|
| `consequence` | `high` \| `low` | The page's accuracy tier. **Fail-safe HIGH:** absent, unrecognized, or duplicated → resolves to HIGH. Only an explicit `consequence: low` opts out. |
| `cite_anchor` | non-empty string | A verbatim source reference. **Required when `consequence` resolves HIGH** (`cite_required` is the derived rule). Whitespace-only counts as absent. |

Enforced by `_scripts/_lib/doc_lint.py::check_consequence` and surfaced by the `audit_citations.py` audit (report-only by default; `--enforce` promotes findings to errors per-wiki once migrated).

> **Presence-Not-Accuracy caveat.** This lint verifies that a citation *exists* on a HIGH page. It does **not** verify that the quote is verbatim, that the anchor resolves, or that a refusal was the correct call. It is a presence check, not a correctness check — do not read a green run as "the content is accurate."

## Source-file frontmatter (v1.1, reduced)

Sources in `_inbox/` and `_sources/raw/` use a reduced schema:

```yaml
---
source: "Original citation (URL, book, conversation, etc.)"
ingested_date: YYYY-MM-DD                  # date scaffolded, not date ingested
status: pending_triage | ingested          # supersedes content-page status values
---
```

`scaffold_source.py` creates these with `status: pending_triage`. Ingest flips them to `ingested` on archive.

## v1.3 — Cross-link frontmatter contract

Three optional fields, all defaulting to empty list when absent:

- **`topics: []`** — every value MUST resolve to an entry in `_canon/topics.yaml` (validated by #18 `validate_topic_registry.py`). Humans add topics they know apply; `build_topic_index.py` (#16) appends additional topics it detects via keyword + TF-IDF, **never removes** human-entered values.
- **`related_files: []`** — managed exclusively by `cross_link_topics.py` (#17). Single source of truth for the page's outgoing topical links. Body "See also" block is a rendered view of this list.
- **`tags: []`** — human-owned ad-hoc workflow markers (e.g. `studythisnow`, `review-q3`). If `_config/cross_link.yaml` enables tag mirroring (default `mirror_from: [topics]`), #16 appends topic-derived tags additively. Codex NEVER removes from `tags:` regardless of config — same contract as `topics:`.

Inline `#tag` syntax in body prose is preserved untouched by all body-scanning validators. Codex manages frontmatter `tags:` only — inline tags are pure human territory. See [[Cross-Link-Generation]].

## Meta-schema vs taxonomy

The three enums above (`type`, `status`, `visibility`) are **Codex's frontmatter meta-schema**, not Library subject-matter taxonomy. They are documented here as content, NOT mirrored into `_canon/taxonomy.yaml` (which holds subject categories only).

<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Glossary]] — *topic: cross_link_generation, framework_durability*
- [[Automation-Scripts]] — *topic: codex_architecture, cross_link_generation*
- [[Configuration-Files]] — *topic: canon_discipline, codex_architecture, cross_link_generation*
- [[Cross-Link-Generation]] — *topic: cross_link_generation, framework_durability, frontmatter_schema*
- [[Design-Principles]] — *topic: canon_discipline, codex_architecture, cross_link_generation, framework_durability*
- [[File-Manifest]] — *topic: codex_architecture, cross_link_generation*
- [[Folder-Architecture]] — *topic: codex_architecture, cross_link_generation*
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
