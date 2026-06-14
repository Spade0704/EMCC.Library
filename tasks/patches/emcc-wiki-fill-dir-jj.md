# Patch — emcc-wiki fill (dir-20260614jj)

Ready-to-apply by the Director (sole writer of the EMCC working tree). Three parts.
After applying, run the Library validators (command at the bottom) and report the score.

---

## Part 1 — `wiki.EMCC/git/00-Start-Here/Glossary.md` (REPLACE whole file)

Replace the entire file with:

```markdown
---
title: "EMCC — Glossary"
type: reference
visibility: internal
completion: 80
status: solid
last_updated: 2026-06-14
dependencies: []
public_pair: null
blocking_questions: []
canon_sources:
  - "Project-Overview.md"
unverified_claims: []
---

# EMCC — Glossary

Terms and definitions used across the `EMCC` wiki. Each entry is derived from a
`status: solid` page (cited under **See also**) — definitions stay traceable, not
invented. Promote a term into `_canon/roster.yaml` (named entities) or
`_canon/taxonomy.yaml` (structured classifications) once it becomes load-bearing
across multiple pages.

## Terms

### EMCC

The portfolio-orchestration meta-system: the shell that coordinates the module
projects (DFDU/Lattice, Codex/Library, Cartometrics/WYAI, Guard-House, CRW, …),
their agents, the readiness model, and the operator-facing dashboard. See
[[Project-Overview]].

### Director

The orchestrator agent that routes operator intent across modules — convenes the
Council on Level-2+ work, cascades one directive per function to the owning agent,
and aggregates the results into one operator-facing summary. See
[[Routing-Orchestration]] and [[Cross-Session-Orchestration]].

### Cross-session orchestration (cascade)

The end-to-end loop in which the Director coordinates module agents over the peer
channel: directive → agent gates + build → delivery_result → aggregation. Gates
still bind under the cascade. See [[Cross-Session-Orchestration]].

### Route-by-work-kind

The routing-enforcement fallback: when a function has no owning agent, it routes by
the kind of work (e.g. a wiki routes to the Librarian). Locked after the Director's
routing drifted to building inline instead of cascading. See [[Routing-Orchestration]].

### Module / Module System

A registered portfolio project (manifest `module.json`) that the EMCC shell
discovers and wires. Each module owns its repo, agent(s), and gates. See
[[Module-System]].

### Co-development model

The build pattern where a general protocol (in its EMCC module) and a consumer/
physical instance are developed simultaneously. See [[Co-Development-Model]].

### Production-readiness (score / red-band)

The 0–100 readiness score per function in the readiness model; the operator stages
push requests against a target (80 / 95). **Red-band** (<30) functions are handled
carefully and atomically. See [[Production-Readiness]].

### Eval discipline

The eval-driven performance regime — functions/agents are scored against evals, not
self-report. See [[Eval-Discipline]].

### Capability catalog

The registry of portfolio capabilities the dashboard surfaces. See
[[Capability-Catalog]].

### Feedback loop

The compiled-feedback → triage → draft-PR loop (human merges everything; nothing
auto-merges). See [[Feedback-Loop]].

### Inbox triage

The intake pass that sorts in-flight planning material into its destination. See
[[Inbox-Triage]].

### Memory architecture

The portfolio's file-based memory model (wiki-as-memory + per-repo `tasks/` +
auto-memory). See [[Memory-Architecture]].

### Reliability layer

The cross-cutting reliability concerns (error handling, retries, escalation) the
orchestrator depends on. See [[Reliability-Layer]].

### Token economics

The cost model for running the agent fleet — budgets, spend, and the economics of
orchestration. See [[Token-Economics]].

### Dashboard command-center

The operator-facing web dashboard (org chart, readiness, chat relay, liveness) that
drives and observes the portfolio. See [[Dashboard-Command-Center]].

### AI runtime

The live agent-execution layer the orchestration depends on (the systemic unlock
behind many readiness ceilings). See [[AI-Runtime]].

### Genesis and extraction

The portfolio's origin story — how the modules were extracted from the original
monorepo into their own repos. See [[Genesis-and-Extraction]].

### TAT reuse

The cross-portfolio reuse ledger ("while you're at it") — opportunistic reuse of
work across projects. See [[TAT-Reuse]].

## Related pages

- [[Terminology-Rules]]
- [[How-to-Use-This-Wiki]]
- `_canon/roster.yaml`
- `_canon/taxonomy.yaml`
```

> Note: every `[[…]]` above targets an existing `status: solid` page in `wiki.EMCC/git`,
> so the cross-ref validator resolves them. If any page title differs, adjust the link to
> the real stem (or drop the See-also line) — definitions must stay faithful to the page.

---

## Part 2 — `wiki.EMCC/git/Home.md` (clear the codex orphan)

In the **`### Infrastructure (read-only context)`** section, after the
`SEMANTIC_LINT_PROCEDURE.md` bullet (the last bullet before `## Status`), ADD:

```markdown
- [[codex/PROJECT_WIKI_BUILD_SPEC]] — the Codex wiki build spec this wiki was materialized from (protocol canon; **spec wins** any contradiction)
```

---

## Part 3 — allow_orphan the 8 generated tasks mirrors

These are `status: generated` operational mirrors, not curated knowledge pages
(disposition CONFIRMED by the Director). In EACH file's frontmatter block, add the
line `allow_orphan: true` (e.g. immediately after the `status:` line):

- `wiki.EMCC/git/tasks/architect-notes.md`
- `wiki.EMCC/git/tasks/board.md`
- `wiki.EMCC/git/tasks/ideas.md`
- `wiki.EMCC/git/tasks/lessons.md`
- `wiki.EMCC/git/tasks/notes.md`
- `wiki.EMCC/git/tasks/overnight-log.md`
- `wiki.EMCC/git/tasks/sessions.md`
- `wiki.EMCC/git/tasks/todo.md`

---

## Validate after applying

From `D:\Projects\Enterprise Matrix\EMCC.Library`:

```bash
PYTHONPATH="Biz.Automation/wikisys.library/_scripts" python -c "
from pathlib import Path
import check_cross_refs, validate_terminology, validate_canon_integrity
W=Path('D:/Projects/Enterprise Matrix/EMCC/wiki.EMCC/git')
r=check_cross_refs.run(W); print('cross_refs broken=%d orphans=%d'%(len(r['broken_links']),len(r['orphans'])))
print('terminology=%d canon_integrity=%d'%(len(validate_terminology.run(W)['findings']),len(validate_canon_integrity.run(W)['findings'])))
"
```

Expected after apply: **cross_refs broken=0 orphans=0**, terminology=0, canon_integrity=0.
(That run writes `wiki.EMCC/git/_dashboards/*` — revert that generated churn before committing,
per the cosmetic-churn discipline; commit only the Glossary/Home/tasks edits.)

Expected honest score: emcc-wiki **25 → ~50** (Glossary now real + all orphans/broken cleared on
top of the existing 28 solid pages + completion 70). CAPPED <95, ceiling = deeper per-topic
coverage + ongoing ingest needs the live AI runtime + operator source material.
