# EMCC.Library

**Module placeholder.** EMCC.Library is the planned home of the **Codex** protocol — the Librarian agent responsible for cross-project knowledge artefacts (wikis, indices, ingestion pipelines).

## Current status: not-ready

This repo is intentionally minimal pending Step 2 of EMCC's Binary-Orbit sequencing (see `spade0704/emcc/CLAUDE.md` §Master strategy — currently blocked on `project-codex` v1.0 SHIP).

EMCC's consumer-project template (`spade0704/emcc/templates/consumer-project/emcc.modules.json`) reserves the `library` slot with `status: not-ready`. Consumer projects skip Library wiring on session start until this status flips.

## When this module ships, it will provide

- `documents/librarian/` — canonical Codex spec (analogous to DFDU's `documents/lattice/`)
- `documents/librarian/12-CONSUMING-PROJECT-SETUP.md` — module-specific install playbook, mirroring DFDU's pattern
- `scripts/librarian/` (or similar) — Python package, pip-installable as `librarian`
- `pyproject.toml` at repo root — declares the `librarian` distribution

At that point, EMCC's consumer template gains automatic Library detection alongside DFDU's existing detection in `scripts/emcc_bootstrap.py`. No consumer-side changes needed beyond re-running the bootstrap CLI (or hand-editing `emcc.modules.json` to flip `status: ready`).

## Related repos

- `spade0704/emcc` — umbrella orchestrator + consumer-project template + bootstrap CLI
- `spade0704/emcc.dfdu` — sibling module (Lattice 3.0, ready)
- `spade0704/project-codex` — Codex's pre-extraction home (transitional)
