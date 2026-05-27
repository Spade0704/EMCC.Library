---
title: "Codex — Overview"
type: overview
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-27
dependencies: ["01-Architecture/Folder-Architecture", "01-Architecture/Design-Principles", "02-Operations/Bootstrap", "02-Operations/Sync", "02-Operations/Ingest"]
public_pair: null
blocking_questions: []
topics: [codex_architecture, codex_operations, cross_link_generation, iron_soul_reference]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Build-Workflow.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_architecture, codex_operations, cross_link_generation, iron_soul_reference]
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §1"]
unverified_claims:
  - "Source CODEX_BUILD_SPEC_v1_3.md carries inconsistent version stamps: header says v1.3, footer says 'Codex Build Spec v1.2 — April 2026', and an embedded Phase-1-Q3 reads 'spec is v1.2'. The header (v1.3) is treated as authoritative for routing; the footer/Phase-1 mismatches are pending an upstream Scribe fix to the source. Do NOT edit the archived source."
---

# Codex — Overview

`Codex` is a **scaffolding and sync tool** for creating and maintaining markdown-based documentation wikis. One Codex installation, many consuming-project wikis. Each consuming project's wiki is its own folder of plain markdown files, openable in Obsidian or any markdown reader, with automated dashboards, validators, and integrity checks.

Codex itself is not a wiki. Codex is the tool that *creates* wikis, and that *cascades infrastructure improvements* to wikis it has created without touching their content.

## What Codex produces

A two-tier documentation system:

- **Tier 1 — Developer Wiki (internal).** Browseable in Obsidian. Internal frameworks, technical references, contributing guides. Shareable with collaborators when ready.
- **Tier 2 — Confidential Profile.** Single markdown file with project secrets, business strategy, and behavioral rules Claude follows when the file is loaded as project knowledge. Upload-ready.

Both tiers are plain markdown with YAML frontmatter, with a pure-Python automation layer providing 15 base utility functions plus 3 v1.3 cross-link scripts (see [[Automation-Scripts]]).

## Why Codex exists

Without Codex, a developer running multiple projects either (a) maintains documentation inconsistently across projects, or (b) reinvents the same documentation discipline repeatedly. Codex standardizes the discipline once and applies it everywhere.

Problems Codex solves:

- **Knowledge drift** — facts that change in one place but not in three others.
- **Confidentiality leaks** — internal terminology accidentally appearing in public docs.
- **Stale documentation** — a framework changed, but its briefing guide is still last quarter's version.
- **Loss of decision context** — choices made in chat that nobody remembers six months later.
- **Brain dump pollution** — speculative ideas accidentally treated as canonical.
- **Source drift** — new sources arriving but never integrated into the wiki (v1.1 Ingest, see [[Ingest]]).
- **Multi-project documentation overhead** — every project needing the same structural setup from scratch.

## How to navigate this wiki

- Architecture (this domain) — *what Codex is* (folders, schema, scripts, principles).
- Operations — *how to drive Codex*: [[Bootstrap]], [[Sync]], [[Ingest]], [[Build-Workflow]], [[Quickstart]].
- See [[Home]] for the full table of contents.

## History — embedded v1.1 changelist (preserved verbatim)

> The source `CODEX_BUILD_SPEC_v1_3.md` embeds the v1.1 changelist (L22–29) as legacy/historical context. Preserved here verbatim.

> **What changed in v1.1 (vs v1.0):**
> - Ingest named as a first-class operation alongside Bootstrap and Sync (§4.3).
> - New permanent source archive `_sources/raw/` alongside the ephemeral `_inbox/` (§2.2).
> - Two new `_context/` templates: `INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md`.
> - New validator `check_concept_coverage.py` (§2.4 #15).
> - New scaffold `scaffold_source.py`.
> - Required Q&A-behavior rules added to the `CLAUDE_CONTEXT_RULES.md` template (§7 Phase 4).
> - Framework/reference durability split named as Principle #12, with a corresponding annotation on the `type` field in §2.3. Tooling to automate the framework export deferred to v1.2.

## What changed in v1.3 (current)

Cross-link generation. Stacks on the v1.2 baseline (health-summary orchestration; already shipped). Adds topical cross-linking: a per-project topic registry (`_canon/topics.yaml`), three new scripts (#16 `build_topic_index.py`, #17 `cross_link_topics.py`, #18 `validate_topic_registry.py`), two new optional frontmatter fields (`topics`, `related_files`) plus a human-owned `tags` field, a marker-bracketed "See also" body block, and an optional **project-local** linker plug-in (TF-IDF default is pure stdlib). No change to existing aggregator/validator contracts; the cross-link pipeline runs as an additive stage in `update_dashboards.py`. See [[Cross-Link-Generation]].

## Codex v1.1 update arc (2026-05-27)

Codex v1.0 → v1.1 shipped via Library S002 (closed 2026-05-27). Three structural shifts landed:

- **Portfolio folder layout.** Module source files (`_scripts/`, `_template/`, `_config/`, `_canon/`, `_context/`, `_decisions/`) extracted from the wiki into a sibling `Biz.Automation/wikisys.<projectname>/` container per the operator's portfolio folder-structure spec (F5 + F6 resolution). Wiki content split into a public `wiki.<name>/git/` zone and a private `wiki.<name>/local/` zone (F10). See `REORGANIZATION-INSTRUCTIONS.md` for the pattern P1–P8 manifest.
- **Canonical-output `bootstrap.py`.** `bootstrap.py <projectname> [--minimal | --code | --website | --full]` produces the canonical tree per spec §(c). Scaffold-only — no script copy; consumers run scripts from a vendored / submodule / sibling-checkout of Library. `sync_from_kit.py` still ships at the v1.0 contract (MI-16 carry; v1.0-shape script copy + procedure-doc delivery); reconciliation deferred to S004 along with the v1.0 → v1.1 wiki migration path.
- **5 new audit scripts + Librarian extension.** `audit_doc_pairing.py`, `audit_gitignore.py`, `route_inbox.py`, `audit_assets.py`, `audit_local_split.py` ship in `wikisys.library/_scripts/`. `CODEX_LIBRARIAN.md` extended with 3 new operations (Inbox-Sort, Pairing-Audit, Cross-Project-Scan), 5 Mentor pattern codifications, and a Telegram auto-summary contract.

See `tasks/sessions.md` Session 2 CLOSED entry for the full close record and `tasks/plans/portfolio-folder-structure-spec.md` for the canonical layout spec.

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
