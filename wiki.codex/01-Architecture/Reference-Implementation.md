---
title: "Reference Implementation — Iron Soul (brief)"
type: reference
visibility: internal
completion: 35
status: outlined
last_updated: 2026-05-24
dependencies: ["02-Operations/Ingest"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation, ingest_procedure, iron_soul_reference]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation, ingest_procedure, iron_soul_reference]
canon_sources:
  - "_sources/raw/CODEX_BUILD_SPEC_v1_3.md §6"
  - "_sources/raw/CODEX_BUILD_SPEC_v1_3.md App A"
unverified_claims: []
---

# Reference Implementation — Iron Soul (brief)

The spec uses **Iron Soul / Planet Scoria Prime** as its reference implementation (§6 and Appendix A). Iron Soul is an **external consumer wiki**, not part of Codex. It demonstrates the patterns but **predates the Ingest feature**.

This page is intentionally brief — Iron Soul internals are out of scope for this wiki. The page exists to record the relationship and the asymmetries.

## What Iron Soul provides

Iron Soul v3.3 is the working reference Codex was derived from. Every Codex script and template is a generalized version of what exists in the Iron Soul wiki. When implementing a Codex script, the Iron Soul filename at the matching path is the reference behavior.

Iron Soul demonstrates these patterns Codex needs to support:

- Internal frameworks with public briefing-guide pairs.
- A confidentiality conceit (Arc 8 reveal) preserved through validation.
- Brain dump quarantine pattern.
- Canon consistency across many cross-cutting facts.
- Custom config (`reveal_leak_patterns.yaml` uses `severity: info` to document approved-public terms).

## Headline reference facts (from Appendix A)

- **Version:** v3.3.
- **Pages:** 31 internal + 10 public + 8 auto-generated dashboards.
- **Validators:** 0 errors, 0 warnings on the canonical state.
- **Canon coverage:** 4 YAML files with 60+ facts.
- **Confidential profile:** 11 sections including Claude behavior rules.

## Asymmetry: Iron Soul predates Ingest

Iron Soul v3.3 pre-dates the v1.1 Ingest operation and the `_sources/raw/` archive. When building Codex:

- **Derive scripts/templates from Iron Soul** where a precedent exists.
- **Exception:** `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` come from the separate files accompanying the spec, NOT from Iron Soul.
- **Exception:** `check_concept_coverage.py` and `scaffold_source.py` have no Iron Soul precedent and must be implemented from spec alone.

## Transformation pattern (sanitization)

When deriving a Codex template from an Iron Soul file: replace project-specific entries with commented examples and leave the file structurally valid (e.g., `rules: []` for an empty config).

If Iron Soul is not provided as a reference, build templates from the spec alone.

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
