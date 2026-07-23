# Librarian asset-registry extension — gap report + Codex extension proposal (v1.2)

> **Status: PROPOSAL v1.2 (propose-not-dispose, Principle #11 respected — NO Library canon file is
> edited by this drop).** Authored 2026-07-21 by the EMCC Director session during the
> EMCC.Marketing module stand-up (loop contract:
> `EMCC/Biz.Automation/LOOP-DEFINITION-marketing-module-build.md`).
> **v1.1 (same day): OPERATOR-APPROVED TO PROCEED with EXPANDED SCOPE** — the Operator ratified
> Herald OP-4 and **generalized the role beyond marketing**: the Librarian becomes the
> portfolio's **asset registrar** for ANY asset, not only marketing-produced ones (see §2b). The
> wiki is not just framework/spec/documentation — it **tracks all the assets**. Library's own
> Level-2+ gate still rules on the mechanics.
> **v1.2 (2026-07-23): GAME/ANVIL SCOPE ACTIVATED (Operator ruling, Iron Soul asset-creation-loop
> session).** The §2b "Flagged FUTURE consumer — Anvil (DEFERRED)" TODO is flipped ON: the
> Operator has started on the game track, and the Library gate now rules on a registry covering
> **Scoria production assets AND game assets** (sprite / identity / frame-set / audio classes) in
> ONE schema — see §2c. Iron Soul asset creation becomes the second named consumer (after the
> Herald marketing codex). Council transcript for the gate:
> `EMCC/tasks/council/2026-07-23-asset-registry-scope.md`.
> **Ask:** Library runs its own Level-2+ gate (council + Lattice Regime B) on this scope and, if
> accepted, lands it as a Codex spec amendment (v1.3 → v1.4 or v2.0 per the spec-change rules).
> **RECONCILIATION NOTE (v1.2, 2026-07-23):** this doc's v1.0/v1.1 framing ("gate still rules on
> the mechanics") is STALE — the Library gate on the v1.1 generalized scope RAN 2026-07-21
> (second pass, transcript `tasks/council/2026-07-21-asset-registrar-gate.md`, verdict
> PROCEED-WITH-CHANGES): the **Codex v1.4 amendment is canon** (`CODEX_BUILD_SPEC_v1_4.md` §9
> Asset Registry; name **"asset registry" Operator-locked** in-spec), and the v1.4 CORE is BUILT
> (`_scripts/asset_registry.py`, Auditor concerns-proceed; Grok cert slot + OP-5/R2 still open —
> see `tasks/todo.md`). What the prior gate explicitly kept OUT was the game/Anvil scope
> ("vocabulary-extensible, zero code now"). **This v1.2 bump + the 2026-07-23 gate cover exactly
> that remainder.**
> **GATE VERDICT — GAME-SCOPE ACTIVATION (council run 2026-07-23 — transcript
> `EMCC/tasks/council/2026-07-23-asset-registry-scope.md`): PROCEED at v1.2 scope** (game classes
> as schema-forcing test cases; Iron Soul fenced on `maps_index.json` until the registrar service
> is operational). Rulings, reconciled against the 2026-07-21 verdict:
> **Q1** R2 writes — consistent with the prior carve-out ruling; adds the empirical spike (30-min:
> upload one real file to R2 stdlib-only; if untenable, the seam permits SDK/CLI inside the
> adapter only). **Q2** naming — council concurs 4-1 with the ALREADY-LOCKED "asset registry"
> (spec §9); no action. **Q3** zone rules — sufficient ONLY WITH two named mechanical checks
> layered on the v1.4 pre-commit zone validator: a public pointer-row leak lint + a zone-anomaly
> hunt in the reconciliation sweep; sweeps never delete — orphans quarantined. **Q4** lineage —
> NOT adequate for the game shape as drafted: amend before game-class implementation: (a)
> frame-set grouping/ordering semantics (ordered, grouped derivations — a flat `derived_from[]`
> can't express them); (b) recipe as a first-class typed object incl. `tool_version`; (c)
> capture-at-generation-time rule (no asset registers without lineage
> populated-or-explicitly-null-with-reason, incl. the interim `maps_index.json` rows at
> retro-registration). **Amendment class — FLAGGED CONFLICT, Operator to rule:** the 2026-07-23
> council called this v2.0 territory; the 2026-07-21 gate unanimously reserved v2.0 for changes
> that break existing consumers (v1.4 precedent). If (a)–(c) land additively, the precedent says
> **v1.5**; if frame-set semantics force a breaking lineage-model change, v2.0. Flag, don't
> silently resolve. Pre-implementation obligations: the two-chain paper walk (eddyandwolff cert
> flat case + Iron Soul identity→frames→cinematic deep case) + the R2 spike. **New Operator open
> items:** (1) deletion/takedown policy vs. URL permanence (pilot corpus holds UGC/certs/personal
> photos); (2) OP-5 R2 credential provisioning is on the critical path — needs owner + trigger
> sequenced against Herald P1. Lattice Regime B (Auditor) still applies at the implementation
> build, per framework/22.
> **Why Library:** the Operator ruled 2026-07-21 that asset cataloging for the Herald protocol
> (EMCC.Marketing) is **Librarian-owned** — stable IDs, filing, renames, the asset codex with
> lineage, Cloudflare R2 writes + public-URL minting, and the generalized inbox ingestion service
> (Herald spec §D Decision Log C3; canon:
> `EMCC.Marketing/documents/herald/herald-creation-framework.md` §§1, 4–7, 9–12 and
> `herald-brain-framework.md` §11) — and then expanded it portfolio-wide (v1.1).

---

## 1. Gap report — the Librarian's current role vs. the Herald-assigned role

Audit of `wiki.codex/git/codex/CODEX_LIBRARIAN.md` (361 lines; v1.1/v1.2/v1.3 extensions) + the
generated drop-in + `INGEST_PROCEDURE.md` + `_scripts/` (2026-07-21):

| # | Herald-assigned capability | Today | Evidence |
|---|---|---|---|
| (a) | **Scheduled/watch inbox ingestion across ALL `0-Inbox/` subfolders** (the system-wide inbox service) | **ABSENT** (near-miss) | Ingest + Inbox-Sort are operator-triggered; `CLAUDE.librarian.md:79` — Maintenance is "operator-triggered … until a watchdog mechanism is built." Cross-Project-Scan is spec'd as a future scheduled hook only. EMCC's CLAUDE.md names this exact gap: "P2-2 scheduled Librarian ingest is not yet built." Herald needs it live. |
| (b) | **Stable asset IDs distinct from filenames** (opaque serial `AST-#####`; identity never rides on names) | **ABSENT** | No ID-minting anywhere; Inbox-Sort places `.png/.jpg` by extension (`CLAUDE.librarian.md:168`), assigns nothing. |
| (c) | **Binary media lifecycle management** | **PARTIAL (hygiene only)** | `audit_assets.py` = heavy-file (>5MB) gitignore scanning + dashboard; docstring defers dup-hash/dependency/size-budget work. No lifecycle (role, versioning, supersedes). |
| (d) | **Cloudflare R2 writes + public-URL minting** (sole writer for deliverables; URL from the final R2 path, never moved) | **ABSENT** | Zero R2/Cloudflare/public-URL surface in the repo. Codex is stdlib/filesystem-only today. |
| (e) | **Asset codex with a lineage graph** (`derived_from[]`, `recipe`, `version`/`supersedes`, stale-downstream detection) | **ABSENT** | Codex has a *document* cross-link graph (topics → `related_files`) and source→derived update direction — no asset lineage; council flagged lineage as the one thing that can't be retrofitted. |
| (f) | **Auto-rename for readability** (safe because identity rides on the ID; atomic path/URL update on rename) | **ABSENT** | Ingest archives preserving names; no normalize-rename behavior. |
| (g) | **Asset reconciliation sweeps** (orphans / ghosts / doubles / stale-downstream across disk + R2 + codex) | **PARTIAL** | Pairing-Audit covers doc↔automation folders only (`CLAUDE.librarian.md:183-191`), operator-triggered. No asset-class reconciliation, no schedule. |

**Net:** the Librarian today is a document/wiki curator. Of the 7 Herald-assigned capabilities:
**5 absent, 2 partial.** All are greenfield — nothing conflicts with existing canon; they extend it.

## 2b. v1.1 — the GENERALIZED scope (Operator direction, 2026-07-21)

**The Librarian is the portfolio's asset registrar, not just Herald's.** Verbatim intent from the
Operator: assets dropped into any inbox — or already resident in a repo — get documented in the
wiki with tags, a renamed readable filename, and metadata, so they can be found, referenced, and
used (for marketing or anything else). "Where do I find the logo / the certificate / that photo?"
must be answerable from the wiki.

**Asset classes in scope (beyond marketing deliverables):**
- **UGC images** (customer-generated; note a `rights/consent` metadata field — UGC carries reuse
  constraints a logo doesn't).
- **Professionally-shot photos** — dishes, locations, interiors, staff.
- **Brand assets** — logos (and their variants), brand guidelines, fonts.
- **Credentials** — certificates, accreditation badges, awards (e.g. Coeliac Australia
  certification, Chef Hat).
- **Video / audio** and any other binary the portfolio produces or receives.

**Pilot corpus (Operator-named): eddyandwolff.** Large UGC image sets live in
`wiki.eddyandwolff/local/`, plus professional dish/location photos and brand/cert assets. The
pilot documents all of them: stable ID + tags + normalized filename + metadata page → referenced
from the wiki index.

**Metadata schema (per asset — extends the Herald codex schema §1(e) with general fields):**
`id` (stable, opaque) · `tags[]` (controlled vocab) · `name`/`description` · `asset_class` (ugc |
professional-photo | brand | credential | deliverable | …) · `subject` (dish name, location,
person-role) · `zone` (git | local) · `path` · `source` (who shot/submitted it, when) ·
`rights/consent` (esp. UGC) · `derived_from[]`/`recipe` where applicable · `created_at`/`updated_at`.

**Zone rule (privacy-preserving by construction):** metadata FOLLOWS the asset's zone. A
`local/` asset (gitignored — e.g. the eddyandwolff UGC) gets its index/metadata page in the
repo's `local/` zone; only public-safe assets get `git/`-zone pages. **Files never change zones
during registration**, and no `wiki.*/local/` gitignore rule is ever weakened. Public `git/`
indexes may carry a count/pointer row ("N UGC images — see local index") without item-level PII.

**Retro-ingestion mode (new operation):** unlike the inbox filing loop (new drops), the pilot
requires documenting assets **already in place** — register + tag + rename (with the same
atomic path-update discipline) + index, WITHOUT moving files across zones or breaking existing
references. Renames of referenced files update referrers or are skipped-with-flag.

**Relationship to Herald:** the Herald marketing asset codex (§2 below) becomes the FIRST
INSTANCE of this general asset registry — same store class, same filing loop, same
reconciliation; marketing deliverables are the only class that additionally takes the R2
public-URL step and the certification/ratification block.

**Flagged FUTURE consumer — Anvil (~~DEFERRED; Operator 2026-07-21~~ → ACTIVATED 2026-07-23, see
§2c below):** the **Anvil** game engine
(`spade0704/iron-soul-anvil` — agent-native multi-genre TypeScript engine, used by Iron Soul's
game work and intended for other game-dev projects) creates its assets via **Grok Imagine**
(`image_gen` new identities / `image_edit` pose+variant frames / `image_to_video` cinematics —
`docs/GROK_WORKFLOW.md`), while the engine itself only *loads* files from `assetsRoot` (media
contract: `anvil/docs/design/09_ASSETS_AND_MEDIA.md`; hard rule: no image-generation APIs inside
Anvil). That division of labor is exactly this registry's shape: generators create, the
**Librarian registers** — stable IDs, tags, lineage (`derived_from` across identity → pose/variant
frames → cinematic), recipe/provenance (Grok Imagine job + prompt), filing + metadata. ~~**Do NOT
scope Anvil into the gate now** — the Operator flagged it as a TODO to be activated **when he
starts working on Anvil** (the engine's M10/M11 authoring integration is still landing). Design
consequence today: keep the registry's `asset_class` vocabulary and store class game-dev-extensible
(sprites / audio / identities / frame-sets), nothing more.~~ **SUPERSEDED by v1.2 §2c — the
activation condition fired 2026-07-23 (the Operator started the game asset-creation track).**

## 2c. v1.2 — GAME/ANVIL SCOPE ACTIVATED (Operator ruling, 2026-07-23)

The §2b deferral's stated activation condition — "when he starts working on Anvil" — fired: the
Operator validated a loop-driven asset-creation pipeline for Iron Soul / Planet Scoria Prime / the
Anvil autobattler (decision record:
`Iron_Soul/0-Inbox/Iron_Soul_Asset_Creation_Loop_Summary_v0_1.md`; formal loop contract:
`Iron_Soul/Biz.Automation/LOOP-DEFINITION-asset-creation.md` DRAFT v0.1) and ruled the registry's
game scope IN for the Library gate.

**What enters the gate's scope (beyond v1.1):**
- **Game-dev asset classes** join the `asset_class` vocabulary as first-class (not just
  "extensible"): `sprite` · `identity` (character/MAP reference identity) · `frame-set`
  (pose/variant frames) · `game-audio` — alongside the v1.1 classes (ugc / professional-photo /
  brand / credential / deliverable).
- **Lineage examples extended** to the generation-pipeline shape: identity → pose/variant frames →
  cinematic, with `recipe`/provenance = the generation job + prompt (Grok Imagine job for final
  game assets; Higgsfield job for ingredient/reference assets — per the Operator's 2026-07-23
  hybrid tooling ruling recorded in `Iron_Soul/tasks/todo.md`).
- **Second named consumer:** Iron Soul asset creation (the loop above) — the Herald marketing
  codex remains the FIRST instance; the loop's registration contract explicitly targets this
  registry *only once the gate lands it* (interim truth stays `maps_index.json`).

**What does NOT change:** one schema, one store class, one filing loop — the v1.1 generalized
design already anticipated this (its "game-dev-extensible" consequence); v1.2 promotes it from
design headroom to gated scope. The division of labor holds: **generators create, the Librarian
registers.** No R2/credential work is added by this bump (still OP-5 / Operator items); no
implementation in this drop (scope + gate only).

## 2. Proposed Codex extension scope (what Library's gate should rule on)

1. **Asset-codex store + schema** — a new Codex-managed store class for asset records (the Herald
   asset codex; schema per `herald-creation-framework.md` §9: id / tags / role / lifecycle /
   path / created_by / derived_from / recipe / version / supersedes / deliverable block).
   Naming note: "asset codex" deliberately sits UNDER the Codex protocol (the Librarian operates
   both); if the collision bothers the gate, "asset registry" is the fallback name — flag, don't
   silently rename.
2. **The filing loop** (crash-safe ordering, verbatim from Herald canon): assign ID → resolve
   intra-batch lineage refs → rename → ONE move to the role-determined final home → R2 write +
   URL mint (deliverables) → **codex write = commit point** → wiki update → **inbox cleared
   LAST**. Batch resilience: malformed entries stay flagged in the inbox; never choke the batch.
   One human checkpoint: on regeneration ask "new version or new asset?"
3. **R2 writer** — the Librarian as the ONLY writer to R2 for deliverables; URL minted from the
   final R2 path. Needs: bucket/path convention + auth (Operator setup, OP-5 in the Herald spec).
   ⚠ Deviates from stdlib-only IF an SDK is used — an S3-compatible PUT via stdlib
   `urllib`/sigv4 is possible but ugly; the gate should rule stdlib-vs-dependency explicitly
   (the "stdlib or add X?" question, asked here in advance).
4. **Generalized scheduled ingestion service** — watch/schedule over `0-Inbox/` + ALL subfolders,
   protocol-selected by source subfolder; this IS the previously-named P2-2 scheduled Librarian
   ingest. Includes the "no matching protocol → flag as coverage gap, never silent" rule; the EMCC
   Director health-monitors it (coverage / backlog / wiki freshness / protocol gaps — Herald
   Brain doc §12.2).
5. **Asset reconciliation sweeps** — periodic orphans/ghosts/doubles/stale-downstream across
   disk + R2 + codex, joining the existing dashboard family.
6. **Persona/spec text updates** — `CODEX_LIBRARIAN.md` gains the asset-cataloger role section +
   the marketing-inbox operation; `CODEX_BUILD_SPEC` gains the asset-store class. (Bumps per the
   spec-change rules; generated drop-in regenerated via `generate_persona_dropin.py`.)

## 3. What this proposal does NOT ask

- No change to document-ingest verbatim procedures (`INGEST_PROCEDURE.md` /
  `SEMANTIC_LINT_PROCEDURE.md` untouched).
- No R2 account creation, no credentials handling now (Operator items).
- No implementation in this drop — scope + gate only. Implementation lands under the framework/22
  gate once accepted, sequenced against Herald P1 (first renders).

## 4. Sequencing + dependencies

- Herald P1 (first renders) is the consumer deadline; until this lands, the Herald spec forbids
  building against these capabilities as if they exist (`EMCC.Marketing/CLAUDE.md` Module wiring).
- (v1.2) Iron Soul's asset-creation loop is the second consumer; its loop contract carries the
  same "do not build against the registry as if it exists" fence and runs on `maps_index.json`
  until this gate lands — so the loop can start (once its own asset-audit gate clears) without
  waiting on the registry; a one-time retro-registration pass migrates existing rows later.
- Depends on: OP-4 (this gate), OP-5 (R2 + credential store), the roster lock (C1 — determines
  which Marketing-side agent hands off to the Librarian).
- Cross-refs: Herald spec §D C3/C9, `herald-creation-framework.md` (the filing-loop canon),
  `herald-brain-framework.md` §11–12.

*Drop location: `0-Inbox/` per Library convention (in-flight planning docs awaiting triage). The
Librarian routes this per Inbox-Sort; it becomes canon only through Library's own gate.*
