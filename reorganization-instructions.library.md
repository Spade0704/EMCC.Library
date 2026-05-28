# reorganization-instructions.library.md

> **Scope:** Per-project path-migration manifest for **EMCC.Library** only.
> Cross-repo patterns (P1–P8), audit-hook contract, and the master index of
> per-project files live in `REORGANIZATION-INSTRUCTIONS.md` (master) at
> the Library root. Read the master first for pattern definitions; come
> here for the concrete Library-side moves.

> **Audience:** Librarian agent, audit scripts, and any Claude Code session
> in this repo that hits a "file not found" error referencing an old path.

> **Pair docs:** `SOURCE-HISTORY.md` (where this Library's content came
> from originally — project-codex SHA), `MIGRATION-ISSUES.md` (issues
> encountered during migration), `tasks/plans/portfolio-folder-structure-spec.md`
> (the narrative + decisions; this file is the machine-readable manifest
> derived from that spec for Library specifically).

---

## EMCC.Library — per-project moves

### Session 1 (master plan Step 3) — Codex MODULE source files imported

**Pre-Session-1 state:** SHA `156c253` on `main`. Library was the
`not-ready` placeholder; only `wiki.codex/` (dogfood wiki) + `0. Inbox/`
+ `.gitignore` + `README.md` existed at root.

**Session 1 moves** — commits `094e8a3` → `ab94fc7` on
`claude/lattice-3-production-check-Rdkfu`, pushed 2026-05-27. These
moves brought Codex MODULE source files from project-codex into Library
root; they did NOT yet apply the canonical-layout restructure.

| Old path (project-codex SHA `ccf21b7`) | New path (Library Session 1) | Pattern | Status |
|---|---|---|---|
| `0. Inbox/codex-wiki-folder-org-principle.md` | `0-Inbox/codex-wiki-folder-org-principle.md` | P6 | ✅ Session 1 |
| `bootstrap.py` | `bootstrap.py` (Library root) | — | ✅ Session 1 |
| `CODEX_BUILD_SPEC_v1_3.md` | `CODEX_BUILD_SPEC_v1_3.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `CODEX_LIBRARIAN.md` | `CODEX_LIBRARIAN.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `INGEST_PROCEDURE.md` | `INGEST_PROCEDURE.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `SEMANTIC_LINT_PROCEDURE.md` | `SEMANTIC_LINT_PROCEDURE.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `PROJECT_WIKI_BUILD_SPEC.md` | `PROJECT_WIKI_BUILD_SPEC.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `Obsidian-Setup-Guide.md` | `Obsidian-Setup-Guide.md` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `codex-build-plan.html` | `codex-build-plan.html` (Library root) | — | ✅ Session 1 (S002 moves it again per P2) |
| `_scripts/` (minus 3 lattice-2.0 scripts) | `_scripts/` (Library root) | — | ✅ Session 1 (S002 moves it again per P1) |
| `_template/` | `_template/` (Library root) | — | ✅ Session 1 (S002 moves it again per P1) |
| `_config/` | `_config/` (Library root) | — | ✅ Session 1 (S002 moves it again per P1) |
| `tests/` (minus 5 lattice-2.0 tests) | `tests/` (Library root) | — | ✅ Session 1 (stays at root per `<product-code-root>` rule) |
| `Sources/Raw/` | `Sources/Raw/` (Library root) | — | ✅ Session 1 (S002 moves it again per P3) |
| `documents/Codex_*.{pdf,txt}` + `documents/codex-build-progress.md` | `documents/codex/<filename>` | — | ✅ Session 1 (S002 moves them again per P2) |
| `.claude/personas/CLAUDE.librarian.md` | `.claude/personas/CLAUDE.librarian.md` (Library root) | P7 | ✅ Session 1 |
| (NEW) | `.claude/personas/CLAUDE.auditor.md` (byte-equal from `EMCC.DFDU/personas/CLAUDE.auditor.md`) | P7 | ✅ Session 1 |
| (NEW) | `CLAUDE.md`, `module.json`, `SOURCE-HISTORY.md`, `MIGRATION-ISSUES.md`, `.github/workflows/test.yml` | — | ✅ Session 1 |
| `tasks/v1.1-backlog.md` | `tasks/v1.1-backlog.md` (Library) | — | ✅ Session 1 |
| (NEW) | `tasks/{todo,sessions,lessons,archive}.md` | — | ✅ Session 1 |

### S002 / Codex v1.1 — canonical-layout restructure

Module source files extracted to `Biz.Automation/wikisys.library/`; spec
docs became wiki content under `wiki.codex/git/codex/`; `wiki.codex/`
internal restructure into `git/` + `local/` subfolders. Closed
2026-05-27 with 8+ commits on `claude/codex-v1.1-S002-restructure`.

| Old path (Library Session 1) | New path (post-S002) | Pattern | Status |
|---|---|---|---|
| `_scripts/` | `Biz.Automation/wikisys.library/_scripts/` | P1 | ✅ Done in S002 B2 (commit `1e675fd`) |
| `_template/` | `Biz.Automation/wikisys.library/_template/` | P1 | ✅ Done in S002 B2 (commit `1e675fd`) |
| `_config/` | `Biz.Automation/wikisys.library/_config/` (merged with `wiki.codex/_config/`) | P1 | ✅ Done in S002 B2 + B4 (commits `1e675fd` + `d0dfdbb`) |
| `Sources/Raw/` | `wiki.codex/git/raw/` (merged with `wiki.codex/_sources/raw/`; root README deleted as superseded — MI-15) | P3 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `CODEX_BUILD_SPEC_v1_3.md` | `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `CODEX_LIBRARIAN.md` | `wiki.codex/git/codex/CODEX_LIBRARIAN.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `INGEST_PROCEDURE.md` | `wiki.codex/git/codex/INGEST_PROCEDURE.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `SEMANTIC_LINT_PROCEDURE.md` | `wiki.codex/git/codex/SEMANTIC_LINT_PROCEDURE.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `PROJECT_WIKI_BUILD_SPEC.md` | `wiki.codex/git/codex/PROJECT_WIKI_BUILD_SPEC.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `Obsidian-Setup-Guide.md` | `wiki.codex/git/codex/Obsidian-Setup-Guide.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `codex-build-plan.html` | `wiki.codex/git/codex/codex-build-plan.html` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `documents/codex/Codex_Project_Documentation.pdf` | `wiki.codex/git/codex/Codex_Project_Documentation.pdf` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `documents/codex/Codex_Workflow_Cheatsheet_v1.txt` | `wiki.codex/git/codex/Codex_Workflow_Cheatsheet_v1.txt` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `documents/codex/codex-build-progress.md` | `wiki.codex/git/codex/codex-build-progress.md` | P2 | ✅ Done in S002 B3 (commit `fc99147`) |
| `wiki.codex/Home.md` | `wiki.codex/git/Home.md` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/00-Start-Here/` | `wiki.codex/git/00-Start-Here/` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/01-Architecture/` | `wiki.codex/git/01-Architecture/` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/02-Operations/` | `wiki.codex/git/02-Operations/` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/04-Contributing/` | `wiki.codex/git/04-Contributing/` | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/.claude/` | `wiki.codex/git/.claude/` (dogfood Librarian drop-in) | P5 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_canon/` | `Biz.Automation/wikisys.library/_canon/` | P1 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_config/` | `Biz.Automation/wikisys.library/_config/` (merged with root `_config/`) | P1 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_context/` | `Biz.Automation/wikisys.library/_context/` | P1 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_decisions/` | `Biz.Automation/wikisys.library/_decisions/` | P1 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_sources/raw/` | `wiki.codex/git/raw/` (merged with root `Sources/Raw/`) | P3 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_brain_dump/` | `wiki.codex/local/ideas/` (untracked content; gitignored under new `wiki.*/local/` rule) | P4 | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `wiki.codex/_scripts/` (27 stale bootstrap-output files) | DELETED (older than canonical; documented as MI-14) | — | ✅ Done in S002 B4 (commit `d0dfdbb`) |
| `bootstrap.py` | `bootstrap.py` (STAYS at Library root — entry script) | — | ✅ Stays |
| `tests/` | `tests/` (STAYS at root — `<product-code-root>` rule) | — | ✅ Stays |
| `.claude/personas/CLAUDE.{auditor,librarian}.md` | `.claude/personas/CLAUDE.{auditor,librarian}.md` (STAYS — P7 already canonical) | — | ✅ Stays |
| `module.json`, `CLAUDE.md`, `SOURCE-HISTORY.md`, `MIGRATION-ISSUES.md`, `README.md`, `.gitignore` | (STAY at root) | — | ✅ Stays |
| `Index.md`, `Cheatsheet.md` | (NEW root files; ship in S004 first real consumer-project bootstrap; Library itself uses CLAUDE.md ROOT_INDEX as Index.md surrogate per spec a variance allowance) | — | ⏳ Deferred to S004 |

### S003b — Library staleness archive sweep (closed 2026-05-27)

Two full relocations on `claude/library-staleness-S003b-n8r3w`. Rest of
the audit's 9 ARCHIVE candidates use banner-at-current-path so the
cross-link validator stays green — those banner-only files do NOT
appear in this manifest because path is unchanged.

| Old path (post-S002) | New path (post-S003b) | Pattern | Status |
|---|---|---|---|
| `0-Inbox/codex-wiki-folder-org-principle.md` | `wiki.codex/git/_archive/_inbox/codex-wiki-folder-org-principle.md` | — (full relocation; 0 inbound wikilinks; move = Librarian-discipline empty-inbox signal) | ✅ Done in S003b |
| `Biz.Automation/wikisys.library/_scripts/launchers/` (5 files: 4 .ps1 + README.md) | `Biz.Automation/wikisys.library/_scripts/_archive/launchers/` (+ new `_archive/README.md` documenting Lattice 2.0 → 3.0 transition) | — (full relocation; Lattice 2.0 Nexus 4-persona model retired; no active dependents — `test_bootstrap.py` reference is MI-16-retired) | ✅ Done in S003b |

### S002-internal callers updated

The B5a path-rebase commit (`7707d5b`) and B5b bootstrap.py rewrite
(`9bf1004`) updated the following internal callers to read from the
new source-of-truth paths:

| Caller | Changed via | Update |
|---|---|---|
| `bootstrap.py` `_resolve_source_scripts_dir()` (line 62) | B5a `7707d5b` | default → `Biz.Automation/wikisys.library/_scripts` |
| `bootstrap.py` `_resolve_template_dir()` (line 114) | B5a `7707d5b` | default → `Biz.Automation/wikisys.library/_template` |
| `bootstrap.py` (entire file) | B5b `9bf1004` | full canonical-output rewrite per spec (c); scaffold-only (no script copy); `<projectname>` positional CLI; 5 stub generators |
| `Biz.Automation/wikisys.library/_scripts/sync_from_kit.py` | B5a `7707d5b` | new `WIKISYS_REL` + `SPEC_DOCS_REL` constants; `_required_sources()` + `_build_plan()` prefix source paths with `wikisys.library/` + `wiki.codex/git/codex/` |
| `Biz.Automation/wikisys.library/_scripts/_lib/frontmatter.py` `parse_config_yaml` | B6 `0127c4e` | FINDING #1: block-list sub-list under continuation field — `pending_subkey` FSM state added |
| `tests/__init__.py` sys.path | B5a `7707d5b` | rebase to `wikisys.library/_scripts` |
| `tests/perf/bench_frontmatter.py` sys.path inserts (×2) | B5a `7707d5b` | rebase |
| `tests/test_phase6_full_chain_e2e.py` (REPO_ROOT-relative paths) | B5a `7707d5b` then B5b `9bf1004` (module SkipTest) | rebased; later skipped as MI-16 |
| `tests/test_scaffold_source.py`, `tests/test_scaffold_brain_dump.py` (SCAFFOLD_PY) | B5a `7707d5b` | rebase |
| `tests/test_t1_p52_bootstrap_operation.py` (TEMPLATE_DIR, CODEX_SCRIPTS) | B5a then B5b skip | rebased then MI-16 retire |
| `tests/test_t2_p53_sync_operation.py` (multiple REPO_ROOT paths) | B5a then B5b skip | rebased then MI-16 retire |
| `tests/test_t3_p54_ingest_operation.py` (TEMPLATE_DIR) | B5a then B5b skip | rebased then MI-16 retire |
| `tests/test_sync_from_kit.py` `_make_codex_install` fixture | B5a `7707d5b` | fixture rewrites source layout to mirror new split (wikisys + spec-docs roots) |
| `tests/test_bootstrap.py` (entire file) | B5b `9bf1004` (module SkipTest) | MI-16 retire — file tests v1.0 contract |

**Note on `_scripts/_lib/config_loader.py`:** the discovery layer
turned out to accept a `config_path` argument (relative to the
consuming wiki, not Library), so no Library-internal path rebase was
needed. The B5a path-rebase plan over-allocated edit time here.

**Note on `_template/_context__SEP__INGEST_PROCEDURE.md`:** the
manifest pre-flight predicted this template file would need rewiring
to read from `wiki.codex/git/codex/` after S002. It turned out the
template file is byte-equal to the spec doc; the symlink/copy chain
flows through `sync_from_kit.py`'s `SPEC_DOCS_REL`-prefixed source
lookup (now in place per B5a). No template-file edit was required.

---

## See also

- `REORGANIZATION-INSTRUCTIONS.md` (master) — patterns P1–P8, audit
  hooks contract, per-project file index.
- `SOURCE-HISTORY.md` — origin SHA from project-codex.
- `MIGRATION-ISSUES.md` — MI-01..MI-18 registry.
- `tasks/plans/portfolio-folder-structure-spec.md` — narrative + decisions.
