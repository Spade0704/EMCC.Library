# Librarian marketing extension — gap report + Codex extension proposal

> **Status: PROPOSAL (propose-not-dispose, Principle #11 respected — NO Library canon file is
> edited by this drop).** Authored 2026-07-21 by the EMCC Director session during the
> EMCC.Marketing module stand-up (loop contract:
> `EMCC/Biz.Automation/LOOP-DEFINITION-marketing-module-build.md`).
> **Ask:** Library runs its own Level-2+ gate (council + Lattice Regime B) on this scope and, if
> accepted, lands it as a Codex spec amendment (v1.3 → v1.4 or v2.0 per the spec-change rules).
> **Why Library:** the Operator ruled 2026-07-21 that asset cataloging for the Herald protocol
> (EMCC.Marketing) is **Librarian-owned** — stable IDs, filing, renames, the asset codex with
> lineage, Cloudflare R2 writes + public-URL minting, and the generalized inbox ingestion service
> (Herald spec §D Decision Log C3; canon:
> `EMCC.Marketing/documents/herald/herald-creation-framework.md` §§1, 4–7, 9–12 and
> `herald-brain-framework.md` §11).

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
- Depends on: OP-4 (this gate), OP-5 (R2 + credential store), the roster lock (C1 — determines
  which Marketing-side agent hands off to the Librarian).
- Cross-refs: Herald spec §D C3/C9, `herald-creation-framework.md` (the filing-loop canon),
  `herald-brain-framework.md` §11–12.

*Drop location: `0-Inbox/` per Library convention (in-flight planning docs awaiting triage). The
Librarian routes this per Inbox-Sort; it becomes canon only through Library's own gate.*
