# Task Backlog — EMCC.Library

> Newest sprint at top. Completed/stale sprints rolled to `tasks/archive.md`.
>
> **Archived 2026-06-16:** all DONE/shipped sprint items (relpath resolver `93fe81d`; readiness cascades dir-ii/hh/jj + dir-20260614n; Codex v1.3.1 cross-link; boilerplate split + stubs; M-A structural Sync; verbatim-only policy `d2c7667`; lifted tat_app patterns; S001/S002/S004 + Post-S002/S004 closures; etc.) plus the stale TestSyncStamp cleanup → see `tasks/archive.md` (§ Archived 2026-06-16).

## Lane-6 — visual-evidence asset ingest (2026-07-24, Orchestrator cascade)

Whole registry-side asset pipeline stood up this session (framework/22, Windows-mandatory
executes-clean). Details: `tasks/sessions.md` 2026-07-24 entry.

- [x] **🔴 B1 — fsync fix (`_move_asset` Windows EBADF).** `DUAL PASS` (Auditor + Grok, real
  Windows). **PR #70** — awaiting operator merge (first in order).
- [x] **🔴 B2 — shared visual-evidence schema landed in §9 canon** (§9.9; sha256 `8c6eb411…`;
  Anvil vendors SHA-pinned). **PR #71** — awaiting merge (after #70).
- [x] **🔴 B3+B4+B5 — registry-side ingest** `validate_visual_evidence.py` (§9.9 walker+R1/R2+
  checks 1/3+recipe fold; §9.10 base-identity binding + style-bible) + game asset_classes.
  Auditor Regime-B PASS. **PR #72** (folded, Grok range `25eb936..616c9cb`).
- [ ] **🟡 Grok Windows cross-check of #72** — `status:pending` handoff on main; on PASS =
  dual-PASS → merge **#70 → #71 → #72** → Library fully asset-ready (P0c done).
- [ ] **🟢 Follow-ups (deferred):** CODEX_LIBRARIAN.md persona op for base-identity
  registration + visual-evidence ingest (+ regen drop-in); B4-info-finding parity already
  folded; base-identity `ast_id` backfill-on-registration path (design noted in §9.10).

## Inbound gate item (2026-07-21)

- [x] **🔴 Portfolio asset-registry extension (v1.1) — run the Library gate.** `Gate run`
  2026-07-21 (second pass): **council PROCEED-WITH-CHANGES** — transcript
  `tasks/council/2026-07-21-asset-registrar-gate.md`. Rulings: schema ACCEPTED with lineage +
  rights/consent mandatory-or-explicitly-empty; filing loop ACCEPTED with the R2 write moved
  OUTSIDE the commit path (skippable-with-flag, `url: pending`, mint later); R2 transport =
  R_ARCH-style carve-out plug-in, SigV4-vs-SDK deferred to the build gate (OP-5 blocks it
  anyway); **spec bump = v1.4** (additive); **name = "asset registry"** (needs Operator
  ratification per taxonomy). Four review-caught blind spots folded in as gate conditions:
  ID-allocation mechanics specified in-gate (collision-safe across repos/sessions, crash-safe
  assign-then-commit); zone-following privacy = pre-commit-point VALIDATOR, not prose;
  pre-flight `local/` snapshot before retro-ingestion; renames documented as skip-with-flag +
  reconciliation sweep, never "atomic". → Follow-up item below (v1.4 amendment authoring).
- [x] **🔴 Author the Codex v1.4 amendment (asset registry) per the gate verdict.** `Done`
  2026-07-21 (same session as the gate): `CODEX_BUILD_SPEC_v1_4.md` supersedes v1_3 (deprecation
  banner; purely additive — new §9 Asset Registry: schema w/ mandatory-or-explicitly-empty
  `rights_consent`/`derived_from`/`recipe`, per-repo namespaced crash-safe AST-ID allocation,
  filing loop w/ registry write as sole commit point + `url: pending` remote-store decoupling,
  pre-commit zone validator, retro-ingestion snapshot rule, reconciliation shape, `remote_store`
  carve-out) + CODEX_LIBRARIAN v1.4 extension (3 registrar ops + hard rules) + drop-in
  regenerated + current-spec pointers swept. Evidence: 874 tests OK (skipped=7); drift guard in
  sync (re-verified post-fix). **Regime B Auditor verdict: `concerns` (proceed) —
  `tasks/audits/2026-07-21-codex-v1.4-asset-registry-audit.md`; both warnings FIXED on top**
  (recipe in the malformed clause; footer version string). Lands via PR #68 (human-at-merge).
- [ ] **🔴 Asset-registry v1.4 CORE — BUILT + Auditor CONCERNS-proceed 2026-07-21; Grok slot OPEN.**
  Auditor verdict `tasks/audits/2026-07-21-asset-registry-core-auditor.md` (all criteria Met,
  evidence re-run 917 OK; W1 late representability refusal orphans a moved file — pre-pass fix
  at follow-up; W2 newline-refusal test missing). Cert drop
  `0-Inbox/grok-audit/2026-07-21-asset-registry-core.md` (validator PASS). Original build record:
  `dir-20260721-library-asset-registry-core` (Delta Force gate
  `EMCC.DFDU/tasks/delta-force/2026-07-21-library-asset-registry-core.md`, chairman scope 1–5):
  `Biz.Automation/wikisys.library/_scripts/asset_registry.py` + `_config/asset_registry.yaml` +
  `tests/test_asset_registry.py` (43 tests; gate-mandated first test
  `test_crash_between_move_and_registry_write_resumes_idempotently` green). Hardened §9.2
  allocator (atomic counter, scan-recovery, stale-lock surfaced never broken), §9.1 record store
  via shared `_lib/frontmatter.py` (REQUIRED_EXPLICIT; opaque git-index rows), §9.4 zone
  validator, `file_inbox` filing loop (registry write = sole commit point; lineage skip-chaining),
  CLI (`file`/`status`) + config-gated `remote_store` stub (zero network imports). Module
  EXCLUDED from `sync_from_kit` propagation this build (gate change 4; explicit wiring decision
  later). Executes-clean evidence: `tasks/evidence/2026-07-21-asset-registry-core-tests.txt`
  (917 tests OK, skipped=7 — baseline 874 + 43 new; + real CLI smoke). Next gate steps:
  Auditor (Regime B) → Grok `/cross-check` → Director DUAL-PASS close (framework/22).
- [ ] **🔴 Asset-registry follow-up build (DEFERRED per the Delta Force gate):** `retro_ingest`
  + §9.5 pre-flight snapshot; `reconcile` v0 (§9.6 sweep); any snapshot verb. Spec-conformant
  per §9.5/§9.6; sequenced after the core lands + the eddyandwolff pilot. Also carries the
  gate's three Operator spec-amendment escalations (registry-derived allocation; multi-machine/
  git-push ID-collision handling; stateless ID schemes — spec unchanged meanwhile) and the
  Auditor W1 (pre-pass representability check before ID/move) + W2 (newline-refusal +
  file-stays-in-inbox test assertions) + builder-surfaced YAML-subset residual: §9.1 `recipe` values are restricted to scalars (a
  nested `params:` sub-mapping doesn't fit the shared `_lib/frontmatter.py` subset and is
  refused with a prose flag, never flattened).
- [ ] **🔴 eddyandwolff asset-registry pilot (~20 assets)** — hand-simulate the §9.3 filing
  loop (retro-ingestion mode; take the §9.5 `local/` snapshot FIRST). **Blocked-out-of-room:**
  the eddyandwolff repo is not in this session's source set — run from a room that has it.
  R2/`url` minting stays out of the pilot (OP-5 still open; deliverable-class only anyway). Original scope item (for reference): triage
  `0-Inbox/2026-07-21-librarian-marketing-extension-proposal.md` v1.1 — Triage `0-Inbox/2026-07-21-librarian-marketing-extension-proposal.md` v1.1: the Librarian becomes the portfolio **asset registrar** — ALL asset classes (UGC images, professional photos, logos, certificates/badges, video), stable IDs + tags + renames + metadata pages, zone-following privacy rule, retro-ingestion mode, asset codex + crash-safe filing loop + R2 writer + generalized scheduled ingestion (the P2-2 seam) + reconciliation sweeps + persona/spec bumps. **Pilot corpus: eddyandwolff** (UGC in `wiki.eddyandwolff/local/` + pro dish/location photos + brand/certs). The gate rules the MECHANICS (schema, spec version bump, stdlib-sigv4 vs S3-SDK for R2); the direction is Operator-ratified. Marketing carries a Publicist-interim fallback, so Herald P0/P1 never blocks.

## Deferred / trigger-gated

- [ ] **⚪ Anvil asset-registry onboarding — DEFERRED until the Operator starts working on Anvil
  (trigger: JP says so; Operator-flagged 2026-07-21).** When Anvil (`spade0704/iron-soul-anvil`
  — game engine for Iron Soul + future game-dev; assets created by Grok Imagine per its
  `docs/GROK_WORKFLOW.md`, engine loads-only from `assetsRoot`) goes active, extend the portfolio
  asset registry to manage its asset creation: register Grok Imagine outputs (identities →
  pose/variant frame-sets → cinematics) with IDs/tags/lineage/recipe-provenance + filing into the
  engine's media-contract layout (`anvil/docs/design/09_ASSETS_AND_MEDIA.md`). Until then the only
  cost is keeping the registry schema game-dev-extensible (noted in the v1.1 proposal §2b). Do not
  build anything Anvil-specific before the trigger.

## Readiness cascade tails (open)

- [ ] **🔴 LLM-seam unlock (operator-gated; raises both toward 80).** lib-summary-op → 80 needs a consumer to wire a real `summarize_fn` (EMCC `librarian_summarize.py` is the seam — currently no-op without an LLM). Logged Director-side as a top systemic unlock alongside backend-hosting.
## Cairn/Gateway accuracy track (absorbed into Library 2026-06-06)

Two EMCC.Gateway councils + a fidelity probe concluded the accuracy-critical context work belongs in Library/Codex, NOT a separate module. /llm-council 2026-06-13 verdict: sequence 1 → 2 → 3, don't merge. Item (1) verbatim-only policy SHIPPED (`d2c7667`, archived). Remaining:

- [ ] **Gated experiment — lossless effectivity-normalization** (dedupe repeated MSN/effectivity variants → canonical body + diff). Belongs in the wiki BUILD pipeline (single-writer), not a runtime module. KILL CRITERIA: must pass BOTH (a) byte-for-byte reconstruction of every variant AND (b) correct-variant retrieval at query time, or it's dropped. First real target: `aviation .../FCTM/PR/AEP/NAV/Unreliable_Airspeed_Indications.md`. (One-day throwaway read-only PROVER first; pass = a funding decision, not auto-build.)

(EMCC.Gateway keeps the local LLM for LOW-consequence compression — transcripts, logs, references, drafts — separate from this accuracy track.)

## Operator / consumer-side carry (open)

- [ ] **Operator:** copy `tasks/plans/aviation-bootstrap-seed/reorganization-instructions.aviation.md` into aviation/ root after `bootstrap.py aviation --full --yes` lands (overwrites the bootstrap-emitted generic stub with the pre-populated seed).
- [ ] **Cartometrics/WYAI seed** — `patterns/Opportunistic-Bundling.md` is flagged as the consumer-level seed for the deferred EMCC.Cartometrics (WYAI) module. Fold it in when that module opens.
- [ ] **Graduation decision** — if/when the `patterns/` pages earn their own first-class module (or a shared `emcc_flutter_kit` Dart package once a 2nd Flutter consumer exists), give them a dedicated wiki + canon. Until then they stay as `patterns/` docs.
- [ ] **Consumer-side carry (tat_app):** TAT's `Biz.Automation/wikisys.tat_app/_canon/roster.yaml` is still template-only, so the Codex `concept_coverage` check (P13) errors on the new TAT wiki. Populate it on the next TAT wiki session (tracked in tat_app `Tasks/todo.md`).
- [ ] **Content-side bootstrap drop-in** (`wiki.codex/git/.claude/personas/CLAUDE.librarian.md`) — still hand/bootstrap-maintained; its drift cure belongs to `bootstrap.py`'s generation path, separate from the OBS-4 project-root fix. Low priority. _(reconcile-verified-open: `bootstrap.py` shipped, but this content-side drop-in is STILL hand-maintained — its bootstrap-generation-path cure is unbuilt → legit-OPEN, verified 2026-07-12.)_

### Cross-repo (Mentor-side; tracked here for visibility)
- [ ] Mentor SPLIT pairing for Karpathy + Cherny — backfill stub R-XXXXX on next publish event
- [ ] Mentor R-00008 cross-link surface (M001 follow-up)
- [ ] Mentor JP CheatSheet canonicalization (operator decision)

---

## Next sprints (planned)

- **S007 — adopt EMCC shared-marketplace + `claude-<module>.md` delivery for Codex (planned; co-ship with DFDU per-project wiring).** EMCC hosts a shared package (`EMCC/templates/shared/` + `EMCC/marketplace/` + `EMCC/scripts/emcc_wire.py`) that wires modules into existing repos. The Codex/Librarian consumer guidance is templated as `EMCC/templates/shared/module-templates/claude-library.md`. **Codex actions (to land alongside DFDU wiring, per project):**
  - (a) Migrate each consumer's inlined Codex block → vendored `.claude/modules/claude-library.md` via `emcc_wire.py --module library` (done for iSommelier pilot 2026-05-28; tat_app + supplystationusa pending).
  - (b) `emcc-codex` plugin SHIPPED (2026-05-28) — `/ingest`, `/lint`, `/maintain`, `/sync`. (tat_app + supplystationusa pick it up during their DFDU wiring.)
  - (c) Keep `claude-library.md` ⇄ `CODEX_LIBRARIAN.md` aligned (the module file is a pointer/summary; the synced `_context/CODEX_LIBRARIAN.md` stays canonical). ~~Consider a drift check analogous to `generate_persona_dropin.py`.~~ **Drift-check evaluated 2026-06-19 → STOP / will NOT build** (pre-build gate; Regime-B). Not analogous: the persona drop-in is the canonical *verbatim* (regenerate-and-compare) while `claude-library.md` is a hand-authored placeholder'd pointer with no deterministic generation function; plus the template is EMCC-owned and there's ~1 modular consumer today. Full rationale in `tasks/architect-notes.md` §S007 decision-fork (b) RESOLVED-STOP. Revisit only as an EMCC-side reference-integrity lint if 3+ consumers + observed staleness.
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
