---
title: "Build Workflow — 8 Phases"
type: guide
visibility: internal
completion: 40
status: outlined
last_updated: 2026-05-24
dependencies: ["01-Architecture/File-Manifest", "01-Architecture/Automation-Scripts", "01-Architecture/Cross-Link-Generation", "02-Operations/Claude-Behavior-Rules"]
public_pair: null
blocking_questions: []
topics: [codex_operations, cross_link_generation]
related_files: [.claude/personas/CLAUDE.librarian.md, 00-Start-Here/Glossary.md, 01-Architecture/Automation-Scripts.md, 01-Architecture/Configuration-Files.md, 01-Architecture/Cross-Link-Generation.md, 01-Architecture/Design-Principles.md, 01-Architecture/File-Manifest.md, 01-Architecture/Folder-Architecture.md, 01-Architecture/Frontmatter-Schema.md, 01-Architecture/Overview.md, 01-Architecture/Reference-Implementation.md, 01-Architecture/Wiki-Structure.md, 02-Operations/Bootstrap.md, 02-Operations/Claude-Behavior-Rules.md, 02-Operations/Ingest.md, 02-Operations/Quickstart.md, 02-Operations/Sync.md, 04-Contributing/Style-Guide.md, Home.md]
tags: [codex_operations, cross_link_generation]
canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §7"]
unverified_claims: []
---

> **ARCHIVED 2026-05-27 (S003b):** Historical reference. Codex v1.0 is built — the 8-phase build-Codex workflow described here documents the construction of the tool itself, complete as of `project-codex` SHA `c106155` (2026-05-22) → Library extraction Session 1 (2026-05-27). Now historical. Build-Codex-related ops are tracked in `tasks/sessions.md` S001 + S002 close entries.
> Preserved for reference; do not update. Cross-link from current docs at your own risk.
> See `tasks/sessions.md` S003b close entry for the archival decision context.
> Original content below this line.

---

# Build Workflow — 8 Phases

The order to follow when building Codex itself. Hard rule (Operating Preference #6 — see [[Claude-Behavior-Rules]]): build in this order. Don't write `bootstrap.py` before the scripts and templates exist.

## Phase 1 — Intake (BEFORE writing any code)

Ask the user these questions and confirm before proceeding:

1. **Where should Codex be installed?** (e.g., `D:/claude/_codex/`)
2. **Are you providing the Iron Soul reference implementation?** If yes, use it as a derivation source for scripts, configs, and most templates. If no, build from the spec only.
3. **Codex version to start at?** Default: v1.0. The CHANGELOG's first line drives version detection. The spec itself is v1.3 (per header); the built tool starts at v1.0 unless the user specifies otherwise.
4. **Should bootstrap also git-init the new wiki?** Recommended: yes, with an initial commit.
5. **Any project-specific constraints I need to know?** Operating system, Python version available, network restrictions.

## Phase 2 — Scaffold Codex

Create the directory structure from [[File-Manifest]] §5. Empty folders are fine at this stage.

## Phase 3 — Build the scripts

For each of the 15 base scripts plus 3 v1.3 cross-link scripts, implement against the contract in [[Automation-Scripts]] (§2.4) and the principles in [[Design-Principles]]. Reference implementation is in the Iron Soul wiki at the matching filename; the v1.1-new scripts (`check_concept_coverage.py`, `scaffold_source.py`) and the v1.3 cross-link scripts have no Iron Soul precedent and must be implemented from spec.

### v1.2 update — P19 orchestrator contract

When implementing `update_dashboards.py` (P19 in `codex-build-plan.html`), follow the v1.2 contract in §2.4 #1, which requires the orchestrator to synthesize `_dashboards/health.md` after the aggregator + validator pass. Wikis built under v1.1 must re-run P19 under v1.2 to produce the health dashboard.

### Critical implementation details

- **No external dependencies.** Pure Python stdlib only. Do not use PyYAML — implement a tiny YAML-subset parser that handles the formats this spec uses (see `_lib/frontmatter.py`).
- **Path math:** `WIKI_ROOT = Path(__file__).resolve().parent.parent.parent` from inside `_lib/frontmatter.py` (because `_lib` is one level deep inside `_scripts`).
- **Code-block stripping:** Validators that scan markdown content must strip fenced code blocks and inline code before pattern-matching, otherwise example syntax in documentation gets flagged.
- **Frontmatter list fields:** `dependencies`, `blocking_questions`, `canon_sources`, `unverified_claims`, `migrated_to` are all parsed as YAML-subset lists.
- **`check_concept_coverage.py` (v1.1):** reads `_canon/roster.yaml`, counts mentions of each canonical name (and aliases) across all content pages. Matching is **word-boundary** (`\b...\b`), **case-sensitive**, with **aliases counted alongside the canonical name**. Each page is counted **at most once per entity** — the threshold tracks page coverage, not mention frequency. Frontmatter and fenced code blocks are stripped before matching. Output: `_dashboards/concept_coverage.md`. Threshold + folder scope configurable via `_config/concept_coverage.yaml`.
- **`scaffold_source.py` (v1.1):** accepts a local file path or URL. For local files, copies into `_inbox/<basename>.md`. For URLs, the script does NOT fetch — it creates a placeholder `_inbox/<slug>.md` with frontmatter and instructs the user to paste the source content (keeps Codex fully offline and dependency-free).

### v1.3 cross-link build phases (T2 band, pre-orchestrator)

Inserted in the **end of the pre-orchestrator T2 band** (after scaffold scripts P17/P18, before P19 orchestrator). Dependency order: lib → index → linker → validator.

| Phase | Script | Spec # | Notes |
|---|---|---|---|
| **P18.1** | `_lib/topics.py` — topic registry parser | (lib; not in spec table) | Extends `parse_config_yaml` precedent. Validates `_canon/topics.yaml` schema; returns typed Topic objects + alias-resolution lookup. Mirrors `_lib/frontmatter.py` foundation pattern. Sets precedent for the 3 following. |
| **P18.2** | `build_topic_index.py` | #16 | TF-IDF pure stdlib (`math`, `collections.Counter`, `re`). Plug-in import gated behind `_config/cross_link.yaml` presence. Updates frontmatter `topics:` + `tags:` additively (never removes human entries). Dashboard `_dashboards/topic_index.md`. |
| **P18.3** | `cross_link_topics.py` | #17 | Marker-block writer. Idempotent test mandatory. Updates frontmatter `related_files:` and body block atomically (both succeed or both rolled back). |
| **P18.4** | `validate_topic_registry.py` | #18 | (a) every page `topics:` value resolves (error); (b) every registry topic has ≥1 member page (warning). |

P19 (`update_dashboards.py`) keeps its number; its orchestrator contract is amended to run #16 → #17 → #18 between validators and health-summary synthesis (see [[Automation-Scripts]]).

**Test-fixture additions:** `tests/fixtures/sample_wiki/_canon/topics.yaml` with 2–3 topics covering same-folder and cross-folder linking; updated page frontmatter `topics:`; expected `related_files:` post-link state; tag-mirroring cases (flat / nested / disabled / human-entry-preserved).

### Q4 deferral (out of v1.3 active contract)

> *Future enhancement (T-XL-E1, post-v1.0): `delta_source_docs.py` (#13) gains an optional pluggable section-identifier callable. Default line-level diff unchanged. Plug-in shape mirrors the §2.7 cross-link plug-in pattern.* — `delta_source_docs.py` is already shipped (S037, build-plan P16); this is an enhancement-to-shipped, NOT a pre-SHIP item.

## Phase 4 — Build the templates

Create page templates in `_template/` with:

- Complete frontmatter (including `canon_sources: []` and `unverified_claims: []`).
- Placeholder content with `<Project Name>` markers where customization is expected.
- Comments inside YAML config templates showing example entries (commented out, so the file parses but has no active rules).

### `_context/` templates (v1.1 requirements)

- **`INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md`** are shipped verbatim from the separate files accompanying the spec. Do not generate, paraphrase, or modify them.
- **`CLAUDE_CONTEXT_RULES.md`** is customized per project. It must include a **"Question-Answering Behavior"** section with these four rules (canonical count: see `_canon/counts.yaml` "CLAUDE_CONTEXT_RULES.md required Q&A rules" = 4):
  1. Consult wiki pages before raw sources when answering questions about the project.
  2. Cite specific pages using `[[wikilinks]]` in answers.
  3. Flag uncertainty explicitly; never confabulate when canon is silent.
  4. For cross-source synthesis, name every page being synthesized.

These four rules are the minimum. Projects may add more. The section must exist in every bootstrapped `CLAUDE_CONTEXT_RULES.md`.

## Phase 5 — Build `bootstrap.py` and `sync_from_kit.py`

Two user-facing operations. Both must:

- Refuse to operate destructively without confirmation (interactive prompt or `--yes` flag).
- Support `--dry-run` for preview.
- Print clear summaries of what was/will be done.

Bootstrap (v1.1) must create `_sources/raw/` and `_sources/` folders with READMEs. Sync (v1.1) must overwrite `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` but leave `_context/CLAUDE_CONTEXT_RULES.md` untouched.

## Phase 6 — Self-test

Bootstrap a test wiki to a temporary path, run `update_dashboards.py` on it, confirm:

- All aggregators write to `_dashboards/`.
- All validators run with 0 errors.
- The bootstrap is reproducible (idempotent given the same inputs).
- `_sources/raw/` exists and is empty with a README (v1.1).
- `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` exist verbatim (v1.1).

## Phase 7 — Document

Write `README.md` with:

- One-paragraph "what Codex is".
- Quickstart commands (bootstrap a new wiki, sync an existing wiki, ingest a source).
- Pointer to `PROJECT_WIKI_BUILD_SPEC.md` for the full specification.

Write `CHANGELOG.md` starting with `# v1.0 — <today's date>`.

## Phase 8 — Confirm with user

Show the user the file manifest, the directory tree at the install path, and the output of a successful self-test bootstrap. Confirm everything works before considering the build complete.

## Cascade impact (informational; NOT part of amendment scope)

When v1.3 lands:

- Consuming projects with keyword files migrate to `_canon/topics.yaml` (rename + restructure).
- Frontmatter emission at extraction time seeds `topics: []` from keyword-match; #16 augments.
- Codex self-test bootstrap (P54) fixture gains a `_canon/topics.yaml` example.
- Resolves EMCC-side TBDs `<<TBD-codex-tf-idf-pipeline>>` (taxonomy-audit §3 #12) + `<<TBD-codex-tag-namespace>>` (#13).

<!-- codex:see-also:start -->
## See also

- [[CLAUDE.librarian]] — *topic: codex_operations, cross_link_generation, ingest_procedure, librarian_persona*
- [[Glossary]] — *topic: cross_link_generation, framework_durability*
- [[Automation-Scripts]] — *topic: codex_architecture, cross_link_generation*
- [[Configuration-Files]] — *topic: canon_discipline, codex_architecture, cross_link_generation*
- [[Cross-Link-Generation]] — *topic: cross_link_generation, framework_durability, frontmatter_schema*
- [[Design-Principles]] — *topic: canon_discipline, codex_architecture, cross_link_generation, framework_durability*
- [[File-Manifest]] — *topic: codex_architecture, cross_link_generation*
- [[Folder-Architecture]] — *topic: codex_architecture, cross_link_generation*
- [[Frontmatter-Schema]] — *topic: cross_link_generation, framework_durability, frontmatter_schema, status_bands*
- [[Overview]] — *topic: codex_architecture, codex_operations, cross_link_generation, iron_soul_reference*
- [[Reference-Implementation]] — *topic: codex_operations, cross_link_generation, ingest_procedure, iron_soul_reference*
- [[Wiki-Structure]] — *topic: codex_architecture, cross_link_generation, ingest_procedure, status_bands*
- [[Bootstrap]] — *topic: codex_operations, cross_link_generation*
- [[Claude-Behavior-Rules]] — *topic: codex_operations, cross_link_generation, librarian_persona*
- [[Ingest]] — *topic: codex_operations, cross_link_generation, ingest_procedure*
- [[Quickstart]] — *topic: codex_operations, cross_link_generation*
- [[Sync]] — *topic: codex_operations, cross_link_generation*
- [[Style-Guide]] — *topic: cross_link_generation, frontmatter_schema*
- [[Home]] — *topic: codex_architecture, codex_operations, cross_link_generation*
<!-- codex:see-also:end -->
