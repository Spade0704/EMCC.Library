---
title: "Semantic Lint Procedure"
type: context_rules
visibility: internal
completion: 100
status: ready
last_updated: 2026-04-23
dependencies: []
canon_sources: ["PROJECT_WIKI_BUILD_SPEC.md §4 (Codex v1.1)"]
unverified_claims: []
---

# Semantic Lint Procedure

**Audience:** Claude, when the user says "lint the wiki" or "run semantic lint."

**Authority:** This procedure complements the structural validators in `_scripts/`. Structural validators are enforcement (regex, frontmatter, link graph, canon integrity, cascade staleness). Semantic lint is inspection — it surfaces concerns that regex cannot see.

## Hard rules

1. **Report only — never modify files.** Output goes to `_dashboards/semantic_lint_report.md`. Even obvious fixes are reported, not applied.
2. **Read the wiki end to end before reporting.** No partial reports. If context is too large, ask the user to scope the lint (e.g. "lint only `02-Frameworks/`").
3. **Cite every finding.** Each issue names the page(s), the section, and the evidence that triggered it.
4. **Never flag `_brain_dump/`** as contradicting canon. Brain dump is explicitly not canon — that is its purpose.
5. **Respect escape hatches.** `allow_forbidden_terms: true` and analogous opt-outs are deliberate. Skip pages that opt out of the relevant check.
6. **Structural issues are out of scope.** Broken links, orphan pages, forbidden terms, canon-integrity gaps, cascade staleness, and briefing-pair sync belong to the structural validators. Do not duplicate them.

## Categories of findings

### A. Page-to-page contradictions (unarbitrated)
Two pages disagree on a fact that `_canon/` does not currently adjudicate. Report both pages, both claims, and whether promoting the fact to canon would resolve the disagreement.

### B. Staleness
A page's claims appear superseded by a newer source in `_sources/raw/` that has not yet been reflected in the wiki. Report the page, the newer source with section reference, and the specific claim that looks stale.

### C. Concept gaps
Proper-noun entities, frameworks, or concepts mentioned in **three or more pages** with no dedicated page of their own. Report the concept, the mentioning pages, and a suggested page path consistent with the domain structure.

### D. Canon gaps
Numbers or named entities appearing in **two or more pages** that belong in `_canon/counts.yaml` or `_canon/roster.yaml` but are not there yet. Report each with a suggested YAML entry. Do not write the entry — propose it.

### E. Tone / voice drift
Pages whose tone or audience register is noticeably inconsistent with neighbors of the same `visibility:` tier. Be conservative here — only flag clear outliers (e.g. a casual blog-voice page sitting among formal framework references at the same visibility).

### F. Orphan reasoning
Entries in `_decisions/` whose rationale references pages, canon facts, or sources that no longer exist or have materially changed meaning. Report the decision entry and the dangling reference.

## Output format

Write `_dashboards/semantic_lint_report.md` with the following structure. Use quad-backtick fences inside to render nested code blocks cleanly.

    ---
    title: "Semantic Lint Report"
    type: dashboard
    visibility: internal
    generated: true
    last_updated: YYYY-MM-DD
    ---

    # Semantic Lint Report — YYYY-MM-DD

    **Scope:** <folder or "whole wiki">
    **Pages reviewed:** N

    ## A. Page-to-page contradictions
    - [[Page-One]] says X. [[Page-Two]] says Y. Canon does not arbitrate.
      Suggest: promote to `_canon/<file>.yaml`.

    ## B. Staleness
    - [[Framework-Foo]] claims <old value>. `_sources/raw/<file>.md §N`
      now says <new value>.

    ## C. Concept gaps
    - "<Concept Name>" mentioned in N pages, no dedicated page.
      Suggest: `<NN-Domain>/<Concept-Name>.md`.

    ## D. Canon gaps
    - <Value> appears in [[Page-A]] and [[Page-B]]. Suggest entry in
      `_canon/counts.yaml`:
      ```yaml
      <key>: <value>   # source: <citation>
      ```

    ## E. Tone / voice drift
    - [[Page-X]] — casual register in a formal tier. (Optional, conservative.)

    ## F. Orphan reasoning
    - `_decisions/<file>.md` cites [[Removed-Page]], which no longer exists.

    ## Summary
    - Contradictions: N
    - Stale claims: N
    - Concept gaps: N
    - Canon gaps: N
    - Tone drift: N
    - Orphan reasoning: N

## When to run

- Monthly on active wikis.
- After any ingest batch larger than three sources.
- Before considering any page `status: ready`.
- Before sharing a public briefing pair externally.
- When the user asks.

## Reminder

Semantic lint is a reading discipline, not a writing one. The user decides what to act on. You produce a map — you do not redraw the territory.
