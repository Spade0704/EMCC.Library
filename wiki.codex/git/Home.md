---
title: "Codex — Home"
type: overview
visibility: internal
completion: 30
status: outlined
last_updated: 2026-05-24
dependencies: ["01-Architecture/Overview", "02-Operations/Bootstrap"]
public_pair: null
blocking_questions: []
topics: [codex_architecture, codex_operations, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md]
tags: [codex_architecture, codex_operations, cross_link_generation]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §1"]
unverified_claims: []
---

# Codex — Home

Landing page for the **Codex** wiki. Codex is a scaffolding-and-sync tool that creates and maintains markdown documentation wikis for other projects. This wiki documents Codex itself — its architecture, operations, and the build-spec it derives from.

For a one-page orientation, start with [[Overview]].

## Table of Contents

### Start Here

- [[00-Start-Here/Project-Overview]] — what `Codex` is and why it exists
- [[00-Start-Here/How-to-Use-This-Wiki]] — navigation, conventions, status bands
- [[00-Start-Here/Glossary]] — terms and definitions
- [[00-Start-Here/Terminology-Rules]] — forbidden-term policy and rationale

### 01 — Architecture

What Codex is — folders, schema, scripts, principles.

- [[Overview]] — Codex in one page
- [[Folder-Architecture]] — the three folder roles (`_codex/`, consuming projects, wikis)
- [[Wiki-Structure]] — what `bootstrap.py` creates in each wiki
- [[Frontmatter-Schema]] — the YAML header contract + meta-schema enums
- [[Automation-Scripts]] — 15 base + 3 v1.3 cross-link scripts, orchestrator pipeline, health-summary
- [[Configuration-Files]] — `_config/` and `_canon/` schemas (+ `cross_link.yaml`, `topics.yaml`)
- [[Cross-Link-Generation]] — v1.3 marker contract, plug-in interface, idempotency
- [[Design-Principles]] — the 13 load-bearing rules
- [[File-Manifest]] — every file to build inside `_codex/` (`__SEP__` rationale)
- [[Reference-Implementation]] — Iron Soul as reference (brief; external context)

### 02 — Operations

How to drive Codex — Bootstrap, Sync, Ingest, build workflow, quickstart.

- [[Bootstrap]] — one-time wiki creation
- [[Sync]] — ongoing infrastructure refresh (overwrite / merge / never-touched matrix)
- [[Ingest]] — source integration (most frequent operation; refusal conditions; `--dry-run`)
- [[Build-Workflow]] — the 8 phases for building Codex itself
- [[Claude-Behavior-Rules]] — hard rules, operating preferences, red flags
- [[Quickstart]] — Appendix B reference for consuming projects after Codex is built

### Contributing

- [[04-Contributing/Update-Cascade]] — how changes propagate through the wiki
- [[04-Contributing/File-Routing]] — which folder for which content
- [[04-Contributing/Style-Guide]] — markdown + frontmatter conventions

### Infrastructure (read-only context)

- `_context/CLAUDE_CONTEXT_RULES.md` — project-specific Claude operating rules
- `_context/INGEST_PROCEDURE.md` — source-ingest procedure (shipped verbatim)
- `_context/SEMANTIC_LINT_PROCEDURE.md` — semantic-lint procedure (shipped verbatim)
- `_context/CODEX_LIBRARIAN.md` — Librarian persona declaration (canonical)
- `.claude/personas/CLAUDE.librarian.md` — Librarian persona drop-in (summary form)

## Status

This wiki was scaffolded by Codex and seeded by the v1.3 spec ingest (2026-05-24). Pages currently sit at `status: outlined` — sections are named and key claims cited, but most pages are sketches not yet promoted through the status bands (`gap → outlined → solid → ready`). See [[Frontmatter-Schema]] for the status-band rules.

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
<!-- codex:see-also:end -->
