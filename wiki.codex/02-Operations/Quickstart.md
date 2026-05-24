---
title: "Quickstart — after Codex is built"
type: guide
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-24
dependencies: ["02-Operations/Bootstrap", "02-Operations/Sync", "02-Operations/Ingest"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md App B"]
unverified_claims: []
---

# Quickstart — after Codex is built

For consuming projects after Codex v1.0 is in production. NOT for building Codex itself — for that, see [[Build-Workflow]].

```bash
# Bootstrap a new wiki
cd <Codex install path>
python bootstrap.py <new-wiki-path>

# Customize the new wiki:
#   1. Rename 01-Domain-1/, 02-Domain-2/ to project domains
#   2. Populate _config/*.yaml with project rules
#   3. Populate _canon/*.yaml with project facts
#   4. Customize _confidential/Confidential_Profile.md
#   5. Customize _context/CLAUDE_CONTEXT_RULES.md
#   6. Customize Home.md and 00-Start-Here/ pages

# Run dashboards
cd <new-wiki-path>
python _scripts/update_dashboards.py

# Ingest a new source (v1.1, ongoing)
python _scripts/scaffold_source.py <path-to-source-or-URL>
#   Then in Claude Code: "Ingest _inbox/<source>.md"

# Semantic lint (v1.1, periodic)
#   In Claude Code: "Run semantic lint" — writes to _dashboards/semantic_lint_report.md

# Sync with updated Codex (later, when Codex improves)
cd <wiki-path>
python _scripts/sync_from_kit.py <Codex install path> --dry-run
python _scripts/sync_from_kit.py <Codex install path>
python _scripts/update_dashboards.py
```

## Customization checklist (after Bootstrap)

| # | Step | Where |
|---|---|---|
| 1 | Rename `01-Domain-1/`, `02-Domain-2/` to your domain names. | Top-level wiki folders. |
| 2 | Populate `_config/*.yaml` with project-specific rules. | `_config/forbidden_terms.yaml`, `reveal_leak_patterns.yaml`, `cascade_map.yaml`, `steel_threads.yaml`, optional `concept_coverage.yaml`, optional `cross_link.yaml`. |
| 3 | Populate `_canon/*.yaml` with project facts. | `_canon/counts.yaml`, `roster.yaml`, `taxonomy.yaml`, `timeline.yaml`, `topics.yaml` (v1.3). |
| 4 | Customize `_confidential/Confidential_Profile.md`. | One file, project-specific secrets. |
| 5 | Customize `_context/CLAUDE_CONTEXT_RULES.md`. | Keep the four Q&A rules intact (see [[Build-Workflow]] Phase 4). |
| 6 | Customize `Home.md` and `00-Start-Here/` pages. | Replace `<Project Name>` markers. |

## Common runtime cycle

| Action | Command |
|---|---|
| Ingest a source | `scaffold_source.py <path>` → tell Claude "Ingest `_inbox/<name>`" |
| Refresh dashboards | `python _scripts/update_dashboards.py` |
| Periodic semantic lint | Tell Claude "Run semantic lint" |
| Pick up Codex improvements | `sync_from_kit.py <codex path> --dry-run` then `sync_from_kit.py <codex path>` |

See [[Bootstrap]], [[Sync]], [[Ingest]] for full operational details.

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
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
