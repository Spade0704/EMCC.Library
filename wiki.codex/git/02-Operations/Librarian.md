---
title: "The Librarian — Codex's Operating Agent"
type: framework
visibility: internal
completion: 45
status: outlined
last_updated: 2026-06-06
dependencies: ["02-Operations/Bootstrap", "02-Operations/Sync", "02-Operations/Ingest", "01-Architecture/Design-Principles"]
public_pair: null
blocking_questions: []
topics: [codex_operations, librarian_persona, ingest_procedure]
tags: [codex_operations, librarian_persona, ingest_procedure]
related_files: []
canon_sources: ["wiki.codex/git/codex/CODEX_LIBRARIAN.md", "wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §4"]
unverified_claims: []
---

# The Librarian — Codex's Operating Agent

This page is a derived overview. The canonical, authoritative definition is
`wiki.codex/git/codex/CODEX_LIBRARIAN.md` (`status: ready`). Where this page and
the canon disagree, the canon wins.

Codex (the engine) and the Librarian (the agent) are the module's **two distinct
things** — keep them separate. [[Overview]] documents the engine: *how* raw
material becomes a structured, validated wiki. This page documents the agent:
*who* operates that engine.

- **Codex** is the machine — the scaffolding/sync tool, the frontmatter schema,
  the validators and dashboards, the cross-link graph.
- **The Librarian** is the operator of the machine — the Claude persona that
  ingests sources, curates pages, maintains canon, and runs the dashboards.

Codex has exactly **one** canonical persona, the Librarian. (Lattice's Nexus has
four — Architect / Craftsman / Auditor / Scribe — but those belong to Lattice,
not Codex; the two persona sets are intentionally distinct. Source:
`wiki.codex/git/codex/CODEX_LIBRARIAN.md`.)

## What the Librarian owns

The Librarian drives the Codex operations defined in the build spec §4 and the
v1.1 extensions:

- **[[Bootstrap]]** (§4.1) — one-time wiki creation for a new project.
- **[[Sync]]** (§4.2) — infrastructure refresh from Codex into a live wiki.
- **[[Ingest]]** (§4.3) — the most frequent operation; integrate new source
  documents into a wiki. Claude-driven, not a script.
- **Maintenance** — act on validator findings already on disk (distinct from
  Ingest, which acts on new sources entering `_inbox/`).

Beyond execution, the Librarian owns wiki taxonomy and cross-link integrity,
canon *proposals* (never auto-writes), brain-dump promotion, source-revision
handling, and internal -> public visibility promotion. The v1.1 portfolio layout
adds three further operations — Inbox-Sort, Pairing-Audit, and
Cross-Project-Scan. For the full enumeration, see
`wiki.codex/git/codex/CODEX_LIBRARIAN.md`.

## What the Librarian never owns

- **The Codex tool itself.** Codex's `_scripts/`, `_lib/`, `tests/`, and the spec
  belong to whoever builds Codex. The Librarian *uses* Codex; it does not modify
  it. (Codex is the tool, not the content — Principle #10.)
- **Final canon writes.** Canon writes require user confirmation. The Librarian
  proposes; the user disposes (Principle #11).
- **`_context/CLAUDE_CONTEXT_RULES.md` on Sync** — per-project; never overwritten.
- **Lattice framework content** (`documents/lattice/**`) and the Nexus persona
  drop-ins.
- **End-user question-answering.** The Librarian is the *maintenance* surface
  (curation, ingest, sync, promotion); the Q&A surface is governed separately by
  `_context/CLAUDE_CONTEXT_RULES.md`.

## Hard rules (the load-bearing few)

These are summarized from the canon; the full, authoritative list is in
`wiki.codex/git/codex/CODEX_LIBRARIAN.md` "Hard rules".

- **Verbatim discipline.** `INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md`
  ship verbatim into every bootstrapped wiki's `_context/`. Never paraphrase,
  shorten, or "improve" them. If they contradict your judgment, the procedure
  wins; surface the contradiction, don't act against it.
- **Ingest proposes, humans dispose.** Canon writes require confirmation;
  contradictions are flagged, never silently overwritten; archived sources are
  read-only.
- **Authoritative source != wiki.** The wiki is derived; the source wins
  conflicts; cite via `canon_sources` (Principle #2).
- **Frontmatter is the API.** Read page metadata from frontmatter, never from
  prose (Principle #5).
- **Halt-loud on ambiguity and on tool failure.** A source contradicting canon,
  an unclear classification, or a script/validator crash -> halt and surface;
  never guess, never paper over.

## Persona drop-in

The runtime drop-in `.claude/personas/CLAUDE.librarian.md` is **generated** from
the canonical `wiki.codex/git/codex/CODEX_LIBRARIAN.md` via
`generate_persona_dropin.py` — do not hand-edit it (a drift guard test enforces
this). See [[CLAUDE.librarian]] for the loaded drop-in and
[[Claude-Behavior-Rules]] for the operating-rule surface.

## Related pages

- [[Overview]] — Codex (the engine) in one page
- [[Bootstrap]] | [[Sync]] | [[Ingest]] — the operations the Librarian drives
- [[Design-Principles]] — the load-bearing rules the Librarian enforces
- [[Claude-Behavior-Rules]] — hard rules, operating preferences, red flags
