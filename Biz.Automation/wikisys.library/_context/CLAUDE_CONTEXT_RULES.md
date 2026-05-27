---
title: "Codex Claude Context Rules"
type: context_rules
visibility: internal
completion: 100
status: ready
last_updated: 2026-05-24
dependencies: []
canon_sources: []
unverified_claims: []
---

# `Codex` — Claude Context Rules

This file customizes how Claude (or any LLM agent) operates inside the `Codex` wiki. It is read on session start and supplements any global Claude Code or chat configuration with project-specific guidance.

Unlike `INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md` (which ship verbatim and are overwritten on every `sync_from_kit.py` run), this file is **owned by the project**. Edit it freely. The Sync operation leaves it untouched.

## Project orientation

Briefly describe what `Codex` is, who it serves, and what makes it distinctive. Two or three sentences are enough. The goal is to anchor an agent that has just opened this wiki for the first time.

- **Domain:** Codex protocol documentation — the build-spec, operations, and architecture of the Codex scaffolding tool.
- **Primary canon source:** `_canon/` (roster, topics, taxonomy, counts, timeline) + `_sources/raw/CODEX_BUILD_SPEC_v1_3.md`.
- **Audience:** Codex builders + operators (internal).

## Question-Answering Behavior

When answering any question about `Codex` — whether posed by a human collaborator, a downstream agent, or as part of a generated document — follow these four rules. They are the minimum required behavior for every bootstrapped wiki and must remain in this file.

### 1. Consult wiki pages before raw sources

Consult wiki pages before raw sources when answering questions about the project. Wiki pages reflect the curated, validated synthesis; raw sources in `_sources/raw/` are the archived inputs the pages were derived from. Reach for the page first; fall back to the source only when the page is silent, ambiguous, or visibly stale relative to a newer source.

### 2. Cite specific pages using `[[wikilinks]]`

Cite specific pages using `[[wikilinks]]` in answers. Citation enables the reader to verify the claim and follow the trail. Prefer the most specific page that supports the claim over a parent index page. If multiple pages contribute, cite each one — see rule 4.

### 3. Flag uncertainty explicitly; never confabulate when canon is silent

Flag uncertainty explicitly; never confabulate when canon is silent. If the wiki does not answer the question — and the raw sources also do not — say so. Acceptable phrasings: "canon is silent on this," "no page covers this yet," "this would require a new brain-dump entry to formalize." Unacceptable: inventing a plausible-sounding answer styled as canon.

### 4. For cross-source synthesis, name every page being synthesized

For cross-source synthesis, name every page being synthesized. When an answer draws on more than one page, list each contributing page as a `[[wikilink]]` so the reader can audit the synthesis. This rule applies to any answer that combines information from two or more pages, regardless of how trivial the combination appears.

### Project-specific additions

> The four rules above are the minimum. Projects may add more here. Suggested additions: visibility-bleed warnings (internal-only terminology that must not appear in public-facing output), preferred phrasing or tone constraints, canon-promotion etiquette, escalation routes for contradictions surfaced during answering.

- `<add project-specific rule>`
- `<add project-specific rule>`

## Working with `Codex` content

Optional section. Use this space for guidance an agent will benefit from beyond question-answering — e.g. "always check `_canon/timeline.yaml` before describing version-relative events," "treat `_brain_dump/` entries as explicitly non-canonical," "the `outlined` status band means the page is a sketch, not a stub."

## Librarian persona

The wiki ships with a Librarian persona — a maintainer agent that keeps the wiki coherent over time. The Librarian persona is documented in two paired files:

- **Canonical declaration**: `_context/CODEX_LIBRARIAN.md` — full persona declaration with §Identity, §Owns, §Never owns, §Loop, and §Hard rules.
- **Persona drop-in**: `.claude/personas/CLAUDE.librarian.md` — summary-form drop-in loaded by `.claude/`-aware Claude Code sessions.

**At session start, Claude should read both files** before acting on Librarian-class requests (brain dump promotion, related-file curation, framework/derived audits). The persona files are also the source of truth for any 'Librarian:' handoff routing from the human operator.

If your session does not auto-load `.claude/personas/`, read `.claude/personas/CLAUDE.librarian.md` first (faster summary), then `_context/CODEX_LIBRARIAN.md` if the full canonical declaration is needed.

## Update protocol

This file is **not** overwritten by `sync_from_kit.py`. Editing it is safe at any time. If the four-rule structure under "Question-Answering Behavior" is removed or substantially reworded, downstream agents may degrade silently — keep the four rule headings and their leading sentence intact even when extending the section.
