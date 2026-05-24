---
title: "Sync — ongoing infrastructure refresh"
type: guide
visibility: internal
completion: 45
status: outlined
last_updated: 2026-05-24
dependencies: ["02-Operations/Bootstrap", "01-Architecture/Automation-Scripts"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §4.2"]
unverified_claims: []
---

# Sync — ongoing infrastructure refresh

```bash
cd <wiki path>
python _scripts/sync_from_kit.py <path-to-Codex-installation>
```

Pulls updated infrastructure from Codex into the consuming wiki. Sync flows **tool → wiki, never reverse** (Principle #4).

## Sync matrix — overwrite / merge / never-touched

| Behavior | Targets |
|---|---|
| **Overwritten** | `_scripts/` (the 15 automation scripts) |
| **Overwritten** | `04-Contributing/PROJECT_WIKI_BUILD_SPEC.md` |
| **Overwritten** | `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` (shipped procedures — not customized per project) |
| **Merge-new-only** | `_config/` and `_template/` files (existing customized files are preserved; new template files are added) |
| **NEVER touched** | `00-Start-Here/`, `01-*/`, `_canon/`, `_sources/raw/`, `_confidential/`, `_decisions/`, `_brain_dump/`, `_dashboards/`, `_inbox/`, `public/`, `Home.md`, `README.md` |
| **NEVER touched** | `_context/CLAUDE_CONTEXT_RULES.md` (customized per project) |

## Safety rails

- Refuses to run if the wiki has uncommitted git changes. Override: `--force`.
- Supports `--dry-run` to preview changes before writing.

## When Sync runs

- After Codex itself receives a fix or feature in the master `_scripts/`.
- Periodically, to pick up shipped-procedure updates (`INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`).
- NEVER as a substitute for [[Ingest]] — Sync handles infrastructure, not content.

## Relationship to other operations

- [[Bootstrap]] creates the initial tree; Sync refreshes infrastructure inside it.
- [[Ingest]] adds content; Sync never touches content.
- See [[Automation-Scripts]] for the list of files Sync overwrites.

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
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
