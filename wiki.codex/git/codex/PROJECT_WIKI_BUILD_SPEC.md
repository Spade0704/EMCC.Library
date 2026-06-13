# Codex — Build Specification

> **If you are Claude Code and this document is in a project:** your job is to build the **Codex** tool. Codex is a portable, local-first, scaffolding-and-sync tool that creates and maintains documentation wikis for other projects. Read this entire document, then ask the user the Phase 1 questions in Section 7 before writing any code.

**Project name:** Codex
**Project type:** Developer tool (CLI + library, no GUI)
**Language:** Python 3.8+ (pure standard library, zero external dependencies)
**Audience:** A solo developer (and Claude Code) managing multiple projects, each needing structured documentation
**Reference implementation:** the Iron Soul / Planet Scoria Prime wiki, v3.3 — see Appendix A
**Spec version:** v1.3

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

Add to the content-page frontmatter contract three new **optional** fields:

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

### 2.4 The 15 Automation Scripts

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
| 16 | `build_topic_index.py` | Builds topic → pages map from `_canon/topics.yaml` keywords + TF-IDF augmentation. Updates each page's frontmatter `topics: []` additively; mirrors topic-derived `tags:` per config. Writes `_dashboards/topic_index.md`. |
| 17 | `cross_link_topics.py` | For each multi-page topic, writes `related_files: []` in frontmatter AND a marker-bracketed "See also" block in body. Idempotent. Reads index from #16. |
| 18 | `validate_topic_registry.py` | Every page `topics:` value resolves in `_canon/topics.yaml` (error). Every registry topic has ≥1 member page (warning; orphan-topic detection). |

**Orchestrator update (#1).** `update_dashboards.py` runs #16 → #17 → #18 after the existing aggregator/validator pass, **before** health-summary synthesis. Pipeline order matters: #17 needs #16's index; #18 validates the post-#17 state. Health summary gains a `cross_link_coverage` signal (pages with ≥1 entry in `related_files`). **Failure isolation:** #16/#17/#18 failure produces a stderr warning + non-zero exit but does NOT block the existing aggregator/validator runs or other dashboard regeneration.

> **Numbering note (reconciled).** Spec-table `#16/#17/#18` are the scripts' rows in this §2.4 table. Their build-plan phases are **P18.2 / P18.3 / P18.4** respectively (with foundation lib `_lib/topics.py` at **P18.1**). Build-plan `P16` is the already-shipped `delta_source_docs.py` (S037) — a different axis. See §7.
| + | `scaffold_<type>.py` | Project-specific scaffolds (added per project) |

### 2.5 Configuration Files

**`_config/`** (behavior tuning, per-project):

- **`forbidden_terms.yaml`** — regex rules for trademark/naming violations, context-aware (`all` / `audience` / `internal`)
- **`reveal_leak_patterns.yaml`** — phrases that leak unreleased content. Severities: `error` / `warning` / `info` (info documents approved terms without flagging)
- **`cascade_map.yaml`** — source → derived doc propagation
- **`steel_threads.yaml`** — multi-layer feature manifest
- **`concept_coverage.yaml`** (v1.1, optional) — tunes `check_concept_coverage.py`. Keys: `min_mentions` (default 2), `exclude_folders` (list of folder names skipped during scanning), `exclude_entities` (list of canonical names skipped — escape hatch)

> **Regex convention (amended 2026-06-10, M-A component 1).** The `_config/` files are read by Codex's YAML-subset parser, which performs **no escape processing**: quoted strings are delivered verbatim to `re.compile`. Regex values MUST be written **single-backslash** (`"(?i)\bterm\b"`), never real-YAML double-backslash (`"\\b"` is delivered as a literal backslash pair — a rule that compiles but never fires). The parser must NOT gain escape processing: it would reinterpret `\b` as backspace and silently break every live single-backslash rule in consuming wikis. Shipped examples follow this convention and are guarded by negative-control tests in the Library suite.

> **Materialize-then-link (amended 2026-06-11, M-A component 5 / CARTO-06).** "Every advertised hop resolves; the generator owns consistency" (C2 council convention lock). Bootstrap materializes the six ToC-advertised boilerplate pages (`00-Start-Here/{How-to-Use-This-Wiki,Glossary,Terminology-Rules}.md` + `04-Contributing/{Update-Cascade,File-Routing,Style-Guide}.md`) from templates into `wiki.<name>/git/` at scaffold time, so a new wiki is never born with dead Home links. Existing wikis use the kit's `materialize_boilerplate.py` standalone (idempotent: existing pages are always SKIPPED — once materialized, a page is consumer content).

> **Boilerplate location (amended 2026-06-11, Operator-RATIFIED; resolves the previously-pending per-repo-vs-once-upstream question — proposal: EMCC.Library `tasks/plans/boilerplate-location-spec-proposal.md`).** The six pages split by content class: the four PROTOCOL pages — `How-to-Use-This-Wiki`, `Style-Guide`, `Update-Cascade`, `File-Routing` — live ONCE in the canonical Codex wiki (`wiki.codex/git/00-Start-Here/` + `04-Contributing/` in EMCC.Library); consumer wikis carry generated STUBS (frontmatter + one-paragraph summary + canonical pointer; Option A — static stubs, materialized at bootstrap like any page, consumer content thereafter; no sync-contract change). The two PROJECT pages — `Glossary`, `Terminology-Rules` — stay per-repo full pages. Pre-convention wikis migrate via the kit's `demote_boilerplate_stubs.py` (one-off; a page is demoted IFF its body equals ANY previously shipped version of the template with the project name substituted — anything else is consumer content, skipped and reported).

**`_canon/`** (ground-truth facts, per-project):

- **`counts.yaml`** — every canonical number that appears more than once
- **`roster.yaml`** — named entities with canonical names and aliases
- **`taxonomy.yaml`** — structured classifications
- **`timeline.yaml`** — milestones, versions, progression parameters

The consistency checker reads `_canon/` as ground truth. Pages contradicting it are flagged. Pages contradicting *each other* (when `_canon/` doesn't arbitrate) are also flagged in a separate section.

### `_canon/topics.yaml`

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

> Template instance ships **domain-neutral** (1–2 placeholder topics + commented examples + structurally-valid empty default). Consuming projects populate domain content themselves.

### `_config/cross_link.yaml` (optional)

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

### 2.7 Cross-link Generation Contract

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
- Wikilink format: `[[FileStem]]` (precedent: lessons.md "wikilinks use filename stem, not page path or frontmatter title").

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

> **! R_ARCH carve-out (stdlib-only contract).** Project-local plug-ins are **out-of-scope** for Codex's stdlib-only contract — they are consuming-project artifacts, dynamically imported via opt-in config (`_config/cross_link.yaml` `plugin.module_path`), failure-isolated to log-and-degrade. Codex itself imports **zero** non-stdlib packages; plug-ins may import anything in their own environment. This is **distinct from** a Codex-*bundled* plug-in architecture (rejected). (Mirrored canonically in `CLAUDE.md` R_ARCH › D_RULES.)

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
13. **Cross-link injection is marker-bracketed and idempotent.** Frontmatter `related_files: []` is the source of truth; the body "See also" block is its rendered view. Content between `<!-- codex:see-also:start -->` and `<!-- codex:see-also:end -->` is regenerated every run; human prose around the markers is preserved. Humans curate `topics: []` to influence what gets linked; they do not hand-edit the rendered block. Frontmatter `tags: []` is human-owned but optionally mirror-augmented from `topics:` per `_config/cross_link.yaml`. Codex never removes entries from `tags:` — additive only.
14. **Build sessions keep the wiki current.** A consuming project's wiki is derived documentation maintained **every build session**, not a one-time artifact. A coding session that changes a project (code, schema, config, APIs, behavior) is not done until that project's wiki reflects it: update the affected pages, run the cascade, bump `last_updated`, and log the session. This per-session contract is encoded in the bootstrapped `_context/CLAUDE_CONTEXT_RULES.md` ("Wiki Maintenance Behavior") and `04-Contributing/Update-Cascade.md` ("Per build session").

---

## 4. The Three Operations Codex Performs

### 4.1 Bootstrap (one-time per project)

```bash
cd <wherever Codex is installed>
python bootstrap.py <target-wiki-path>
```

Creates the full wiki folder structure at `<target-wiki-path>`, copies all 15 scripts, drops in commented config templates, populates starter meta-pages (Home, Glossary, Terminology-Rules, How-to-Use-This-Wiki, Style-Guide, Update-Cascade, File-Routing, Confidential Profile skeleton, CLAUDE_CONTEXT_RULES, INGEST_PROCEDURE, SEMANTIC_LINT_PROCEDURE, canon/brain_dump/decisions/sources READMEs).

After bootstrap, the consuming project does Phases 3–7 of Section 7 to populate content.

### 4.2 Sync (ongoing, when Codex itself improves)

```bash
cd <wiki path>
python _scripts/sync_from_kit.py <path-to-Codex-installation>
```

Pulls updated infrastructure from Codex into the consuming wiki:

- **Overwritten:** `_scripts/` (the 15 automation scripts)
- **Overwritten:** `04-Contributing/PROJECT_WIKI_BUILD_SPEC.md`
- **Overwritten:** `_context/INGEST_PROCEDURE.md` and `_context/SEMANTIC_LINT_PROCEDURE.md` (shipped procedures — not customized per project)
- **Merge-new-only:** `_config/` and `_template/` files (existing customized files are preserved; new template files are added)
- **NEVER touched:** content folders (`00-Start-Here/`, `01-*/`, `_canon/`, `_sources/raw/`, `_confidential/`, `_decisions/`, `_brain_dump/`, `_dashboards/`, `_inbox/`, `public/`, `Home.md`, `README.md`), `_context/CLAUDE_CONTEXT_RULES.md` (customized per project)

Sync refuses to run if the wiki has uncommitted git changes (override with `--force`). Sync supports `--dry-run` to preview changes.

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
3. **Codex version to start at?** (Default: v1.0. The CHANGELOG's first line drives version detection. The spec itself is v1.2, but the built tool starts at v1.0 unless the user specifies otherwise.)
4. **Should bootstrap also git-init the new wiki?** (Recommended: yes, with an initial commit.)
5. **Any project-specific constraints I need to know?** (Operating system, Python version available, network restrictions.)

### Phase 2 — Scaffold Codex

Create the directory structure from Section 5. Empty folders are fine at this stage.

### Phase 3 — Build the scripts

For each of the 15 scripts, implement against the contract in Section 2.4 and the principles in Section 3. Reference implementation is in the Iron Soul wiki at the matching filename; the two v1.1-new scripts (`check_concept_coverage.py`, `scaffold_source.py`) have no Iron Soul precedent and must be implemented from spec.

Critical implementation details:

- **No external dependencies.** Pure Python stdlib only. Do not use PyYAML — implement a tiny YAML-subset parser that handles the formats this spec uses (see `_lib/frontmatter.py` in the reference implementation).
- **Path math:** `WIKI_ROOT = Path(__file__).resolve().parent.parent.parent` from inside `_lib/frontmatter.py` (because `_lib` is one level deep inside `_scripts`).
- **Code-block stripping:** Validators that scan markdown content must strip fenced code blocks and inline code before pattern-matching, otherwise example syntax in documentation gets flagged.
- **Frontmatter list fields:** `dependencies`, `blocking_questions`, `canon_sources`, `unverified_claims`, `migrated_to` are all parsed as YAML-subset lists.
- **`check_concept_coverage.py` (v1.1):** reads `_canon/roster.yaml`, counts mentions of each canonical name (and aliases) across all content pages, and reports entities with ≥ N mentions (default N=2) that lack a dedicated page file. Matching is **word-boundary** (`\b...\b`), **case-sensitive**, with **aliases counted alongside the canonical name** (i.e. for each entity, build a regex from `[canonical_name] + aliases` and scan). Each page is counted **at most once per entity** — the threshold tracks page coverage, not mention frequency. Frontmatter and fenced code blocks are stripped before matching. Output is written to `_dashboards/concept_coverage.md`. Threshold and folder scope are configurable via `_config/concept_coverage.yaml` (new, optional). The signal for "dedicated page" is intentionally deferred — to be pinned down when the first consuming wiki runs the validator; the current placeholder is a filename match against the slugified canonical name.
- **`scaffold_source.py` (v1.1):** accepts a local file path or URL. For local files, copies into `_inbox/<basename>.md`. For URLs, the script does NOT fetch — it creates a placeholder `_inbox/<slug>.md` with frontmatter and instructs the user to paste the source content (keeps Codex fully offline and dependency-free).

**Cross-link build phases.** Insert four new phases in the **end of the pre-orchestrator T2 band** (after the scaffold scripts P17/P18, before P19 orchestrator), preserving dependency order: lib → index → linker → validator.

| Phase | Script | Spec # | Notes |
|---|---|---|---|
| **P18.1** | `_lib/topics.py` — topic registry parser | (lib; not in spec table) | Extends `parse_config_yaml` precedent. Validates `_canon/topics.yaml` schema; returns typed Topic objects + alias-resolution lookup. Mirrors `_lib/frontmatter.py` foundation pattern. Sets precedent for the 3 following. |
| **P18.2** | `build_topic_index.py` | #16 | TF-IDF pure stdlib (`math`, `collections.Counter`, `re`). Plug-in import gated behind `_config/cross_link.yaml` presence. Updates frontmatter `topics:` + `tags:` additively (never removes human entries). Dashboard `_dashboards/topic_index.md`. |
| **P18.3** | `cross_link_topics.py` | #17 | Marker-block writer. Idempotent test mandatory. Updates frontmatter `related_files:` and body block atomically (both succeed or both rolled back). |
| **P18.4** | `validate_topic_registry.py` | #18 | (a) every page `topics:` value resolves (error); (b) every registry topic has ≥1 member page (warning). |

P19 (`update_dashboards.py`) keeps its number; its orchestrator contract is amended to run #16 → #17 → #18 between validators and health-summary synthesis (see §2.4 orchestrator note).

**Test fixture additions:** `tests/fixtures/sample_wiki/_canon/topics.yaml` with 2–3 topics covering same-folder and cross-folder linking; updated page frontmatter `topics:`; expected `related_files:` post-link state; tag-mirroring cases (flat / nested / disabled / human-entry-preserved).

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

**Cross-link cascade impact (informational; NOT part of normative spec).** When the cross-link generation feature lands:
- Consuming projects with keyword files migrate to `_canon/topics.yaml` (rename + restructure).
- Frontmatter emission at extraction time seeds `topics: []` from keyword-match; #16 augments.
- Codex self-test bootstrap fixture gains a `_canon/topics.yaml` example.

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

## Accuracy contract — verbatim-only / cite-always / correct-refusal (v1.3)

Codex content must never fabricate. The accuracy posture is three rules:

1. **Verbatim-only** — quote source material exactly; never paraphrase a load-bearing fact into a new claim.
2. **Cite-always** — a HIGH-`consequence` page carries a non-empty `cite_anchor` pointing at its verbatim source.
3. **Correct-refusal** — when a fact is not in the corpus, refuse or escalate rather than invent.

The enforceable slice is the `consequence`/`cite_anchor` frontmatter contract (see [[Frontmatter-Schema]] §"Accuracy fields — consequence / cite_anchor"): fail-safe HIGH; a HIGH page requires a non-empty `cite_anchor`. Checked by `_scripts/_lib/doc_lint.py::check_consequence` and surfaced by the report-only `_scripts/audit_citations.py` audit. **Presence-Not-Accuracy:** the lint proves a citation is *present*, not that it is verbatim or correct — a floor, not a guarantee.

---

*— END OF CODEX BUILD SPECIFICATION —*

*Codex Build Spec v1.2 — April 2026*
*Reference implementation: Iron Soul / Planet Scoria Prime wiki v3.3*
*v1.1 additions: Ingest operation (§4.3), `_sources/raw/` archive, concept-coverage validator, scaffold_source.py, shipped `_context/` procedures*
