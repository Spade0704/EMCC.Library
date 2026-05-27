---
title: "Folder Architecture — Three Folder Roles"
type: framework
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-24
dependencies: ["01-Architecture/Wiki-Structure", "01-Architecture/Design-Principles"]
public_pair: null
blocking_questions: []
topics: [codex_architecture, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_architecture, cross_link_generation]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §2.1"]
unverified_claims: []
---

> **ARCHIVED 2026-05-27 (S003b):** Historical reference. Superseded by `tasks/plans/portfolio-folder-structure-spec.md` §(a) Canonical Structure Spec + §(b) per-project punchlists. The "three folder roles" model was the Codex-internal precursor; F1–F12 portfolio resolution is the authoritative v1.1 model.
> Preserved for reference; do not update. Cross-link from current docs at your own risk.
> See `tasks/sessions.md` S003b close entry for the archival decision context.
> Original content below this line.

---

# Folder Architecture — Three Folder Roles

Codex's filesystem model divides everything into exactly three categories of folder.

## The tree

```
D:/claude/                              ← workspace root (or wherever)
│
├── _codex/                             ← THE TOOL. Exactly one of these.
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── PROJECT_WIKI_BUILD_SPEC.md
│   ├── bootstrap.py                    Creates new wikis from templates
│   ├── _scripts/                       Master copies of all 15 automation scripts
│   │   └── _lib/
│   │       └── frontmatter.py          Shared parser
│   ├── _config/                        Generic config templates (commented)
│   └── _template/                      Page templates for starter content
│
├── project-x/                          ← A consuming project
│   ├── (project x source code)/        Untouched by Codex
│   └── wiki/                           ← THE WIKI for project x
│       ├── Home.md
│       ├── 00-Start-Here/
│       ├── 01-<Domain-1>/
│       ├── _scripts/                   Synced from _codex/_scripts/
│       ├── _config/                    Customized for project x
│       ├── _canon/                     Project x ground-truth facts
│       ├── _sources/raw/               Project x ingested-source archive (v1.1)
│       └── _confidential/              Project x secrets
│
└── project-y/
    ├── (project y source)/
    └── wiki/                           ← Same structure, different content
```

## Three categories

| Category | Role | Count |
|---|---|---|
| `_codex/` | The tool itself | Exactly one |
| `project-x/`, `project-y/`, … | Consuming projects | Many, one per thing you work on |
| `project-x/wiki/`, … | Wikis (one per project) | One per project that wants docs |

## Implications

- **One Codex, many wikis.** Codex is installed once at a workspace root; each consuming project gets exactly one wiki under its own tree. Cross-wiki linking is out of scope.
- **Codex never holds project content.** It owns the tool, the templates, and the master scripts. The wiki holds the content. See [[Design-Principles]] #10.
- **Sync flows tool → wiki, never reverse.** Infrastructure improvements in `_codex/` cascade into `<project>/wiki/_scripts/` via [[Sync]]. The reverse — pulling content out of a wiki back into Codex — is forbidden.

For the per-wiki folder breakdown, see [[Wiki-Structure]].

<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Glossary]] — *topic: cross_link_generation, framework_durability*
- [[Automation-Scripts]] — *topic: codex_architecture, cross_link_generation*
- [[Configuration-Files]] — *topic: canon_discipline, codex_architecture, cross_link_generation*
- [[Cross-Link-Generation]] — *topic: cross_link_generation, framework_durability, frontmatter_schema*
- [[Design-Principles]] — *topic: canon_discipline, codex_architecture, cross_link_generation, framework_durability*
- [[File-Manifest]] — *topic: codex_architecture, cross_link_generation*
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
