---
title: "Codex — Home"
type: overview
visibility: internal
completion: 30
status: outlined
last_updated: 2026-06-18
dependencies: ["01-Architecture/Overview", "02-Operations/Bootstrap", "02-Operations/Librarian"]
public_pair: null
blocking_questions: []
topics: [codex_architecture, codex_operations, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Input-Validation.md, 01-Architecture/Link-Graph-Integrity.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Orchestrator-Participation.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md]
tags: [codex_architecture, codex_operations, cross_link_generation]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §1"]
unverified_claims: []
---

# Codex — Home

Landing page for the **Codex** wiki. This wiki documents the Library module's
two distinct things — keep them separate:

- **Codex** (the engine) — the scaffolding-and-sync tool that creates and
  maintains markdown documentation wikis for other projects. *How* raw material
  becomes a structured, validated wiki. Start with [[Overview]].
- **The Librarian** (the agent) — the single canonical Codex persona that
  *operates* the engine: ingests sources, curates pages, maintains canon, runs
  the dashboards. *Who* does the work. See [[Librarian]].

This wiki documents both — Codex's architecture, operations, the Librarian
agent, and the build-spec they derive from.

For a one-page orientation, start with [[Overview]]; for the agent, [[Librarian]].

## Table of Contents

### Start Here

- [[00-Start-Here/Project-Overview]] — what `Codex` is, why it exists, who it serves
- [[00-Start-Here/How-to-Use-This-Wiki]] — navigation, conventions, status bands
- [[00-Start-Here/Glossary]] — terms and definitions
- [[00-Start-Here/Terminology-Rules]] — forbidden-term policy and rationale

### 01 — Architecture

What Codex is — folders, schema, scripts, principles.

- [[Overview]] — Codex in one page
- [[Folder-Architecture]] — the three folder roles (`_codex/`, consuming projects, wikis)
- [[Wiki-Structure]] — what `bootstrap.py` creates in each wiki
- [[Frontmatter-Schema]] — the YAML header contract + meta-schema enums
- [[Input-Validation]] — fail-closed tree-confinement + projectname validation (route_inbox + bootstrap)
- [[Link-Graph-Integrity]] — link-resolver coherence, escapes-root signal, whole-graph integrity validator
- [[Automation-Scripts]] — 15 base + 3 v1.3 cross-link scripts, orchestrator pipeline, health-summary
- [[Configuration-Files]] — `_config/` and `_canon/` schemas (+ `cross_link.yaml`, `topics.yaml`)
- [[Cross-Link-Generation]] — v1.3 marker contract, plug-in interface, idempotency
- [[Design-Principles]] — the 13 load-bearing rules
- [[File-Manifest]] — every file to build inside `_codex/` (`__SEP__` rationale)
- [[Reference-Implementation]] — Iron Soul as reference (brief; external context)

### 02 — Operations

How to drive Codex — the Librarian agent, Bootstrap, Sync, Ingest, build workflow, quickstart.

- [[Librarian]] — the agent that operates Codex (the single canonical persona; drives the operations below)
- [[Bootstrap]] — one-time wiki creation
- [[Sync]] — ongoing infrastructure refresh (overwrite / merge / never-touched matrix)
- [[Ingest]] — source integration (most frequent operation; refusal conditions; `--dry-run`)
- [[Build-Workflow]] — the 8 phases for building Codex itself
- [[Claude-Behavior-Rules]] — hard rules, operating preferences, red flags
- [[Quickstart]] — Appendix B reference for consuming projects after Codex is built
- [[Orchestrator-Participation]] — Librarian in EMCC cascades; Codex gates still bind (2026-06-03)

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

### Protocol canon (Codex spec documents)

The authoritative spec docs the overviews above drill down into (the `canon_sources`
the derived pages cite). Read these for exact wording / numbers — **spec wins** any
contradiction with a derived page.

- [[codex/CODEX_BUILD_SPEC_v1_4]] — the authoritative Codex build specification (single canonical version; v1.4 adds §9 Asset Registry — v1_3 retained with a deprecation banner)
- [[codex/PROJECT_WIKI_BUILD_SPEC]] — what `bootstrap.py` materializes for a consuming project
- [[codex/CODEX_LIBRARIAN]] — the Librarian agent specification (the persona this module ships)
- [[codex/INGEST_PROCEDURE]] — source-ingest procedure (shipped verbatim into bootstrapped wikis)
- [[codex/SEMANTIC_LINT_PROCEDURE]] — semantic-lint procedure (shipped verbatim)
- [[codex/SYNC_STAMP_CONTRACT]] — the `SYNC-STAMP.json` schema + drift vocabulary
- [[codex/Obsidian-Setup-Guide]] — consumer guidance for Obsidian users
- [[codex/codex-build-progress]] — archived pre-extraction build snapshot (historical)

## Status

This wiki was scaffolded by Codex and seeded by the v1.3 spec ingest (2026-05-24). The two distinct things this module ships are both covered: **Codex** (the engine) by the [[Overview]] plus the full 01-Architecture domain, and **the Librarian** (the agent) by [[Librarian]] — each a derived overview citing the `wiki.codex/git/codex/*` canon. Most pages sit at `status: outlined` — sections are named and key claims cited, but they are not yet promoted through the status bands (`gap → outlined → solid → ready`); a few 00-Start-Here pages remain raw template stubs at `status: gap`. Home stays `outlined` until that tail is filled. See [[Frontmatter-Schema]] for the status-band rules.

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
