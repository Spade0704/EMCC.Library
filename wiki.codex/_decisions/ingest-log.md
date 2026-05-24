# Ingest Log

Append-only record of every Ingest operation. New entries land **above** the example block but **below** this header. Each entry follows the format in `_context/INGEST_PROCEDURE.md` §6.

## 2026-05-24 — CODEX_BUILD_SPEC_v1_3.md

- **Source:** `_sources/raw/CODEX_BUILD_SPEC_v1_3.md`
- **Supersedes:** none ingested (predecessors `CODEX_BUILD_SPEC_v1_1.md` / `_v1_2.md` exist but were NOT ingested — they remain external history per the routing spec)
- **Pages created (16):**
  - 01-Architecture: [[Overview]], [[Folder-Architecture]], [[Wiki-Structure]], [[Frontmatter-Schema]], [[Automation-Scripts]], [[Configuration-Files]], [[Cross-Link-Generation]], [[Design-Principles]], [[File-Manifest]], [[Reference-Implementation]]
  - 02-Operations: [[Bootstrap]], [[Sync]], [[Ingest]], [[Build-Workflow]], [[Claude-Behavior-Rules]], [[Quickstart]]
- **Pages updated:** [[Home]] (added 01-Architecture + 02-Operations TOC sections; reframed as Codex wiki orientation); `_context/CLAUDE_CONTEXT_RULES.md` (filled Domain / Audience / Primary-canon-source / last_updated placeholders)
- **Canon entries added:**
  - `roster.yaml`: Codex, Bootstrap, Sync, Ingest, Iron Soul, Librarian, Project Codex, Lattice
  - `topics.yaml`: codex_architecture, codex_operations, cross_link_generation, canon_discipline, frontmatter_schema, ingest_procedure, iron_soul_reference, librarian_persona, framework_durability, status_bands
  - `taxonomy.yaml`: Codex Operation + Bootstrap / Sync / Ingest / Maintenance children (subject-matter only — page-type / status-band / visibility enums deliberately kept OUT of taxonomy; documented as content on [[Frontmatter-Schema]])
  - `counts.yaml`: 15 base scripts, 3 v1.3 cross-link scripts, 18 v1.3 total scripts, 13 design principles, 4 required Q&A rules
  - `timeline.yaml`: DEFERRED — no entries this pass; timeline will seed from the version-history sources (CHANGELOG / build-plan / lessons) in the batch ingest, where the real milestones live
- **Contradictions flagged:**
  - Version-stamp mismatch in source: header reads "v1.3", footer reads "Codex Build Spec v1.2 — April 2026", embedded Phase-1-Q3 reads "spec is v1.2". Recorded as `unverified_claims` on [[Overview]]; header (v1.3) treated as authoritative for routing. A separate upstream Scribe fix to the source doc is being drafted — do NOT edit the archived source.
- **Notes:**
  - Structure is **flat** (pages directly under `01-Architecture/` and `02-Operations/`, no per-subject `Codex/` subfolder).
  - `phase` frontmatter field omitted from all created pages per routing spec.
  - `_inbox/` vs `_sources/raw/` distinction (§2.2) + the §2.6 numbering gap noted on [[Wiki-Structure]] (the latter as `blocking_questions`).
  - Iron Soul is treated as external context only — [[Reference-Implementation]] kept brief; no deep catalog of Iron Soul internals.
  - Embedded v1.1 changelist (source L22–29) preserved verbatim under a "History" section of [[Overview]].
  - **Batch candidate (deferred):** `CODEX_LIBRARIAN.md` is out of scope this pass per routing spec; surfaced here for a future batch ingest alongside related Librarian-persona sources.
  - **Predecessor specs (`CODEX_BUILD_SPEC_v1_1.md` / `_v1_2.md`):** explicitly NOT ingested per routing spec.



<!--
Example entry format — delete this comment block once the first real entry lands.

## YYYY-MM-DD — <source filename>

- **Source:** `_sources/raw/<source>`
- **Supersedes:** `_sources/raw/<predecessor>` (if applicable)
- **Pages created:** [[Page-A]], [[Page-B]]
- **Pages updated:** [[Page-C]] (added section on X), [[Page-D]] (updated table)
- **Canon entries added:** `counts.yaml: foo = 42`; `roster.yaml: Bar-Entity`
- **Contradictions flagged:** <list, or "none">
- **Notes:** <anything the user should know>
-->
