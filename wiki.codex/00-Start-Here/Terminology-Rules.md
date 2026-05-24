---
title: "Codex — Terminology Rules"
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

# Codex — Terminology Rules

This page documents `Codex`-specific terminology policy: which terms are forbidden in which contexts, why, and how to use the escape hatch when a forbidden term is unavoidable.

The machine-readable rules live in `_config/forbidden_terms.yaml`. The `_scripts/validate_terminology.py` validator reads that file and scans every wiki page for matches; this page is the human-readable companion that explains the *why* behind each rule.

## Forbidden Terms

The `_config/forbidden_terms.yaml` file holds entries shaped like:

```yaml
- term: "<forbidden-term>"
  scope: all | audience | internal
  reason: "<one-line rationale>"
  replacement: "<preferred phrasing>"  # optional
```

Scope semantics:

- **`all`** — never appears anywhere in the wiki.
- **`audience`** — never appears on `visibility: public` pages; allowed on internal pages.
- **`internal`** — never appears on `visibility: internal` pages (reverse of `audience`; rare, but supported for terms that should only surface in public-facing output).

### Why forbid a term?

Common reasons:

- **Visibility leak** — internal codename or working term that should never reach a public audience.
- **Outdated terminology** — superseded vocabulary kept out of new pages to prevent drift.
- **Ambiguity** — term has multiple meanings in different contexts; project standard is to use the more specific alternative.
- **Sensitivity** — term carries connotations the project explicitly avoids.

## Escape hatch

A page may set `allow_forbidden_terms: true` in its frontmatter to bypass terminology validation. Use sparingly and with comment justification — every escape-hatch page is a known divergence and should be reviewed periodically.

## Adding a new forbidden term

1. Add the entry to `_config/forbidden_terms.yaml` with `term`, `scope`, and `reason`.
2. Document the reasoning here under a brief subsection if the rule is non-obvious.
3. Run `python _scripts/validate_terminology.py` from the wiki root to surface any existing pages that violate the new rule.
4. Either remediate the offending pages or add `allow_forbidden_terms: true` (with justification) where the term is genuinely intentional.

## Related pages

- [[00-Start-Here/Glossary]]
- [[00-Start-Here/How-to-Use-This-Wiki]]
- [[04-Contributing/Style-Guide]]
- `_config/forbidden_terms.yaml`
