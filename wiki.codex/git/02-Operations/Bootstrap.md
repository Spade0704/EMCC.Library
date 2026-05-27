---
title: "Bootstrap — one-time wiki creation"
type: guide
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-27
dependencies: ["01-Architecture/Wiki-Structure", "01-Architecture/File-Manifest", "02-Operations/Sync"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §4.1", "tasks/plans/portfolio-folder-structure-spec.md §(c)"]
unverified_claims: []
---

# Bootstrap — one-time project creation (v1.1 canonical-output)

```bash
cd <Library checkout>
python bootstrap.py <projectname> [--minimal | --code | --website | --full]
```

- `<projectname>` — required positional. Used as folder name AND as suffix for `wikisys.<projectname>/` + `wiki.<projectname>/`. Filesystem-safe characters only.
- `--minimal` — thin braindump (aviation-career style). Root files + `tasks/` + `0-Inbox/` + `wiki.<name>/git/` only.
- `--code` — product-code project (Flutter, Python pkg, CLI). Adds `<product-code-root>/.gitkeep` + code-aware `.gitignore`.
- `--website` — public-website project (Next.js, Squarespace). Adds `website/.gitkeep` + web-aware `.gitignore`.
- `--full` — default. Full canonical tree per `tasks/plans/portfolio-folder-structure-spec.md` §(c).

## Scaffold-only contract (v1.1)

Bootstrap is **scaffold-only** post-S002. It emits `.gitkeep` placeholders + 4 root stubs (`CLAUDE.md`, `Index.md`, `Cheatsheet.md`, `.gitignore`) + 4 task stubs (`tasks/todo.md`, `sessions.md`, `lessons.md`, `archive.md`) per spec §(c) lines 864–895. **No script copy.** Consumers run scripts directly from a vendored / submodule / sibling-checkout of Library (MI-13 disposition: stdlib-only, no Python wheel distribution).

## What Bootstrap creates (`--full`)

The canonical tree (~40 ops on a clean target — 16 folders + 4 root stubs + 4 task stubs + assorted `.gitkeep`):

```
<projectname>/
├── 0-Inbox/.gitkeep
├── Biz.Automation/
│   ├── wikisys.<projectname>/
│   │   ├── _scripts/.gitkeep
│   │   ├── _template/.gitkeep
│   │   ├── _config/.gitkeep
│   │   └── _canon/.gitkeep
│   └── .gitkeep
├── wiki.<projectname>/
│   ├── local/.gitkeep
│   └── git/
│       ├── raw/.gitkeep
│       └── ideas/.gitkeep
├── tasks/{todo,sessions,lessons,archive}.md
├── assets/{logos,brand,photos,videos,designs,generated}/.gitkeep
├── Index.md
├── CLAUDE.md
├── Cheatsheet.md
└── .gitignore
```

`_context/` + `_decisions/` are Codex-pattern optionals; consumers add them as needed (only Library uses them today).

## After Bootstrap

The consuming project populates `wiki.<name>/git/` topic folders + `wikisys.<name>/_config/` + `_canon/` content. Quick-reference: [[Quickstart]].

## When Bootstrap runs

Exactly once per consuming project. Re-running Bootstrap against an existing project is not supported — for ongoing infrastructure refresh, use [[Sync]].

## MI-16 carry — sync still on v1.0 contract

`sync_from_kit.py` ships at the v1.0 contract: copies scripts into a `_scripts/` directory inside the consuming wiki and ships procedure docs to `_context/`. v1.1 bootstrap is scaffold-only and does NOT produce that `_scripts/` directory, so a freshly-bootstrapped v1.1 project is misaligned with what sync expects to find. Resolution: two coupled S004 decisions — (a) where post-v1.1 sync delivers procedure docs, (b) how legacy v1.0 wikis migrate forward. See `MIGRATION-ISSUES.md` MI-16 and `tasks/sessions.md` Session 2 close entry.

## Verification recipe

After bootstrap, verify:

```bash
python bootstrap.py <projectname> --full --yes
# Expect: 40 ops on a clean target (Library's own S002 close verification).
```

The canonical tree must match `tasks/plans/portfolio-folder-structure-spec.md` §(c) lines 864–895 exactly. See AC2 in Library S002 acceptance criteria for the historical baseline.

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
