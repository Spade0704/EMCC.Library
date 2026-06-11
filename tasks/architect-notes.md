# Architect Notes — EMCC.Library

> Active scope notes, open threads, deferred decisions. Auditor MAY READ this for scope context (per `EMCC.DFDU/personas/CLAUDE.auditor.md` allow-list — `tasks/lessons.md` and `tasks/plans/` are off-limits; this file is not).

## 2026-06-11 — demote guard observation: raw-placeholder pages evade the substituted-body comparison (proposed enhancement, not built)

Mentor's boilerplate disposition (Operator-ratified demote-all-4) surfaced the root cause of its
4x SKIP-MODIFIED: the pages were materialized pre-Codex WITHOUT `<Project Name>` substitution, so
their bodies kept the raw placeholders. `demote_boilerplate_stubs.py` compares against historical
template bodies with the project name SUBSTITUTED, so a raw-placeholder page can never match even
when it is byte-identical to a shipped template (Mentor's Style-Guide literally was). The guard
behaved correctly per R4 (skip + report; a human decided), but a cheap enhancement would also
compare against the RAW un-substituted template bodies — pages matching those are boilerplate by
construction. PROPOSED only; needs its own gate if/when a second consumer hits the same vintage.
(Mentor was hand-demoted 2026-06-11; no other consumer is known to carry raw-placeholder
boilerplate — the other 10 demoted clean at the wave.)

## S007 — EMCC shared package + modular `claude-<module>.md` delivery (2026-05-28, OPEN/planned)

> Cross-repo architectural alignment recorded here so Codex stays consistent with how DFDU/Lattice is now delivered into projects. Implementation co-ships with DFDU per-project wiring (operator: "we will implement this together as we implement DFDU on a project"). Tracked actionably in `tasks/todo.md` S007.

**Context.** While making Lattice 3.0 bootstrappable into all projects, EMCC gained a *shared package* + a *merge-safe wiring tool* (built 2026-05-28, EMCC branch `claude/nifty-ritchie-f6snD`):
- `EMCC/scripts/emcc_wire.py` — idempotent, merge-safe initializer for **existing** repos (vs `emcc_bootstrap.py`, which is greenfield-only). Reuses `sync_from_kit.py`'s OVERWRITE / MERGE-NEW / NEVER-TOUCH model.
- `EMCC/templates/shared/module-templates/{claude-dfdu,claude-library}.md` — vendored per-module instruction drop-ins (placeholder-substituted: `{{PROJECT_NAME}}`, `{{WIKINAME}}`, profile fields).
- `EMCC/marketplace/` — a Claude Code plugin marketplace; first plugin `emcc-lattice` ships `/research` `/build` `/update_doc`.

**Modular CLAUDE.md convention (now portfolio-standard).** Root `CLAUDE.md` carries only a marker-delimited (`<!-- EMCC:MODULES:BEGIN/END -->`) "Connected EMCC modules" index; per-module detail lives in `.claude/modules/claude-<module>.md`, loaded on-demand. This *supersedes* the S006-era pattern of inlining the Codex/Librarian block at the bottom of each consumer's root `CLAUDE.md`. iSommelier pilot migrated 2026-05-28 (`emcc_wire.py --module dfdu --module library --tier lite`): its inlined Codex block was lifted into `.claude/modules/claude-library.md`.

**Implication for Codex (delivery only — spec/scripts/`sync_from_kit` unchanged):**
1. The Librarian consumer guidance is now a *vendored module file* (`claude-library.md`), not an inline CLAUDE.md block. The canonical source stays `wiki.codex/git/codex/CODEX_LIBRARIAN.md` (synced to each consumer's `_context/`); `claude-library.md` is the routing/summary drop-in.
2. Future: an **`emcc-codex`** marketplace plugin for Librarian skills (Ingest / Semantic-Lint / Maintain), mirroring `emcc-lattice` — factor prompts from `CODEX_LIBRARIAN.md`. Open question: do we want a drift guard (`claude-library.md` ⇄ `CODEX_LIBRARIAN.md`) analogous to `generate_persona_dropin.py`'s `--check`?
3. tat_app + supplystationusa still carry the inlined Codex block; they get migrated to the modular layout when DFDU is wired into them.

**Decision forks:** (a) ~~Librarian skill names + ship `emcc-codex` now vs later~~ **RESOLVED 2026-05-28** — shipped now as `/ingest` `/lint` `/maintain` `/sync` (skills load persona + verbatim procedure; no spec change). (b) drift-guard for the vendored `claude-library.md` ⇄ `CODEX_LIBRARIAN.md` — still open. (c) whether `bootstrap.py` should emit the modular `.claude/modules/` layout for greenfield wikis directly (today `emcc_wire.py` adds it post-hoc) — still open.

## S004-mentor-v1.1-migration (2026-05-27) — Architect plan

### Goal

Ship Mentor's v1.0 → v1.1 canonical-layout migration on `spade0704/Project-Mentor` and concurrently close MI-16 (sync_from_kit at v1.0 contract) + MI-18 (canon-lookup divergence post-S002 split) on `spade0704/EMCC.Library`. Two repos, one arc. After close, Library + Mentor are both at full v1.1 production state.

Operator pulled this forward 2026-05-27. Original plan: M002 (Mentor folder cleanup within v1.0-shape) as small sprint; v1.1 canonical migration deferred to later S004. Pull-forward rationale: Mentor at 0 concept gaps / 0 contradictions post-M001 is the cleanest baseline available; deferring accumulates state. Full v1.1 + MI-16 + MI-18 closure in one arc lower-risk than incremental.

### Spec correction note (carried in this sprint)

`tasks/plans/portfolio-folder-structure-spec.md` §"Mentor — Greenfield bootstrap" line 881 reads "No on-disk migration needed. Mentor was greenfield." That claim is outdated. Mentor was bootstrapped 2026-05-25 via Codex's S048-T1, BEFORE S002 v1.1 spec landed on 2026-05-27. Mentor's on-disk shape is v1.0 (`<wiki>/_scripts/`, `<wiki>/_canon/`, etc. at wiki root) not v1.1 canonical. This sprint performs the on-disk migration the spec claimed was unnecessary. Spec edit deferred to Phase E5 (REORGANIZATION-INSTRUCTIONS.md manifest update) or as inline doc-correction during E2.

### Source-of-truth references

- Master plan: `/root/.claude/plans/check-the-dfdu-project-bubbly-knuth.md` Step 6 (consumer-project wikis)
- Portfolio spec: `tasks/plans/portfolio-folder-structure-spec.md` §(a) canonical layout + §(b) Mentor punchlist (treat as v1.0-shape consumer; spec line 881 outdated)
- Migration manifest: `REORGANIZATION-INSTRUCTIONS.md` (Mentor per-project moves table to be added in Phase E5)
- Mentor pre-migration SHA on `main`: `932e3ee4d37a9185551159b899ca7eda73445e1c` (rollback anchor)
- Library pre-S004 SHA on `main`: `8c2193ca4b230446aefb555695ee190540022346`
- Branch (both repos): `claude/s004-mentor-v1.1-migration-na3hg`
- Branch suffix: `na3hg`

### Operator decisions locked at Phase A

| # | Decision | Locked answer |
|---|---|---|
| D1 | Scope (lean structural-only vs full incl. MI-16+MI-18) | **FULL** — MI-16 + MI-18 fixes ship in this sprint; no interim broken-sync state |
| D2 | Canonical layout (v1.1 per spec §a + §b Mentor punchlist) | **YES** — Subject-named variance preserved: `wiki.mentor/` (Mentor IS project name) |
| D3 | `wiki_legacy_2026-05-25/` disposition | **Relocate** → `wiki.mentor/git/_archive/wiki_legacy_2026-05-25/` with banner pointing at v1.1 layout |
| D4 | SPLIT pattern audit handling | **Fold into B5/B6** — touch each page when moving; audit pairing as we go; surface unpaired Authorities (Karpathy + Cherny) as operator-confirm proposals |
| D5 | Auditor dispatch | **Lattice 3.0 Regime B** — Agent tool fresh-context dispatch at session close per S002 pattern; DFDU `CLAUDE.auditor.md` 116-line persona embedded in dispatch prompt |

### Sub-phase decomposition (A-F)

**Phase A — Session open + plan + snapshot** — commit 1 (both repos)
- Boris S004 OPEN session entry on Library `tasks/sessions.md` + Mentor `wiki/_decisions/sessions.md`
- Architect plan banked here (Library `tasks/architect-notes.md` §S004)
- Pre-migration SHAs recorded (rollback anchor)
- Verify Mentor post-M001 clean baseline: 28 pages, 0 contradictions, 0 cascade staleness, 54% cross-link, 15/15 validators OK
- Branch `claude/s004-mentor-v1.1-migration-na3hg` created on BOTH repos

**Phase B — Mentor structural migration (B1-B10)** — commits 2-11 on Mentor

- **B1. Pre-flight.** `.gitignore` add `wiki.mentor/local/` + `Biz.Automation/`; verify post-M001 clean (modulo persistent operator-local UI dirts: `.obsidian/workspace.json`, `.obsidian/graph.json`, `JP CheatSheet` — accepted carry-state, non-blocking).
- **B2. `wiki/_scripts/` → `Biz.Automation/wikisys.mentor/_scripts/`.** Pattern P1. Includes `_lib/` + `__pycache__/` (skip pycache); use `git mv` for rename detection.
- **B3. `wiki/_template/` (none — Mentor has no template dir), `_config/`, `_canon/`, `_context/`, `_decisions/` → `Biz.Automation/wikisys.mentor/_*`.** Pattern P1.
- **B4. `wiki/_sources/raw/` → `wiki.mentor/git/raw/`.** Pattern P3. Includes legacy-inbox / legacy-pages / legacy-tasks / playbook / web / x / youtube / 0-inbox-items / README.md.
- **B5. `wiki/_brain_dump/` → `wiki.mentor/local/ideas/`.** Pattern P4. Empty other than README; gitignored under new pattern.
- **B6. Topic folders + Home + SPLIT audit + legacy archive.** Pattern P5.
  - `wiki/00-Start-Here/` → `wiki.mentor/git/00-Start-Here/`
  - `wiki/01-Authorities/` → `wiki.mentor/git/01-Authorities/`
  - `wiki/02-References/` → `wiki.mentor/git/02-References/`
  - `wiki/03-Topics/` (empty) → `wiki.mentor/git/03-Topics/`
  - `wiki/04-Contributing/` → `wiki.mentor/git/04-Contributing/`
  - `wiki/Home.md` → `wiki.mentor/git/Home.md`
  - `wiki_legacy_2026-05-25/` → `wiki.mentor/git/_archive/wiki_legacy_2026-05-25/` + `_archive/README.md` banner
  - SPLIT pairing audit per file: surface unpaired Authorities (Karpathy + Cherny) as proposals in commit message; resolve in B6 followup or carry to backlog.
  - Empty wiki/ dirs `Attachments/`, `public/`, `scripts/` — delete in B10 cleanup.
- **B7. `wiki/_confidential/` → `wiki.mentor/local/_confidential/`.** Per P4 zone reshuffle; gitignored.
- **B8. Persona hoist.** `wiki/.claude/personas/CLAUDE.librarian.md` exists? — verify. If yes, move to `<mentor-root>/.claude/personas/CLAUDE.librarian.md` per P7. Mentor `.claude/` already exists at root (per CLAUDE.md folder listing).
- **B9. Root v1.1 frame author.** Per spec §a:
  - `CLAUDE.md` (Mentor-specific operating rules; light template-based; rewrite existing project-root CLAUDE.md to v1.1 shape — currently points at `wiki/` paths, needs path-migration update + Index.md pointer + ROOT_INDEX table)
  - `Index.md` (file-map — NEW; Mentor-specific structure, not Library's)
  - `Cheatsheet.md` (operator preference)
  - `tasks/{todo,sessions,lessons,archive}.md` (move from `wiki/_decisions/` via `git mv`)
  - `tasks/architect-notes.md` (NEW or move existing M001 notes if any)
  - `0-Inbox/.gitkeep` (rename existing `0. Inbox/` — operator-facing legacy mirror — per P6)
  - **`module.json` vs `emcc.modules.json` decision:** Mentor is a CONSUMER (not a Library/DFDU module). Per spec §c, consumer projects get `emcc.modules.json` referencing Library + DFDU, NOT `module.json` (which is for module identity). Decision: ship `emcc.modules.json` referencing Library@1.1.0 + DFDU.
  - `assets/{logos,brand,photos,videos,designs,generated}/.gitkeep` per spec §c canonical tree.
  - `.gitignore` extend (already extended in B1).
- **B10. Cleanup empty wiki/ shell.** Verify `git ls-files | grep "^wiki/"` returns empty; `rm -rf wiki/` (directory only — content all moved). Also remove pre-existing empty stubs `Attachments/`, `public/`, `scripts/` per M002 carry-forward.

**Phase C — MI-16 sync_from_kit v1.1 rewrite (Library)** — commits 12-15 on Library

- **C1.** Rewrite `Biz.Automation/wikisys.library/_scripts/sync_from_kit.py` for v1.1 contract:
  - Old: copies `<library>/_scripts/`, `_template/`, `_config/`, `_context/` to `<wiki>/_scripts/` etc.
  - New: copies `<library>/Biz.Automation/wikisys.library/_scripts/`, `_template/`, `_config/`, `_context/` to `<consumer>/Biz.Automation/wikisys.<consumer>/_*`; spec docs (INGEST_PROCEDURE.md + SEMANTIC_LINT_PROCEDURE.md) to `<consumer>/wiki.<consumer>/git/codex/`.
  - Preserve precedence rules (overwrite vs merge-new vs never-touch — `Home.md` NEVER-touched-by-Sync per Mentor pattern).
- **C2.** Add `tests/test_sync_from_kit.py` v1.1 contract tests against synthetic consumer wiki in `tmp/`; un-skip the MI-16-marked test cases that asserted v1.0 contract.
- **C3.** Update `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` §4.2 Sync to document v1.1 paths.
- **C4.** End-to-end verify: `cd <mentor>; python <library>/Biz.Automation/wikisys.library/_scripts/sync_from_kit.py <library>` produces clean sync — `wikisys.mentor/_scripts/` refreshed, `wiki.mentor/git/*` untouched, `_context/*` updated verbatim.

**Phase D — MI-18 canon-lookup marker-walk (Library)** — commits 16-18 on Library

- **D1.** Add `find_canon_dir()` to `Biz.Automation/wikisys.library/_scripts/_lib/`. Architect decision: extend `frontmatter.py` (already houses `_find_wiki_root()` from MI-17 partial fix) rather than new `canon.py` module — keeps marker-walk discovery family together.
  - Marker-walk from WIKI_ROOT:
    - Case 1 (v1.0-shape): `<WIKI_ROOT>/_canon/` exists → return that
    - Case 2 (v1.1-shape): walk up to install root (CLAUDE.md + module.json co-existing) → check `<install>/Biz.Automation/wikisys.<name>/_canon/`
    - Case 3 (no canon): raise `FileNotFoundError` with clear message; don't crash silently
- **D2.** Update `check_concept_coverage.py` (P13) to use `find_canon_dir()`. Sweep other affected scripts via grep — likely affected per MI-17 carry: `validate_canon_integrity.py`, `build_canon_drift_report.py`, `validate_topic_registry.py`, any script reading `_canon/*.yaml`.
- **D3.** Same marker-walk pattern for `_decisions/` lookups — Recent Ingest section of Library's `health.md` is currently empty because dashboard generator can't find `_decisions/ingest-log.md` post-S002. Add `find_decisions_dir()` companion to `_lib/`. Affected: `update_dashboards.py` orchestrator.
- **D4.** Tests for `find_canon_dir()` + `find_decisions_dir()` against both v1.0-shape (pre-migration Mentor fixture, synthetic) and v1.1-shape (Library + post-migration Mentor fixture, synthetic). Register MI-18 in `MIGRATION-ISSUES.md` with disposition `RESOLVED in S004`.

**Phase E — End-to-end validation** — verification, no new commits unless edits needed

- **E1.** Library: `python -m unittest discover -s tests -t .` from Library root. Expected: 589+ tests pass (Phase D adds new tests for canon-lookup).
- **E2.** Library: `python Biz.Automation/wikisys.library/_scripts/update_dashboards.py` against Library's own `wiki.codex/git/`. Expected: ALL 17 sub-scripts return OK; MI-18 fix closes remaining MI-17-deferred failures; `health.md` shows real "Recent Ingest" entries from `_decisions/ingest-log.md`.
- **E3.** Mentor: `python <mentor>/Biz.Automation/wikisys.mentor/_scripts/update_dashboards.py` against `wiki.mentor/git/`. Expected: same as E2; post-migration content state matches post-M001 (28 pages, 0 contradictions, 54% cross-link, 53% completion) — no regression from restructure.
- **E4.** Sync Library → Mentor end-to-end (per C4).
- **E5.** `REORGANIZATION-INSTRUCTIONS.md` manifest update on Library: add Mentor per-project moves table with all B1–B10 mapping rows. Spec-correction note re Mentor "no migration needed" outdatedness.

**Phase F — Auditor dispatch + session close** — commit 19+20 on both repos

- **F1.** Construct `audit_request` envelope:
  - `audit_id`: `audit-mentor-v1.1-migration-2026-05-27`
  - `task_id`: `s004-mentor-v1.1-migration`
  - `trigger`: schedule (sprint close) + risk (cross-repo + L2+ + sync rewrite + canon-lookup new module)
  - `profile`: l2-plus
  - Acceptance criteria AC1-AC10 enumerated below
- **F2.** Build dispatch prompt via DFDU `build_auditor_prompt` if importable; else inline equivalent. Embed `EMCC.DFDU/personas/CLAUDE.auditor.md` (canonical 116-line persona).
- **F3.** Dispatch via Claude Code Agent tool, `subagent_type general-purpose`, fresh context. Auditor judges both repos' final state.
- **F4.** Read verdict. Pass → close session with Boris CLOSED entries on Library + Mentor + open PRs. Concerns → address inline + close on pass. Block → surface to operator via Telegram `decision_needed`.

### Acceptance criteria (AC1–AC10)

| AC | Criterion |
|---|---|
| AC1 | Mentor at v1.1 canonical layout per spec §a — `wiki.mentor/git/`, `Biz.Automation/wikisys.mentor/`, `tasks/`, `0-Inbox/`, `.claude/personas/` at root, etc. |
| AC2 | `wiki_legacy_2026-05-25/` archived with banner at `wiki.mentor/git/_archive/`; no broken cross-refs |
| AC3 | SPLIT pattern audited per page; unpaired Authorities (Karpathy + Cherny) flagged (or paired) per operator decision |
| AC4 | `sync_from_kit.py` rewritten for v1.1 contract; tests pass; Library → Mentor sync verified end-to-end |
| AC5 | `find_canon_dir()` + `find_decisions_dir()` implemented; affected scripts use them; tests pass against both v1.0 + v1.1 layouts |
| AC6 | Library tests green (no regression from MI-16 + MI-18 changes) |
| AC7 | Library dashboards run cleanly against `wiki.codex/git/` — all 17 sub-scripts OK; Recent Ingest populated |
| AC8 | Mentor dashboards run cleanly against `wiki.mentor/git/` — no regression vs post-M001 (28 pages, 0 contradictions, 54% cross-link, 53% completion) |
| AC9 | `REORGANIZATION-INSTRUCTIONS.md` Mentor per-project moves table added |
| AC10 | Auditor verdict = `pass` (or concerns with resolution) |

### Risk register

- **R1 — git mv preserves history?** Per-file `git log --follow` must work post-merge. Mitigation: use `git mv` for every move; never rewrite-as-new-file.
- **R2 — Path-hardcoded scripts break post-move.** Mentor's `_scripts/` includes `_lib/frontmatter.py::WIKI_ROOT = parent.parent.parent` (3 levels up). Post-move from `wiki/_scripts/_lib/` to `Biz.Automation/wikisys.mentor/_scripts/_lib/`, the path math now resolves to `Biz.Automation/wikisys.mentor/` — incorrect. Mitigation: Mentor's `_scripts/` carries Codex's pre-MI-17 `WIKI_ROOT` math; needs MI-17 marker-walk pattern applied. Either (a) re-sync from Library post-migration so Mentor inherits the marker-walk fix (Phase E4 covers this; sync_from_kit will deliver post-MI-17 frontmatter.py), or (b) apply marker-walk fix to Mentor's local copy in B2.
- **R3 — Mentor's R-00006 references `Project Mentor/` skill folder at root** — that path stays. Cross-link validator may flag if any wiki page references `wiki/...` paths post-migration. Mitigation: grep for `wiki/_` prefix in moved page bodies; rewrite to `wiki.mentor/git/...` patterns; commit as B-cleanup.
- **R4 — `.obsidian/` Obsidian vault state** — workspace.json + graph.json persist across migration; should NOT be in repo. Mitigation: Phase B1 .gitignore extension adds `.obsidian/workspace.json` + `.obsidian/graph.json` (operator-local UI state).
- **R5 — Telegram auto-summary tool not loaded at session start** — soft compliance only per CLAUDE.md. Skip if `mcp__plugin_telegram_telegram__reply` not available.

### Verification recipe (smoke-test after each phase)

1. After each Phase B sub-phase: `git status` clean; `python <relevant>/update_dashboards.py` no regressions.
2. After Phase C: Library tests green; cross-repo sync command works.
3. After Phase D: Library + Mentor dashboards both clean; `_decisions/ingest-log.md` surfaces in Library's `health.md` Recent Ingest section.
4. After Phase E: all 10 ACs verifiable via direct file/dashboard inspection.

### Out of scope (deferred to post-S004)

- Other consumer wikis (Aviation / Tat / iSommelier / etc.) — bootstrap on v1.1 from start, no migration needed (greenfield)
- MI-12 (historical curation) — still carried
- OBS-1 (AC12 sweep methodology) — audit-method sprint TBD
- R-00008 cross-link surface expansion (M001 follow-up) — separate content sprint
- Spec line 881 outdated-claim correction — patch as part of E5 spec edit or carry to next maintenance pass

### Telegram auto-summary contract

Active per Library CLAUDE.md §"Telegram auto-summary contract" + Mentor's persona discipline. Soft compliance: if tool not loaded, log and continue.

---

## S002-codex-v1.1-update (2026-05-27) — Architect plan

### Goal

Ship the Codex v1.0 → v1.1 update arc on `spade0704/EMCC.Library`. Three converging inputs:

1. Session 1 deferrals (MI-10/11/12/13) and F-1/F-2/F-3 observations from S001 Auditor close.
2. Portfolio folder-structure spec (operator-signed-off via PR #3, 4 amendments applied) — Library restructures into `Biz.Automation/wikisys.library/_*` (system) + `wiki.codex/{git,local}/` (content) per F1–F12.
3. Mentor wiki report (2026-05-27): Mentor already bootstrapped 2026-05-25 as wiki #2 in `spade0704/Project-Mentor`; FINDING #1 parser bug + 5 Librarian patterns to codify.

S002 explicitly lifts Session 1's AC8 verbatim discipline: `bootstrap.py` code changes and Codex spec-doc edits are in scope for v1.1.

### Source-of-truth references

- Master plan: `/root/.claude/plans/check-the-dfdu-project-bubbly-knuth.md` Step 4 (Codex v1.1)
- Portfolio spec: `tasks/plans/portfolio-folder-structure-spec.md` (4-amendment-applied version on `main` post-PR-#3)
- Migration manifest: `REORGANIZATION-INSTRUCTIONS.md` (machine-readable; rows ⏳ Pending S002 flip to ✅ Done in S002 as moves land)
- Mentor wiki report (search room, 2026-05-27): 4 canonical artifacts cited in `tasks/plans/portfolio-folder-structure-spec.md` "Mentor — Greenfield bootstrap (shipped 2026-05-25)" section
- Destination branch: `claude/codex-v1.1-S002-restructure`

### Operator decisions locked at Phase A

| # | Question | Locked answer |
|---|---|---|
| D1 | bootstrap.py scope (narrow path-lookups vs wide spec-c rewrite) | **WIDE** — full canonical-output rewrite per spec section (c) |
| D2 | Commit granularity (per-phase vs Session-1-style grouped) | **Per-phase** — 10 commits (A + B1–B10) |
| D3 | Auditor dispatch mechanism (inline Agent envelope vs file bus) | **Session-1-style** — Agent inline envelope; `.lattice/bus/` deferred |

### Sub-phase decomposition (B1–B10)

**B1. Pre-extraction prep** — commit 2
- `.gitignore` add `wiki.*/local/` if missing; verify `.lattice/`; prune stale `wiki.codex/_brain_dump/` rule (subsumed by `wiki.*/local/`); keep `wiki.codex/_dashboards/`, `_inbox/`, `_confidential/` rules.
- Baseline assertion: clean tree; record Session-1 baseline test count (615 / 611 pass / 3 fail / 1 skip).
- Capture move-plan dry-run inventory under §S002 "B1 move plan".

**B2. Module source → `Biz.Automation/wikisys.library/_*`** — commit 3
- `git mv _scripts/` → `Biz.Automation/wikisys.library/_scripts/`
- `git mv _template/` → `Biz.Automation/wikisys.library/_template/`
- `git mv _config/` → `Biz.Automation/wikisys.library/_config/`
- Verify rename detection via `git log --follow` on a sample moved file.

**B3. Codex spec docs → `wiki.codex/git/codex/`** — commit 4
- `git mv` the 7 root-level spec docs (`CODEX_BUILD_SPEC_v1_3.md`, `CODEX_LIBRARIAN.md`, `INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`, `PROJECT_WIKI_BUILD_SPEC.md`, `Obsidian-Setup-Guide.md`, `codex-build-plan.html`) to `wiki.codex/git/codex/`.
- `git mv documents/codex/*` (3 files) to `wiki.codex/git/codex/`.
- Remove empty `documents/codex/` and `documents/` shells.

**B4. wiki.codex/ internal restructure** — commit 5

Content side (P5 — under `git/`):
- `wiki.codex/{Home.md,00-Start-Here,01-Architecture,02-Operations,04-Contributing,Attachments,public,scripts}` → `wiki.codex/git/`

System side (P1 — merges into `wikisys.library/`):
- `wiki.codex/{_canon,_config,_context,_decisions,_dashboards}` → `Biz.Automation/wikisys.library/`
- `wiki.codex/_scripts/` (if non-empty) → `Biz.Automation/wikisys.library/_scripts/` (merge)
- `wiki.codex/{_inbox,_confidential}` STAY as wiki-internal artifacts (legacy; superseded by `local/` but kept until Librarian migrates content)

Sources (P3 merge):
- `Sources/Raw/` + `wiki.codex/_sources/raw/` → `wiki.codex/git/raw/`

Private (P4):
- `wiki.codex/_brain_dump/` → `wiki.codex/local/ideas/`

**B5. bootstrap.py full canonical-output rewrite per spec (c) + path-lookup updates** — commit 6

Path-lookup updates (foundation):
- `bootstrap.py:59-62` `_resolve_source_scripts_dir()` → `Biz.Automation/wikisys.library/_scripts`
- `bootstrap.py:111-114` `_resolve_template_dir()` → `Biz.Automation/wikisys.library/_template`
- `_scripts/_lib/config_loader.py`: rebase `_config/` discovery to `Biz.Automation/wikisys.library/_config/`
- `_scripts/sync_from_kit.py`: source roots → `Biz.Automation/wikisys.library/_*`

Canonical-output rewrite:
- Drop Lattice-2.0-flavored `WIKI_FOLDERS` constant
- Add `CANONICAL_FOLDERS_FULL`, `_MINIMAL`, `_CODE`, `_WEBSITE` per spec (c)
- CLI: `bootstrap.py <projectname> [--minimal | --code | --website | --full] [--dry-run] [--yes]`
- Interpolate `wikisys.<projectname>/` + `wiki.<projectname>/` from positional
- Stub generators: `_emit_stub_claude_md`, `_emit_stub_index_md`, `_emit_stub_tasks`, `_emit_stub_cheatsheet`, `_emit_stub_gitignore` (mode-aware)
- Post-bootstrap checklist to stdout per spec (c)

Test refresh:
- `tests/test_phase6_full_chain_e2e.py` invariants revalidate against new tree
- New tests: `test_bootstrap_canonical_full.py`, `_minimal.py`, `_code.py`, `_website.py`, `_idempotency.py`, `_outside_cwd.py`

Validators (P4–P18): all 15 must pass against new tree; adjust validator configs as needed.

**B6. 5 new audit scripts + FINDING #1 parser fix** — commit 7

FINDING #1 fix:
- `Biz.Automation/wikisys.library/_scripts/_lib/frontmatter.py::parse_config_yaml` extends to 3-level nesting; 4+ level stays out of scope (raises explicit error)
- New regression fixture `tests/fixtures/yaml/mentor_topics.yaml`
- New test `tests/test_frontmatter_three_level_nesting.py`

5 new scripts under `Biz.Automation/wikisys.library/_scripts/`:
1. `audit_doc_pairing.py` (P0) — finds unpaired `Biz.Automation/<name>/` vs `wiki.<name>/git/<name>.doc/`; outputs `_dashboards/doc-pairing.md`
2. `audit_gitignore.py` (P0) — verifies `wiki.*/local/`, `Local/`, heavy-asset patterns; outputs `_dashboards/gitignore.md`
3. `route_inbox.py` (P0; two-phase scan + execute) — enumerates `0-Inbox/`, emits `route_candidates.json` for Librarian; agent fills destinations; script executes moves
4. `audit_assets.py` (P1) — heavy-file scan + dup detection; outputs `_dashboards/assets.md`
5. `audit_local_split.py` (P1) — misclassification suspects in `local/` vs `git/`; outputs `_dashboards/local-split.md`

Each ships with `tests/test_<name>.py` (happy + 2 error paths). All read `REORGANIZATION-INSTRUCTIONS.md` patterns for old-path detection.

**B7. CODEX_LIBRARIAN.md extension + Librarian persona update + Mentor pattern codification** — commit 8

Three new canonical Librarian operations (per spec d Changes 1–3 + 5):
- **Inbox-Sort** — classify `0-Inbox/` drops by destination zone (wiki / tasks / assets / website / code). Driven by `route_inbox.py scan` manifest.
- **Pairing-Audit** — every `Biz.Automation/<name>/` paired with `wiki.<name>/git/<name>.doc/`. Driven by `audit_doc_pairing.py`.
- **Cross-Project-Scan (Phase 2 stub)** — read sibling project wikis via EMCC orchestration. STUB ONLY in S002; full implementation = S004+.

Five Mentor-pattern codifications:
- **SPLIT (entity-vs-content)** — separate canon facts from page bodies
- **Style-Guide / INGEST / LINT verbatim + project-addenda** — `_context/_addenda.md` per-project override
- **`Home.md` NEVER-touched-by-Sync** — Sync-precedence table extends
- **Atomic paired writes** — page + index + archive trio (Ingest); page + canon + cross-link trio (canon promotion)
- **`max_links_per_page` per-project override** — knob in `_config/cross_link.yaml`

Persona file (`.claude/personas/CLAUDE.librarian.md`) mirrors with summary + pointer to canonical at `wiki.codex/git/codex/CODEX_LIBRARIAN.md`.

**B8. REORGANIZATION-INSTRUCTIONS.md manifest flip** — commit 9
- Every B2/B3/B4 move row: Status `⏳ Pending S002` → `✅ Done in S002`
- New §"S002-internal callers updated" — logs every bootstrap.py / sync_from_kit.py / config_loader.py / test fixture edit landed in B5

**B9. module.json bump + README + CLAUDE.md path-migration + MI-* resolution** — commit 10
- `module.json` v1.0.0 → v1.1.0
- README.md refresh for canonical layout + Quick-start
- CLAUDE.md insert §"Path migrations" pointer between "Required reading" and "ROOT_INDEX"; ROOT_INDEX rows refreshed
- MI-10 resolve (generalize persona drop-in test); MI-11 resolve (repoint to `wiki.codex/git/codex/*.md`); MI-12 carry (S004+ curation); MI-13 resolve-as-drop (stdlib only; no wheel distribution)

**B10. Auditor dispatch + verdict + Session 2 close** — commit 11
- Agent tool dispatch, `subagent_type: general-purpose`, fresh context
- Persona content: `EMCC.DFDU/personas/CLAUDE.auditor.md` embedded
- Audit envelope: this plan + AC1–AC12 + 10-commit summary + test results + synth bootstrap validation + manifest delta + MI dispositions
- Auditor NO-READ enforced structurally by persona; dispatch prompt does NOT re-paraphrase
- Verdict integration into Session 2 CLOSED entry in `tasks/sessions.md`

### Acceptance criteria (AC1–AC12)

- **AC1.** Session 2 OPEN entry + plan banked + Mentor spec corrected — Phase A complete
- **AC2.** `.gitignore` ready; baseline test count recorded; clean tree at B1 entry
- **AC3.** Module source moved with `git mv` history preservation (B2)
- **AC4.** All 10 spec-doc files at `wiki.codex/git/codex/`; `documents/` gone (B3)
- **AC5.** `wiki.codex/{git,local}/` populated; `Biz.Automation/wikisys.library/_*` shows all underscore folders (B4)
- **AC6.** `python bootstrap.py /tmp/v1.1-mentor --full` produces exact tree per spec (c) lines 864–895 (B5)
- **AC6b.** `--minimal | --code | --website` emit expected sub-trees (B5)
- **AC6c.** Old `bootstrap.py /tmp/target` invocation form rejected with migration error (B5)
- **AC7.** FINDING #1 reproducer parses clean; 5 new scripts ship green; each emits valid dashboard markdown against Library's own tree (B6)
- **AC8.** `CODEX_LIBRARIAN.md` extends + persona mirrors (B7)
- **AC9.** Manifest current; S002-internal callers section added (B8)
- **AC10.** v1.1.0 + README + CLAUDE.md path-migration + MI-10/11/12/13 dispositioned (B9)
- **AC11.** Auditor verdict `pass` (or `concerns` with documented inline resolution) recorded (B10)
- **AC12.** `git grep` sweep for stale paths returns 0 hits outside migration-trail docs (B10)

### Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| `bootstrap.py` rewrite breaks Session 1 phase-6 self-test invariants | Medium | B5 includes test-suite refresh; spec-c canonical tree drives the assertions |
| `git mv` rename detection fails on a few files | Low | Mechanical moves preserve content byte-equal; threshold not hit |
| FINDING #1 fix changes existing 2-level behavior | Low-Medium | Existing 2-level tests stay green; new tests cover 3-level adds |
| Auditor flags MI-* dispositions as concerns | Medium | Document each disposition with explicit "why this choice"; AC10 covers Auditor sightline |
| Validator config drift after `wikisys.library/_config/` merge | Medium | B4 explicit merge step; B5 includes validator re-run against new tree |
| `bootstrap.py` CLI breaking change (`<target>` → `<projectname>`) is downstream-breaking | Low | Library currently has zero downstream consumers depending on `<target>` form; document in commit body + README |

### Telegram auto-summary — Option B (Stop hook) deferred to v1.2

S002 ships Option A (persona-instruction discipline) — see Phase B7
commit + `wiki.codex/git/codex/CODEX_LIBRARIAN.md` §"Telegram
auto-summary contract" + `.claude/personas/CLAUDE.librarian.md` +
project-root `CLAUDE.md`.

**Option B trigger:** if compliance audits show >20% of meaningful
turns missing the summary call, escalate to Option B.

**Option B mechanism:** install a Claude Code Stop hook (in
`.claude/settings.json` or equivalent) that fires at every Stop
event and runs a 1-line summary directly (bypasses persona
discipline; mechanical). Hook reads the last assistant message,
extracts a 2-4 line synopsis, calls
`mcp__plugin_telegram_telegram__reply`. Tradeoffs: more reliable
delivery but more architectural surface (hook config + summary
extraction logic + per-project portability).

**Decision criteria for v1.2:**
- Compliance rate from S002-S003 sessions logged via
  Telegram delivery receipts.
- Operator feedback on auto-summary signal quality.
- Whether Stop hook integration would be reusable across projects
  (not just Library) — i.e. whether the hook config belongs in
  `EMCC.DFDU/documents/lattice/` as a portfolio-wide pattern.

### S002 Auditor observations (audit-codex-v1.1-2026-05-27-001, verdict `pass`)

The Auditor (general-purpose Agent dispatch, fresh context; 116-line CLAUDE.auditor.md persona embedded) returned verdict `pass` with 4 info-level observations. Dispatch SHA: this session's B10 commit. No `concerns` or `blocking` findings; no Karpathy principle violations identified; no Level-2 surface mismatch.

| # | Severity | Disposition |
|---|---|---|
| **OBS-1** | info | **RESOLVED (Post-S004 carry-closure, 2026-05-28)**: structural enforcement landed as `audit_doc_pairing.py --stale-paths` — corpus scan for old-layout path fragments with an explicit allow-list (`_config/stale_paths.yaml`; migration-trail/planning docs + pattern-definition files exempt). Repo-guard test asserts 0 un-allowlisted hits. Replaces the under-counting manual `git grep`. |
| **OBS-2** | info | **Fixed inline (this B10 commit)**: REORGANIZATION-INSTRUCTIONS.md §245 `import librarian, pathlib` example was inert (Library not on PyPI / not packaged). Rewrote the consumer-project pointer to reference vendored / submodule / sibling-checkout resolution. MI-13 cross-link added. |
| **OBS-3** | info | **Fixed inline (this B10 commit)**: README.md added §"v1.1 known limitations" surfacing the sync_from_kit-broken-against-v1.1-bootstrap chain (MI-16) + the no-packaging-artifact caveat (MI-13). Consumer-facing surface now accurately reflects v1.1 carry. |
| **OBS-4** | info | **RESOLVED (Post-S004 carry-closure, 2026-05-28)**: chose build-time generation (Karpathy Structural-over-Advisory). `.claude/personas/CLAUDE.librarian.md` is now generated from the canonical `wiki.codex/git/codex/CODEX_LIBRARIAN.md` by `generate_persona_dropin.py` (generated fm + DO-NOT-EDIT banner + canonical body verbatim; `last_updated` sourced from canonical → deterministic). `tests/test_persona_dropin.py` fails CI on drift. Mirror drift now structurally impossible. (Content-side bootstrap drop-in `wiki.codex/git/.claude/personas/CLAUDE.librarian.md` remains a `bootstrap.py` concern — see todo.md.) |

Auditor envelope content preserved in B10 commit body (Session 1 precedent — Library bus root deferred; envelope captured in-commit-message-trail rather than written to `.lattice/bus/outbox/`).

### Deferred to S004+ (NOT in S002 scope)

- Phase-2 Librarian Cross-Project-Scan full implementation (only stub lands in B7)
- B4 historical `tasks/*` + `CHANGELOG.md` curation (MI-12 carry)
- `pyproject.toml` decision revisit (MI-13 resolved as drop; revisit only if Library ever distributes as wheel)
- DFDU-style flat `personas/` layout reconciliation (Session 1 `.claude/personas/` decision stands; org-wide reconciliation = future)
- Real consumer-project bootstraps (Aviation / Tat / etc. per portfolio spec section (b) §"Project list" rows 3–9) — S004
- DFDU's own `wiki/` bootstrap — master plan Step 7 / S005
- Telegram channel boot — S003

### Auditor dispatch plan (B10)

- **Trigger basis:** schedule (sprint close at v1.1 implementation completion) + risk (Level-2+: ~150 file moves + bootstrap.py rewrite + 5 new scripts + spec/persona changes)
- **Mechanism:** Claude Code Agent tool dispatch using `subagent_type: general-purpose`, fresh context
- **Persona:** `EMCC.DFDU/personas/CLAUDE.auditor.md` (116-line canonical) embedded verbatim in dispatch prompt
- **Audit envelope payload:**
  - `audit_id`: `audit-codex-v1.1-2026-05-27-001`
  - `regime`: B (persona, on-demand)
  - Architect plan reference (this §S002)
  - AC1–AC12
  - 10-commit summary (per-commit SHAs + 1-line subjects)
  - Test result summary (pre-S002 vs post-S002 count + pass/fail)
  - Synth bootstrap validation transcript
  - Manifest delta (B8)
  - MI-10/11/12/13 dispositions (B9)
- **Auditor NO-READ:** enforced structurally by persona file; dispatch prompt does NOT re-paraphrase the rule.
- **Verdict integration:** written to Session 2 CLOSED entry in `tasks/sessions.md`; envelope content preserved in this §S002 in a "B10 audit result" subsection at session close.

---

## S001-codex-extraction (2026-05-27) — Architect plan

### Goal
Extract Codex (Librarian protocol) from `spade0704/project-codex` to this repo. **Mechanical relocation only**; spec changes deferred to a follow-up "Codex v1.0 → v1.1 update" session (master plan Step 4).

### Source-of-truth references
- Master plan: `/root/.claude/plans/check-the-dfdu-project-bubbly-knuth.md` (operator-approved 2026-05-27)
- Source repo HEAD at session start: `ccf21b7` on `spade0704/project-codex@main` (S048-session-close, 2026-05-25)
- Destination branch (this repo): `claude/lattice-3-production-check-Rdkfu`
- DFDU production-ready stamp: Session 8 / `f056f81` (2026-05-27)

### Goes/stays inventory (locked)

**GOES → EMCC.Library:**

| # | Path in project-codex | Kind |
|---|---|---|
| G1 | `bootstrap.py` | Codex entry |
| G2 | `CODEX_BUILD_SPEC_v1_3.md` | Spec (single canonical per locked decision; v1_1/v1_2 stay as historical archive) |
| G3 | `CODEX_LIBRARIAN.md` | Librarian agent spec |
| G4 | `INGEST_PROCEDURE.md` | Doctrine (verbatim) |
| G5 | `SEMANTIC_LINT_PROCEDURE.md` | Doctrine (verbatim) |
| G6 | `PROJECT_WIKI_BUILD_SPEC.md` | Wiki build spec |
| G7 | `Obsidian-Setup-Guide.md` | Consumer guidance |
| G8 | `_scripts/` minus 3 lattice-2.0 scripts (see A1) | Automation |
| G9 | `_template/` (26 wiki template files) | Templates |
| G10 | `_config/` (5 YAML + README) | Config |
| G11 | `tests/` minus 5 lattice-2.0 tests (A1 only; A2 revoked — see ambiguities section) | Test suite (~821 tests; refined count established in B5) |
| G12 | `documents/Codex_Project_Documentation.pdf` | Doc |
| G13 | `documents/Codex_Workflow_Cheatsheet_v1.txt` | Cheatsheet |
| G14 | `documents/codex-build-progress.md` | Build progress log |
| G15 | `codex-build-plan.html` | Build plan |
| G16 | `.claude/personas/CLAUDE.librarian.md` | Persona |
| G17 | `Sources/Raw/` | Source-archive convention root (currently README only) |
| G18 | Codex-class entries curated from `tasks/{lessons,architect-notes,sessions,auditor-notes}.md` | Curated migration |
| G19 | `tasks/v1.1-backlog.md` | Codex v1.1 backlog |
| G20 | Codex-class entries curated from `CHANGELOG.md` | Curated migration |

**STAYS in project-codex (archive):**

`CLAUDE.md` (rewritten as archive banner), `README.md` (rewritten as archive banner), all 7 `LATTICE_v0.*_SPEC.md` files, `CODEX_BUILD_SPEC_v1_1.md` + `v1_2.md` (historical), `PROJECT_INDEX.md`, `documents/lattice/` (13 files), `.claude/personas/{architect,auditor,craftsman,scribe}.md`, `.claude/settings.json`, `tasks/lattice-extraction-tracker.md`, `tasks/{lessons,architect-notes,sessions,auditor-notes}.md` (post-curation residue), `tasks/todo.md` (with strikethroughs), `tasks/archive.md`, `0-Inbox/`, `.gitignore`, plus the A1/A2 carry below.

### Ambiguities flagged (audit gate)

**A1.** `_scripts/lattice-bridge.py`, `_scripts/lattice_session_start.py`, `_scripts/lattice_valid_roles_audit.py` + their 5 tests (`test_lattice_bridge*.py`, `test_lattice_session_start.py`, `test_lattice_valid_roles_audit.py`) are Lattice 2.0, not Codex. **Decision: STAY** in project-codex archive.

**A2.** ~~`test_phase6_full_chain_e2e.py` and `test_steel_thread_tracker.py` — Phase 6 / steel threads were Lattice 2.0 tactical work, not Codex.~~ **REVOKED in Phase B3 verification.** Re-reading the actual files: `steel_thread_tracker.py` is Codex's P14 script per `CODEX_BUILD_SPEC_v1_2.md §2.4 row 11` (also v1.3); `test_phase6_full_chain_e2e.py` is Codex's spec §7 Phase 6 self-test invariant verifier (bootstrap + sync + scaffolds + Librarian wiring assertions). Both are CODEX, not Lattice tactical. **Revised decision: BOTH GO to Library.** Naming overlap ("phase 6" appears in both Codex's roadmap and Lattice 2.0's bridge dogfood; "steel threads" is a generic-enough term that I mistook it for Lattice 2.0's concept) caused the initial misclassification. Lesson logged after session close.

**A3.** **VERIFY (in Phase B1)** that `bootstrap.py` and the remaining Codex `_scripts/` have no Python imports from A1's three lattice-2.0 scripts before removing them from the GOES set. If imports exist, either fold the import target into Codex (rename to remove "lattice" prefix) or leave the dependency edge as a documented carry.

### Sub-phase decomposition

**B1. Pre-extraction prep.**
- Rename `0. Inbox/` → `0-Inbox/` (locked canonical naming) — done in Phase A
- A3 cross-module import verification: grep `bootstrap.py` + all GOES `_scripts/` for `import lattice_` / `from lattice_` / `lattice-bridge` / `lattice_session_start` / `lattice_valid_roles_audit` references; document findings
- Create `pyproject.toml` (declares `librarian` package + DFDU as dev dep for protocol-following)
- Extend `.gitignore` with Codex test artifacts (`tests/fixtures/source_delta/`, etc., per project-codex pattern) + bus state if added later

**B2. Bootstrap files.**
- `CLAUDE.md` (light version — points at DFDU canon, declares this as a consumer of DFDU AND a producer of Codex)
- `module.json` (mirrors DFDU pattern; `module_type: protocol-wrapper`; `produces_for: [...]`; `consumes: [DFDU]`)
- `SOURCE-HISTORY.md` (pointer to project-codex SHA `ccf21b7`; date; license carry)
- `MIGRATION-ISSUES.md` (append-only registry header; references DFDU's MI-01..MI-08 convention)
- `README.md` (replace not-ready placeholder with production-ready text)
- `.github/workflows/test.yml` (matches DFDU pattern: pytest + python 3.11; pinned `actions/checkout@v4` + `actions/setup-python@v5`)
- `requirements.txt` + `requirements-dev.txt` (Codex's actual runtime + dev deps — read from project-codex test imports if no manifest exists)
- `personas/CLAUDE.auditor.md` (copy from DFDU verbatim — same 116-line file)
- `personas/CLAUDE.librarian.md` (G16 — copy from project-codex `.claude/personas/`)
- `TIERS.md` (optional — only if Codex has Subagent-N analogue; deferred to Phase B2 if not)

**B3. Relocate G1–G17.**
- Copy files from project-codex to corresponding Library paths (mechanical; preserves layout aside from inbox rename)
- For root-level docs (`G1, G2, G3, G4, G5, G6, G7, G15`), destination = Library root (matches project-codex layout)
- For `_scripts/`, `_template/`, `_config/`, `Sources/Raw/`: destination = same relative path
- For `tests/`: destination = same; rewire any hardcoded `project-codex/` paths (likely none — Codex was designed path-agnostic)
- For `documents/Codex_*`: destination = Library `documents/codex/` (new sub-directory for Codex docs)
- For G16 persona: destination = Library `personas/CLAUDE.librarian.md` (no `.claude/` nesting — matches DFDU's flat `personas/` pattern)
- Record source SHA + per-file destination in `SOURCE-HISTORY.md`
- Wiki dogfood note: existing `wiki.codex/` stays in current location and layout (operator decision; F7/F8 folder restructure happens in Step 4)

**B4. Curated migration: tasks/* + CHANGELOG.**
- For each of project-codex's `tasks/{lessons,architect-notes,sessions,auditor-notes}.md`: extract Codex-class entries (anything tagged with codex/librarian/ingest/wiki concerns) → append to Library's corresponding `tasks/` files; leave Lattice-class entries in project-codex
- For `tasks/v1.1-backlog.md` (G19): full move (it's Codex-only)
- For `CHANGELOG.md` (~337KB): extract Codex-class lines → new `CHANGELOG.md` at Library root with timestamps preserved; Lattice-class lines stay in project-codex's CHANGELOG
- Curation criterion: anything that references Codex agent spec / bootstrap / ingest / semantic lint / template / config / spec versions is Codex-class. Lattice 2.0 (bridge, session_start, valid_roles_audit, steel_thread, telegram_l1_l2, scribe spec, etc.) is Lattice-class.

**B5. Test infrastructure rewire + pytest green.**
- Run `pytest tests/` from Library root post-relocation
- Expected count: ~821 (826 − 5 lattice-bridge − ? lattice-tactical, refined during B3)
- Fix import paths if any test references `project-codex/...` directly (likely zero — verify)
- Add `tests/__init__.py` if needed
- Tests must pass before B6

**B6. Synthetic wiki bootstrap validation.**
- Run `python bootstrap.py /tmp/extraction-validation-wiki` from Library root
- Verify: scaffold succeeds; all dashboards build; all validators pass with 0 errors
- This validates end-to-end Codex still works after extraction

**B7. EMCC consumer template flip (cross-repo edit on EMCC's branch).**
- Edit `EMCC/templates/consumer-project/emcc.modules.json`: `library.status` `"not-ready"` → `"ready"`
- Commit on `claude/lattice-3-production-check-Rdkfu` in EMCC repo

**B8. project-codex archive disposition (cross-repo edits on project-codex's branch).**
- Replace `CLAUDE.md` content with archive banner pointing at EMCC.Library + EMCC.DFDU
- Replace `README.md` content with archive notice
- Apply strikethroughs to `tasks/todo.md` items now done by Library
- Commit on `claude/lattice-3-production-check-Rdkfu` in project-codex repo

**B9. Auditor dispatch + verdict + Session 1 close.**
- Construct `audit_request` payload: this architect plan + acceptance criteria + post-extraction artifact summary (file moves, test count, bootstrap synth validation result)
- Build prompt via DFDU's `build_auditor_prompt` helper (importable from `EMCC.DFDU/scripts/lattice_scripting/audit/dispatch_adapters.py`)
- Dispatch Auditor via Claude Code Agent tool with fresh context
- Read `audit_result`; record verdict + findings in Boris log Session 1 close entry
- If `pass`: close Session 1
- If `concerns`: address each; re-dispatch if needed; close on `pass`
- If `block`: surface to operator; do not commit final state

### Acceptance criteria (AC1–AC8)

- **AC1.** All G1–G20 items relocated to Library. ~821 tests pass post-relocation (refined count established in B5).
- **AC2.** `python bootstrap.py /tmp/synth-wiki` succeeds from Library root; synthetic wiki passes its own validators with 0 errors.
- **AC3.** Library has full module-level bootstrap: `CLAUDE.md`, `module.json`, `tasks/{todo,sessions,architect-notes,lessons,archive}.md`, `SOURCE-HISTORY.md`, `MIGRATION-ISSUES.md`, `pyproject.toml`, `.github/workflows/test.yml`, `personas/CLAUDE.{auditor,librarian}.md`.
- **AC4.** `INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md` byte-equal between project-codex source and Library destination (verbatim discipline preserved). Verify via `diff` after B3.
- **AC5.** EMCC `templates/consumer-project/emcc.modules.json` Library status flipped `not-ready` → `ready`.
- **AC6.** project-codex archive banners applied to `CLAUDE.md` + `README.md`; `tasks/todo.md` Library-related items struck through with reference to Library Session 1.
- **AC7.** Auditor verdict on extraction: `pass` (or `concerns` with documented resolution + re-audit `pass`).
- **AC8.** No Codex spec content changes during extraction — pure relocation. Any spec edits required for relocation paths (e.g., `_scripts/` path references in `CODEX_BUILD_SPEC_v1_3.md` if any) are flagged for Step 4 follow-up rather than edited mid-extraction.

### Auditor dispatch plan

- **Trigger basis:** schedule (sprint close at extraction completion) + risk (Level-2+ cross-repo + 50+ file moves + new module ship)
- **Mechanism:** Claude Code Agent tool dispatch using fresh context. If `EMCC.DFDU.scripts.lattice_scripting.audit.dispatch_adapters.build_auditor_prompt` is importable from the session env, use it verbatim. Else inline-construct an equivalent prompt that includes: Auditor persona content + audit_request payload + envelope-writing instructions per §4.
- **Auditor persona content:** `EMCC.DFDU/personas/CLAUDE.auditor.md` embedded in dispatch prompt (canonical 116-line version)
- **Audit envelope payload includes:**
  - This architect plan §S001
  - AC1–AC8
  - File-by-file move summary (source SHA + destination path for each G1–G20)
  - Test result summary (count + duration + zero-regression confirmation)
  - Bootstrap synth validation transcript
  - Cross-repo summary (B7 + B8 commits)
- **Verdict integration:** Written to Boris log Session 1 close entry; full envelope content saved in `tasks/architect-notes.md` §S001-audit-result section

### Deferred to Step 4 (Codex v1.0 → v1.1 update session)

- Operator's portfolio-room refined folder-structure spec (resolves F1–F11; drives `Biz.Automation/wikisys.<projectname>/` vs `wiki.<projectname>/` split for consumer wikis)
- Mentor wiki report findings
- 5 deferred Librarian-spec items from EMCC `tasks/todo.md` (TF-IDF cross-link curation, routing tag work queue, Maintenance loop tag-scan, three-tier tag namespace authority, plug-in failure handling)
- S048-T1 findings from project-codex (if/when that sprint closes)
- Spec edits surfaced during AC8 (path references, etc.)
- Library's own dogfood wiki rebuild under new folder layout
- Bus infrastructure for Library's own Lattice 3.0 sessions (if Library becomes its own Lattice 3.0 client beyond ad-hoc dispatches)
