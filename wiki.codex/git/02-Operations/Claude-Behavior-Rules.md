---
title: "Claude Code Behavior Rules (when building Codex)"
type: guide
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-24
dependencies: ["02-Operations/Build-Workflow", "01-Architecture/Design-Principles"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation, librarian_persona]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation, librarian_persona]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §8"]
unverified_claims: []
---

> **ARCHIVED 2026-05-27 (S003b):** Historical reference. Rules-when-building-Codex superseded — Codex is built. Runtime rules now live in the Librarian persona at `wiki.codex/git/codex/CODEX_LIBRARIAN.md` (authoritative spec, S002 v1.1 extension) + `.claude/personas/CLAUDE.librarian.md` (Claude Code drop-in).
> Preserved for reference; do not update. Cross-link from current docs at your own risk.
> See `tasks/sessions.md` S003b close entry for the archival decision context.
> Original content below this line.

---

# Claude Code Behavior Rules (when building Codex)

When the spec is loaded as project knowledge and **Codex is being built**, follow these rules. These are distinct from the runtime Librarian persona (declared in `_context/CODEX_LIBRARIAN.md` and `.claude/personas/CLAUDE.librarian.md`) that operates inside *consumed* wikis.

## Hard Rules

1. **Never use external Python packages.** Pure stdlib. Period.
2. **Never edit files outside the Codex install path** unless the user explicitly directs (e.g., for self-test bootstraps to `/tmp/`).
3. **Always run a self-test bootstrap** before declaring Codex complete.
4. **Always show the user the file manifest** at the end of the build.
5. **If the Iron Soul reference implementation is available, derive templates from it.** Do not invent template content from scratch when a working reference exists. Exception (v1.1): `INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md` ship verbatim from the spec's accompanying files, not from Iron Soul.

## Operating Preferences

6. **Build in the order of [[Build-Workflow]] phases.** Don't write `bootstrap.py` before the scripts and templates exist.
7. **Test every script in isolation** as soon as it's written, before moving to the next.
8. **Use the same frontmatter parser** in every script (DRY — `_lib/frontmatter.py` is shared).
9. **Document operational caveats inline** as code comments, especially around regex tips, escape hatches, and cross-platform path handling.

## Red Flags (Stop and Ask)

- The user asks for a feature not in this spec — confirm scope before adding.
- A script needs an external library — find a stdlib alternative or escalate.
- The reference implementation contradicts this spec — flag the conflict, ask which to follow.
- **v1.1-specific:** the two shipped procedures (`INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`) are missing from the build project — stop and request them; do not invent substitutes.

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
- [[Ingest]] — *topic: codex_operations, cross_link_generation, ingest_procedure*
- [[Quickstart]] — *topic: codex_operations, cross_link_generation*
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
