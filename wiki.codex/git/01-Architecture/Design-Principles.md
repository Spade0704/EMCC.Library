---
title: "Design Principles (13)"
type: framework
visibility: internal
completion: 45
status: outlined
last_updated: 2026-05-27
dependencies: []
public_pair: null
blocking_questions: []
topics: [canon_discipline, codex_architecture, cross_link_generation, framework_durability]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [canon_discipline, codex_architecture, cross_link_generation, framework_durability]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §3"]
unverified_claims: []
---

# Design Principles (13)

The structural rules of Codex. Load-bearing — mirror to external durable storage per Principle #12.

1. **One idea per page.** If a page grows past ~400 lines, split it.
2. **Authoritative source ≠ wiki.** The wiki is derived. Source wins conflicts. Cite via `canon_sources`.
3. **Internal/public split is directional.** Internal → Public, never reverse. Strip internal terminology unless confirmed public-safe. Public pages link only to other public pages.
4. **Update cascade is directional.** Source → Derived → Wiki. Never reverse.
5. **Frontmatter is the API.** Scripts read frontmatter. Don't hardcode page metadata.
6. **Validators have escape hatches.** `allow_forbidden_terms: true` exists by design.
7. **Dashboards are expendable.** Regenerated every run.
8. **Canon is the floor, not the ceiling.** `_canon/` captures facts that MUST be consistent. Pages can contain more — they just can't contradict canon.
9. **Brain dump is quarantine.** `_brain_dump/` is explicitly NOT canon. Promotion is always explicit.
10. **Codex is the tool, not the content.** Codex never holds project content. It creates and updates wikis. Each wiki holds its own content.
11. **Ingest proposes, humans dispose (v1.1).** Canon writes require confirmation. Contradictions get flagged, not overwritten. Archived sources are read-only.
12. **Frameworks are load-bearing; references are derived inventory.** Pages with `type: framework` are the structural rules of a project — they should exist in both the wiki and an external durable location (e.g. project knowledge files uploaded to a Claude project). Pages with `type: reference` (and similar inventory types: `episode`, etc.) are generated from frameworks plus sources, and are durable only to the extent that the wiki itself is. Losing a reference is recoverable from its framework; losing a framework is not. The wiki is the source of truth for both, but frameworks earn a second home.
13. **Cross-link injection is marker-bracketed and idempotent (v1.3).** Frontmatter `related_files: []` is the source of truth; the body "See also" block is its rendered view. Content between the see-also start and end markers (shown in [[Cross-Link-Generation]]) is regenerated every run; human prose around the markers is preserved. Humans curate `topics: []` to influence what gets linked; they do not hand-edit the rendered block. Frontmatter `tags: []` is human-owned but optionally mirror-augmented from `topics:` per `_config/cross_link.yaml`. Codex never removes entries from `tags:` — additive only.

## Cross-reference

Canonical count (from `_canon/counts.yaml`): **13 Codex design principles (v1.3)**.

<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Glossary]] — *topic: cross_link_generation, framework_durability*
- [[Automation-Scripts]] — *topic: codex_architecture, cross_link_generation*
- [[Configuration-Files]] — *topic: canon_discipline, codex_architecture, cross_link_generation*
- [[Cross-Link-Generation]] — *topic: cross_link_generation, framework_durability, frontmatter_schema*
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
