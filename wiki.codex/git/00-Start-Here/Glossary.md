---
title: "Codex — Glossary"
type: reference
visibility: internal
completion: 80
status: solid
last_updated: 2026-06-14
dependencies: []
public_pair: null
blocking_questions: []
canon_sources: []
unverified_claims: []
topics: [cross_link_generation, framework_durability]
tags: [cross_link_generation, framework_durability]
related_files: [.claude/personas/CLAUDE.librarian.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
---

# Codex — Glossary

Terms and definitions used across the `Codex` wiki. Populate this stub as new domain terms emerge; promote frequently-used terms into `_canon/roster.yaml` (named entities) or `_canon/taxonomy.yaml` (structured classifications) when they become load-bearing across multiple pages.

## Terms

### Codex

The **protocol / engine** — the *how*. The ingest and semantic-lint procedures, the
frontmatter schema, the validators and dashboards, R-XXXXX numbering, and the cross-link
graph that together turn raw material into a structured, validated wiki. See [[01-Architecture/Overview]].
Distinct from the **Librarian** (the agent that operates it).

### Librarian

The **agent / persona** that operates Codex — the *who*. It ingests sources, curates pages,
maintains canon, and runs the dashboards. See [[02-Operations/Librarian]]. The Codex engine is
the machine; the Librarian is its operator.

### Ingest

The procedure that turns a raw source document into structured, validated wiki pages —
extraction, frontmatter, citation, and cross-linking. Shipped verbatim as `INGEST_PROCEDURE.md`.
See [[02-Operations/Ingest]].

### Semantic lint

An inspection pass that surfaces concerns regex validators cannot see — page-to-page
contradictions, staleness against sources, concept gaps, and canon gaps. Complements (does not
replace) the structural validators. Shipped verbatim as `SEMANTIC_LINT_PROCEDURE.md`.

### Canon

The authoritative structured entities a page cites — `_canon/*.yaml` (roster, taxonomy,
timeline, topics). A `status: ready` page must cite its canon via `canon_sources`. See
[[01-Architecture/Configuration-Files]].

### Frontmatter

The YAML header contract carried by every content page (`title`, `type`, `status`,
`canon_sources`, `topics`, `related_files`, and more). The schema is the validation surface
for the whole wiki. See [[01-Architecture/Frontmatter-Schema]].

### Status bands

The page-maturity ladder: **`gap` → `outlined` → `solid` → `ready`**. A page is promoted only
as its sections are filled and its claims cited; `ready` is the canon-backed top band. See
[[01-Architecture/Frontmatter-Schema]].

### Cross-link graph

The wiki's context engine — **lexical, not vector**. The `related_files` frontmatter and
in-body `[[wikilinks]]` connect pages so loading one page and expanding one hop pulls the
related cluster. See [[01-Architecture/Cross-Link-Generation]].

### Wikilink

An intra-wiki reference: bare `[[Page-Name]]` or path-qualified `[[Folder/Page-Name]]`. Use the
folder prefix when a stem is ambiguous wiki-wide; the cross-reference validator resolves the
bare form by filename stem and the path-qualified form by full wiki-relative path. See
[[04-Contributing/Style-Guide]].

### Bootstrap

The one-time scaffolding of a new consumer-project wiki from the Codex kit (`bootstrap.py`).
Materializes the canonical folder layout, templates, and verbatim procedures. See
[[02-Operations/Bootstrap]].

### Sync

The ongoing refresh that pulls updated Codex infrastructure into a consumer wiki
(`sync_from_kit.py`), governed by the overwrite / merge / never-touched matrix and the
SYNC-STAMP drift contract. See [[02-Operations/Sync]].

### Dashboard

A generated roll-up under `_dashboards/` (completion, cross-references, canon integrity,
health, and more). Always `generated: true`; never hand-edited.

### Health summary

The single dashboard that rolls up completion percentage, canon contradictions, cascade
staleness, concept-coverage gaps, unverified-claim totals, cross-link coverage, and recent
ingest activity. Synthesized last in the `update_dashboards.py` pipeline.

### Verbatim discipline

The rule that `INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md` ship into bootstrapped
wikis **byte-identical** — never paraphrased, shortened, or "improved."

### Visibility / public_pair

Pages are `internal` by default; a public-facing version may be drafted as the page's
`public_pair`. The reveal-conceit validator guards against internal detail leaking into a
public page. Visibility is promoted per-page, never blended.

## Related pages

- [[00-Start-Here/Terminology-Rules]]
- [[00-Start-Here/How-to-Use-This-Wiki]]
- `_canon/roster.yaml`
- `_canon/taxonomy.yaml`

<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Automation-Scripts]] — *topic: codex_architecture, cross_link_generation*
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
