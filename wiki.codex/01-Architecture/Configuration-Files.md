---
title: "Configuration Files (_config/ + _canon/)"
type: reference
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-24
dependencies: ["01-Architecture/Automation-Scripts", "01-Architecture/Cross-Link-Generation"]
public_pair: null
blocking_questions: []
topics: [canon_discipline, codex_architecture, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [canon_discipline, codex_architecture, cross_link_generation]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §2.5"]
unverified_claims: []
---

# Configuration Files

Codex separates **behavior tuning** (`_config/`) from **ground-truth facts** (`_canon/`).

## `_config/` — behavior tuning, per-project

| File | Purpose |
|---|---|
| `forbidden_terms.yaml` | Regex rules for trademark/naming violations, context-aware (`all` / `audience` / `internal`). |
| `reveal_leak_patterns.yaml` | Phrases that leak unreleased content. Severities: `error` / `warning` / `info` (info documents approved terms without flagging). |
| `cascade_map.yaml` | Source → derived doc propagation. |
| `steel_threads.yaml` | Multi-layer feature manifest. |
| `concept_coverage.yaml` (v1.1, optional) | Tunes `check_concept_coverage.py`. Keys: `min_mentions` (default 2), `exclude_folders`, `exclude_entities`. |
| `cross_link.yaml` (v1.3, optional) | Tunes `build_topic_index.py` + `cross_link_topics.py`. See below. |

## `_canon/` — ground-truth facts, per-project

| File | Purpose |
|---|---|
| `counts.yaml` | Every canonical number that appears more than once. |
| `roster.yaml` | Named entities with canonical names and aliases. |
| `taxonomy.yaml` | Structured classifications. |
| `timeline.yaml` | Milestones, versions, progression parameters. |
| `topics.yaml` (v1.3) | Topic registry for cross-link generation. |

The consistency checker reads `_canon/` as ground truth. Pages contradicting it are flagged. Pages contradicting *each other* (when `_canon/` doesn't arbitrate) are also flagged in a separate section.

Canon is the **floor**, not the ceiling (Principle #8 — see [[Design-Principles]]). Pages can contain more — they just can't contradict canon.

## v1.3 — `_canon/topics.yaml` schema

Per-project topic registry. Ground truth.

```yaml
topics:
  - name: example_topic                 # canonical topic name; lowercase, snake_case
    aliases: [alt_name]                 # alternate names accepted in frontmatter topics: lists
    keywords:                           # word-boundary case-insensitive patterns scanned in H1/H2/intro
      - "example"
    cross_manual: true                  # if true, links across top-level folder boundaries; default false
    min_similarity: 0.35                # optional per-topic TF-IDF override; defaults from _config/cross_link.yaml
```

Matching rules:

- Word-boundary (`\b...\b`), case-insensitive by default.
- Frontmatter + fenced code blocks stripped before scanning (precedent: lessons.md "strip-as-whitespace for body-scanning validators").
- Aliases counted as topic matches alongside canonical name (precedent: `roster.yaml` in `check_concept_coverage.py`).

Template instance ships **domain-neutral** (1–2 placeholder topics + commented examples + structurally-valid empty default). Consuming projects populate domain content themselves.

## v1.3 — `_config/cross_link.yaml` schema (optional)

All keys optional with documented defaults:

```yaml
tfidf:
  min_similarity: 0.35                  # cosine threshold below which pages are not linked
  max_links_per_page: 8                 # cap on "See also" entries per page
  scan_fields: [h1, h2, intro_para_1]   # which page regions feed the TF-IDF vector

plugin:
  module_path: ~                        # e.g. "scripts/st_linker.py" — PROJECT-LOCAL Python file; default unset
  callable: ~                           # callable name; signature: link(pages: list[ParsedPage]) -> dict[str, list[str]]
  weight: 0.5                           # blend factor when augmenting TF-IDF (0.0 = TF-IDF only; 1.0 = plug-in only)

tags:
  mirror_from: [topics]                 # frontmatter fields to mirror as tags; [] disables mirroring
  prefix_scheme: flat                   # flat | nested ; "nested" emits "topic/smoke" instead of "smoke"
  prefix_map:                           # used only when prefix_scheme: nested
    topics: topic                       # topics: [smoke] → tags: [topic/smoke]
```

If `plugin.module_path` is unset, #16 runs **TF-IDF only (pure stdlib)**. If set, Codex dynamically imports the project-local module and merges its output with TF-IDF results per `plugin.weight`. Tag mirroring defaults to mirror-from-`topics`, flat prefix.

See [[Cross-Link-Generation]] for the full contract.

<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Glossary]] — *topic: cross_link_generation, framework_durability*
- [[Automation-Scripts]] — *topic: codex_architecture, cross_link_generation*
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
- [[Quickstart]] — *topic: codex_operations, cross_link_generation*
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
