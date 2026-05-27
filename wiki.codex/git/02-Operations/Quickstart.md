---
title: "Quickstart — after Codex is built"
type: guide
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-27
dependencies: ["02-Operations/Bootstrap", "02-Operations/Sync", "02-Operations/Ingest"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md App B"]
unverified_claims: []
---

# Quickstart — after Codex is built

For consuming projects using Codex v1.1 (the canonical-output bootstrap shipped via Library S002, 2026-05-27). NOT for building Codex itself — for that, see [[Build-Workflow]].

```bash
# Bootstrap a new wiki (v1.1 CLI: <projectname> positional + variant flag)
cd <Library checkout>
python bootstrap.py <projectname> [--minimal | --code | --website | --full]
# Default: --full. Output is scaffold-only (no script copy).

# Customize the new project:
#   1. Add topic folders under wiki.<projectname>/git/ (the canonical content side)
#   2. Populate Biz.Automation/wikisys.<projectname>/_config/*.yaml with project rules
#   3. Populate Biz.Automation/wikisys.<projectname>/_canon/*.yaml with project facts
#   4. Customize CLAUDE.md, Index.md, Cheatsheet.md at project root
#   5. Add Biz.Automation/<automationname>/ automations as needed; pair with wiki.<name>/git/<automationname>.doc/

# Run dashboards (scripts execute from Library checkout against the consumer wiki)
cd <Library checkout>
python Biz.Automation/wikisys.library/_scripts/update_dashboards.py --wiki <consumer-wiki-path>

# Ingest a new source (v1.1, ongoing)
python Biz.Automation/wikisys.library/_scripts/scaffold_source.py <path-to-source-or-URL>
#   Then in Claude Code: "Ingest _inbox/<source>.md"

# Semantic lint (v1.1, periodic)
#   In Claude Code: "Run semantic lint" — writes to _dashboards/semantic_lint_report.md

# Sync with updated Library (MI-16: v1.0 contract still active — script copy + procedure delivery)
cd <v1.0-shape consumer wiki>
python _scripts/sync_from_kit.py <Library checkout> --dry-run
python _scripts/sync_from_kit.py <Library checkout>
# Note: post-S002 sync against v1.1-bootstrapped wikis is the MI-16 deferred carry; see [[Sync]].
```

## Customization checklist (after Bootstrap, v1.1 canonical-output)

| # | Step | Where |
|---|---|---|
| 1 | Add topic folders under `wiki.<projectname>/git/`. | Canonical content side. Public by default; private content goes under `wiki.<name>/local/`. |
| 2 | Populate `Biz.Automation/wikisys.<projectname>/_config/*.yaml` with project-specific rules. | `forbidden_terms.yaml`, `reveal_leak_patterns.yaml`, `cascade_map.yaml`, `steel_threads.yaml`, optional `concept_coverage.yaml`, optional `cross_link.yaml`. |
| 3 | Populate `Biz.Automation/wikisys.<projectname>/_canon/*.yaml` with project facts. | `counts.yaml`, `roster.yaml`, `taxonomy.yaml`, `timeline.yaml`, `topics.yaml`. |
| 4 | Customize root `CLAUDE.md`, `Index.md`, `Cheatsheet.md` stubs that bootstrap emitted. | Project root. |
| 5 | (Optional) Add `Biz.Automation/<automationname>/` per automation; pair each with `wiki.<name>/git/<automationname>.doc/`. | F9 pairing contract. |

## Common runtime cycle (v1.1)

| Action | Command |
|---|---|
| Ingest a source | `Biz.Automation/wikisys.library/_scripts/scaffold_source.py <path>` → tell Claude "Ingest `_inbox/<name>`" |
| Refresh dashboards | `python Biz.Automation/wikisys.library/_scripts/update_dashboards.py` |
| Periodic semantic lint | Tell Claude "Run semantic lint" |
| Pick up Library improvements (MI-16: v1.0-shape consumers only) | `_scripts/sync_from_kit.py <Library path> --dry-run` then real run |

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
