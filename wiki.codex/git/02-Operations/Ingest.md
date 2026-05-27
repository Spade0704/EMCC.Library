---
title: "Ingest — source integration"
type: guide
visibility: internal
completion: 45
status: outlined
last_updated: 2026-05-27
dependencies: ["01-Architecture/Wiki-Structure", "01-Architecture/Frontmatter-Schema", "02-Operations/Bootstrap"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation, ingest_procedure]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation, ingest_procedure]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §4.3"]
unverified_claims: []
---

# Ingest — source integration (v1.1)

```bash
# In Library (post-S002 canonical path):
python Biz.Automation/wikisys.library/_scripts/scaffold_source.py <path-or-url>
# In a v1.0-shape consuming wiki (post-Sync delivery; MI-16 carry):
python _scripts/scaffold_source.py <path-or-url>
# Then, in Claude Code:
# "Ingest _inbox/<source>.md"
```

Reads a new source document and integrates it into the wiki: extracts facts, routes them to `_canon/` (with confirmation) or to existing/new wiki pages, links related concepts, archives the original source, and appends an entry to `_decisions/ingest-log.md`.

Ingest is the **most frequent Codex operation** on a live project. Unlike Bootstrap (one-time) and Sync (occasional, initiated from Codex), Ingest happens whenever a new source enters orbit — an article, a meeting note, a spec revision, a transcript.

The full procedure Claude follows is documented in `_context/INGEST_PROCEDURE.md` (shipped by bootstrap). Summary below.

## The 7-step procedure

1. **Read** the source in `_inbox/<source>.md`.
2. **Extract** candidate facts, entities, and concepts. Group by: canon-worthy (numbers, named entities, timeline events), page-worthy (a concept deserving its own page), mention-worthy (belongs in an existing page).
3. **Route** each item:
   - Canon-worthy → propose YAML entry for `_canon/*.yaml`; **ask before writing**.
   - Page-worthy → create a new page under the correct domain folder with full frontmatter (`canon_sources` pointing at the archived source, `status: outlined` or higher).
   - Mention-worthy → update the existing page; cite the source.
   - Contradicts canon or an existing page → flag in the ingest log; **never silently overwrite**.
4. **Link** — add `[[wikilinks]]` between related pages. Update `Home.md` only if a new top-level section was created.
5. **Archive** — move the source from `_inbox/` to `_sources/raw/` (permanent, read-only archive). Update source frontmatter: `status: ingested`, `ingested_date: YYYY-MM-DD`.
6. **Log** — append an entry to `_decisions/ingest-log.md` naming: date, source filename, pages created, pages updated, canon entries added, contradictions flagged.
7. **Validate** — run `python _scripts/update_dashboards.py` (or `python Biz.Automation/wikisys.library/_scripts/update_dashboards.py` when running against Library's own wiki post-S002) and confirm no new validator errors.

## Writes / moves / never-touched

- **Writes:** `_canon/*.yaml` (with confirmation), new/updated wiki content pages, `_decisions/ingest-log.md`, source frontmatter (status), optionally `Home.md` (only if a new top-level section is created).
- **Moves:** `_inbox/<source>` → `_sources/raw/<source>` on successful ingest.
- **NEVER touched:** `_scripts/`, `_config/`, `_confidential/` (unless the user explicitly directs), `_brain_dump/`, unrelated content pages, `04-Contributing/`.

## Refusal conditions

Ingest refuses to run if:

- The source in `_inbox/` lacks required frontmatter (`source`, `ingested_date`, `status: pending_triage`). Run `scaffold_source.py` first.
- Canon contradictions are detected and the user has not confirmed either overwrite or quarantine.
- The wiki has uncommitted git changes from an unrelated session (override with `--force`).

## `--dry-run`

Ingest supports `--dry-run` to preview the full routing plan without writing anything. Recommended for the first ingest in any new project, and for any source over ~5k words.

## Related

- [[Wiki-Structure]] — `_inbox/` vs `_sources/raw/` semantics.
- [[Frontmatter-Schema]] — source-file vs content-page frontmatter contracts.
- [[Bootstrap]] — ships the `INGEST_PROCEDURE.md` and the ingest-log starter.
- `_context/INGEST_PROCEDURE.md` — the verbatim Claude-facing contract.

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
- [[Quickstart]] — *topic: codex_operations, cross_link_generation*
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
