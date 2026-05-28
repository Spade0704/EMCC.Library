# reorganization-instructions.aviation.md

> **Status:** SEED (pre-populated). To be copied to `<aviation-root>/reorganization-instructions.aviation.md` during Aviation Phase 1 (see `EMCC.Library/tasks/plans/before-we-go-to-warm-cocke.md` Part B).

> **Scope:** Per-project path-migration manifest for the **Aviation** repo (`spade0704/aviation`). Cross-repo patterns (P1–P8), audit-hook contract, and the master index of per-project files live in `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md`. Read the master first for pattern definitions; come here for the concrete Aviation moves.

> **Audience:** Librarian agent in the Aviation repo, audit scripts, and any Claude Code session that hits a "file not found" error referencing an old path under `etihad-wiki/output/`.

> **Pair docs:** `EMCC.Library/tasks/plans/portfolio-folder-structure-spec.md` (canonical layout), `EMCC.Library/tasks/plans/before-we-go-to-warm-cocke.md` (the coordination plan that authorized these moves).

---

## How to fill this in during Phase 1

1. When you run `git mv` for a row below, change the row's Status from `⏳ Planned` to `✅ Done in Phase 1 (<commit-sha>)`.
2. If a move was skipped, mark `❌ Skipped — <reason>`.
3. If you discover an additional move not listed here (e.g. an empty stale folder you decide to delete), add a new row and mark it `✅ Done in Phase 1`.
4. After Phase 1 commits land, run a sanity scan: `grep -r "etihad-wiki/output" .` should return zero hits (or only this manifest file).

---

## Aviation — Phase 1 moves (planned 2026-05-28)

**Pre-Phase-1 state:** Aviation repo holds a custom `etihad-wiki/` builder pipeline whose output dir `etihad-wiki/output/` contains 1,857 markdown pages organized by manual (`FCOM/`, `FCTM/`, `OMA/`, `QRH/`) plus `_assets/` and a generated `index.md`. The builder tooling (`build_wiki/`, `build_wiki.py`, `keywords.yaml`, `requirements.txt`) lives alongside the output dir.

**Phase 1 goal:** Adopt the v1.1 canonical portfolio layout. Content moves to `wiki.aviation/git/`; builder tooling moves under `Biz.Automation/wikisys.aviation/`. Codex frame (0-Inbox, tasks, assets, root stubs) emitted by `bootstrap.py aviation --full --yes` from `EMCC.Library`.

### Bootstrap-emitted root frame (S006 Phase 1.B1)

These items are *created* by `bootstrap.py`, not moved. Listed here for completeness so the manifest covers every Phase 1 on-disk delta.

| New path (post-Phase-1) | Source | Pattern | Status |
|---|---|---|---|
| `0-Inbox/.gitkeep` | bootstrap | P6 | ⏳ Planned |
| `Biz.Automation/wikisys.aviation/{_scripts,_template,_config,_canon}/.gitkeep` | bootstrap | P1 | ⏳ Planned |
| `wiki.aviation/{local,git/raw,git/ideas}/.gitkeep` | bootstrap | P4 + P5 | ⏳ Planned |
| `tasks/{todo,sessions,lessons,archive}.md` | bootstrap stub | P8 | ⏳ Planned |
| `assets/{logos,brand,photos,videos,designs,generated}/.gitkeep` | bootstrap | — | ⏳ Planned |
| `CLAUDE.md`, `Index.md`, `Cheatsheet.md`, `.gitignore` | bootstrap stub | — | ⏳ Planned |
| `reorganization-instructions.aviation.md` | bootstrap stub (this file replaces it) | — | ⏳ Planned (overwrite stub with this seed) |
| `.claude/personas/CLAUDE.librarian.md` | bootstrap drop-in | P7 | ⏳ Planned |

### Content moves: etihad-wiki/output/ → wiki.aviation/git/ (Phase 1.B2)

| Old path (pre-Phase-1) | New path (post-Phase-1) | Pattern | Status |
|---|---|---|---|
| `etihad-wiki/output/QRH/` | `wiki.aviation/git/QRH/` | P5 | ⏳ Planned |
| `etihad-wiki/output/FCOM/` | `wiki.aviation/git/FCOM/` | P5 | ⏳ Planned |
| `etihad-wiki/output/OMA/` | `wiki.aviation/git/OMA/` | P5 | ⏳ Planned |
| `etihad-wiki/output/FCTM/` | `wiki.aviation/git/FCTM/` | P5 | ⏳ Planned |
| `etihad-wiki/output/_assets/` | `wiki.aviation/git/_assets/` | P5 | ⏳ Planned |
| `etihad-wiki/output/index.md` | merged into `wiki.aviation/git/Index.md` (then `wiki.aviation/git/index.md` deleted) | P5 + manual merge | ⏳ Planned |
| `etihad-wiki/output/linkify_report.txt` | `tasks/archive/linkify_report_pre-phase-1.txt` (or DELETED if no value) | — | ⏳ Planned (operator decision) |
| `etihad-wiki/output/CLAUDE.md` | DELETED (superseded by bootstrap-emitted root `CLAUDE.md`; content reviewed for any wiki-specific rules to merge into the new root file) | — | ⏳ Planned (operator review) |

### Builder relocation: etihad-wiki/ → Biz.Automation/wikisys.aviation/ (Phase 1.B2)

| Old path (pre-Phase-1) | New path (post-Phase-1) | Pattern | Status |
|---|---|---|---|
| `etihad-wiki/build_wiki/` | `Biz.Automation/wikisys.aviation/_scripts/build_wiki/` | P1 | ⏳ Planned |
| `etihad-wiki/build_wiki.py` | `Biz.Automation/wikisys.aviation/_scripts/build_wiki.py` | P1 | ⏳ Planned |
| `etihad-wiki/keywords.yaml` | `Biz.Automation/wikisys.aviation/_config/keywords.yaml` | P1 | ⏳ Planned |
| `etihad-wiki/requirements.txt` | `Biz.Automation/wikisys.aviation/_scripts/requirements.txt` | P1 | ⏳ Planned |
| `etihad-wiki/check_pdf.py` | `Biz.Automation/wikisys.aviation/_scripts/check_pdf.py` | P1 | ⏳ Planned |
| `etihad-wiki/.claudeignore` | DELETED (replaced by root `.gitignore` from bootstrap; per-builder ignore patterns can be merged into root if still needed) | — | ⏳ Planned |
| `etihad-wiki/.claude/settings.local.json` | `.claude/settings.local.json` (project root; merged with any bootstrap-installed personas drop-in) | P7 | ⏳ Planned |
| `etihad-wiki/README.md` | `Biz.Automation/wikisys.aviation/_scripts/README.md` (or merged into root `README.md` if appropriate) | — | ⏳ Planned (operator review) |

### Post-move sanity (Phase 1 close)

After all moves above, the old `etihad-wiki/` directory should be empty. Delete it. The path `etihad-wiki/` should not exist post-Phase-1.

| Old path (post-moves) | Disposition | Status |
|---|---|---|
| `etihad-wiki/` (now empty) | DELETED | ⏳ Planned |
| `test-edit.md` (project root, currently present) | Operator decision — likely DELETE (debug remnant) | ⏳ Planned (operator review) |

### Empty / numbering-only / placeholder pages (Phase 1.B3)

Phase 1.B3 sweeps `wiki.aviation/git/` for blank / numbering-only / placeholder pages and deletes them after operator confirmation (Librarian Inbox-Sort + propose-await pattern). Each deletion gets a row below at Phase 1 close. Until then, this section is **EMPTY — to be filled in after Inbox-Sort scan**.

| Deleted path | Reason | Status |
|---|---|---|
| (TBD) | (TBD) | ⏳ Phase 1.B3 pending |

### Internal path-reference updates required (Phase 1.B2 follow-up)

When code or docs reference `etihad-wiki/output/`, those references must be rewritten. Track each update below.

| File | Old reference | New reference | Status |
|---|---|---|---|
| `Biz.Automation/wikisys.aviation/_scripts/build_wiki.py` (formerly `etihad-wiki/build_wiki.py`) | output paths to `etihad-wiki/output/` | rewrite to write into `../../../wiki.aviation/git/` (or accept CLI arg) | ⏳ Planned |
| `Biz.Automation/wikisys.aviation/_scripts/build_wiki/` modules (any) | internal `Path("output")` or `output/` literals | rewrite to relative path from new script location | ⏳ Planned |

---

## Phase 2+ moves

Phase 2 (readability passes per manual, manual-by-manual QRH→FCOM→OMA→FCTM) is content-internal — heading normalization, frontmatter, OCR cleanup. No on-disk path moves expected. If a Phase 2 pass requires moving pages between manuals (e.g. a misfiled topic), add a new "Phase 2 corrections" section below.

Phase 3 (cross-linking) is also content-internal. No path moves expected.

---

## See also

- `EMCC.Library/REORGANIZATION-INSTRUCTIONS.md` (master) — patterns P1–P8, audit hooks contract, per-project file index.
- `EMCC.Library/tasks/plans/portfolio-folder-structure-spec.md` — canonical layout decisions.
- `EMCC.Library/tasks/plans/before-we-go-to-warm-cocke.md` — the coordination plan that authorized these moves.
