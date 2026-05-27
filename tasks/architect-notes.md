# Architect Notes — EMCC.Library

> Active scope notes, open threads, deferred decisions. Auditor MAY READ this for scope context (per `EMCC.DFDU/personas/CLAUDE.auditor.md` allow-list — `tasks/lessons.md` and `tasks/plans/` are off-limits; this file is not).

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
