---
title: "Wiki Folder Structure"
type: framework
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-24
dependencies: ["01-Architecture/Folder-Architecture", "02-Operations/Bootstrap", "02-Operations/Ingest"]
public_pair: null
blocking_questions:
  - "Source CODEX_BUILD_SPEC_v1_3.md has no §2.6 — the section header is skipped between §2.5 and §2.7. Is this an intentional reservation, an upstream numbering bug, or content that was elided? Pending Scribe clarification."
topics: [codex_architecture, cross_link_generation, ingest_procedure, status_bands]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_architecture, cross_link_generation, ingest_procedure, status_bands]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §2.2"]
unverified_claims: []
---

# Wiki Folder Structure

What `bootstrap.py` creates inside `<project>/wiki/`.

```
<project>/wiki/
├── README.md                       Top-level overview for humans
├── Home.md                         Landing page; table of contents
├── 00-Start-Here/                  Overview, glossary, terminology, how-to
├── 01-Domain-1/                    Project-specific section (renamed in Phase 1; bare-name placeholder per Lesson #22 STANDARD 2nd sub-pattern Win32-safety — `<>` characters NTFS-illegal)
├── 02-Domain-2/                    Another project-specific section (bare-name placeholder; rename per Quickstart Appendix B step 1)
├── 04-Contributing/                Update cascade, file routing, style guide, SPEC
├── Attachments/                    Images, diagrams, PDFs
├── public/                         Public-facing briefing-guide pairs
├── scripts/                        Project-specific scripts (e.g. exporters)
├── _dashboards/                    Auto-generated. Never hand-edit.
├── _decisions/                     Append-only decision log (inc. ingest-log.md)
├── _inbox/                         Ephemeral holding pen for sources awaiting triage
├── _sources/raw/                   Permanent, read-only archive of ingested sources
├── _brain_dump/                    Quarantined unvalidated ideas — NOT canon
├── _canon/                         Structured ground-truth facts (YAMLs)
├── _context/                       Claude operating rules for this wiki
├── _scripts/                       The 15 automation scripts (synced from Codex)
├── _config/                        YAML config for validators
└── _confidential/                  Personal + Claude profile. NEVER publish.
```

Folders prefixed `_` are infrastructure. When sharing a wiki externally, exclude every `_`-prefixed folder except optionally `_decisions`.

## `_inbox/` vs `_sources/raw/` (v1.1)

`_inbox/` is **ephemeral** — a triage area for sources that arrived but haven't been ingested yet.

`_sources/raw/` is **permanent and read-only** — the archive of sources that *have* been ingested.

`canon_sources` on wiki pages cite paths in `_sources/raw/`, never `_inbox/`. Ingest moves files from `_inbox/` to `_sources/raw/` on success. See [[Ingest]] §4.3.

## Section-numbering gap (§2.6)

The source spec skips §2.6 — the document goes from §2.5 (Configuration Files) directly to §2.7 (Cross-link Generation Contract). This is flagged as a blocking question above; treat the gap as unintentional pending Scribe confirmation, and do not assume content was lost.

## Related

- [[Folder-Architecture]] — the three-folder workspace model that contains this per-wiki tree.
- [[Frontmatter-Schema]] — the contract every content page in this tree must satisfy.
- [[Bootstrap]] — how this tree is created.

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
- [[Bootstrap]] — *topic: codex_operations, cross_link_generation*
- [[Build-Workflow]] — *topic: codex_operations, cross_link_generation*
- [[Claude-Behavior-Rules]] — *topic: codex_operations, cross_link_generation, librarian_persona*
- [[Ingest]] — *topic: codex_operations, cross_link_generation, ingest_procedure*
- [[Quickstart]] — *topic: codex_operations, cross_link_generation*
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
