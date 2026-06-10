# `_config/` — Validator Rule Directory

This directory holds the YAML rule files that drive Codex's content-quality validators. Each file is consumed by one or more scripts in `_scripts/`; files ship as structurally valid skeletons (e.g., `rules: []`, `pairs: []`) with commented examples that consuming-wiki maintainers fill in once project values are known.

## Files

**`forbidden_terms.yaml`** — Regex rules for trademark, naming, and convention violations. Each rule carries a `context` scope: `all` (flag everywhere), `audience` (flag only when page `visibility` matches the scope), or `internal` (flag only on `visibility: internal` pages). Consumed by `_scripts/validate_terminology.py`.

**`reveal_leak_patterns.yaml`** — Patterns that leak unreleased plot, mechanics, or roadmap content into `visibility: public` pages. Severities: `error` (block), `warning` (flag), `info` (document approved terminology without flagging — the "this term is fine, stop asking" lane). Consumed by `_scripts/validate_reveal_conceit.py`.

**`cascade_map.yaml`** — Source-to-derived-doc propagation pairs (`pairs: [{source, derived}]`). Declares which derived pages must be re-reviewed when a source page changes. Consumed by `_scripts/check_cascade.py` (mtime-based staleness detection) and `_scripts/delta_source_docs.py` (cascade-impact analysis when diffing two source-doc versions).

**`steel_threads.yaml`** — Multi-layer feature manifest. Each thread declares the layers (e.g., spec → tests → code → docs → dashboard) that must all be present for the feature to ship. Consumed by `_scripts/steel_thread_tracker.py`.

**`concept_coverage.yaml`** (v1.1, optional) — Tunes `_scripts/check_concept_coverage.py`. Keys: `min_mentions` (default 2; threshold for "entity mentioned in N+ pages but lacks a dedicated page"), `exclude_folders` (folder names skipped during scanning), `exclude_entities` (canonical names skipped — escape hatch for entities deliberately without a dedicated page).

## Regex convention (single-backslash)

The config files are parsed by Codex's YAML-subset parser (`_lib/frontmatter.py`), which does **no escape processing**: a quoted string is delivered verbatim to `re.compile`. Write regexes **single-backslash** — `"(?i)\bterm\b"` — exactly as you would in a raw Python regex. Real-YAML double-backslash (`"\\b"`) arrives as a literal backslash pair and produces a rule that compiles cleanly but **never fires** (a silent false-green validator). Do not "fix" this in the parser: adding escape processing would turn `\b` into backspace `0x08` and silently kill every live single-backslash rule in consuming wikis. Negative-control tests welded to the shipped examples: `tests/test_validate_terminology.py` + `tests/test_validate_reveal_conceit.py` (M-A component 1).

## Schema authority

Full schema definitions and rule semantics live in `<wiki>/04-Contributing/PROJECT_WIKI_BUILD_SPEC.md` §2.5 (synced verbatim from Codex). Edit examples in-file when project values are known; ship as-is for skeleton wikis.
