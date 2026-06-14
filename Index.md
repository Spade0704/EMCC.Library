# Index — EMCC.Library

> The single repo **MAP + routing header** for `EMCC.Library` (the Codex **home** — the module that owns the Codex protocol/engine + the Librarian agent). `CLAUDE.md` reads this FIRST. *(Restructured 2026-06-06 into the 3-zone wiki-as-memory form per `EMCC/framework/18-wiki-memory-routing.md`; all prior file-map content preserved below in Zone 2.)*
>
> **Wiki router:** `wiki.codex/git/Home.md` (the topic/semantic router over Codex's self-knowledge). **Protocol canon:** `wiki.codex/git/codex/` (the authoritative Codex spec docs — `CODEX_BUILD_SPEC_v1_3.md` is the single canonical version; **spec wins** any contradiction). **Note:** EMCC.Library is the Codex home, so its wiki dir is **`wiki.codex`** (not `wiki.EMCC.Library`).

## Routing contract (how to get full context at minimum tokens)

- **Topic / domain / task question** -> **Zone 1**: go to the wiki router (`wiki.codex/git/Home.md`), open the ONE relevant page, then **expand one hop** via its `related_files:` + `[[wikilinks]]` for related context. Drill to the cited canon (`wiki.codex/git/codex/`) only when you need authoritative precision / exact spec wording. (Lexical, not vector — `EMCC/framework/13`.)
- **"Where does X live / which operational file" question** -> **Zone 2** (the non-wiki knowledge catalog below — this is the original Library file-map, preserved in full).
- **Private / not-yet-in-repo** -> **Zone 3** (Phase 2 stub).

---

## Zone 1 — Topic / knowledge -> the wiki

Route any topic/domain/task question into the wiki; do not grep blindly.

- **Entry: `wiki.codex/git/Home.md`** — TOC + semantic router over Codex's self-knowledge (architecture, operations, the Librarian agent, build-spec derivations).
- Load the single relevant page, then **follow its `related_files:`/`[[wikilinks]]` one hop** to pull the related cluster (the cross-link graph is the context-expansion engine). Wiki pages are derived overviews that cite their canon via `canon_sources` — the **Codex spec docs live under `wiki.codex/git/codex/`** and are reachable as the canon drill-down (e.g. an Architecture overview cites `CODEX_BUILD_SPEC_v1_3.md`). Drill to `wiki.codex/git/codex/` for exact wording/numbers.
- The wiki's page list lives in `Home.md`; this Index does **not** duplicate it (the router owns it).

> Cross-link note: the verbatim-shipped procedures (`INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`) under `wiki.codex/git/codex/` are **canon, not curation targets** — quote them verbatim; never paraphrase or restructure (CLAUDE.md "Verbatim discipline").

---

## Zone 2 — Non-wiki knowledge (committed)

The knowledge-bearing files that live OUTSIDE the wiki, catalogued by purpose with when-to-load. (Codex spec canon under `wiki.codex/git/codex/` is also reachable as a topic via its wiki overview page; this zone is the drill-down map.) *This is the original Library file-map, preserved in full.*

### Top-level files

| File | Purpose |
|---|---|
| `Index.md` | **This file.** The repo MAP + 3-zone routing header (routes topics to the wiki + maps the non-wiki files). |
| `CLAUDE.md` | Operating rules + memory architecture for sessions working on Library. Read AFTER Index. |
| `README.md` | Public-facing module description; what Library is + how consumers use it. |
| `module.json` | EMCC module registration (v1.1.0). EMCC's consumer-bootstrap auto-detection reads this. |
| `bootstrap.py` | Entry script consumers run: `python bootstrap.py <new-wiki-path> [--minimal \| --code \| --website \| --full]`. Implements spec section (c). |
| `.gitignore` | Excludes `wiki.*/local/`, `.lattice/`, `.DS_Store`, `__pycache__`, etc. |
| `SOURCE-HISTORY.md` | Per-file move inventory from project-codex at SHA `ccf21b7` (Session 1 extraction). |
| `MIGRATION-ISSUES.md` | Append-only registry of migration issues (currently MI-01..MI-17). |
| `REORGANIZATION-INSTRUCTIONS.md` | **Master** manifest (patterns P1–P8 + audit-hook contract + cross-repo index of per-project files). Updated 2026-05-28 per v1.3 addendum: trimmed to master-only; per-project content extracted. |
| `reorganization-instructions.library.md` | **Per-project** manifest for EMCC.Library: Session 1 + S002 + S003b concrete moves. Pairs with the master above. |

### Top-level folders

| Folder | Contains | When to load |
|---|---|---|
| `0-Inbox/` | Files awaiting Librarian sort | Triage; planning a change to canon |
| `Biz.Automation/wikisys.library/` | Codex automation engine (system side per portfolio-spec F6) | All script / config / template work |
| `wiki.codex/` | Library's self-hosted dogfood wiki (Codex documenting Codex) | Reference; self-documentation; spec lookups |
| `tasks/` | Operational state (todo / sessions / lessons / architect-notes / archive / v1.1-backlog) + `tasks/plans/` planning docs | Every session start |
| `tests/` | Python stdlib `unittest` suite (~589 tests) | After any code change; CI workflow runs `python -m unittest discover -s tests -t .` |
| `.claude/` | Claude Code config — `personas/CLAUDE.{librarian,auditor}.md` | Persona / agent work; auto-loaded by Claude Code at session start |
| `.github/` | CI workflow (tests + JSON schema validation) | CI-related changes |

### `Biz.Automation/wikisys.library/` — Codex engine

| Subfolder | What | When to load |
|---|---|---|
| `_scripts/` | 27 Python scripts (foundation `_lib/` + 22 P-indexed + 5 new S002 audit scripts) + `launchers/` PowerShell helpers | Logic / script work |
| `_scripts/_lib/` | Foundation modules: `frontmatter.py` (P1), `config_loader.py`, `dashboard.py`, `doc_lint.py`, `markdown.py`, `topics.py` | Foundation; everything imports from here |
| `_template/` | 26 wiki templates (with `__SEP__` path encoding per Lesson #22 Win32-safety) | Template work; Sync ships these into consumer wikis |
| `_config/` | 5 YAML config files + README + `cross_link.yaml` | Config work |
| `_canon/` | Library's own canon entities (roster / taxonomy / timeline / topics — Codex documenting Codex) | Canon work |
| `_context/` | Runtime context rules | Reference |
| `_decisions/` | Decision history (e.g., `ingest-log.md`) | Reference |

### `wiki.codex/git/codex/` — Codex authoritative spec docs (protocol canon)

These are the spec docs the Librarian agent + consumers reference for Codex semantics. They are the **protocol canon** the Zone 1 wiki overviews drill down into. Moved here in S002 per spec section (b) (the DFDU analogy: `documents/lattice/` → `wiki.dfdu/git/lattice/`).

| File | What |
|---|---|
| `CODEX_BUILD_SPEC_v1_3.md` | Authoritative Codex build specification. Single canonical version. **Spec wins** any contradiction with CLAUDE.md or other docs. |
| `CODEX_LIBRARIAN.md` | Librarian agent specification (S002 v1.1 extension: 3 new ops — Inbox-Sort / Pairing-Audit / Cross-Project-Scan; 5 Mentor pattern codifications; Telegram auto-summary contract) |
| `INGEST_PROCEDURE.md` | Verbatim-shipped procedure for ingesting new sources into wikis |
| `SEMANTIC_LINT_PROCEDURE.md` | Verbatim-shipped lint procedure |
| `PROJECT_WIKI_BUILD_SPEC.md` | Wiki build spec (what `bootstrap.py` materializes for consuming projects). §2.5 carries the single-backslash regex convention for `_config/` rule files (M-A, 2026-06-10: the YAML-subset parser does no escape processing). |
| `SYNC_STAMP_CONTRACT.md` | **SYNC-STAMP contract** (M-A, 2026-06-10; MI-20) — schema of the `SYNC-STAMP.json` version stamp `sync_from_kit.py` writes as its dedicated final action (`{kit_commit, synced_at, manifest}`; the stamp IS the kit manifest), the three-state drift vocabulary (STALE / MODIFIED / PERSONA-DRIFT — co-occurring, never blended) consumed by report-only `EMCC/scripts/check_drift.py`, the lifecycle (all-OK only; never on `--dry-run`; dirty-kit WARN), and the locked fences. |
| `Obsidian-Setup-Guide.md` | Consumer guidance for Obsidian users |
| `codex-build-plan.html` | Original Codex build plan (P1–P54 priorities) |
| `Codex_Project_Documentation.pdf` + `Codex_Workflow_Cheatsheet_v1.txt` + `codex-build-progress.md` | Background / historical Codex materials |

### `_scripts/` — automation (P-indexed per `CODEX_BUILD_SPEC_v1_3.md` §2.4)

| Priority | Script | What |
|---|---|---|
| P1 | `_lib/frontmatter.py` | YAML-subset parser + frontmatter loader. Foundation. |
| P4 | `collect_open_questions.py` | Roll up `blocking_questions` into `_dashboards/` |
| P5 | `build_completion_dashboard.py` | red/yellow/green completion roll-up |
| P6 | `validate_terminology.py` | Forbidden-terms scan |
| P7 | `validate_canon_integrity.py` | `status=ready` → `canon_sources` non-empty, `unverified_claims` empty |
| P8 | `validate_reveal_conceit.py` | Public-page leak scan |
| P9 | `check_cross_refs.py` | Broken `[[wikilinks]]` + orphan pages |
| P10 | `check_cascade.py` | Source vs derived-doc mtime comparison |
| P11 | `check_framework_briefing_sync.py` | Framework ↔ public_pair mtime check |
| P12 | `check_canon_consistency.py` | Page-vs-canon consistency |
| P13 | `check_concept_coverage.py` | `roster.yaml` entities mentioned in N+ pages |
| P14 | `steel_thread_tracker.py` | Multi-layer feature manifest |
| P15 | `build_canon_drift_report.py` | Snapshot + diff of `_canon/` over time |
| P16 | `delta_source_docs.py` | Diff two source-doc versions + cascade impact |
| P17 | `scaffold_brain_dump.py` | Create `_brain_dump/` entry |
| P18 | `scaffold_source.py` | Create `_inbox/` entry for ingest |
| P19 | `update_dashboards.py` | Orchestrator; runs all aggs + vals |
| P20 | `sync_from_kit.py` | Pull updated infrastructure from Codex into a consuming wiki (MI-16: still at v1.0 contract; canonical-shape migration deferred to S004) |
| — | `summarize.py` | Canonical Librarian `summarize(source, audience)` op (CODEX_LIBRARIAN v1.2) — stdlib extractive default + injectable LLM `summarize_fn` seam |
| — | `build_topic_index.py` | Topic index builder (v1.1 addition) |
| — | `cross_link_topics.py` | Topic cross-link generator |
| — | `validate_topic_registry.py` | Topic registry validator |
| **S002** | `audit_doc_pairing.py` | Audit `Biz.Automation/<name>/` paired with `wiki.<name>/git/<name>.doc/` |
| **S002** | `audit_gitignore.py` | Verify `wiki.*/local/` + heavy-asset patterns excluded |
| **S002** | `route_inbox.py` | Two-phase: scan `0-Inbox/` → emit manifest → Librarian fills destinations → execute moves |
| **S002** | `audit_assets.py` | Heavy-file scan + duplicate detection |
| **S002** | `audit_local_split.py` | Misclassification suspects in `local/` vs `git/` |

### `tasks/` — operational state

| File | What | When to read |
|---|---|---|
| `tasks/todo.md` | Current sprint + In Progress + Immediate + This Week + Backlog | Every session start |
| `tasks/sessions.md` | Dated session log (newest at top); S001 (extraction) + S002 (v1.1 restructure) closed | Most recent entry at session start |
| `tasks/lessons.md` | Architectural lessons. **Auditor NO READ** per `EMCC.DFDU/documents/lattice/02-PRINCIPLES-AND-WORKFLOW.md` §B independence rule | Before any code change |
| `tasks/architect-notes.md` | Open threads, deferred decisions, plans §S001 + §S002 | Architect work |
| `tasks/archive.md` | Historical sprints rolled out of `todo.md` | Reference |
| `tasks/v1.1-backlog.md` | Codex v1.1 enhancement queue (mostly shipped in S002) | Reference for what's done vs deferred |
| `tasks/plans/portfolio-folder-structure-spec.md` | Multi-session planning spec for the v1.1 layout (1,500+ lines; signed off + 4 amendments applied) | Architect reference for canonical structure |

### `wiki.codex/` content layout (post-S002)

| Path | What |
|---|---|
| `wiki.codex/git/` | Public content side (per portfolio spec F10) |
| `wiki.codex/git/Home.md` | Wiki home / front page (**the Zone 1 router**) |
| `wiki.codex/git/00-Start-Here/` | Onboarding pages |
| `wiki.codex/git/01-Architecture/` | Architecture docs |
| `wiki.codex/git/02-Operations/` | Operations docs |
| `wiki.codex/git/04-Contributing/` | Contributing guide |
| `wiki.codex/git/codex/` | Codex authoritative spec docs (see table above — protocol canon) |
| `wiki.codex/git/raw/` | Source archive (formerly `_sources/raw/`) |
| `wiki.codex/local/` | Private content side (gitignored; never committed) — see Zone 3 |
| `wiki.codex/local/ideas/` | Brain-dump / unfiled notes (formerly `_brain_dump/`) — see Zone 3 |

### Cross-module references

| Module | Relationship | Where to read |
|---|---|---|
| `EMCC.DFDU` | Library consumes DFDU's Lattice 3.0 protocol for Library's own session work | `EMCC.DFDU/documents/lattice/00-README.md` (ToC) |
| `EMCC` | EMCC's consumer-project template references Library via `templates/consumer-project/emcc.modules.json`; status = `ready` (flipped Session 1). Wiki-as-memory routing standard canon: `EMCC/framework/18-wiki-memory-routing.md` | `EMCC/templates/consumer-project/CLAUDE.md` (consumer-side wiring) |
| `spade0704/project-codex` | Source of Session 1 extraction (now archived) | `SOURCE-HISTORY.md` for SHA + per-file move inventory |
| `spade0704/Mentor` | First dogfood wiki bootstrapped via Codex (wiki #2, 2026-05-25); findings folded into S002 | `tasks/architect-notes.md` §S002 + `tasks/plans/portfolio-folder-structure-spec.md` §"Mentor — Greenfield bootstrap (shipped 2026-05-25)" |

### Inventory-seed (non-wiki, committed)

From `python EMCC/scripts/inventory_repo.py /home/user/EMCC.Library` (2026-06-06; 195 non-wiki-git files, 37 wiki-git-content, 3 wiki-git-infra, 0 wiki-local). The folder tables above are the curated catalog; these are the inventory-classified roots for cross-check:

| Path | Files | When to load |
|---|---|---|
| `.claude/` | 3 | Personas / modules / skills / commands (agent config). |
| `CLAUDE.md` | 1 | Operating brain — read first every session. |
| `Index.md` | 1 | This file — the repo MAP + routing header. |
| `README.md` | 1 | Repo overview. |
| `module.json` | 1 | Module runtime manifest. |
| `tasks/` | 10 | Operational state (Boris: todo/sessions/lessons/...). Read at session start. |

### Maintenance discipline

- **When you add a non-wiki file under any folder above, update its Zone 2 row.** Keep the MAP authoritative. **When you add WIKI content, update `wiki.codex/git/Home.md`** (not this Index) — Zone 1 delegates the wiki page list to the router.
- **When a new MI lands in `MIGRATION-ISSUES.md`, update the file's purpose row above** (just bump the MI count range).
- **When a new tasks/* file is added (e.g., a new planning doc), add a row** under the "tasks/" table.
- This file is the operator's first stop for "where is X?"; let it rot and the value drops sharply.

---

## Zone 3 — Private / uncommitted (Phase 2)

Placeholder per `EMCC/framework/18-wiki-memory-routing.md` Phase 2. Will catalog the knowledge that is NOT in the committed repo:

- `wiki.codex/local/` (gitignored; never committed) — Library's private zone, including `wiki.codex/local/ideas/` (brain-dump / unfiled notes, formerly `_brain_dump/`). Currently 0 committed files; indexed here when Phase 2 builds out the owner-cadence ingest model.
- `.lattice/bus/` (per-machine, gitignored) — Lattice session bus state when Library dogfoods DFDU.
- Outside-repo sources (operator Drive, external Codex source material) indexed via the owner-cadence ingest model; optionally a machine-readable index manifest for the Director / `build_director_context`.
