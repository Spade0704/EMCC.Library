# Task Backlog — EMCC.Library

> Newest sprint at top. Completed/stale sprints rolled to `tasks/archive.md`.
>
> **Archived 2026-06-16:** all DONE/shipped sprint items (relpath resolver `93fe81d`; readiness cascades dir-ii/hh/jj + dir-20260614n; Codex v1.3.1 cross-link; boilerplate split + stubs; M-A structural Sync; verbatim-only policy `d2c7667`; lifted tat_app patterns; S001/S002/S004 + Post-S002/S004 closures; etc.) plus the stale TestSyncStamp cleanup → see `tasks/archive.md` (§ Archived 2026-06-16).

## Codex-engine backlog (gated; not yet scheduled)

- [ ] **⚪ `./Folder/Page` resolves wiki-root-relative, not page-relative — coherence gap.** Surfaced during the `../` resolver DF (Reviewer/Simplifier seats): `./` literally means "here" yet the resolver strips it to root-relative, while `../` is page-relative — a mild dual-dialect. Held OUT of the `../` commit (directive scope = `..` only; flipping `./` is a silent finding-flip Synced to 4 consumer wikis → needs its own gate + consumer-impact audit). Decide later: make `./` page-relative for coherence, or document the root-default contract and keep. Level-2+.
- [ ] **⚪ Distinct "escapes wiki root" dashboard message for over-popped `../` links.** Reviewer seat (DF 155733): an escaped `[[../../../x]]` currently reports generic `target not found`; a distinct "escapes wiki root" message is a better author signal but expands the Pattern-#5 locked dashboard literal + its tests. Deferred from the atomic commit as gold-plating.
- [ ] **🔴 Codex engine bug (gated): YAML-subset parser drops block-list sequences.** `canon_sources:` (and any block seq) with `- item` lines parses to `None`. `validate_canon_integrity` only checks `ready` pages, so block-list `canon_sources` on solid/outlined pages is silently ignored and fails on promotion to `ready`. Fix = teach `_lib/frontmatter` block sequences OR ship an inline-only lint (+ migrate existing block-list frontmatter). Level-2+ (Syncs to all consumers) → delta-force + Auditor. Surfaced by EMCC `Inbox-Triage.md`.

## Readiness cascade tails (open)

- [ ] **🔴 LLM-seam unlock (operator-gated; raises both toward 80).** lib-summary-op → 80 needs a consumer to wire a real `summarize_fn` (EMCC `librarian_summarize.py` is the seam — currently no-op without an LLM). Logged Director-side as a top systemic unlock alongside backend-hosting.
- [ ] **⚪ lib-wiki deeper link-graph-integrity layer** (beyond cross-refs) for the path from 70 → 80.

## Codex v1.3.1 cross-link tails (open)

- [ ] **⚪ Wire the plugin hook end-to-end (or remove it).** `load_plugin`/`blend_results` exist but the `build_topic_index.py` run path never calls them.
- [ ] **⚪ Add dotted-code section-topic derivation to `backfill_topics.py`** so Aviation can drop its local `stamp_topics`/`cross_link` forks and Sync the kit instead.
- [ ] **⚪ Full dry-Sync zero-diff check to DFDU/Mentor** (deferred — sync-stamp tests env-broken on this box; covered indirectly by no-consumer-opt-in grep + default-config test).

## Cairn/Gateway accuracy track (absorbed into Library 2026-06-06)

Two EMCC.Gateway councils + a fidelity probe concluded the accuracy-critical context work belongs in Library/Codex, NOT a separate module. /llm-council 2026-06-13 verdict: sequence 1 → 2 → 3, don't merge. Item (1) verbatim-only policy SHIPPED (`d2c7667`, archived). Remaining:

- [ ] **Tiered caution-index**: an `index.md` improvement that surfaces a cheap decision/router layer + verbatim safety cautions, then loads full source on demand. Deterministic — NO neural picker in the safety path (grep/keyword search is the retriever). *(Make the ambiguity-refuse/escalate default a definition-of-done precondition per the council verdict.)*
- [ ] **Gated experiment — lossless effectivity-normalization** (dedupe repeated MSN/effectivity variants → canonical body + diff). Belongs in the wiki BUILD pipeline (single-writer), not a runtime module. KILL CRITERIA: must pass BOTH (a) byte-for-byte reconstruction of every variant AND (b) correct-variant retrieval at query time, or it's dropped. First real target: `aviation .../FCTM/PR/AEP/NAV/Unreliable_Airspeed_Indications.md`. (One-day throwaway read-only PROVER first; pass = a funding decision, not auto-build.)

(EMCC.Gateway keeps the local LLM for LOW-consequence compression — transcripts, logs, references, drafts — separate from this accuracy track.)

## Operator / consumer-side carry (open)

- [ ] **Operator:** copy `tasks/plans/aviation-bootstrap-seed/reorganization-instructions.aviation.md` into aviation/ root after `bootstrap.py aviation --full --yes` lands (overwrites the bootstrap-emitted generic stub with the pre-populated seed).
- [ ] **Cartometrics/WYAI seed** — `patterns/Opportunistic-Bundling.md` is flagged as the consumer-level seed for the deferred EMCC.Cartometrics (WYAI) module. Fold it in when that module opens.
- [ ] **Graduation decision** — if/when the `patterns/` pages earn their own first-class module (or a shared `emcc_flutter_kit` Dart package once a 2nd Flutter consumer exists), give them a dedicated wiki + canon. Until then they stay as `patterns/` docs.
- [ ] **Consumer-side carry (tat_app):** TAT's `Biz.Automation/wikisys.tat_app/_canon/roster.yaml` is still template-only, so the Codex `concept_coverage` check (P13) errors on the new TAT wiki. Populate it on the next TAT wiki session (tracked in tat_app `Tasks/todo.md`).
- [ ] **Content-side bootstrap drop-in** (`wiki.codex/git/.claude/personas/CLAUDE.librarian.md`) — still hand/bootstrap-maintained; its drift cure belongs to `bootstrap.py`'s generation path, separate from the OBS-4 project-root fix. Low priority.

### Cross-repo (Mentor-side; tracked here for visibility)
- [ ] Mentor SPLIT pairing for Karpathy + Cherny — backfill stub R-XXXXX on next publish event
- [ ] Mentor R-00008 cross-link surface (M001 follow-up)
- [ ] Mentor JP CheatSheet canonicalization (operator decision)

---

## Next sprints (planned)

- **S007 — adopt EMCC shared-marketplace + `claude-<module>.md` delivery for Codex (planned; co-ship with DFDU per-project wiring).** EMCC hosts a shared package (`EMCC/templates/shared/` + `EMCC/marketplace/` + `EMCC/scripts/emcc_wire.py`) that wires modules into existing repos. The Codex/Librarian consumer guidance is templated as `EMCC/templates/shared/module-templates/claude-library.md`. **Codex actions (to land alongside DFDU wiring, per project):**
  - (a) Migrate each consumer's inlined Codex block → vendored `.claude/modules/claude-library.md` via `emcc_wire.py --module library` (done for iSommelier pilot 2026-05-28; tat_app + supplystationusa pending).
  - (b) `emcc-codex` plugin SHIPPED (2026-05-28) — `/ingest`, `/lint`, `/maintain`, `/sync`. (tat_app + supplystationusa pick it up during their DFDU wiring.)
  - (c) Keep `claude-library.md` ⇄ `CODEX_LIBRARIAN.md` aligned (the module file is a pointer/summary; the synced `_context/CODEX_LIBRARIAN.md` stays canonical). Consider a drift check analogous to `generate_persona_dropin.py`.
  - Coupling note: this is delivery/packaging only — no change to the Codex spec, scripts, or `sync_from_kit` contract.
- **S003** (master plan Step 5) — Telegram channel boot. **Partially done**: Option A (local-only Windows env vars; bot at chat_id 1415844818) configured by operator post-S002. Cloud-CC remainder: no action required (network policy blocks `api.telegram.org`; soft-compliance contract honored).
- **S005** (master plan Step 7) — bootstrap DFDU's own `wiki/` directory.
- **S006 — consumer/module wiki bootstrap (CLOSED 2026-05-28).** Consumer bootstrapping COMPLETE. Remaining (next phase, not blocking close): script init (`sync_from_kit.py`) + first ingest for the five wikis — the three newly-scaffolded consumers (Tat / iSommelier / SupplyStationUSA) and the two module wikis (EMCC / EMCC.DFDU). Operator/Librarian-driven.

## Out of scope (deferred per master plan §"Out of scope")

- EMCC Step 3 (build EMCC spine — Director + Migrator agents + shell)
- EMCC Step 4 (wire DFDU + Library to EMCC via Orchestrator envelopes); Librarian Phase 2 ships here
- Guard-House / Aegis module
- EMCC.Marketing module
- Codex v1.2+ feature work beyond S002 scope
