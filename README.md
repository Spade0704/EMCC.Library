# EMCC.Library

EMCC.Library wraps the **Codex** protocol — the Librarian agent and the wiki scaffolding-and-sync tooling that consuming projects use to build and maintain structured markdown documentation wikis. Sibling to `spade0704/EMCC.DFDU` (Lattice 3.0 protocol wrapper).

## Status

**v1.1 — Ready** as of 2026-05-27 (Session 2 / S002 close); consumer-wiki Sync shipped in S004 (2026-05-28, MI-16 + MI-18 closure). The canonical portfolio folder layout per `tasks/plans/portfolio-folder-structure-spec.md` section (a) + (c) is shipped:

- `bootstrap.py` — scaffold a canonical-shape project (`python bootstrap.py <projectname> [--full|--minimal|--code|--website]`); spec section (c). v1.1 is scaffold-only — no script copy.
- `Biz.Automation/wikisys.library/_scripts/` — Codex automation (27 .py: 20 root + 7 `_lib/` + 5 launcher .ps1). Source-of-truth for the protocol's runtime.
- `Biz.Automation/wikisys.library/_template/` — wiki templates that `sync_from_kit.py` ships into consuming wikis' `_context/` (verbatim discipline preserved).
- `Biz.Automation/wikisys.library/_config/` — config YAMLs (`forbidden_terms`, `cascade_map`, `concept_coverage`, etc.).
- `Biz.Automation/wikisys.library/_canon/` — Library's own canonical entities (roster, taxonomy, timeline, topics — Codex documenting Codex).
- `Biz.Automation/wikisys.library/_context/` — runtime context rules + canonical INGEST/SEMANTIC_LINT/CODEX_LIBRARIAN drop-ins.
- `Biz.Automation/wikisys.library/_decisions/` — ingest log + decision history.
- `wiki.codex/git/codex/` — Codex spec docs canonical location (CODEX_BUILD_SPEC_v1_3.md, CODEX_LIBRARIAN.md, INGEST_PROCEDURE.md, SEMANTIC_LINT_PROCEDURE.md, PROJECT_WIKI_BUILD_SPEC.md, Obsidian-Setup-Guide.md, codex-build-plan.html, Codex_Project_Documentation.pdf, Codex_Workflow_Cheatsheet_v1.txt, codex-build-progress.md).
- `wiki.codex/git/` — Library's self-hosted dogfood wiki content (Codex documenting Codex). 
- `wiki.codex/local/` — gitignored private zone (brain-dump / unfiled).
- `tests/` — Codex test suite (Python stdlib `unittest`; ~589 tests post-S002; v1.0-shape tests retired as MI-16 deferred to S004).
- `.claude/personas/CLAUDE.librarian.md` — the Librarian persona (extended in S002 with 3 new operations + 5 Mentor patterns + Telegram auto-summary contract).
- `.claude/personas/CLAUDE.auditor.md` — Auditor persona (carried verbatim from EMCC.DFDU for Library's own Lattice 3.0 sessions).

## Quick start (new consumer project)

```
cd <portfolio-root>
python <path-to-EMCC.Library>/bootstrap.py <projectname>
cd <projectname>
git init && git add -A && git commit -m "bootstrap"
```

Produces the canonical tree per `tasks/plans/portfolio-folder-structure-spec.md` section (c). Use `--minimal` for thin braindump projects (aviation-career style), `--code` for product-code projects (mobile app / CLI / library), `--website` for public-website projects (Next.js / Squarespace).

## Source

Extracted from `spade0704/project-codex` at SHA `ccf21b7c` (Session 1, 2026-05-27). See `SOURCE-HISTORY.md` for the per-file move inventory, `MIGRATION-ISSUES.md` (MI-01..MI-16) for the per-session known carry, and `REORGANIZATION-INSTRUCTIONS.md` for the machine-readable migration manifest (every old-path → new-path move with commit SHA).

## How consumers use it

A consuming project (scaffolded via `spade0704/EMCC` orchestrator's `scripts/emcc_bootstrap.py`) gets `library` auto-detected and wired into its `emcc.modules.json`. The consuming project runs `python <library>/bootstrap.py <projectname>` to scaffold its canonical frame. Subsequent script + spec-doc delivery into the wiki goes through `sync_from_kit.py` (Sync operation).

Codex itself ships zero external Python dependencies — stdlib only per `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` R_ARCH "Pure Python stdlib only. No pip install."

## Related repos

- `spade0704/EMCC` — umbrella orchestrator + consumer-project template + `emcc_bootstrap.py`
- `spade0704/EMCC.DFDU` — sibling module (Lattice 3.0 protocol; production-ready DFDU Session 8 / `f056f81`)
- `spade0704/project-codex` — Codex's pre-extraction home; archived 2026-05-27

## Tests + CI

```
python -m unittest discover -s tests -t .
```

CI runs on push to `main` and `claude/**`, plus PRs to `main`. See `.github/workflows/test.yml`.

## v1.1 known limitations

- **`sync_from_kit.py` is now v1.1-only.** Resolved in S004 (MI-16 closure): Sync was rewritten for the canonical layout and delivers Codex runtime into the consumer at `Biz.Automation/wikisys.<consumer>/_scripts/` + `_context/` (`INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`, `CODEX_LIBRARIAN.md`) + `wiki.<consumer>/git/codex/PROJECT_WIKI_BUILD_SPEC.md`. It is invoked from the consumer project root: `python <library>/Biz.Automation/wikisys.library/_scripts/sync_from_kit.py <library> [--dry-run] [--force]`. v1.0-shape Sync (writing to `<wiki>/_scripts/` at the wiki root) is **no longer supported** — pre-S004 consumers either migrate to v1.1 first (S004 Mentor-pattern playbook) or freeze at v1.0 on a pre-S004 build.
- **No packaging artifact.** Library is not distributed as a Python wheel (MI-13 — stdlib-only discipline). Consumers vendor via clone / submodule / sibling-directory checkout. If a packaging story is needed, re-open MI-13.

## Next sprints

- **S003 (master plan Step 5)** — Telegram channel boot. **Partially done** (Option A local env vars + bot configured post-S002; cloud-CC remainder blocked by network policy, soft-compliance honored).
- **S004 (master plan Step 6)** — **CLOSED 2026-05-28.** First real consumer wiki (Mentor) migrated v1.0 → v1.1; shipped MI-16 (sync_from_kit v1.1 rewrite) + MI-18 (canon/decisions lookup) closures.
- **S005 (master plan Step 7)** — bootstrap DFDU's own `wiki/` directory.
- **S006+** — remaining consumer wikis (Aviation / Tat / iSommelier / eddyandwolff / aviation-career / EMCC / EMCC.DFDU) on the v1.1 canonical scaffold; greenfield via `bootstrap.py <projectname> --full`.
