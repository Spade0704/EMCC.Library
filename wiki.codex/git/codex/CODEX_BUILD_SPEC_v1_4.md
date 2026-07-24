# Codex — Build Specification

**Spec version:** v1.4

## What changed in v1.4

> **v1.4 — Asset Registry (2026-07-21).** Adds §9: Codex gains a portfolio-wide **asset registry**
> — a Librarian-operated ledger of binary assets (UGC images, professional photos, brand assets,
> credentials, video/audio, deliverables) with stable opaque IDs (`AST-<PROJECT>-#####`),
> mandatory-or-explicitly-empty lineage (`derived_from[]`/`recipe`) and `rights_consent`, a
> zone-following privacy rule enforced by a pre-commit-point validator, a crash-safe filing loop
> whose sole commit point is the registry write (remote-store upload decoupled via
> `url: pending`), a retro-ingestion mode with a required pre-flight `local/` snapshot, and a
> remote-store carve-out seam (Cloudflare R2 first backend) outside both the stdlib contract and
> the commit path. Purely additive — no change to any existing section, operation, template, or
> the verbatim procedures. Gate: `tasks/council/2026-07-21-asset-registrar-gate.md`
> (PROCEED-WITH-CHANGES); role + name Operator-ratified 2026-07-21 (Herald OP-4; "asset
> registry" locked, EMCC taxonomy §4(a)).

## What changed in v1.3

> **v1.3 — Cross-link generation.** Stacks on the v1.2 baseline (health-summary orchestration; already shipped). Adds topical cross-linking: a per-project topic registry (`_canon/topics.yaml`), three new scripts (#16 `build_topic_index.py`, #17 `cross_link_topics.py`, #18 `validate_topic_registry.py`), two new optional frontmatter fields (`topics`, `related_files`) plus a human-owned `tags` field, a marker-bracketed "See also" body block, and an optional **project-local** linker plug-in (TF-IDF default is pure stdlib). No change to existing aggregator/validator contracts; the cross-link pipeline runs as an additive stage in `update_dashboards.py`.

> **v1.3 addendum (2026-05-28) — Per-project reorganization manifests.** `bootstrap.py` now emits a `reorganization-instructions.<projectname>.md` stub at the consumer root alongside `CLAUDE.md` / `Index.md` / `Cheatsheet.md` (full + code + website modes; omitted in minimal mode). The new file is RECOMMENDED — see `tasks/plans/portfolio-folder-structure-spec.md` §"Variance allowance". Its sister at `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md` (master) holds patterns P1–P8 + audit-hook contract + the cross-repo index of all per-project manifests. Sync (§4.2 NEVER-touched list) now explicitly excludes the per-project file so consumer-owned move history is not overwritten.

This file (`CODEX_BUILD_SPEC_v1_4.md`) supersedes `CODEX_BUILD_SPEC_v1_3.md`, which remains in the repo as a historical artifact with a deprecation banner pointing here (as v1.2 does toward v1.3). Historical citations of `CODEX_BUILD_SPEC_v1_3.md §N` remain accurate — v1.4 changes no pre-existing section.

---

> **If you are Claude Code and this document is in a project:** your job is to build the **Codex** tool. Codex is a portable, local-first, scaffolding-and-sync tool that creates and maintains documentation wikis for other projects. Read this entire document, then ask the user the Phase 1 questions in Section 7 before writing any code.

**Project name:** Codex
**Project type:** Developer tool (CLI + library, no GUI)
**Language:** Python 3.8+ (pure standard library, zero external dependencies)
**Audience:** A solo developer (and Claude Code) managing multiple projects, each needing structured documentation
**Reference implementation:** the Iron Soul / Planet Scoria Prime wiki, v3.3 — see Appendix A
**Spec version:** v1.4

> **What changed in v1.1 (vs v1.0):**
> - Ingest named as a first-class operation alongside Bootstrap and Sync (§4.3).
> - New permanent source archive `_sources/raw/` alongside the ephemeral `_inbox/` (§2.2).
> - Two new `_context/` templates: `INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md`.
> - New validator `check_concept_coverage.py` (§2.4 #15).
> - New scaffold `scaffold_source.py`.
> - Required Q&A-behavior rules added to the `CLAUDE_CONTEXT_RULES.md` template (§7 Phase 4).
> - Framework/reference durability split named as Principle #12, with a corresponding annotation on the `type` field in §2.3. Tooling to automate the framework export deferred to v1.2.

---

## 1. What Codex Is

Codex is a **scaffolding and sync tool** for creating and maintaining markdown-based documentation wikis. One Codex installation, many consuming-project wikis. Each consuming project's wiki is its own folder of plain markdown files, openable in Obsidian or any markdown reader, with automated dashboards, validators, and integrity checks.

Codex itself is not a wiki. Codex is the tool that *creates* wikis, and that *cascades infrastructure improvements* to wikis it has created without touching their content.

### What Codex produces

A two-tier documentation system:

**Tier 1 — Developer Wiki (internal)** — browseable in Obsidian. Internal frameworks, technical references, contributing guides. Shareable with collaborators when ready.

**Tier 2 — Confidential Profile** — single markdown file with project secrets, business strategy, and behavioral rules Claude follows when the file is loaded as project knowledge. Upload-ready.

Both tiers are plain markdown with YAML frontmatter, with a pure-Python automation layer providing 15 utility functions (dashboards, validators, integrity checks, canon consistency, sync, concept coverage).

### Why Codex exists

Without Codex, a developer running multiple projects either (a) maintains documentation inconsistently across projects, or (b) reinvents the same documentation discipline repeatedly. Codex standardizes the discipline once and applies it everywhere.

The problems Codex solves:
- **Knowledge drift** — facts that change in one place but not in three others
- **Confidentiality leaks** — internal terminology accidentally appearing in public docs
- **Stale documentation** — a framework changed, but its briefing guide is still last quarter's version
- **Loss of decision context** — choices made in chat that nobody remembers six months later
- **Brain dump pollution** — speculative ideas accidentally treated as canonical
- **Source drift** — new sources arriving but never integrated into the wiki (v1.1: Ingest)
- **Multi-project documentation overhead** — every project needing the same structural setup from scratch

---

## 2. Architecture

### 2.1 The Three Folder Roles

```
D:/claude/                              ← workspace root (or wherever)
│
├── _codex/                             ← THE TOOL. Exactly one of these.
│   ├── README.md
│   ├── CHANGELOG.md
│   ├── PROJECT_WIKI_BUILD_SPEC.md
│   ├── bootstrap.py                    Creates new wikis from templates
│   ├── _scripts/                       Master copies of all 15 automation scripts
│   │   └── _lib/
│   │       └── frontmatter.py          Shared parser
│   ├── _config/                        Generic config templates (commented)
│   └── _template/                      Page templates for starter content
│
├── project-x/                          ← A consuming project
│   ├── (project x source code)/        Untouched by Codex
│   └── wiki/                           ← THE WIKI for project x
│       ├── Home.md
│       ├── 00-Start-Here/
│       ├── 01-<Domain-1>/
│       ├── _scripts/                   Synced from _codex/_scripts/
│       ├── _config/                    Customized for project x
│       ├── _canon/                     Project x ground-truth facts
│       ├── _sources/raw/               Project x ingested-source archive (v1.1)
│       └── _confidential/              Project x secrets
│
└── project-y/
    ├── (project y source)/
    └── wiki/                           ← Same structure, different content
```

**Three categories:**

| Category | Role | Count |
|---|---|---|
| `_codex/` | The tool itself | Exactly one |
| `project-x/`, `project-y/`, … | Consuming projects | Many, one per thing you work on |
| `project-x/wiki/`, … | Wikis (one per project) | One per project that wants docs |

### 2.2 Wiki Folder Structure (what `bootstrap.py` creates)

```
<project>/wiki/
├── README.md                       Top-level overview for humans
├── Home.md                         Landing page; table of contents
├── 00-Start-Here/                  Overview, glossary, terminology, how-to
├── 01-Domain-1/                    Project-specific section (renamed in Phase 1; bare-name placeholder per Lesson #22 STANDARD 2nd sub-pattern Win32-safety — `<>` characters NTFS-illegal)
├── 02-Domain-2/                    Another project-specific section (bare-name placeholder; rename per Quickstart Appendix B step 1)
├── 04-Contributing/                Update cascade, file routing, style guide, SPEC
├── Attachments/                    Images, diagrams, PDFs
├── public/                         Public-facing briefing-guide pairs
├── scripts/                        Project-specific scripts (e.g. exporters)
├── _dashboards/                    Auto-generated. Never hand-edit.
├── _decisions/                     Append-only decision log (inc. ingest-log.md)
├── _inbox/                         Ephemeral holding pen for sources awaiting triage
├── _sources/raw/                   Permanent, read-only archive of ingested sources
├── _brain_dump/                    Quarantined unvalidated ideas — NOT canon
├── _canon/                         Structured ground-truth facts (YAMLs)
├── _context/                       Claude operating rules for this wiki
├── _scripts/                       The 15 automation scripts (synced from Codex)
├── _config/                        YAML config for validators
└── _confidential/                  Personal + Claude profile. NEVER publish.
```

Folders prefixed `_` are infrastructure. When sharing a wiki externally, exclude every `_`-prefixed folder except optionally `_decisions`.

**`_inbox/` vs `_sources/raw/` (v1.1).** `_inbox/` is ephemeral — a triage area for sources that arrived but haven't been ingested yet. `_sources/raw/` is permanent and read-only — the archive of sources that *have* been ingested. `canon_sources` on wiki pages cite paths in `_sources/raw/`. Ingest moves files from `_inbox/` to `_sources/raw/` on success (see §4.3).

### 2.3 Frontmatter Schema

Every content page has this YAML header:

```yaml
---
title: "Human-Readable Page Title"
type: framework | reference | guide | overview | episode | dashboard | profile | brain_dump | decision | context_rules
visibility: internal | public | confidential
completion: 0-100
status: gap | outlined | solid | ready
phase: 0-N                                 # optional
last_updated: YYYY-MM-DD
dependencies: ["Other-Page"]
public_pair: "public/Briefing.md" | null
blocking_questions: ["What is X?"]
canon_sources: ["_sources/raw/<file>.md §2.1"]   # required for status: ready
unverified_claims: []                      # must be empty for status: ready
source: "Free-text citation (legacy)"
allow_forbidden_terms: true | false        # optional escape hatch
generated: true                            # auto-gen dashboards only

# Brain dump entries only:
dump_status: exploring | validated | migrated | superseded | rejected
migrated_to: ["Path/To/Canon-Page.md"]
---
```

Status band rule: `ready` ≥ 80, `solid` 55–79, `outlined` 30–54, `gap` < 30.

**`type` durability convention (per Principle #12):** `framework` pages are load-bearing — the structural rules of the project. Consuming projects are expected to mirror every `type: framework` page to an external durable location (typically a Claude project knowledge file). `reference`, `episode`, and similar inventory types are derived from frameworks plus source material; their durability is only as good as the wiki itself. `guide`, `overview`, `dashboard`, `profile`, `brain_dump`, `decision`, and `context_rules` are operational and not part of the framework/reference split.

**Source files in `_inbox/` and `_sources/raw/` use a reduced frontmatter (v1.1):**

```yaml
---
source: "Original citation (URL, book, conversation, etc.)"
ingested_date: YYYY-MM-DD                  # date scaffolded, not date ingested
status: pending_triage | ingested          # supersedes the content-page status values
---
```

`scaffold_source.py` creates these with `status: pending_triage`. Ingest flips them to `ingested` on archive.

**v1.3 additions — Cross-link frontmatter fields.** Add to the content-page frontmatter contract three new **optional** fields:

```yaml
topics: []              # list of topic names; human-curated + script-augmented (additive, never clobbered)
related_files: []       # list of repo-relative paths; SCRIPT-MANAGED — humans should not hand-edit
tags: []                # Obsidian tags; HUMAN-OWNED, optional script-mirroring from topics (additive, never clobbered)
```

**Semantics:**
- `topics`: every value MUST resolve to an entry in `_canon/topics.yaml` (validated by #18). Humans add topics they know apply; `build_topic_index.py` (#16) appends additional topics it detects via keyword + TF-IDF, never removes human-entered values.
- `related_files`: managed exclusively by `cross_link_topics.py` (#17). Single source of truth for the page's outgoing topical links. Body "See also" block is a rendered view of this list.
- `tags`: human-owned ad-hoc workflow markers (`studythisnow`, `review-q3`, `check-ride-prep`). If `_config/cross_link.yaml` enables tag mirroring (default `mirror_from: [topics]`), #16 appends topic-derived tags additively. Codex NEVER removes from `tags:` regardless of config — same contract as `topics:`.

All three default to empty list when absent. Validators tolerate absence. **Inline `#tag` in body prose** is preserved untouched by all body-scanning validators (existing strip-code-blocks-only behavior); Codex manages frontmatter `tags:` only — inline tags are pure human territory.

### 2.4 The 18 Automation Scripts

All pure Python stdlib. No `pip install`. Live in `_scripts/` of every wiki, master copies in `_codex/_scripts/`.

| # | Script | Purpose |
|---|---|---|
| 1 | `update_dashboards.py` | Master orchestrator — runs all aggregators and validators |
| 2 | `build_completion_dashboard.py` | Red/yellow/green completion dashboard |
| 3 | `validate_terminology.py` | Forbidden-terms scan, context-aware |
| 4 | `validate_reveal_conceit.py` | Leak scan on `visibility: public` pages |
| 5 | `validate_canon_integrity.py` | `status: ready` must have `canon_sources`, empty `unverified_claims` |
| 6 | `check_cascade.py` | Source → parallel doc mtime comparison |
| 7 | `check_cross_refs.py` | Broken `[[links]]` + orphan pages |
| 8 | `check_framework_briefing_sync.py` | Framework ↔ public-pair staleness |
| 9 | `check_canon_consistency.py` | Page contradictions vs `_canon/` AND page-to-page |
| 10 | `collect_open_questions.py` | Roll up all `blocking_questions` |
| 11 | `steel_thread_tracker.py` | Multi-layer feature completion |
| 12 | `build_canon_drift_report.py` | Snapshot + diff of `_canon/` over time |
| 13 | `delta_source_docs.py` | Diff two source-doc versions + cascade impact |
| 14 | `sync_from_kit.py` | Pull updated infrastructure from the Codex installation |
| 15 | `check_concept_coverage.py` | Entities in `_canon/roster.yaml` mentioned in pages but lacking a dedicated page (v1.1) |
| + | `scaffold_brain_dump.py` | Create a new brain dump entry |
| + | `scaffold_source.py` | Create a new `_inbox/` entry with frontmatter for ingest (v1.1) |
| + | `scaffold_<type>.py` | Project-specific scaffolds (added per project) |

The orchestrator additionally synthesizes `_dashboards/health.md` after the aggregator + validator pass completes. The health summary captures, in a single dashboard, the following signals roll-up: completion percentage (from `build_completion_dashboard.py`), canon contradictions (from `check_canon_consistency.py` page-vs-canon mode), cascade staleness (from `check_cascade.py`), concept-coverage gaps (from `check_concept_coverage.py`), unverified-claim count (aggregated from page frontmatter `unverified_claims[]` totals), and recent ingest entries (most recent N entries from `_sources/raw/`'s ingest log per `INGEST_PROCEDURE.md`). Health summary frontmatter follows the standard 5-field dashboard contract (`title` / `type: dashboard` / `visibility: internal` / `generated: true` / `last_updated: YYYY-MM-DD`).

**v1.3 additions — Cross-link script rows.** Append three rows to the §2.4 scripts table:

| # | Script | Purpose |
|---|---|---|
| 16 | `build_topic_index.py` | Builds topic → pages map from `_canon/topics.yaml` keywords + TF-IDF augmentation. Updates each page's frontmatter `topics: []` additively; mirrors topic-derived `tags:` per config. Writes `_dashboards/topic_index.md`. |
| 17 | `cross_link_topics.py` | For each multi-page topic, writes `related_files: []` in frontmatter AND a marker-bracketed "See also" block in body. Idempotent. Reads index from #16. |
| 18 | `validate_topic_registry.py` | Every page `topics:` value resolves in `_canon/topics.yaml` (error). Every registry topic has ≥1 member page (warning; orphan-topic detection). |

**Orchestrator update (#1).** `update_dashboards.py` runs #16 → #17 → #18 after the existing aggregator/validator pass, **before** health-summary synthesis. Pipeline order matters: #17 needs #16's index; #18 validates the post-#17 state. Health summary gains a `cross_link_coverage` signal (pages with ≥1 entry in `related_files`). **Failure isolation:** #16/#17/#18 failure produces a stderr warning + non-zero exit but does NOT block the existing aggregator/validator runs or other dashboard regeneration.

> **Numbering note (reconciled).** Spec-table `#16/#17/#18` are the scripts' rows in this §2.4 table. Their build-plan phases are **P18.2 / P18.3 / P18.4** respectively (with foundation lib `_lib/topics.py` at **P18.1**). Build-plan `P16` is the already-shipped `delta_source_docs.py` (S037) — a different axis. See §7.

### 2.5 Configuration Files

**`_config/`** (behavior tuning, per-project):

- **`forbidden_terms.yaml`** — regex rules for trademark/naming violations, context-aware (`all` / `audience` / `internal`)
- **`reveal_leak_patterns.yaml`** — phrases that leak unreleased content. Severities: `error` / `warning` / `info` (info documents approved terms without flagging)
- **`cascade_map.yaml`** — source → derived doc propagation
- **`steel_threads.yaml`** — multi-layer feature manifest
- **`concept_coverage.yaml`** (v1.1, optional) — tunes `check_concept_coverage.py`. Keys: `min_mentions` (default 2), `exclude_folders` (list of folder names skipped during scanning), `exclude_entities` (list of canonical names skipped — escape hatch)

**`_canon/`** (ground-truth facts, per-project):

- **`counts.yaml`** — every canonical number that appears more than once
- **`roster.yaml`** — named entities with canonical names and aliases
- **`taxonomy.yaml`** — structured classifications
- **`timeline.yaml`** — milestones, versions, progression parameters

The consistency checker reads `_canon/` as ground truth. Pages contradicting it are flagged. Pages contradicting *each other* (when `_canon/` doesn't arbitrate) are also flagged in a separate section.

**v1.3 additions — Cross-link configuration.**

### `_canon/topics.yaml` (NEW)

Per-project topic registry. Ground truth. Schema:

```yaml
topics:
  - name: example_topic                 # canonical topic name; lowercase, snake_case
    aliases: [alt_name]                 # alternate names accepted in frontmatter topics: lists
    keywords:                           # word-boundary case-insensitive patterns scanned in H1/H2/intro
      - "example"
    cross_manual: true                  # if true, links across top-level folder boundaries; default false
    min_similarity: 0.35                # optional per-topic TF-IDF override; defaults from _config/cross_link.yaml
```

Matching rules:
- Word-boundary (`\b...\b`), case-insensitive by default.
- Frontmatter + fenced code blocks stripped before scanning (precedent: lessons.md "strip-as-whitespace for body-scanning validators").
- Aliases counted as topic matches alongside canonical name (precedent: `roster.yaml` in `check_concept_coverage.py`).

> Template instance ships **domain-neutral** (1–2 placeholder topics + commented examples + structurally-valid empty default) — drafted in T-XL-7 scope, not this spec. Consuming projects populate domain content themselves.

### `_config/cross_link.yaml` (NEW, optional)

Behavior tuning. All keys optional with documented defaults:

```yaml
tfidf:
  min_similarity: 0.35                  # cosine threshold below which pages are not linked
  max_links_per_page: 8                 # cap on "See also" entries per page
  scan_fields: [h1, h2, intro_para_1]   # which page regions feed the TF-IDF vector

plugin:
  module_path: ~                        # e.g. "scripts/st_linker.py" — PROJECT-LOCAL Python file; default unset
  callable: ~                           # callable name; signature: link(pages: list[ParsedPage]) -> dict[str, list[str]]
  weight: 0.5                           # blend factor when augmenting TF-IDF (0.0 = TF-IDF only; 1.0 = plug-in only)

tags:
  mirror_from: [topics]                 # frontmatter fields to mirror as tags; [] disables mirroring
  prefix_scheme: flat                   # flat | nested ; "nested" emits "topic/smoke" instead of "smoke"
  prefix_map:                           # used only when prefix_scheme: nested
    topics: topic                       # topics: [smoke] → tags: [topic/smoke]
```

If `plugin.module_path` is unset, #16 runs **TF-IDF only (pure stdlib)**. If set, Codex dynamically imports the project-local module and merges its output with TF-IDF results per `plugin.weight`. Tag mirroring defaults to mirror-from-`topics`, flat prefix.

---

### 2.6 — Reserved (intentionally unused)

> §2.7 (Cross-link Generation Contract) was added in the v1.3 amendment (commit `6fd35a6`) and numbered directly, leaving §2.6 unpopulated. §2.6 has never held content in any version of this spec. This note exists so the skip is not re-investigated; the number is free for future use, and populating it requires no renumbering of §2.7+.

### 2.7 Cross-link Generation Contract (NEW SECTION, v1.3)

#### Marker contract (mandatory)

`cross_link_topics.py` injects a "See also" block bracketed by literal markers:

```markdown
<!-- codex:see-also:start -->
## See also

- [[OtherPageStem]] — *topic: smoke*
- [[AnotherPageStem]] — *topic: smoke, fumes*
<!-- codex:see-also:end -->
```

Rules:
- Markers are byte-exact. The linker locates the block via marker pair and replaces only content between them.
- Block placement: end of file by default, before any trailing trivia. If a marker pair already exists anywhere in the file, that position is preserved.
- Human edits **between** markers are OVERWRITTEN on next run — by design. Humans edit `topics:` in frontmatter to influence the rendered block.
- Human edits **outside** the marker pair are preserved.
- Wikilink format: `[[FileStem]]` (precedent: lessons.md "wikilinks use filename stem, not page path or frontmatter title"). **Exception (v1.3.1 duplicate-stem disambiguation, opt-in):** see "See-also list control" below.

#### See-also list control (v1.3.1, 2026-06-13 — opt-in, defaults preserve v1.3 output byte-for-byte)

Two `_config/cross_link.yaml` `see_also:` keys tune the `cross_link_topics.py` (#17) block. Both default to the pre-v1.3.1 behavior so existing consumers are unaffected (no `see_also` section → identical output):

- `max_links_per_page` (int; default **0 = uncapped**). When > 0, the related set is ranked and truncated to the top-N. Ranking key: (shared-topic-count desc, then a DIFFERENT top-level container first — surfaces cross-manual/cross-section jumps, then path asc for stable idempotent output). `related_files:` frontmatter records the same capped set. Rationale: a broad topic spanning hundreds of pages otherwise yields an unusable See-also block; the cap keeps the *most related*, not an arbitrary slice.
- `disambiguate_duplicate_stems` (bool; default **false**). When true, a link whose target stem occurs in **more than one** content page wiki-wide is rendered path-qualified: `[[<wiki-relative-path-without-ext>|<Stem> (<top-level-container>)]]`, so Obsidian resolves it unambiguously. Collision-triggered only — unique stems stay bare `[[Stem]]`, so wikis without cross-folder stem collisions are byte-identical regardless of this flag. Required by wikis that legitimately carry same-named pages across folders/manuals (e.g. a QRH quick-reference page and its FCOM master page sharing a stem).

The marker contract, idempotency requirement, and "frontmatter is source of truth" rule are unchanged by these options.

#### Frontmatter as source of truth

`related_files: []` in frontmatter is canonical. The body block is a rendered view. If they ever disagree (e.g. user manually edits frontmatter), `cross_link_topics.py` regenerates the block to match frontmatter on next run.

#### Plug-in interface (TF-IDF default + optional project-local augmentation)

Default linker is TF-IDF cosine over the page's scan fields, implemented in **pure stdlib** (`math`, `collections.Counter`, `re`). Project-local plug-ins extend by exposing a callable:

```python
# scripts/st_linker.py (PROJECT-LOCAL example — NOT distributed by Codex)
from sentence_transformers import SentenceTransformer
_model = SentenceTransformer("all-MiniLM-L6-v2")

def link(pages):
    """pages: list of dicts {path, title, intro, topics, frontmatter}
       returns: dict mapping page path → list of related page paths"""
    ...
```

`build_topic_index.py`: (1) runs TF-IDF on all pages (always, pure stdlib); (2) if `_config/cross_link.yaml` defines a plug-in, imports `module_path:callable` and calls it; (3) blends both per `plugin.weight` (linear interpolation of similarity scores; union of candidates); (4) writes the final index.

Plug-in failures (import error, callable exception, malformed return) log a warning and **degrade to TF-IDF-only. Never block the pipeline.**

> **! Status (v1.3.1): EXPERIMENTAL — not yet invoked.** `load_plugin`/`blend_results` exist with the contract above, but the live `build_topic_index.py` run path does **not** call them this cycle (`plugin.module_path` defaults unset; the call site is reserved). Custom See-also ranking is shipped instead via `_config/cross_link.yaml` `see_also:` (cap + shared-topic/cross-container ranking). Treat `plugin:` as a forward-declared contract, not a shipped feature, until wired + tested.

> **! R_ARCH carve-out (stdlib-only contract).** Project-local plug-ins are **out-of-scope** for Codex's stdlib-only contract — they are consuming-project artifacts, dynamically imported via opt-in config (`_config/cross_link.yaml` `plugin.module_path`), failure-isolated to log-and-degrade. Codex itself imports **zero** non-stdlib packages; plug-ins may import anything in their own environment. This is **distinct from** the 2026-05-20 triage reject, which targeted a Codex-*bundled* plug-in architecture (rejected). (Mirrored canonically in `CLAUDE.md` R_ARCH › D_RULES.)

#### Tag mirroring (optional, configurable)

`build_topic_index.py` (#16) optionally mirrors frontmatter field values into `tags:`:
- Reads `_config/cross_link.yaml`'s `tags.mirror_from` (defaults `[topics]`).
- For each source field per page, adds each value to `tags:` if not already present.
- Applies `prefix_scheme` if `nested`.
- NEVER removes existing tags. Additive only — same contract as topic auto-detection.

Tag-mirroring failures (missing config, malformed `prefix_map`) degrade silently: linker proceeds without mirroring, logs a warning.

#### Inline body tags are off-limits to Codex

Inline `#tag` syntax in body prose is invisible to Codex's writers. Body-scanning validators (terminology, reveal-conceit) treat `#tag` as ordinary text but never rewrite it. Humans own inline tags entirely.

#### Idempotency requirement

Running `cross_link_topics.py` twice in succession with no source changes produces **zero diffs**. Test fixture must verify this (precedent: P4 aggregator test patterns).

---

## 3. Design Principles

1. **One idea per page.** If a page grows past ~400 lines, split it.
2. **Authoritative source ≠ wiki.** The wiki is derived. Source wins conflicts. Cite via `canon_sources`.
3. **Internal/public split is directional.** Internal → Public, never reverse. Strip internal terminology unless confirmed public-safe. Public pages link only to other public pages.
4. **Update cascade is directional.** Source → Derived → Wiki. Never reverse.
5. **Frontmatter is the API.** Scripts read frontmatter. Don't hardcode page metadata.
6. **Validators have escape hatches.** `allow_forbidden_terms: true` exists by design.
7. **Dashboards are expendable.** Regenerated every run.
8. **Canon is the floor, not the ceiling.** `_canon/` captures facts that MUST be consistent. Pages can contain more — they just can't contradict canon.
9. **Brain dump is quarantine.** `_brain_dump/` is explicitly NOT canon. Promotion is always explicit.
10. **Codex is the tool, not the content.** Codex never holds project content. It creates and updates wikis. Each wiki holds its own content.
11. **Ingest proposes, humans dispose (v1.1).** Canon writes require confirmation. Contradictions get flagged, not overwritten. Archived sources are read-only.
12. **Frameworks are load-bearing; references are derived inventory.** Pages with `type: framework` are the structural rules of a project — they should exist in both the wiki and an external durable location (e.g. project knowledge files uploaded to a Claude project). Pages with `type: reference` (and similar inventory types: `episode`, etc.) are generated from frameworks plus sources, and are durable only to the extent that the wiki itself is. Losing a reference is recoverable from its framework; losing a framework is not. The wiki is the source of truth for both, but frameworks earn a second home.
13. **Cross-link injection is marker-bracketed and idempotent (v1.3).** Frontmatter `related_files: []` is the source of truth; the body "See also" block is its rendered view. Content between `<!-- codex:see-also:start -->` and `<!-- codex:see-also:end -->` is regenerated every run; human prose around the markers is preserved. Humans curate `topics: []` to influence what gets linked; they do not hand-edit the rendered block. Frontmatter `tags: []` is human-owned but optionally mirror-augmented from `topics:` per `_config/cross_link.yaml`. Codex never removes entries from `tags:` — additive only.
14. **Build sessions keep the wiki current (v1.3).** A consuming project's wiki is derived documentation maintained **every build session**, not a one-time artifact. A coding session that changes a project (code, schema, config, APIs, behavior) is not done until that project's wiki reflects it: update the affected pages, run the cascade, bump `last_updated`, and log the session. This per-session contract is encoded in the bootstrapped `_context/CLAUDE_CONTEXT_RULES.md` ("Wiki Maintenance Behavior") and `04-Contributing/Update-Cascade.md` ("Per build session") — see §7 Phase 4.

---

## 4. The Three Operations Codex Performs

### 4.1 Bootstrap (one-time per project)

```bash
cd <wherever Codex is installed>
python bootstrap.py <target-wiki-path>
```

Creates the full wiki folder structure at `<target-wiki-path>`, copies all 15 scripts, drops in commented config templates, populates starter meta-pages (Home, Glossary, Terminology-Rules, How-to-Use-This-Wiki, Style-Guide, Update-Cascade, File-Routing, Confidential Profile skeleton, CLAUDE_CONTEXT_RULES, INGEST_PROCEDURE, SEMANTIC_LINT_PROCEDURE, canon/brain_dump/decisions/sources READMEs).

After bootstrap, the consuming project does Phases 3–7 of Section 7 to populate content.

### 4.2 Sync (ongoing, when Codex itself improves) — v1.1

S004 / MI-16 closure rewrote `sync_from_kit.py` for the v1.1 consumer
layout. The script is invoked from the **consumer project ROOT** (not
from inside a `wiki.<name>/` subfolder); it auto-discovers the consumer
name by globbing `Biz.Automation/wikisys.<name>/` and pairs it with the
matching `wiki.<name>/git/` directory.

```bash
cd <consumer project root>
python <library>/Biz.Automation/wikisys.library/_scripts/sync_from_kit.py <library>
```

Pulls updated infrastructure from EMCC.Library into the consuming
project's v1.1 canonical-layout zones:

- **Overwritten:** `Biz.Automation/wikisys.<consumer>/_scripts/` (the full Codex automation tree from Library's `Biz.Automation/wikisys.library/_scripts/`)
- **Overwritten:** `wiki.<consumer>/git/codex/PROJECT_WIKI_BUILD_SPEC.md` (spec doc lands inside the consumer's wiki content zone, mirroring Library's own `wiki.codex/git/codex/` pattern)
- **Overwritten:** `Biz.Automation/wikisys.<consumer>/_context/INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`, `CODEX_LIBRARIAN.md` (verbatim-shipped procedures — never customize)
- **Merge-new-only:** `Biz.Automation/wikisys.<consumer>/_config/<filename>` and `Biz.Automation/wikisys.<consumer>/_template/<filename>` (existing customized files preserved; new files added)
- **NEVER touched:** all content folders under `wiki.<consumer>/git/` (`Home.md`, `00-Start-Here/`, `01-*/`, `_archive/`, `raw/`, `README.md`), all content under `wiki.<consumer>/local/` (gitignored zone), `Biz.Automation/wikisys.<consumer>/_canon/` (consumer's canon YAML), `Biz.Automation/wikisys.<consumer>/_decisions/` (consumer's ingest log), `Biz.Automation/wikisys.<consumer>/_dashboards/` (generated), `Biz.Automation/wikisys.<consumer>/_context/CLAUDE_CONTEXT_RULES.md` (consumer-customized), root files (`CLAUDE.md`, `Index.md`, `Cheatsheet.md`, `reorganization-instructions.<consumer>.md`, `emcc.modules.json`, `.gitignore`), `tasks/*.md`, `assets/*`, `0-Inbox/*`, `.claude/*`

Sync refuses to run if:
- The consumer tree has uncommitted git changes (override with `--force`; exit code 2).
- Required sources are missing at the Library install path (exit code 3).
- Consumer-name discovery is ambiguous: zero or multiple `Biz.Automation/wikisys.*/` matches at consumer root (use `--consumer-name <name>` to disambiguate; exit code 4).

Sync supports `--dry-run` to preview changes.

**v1.0-shape consumer support retired in S004.** Pre-S004 wikis (with
`_scripts/` etc. at wiki root) must either (a) migrate to v1.1 first
following the Mentor S004 playbook, or (b) freeze at v1.0 and use a
pre-S004 build of `sync_from_kit.py` (preserved at git SHA `8c2193c` on
`main`).

### 4.3 Ingest (ongoing, once per new source) — v1.1

```bash
# In the consuming wiki:
python _scripts/scaffold_source.py <path-or-url>
# Then, in Claude Code:
# "Ingest _inbox/<source>.md"
```

Reads a new source document and integrates it into the wiki: extracts facts, routes them to `_canon/` (with confirmation) or to existing/new wiki pages, links related concepts, archives the original source, and appends an entry to `_decisions/ingest-log.md`.

Ingest is the most frequent Codex operation on a live project. Unlike Bootstrap (one-time) and Sync (occasional, initiated from Codex), Ingest happens whenever a new source enters orbit — an article, a meeting note, a spec revision, a transcript.

The full procedure Claude follows is documented in `_context/INGEST_PROCEDURE.md` (shipped by bootstrap). Summary:

1. **Read** the source in `_inbox/<source>.md`.
2. **Extract** candidate facts, entities, and concepts. Group by: canon-worthy (numbers, named entities, timeline events), page-worthy (a concept deserving its own page), mention-worthy (belongs in an existing page).
3. **Route** each item:
   - Canon-worthy → propose YAML entry for `_canon/*.yaml`; **ask before writing**.
   - Page-worthy → create a new page under the correct domain folder with full frontmatter (`canon_sources` pointing at the archived source, `status: outlined` or higher).
   - Mention-worthy → update the existing page; cite the source.
   - Contradicts canon or an existing page → flag in the ingest log; **never silently overwrite**.
4. **Link** — add `[[wikilinks]]` between related pages. Update `Home.md` only if a new top-level section was created.
5. **Archive** — move the source from `_inbox/` to `_sources/raw/` (permanent, read-only archive). Update source frontmatter: `status: ingested`, `ingested_date: YYYY-MM-DD`.
6. **Log** — append an entry to `_decisions/ingest-log.md` naming: date, source filename, pages created, pages updated, canon entries added, contradictions flagged.
7. **Validate** — run `python _scripts/update_dashboards.py` and confirm no new validator errors.

**Writes:** `_canon/*.yaml` (with confirmation), new/updated wiki content pages, `_decisions/ingest-log.md`, source frontmatter (status), optionally `Home.md` (only if a new top-level section is created).

**Moves:** `_inbox/<source>` → `_sources/raw/<source>` on successful ingest.

**NEVER touched:** `_scripts/`, `_config/`, `_confidential/` (unless the user explicitly directs), `_brain_dump/`, unrelated content pages, `04-Contributing/`.

Ingest refuses to run if:
- The source in `_inbox/` lacks required frontmatter (`source`, `ingested_date`, `status: pending_triage`). Run `scaffold_source.py` first.
- Canon contradictions are detected and the user has not confirmed either overwrite or quarantine.
- The wiki has uncommitted git changes from an unrelated session (override with `--force`).

Ingest supports `--dry-run` to preview the full routing plan without writing anything — recommended for the first ingest in any new project, and for any source over ~5k words.

---

## 5. Codex File Manifest (what to build)

Build these files in `_codex/`:

```
_codex/
├── README.md                                Quickstart for humans
├── CHANGELOG.md                             Version history (first line: "# v1.0 — <date>")
├── PROJECT_WIKI_BUILD_SPEC.md               The portable spec (this document, copied)
├── bootstrap.py                             Scaffolder
│
├── _scripts/
│   ├── _lib/
│   │   ├── __init__.py
│   │   └── frontmatter.py                   Shared frontmatter + YAML-subset parser
│   │
│   ├── update_dashboards.py                 Orchestrator
│   ├── build_completion_dashboard.py
│   ├── validate_terminology.py
│   ├── validate_reveal_conceit.py
│   ├── validate_canon_integrity.py
│   ├── check_cascade.py
│   ├── check_cross_refs.py
│   ├── check_framework_briefing_sync.py
│   ├── check_canon_consistency.py
│   ├── collect_open_questions.py
│   ├── steel_thread_tracker.py
│   ├── build_canon_drift_report.py
│   ├── delta_source_docs.py
│   ├── sync_from_kit.py
│   ├── check_concept_coverage.py            (v1.1)
│   ├── scaffold_brain_dump.py
│   └── scaffold_source.py                   (v1.1)
│
├── _config/                                 Templates with commented examples
│   ├── README.md
│   ├── forbidden_terms.yaml
│   ├── reveal_leak_patterns.yaml
│   ├── cascade_map.yaml
│   ├── steel_threads.yaml
│   └── concept_coverage.yaml                (v1.1, optional)
│
└── _template/                               Page templates for starter content
    ├── Home.md
    ├── 00-Start-Here__SEP__Project-Overview.md
    ├── 00-Start-Here__SEP__How-to-Use-This-Wiki.md
    ├── 00-Start-Here__SEP__Glossary.md
    ├── 00-Start-Here__SEP__Terminology-Rules.md
    ├── 04-Contributing__SEP__Update-Cascade.md
    ├── 04-Contributing__SEP__File-Routing.md
    ├── 04-Contributing__SEP__Style-Guide.md
    ├── _canon__SEP__README.md
    ├── _canon__SEP__counts.yaml
    ├── _canon__SEP__roster.yaml
    ├── _canon__SEP__taxonomy.yaml
    ├── _canon__SEP__timeline.yaml
    ├── _brain_dump__SEP__README.md
    ├── _decisions__SEP__README.md
    ├── _decisions__SEP__ingest-log.md             (v1.1, starter append-only log)
    ├── _inbox__SEP__README.md
    ├── _sources__SEP__README.md                   (v1.1)
    ├── _sources__SEP__raw__SEP__README.md         (v1.1, explains read-only archive)
    ├── _context__SEP__CLAUDE_CONTEXT_RULES.md
    ├── _context__SEP__INGEST_PROCEDURE.md         (v1.1, ship verbatim — see separate file)
    ├── _context__SEP__SEMANTIC_LINT_PROCEDURE.md  (v1.1, ship verbatim — see separate file)
    └── _confidential__SEP__Confidential_Profile.md
```

Template filenames use `__SEP__` as a path separator placeholder. The `bootstrap.py` script replaces `__SEP__` with `/` when copying templates into the destination wiki.

**Rationale.** Win32 reserves 9 characters in NTFS filenames (`<>:"|?*` plus NUL plus path-separators `/\`); using any of these as a placeholder produces silent MSYS2/Cygwin Private-Use-Area mangling on Windows (e.g. `|` U+007C → U+EF7C via POSIX-EFXX +0xEF00 offset) that breaks the `bootstrap.py` substitution contract at runtime. `__SEP__` is filesystem-safe across POSIX, Windows, and git tree representation, with zero real-filename collision risk. See `tasks/lessons.md` 2026-05-16 entry on Win32 reserved chars in spec filename placeholders (Lesson #22 STANDARD).

`INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md` are shipped verbatim from the separate files accompanying this spec — do not paraphrase, do not shorten, do not "improve." They are Claude-facing contracts and their exact wording matters.

---

## 6. Reference Implementation

Codex is derived from the Iron Soul / Planet Scoria Prime wiki, which proved the pattern in production. The reference wiki is at `Iron-Soul-Wiki-v3.3.zip` — every Codex script and template is a generalized version of what exists there.

When building Codex, you can use the Iron Soul wiki as a working example:

- **Iron Soul has:** project-specific config values in `_config/forbidden_terms.yaml` (Iron Soul-specific terms like "MAP", "Scoria Prime"), project-specific canon in `_canon/*.yaml` (Iron Soul-specific facts), project-specific Claude rules in `_confidential/SCORIA_Confidential_Profile.md`
- **Codex needs:** the same files but with **commented-out examples** instead of real values

The transformation pattern: replace project-specific entries with commented examples and leave the file structurally valid (e.g., `rules: []` for an empty config).

If the user provides Iron Soul as a reference, derive each Codex template by sanitizing the Iron Soul file. If they don't, build templates from this spec alone.

**Note (v1.1):** Iron Soul v3.3 pre-dates the Ingest operation. The `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` files must come from the separate files accompanying this spec, not from Iron Soul.

---

## 7. Build Workflow

### Phase 1 — Intake (BEFORE writing any code)

Ask the user these questions and confirm before proceeding:

1. **Where should Codex be installed?** (e.g., `D:/claude/_codex/`)
2. **Are you providing the Iron Soul reference implementation?** (If yes, use it as a derivation source for scripts, configs, and most templates. If no, build from this spec only.)
3. **Codex version to start at?** (Default: v1.0. The CHANGELOG's first line drives version detection. The spec itself is v1.3, but the built tool starts at v1.0 unless the user specifies otherwise.)
4. **Should bootstrap also git-init the new wiki?** (Recommended: yes, with an initial commit.)
5. **Any project-specific constraints I need to know?** (Operating system, Python version available, network restrictions.)

### Phase 2 — Scaffold Codex

Create the directory structure from Section 5. Empty folders are fine at this stage.

### Phase 3 — Build the scripts

For each of the 15 scripts, implement against the contract in Section 2.4 and the principles in Section 3. Reference implementation is in the Iron Soul wiki at the matching filename; the two v1.1-new scripts (`check_concept_coverage.py`, `scaffold_source.py`) have no Iron Soul precedent and must be implemented from spec.

**v1.2 update — P19 contract:** When implementing `update_dashboards.py` (P19 in `codex-build-plan.html`), follow the v1.2 contract in §2.4 #1, which requires the orchestrator to synthesize `_dashboards/health.md` after the aggregator + validator pass. Wikis built under v1.1 must re-run P19 under v1.2 to produce the health dashboard.

Critical implementation details:

- **No external dependencies.** Pure Python stdlib only. Do not use PyYAML — implement a tiny YAML-subset parser that handles the formats this spec uses (see `_lib/frontmatter.py` in the reference implementation).
- **Path math:** `WIKI_ROOT = Path(__file__).resolve().parent.parent.parent` from inside `_lib/frontmatter.py` (because `_lib` is one level deep inside `_scripts`).
- **Code-block stripping:** Validators that scan markdown content must strip fenced code blocks and inline code before pattern-matching, otherwise example syntax in documentation gets flagged.
- **Frontmatter list fields:** `dependencies`, `blocking_questions`, `canon_sources`, `unverified_claims`, `migrated_to` (and the v1.3 cross-link fields `topics`, `related_files`, `tags`) are all parsed as YAML-subset lists. **Both list forms are accepted and equivalent: inline flow (`canon_sources: ["a.md", "b.md"]`) — the canonical / preferred form — and block-style scalar lists (`canon_sources:` then indented `- "a.md"` lines).** Block-style scalar lists were added in dir-20260614qq after the parser was found to silently drop them to `None` (a latent bug — `validate_canon_integrity` only gates `status: ready` pages, so block-list `canon_sources` on `solid`/`outlined` pages was ignored until promotion). Block items must be **indented**; block items that are themselves mappings (list-of-mappings) remain out of scope for frontmatter (only `parse_config_yaml` for `_config/*.yaml` handles those).
- **`check_concept_coverage.py` (v1.1):** reads `_canon/roster.yaml`, counts mentions of each canonical name (and aliases) across all content pages, and reports entities with ≥ N mentions (default N=2) that lack a dedicated page file. Matching is **word-boundary** (`\b...\b`), **case-sensitive**, with **aliases counted alongside the canonical name** (i.e. for each entity, build a regex from `[canonical_name] + aliases` and scan). Each page is counted **at most once per entity** — the threshold tracks page coverage, not mention frequency. Frontmatter and fenced code blocks are stripped before matching. Output is written to `_dashboards/concept_coverage.md`. Threshold and folder scope are configurable via `_config/concept_coverage.yaml` (new, optional).

  #### "Dedicated page" signal (pinned v1.3)

  A **dedicated page** for an entity is a content page whose slug (filename stem, slugified) equals the slugified canonical name of that entity. `check_concept_coverage.py` (P13) flags any `roster.yaml` entity that is mentioned in at least `threshold` pages but has no dedicated page. (This promotes the prior placeholder definition to canonical; behavior for ordinary entities is unchanged.)

  **Subject-entity exemption.** Subject-wikis — where the whole wiki documents a single subject — would otherwise self-flag that subject as uncovered, since no single page is "the" dedicated page when every page is about it. The optional `subject_entities` list in `_config/concept_coverage.yaml` exempts named entities from the no-dedicated-page signal:

  ```yaml
  # _config/concept_coverage.yaml
  subject_entities:
    - Codex        # the wiki's own subject; exempt from the dedicated-page signal
  ```

  Listed entities are excluded from the no-dedicated-page warning but still appear in `_dashboards/concept_coverage.md`, annotated `subject (exempt)`. Default is an empty list — no exemptions, identical to prior behavior.
- **`scaffold_source.py` (v1.1):** accepts a local file path or URL. For local files, copies into `_inbox/<basename>.md`. For URLs, the script does NOT fetch — it creates a placeholder `_inbox/<slug>.md` with frontmatter and instructs the user to paste the source content (keeps Codex fully offline and dependency-free).

**v1.3 additions — Cross-link build phases.** Insert four new phases in the **end of the pre-orchestrator T2 band** (after the scaffold scripts P17/P18, before P19 orchestrator), preserving dependency order: lib → index → linker → validator.

| Phase | Script | Spec # | Notes |
|---|---|---|---|
| **P18.1** | `_lib/topics.py` — topic registry parser | (lib; not in spec table) | Extends `parse_config_yaml` precedent (lessons.md 2026-05-05). Validates `_canon/topics.yaml` schema; returns typed Topic objects + alias-resolution lookup. Mirrors `_lib/frontmatter.py` foundation pattern. Sets precedent for the 3 following. |
| **P18.2** | `build_topic_index.py` | #16 | TF-IDF pure stdlib (`math`, `collections.Counter`, `re`). Plug-in import gated behind `_config/cross_link.yaml` presence. Updates frontmatter `topics:` + `tags:` additively (never removes human entries). Dashboard `_dashboards/topic_index.md`. |
| **P18.3** | `cross_link_topics.py` | #17 | Marker-block writer. Idempotent test mandatory. Updates frontmatter `related_files:` and body block atomically (both succeed or both rolled back). |
| **P18.4** | `validate_topic_registry.py` | #18 | (a) every page `topics:` value resolves (error); (b) every registry topic has ≥1 member page (warning). |

P19 (`update_dashboards.py`) keeps its number; its orchestrator contract is amended to run #16 → #17 → #18 between validators and health-summary synthesis (see §2.4 orchestrator note).

**Test fixture additions:** `tests/fixtures/sample_wiki/_canon/topics.yaml` with 2–3 topics covering same-folder and cross-folder linking; updated page frontmatter `topics:`; expected `related_files:` post-link state; tag-mirroring cases (flat / nested / disabled / human-entry-preserved).

> **Q4 deferral (reclassified per reconciliation).** *Future enhancement (T-XL-E1, post-v1.0): `delta_source_docs.py` (#13) gains an optional pluggable section-identifier callable. Default line-level diff unchanged. Plug-in shape mirrors the §2.7 cross-link plug-in pattern.* — `delta_source_docs.py` is already shipped (S037, build-plan P16); this is an enhancement-to-shipped, NOT a pre-SHIP item. Out of the v1.3 active contract.

### Phase 4 — Build the templates

Create page templates in `_template/` with:
- Complete frontmatter (including `canon_sources: []` and `unverified_claims: []`)
- Placeholder content with `<Project Name>` markers where customization is expected
- Comments inside YAML config templates showing example entries (commented out, so the file parses but has no active rules)

**`_context/` templates (v1.1 requirements):**

- **`INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md`** are shipped verbatim from the separate files accompanying this spec. Do not generate, paraphrase, or modify them.
- **`CLAUDE_CONTEXT_RULES.md`** is customized per project. It must include a **"Question-Answering Behavior"** section with these four rules:
  1. Consult wiki pages before raw sources when answering questions about the project.
  2. Cite specific pages using `[[wikilinks]]` in answers.
  3. Flag uncertainty explicitly; never confabulate when canon is silent.
  4. For cross-source synthesis, name every page being synthesized.

  These four rules are the minimum. Projects may add more. The section must exist in every bootstrapped `CLAUDE_CONTEXT_RULES.md`.

  It must **also** include a **"Wiki Maintenance Behavior"** section (per Principle #14) requiring that **every build/coding session updates the project wiki before it ends** — identify what changed, update the affected pages (+ `canon_sources`/`last_updated`), run the update cascade, and log the session. The bootstrapped `_context/CLAUDE_CONTEXT_RULES.md` and `04-Contributing/Update-Cascade.md` templates ship this rule; like the four Q&A rules, it is the minimum and must remain present.

### Phase 5 — Build bootstrap.py and sync_from_kit.py

These are the two user-facing operations. Both must:
- Refuse to operate destructively without confirmation (interactive prompt or `--yes` flag)
- Support `--dry-run` for preview
- Print clear summaries of what was/will be done

Bootstrap (v1.1) must create `_sources/raw/` and `_sources/` folders with READMEs. Sync (v1.1) must overwrite `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` but leave `_context/CLAUDE_CONTEXT_RULES.md` untouched.

### Phase 6 — Self-test

Bootstrap a test wiki to a temporary path, run `update_dashboards.py` on it, confirm:
- All aggregators write to `_dashboards/`
- All validators run with 0 errors
- The bootstrap is reproducible (idempotent given the same inputs)
- `_sources/raw/` exists and is empty with a README (v1.1)
- `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` exist verbatim (v1.1)

### Phase 7 — Document

Write `README.md` with:
- One-paragraph "what Codex is"
- Quickstart commands (bootstrap a new wiki, sync an existing wiki, ingest a source)
- Pointer to `PROJECT_WIKI_BUILD_SPEC.md` for the full specification

Write `CHANGELOG.md` starting with `# v1.0 — <today's date>`.

### Phase 8 — Confirm with user

Show the user the file manifest, the directory tree at the install path, and the output of a successful self-test bootstrap. Confirm everything works before considering the build complete.

---

## 8. Claude Code Behavior Rules

When this spec is loaded as project knowledge and Codex is being built:

### Hard Rules

1. **Never use external Python packages.** Pure stdlib. Period.
2. **Never edit files outside the Codex install path** unless the user explicitly directs (e.g., for self-test bootstraps to `/tmp/`).
3. **Always run a self-test bootstrap** before declaring Codex complete.
4. **Always show the user the file manifest** at the end of the build.
5. **If the Iron Soul reference implementation is available, derive templates from it.** Do not invent template content from scratch when a working reference exists. Exception (v1.1): `INGEST_PROCEDURE.md` and `SEMANTIC_LINT_PROCEDURE.md` ship verbatim from this spec's accompanying files, not from Iron Soul.

### Operating Preferences

6. **Build in the order of Section 7.** Don't write bootstrap.py before the scripts and templates exist.
7. **Test every script in isolation** as soon as it's written, before moving to the next.
8. **Use the same frontmatter parser** in every script (DRY — `_lib/frontmatter.py` is shared).
9. **Document operational caveats inline** as code comments, especially around regex tips, escape hatches, and cross-platform path handling.

### Red Flags (Stop and Ask)

- The user asks for a feature not in this spec — confirm scope before adding
- A script needs an external library — find a stdlib alternative or escalate
- The reference implementation contradicts this spec — flag the conflict, ask which to follow
- v1.1-specific: the two shipped procedures (`INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`) are missing from the build project — stop and request them; do not invent substitutes.

**v1.3 — Cascade impact (informational; NOT part of amendment scope).** When v1.3 lands:
- Consuming projects with keyword files migrate to `_canon/topics.yaml` (rename + restructure).
- Frontmatter emission at extraction time seeds `topics: []` from keyword-match; #16 augments.
- Codex self-test bootstrap (P54) fixture gains a `_canon/topics.yaml` example.
- Resolves EMCC-side TBDs `<<TBD-codex-tf-idf-pipeline>>` (taxonomy-audit §3 #12) + `<<TBD-codex-tag-namespace>>` (#13).

---

## 9. Asset Registry (v1.4)

Codex wikis document more than prose: the portfolio's binary assets (UGC images, professional
photos, brand assets/logos, credentials/certificates/badges, video/audio, and module
deliverables) are tracked in a per-wiki **asset registry** operated by the Librarian. The
registry is a **ledger, not a page collection** — an append-mostly record of identity, location,
lineage, and rights. The record-vs-page distinction is load-bearing and the name is
Operator-locked: this is the *asset registry* (records), never the "asset codex" (the Codex
protocol makes pages). The Librarian is the registry's **sole writer**.

Provenance: proposal v1.1 (`0-Inbox/2026-07-21-librarian-marketing-extension-proposal.md`),
Library gate `tasks/council/2026-07-21-asset-registrar-gate.md` (council PROCEED-WITH-CHANGES),
role ratified Operator 2026-07-21 (Herald OP-4, portfolio scope, eddyandwolff pilot corpus).

### 9.1 Asset records (the store class)

One markdown record per asset, frontmatter-first (parsed by the shared `_lib/frontmatter.py`),
living in the **same zone as the asset** (§9.4): `wiki.<name>/git/_registry/<AST-ID>.md` for
git-zone assets, `wiki.<name>/local/_registry/<AST-ID>.md` for local-zone assets. Each zone
carries its own index (`_registry/asset-index.md`), regenerated by the registry scripts.

Record schema (per asset):

```yaml
id: AST-<PROJECT>-#####        # stable, opaque; §9.2. Identity NEVER rides on filenames.
asset_class: ugc | professional-photo | brand | credential | deliverable | ...
                               # config-extensible vocabulary (_config/asset_registry.yaml);
                               # validated against config, never enum-locked in code.
name: ""                       # short human name (post-normalization)
description: ""
tags: []                       # controlled vocab (topics.yaml discipline applies)
subject: ""                    # dish / location / person-role / episode ref ...
zone: git | local              # MUST match the record's own on-disk zone (§9.4 validator)
path: ""                       # repo-relative path to the asset file
source: {by: "", date: ""}     # who shot/submitted/generated it, when
rights_consent: ""             # REQUIRED field. Explicit value always present; "unknown" is
                               # legal but explicit (UGC reuse constraints live here).
derived_from: []               # REQUIRED field. [] means VERIFIED ROOT ASSET (explicitly
                               # empty), never "not yet filled". Lineage cannot be retrofitted.
recipe: {}                     # structured generation/derivation data (tool, prompt/job ref,
                               # params) — structured, not freetext, where a generator is known
version: 1
supersedes: ""                 # prior AST-ID on regeneration ("new version" answer, §9.3)
url: pending                   # deliverables only: public URL after remote-store mint (§9.7);
                               # `pending` is a VALID committed state
created_at: ""
updated_at: ""
```

`rights_consent`, `derived_from`, and `recipe` are **mandatory-or-explicitly-empty**: a record
missing any of the three is malformed (flagged, not written). Explicit-empty forms: `""` /
`unknown` for `rights_consent`, `[]` for `derived_from` (verified root asset), `{}` for
`recipe` (no known generation/derivation data). All other consumers of the vocabulary
(future game-dev classes for Anvil: sprites / audio / identities / frame-sets) arrive by
config addition only — zero speculative fields ship in v1.4.

### 9.2 ID allocation (collision-safe, crash-safe)

- **Format:** `AST-<PROJECT>-#####` — `<PROJECT>` is the wiki's project slug, uppercased. The
  per-repo namespace makes IDs portfolio-unique without any global allocator.
- **Allocator:** one counter per repo at `wiki.<name>/git/_registry/_counter` (a committed
  high-water integer; both zones draw from it — the counter itself carries no asset data).
- **Assign-then-commit ordering:** the counter is incremented and persisted BEFORE the record
  is written. A crash between counter-write and record-write **burns** an ID (a permanent,
  harmless gap); it can never duplicate one. IDs are never reused and never re-derived.
- **Concurrency:** the Librarian is the sole allocator in a repo. Concurrent sessions
  serialize on an `O_EXCL` lockfile (`_registry/_counter.lock`); a stale lock (>15 min) is
  surfaced to the operator — never silently broken.

### 9.3 The filing loop (crash-safe ordering; the registry write is the ONLY commit point)

```
1. assign ID                      (§9.2 — counter persisted first)
2. resolve intra-batch lineage    (derived_from refs between batch entries)
3. normalize-rename               (readable filename; identity stays on the ID)
4. ONE move to the final home     (role-determined; never across zones)
   [pre-commit validator: §9.4 zone check — a failing entry is flagged + skipped]
5. REGISTRY WRITE  = COMMIT POINT (deliverables commit with url: pending)
6. wiki index update
7. remote-store upload + URL mint (deliverables only; POST-commit; skippable-with-flag —
                                   failure/absence leaves a valid record at url: pending)
8. inbox cleared LAST
```

Malformed entries stay flagged in the inbox and never choke the batch. On regeneration of an
existing asset the Librarian asks the ONE human question: **"new version or new asset?"**
(new version → `version`+1 + `supersedes`). Steps 6–8 are post-commit bookkeeping: a crash
there leaves a committed record and recoverable state; §9.6 sweeps catch the drift. The spec
makes **no atomicity claim** for any multi-file update.

### 9.4 Zone-following privacy (a validator, not prose)

Metadata follows the asset's zone: `local/` assets (gitignored — e.g. UGC with PII/consent
constraints) get `local/` records; only public-safe assets get `git/` records. Git-zone
indexes may reference local content ONLY as count/pointer rows ("N UGC images — see local
index"), never item-level metadata. **Enforcement is mechanical:** the registry scripts run a
zone check **pre-commit-point** on every entry — a record whose `zone: local` would be written
under `git/` (or whose `zone` mismatches its asset's actual zone) FAILS that entry. Files
never change zones during registration, and no `wiki.*/local/` gitignore rule is ever
weakened. (A post-commit check would already be a leak; hence pre-commit.)

### 9.5 Retro-ingestion mode

Registers assets **already in place** (the pilot shape: a large pre-existing `local/` corpus)
— same loop as §9.3 minus the move, plus:

- **Required pre-flight:** a snapshot manifest (paths + sizes + content hashes; plus a backup
  copy where disk allows) of the target corpus BEFORE the first batch. Gitignored zones have
  no VCS safety net; the snapshot is the rollback.
- Renames of referenced files update referrers best-effort; where a referrer can't be safely
  rewritten the rename is **skipped-with-flag**. Drift lands in the §9.6 sweep, by design.

### 9.6 Reconciliation sweeps + scheduled ingestion (shape only; sequenced after the pilot)

A periodic `Reconcile-Assets` sweep joins the dashboard family: **orphans** (file without
record), **ghosts** (record without file), **doubles** (two records, one content-hash),
**pending mints** (`url: pending` beyond threshold), **stale downstream** (lineage children
older than a regenerated parent). Scope spans disk + remote store + registry. The generalized
scheduled inbox-ingestion service (the long-standing P2-2 seam: watch `0-Inbox/` + subfolders,
protocol-selected by subfolder, unmatched → flag, never silent) is a registry consumer with
the same sequencing. Both are **specified here for shape** and implemented only after the
pilot proves the record store.

### 9.7 Remote store (the carve-out seam)

Deliverable-class assets publish through a **`remote_store`** seam (first backend: Cloudflare
R2; the interface is backend-generic — any S3-compatible store). Two hard placements, both
per the v1.4 gate:

- **Outside the stdlib contract** — a project-local carve-out plug-in exactly per the §2
  R_ARCH pattern: opt-in `_config/` wiring, dynamically resolved, failure-isolated
  log-and-degrade. Codex core still imports zero non-stdlib packages.
- **Outside the commit path** (§9.3 step 7) — nothing gates on the upload, which is what
  makes log-and-degrade honest rather than a stuck batch.

The Librarian is the sole remote-store writer; the public URL is minted from the final remote
path and never changes after mint. Transport (stdlib `urllib` + hand-rolled SigV4 vs an SDK
inside the plug-in) is decided at the implementing build gate once credentials exist (Herald
OP-5); hand-rolled SigV4 is acceptable only for simple single-PUT scope.

### 9.8 Scope and non-goals

v1.4 is **purely additive**: no existing section, operation, template, or verbatim procedure
changes. Nothing in this section is implemented by the spec itself — implementation lands
under the consuming project's build gates (Lattice 3.0 / EMCC framework-22) with tests, first
consumer = the Herald marketing pipeline, pilot corpus = eddyandwolff. Anvil/game-dev classes
activate only on the Operator's trigger, as vocabulary additions.

### 9.9 Visual-evidence sidecar (generated visual assets — v0.1)

Generated visual assets (Grok Imagine sprites / base-identities / pose-anim frames / audio
cues — the Anvil/game-dev classes activated per §9.8) carry a provenance **sidecar** beside the
asset: `<asset>.visual-evidence.json`. The sidecar is the portfolio's single **visual-evidence
standard** — ONE artifact consumed by BOTH the game-build mechanical floor
(`pnpm anvil test --strict-assets`) AND this §9 registry ingest. Provenance: LLM Council SHIP
v0.1 (`EMCC/tasks/council/2026-07-24-visual-evidence-standard.md`).

**Canonical schema (single source of truth):**
`wiki.codex/git/codex/schemas/visual-evidence.schema.json` (JSON-Schema draft-07, stdlib-safe
subset). Codex §9 **owns** it; iron-soul-anvil (and any future consumer) **vendors** it
SHA-pinned via Sync and codes its checks against the vendored copy — never a divergent second
definition.

**Two-leg discipline (honest by construction — never "certified" for visuals):** a *mechanical
PASS* (what bytes can prove) + a *named human ACCEPTED* (a record, not a cert).
- `cert_class` is **NOT a sidecar field** — a settable sidecar `cert_class` would let a
  generator self-declare a pass before any gate runs. It is set POST-facto on the **cert-handoff
  only**, locked data-side enum `{mechanical-pass-human-aesthetic, mechanical-fail}`;
  `certified` is BANNED for visuals.
- Two rules both validators hard-code in CODE (not expressible in the stdlib-safe schema
  subset): **R1** `base_asset_ref` XOR fresh-gen (string form == `"fresh-gen"`; object form
  MUST carry `path`+`sha256`; unflagged AND no base = FAIL); **R2** `aesthetic_signoff.name`
  MUST be non-empty (no name = no pass).

**§9-record mapping (sidecar → §9.1 record):** `asset_path`→`path`; provenance scalars
(`prompt`/`seed`/`model_id`/`generator`/`generated_at`)→`recipe:` 1:1; `style_bible_ref`
`{path, commit_sha}` object→flattened to `recipe:` scalars `style_bible_path` +
`style_bible_commit_sha` (recipe values must be scalars — a nested object is 3-level, refused
by `parse_config_yaml`); `base_asset_ref`→`derived_from` (fresh-gen→`[]`; object→resolve
`ast_id`, backfilled on base-identity registration). `style_tokens_declared` (palette LIST) and
`aesthetic_signoff` (nested) are **sidecar-only** — the record points at the sidecar by
`visual_evidence_ref: {path, sha256}`.

**Record-side additions + validator land in B4** (this subsection lands the canonical schema
artifact only — B2). B4: add `sha256` (asset content-hash) + `visual_evidence_ref` to the §9.1
record; ship `validate_visual_evidence.py` (stdlib walker over the schema + checks 1–6 + R1/R2;
check-6 legal/likeness screen is Anvil-side mechanical + human-attested per the v0.1 disposition
— the registry records the attestation, no registry-side legal validator in v0.1). Game asset
classes (`sprite`/`base-identity`/`pose-anim-frame`/`audio-cue`) are added to
`_config/asset_registry.yaml` per §9.8 (Operator-triggered vocabulary addition) in B3.

---


## Appendix A — Reference Implementation Details

The Iron Soul / Planet Scoria Prime wiki is the working reference. Key facts:

- **Version:** v3.3 (Iron Soul wiki built from Codex v1.3 conceptually)
- **Pages:** 31 internal + 10 public + 8 auto-generated dashboards
- **Validators:** 0 errors, 0 warnings on the canonical state
- **Canon coverage:** 4 YAML files with 60+ facts
- **Confidential profile:** 11 sections including Claude behavior rules

Iron Soul demonstrates every pattern Codex needs to support:
- Internal frameworks with public briefing-guide pairs
- A confidentiality conceit (Arc 8 reveal) preserved through validation
- Brain dump quarantine pattern (one example entry)
- Canon consistency across many cross-cutting facts
- Custom config (`reveal_leak_patterns.yaml` uses `severity: info` to document approved-public terms)

When in doubt about how Codex should behave, look at how Iron Soul behaves. **Exception:** Iron Soul pre-dates the Ingest operation and the `_sources/raw/` archive; use this spec's v1.1 text and the shipped procedure files for those.

---

## Appendix B — Quickstart Reference (after Codex is built)

For consuming projects after Codex v1.0 is in production. (Not for building Codex itself.)

```bash
# Bootstrap a new wiki
cd <Codex install path>
python bootstrap.py <new-wiki-path>

# Customize the new wiki:
#   1. Rename 01-Domain-1/, 02-Domain-2/ to project domains
#   2. Populate _config/*.yaml with project rules
#   3. Populate _canon/*.yaml with project facts
#   4. Customize _confidential/Confidential_Profile.md
#   5. Customize _context/CLAUDE_CONTEXT_RULES.md
#   6. Customize Home.md and 00-Start-Here/ pages

# Run dashboards
cd <new-wiki-path>
python _scripts/update_dashboards.py

# Ingest a new source (v1.1, ongoing)
python _scripts/scaffold_source.py <path-to-source-or-URL>
#   Then in Claude Code: "Ingest _inbox/<source>.md"

# Semantic lint (v1.1, periodic)
#   In Claude Code: "Run semantic lint" — writes to _dashboards/semantic_lint_report.md

# Sync with updated Codex (later, when Codex improves)
cd <wiki-path>
python _scripts/sync_from_kit.py <Codex install path> --dry-run
python _scripts/sync_from_kit.py <Codex install path>
python _scripts/update_dashboards.py
```

---

*— END OF CODEX BUILD SPECIFICATION —*

*Codex Build Spec v1.4 — July 2026 (v1.3 — April 2026)*
*Reference implementation: Iron Soul / Planet Scoria Prime wiki v3.3*
*v1.1 additions: Ingest operation (§4.3), `_sources/raw/` archive, concept-coverage validator, scaffold_source.py, shipped `_context/` procedures*
