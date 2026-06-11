# Spec-amendment PROPOSAL — boilerplate-page location (per-repo vs once-upstream)

> **Status: PROPOSAL — pending Operator ratification.** Nothing in this document
> amends canon. On ratification the spec edits + build items in §6 become a gated
> session; on rejection the current materialize-then-link convention simply stands.
>
> Routed here by the C2 council (2026-06-10, resolution 2:
> `EMCC/tasks/council/2026-06-10-c2-zoning-doc-conventions.md` — "the prior question
> (per-repo vs once-upstream boilerplate …) routes to EMCC.Library as a Codex
> spec-amendment proposal — session work; spec wins"). The spec itself marks the
> question open: `PROJECT_WIKI_BUILD_SPEC.md` materialize-then-link note (amended
> 2026-06-11, M-A component 5) — "The per-repo-vs-once-upstream boilerplate-location
> question is a SEPARATE pending spec proposal, deliberately not resolved here."

## 1. The question

Bootstrap materializes six ToC-advertised boilerplate pages into every consumer wiki
(`00-Start-Here/{How-to-Use-This-Wiki,Glossary,Terminology-Rules}.md` +
`04-Contributing/{Update-Cascade,File-Routing,Style-Guide}.md`). Once materialized, a
page is consumer content — sync never touches it. Four of the six are **protocol
content** (they describe how Codex works, identically everywhere); materializing them
mints N permanently-diverging forks of upstream prose (the Contrarian's stale-fork
objection, conceded by the C2 chairman). Two are **project content** (Glossary,
Terminology-Rules — meaningless without project-specific entries).

As of M-A component 6 (2026-06-11), all 11 wave consumers carry full materialized
copies of all six pages.

## 2. Proposed split (per the C2 council's named direction)

| Page | Class | Proposed home |
|---|---|---|
| `How-to-Use-This-Wiki` | protocol | **Once upstream** — canonical page in `wiki.codex/git/`; consumers carry a generated stub |
| `Style-Guide` | protocol | Once upstream + stub |
| `Update-Cascade` | protocol | Once upstream + stub |
| `File-Routing` | protocol | Once upstream + stub |
| `Glossary` | project | **Stays per-repo** (materialized full page, consumer-owned — unchanged) |
| `Terminology-Rules` | project | Stays per-repo (unchanged) |

## 3. Stub mechanism — recommended Option A (static stub, no sync-contract change)

A stub is a complete Codex page (frontmatter + ~5 lines): one-paragraph summary of
what the canonical page covers + an explicit pointer to the canonical location
(`EMCC.Library` → `wiki.codex/git/<path>`, repo URL for humans). Properties:

- **Every advertised hop resolves** (the C2 convention lock) — Home.md ToC links hit
  the stub; the stub names the canonical page. No dead links, no cross-repo wikilink
  machinery invented.
- **Nothing to fork.** The stub carries zero substantive prose, so the stale-fork
  problem dissolves rather than being managed: upstream edits land once in
  `wiki.codex` and are immediately current for every consumer, because consumers
  never had a copy.
- **No sync-contract change.** Stubs are materialized at bootstrap exactly like
  today's pages and become consumer content; MERGE-NEW/never-touch semantics
  (LIB-06, locked) are untouched.

**Option B (rejected-by-default, recorded for completeness):** a dedicated
sync OVERWRITE lane for stub files. Gives generator ownership forever, but breaks
the "sync never touches `wiki.<name>/git/` content" contract for marginal benefit —
a 5-line stub has nothing worth propagating. Only revisit if stubs accrete content.

Cross-link note: the four canonical pages live in Library's wiki and join *Codex's*
topic graph only; consumer topic graphs lose nothing (protocol prose was never
project knowledge).

## 4. Migration (one-off, mirrors the M-A wave mechanics)

For each of the 11 wave consumers: replace each of the four protocol pages with the
stub **iff byte-equal to the shipped template** (i.e. never customized). A modified
copy is consumer content — leave it, report it as a finding (same guard rule as the
LIB-08 `_config` sweep). Idempotent loop in the kit (extend
`materialize_boilerplate.py` or a sibling one-off), run per-consumer, one
commit each.

## 5. What this proposal does NOT touch

- Glossary + Terminology-Rules stay per-repo (project content).
- MERGE-NEW semantics (LIB-06 — council-locked 4-1; do not relitigate).
- The materialize-then-link convention itself (bootstrap still guarantees every
  advertised hop resolves at scaffold time — only *what* gets materialized for the
  four protocol pages changes: stub instead of full copy).
- aviation (MI-19 reference-shelf variance), project-codex (archived), SSUSA +
  residehub (nascent/scaffold-only — they inherit whatever is ratified at their
  first real sync).

## 6. On ratification (a gated Library session builds)

1. Author the four canonical pages in `wiki.codex/git/` (promote the current
   `_template/` prose — it is the best existing draft) + Home.md rows.
2. Replace the four `_template/__SEP__` full templates with stub templates;
   `materialize_boilerplate.py` + `bootstrap.py` emit stubs for the four, full pages
   for Glossary/Terminology-Rules. Tests: stub-shape + idempotence + the existing
   materialize suite.
3. Spec edits (spec wins): `PROJECT_WIKI_BUILD_SPEC.md` materialize-then-link note
   gains the split table; `CODEX_BUILD_SPEC_v1_3.md` cross-reference.
4. The §4 migration loop across the 11 consumers (byte-equal guard; findings for
   modified copies).
5. `Index.md`/`Home.md` rows + session record.

## 7. Decision requested from the Operator

- **Ratify / reject the split** in §2 (the C2 council named it; Library proposes it;
  Operator locks it).
- **Stub mechanism:** confirm Option A (recommended) or direct Option B.

*Authored 2026-06-11 (session work per the C2 routing). No fresh council was run:
the C2 council already deliberated this question and named the direction; this
document is that verdict made concrete for ratification — disclosed.*
