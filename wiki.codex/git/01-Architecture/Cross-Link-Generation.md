---
title: "Cross-Link Generation Contract (v1.3)"
type: framework
visibility: internal
completion: 45
status: outlined
last_updated: 2026-05-27
dependencies: ["01-Architecture/Frontmatter-Schema", "01-Architecture/Configuration-Files", "01-Architecture/Automation-Scripts"]
public_pair: null
blocking_questions: []
topics: [cross_link_generation, framework_durability, frontmatter_schema]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [cross_link_generation, framework_durability, frontmatter_schema]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §2.7"]
unverified_claims: []
---

# Cross-Link Generation Contract (v1.3)

Topical "See also" injection: a per-project topic registry, TF-IDF over page scan fields, and an optional project-local linker plug-in. Pure stdlib for the default path.

## Marker contract (mandatory)

`cross_link_topics.py` injects a "See also" block bracketed by literal markers:

```markdown
<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Glossary]] — *topic: cross_link_generation, framework_durability*
- [[Automation-Scripts]] — *topic: codex_architecture, cross_link_generation*
- [[Configuration-Files]] — *topic: canon_discipline, codex_architecture, cross_link_generation*
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
- [[Quickstart]] — *topic: codex_operations, cross_link_generation*
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
```

Rules:

- Markers are byte-exact. The linker locates the block via marker pair and replaces only content between them.
- Block placement: end of file by default, before any trailing trivia. If a marker pair already exists anywhere in the file, that position is preserved.
- Human edits **between** markers are OVERWRITTEN on next run — by design. Humans edit `topics:` in frontmatter to influence the rendered block.
- Human edits **outside** the marker pair are preserved.
- Wikilink format: `[[FileStem]]` (precedent: lessons.md "wikilinks use filename stem, not page path or frontmatter title").

## Frontmatter as source of truth

`related_files: []` in frontmatter is canonical. The body block is a rendered view. If they ever disagree (e.g. user manually edits frontmatter), `cross_link_topics.py` regenerates the block to match frontmatter on next run.

## Plug-in interface (TF-IDF default + optional project-local augmentation)

Default linker is TF-IDF cosine over the page's scan fields, implemented in **pure stdlib** (`math`, `collections.Counter`, `re`). Project-local plug-ins extend by exposing a callable:

```python
# scripts/st_linker.py (PROJECT-LOCAL example — NOT distributed by Codex)
from sentence_transformers import SentenceTransformer
_model = SentenceTransformer("all-MiniLM-L6-v2")

def link(pages):
    """pages: list of dicts {path, title, intro, topics, frontmatter}
       returns: dict mapping page path → list of related page paths"""
    ...
```

`build_topic_index.py` flow:

1. Run TF-IDF on all pages (always, pure stdlib).
2. If `_config/cross_link.yaml` defines a plug-in, import `module_path:callable` and call it.
3. Blend both per `plugin.weight` (linear interpolation of similarity scores; union of candidates).
4. Write the final index.

Plug-in failures (import error, callable exception, malformed return) log a warning and **degrade to TF-IDF-only. Never block the pipeline.**

### R_ARCH carve-out (stdlib-only contract)

Project-local plug-ins are **out-of-scope** for Codex's stdlib-only contract — they are consuming-project artifacts, dynamically imported via opt-in config (`_config/cross_link.yaml` `plugin.module_path`), failure-isolated to log-and-degrade. Codex itself imports **zero** non-stdlib packages; plug-ins may import anything in their own environment. This is **distinct from** the 2026-05-20 triage reject, which targeted a Codex-*bundled* plug-in architecture (rejected). Mirrored canonically in `CLAUDE.md` R_ARCH › D_RULES.

## Tag mirroring (optional, configurable)

`build_topic_index.py` (#16) optionally mirrors frontmatter field values into `tags:`:

- Reads `_config/cross_link.yaml`'s `tags.mirror_from` (defaults `[topics]`).
- For each source field per page, adds each value to `tags:` if not already present.
- Applies `prefix_scheme` if `nested`.
- NEVER removes existing tags. Additive only — same contract as topic auto-detection.

Tag-mirroring failures (missing config, malformed `prefix_map`) degrade silently: linker proceeds without mirroring, logs a warning.

## Inline body tags are off-limits to Codex

Inline `#tag` syntax in body prose is invisible to Codex's writers. Body-scanning validators (terminology, reveal-conceit) treat `#tag` as ordinary text but never rewrite it. Humans own inline tags entirely.

## Idempotency requirement

Running `cross_link_topics.py` twice in succession with no source changes produces **zero diffs**. Test fixture must verify this (precedent: P4 aggregator test patterns).

## Related

- [[Frontmatter-Schema]] — `topics:`, `related_files:`, `tags:` fields and their write-discipline rules.
- [[Configuration-Files]] — `_canon/topics.yaml` and `_config/cross_link.yaml` schemas.
- [[Automation-Scripts]] — orchestrator pipeline order (#16 → #17 → #18 before health summary).
- [[Design-Principles]] #13 — cross-link injection is marker-bracketed and idempotent.
