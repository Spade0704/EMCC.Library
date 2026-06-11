---
title: "<Project Name> — Update Cascade"
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

# <Project Name> — Update Cascade

This page is a deliberate stub (Codex boilerplate-location convention, ratified 2026-06-11): the cascade workflow is protocol content, identical for every Codex consumer, so it lives ONCE in the canonical Codex wiki rather than as a forkable per-repo copy.

**Canonical page:** `EMCC.Library` repo -> `wiki.codex/git/04-Contributing/Update-Cascade.md` (https://github.com/Spade0704/EMCC.Library)

In one paragraph: when a source page changes, pages derived from it need review or re-derivation; the cascade map (`_config/cascade_map.yaml`) declares those dependencies, validators detect staleness, and the workflow walks the affected pages until the cascade clears. Read the canonical page for the detection rules and resolution workflow; this repo's project-specific dependency declarations live in its own `_config/cascade_map.yaml`.
