# `_config/` — Validator Rule Directory

This directory holds the YAML rule files that drive Codex's content-quality validators. Each file is consumed by one or more scripts in `_scripts/`; files ship as structurally valid skeletons (e.g., `rules: []`, `pairs: []`) with commented examples that consuming-wiki maintainers fill in once project values are known.

## Files

**`forbidden_terms.yaml`** — Regex rules for trademark, naming, and convention violations. Each rule carries a `context` scope: `all` (flag everywhere), `audience` (flag only when page `visibility` matches the scope), or `internal` (flag only on `visibility: internal` pages). Consumed by `_scripts/validate_terminology.py`.

**`reveal_leak_patterns.yaml`** — Patterns that leak unreleased plot, mechanics, or roadmap content into `visibility: public` pages. Severities: `error` (block), `warning` (flag), `info` (document approved terminology without flagging — the "this term is fine, stop asking" lane). Consumed by `_scripts/validate_reveal_conceit.py`.

**`cascade_map.yaml`** — Source-to-derived-doc propagation pairs (`pairs: [{source, derived}]`). Declares which derived pages must be re-reviewed when a source page changes. Consumed by `_scripts/check_cascade.py` (mtime-based staleness detection) and `_scripts/delta_source_docs.py` (cascade-impact analysis when diffing two source-doc versions).

**`steel_threads.yaml`** — Multi-layer feature manifest. Each thread declares the layers (e.g., spec → tests → code → docs → dashboard) that must all be present for the feature to ship. Consumed by `_scripts/steel_thread_tracker.py`.

**`concept_coverage.yaml`** (v1.1, optional) — Tunes `_scripts/check_concept_coverage.py`. Keys: `min_mentions` (default 2; threshold for "entity mentioned in N+ pages but lacks a dedicated page"), `exclude_folders` (folder names skipped during scanning), `exclude_entities` (canonical names skipped — escape hatch for entities deliberately without a dedicated page).

## Schema authority

Full schema definitions and rule semantics live in `<wiki>/04-Contributing/PROJECT_WIKI_BUILD_SPEC.md` §2.5 (synced verbatim from Codex). Edit examples in-file when project values are known; ship as-is for skeleton wikis.
