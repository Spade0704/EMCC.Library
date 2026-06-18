---
title: "Link-Resolver Coherence + Graph Integrity"
type: framework
visibility: internal
completion: 60
status: solid
last_updated: 2026-06-18
dependencies: ["01-Architecture/Cross-Link-Generation", "01-Architecture/Automation-Scripts"]
public_pair: null
blocking_questions: []
topics: [cross_link_generation, codex_architecture, framework_durability]
related_files: [01-Architecture/Cross-Link-Generation.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Design-Principles.md, 04-Contributing/Style-Guide.md]
tags: [cross_link_generation, codex_architecture, framework_durability]
canon_sources: ["EMCC.Library commit f8666f3 (PR #52)"]
unverified_claims: []
---

# Link-Resolver Coherence + Graph Integrity

The cross-reference validator (`check_cross_refs.py`) resolves every `[[wikilink]]`
to decide what is broken and what is orphaned. Three related improvements harden the
resolver's coherence and add a whole-graph integrity layer that single-link checking
cannot see. All three are **additive**: defaults reproduce prior dashboard output, and
the changes were gated against the absence of any real-world links that would flip.

Origin: the Codex-engine cross-reference backlog, items 1–3, landed in PR #52.

## 1. Distinct "escapes wiki root" signal

`_resolve_target` now returns `(page, status)` with `status` in
`{ok, not_found, escapes_root}`. An over-popped link such as `[[../../../x]]` — one that
climbs above the wiki root — renders a distinct dashboard line:

```
- broken: <rel>:<line>: [[<link>]] escapes wiki root
```

separate from the generic `target not found`, and the CLI line gains a terse
`(escapes wiki root)` marker. This tells the Librarian *why* a link is broken (it left
the wiki entirely, versus pointing at a page that does not exist) so the fix is obvious.

Consumer-safe: the dashboard is rendered markdown, not machine-parsed, and **zero**
over-popping `../` links exist in any consumer content today — this is an additive,
future-only signal. The Pattern-#5 locked dashboard literal was updated **with paired tests**.

## 2. Link-graph-integrity layer (`check_link_graph.py`)

A **new additive validator**, `check_link_graph.py`, writes `_dashboards/link_graph.md`.
It **reuses** `check_cross_refs`' link scan and resolver (single source of truth —
imported, not duplicated) to build the directed page graph, then reports two whole-graph
properties cross-refs cannot see:

- **`unreachable_pages`** — pages with no path from the entry page (`Home.md`) by following
  wikilinks. This catches **mutually-linked islands**: pages that link to each other (so they
  clear orphan status) yet are unreachable from the front door.
- **`dead_end_pages`** — pages with zero outbound resolvable links. The directed dual of an
  orphan: nothing leaves the page.

It honours the same `allow_orphan` escape hatch, and the entry page is never self-reported.
The validator is **read-only** and changes no existing check — it is a strictly additional
view onto the same graph.

**Orphan vs unreachable vs dead-end** — three distinct graph defects:

| Defect | Definition | Caught by |
|---|---|---|
| Orphan | No page links *to* it | `check_cross_refs.py` |
| Unreachable | No *path* to it from `Home.md` (clears orphan via island links) | `check_link_graph.py` |
| Dead end | No resolvable links *out* of it | `check_link_graph.py` |

## 3. `./Folder/Page` resolution flipped to page-relative

`[[./Sub/Page]]` from a page in `a/` now resolves to `a/Sub/Page` (page-relative,
**coherent with `../`**), not to root `Sub/Page`. Only an exact leading `./` triggers
page-relative resolution; a `.`-prefixed folder name (e.g. `.hidden/`) stays root-relative.

The flip cleared a silent-finding-flip hazard via a decision gate: every `.md` across all
17 portfolio wikis was grepped for `[[./` — **zero** real `./`-prefixed wikilinks exist
anywhere, so the change alters no current dashboard output. It makes `./` and `../`
resolution coherent for the future.

## Related

- [[Cross-Link-Generation]] — the See-also injection contract these resolvers underpin.
- [[Automation-Scripts]] — `check_cross_refs.py` (#7) and the new `check_link_graph.py` in the script inventory.
- [[Design-Principles]] — cross-link / graph rules.
- [[Style-Guide]] — path-qualified `[[Folder/Page]]` wikilink convention the resolver honours.
