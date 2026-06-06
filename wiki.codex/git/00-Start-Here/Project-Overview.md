---
title: "Codex — Project Overview"
type: overview
visibility: internal
completion: 40
status: outlined
last_updated: 2026-06-06
dependencies: ["01-Architecture/Overview", "02-Operations/Librarian"]
public_pair: null
blocking_questions: []
topics: [codex_architecture, codex_operations]
tags: [codex_architecture, codex_operations]
related_files: []
canon_sources: ["wiki.codex/git/raw/CODEX_BUILD_SPEC_v1_3.md §1"]
unverified_claims: []
---

# Codex — Project Overview

This page is a derived overview. The canonical, authoritative definition is
`wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` §1 ("What Codex Is"). Where this
page and the spec disagree, the spec wins.

The Library module ships **two distinct things** — keep them separate:

- **Codex** is the engine — the scaffolding-and-sync tool (the *how*). Documented
  in depth at [[01-Architecture/Overview]].
- **The Librarian** is the agent — the single canonical persona that operates the
  engine (the *who*). Documented at [[02-Operations/Librarian]].

This page orients a new reader to Codex itself.

## What Codex is

- Codex is a **scaffolding and sync tool** for creating and maintaining
  markdown-based documentation wikis. One Codex installation, many
  consuming-project wikis.
- Project type: a developer tool (CLI + library, no GUI), written in Python 3.8+,
  pure standard library, zero external dependencies.
- The deliverable is a **two-tier documentation system** per consuming project: a
  Tier-1 internal Developer Wiki (browseable in Obsidian, plain markdown with YAML
  frontmatter, automated dashboards and validators) and a Tier-2 Confidential
  Profile (a single upload-ready markdown file of project secrets, strategy, and
  Claude behavioral rules).

Codex itself is not a wiki. Codex is the tool that *creates* wikis, and that
*cascades infrastructure improvements* to wikis it has created without touching
their content. See [[01-Architecture/Overview]] for the full architecture.

## Why Codex exists

Without Codex, a developer running multiple projects either maintains
documentation inconsistently across projects, or reinvents the same documentation
discipline repeatedly. Codex standardizes the discipline once and applies it
everywhere. The problems it solves, per spec §1:

- **Knowledge drift** — facts that change in one place but not in three others.
- **Confidentiality leaks** — internal terminology accidentally appearing in
  public docs.
- **Stale documentation** — a framework changed, but its briefing guide is still
  last quarter's version.
- **Loss of decision context** — choices made in chat that nobody remembers six
  months later.
- **Brain dump pollution** — speculative ideas accidentally treated as canonical.
- **Source drift** — new sources arriving but never integrated into the wiki
  (v1.1 Ingest — see [[02-Operations/Ingest]]).
- **Multi-project documentation overhead** — every project needing the same
  structural setup from scratch.

## Who it serves

The primary audience is a solo developer (and Claude Code) managing multiple
projects, each needing structured documentation. The internal vs. public
distinction matters: visibility rules in `_context/CLAUDE_CONTEXT_RULES.md` and
`validate_reveal_conceit.py` depend on it. New content defaults to
`visibility: internal`; promotion is one-way (`internal -> public`). See
[[01-Architecture/Frontmatter-Schema]] for the visibility enum.

## Status snapshot

- **Phase:** Codex v1.3 (cross-link generation); shipped via Library S002
  (v1.0 -> v1.1, 2026-05-27). See [[01-Architecture/Overview]] "Codex v1.1 update
  arc" for the structural shifts.
- **Last reviewed:** 2026-06-06

## Related pages

- [[00-Start-Here/How-to-Use-This-Wiki]]
- [[00-Start-Here/Glossary]]
- [[01-Architecture/Overview]] — Codex (the engine) in depth
- [[02-Operations/Librarian]] — the agent that operates Codex
- [[Home]]
