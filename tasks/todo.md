# Task Backlog — EMCC.Library

> Newest sprint at top. Older sprints rolled to `tasks/archive.md` once their work is complete.

## Sprint — Readiness cascade dir-ii/hh/jj (DONE 2026-06-14b; all merged)

Gate `tasks/delta-force/delta-force-20260614-092532.md`; Auditor Regime B PASS. Scores reconciled live.

- [x] **lib-codex 90→92** — report-only `audit_citations` wired into the orchestrator (failure-isolated, no health-section, own dashboard) + tests. PR #48.
- [x] **lib-librarian — CAPPED 85** — honest cap (Cross-Project-Scan blocked on EMCC orchestrator; at-scale curation needs live LLM runtime).
- [x] **mentor-wiki 75→77** — surgical orphan link (PR #17).
- [x] **dfdu-wiki 22→48** — Project-Overview + Glossary (18 terms) + orphan link (PR-merged).
- [x] **iso-wiki 20→38** — orphan link (PR #42).
- [x] **emcc-wiki 25→50** — patch handed to Director, applied on EMCC main (300ab02/2b85c0b); `tasks/patches/emcc-wiki-fill-dir-jj.md`.
- [x] **Inbox-Triage.md (EMCC tree)** — 1-line inline-conversion patch handed to Director (block-list `canon_sources` → inline; same sources).
- [ ] **🔴 Codex engine bug (gated): YAML-subset parser drops block-list sequences.** `canon_sources:` (and any block seq) with `- item` lines parses to `None`. `validate_canon_integrity` only checks `ready` pages, so block-list `canon_sources` on solid/outlined pages is silently ignored and fails on promotion to `ready`. Fix = teach `_lib/frontmatter` block sequences OR ship an inline-only lint (+ migrate existing block-list frontmatter). Level-2+ (Syncs to all consumers) → delta-force + Auditor. Surfaced by EMCC `Inbox-Triage.md`.

## Sprint — Readiness cascade dir-20260614n (BUILT 2026-06-14; MERGED via PR #47)

Director cascade `dir-20260614n-readiness-library` (req `96acbc3a`). Gate `tasks/delta-force/delta-force-20260614-061339.md` (DFTS=8). Auditor Regime B: PASS. Branch `claude/readiness-lib-wiki-summary-op-20260614` @ `583fab3` — **operator human-at-merge; scores bump on merge.**

- [x] **lib-wiki 45→70** — self-wiki validators 50 broken + 13 orphans → 0/0: P9 full-path cross-ref resolution (+dup-stem guard), list-aware indented-code strip (clears verbatim-doc false-positives without editing), populated Glossary (16 terms), Home protocol-canon links, CODEX_LIBRARIAN canon_sources. +9 tests.
- [x] **lib-summary-op 55→68** — canonical `_scripts/summarize.py` (extractive default + injectable LLM seam, honestly named, faithfulness guarantee). +16 tests.
- [ ] **🔴 LLM-seam unlock (operator-gated; raises both toward 80).** lib-summary-op → 80 needs a consumer to wire a real `summarize_fn` (EMCC `librarian_summarize.py` is the seam — currently no-op without an LLM). Logged Director-side as a top systemic unlock alongside backend-hosting.
- [ ] **⚪ lib-wiki deeper link-graph-integrity layer** (beyond cross-refs) for the path from 70 → 80.
- [ ] **⚪ Cleanup: 2 pre-existing `test_sync_from_kit` TestSyncStamp failures** — Windows CRLF/git-state churn (NOT from this work); confirmed on clean tree. Candidate for the CRLF sweep.

## Sprint — Codex v1.3.1 cross-link at scale (BUILT 2026-06-13b)

Surfaced by the Aviation consumer; plan `0-Inbox/PLAN-cross-link-promotion-2026-06-13.md`. Opt-in defaults = v1.3 byte-identical. Committed `4dce454`. Independent Auditor: SHIP-WITH-FIXES (fixes applied).

- [x] **P18.3 See-also cap + ranking** — `see_also.max_links_per_page` (0=uncapped) wired into `cross_link_topics.py` with shared-topic/cross-container/path ranking. Fixes the dead `max_links` config.
- [x] **Duplicate-stem disambiguation** — `see_also.disambiguate_duplicate_stems` → path-qualified links on wiki-wide stem collision; spec §2.7 amended.
- [x] **`backfill_topics.py`** — generic bulk topic tagger (path + keyword) for retrofitting pre-existing wikis; inline+block-list `topics:` safe (additive). Template config shipped. +tests (suite 690→720).
- [x] **`CODEX_LIBRARIAN.md` v1.3.1 op** (two-linker distinction, cap, dup-stem, granularity, backfill) + regenerated drop-in. Plugin marked EXPERIMENTAL/not-wired in spec + config.
- [ ] **⚪ Wire the plugin hook end-to-end (or remove it).** `load_plugin`/`blend_results` exist but the `build_topic_index.py` run path never calls them.
- [ ] **⚪ Add dotted-code section-topic derivation to `backfill_topics.py`** so Aviation can drop its local `stamp_topics`/`cross_link` forks and Sync the kit instead.
- [ ] **⚪ Full dry-Sync zero-diff check to DFDU/Mentor** (deferred — sync-stamp tests env-broken on this box; covered indirectly by no-consumer-opt-in grep + default-config test).

## Sprint — boilerplate-location convention (RATIFIED + BUILT 2026-06-11)

- [x] **Operator ratified** `tasks/plans/boilerplate-location-spec-proposal.md` (§2 split + §3 Option A) — 2026-06-11.
- [x] **Built** under the gate `EMCC.DFDU/tasks/delta-force/2026-06-11-boilerplate-stub-build.md`: 4 protocol templates -> stubs (canonical pointer + summary; frontmatter parity); `demote_boilerplate_stubs.py` one-off (body-only guard, git-history baseline at pinned `08d87ac`, structural codex exclusion, dry-run); spec amendment in `PROJECT_WIKI_BUILD_SPEC.md` §"Boilerplate location"; canonical-copy notes on the 4 `wiki.codex` pages; `materialize_boilerplate.py` docstring. Suite 666 -> 678 (6 skipped). Migration run across the wave consumers EMCC-side.

## Sprint — M-A structural Sync build, Library half (CLOSED 2026-06-11 — ALL components shipped + merged)

Gate: `EMCC.DFDU/tasks/delta-force/2026-06-10-ma-structural-sync.md`. Branch `claude/emcc-ma-build-p7ohln` (pushed; no PRs — operator disposes). Session record: `tasks/sessions.md` 2026-06-10b + EMCC `tasks/sessions.md` 2026-06-10g.

- [x] **Component 1 — dead-regex example fix** (`da16ecf`): single-backslash examples in `_config/forbidden_terms.yaml` + `reveal_leak_patterns.yaml`; convention in `_config/README.md` + `PROJECT_WIKI_BUILD_SPEC.md` §2.5; negative-control tests welded to the shipped examples. Auditor PASS.
- [x] **Component 2 — SYNC-STAMP.json** (`260d6c7` + `9f3ff95`): `_write_stamp` dedicated final action; the stamp IS the manifest; all-OK only, never on `--dry-run`; dirty-kit WARN (audit fix). Auditor concerns→fixed.
- [x] **Component 4 docs** (`66a8e22`): `wiki.codex/git/codex/SYNC_STAMP_CONTRACT.md` canon + MI-20 (closes MI-19's version-staleness follow-up) + Index rows. Suite 644→655 (6 skipped). EMCC-side halves: `check_drift.py` + `emcc_wire._copy_librarian` (Lock 1).
- [x] **Component 5 — CARTO-06 materialize-then-link** (PR #42, merged 2026-06-11): `materialize_boilerplate.py` + bootstrap carve-out + canon note; Auditor concerns fixed (`d33921c`). Suite 666.
- [x] **Component 6 — consumer refresh wave** (2026-06-11, all 11 merged incl. tat/isommelier on explicit operator authorization): stamped kit `019168f` + materialize everywhere; first SYNC-STAMP.json portfolio-wide; check_drift verified + surfaced PERSONA-DRIFT follow-ups (emcc_wire re-cascade, EMCC-side).

## Inbound handoff — Cairn/Gateway reframe folds accuracy work into Library (2026-06-06)

Two EMCC.Gateway councils + a fidelity probe concluded the accuracy-critical
context work belongs in Library/Codex, NOT a separate module. Decision trail:
`EMCC/tasks/council/2026-06-06-cairn-v1.md`, `EMCC/tasks/council/2026-06-06-cairn-reframe.md`,
`EMCC.DFDU/tasks/delta-force/2026-06-06-cairn-phase0.md`,
`EMCC.Gateway/wiki.EMCC.Gateway/git/_spike/RESULTS.md`. Backlog to absorb (each its
own sprint; council/delta-force before building):

> **/llm-council verdict 2026-06-13** (`EMCC/tasks/council/2026-06-13-library-cairn-absorption-track.md`): **sequence 1 → 2 → 3, don't merge.** (1) **BUILD NOW** — highest safety-per-effort, near-free on the existing lint/audit base; ship the canon doc + ONE lint rule (flag any claim lacking a citation anchor), and **name the lint honestly as a citation-*presence* check** (it verifies a citation exists, not that the quote is verbatim or the refusal correct). (2) **next**, but make the **ambiguity-refuse/escalate default a definition-of-done precondition** (a keyword router that silently returns the wrong caution verbatim is *more* dangerous than none — citable + confident). (3) **do NOT fund the pipeline** — build a one-day throwaway read-only PROVER on the single FCTM doc (dedupe → reconstruct both variants byte-for-byte → retrieve correct per MSN); pass = a funding decision, not auto-build; note B's caution that once (1) cites verbatim with effectivity tags, duplicate bodies are harmless, so (3) may be storage not safety. Next build = item (1), delta-force-gated per Library convention.

- [x] **Verbatim-only / cite-always / correct-refusal** formalized as Codex canon
  (most consumer wikis' CLAUDE.md already declare a "never fabricate, cite source"
  rule — make it a first-class Codex policy + lint). *(BUILT 2026-06-13, /delta-force REVISE-AND-PROCEED → standalone audit, canon-first: contract locked in `Frontmatter-Schema.md` §"Accuracy fields" + `PROJECT_WIKI_BUILD_SPEC.md` §"Accuracy contract" (`consequence`/`cite_anchor`, fail-safe HIGH, HIGH⇒non-empty cite_anchor, "Presence-Not-Accuracy" caveat); the existing tested-but-unwired `doc_lint.check_consequence` wired into a new report-only `_scripts/audit_citations.py` (`--enforce` opt-in; standalone so it can't red-bar the full-tree gate). +11 tests green. NOTE: keeps the lint to citation-PRESENCE — it does NOT verify verbatim-ness/refusal-correctness.)*
- [ ] **Tiered caution-index**: an `index.md` improvement that surfaces a cheap
  decision/router layer + verbatim safety cautions, then loads full source on demand.
  Deterministic — NO neural picker in the safety path (grep/keyword search is the
  retriever).
- [ ] **Gated experiment — lossless effectivity-normalization** (dedupe repeated
  MSN/effectivity variants → canonical body + diff). Belongs in the wiki BUILD
  pipeline (single-writer), not a runtime module. KILL CRITERIA: must pass BOTH
  (a) byte-for-byte reconstruction of every variant AND (b) correct-variant
  retrieval at query time, or it's dropped. First real target:
  `aviation .../FCTM/PR/AEP/NAV/Unreliable_Airspeed_Indications.md` (prints ~the same
  procedure twice for two MSN ranges).

(EMCC.Gateway keeps the local LLM for LOW-consequence compression — transcripts,
logs, references, drafts — separate from this accuracy track.)

## Current sprint — Pre-S006 Aviation-prep (2026-05-28, IN PROGRESS)

Aviation pivot coordination + Library hygiene. See `/root/.claude/plans/before-we-go-to-warm-cocke.md` (operator-side plan file) for the full coordination plan.

### Done
- [x] **Orchestrator participation: Librarian cross-session addendum** (Session 11, 2026-06-03):
  `.claude/modules/claude-orchestrator.md` (Librarian-side cascade rules — role tag, directive handling,
  envelope logging, and **Codex gates still bind under the cascade**: sources upstream, canon writes need
  confirmation, INGEST/LINT verbatim, halt-loud on ambiguity) + `CLAUDE.md` Development-discipline pointer.
  Codex specs untouched; docs-only, tests unaffected. Branch `claude/lattice-cross-persona-messaging-ekVx8`;
  PR → merge → delete (paired with EMCC + DFDU). Canon: `spade0704/EMCC` → `framework/09-orchestrator-cross-session.md`.
- [x] **Codex canon: wiki updated every build session** (Session 10, 2026-06-02): Design Principle #14 +
  §7 Phase-4 requirement in `CODEX_BUILD_SPEC_v1_3.md` + `PROJECT_WIKI_BUILD_SPEC.md`; "Wiki Maintenance
  Behavior" section in the `CLAUDE_CONTEXT_RULES` template + "Per build session" in the `Update-Cascade`
  template. 631 tests still pass. (branch `claude/codex-wiki-per-session`).
- [x] Closed stale MI-17 carried entry (commit `109d42e`, branch `claude/gallant-bohr-ePBuX`).
- [x] **Per-project reorganization manifest convention** (v1.3 addendum, 2026-05-28):
  - `REORGANIZATION-INSTRUCTIONS.md` trimmed to master (patterns P1–P8 + audit hooks + cross-repo per-project index)
  - `reorganization-instructions.library.md` created at Library root with Session 1 + S002 + S003b moves
  - Mentor section extracted to `tasks/plans/cross-repo-pending/reorganization-instructions.mentor.md` pending cross-repo move on next Mentor session
  - Aviation seed staged at `tasks/plans/aviation-bootstrap-seed/reorganization-instructions.aviation.md` (operator copies to aviation/ root during Phase 1)
  - `bootstrap.py::_stub_reorganization_md` added; emits stub at root for --full / --code / --website modes (omitted in --minimal)
  - 2 new tests in `tests/test_bootstrap_canonical.py`; 606 tests still passing
  - Spec amended: `CODEX_BUILD_SPEC_v1_3.md` (v1.3 addendum + §4.2 NEVER-touched list), `tasks/plans/portfolio-folder-structure-spec.md` (canonical tree + variance allowance + per-folder purpose)
  - `CLAUDE.md` + `Index.md` updated to reference the master/per-project pair

### Open
- [ ] Operator: copy `tasks/plans/aviation-bootstrap-seed/reorganization-instructions.aviation.md` into aviation/ root after `bootstrap.py aviation --full --yes` lands (overwrites the bootstrap-emitted generic stub with the pre-populated seed).

## Reusable patterns — lifted from tat_app (2026-05-30, PR #21 MERGED)

First batch of cross-project engineering patterns generalized from the `tat_app` consumer during the TAT audit/modernization. Hosted at repo-root `patterns/` (Codex frontmatter format), **deliberately outside** `wiki.codex/git/` so the Codex self-canon stays pure and the cross-link orchestrator doesn't bleed app-domain topics into Codex's topic graph.

### Done
- [x] Authored 6 pattern pages + index in `patterns/`: Decision-Scoring, Opportunistic-Bundling, Offline-First-Sync, Soft-Delete-Signal-Preservation, AI-Memory-And-Insight-Extraction, Neurodivergent-First-UX. Frontmatter validated with the `_lib` parser; dogfood wiki byte-unchanged. (PR #21, squash `44d716e`)

### Open
- [ ] **Cartometrics/WYAI seed** — `patterns/Opportunistic-Bundling.md` is flagged as the consumer-level seed for the deferred EMCC.Cartometrics (WYAI) module. Fold it in when that module opens.
- [ ] **Graduation decision** — if/when these patterns earn their own first-class module (or a shared `emcc_flutter_kit` Dart package once a 2nd Flutter consumer exists), give them a dedicated wiki + canon. Until then they stay as `patterns/` docs.
- [ ] **Consumer-side carry (tat_app):** TAT's `Biz.Automation/wikisys.tat_app/_canon/roster.yaml` is still template-only, so the Codex `concept_coverage` check (P13) errors on the new TAT wiki. Populate it on the next TAT wiki session (tracked in tat_app `Tasks/todo.md`).
- [x] Mentor cross-repo move complete — manifest moved into Project-Mentor (commit `7ed7f30`, branch `claude/gallant-bohr-ePBuX`); Library staging copy deleted; master index flipped Mentor → Migrated.

## Past sprint — Post-S004 carry closure (2026-05-28, CLOSED)

Closed four post-S004 carried items in one maintenance sprint. 630 tests pass (+25 from S004's 605 baseline).

### Done
- [x] **MI-17 full closure** + **dashboard relocation** (coupled) — added `_lib/frontmatter.py::find_wiki_content_root()`; switched all 17 dashboard/validator scripts off the install-root `find_wiki_root()` so dashboards now land at `wiki.codex/git/_dashboards/` (gitignored) instead of leaking to repo-root `_dashboards/`, and page-walks scan only the content side. Added `_lib/cli.py::resolve_cli_wiki_root()` + a `--wiki-root` override (or bare positional) in every standalone P-script `__main__`. MI-17 marked RESOLVED in `MIGRATION-ISSUES.md`. (+10 tests)
- [x] **OBS-4** — `.claude/personas/CLAUDE.librarian.md` is now GENERATED from the canonical `wiki.codex/git/codex/CODEX_LIBRARIAN.md` via `generate_persona_dropin.py` (deterministic; `last_updated` sourced from canonical). `tests/test_persona_dropin.py` fails CI on drift. Drift is now structurally impossible. (+8 tests)
- [x] **OBS-1** — `audit_doc_pairing.py --stale-paths`: AC12 stale-path sweep with an explicit allow-list (`_config/stale_paths.yaml`); replaces the under-counting manual `git grep`. Repo-guard test asserts 0 un-allowlisted hits. (+7 tests)

→ See `tasks/sessions.md` for the close record and `tasks/architect-notes.md` §S002 for the updated OBS-1/OBS-4 dispositions.

## Past sprint — S004-mentor-v1.1-migration (2026-05-28, CLOSED)

Cross-repo sprint with `spade0704/Project-Mentor`. Mentor migrated v1.0 → v1.1 canonical layout; Library shipped MI-16 + MI-18 closures + walker fix + manifest update.

### Done (Library side)
- [x] Phase A — open Session 4 + bank architect plan §S004 + Mentor pre-migration anchor SHA
- [x] Phase C — `sync_from_kit.py` v1.1 contract rewrite (MI-16 closure); consumer-name auto-discovery; 17 tests pass + 4 new TestConsumerDiscovery cases; spec doc §4.2 updated
- [x] Phase D — MI-18 canon-lookup marker-walk: `_lib/frontmatter.py::find_canon_dir` + `find_decisions_dir` + extended `_find_wiki_root` with v1.1 consumer marker; 12 scripts retrofitted; 9 new tests; MI-18 registered + RESOLVED
- [x] Phase E — end-to-end validation + carry fixes: `find_config_dir` extension (7 more scripts retrofitted), `markdown.py::iter_content_pages` raw/ exclusion, `update_dashboards.py` CLI arg (MI-17 partial), REORGANIZATION-INSTRUCTIONS Mentor per-project moves + cross-repo Library moves section
- [x] Phase F — Auditor dispatch verdict `concerns` (5 findings); F10 MI-16 registry header RESOLVED-disposition fixed inline; F11 + F12 fixed cross-repo on Mentor side
- [x] S004 CLOSE record on `tasks/sessions.md`

### Cross-repo commits (Mentor side, branch `claude/s004-mentor-v1.1-migration-na3hg`)
- 12 commits: Phase A (`caafc8a`) + B1-B10 (`a966d27` → `f8e919a`) + close (`42dd4fc`) + F4 (`4e985bc`) + CLOSE record (`867c03b`)
- Mentor at v1.1 canonical layout post-S004; baseline parity vs M001 verified (27 pages / 0 contradictions / 54% cross-link)

### Migration issues resolved
- **MI-16** RESOLVED — sync_from_kit v1.1 contract rewrite
- **MI-18** RESOLVED — canon/decisions/config-lookup marker-walk

→ See `tasks/sessions.md` Session 4 CLOSED entry for full close record + Auditor findings table.
→ See `tasks/architect-notes.md` §S004 for the architect plan, risk register, AC1-AC10.
→ See `REORGANIZATION-INSTRUCTIONS.md` §Mentor for per-project moves manifest.

## Carried + Open (post-S004)

### Library-side
- [x] **MI-17 full closure** — RESOLVED (Post-S004 carry-closure sprint). `find_wiki_content_root()` + per-script `--wiki-root` CLI via `_lib/cli.py`. See `MIGRATION-ISSUES.md` MI-17.
- [x] **OBS-1** — RESOLVED. `audit_doc_pairing.py --stale-paths` + `_config/stale_paths.yaml` allow-list.
- [x] **OBS-4** — RESOLVED. `.claude/personas/CLAUDE.librarian.md` generated from canonical via `generate_persona_dropin.py`; drift guard in `tests/test_persona_dropin.py`.
- [x] **Library `_dashboards/` location** — RESOLVED (coupled with MI-17). Content dashboards now write to `wiki.codex/git/_dashboards/` (was leaking to repo-root `_dashboards/`). NOTE: the S002 audit scripts (`audit_doc_pairing`/`audit_local_split`/etc.) still write to system-side `wikisys.library/_dashboards/` by design — that path is NOT stale.
- [x] **MI-12** (historical curation, S001 carry) — **DROPPED (2026-05-28, operator decision).** `project-codex` is being deprecated, so its historical `tasks/*` + `CHANGELOG.md` no longer need curating/migrating. Won't-do.
- [x] **portfolio-folder-structure-spec.md greenfield claim** — RESOLVED. §883 "Mentor was greenfield, no migration needed" corrected to reflect the S004 v1.0→v1.1 migration.
- [ ] **Content-side bootstrap drop-in** (`wiki.codex/git/.claude/personas/CLAUDE.librarian.md`) — still hand/bootstrap-maintained; its drift cure belongs to `bootstrap.py`'s generation path, separate from the OBS-4 project-root fix. Low priority.

### Cross-repo (Mentor-side; tracked here for visibility)
- [ ] Mentor SPLIT pairing for Karpathy + Cherny — backfill stub R-XXXXX on next publish event
- [ ] Mentor R-00008 cross-link surface (M001 follow-up)
- [ ] Mentor JP CheatSheet canonicalization (operator decision)

## Next sprints (planned)

- **S007 — adopt EMCC shared-marketplace + `claude-<module>.md` delivery for Codex (planned; co-ship with DFDU per-project wiring).** EMCC now hosts a shared package (`EMCC/templates/shared/` + `EMCC/marketplace/` + `EMCC/scripts/emcc_wire.py`) that wires modules into existing repos: a marker-delimited "Connected EMCC modules" index in root `CLAUDE.md` routes to vendored `.claude/modules/claude-<module>.md` files (load-on-demand, anti-bloat), and skills ship via a Claude Code plugin marketplace. The Codex/Librarian consumer guidance is already templated as `EMCC/templates/shared/module-templates/claude-library.md`. **Codex actions (to land alongside DFDU wiring, per project):**
  - (a) Migrate each consumer's inlined Codex block → vendored `.claude/modules/claude-library.md` via `emcc_wire.py --module library` (done for iSommelier pilot 2026-05-28; tat_app + supplystationusa pending).
  - (b) **`emcc-codex` plugin SHIPPED (2026-05-28).** `EMCC/marketplace/plugins/emcc-codex/` ships `/ingest`, `/lint`, `/maintain`, `/sync` — each loads `CLAUDE.librarian.md` + the relevant verbatim procedure (`INGEST_PROCEDURE.md` / `SEMANTIC_LINT_PROCEDURE.md`) before acting. `claude-library.md` template references them; iSommelier wired. Mirrors `emcc-lattice`; skill delivery now uniform across modules. (tat_app + supplystationusa pick it up during their DFDU wiring.)
  - (c) Keep `claude-library.md` ⇄ `CODEX_LIBRARIAN.md` aligned (the module file is a pointer/summary; the synced `_context/CODEX_LIBRARIAN.md` stays canonical). Consider a drift check analogous to `generate_persona_dropin.py`.
  - Coupling note: this is delivery/packaging only — no change to the Codex spec, scripts, or `sync_from_kit` contract.
- **S003** (master plan Step 5) — Telegram channel boot. **Partially done**: Option A (local-only Windows env vars; bot at chat_id 1415844818) configured by operator post-S002. Cloud-CC remainder: no action required (network policy blocks `api.telegram.org`; soft-compliance contract honored).
- **S005** (master plan Step 7) — bootstrap DFDU's own `wiki/` directory.
- **S006 — consumer/module wiki bootstrap (CLOSED 2026-05-28).** All consumer + module wikis are scaffolded on the v1.1 canonical frame; consumer bootstrapping is **COMPLETE**. Done: **Aviation ✅, eddyandwolff ✅, Mentor ✅, EMCC ✅, EMCC.DFDU ✅** (EMCC + DFDU also wired via `sync_from_kit`). **aviation-career — DROPPED** (no wiki). **Tat ✅, iSommelier ✅, SupplyStationUSA ✅** scaffolded 2026-05-28 (`bootstrap.py <name>` — tat_app `--code`, isommelier + supplystationusa `--website`; scaffold-only, on branch `claude/nifty-ritchie-f6snD`). See `tasks/sessions.md` Session 7 for the close record.
  - **S006 functional wiring ✅ (2026-05-28)** — both module wikis are now operable. EMCC got a `module.json` (Codex install marker; `emcc.modules.json` rejected as the consumer-app marker, semantically wrong for a module); DFDU's existing `module.json` already served. Ran `sync_from_kit.py` into both (OVERWRITE `_scripts`/`_context` procedures + `PROJECT_WIKI_BUILD_SPEC`; MERGE-NEW `_config`/`_template`) + added `Home.md` skeletons. `find_wiki_root`/`find_wiki_content_root` detection validated from each repo's synced scripts. Cross-repo PRs: EMCC #6 (scaffold, merged) + #7 (wiring); EMCC.DFDU #5 (scaffold, merged) + #6 (wiring).
  - **Remaining (next phase, not blocking S006 close)** — script init (`sync_from_kit.py`) + first ingest for the five wikis: the three newly-scaffolded consumers (Tat / iSommelier / SupplyStationUSA) and the two module wikis (EMCC / EMCC.DFDU). Operator/Librarian-driven.

---

## Past sprint — Post-S002 stabilization (2026-05-27, CLOSED) — PR #5 → #10

Six-PR cleanup arc between S002 close and S004 open. All merged to `main`. See `tasks/sessions.md` "Post-S002 stabilization" entry for full close record + per-PR table.

### Done

- [x] PR #5 — Index.md backfill + CLAUDE.md read-order update (`8735f76`)
- [x] PR #6 — OBS-4 urgent fix: Librarian persona template sync (`ceb4f1d`)
- [x] PR #7 — S002c Library staleness audit (READ-ONLY); 157-line report (`403e860`)
- [x] PR #8 — S003a Library staleness cleanup phase 1 (path refresh + v1.1 alignment) (`f8feca1`)
- [x] PR #9 — S003b Library staleness cleanup phase 2 (archive banners + relocations) (`8c2193c`)
- [x] PR #10 — MI-17 full resolution: `find_wiki_root()` across all 17 scripts (`6b14cb6`)
- [x] PR #11 — Post-MI-17 housekeeping: tasks/{sessions,todo,lessons}.md updated (`bf36e9d`)

### MIs touched this arc

- **MI-17** — Resolved (PR #10). Marker-walk pattern lifted into `_lib/frontmatter.py::find_wiki_root()` public API; 17 scripts converted. (S004 D superseded the content-side resolution with install-root + companion `find_*_dir()` helpers; this arc was the intermediate step.)
- **MI-18** — Surfaced (post-PR-#10), Resolved in S004 D.

---

## Past sprint — S002-codex-v1.1-update (2026-05-27, CLOSED)

### Done
- [x] Phase A — open Session 2 + bank architect plan + Mentor spec correction
- [x] B1 .gitignore wiki.*/local/ extension + baseline assertions
- [x] B2 module source → Biz.Automation/wikisys.library/_* (65 git mv)
- [x] B3 Codex spec docs → wiki.codex/git/codex/ (10 git mv)
- [x] B4 wiki.codex/ internal restructure (git+local split; MI-14 + MI-15)
- [x] B5a path-lookup rebases (bootstrap.py + sync_from_kit + 10 test files)
- [x] B5b bootstrap.py full canonical-output rewrite per spec (c) + 21 new tests + 88 v1.0-shape tests retired (MI-16)
- [x] B6 5 new audit scripts (P0+P1) + FINDING #1 fix + 34 new tests
- [x] B7 CODEX_LIBRARIAN.md +174 lines (3 ops + 5 Mentor patterns + Telegram contract) + persona mirror + CLAUDE.md updates
- [x] B8 REORGANIZATION-INSTRUCTIONS.md flip (27 rows ⏳→✅) + S002-internal callers section
- [x] B9 module.json v1.1.0 + README + CLAUDE.md Path-migrations pointer + MI-10/11/12/13 dispositions
- [x] B10 Auditor dispatch — verdict `pass` with 4 info observations (OBS-2/OBS-3 fixed inline; OBS-1/OBS-4 deferred to architect-notes)

→ See `tasks/sessions.md` Session 2 CLOSED entry for full close record.
→ See `tasks/architect-notes.md` §S002 for the architect plan, Auditor observations, and deferred items.

---

## Past sprint — S001-codex-extraction (2026-05-27, CLOSED)

### Done
- [x] Phase A — open Lattice 3.0 session + architect plan
- [x] B1 pre-extraction prep (A3 import verification + .gitignore extension; pyproject.toml deferred to MI-13)
- [x] B2 bootstrap files (CLAUDE.md / module.json / SOURCE-HISTORY.md / MIGRATION-ISSUES.md / README.md / .github/workflows/test.yml / .claude/personas/CLAUDE.auditor.md)
- [x] B3 relocate G1–G17 (148-file commit; A2 revoked in-flight; personas at .claude/personas/)
- [x] B4 (reduced scope) — v1.1-backlog.md only; historical curation deferred to MI-12
- [x] B5 test infrastructure verified — 615 tests / 611 pass / 3 fail (2 baseline + 1 MI-10) / 1 skip
- [x] B6 synthetic wiki bootstrap validation — all 15 validators OK / 0 errors
- [x] B7 EMCC consumer template flip (cross-repo `b10c766`)
- [x] B8 project-codex archive disposition (cross-repo `53b4fa9`)
- [x] B9 Auditor dispatch — verdict `pass` with 3 observations (F-1 fixed inline; F-2 → MI-13; F-3 implicit Step 4)

→ See `tasks/sessions.md` Session 1 CLOSED entry for full close record.

## Cross-repo task synchronization (handled during S001 B7/B8)

- EMCC `tasks/todo.md`: unblock Step 2 (was "blocked on project-codex v1.0 SHIP"); update branch-deletion items as completed when operator confirms
- EMCC.DFDU `tasks/todo.md`: mark Library-deferred items as resolved (extraction in progress)
- project-codex `tasks/todo.md`: strikethrough items now done by Library; retain rest as reference

## Out of scope (deferred per master plan §"Out of scope")

- EMCC Step 3 (build EMCC spine — Director + Migrator agents + shell)
- EMCC Step 4 (wire DFDU + Library to EMCC via Orchestrator envelopes); Librarian Phase 2 ships here
- Guard-House / Aegis module
- EMCC.Marketing module
- Codex v1.2+ feature work beyond S002 scope
