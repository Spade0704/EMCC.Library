---
title: "Bootstrap — one-time wiki creation"
type: guide
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-24
dependencies: ["01-Architecture/Wiki-Structure", "01-Architecture/File-Manifest", "02-Operations/Sync"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §4.1"]
unverified_claims: []
---

# Bootstrap — one-time wiki creation

```bash
cd <wherever Codex is installed>
python bootstrap.py <target-wiki-path>
```

Creates the full wiki folder structure at `<target-wiki-path>`, copies all 15 scripts, drops in commented config templates, populates starter meta-pages.

## What Bootstrap creates

Starter meta-pages dropped in:

- `Home.md` — landing page.
- `00-Start-Here/Project-Overview`, `How-to-Use-This-Wiki`, `Glossary`, `Terminology-Rules`.
- `04-Contributing/Update-Cascade`, `File-Routing`, `Style-Guide`.
- `_confidential/Confidential_Profile.md` skeleton.
- `_context/CLAUDE_CONTEXT_RULES.md` (customizable per project).
- `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` (shipped verbatim — see Principle #2 / [[Sync]] hard-rules).
- `_canon/`, `_brain_dump/`, `_decisions/`, `_sources/`, `_sources/raw/`, `_inbox/` READMEs.
- `_decisions/ingest-log.md` (starter append-only log, v1.1).
- `_sources/raw/README.md` (explains read-only archive, v1.1).

Full file list: see [[File-Manifest]].

## After Bootstrap

The consuming project does Phases 3–7 of the [[Build-Workflow]] to populate content. Quick-reference: see [[Quickstart]] Appendix B.

## When Bootstrap runs

Exactly once per consuming project. Re-running Bootstrap against an existing wiki is not supported — for infrastructure refresh, use [[Sync]].

## Phase 1 questions Bootstrap implicitly answers

Bootstrap presumes the user has already answered the Phase-1 intake questions from [[Build-Workflow]] §7 — install path, Iron Soul reference availability, starting Codex version, whether to `git init` the new wiki, project-specific constraints.

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
- [[Build-Workflow]] — *topic: codex_operations, cross_link_generation*
- [[Claude-Behavior-Rules]] — *topic: codex_operations, cross_link_generation, librarian_persona*
- [[Ingest]] — *topic: codex_operations, cross_link_generation, ingest_procedure*
- [[Quickstart]] — *topic: codex_operations, cross_link_generation*
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
