# EMCC.Library

EMCC.Library wraps the **Codex** protocol — the Librarian agent and the wiki scaffolding-and-sync tooling that consuming projects use to build and maintain structured markdown documentation wikis. Sibling to `spade0704/EMCC.DFDU` (Lattice 3.0 protocol wrapper).

## Status

**v1.1 — Ready** as of 2026-05-27 (Session 2 / S002 close). The canonical portfolio folder layout per `tasks/plans/portfolio-folder-structure-spec.md` section (a) + (c) is shipped:

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

- **`sync_from_kit.py` v1.0 contract.** v1.1's new `bootstrap.py` is scaffold-only (canonical portfolio frame per spec section c); the consumer wiki it produces has no `_scripts/_template/_config/_context/` subfolders at the wiki root. `sync_from_kit.py` was NOT rewritten in S002 and still writes to those v1.0 target paths — so running Sync against a v1.1-bootstrapped wiki will create paths that don't fit the new shape. MI-16 in `MIGRATION-ISSUES.md` documents this; S004 (consumer-wikis sprint) decides whether to (a) rewrite `sync_from_kit` for the new shape, (b) keep it as v1.0-compat for legacy wikis, or (c) force-migrate legacy wikis forward. Bootstrap a new project with v1.1, but DON'T run Sync against it yet.
- **No packaging artifact.** Library is not distributed as a Python wheel (MI-13 — stdlib-only discipline). Consumers vendor via clone / submodule / sibling-directory checkout. If a packaging story is needed, re-open MI-13.

## Next sprints

- **S003 (master plan Step 5)** — Telegram channel boot (operator action; bot already exists at chat_id 1415844818 with `TELEGRAM_BOT_TOKEN` in env).
- **S004 (master plan Step 6)** — bootstrap the operator's first real consumer wikis (Aviation / Tat / etc.) using the v1.1 canonical scaffold. Retires the MI-16-deferred v1.0-shape tests + decides sync_from_kit's post-v1.1 delivery target.
- **S005 (master plan Step 7)** — bootstrap DFDU's own `wiki/` directory.
