# EMCC.Library

EMCC.Library wraps the **Codex** protocol — the Librarian agent and the wiki scaffolding-and-sync tooling that consuming projects use to build and maintain structured markdown documentation wikis. Sibling to `spade0704/EMCC.DFDU` (Lattice 3.0 protocol wrapper).

## Status

**Ready** as of 2026-05-27, master-plan Step 3 extraction (Session 1; commit history begins at `094e8a3` with Phase A session-open). The repo provides:

- `bootstrap.py` — one-time scaffold of a new wiki for a consuming project
- `CODEX_BUILD_SPEC_v1_3.md` — authoritative build specification (single canonical version; v1_1/v1_2 stay archived in `spade0704/project-codex`)
- `CODEX_LIBRARIAN.md` — Librarian agent specification
- `INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` — verbatim procedures shipped into every bootstrapped wiki's `_context/` folder
- `PROJECT_WIKI_BUILD_SPEC.md` + `Obsidian-Setup-Guide.md` — wiki build spec + consumer guidance
- `_scripts/` — Codex automation (the 15+ scripts indexed P1–P54; `_lib/` foundation modules)
- `_template/` + `_config/` — wiki templates + config YAMLs that bootstrap copies into new wikis
- `tests/` — Codex test suite (Python stdlib `unittest`; ~821 tests)
- `personas/CLAUDE.librarian.md` — the Librarian persona
- `personas/CLAUDE.auditor.md` — Auditor persona (carried verbatim from EMCC.DFDU for Library's own dogfood / Lattice 3.0 sessions)
- `wiki.codex/` — Library's self-hosted dogfood wiki (Codex documenting Codex)

## Source

Extracted from `spade0704/project-codex` at SHA `ccf21b7c` (2026-05-27). See `SOURCE-HISTORY.md` for the per-file move inventory + verbatim-byte-equal verifications, and `MIGRATION-ISSUES.md` (MI-01..MI-08 + A1/A2/A3) for the extraction's known carry.

## How consumers use it

A consuming project (scaffolded via `spade0704/EMCC` orchestrator's `scripts/emcc_bootstrap.py`) gets `library` automatically detected and wired into its `emcc.modules.json`. The consuming project then runs `bootstrap.py` from this repo to scaffold a `wiki/` directory in its own working tree. From there, the consuming-project's CLAUDE session uses Codex's `_scripts/` + the verbatim procedures to ingest sources, route into canon, validate against forbidden-terms / cascade / canon-integrity, and roll up dashboards.

Codex itself ships zero external Python dependencies (`pathlib`, `unittest`, `dataclasses`, `fnmatch`, etc. — stdlib only per `CODEX_BUILD_SPEC_v1_3.md` R_ARCH "Pure Python stdlib only. No pip install."). Consuming projects can run Codex from a vanilla Python 3.11 environment.

## Related repos

- `spade0704/emcc` — umbrella orchestrator + consumer-project template + `emcc_bootstrap.py`
- `spade0704/emcc.dfdu` — sibling module (Lattice 3.0 protocol; production-ready as of DFDU Session 8 / `f056f81`)
- `spade0704/project-codex` — Codex's pre-extraction home; archived as of this Session 1 / master plan Step 3 (CLAUDE.md + README.md rewritten as archive banners pointing here)

## Tests + CI

```
python -m unittest discover -s tests -t .
```

CI runs on push to `main` and `claude/**`, plus PRs to `main`. See `.github/workflows/test.yml`.

## Next sprints

- **S002 (master plan Step 4)** — Codex v1.0 → v1.1 update. Folds in portfolio-room refined consumer-project folder spec, mentor wiki report findings, 5 deferred Librarian-spec items (TF-IDF cross-link curation, routing tag work queue, Maintenance loop tag-scan, three-tier tag namespace authority, plug-in failure handling), and any S048-T1 findings from project-codex.
- **S004 (master plan Step 6)** — bootstrap the operator's first real consumer wikis (portfolio projects: Aviation / Mentor / Tat / etc.) on the refined v1.1 folder layout.
- **S005 (master plan Step 7)** — bootstrap DFDU's own `wiki/` directory.
