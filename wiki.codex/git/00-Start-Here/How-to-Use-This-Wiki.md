---
title: "Codex — How to Use This Wiki"
type: guide
visibility: internal
completion: 0
status: gap
last_updated: <YYYY-MM-DD>
dependencies: []
public_pair: null
blocking_questions: []
canon_sources: []
unverified_claims: []
---

# Codex — How to Use This Wiki

> **Canonical copy.** This page is the canonical, once-upstream home of this protocol content (boilerplate-location convention, Operator-ratified 2026-06-11): consumer wikis carry a generated stub that points here. Edit HERE; never fork into a consumer wiki.

This page explains how the `Codex` wiki is organized, how to navigate it, and the conventions that pages follow. It is generic across projects scaffolded by Codex; minor customization is usually unnecessary.

## Navigation

Start at [[Home]]. The Table of Contents on Home lists the top-level entry points. Most pages link to their related pages in a "Related pages" section at the bottom.

Folder layout:

- `00-Start-Here/` — orientation pages for new readers (this page, Project Overview, Glossary, Terminology Rules).
- `04-Contributing/` — conventions for contributors (update cascade, file routing, style guide).
- `_canon/` — ground-truth YAMLs (counts, roster, taxonomy, timeline). Validators read these as canonical references.
- `_config/` — wiki-level configuration (forbidden terms, cascade map, steel threads, concept coverage).
- `_context/` — Claude operating context (CLAUDE_CONTEXT_RULES, INGEST_PROCEDURE, SEMANTIC_LINT_PROCEDURE).
- `_brain_dump/` — unvalidated working notes; explicitly NOT canon.
- `_inbox/` — ephemeral triage area for sources awaiting ingest.
- `_sources/raw/` — permanent, read-only archive of ingested sources. `canon_sources` cite paths here.
- `_decisions/` — append-only decision logs (including the ingest log).
- `_confidential/` — confidential pages (not for external sharing).
- `_dashboards/` — auto-generated dashboards from `_scripts/update_dashboards.py`.
- `_scripts/` — automation scripts (validators, aggregators, dashboard builders).

## Page conventions

Every content page carries a YAML frontmatter block. Key fields:

- `title` — human-readable page title.
- `type` — page class: `framework | reference | guide | overview | episode | dashboard | profile | brain_dump | decision | context_rules`.
- `visibility` — `internal | public | confidential`.
- `status` — completion band: `gap | outlined | solid | ready`.
- `completion` — 0-100 numeric score; status bands map to this score (`ready ≥ 80`, `solid 55-79`, `outlined 30-54`, `gap < 30`).
- `canon_sources` — required and non-empty for `status: ready` pages.
- `unverified_claims` — must be empty for `status: ready` pages.

Full schema in `04-Contributing/PROJECT_WIKI_BUILD_SPEC.md` §2.3.

## Status bands

Pages progress through four bands as they mature:

1. `gap` (completion < 30) — placeholder or stub; little real content yet.
2. `outlined` (30-54) — structure exists with some content; many open questions.
3. `solid` (55-79) — most content present and reviewed; minor gaps remain.
4. `ready` (≥ 80) — content complete; all claims cite `canon_sources`; `unverified_claims` empty.

Validators in `_scripts/` enforce these bands; `status: ready` with missing `canon_sources` is an error.

## Updating a page

1. Edit the page content and any affected frontmatter fields (notably `last_updated`, `completion`, `status`).
2. If the change touches a load-bearing fact, update the relevant `_canon/` YAML so cross-page consistency checks stay green.
3. Run `python _scripts/update_dashboards.py` from the wiki root to refresh dashboards and validation reports.
4. Review `_dashboards/` output for new findings introduced by your edit.

## Asking questions

When asking Claude (or another agent) a question about `Codex`, follow the four rules in `_context/CLAUDE_CONTEXT_RULES.md` § "Question-Answering Behavior".

## Related pages

- [[Home]]
- [[00-Start-Here/Project-Overview]]
- [[00-Start-Here/Glossary]]
- [[00-Start-Here/Terminology-Rules]]
- [[04-Contributing/Style-Guide]]
