---
title: "Codex File Manifest"
type: reference
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-24
dependencies: ["01-Architecture/Folder-Architecture", "01-Architecture/Automation-Scripts"]
public_pair: null
blocking_questions: []
topics: [codex_architecture, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_architecture, cross_link_generation]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §5"]
unverified_claims: []
---

> **ARCHIVED 2026-05-27 (S003b):** Historical reference. Superseded by `Index.md` ROOT_INDEX + `REORGANIZATION-INSTRUCTIONS.md` (machine-readable old-path → new-path manifest). The `_codex/` layout described below no longer exists — module source files moved to `Biz.Automation/wikisys.library/` per S002.
> Preserved for reference; do not update. Cross-link from current docs at your own risk.
> See `tasks/sessions.md` S003b close entry for the archival decision context.
> Original content below this line.

---

# Codex File Manifest

The files to build inside `_codex/` (the tool itself, not a consuming wiki).

```
_codex/
├── README.md                                Quickstart for humans
├── CHANGELOG.md                             Version history (first line: "# v1.0 — <date>")
├── PROJECT_WIKI_BUILD_SPEC.md               The portable spec (this document, copied)
├── bootstrap.py                             Scaffolder
│
├── _scripts/
│   ├── _lib/
│   │   ├── __init__.py
│   │   └── frontmatter.py                   Shared frontmatter + YAML-subset parser
│   │
│   ├── update_dashboards.py                 Orchestrator
│   ├── build_completion_dashboard.py
│   ├── validate_terminology.py
│   ├── validate_reveal_conceit.py
│   ├── validate_canon_integrity.py
│   ├── check_cascade.py
│   ├── check_cross_refs.py
│   ├── check_framework_briefing_sync.py
│   ├── check_canon_consistency.py
│   ├── collect_open_questions.py
│   ├── steel_thread_tracker.py
│   ├── build_canon_drift_report.py
│   ├── delta_source_docs.py
│   ├── sync_from_kit.py
│   ├── check_concept_coverage.py            (v1.1)
│   ├── scaffold_brain_dump.py
│   └── scaffold_source.py                   (v1.1)
│
├── _config/                                 Templates with commented examples
│   ├── README.md
│   ├── forbidden_terms.yaml
│   ├── reveal_leak_patterns.yaml
│   ├── cascade_map.yaml
│   ├── steel_threads.yaml
│   └── concept_coverage.yaml                (v1.1, optional)
│
└── _template/                               Page templates for starter content
    ├── Home.md
    ├── 00-Start-Here__SEP__Project-Overview.md
    ├── 00-Start-Here__SEP__How-to-Use-This-Wiki.md
    ├── 00-Start-Here__SEP__Glossary.md
    ├── 00-Start-Here__SEP__Terminology-Rules.md
    ├── 04-Contributing__SEP__Update-Cascade.md
    ├── 04-Contributing__SEP__File-Routing.md
    ├── 04-Contributing__SEP__Style-Guide.md
    ├── _canon__SEP__README.md
    ├── _canon__SEP__counts.yaml
    ├── _canon__SEP__roster.yaml
    ├── _canon__SEP__taxonomy.yaml
    ├── _canon__SEP__timeline.yaml
    ├── _brain_dump__SEP__README.md
    ├── _decisions__SEP__README.md
    ├── _decisions__SEP__ingest-log.md             (v1.1, starter append-only log)
    ├── _inbox__SEP__README.md
    ├── _sources__SEP__README.md                   (v1.1)
    ├── _sources__SEP__raw__SEP__README.md         (v1.1, explains read-only archive)
    ├── _context__SEP__CLAUDE_CONTEXT_RULES.md
    ├── _context__SEP__INGEST_PROCEDURE.md         (v1.1, ship verbatim — see separate file)
    ├── _context__SEP__SEMANTIC_LINT_PROCEDURE.md  (v1.1, ship verbatim — see separate file)
    └── _confidential__SEP__Confidential_Profile.md
```

Template filenames use `__SEP__` as a path separator placeholder. The `bootstrap.py` script replaces `__SEP__` with `/` when copying templates into the destination wiki.

## `__SEP__` rationale

Win32 reserves 9 characters in NTFS filenames (`<>:"|?*` plus NUL plus path-separators `/\`); using any of these as a placeholder produces silent MSYS2/Cygwin Private-Use-Area mangling on Windows (e.g. `|` U+007C → U+EF7C via POSIX-EFXX +0xEF00 offset) that breaks the `bootstrap.py` substitution contract at runtime. `__SEP__` is filesystem-safe across POSIX, Windows, and git tree representation, with zero real-filename collision risk.

See `tasks/lessons.md` 2026-05-16 entry on Win32 reserved chars in spec filename placeholders (Lesson #22 STANDARD).

## Shipped verbatim

`INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md` are shipped verbatim from the separate files accompanying the spec — do not paraphrase, do not shorten, do not "improve." They are Claude-facing contracts and their exact wording matters.

<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Glossary]] — *topic: cross_link_generation, framework_durability*
- [[Automation-Scripts]] — *topic: codex_architecture, cross_link_generation*
- [[Configuration-Files]] — *topic: canon_discipline, codex_architecture, cross_link_generation*
- [[Cross-Link-Generation]] — *topic: cross_link_generation, framework_durability, frontmatter_schema*
- [[Design-Principles]] — *topic: canon_discipline, codex_architecture, cross_link_generation, framework_durability*
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
