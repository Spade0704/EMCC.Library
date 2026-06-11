---
title: "Codex — Update Cascade"
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

# Codex — Update Cascade

> **Canonical copy.** This page is the canonical, once-upstream home of this protocol content (boilerplate-location convention, Operator-ratified 2026-06-11): consumer wikis carry a generated stub that points here. Edit HERE; never fork into a consumer wiki.

When a source page changes, derived pages downstream of it need review or re-derivation. This page explains how `Codex` tracks those dependencies, how staleness is detected, and the workflow for resolving a cascade event.

## Cascade map

The machine-readable dependency graph lives in `_config/cascade_map.yaml`. Each entry pairs one source page with one derived page:

```yaml
pairs:
  - source: "01-Framework/Spec.md"
    derived: "public/Spec-Briefing.md"

  - source: "02-Domain/Glossary.md"
    derived: "public/Glossary-Public.md"
```

Schema (per spec §2.5):

- Top-level wrapper key: `pairs` (list).
- Per-pair required keys: `source`, `derived`.
- Paths are wiki-root-relative POSIX strings.

One source may appear in multiple pairs (one source → many derived). One derived may also appear in multiple pairs (one derived from many sources); each cascade event fires independently.

## Staleness detection

`_scripts/check_cascade.py` reads `_config/cascade_map.yaml` and compares modification times: when a `source` is newer than its `derived`, the pair is reported as stale. Output flows into `_dashboards/` via the orchestrator (`_scripts/update_dashboards.py`).

This is mtime-based, not content-based — a no-op `touch` on a source counts as a change. Treat it as a coarse signal: a stale entry means "review whether the derived page still reflects the source."

## Diff-time cascade impact

`_scripts/delta_source_docs.py` takes two versions of a source document and emits the structural diff (sections added / modified / removed). Pair it with `_config/cascade_map.yaml` when reviewing a non-trivial source edit: every derived page listed for the changed source is in scope for review.

## Workflow

1. Edit the source page; update `last_updated`.
2. Run `python _scripts/update_dashboards.py` from the wiki root.
3. Open the cascade-staleness dashboard in `_dashboards/` and locate any newly stale pairs.
4. For each stale pair, decide:
   - **Re-derive** — update the derived page to match the new source; bump `last_updated` and `completion`/`status` as appropriate.
   - **Suppress** — if the change does not affect the derived page, simply bump `last_updated` on the derived page (acknowledges review) without further edits.
5. Re-run the dashboards to confirm the pair is no longer stale.

## Adding a new pair

1. Add the `{source, derived}` entry to `_config/cascade_map.yaml`.
2. Bump `last_updated` on the derived page so the new pair starts in a "fresh" state.
3. Run `_scripts/update_dashboards.py` to confirm the addition is picked up cleanly.

## Removing a pair

If a derivation relationship no longer holds, remove the pair from `_config/cascade_map.yaml`. Consider whether the derived page should be archived, repurposed, or deleted; cascade map removal is independent of the derived page's lifecycle.

## Related pages

- [[04-Contributing/File-Routing]]
- [[04-Contributing/Style-Guide]]
- `_config/cascade_map.yaml`
- `_scripts/check_cascade.py`
- `_scripts/delta_source_docs.py`
- `04-Contributing/PROJECT_WIKI_BUILD_SPEC.md` §2.5 (schema authority)
