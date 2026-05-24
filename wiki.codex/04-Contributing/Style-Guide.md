---
title: "Codex — Style Guide"
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

# Codex — Style Guide

Conventions for authoring pages in the `Codex` wiki. The goal is consistency that lets validators and human readers parse pages quickly without surprises.

## Frontmatter

Every content page opens with a YAML frontmatter block. Required keys are defined in `04-Contributing/PROJECT_WIKI_BUILD_SPEC.md` §2.3 (the canonical schema); this section summarizes the conventions for filling them in.

### Required keys

- **`title`** — Human-readable page title. Use the same string as the H1 immediately below the frontmatter block, so the rendered title and the file metadata agree.
- **`type`** — One of: `framework | reference | guide | overview | episode | dashboard | profile | brain_dump | decision | context_rules`. Pick the closest match; see [[04-Contributing/File-Routing]] for type-to-folder mapping.
- **`visibility`** — `internal | public | confidential`. Default `internal` unless the page is explicitly intended for an external audience or restricted distribution.
- **`completion`** — Integer 0-100. Drives the `status` band per spec §2.3.
- **`status`** — `gap | outlined | solid | ready`. Bands: `ready ≥ 80`, `solid 55-79`, `outlined 30-54`, `gap < 30`. Validators error if `status: ready` is claimed without `canon_sources` populated or with `unverified_claims` non-empty.
- **`last_updated`** — `YYYY-MM-DD`. Bump on every substantive edit so cascade-staleness detection (see [[04-Contributing/Update-Cascade]]) stays accurate.
- **`dependencies`** — List of related page paths the current page leans on. Used by cross-reference checks.
- **`public_pair`** — Path to the public-facing companion page, or `null` if none. Used by `_scripts/check_framework_briefing_sync.py` to detect drift between internal and public versions.
- **`blocking_questions`** — List of open questions whose answers would unblock further work on this page. Aggregated into `_dashboards/` for sprint planning.
- **`canon_sources`** — List of paths into `_sources/raw/` (or canonical canon files) that support claims on this page. **Required and non-empty for `status: ready`.**
- **`unverified_claims`** — List of unproven claims on this page. **Must be empty for `status: ready`.**

### Optional keys

Only include when relevant; omit otherwise to keep frontmatter compact:

- **`source`** — Free-text citation (legacy field; prefer `canon_sources` for new pages).
- **`phase`** — Integer 0-N (project-defined phase ordering).
- **`allow_forbidden_terms: true`** — Escape hatch for pages that intentionally include a term that `_config/forbidden_terms.yaml` would otherwise flag. Use sparingly and explain why in the page body. See [[00-Start-Here/Terminology-Rules]].
- **`generated: true`** — Marks an auto-generated dashboard. Do not author by hand; the build script owns the file.

### Brain-dump-only keys

- **`dump_status`** — `exploring | validated | migrated | superseded | rejected`.
- **`migrated_to`** — List of paths the dump has been promoted into.

## Markdown conventions

- **Headings** — One H1 per page, matching the `title` frontmatter field. Use H2 for top-level sections, H3 for subsections; reserve H4+ for deep nesting.
- **Wikilinks** — Use `[[Folder/Page-Name]]` (with the folder prefix when ambiguous) so cross-reference checks resolve targets correctly. Bare `[[Page-Name]]` is acceptable only when the target is unambiguous wiki-wide.
- **Inline code vs fenced code** — Inline `` `like-this` `` for short identifiers (filenames, frontmatter keys, command fragments). Fenced blocks with a language tag for multi-line code:

  ```yaml
  example_key: value
  ```

- **Lists** — Hyphen (`-`) for unordered, `1.` for ordered. Indent nested items with two spaces.
- **Bold and italic** — `**bold**` for emphasis on terms or warnings; `*italic*` for titles of external works or for first-mention introduction of a new term.
- **Tables** — Standard pipe-syntax markdown tables. Pipes inside table cells are part of the syntax and are correct; this does *not* conflict with the Codex `__SEP__` template-filename rule (which applies to filenames only, not body content).

## Terminology

Stay inside the vocabulary documented in [[00-Start-Here/Glossary]] and the rules in [[00-Start-Here/Terminology-Rules]]. The terminology validator (`_scripts/validate_terminology.py`) reads `_config/forbidden_terms.yaml`; the reveal-leak validator (`_scripts/validate_reveal_conceit.py`) reads `_config/reveal_leak_patterns.yaml`.

If you genuinely need a forbidden term in a page (a quote, a historical citation, a deliberate counter-example), set `allow_forbidden_terms: true` in the frontmatter and add a brief comment in the page body explaining why.

## Cross-references

- Prefer wikilinks to bare URLs for intra-wiki references.
- Cite specific sections of long pages with `[[Page-Name#Section-Heading]]` when supported by the renderer.
- For `canon_sources`, cite the source path *plus* the relevant section anchor: `"_sources/raw/<file>.md §2.1"`.

## Validation

Before committing a non-trivial edit, run `python _scripts/update_dashboards.py` from the wiki root and review the affected dashboards. The orchestrator runs every validator and aggregator; fix new errors before pushing.

## Related pages

- [[04-Contributing/Update-Cascade]]
- [[04-Contributing/File-Routing]]
- [[00-Start-Here/How-to-Use-This-Wiki]]
- [[00-Start-Here/Terminology-Rules]]
- `_config/forbidden_terms.yaml`
- `_config/reveal_leak_patterns.yaml`
- `04-Contributing/PROJECT_WIKI_BUILD_SPEC.md` §2.3 (frontmatter schema canonical reference)
