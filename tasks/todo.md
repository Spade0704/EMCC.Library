# Task Backlog — EMCC.Library

> Newest sprint at top. Completed/stale sprints rolled to `tasks/archive.md`.
>
> **Archived 2026-06-16:** all DONE/shipped sprint items (relpath resolver `93fe81d`; readiness cascades dir-ii/hh/jj + dir-20260614n; Codex v1.3.1 cross-link; boilerplate split + stubs; M-A structural Sync; verbatim-only policy `d2c7667`; lifted tat_app patterns; S001/S002/S004 + Post-S002/S004 closures; etc.) plus the stale TestSyncStamp cleanup → see `tasks/archive.md` (§ Archived 2026-06-16).

## Doc-class drafts DELIVERED, awaiting a write path (2026-08-02) — NOT mine to land

Director (`claude:EMCC-Director` / 12a447b6) assigned three doc-class items; all three targets are
**outside this repo**. Chief (`chief:EMCC.CRW`) ruled **NO cross-repo lane** — correctly: write
authority is arbitrated *within* the map, not created out of another repo's canon. Drafts are
complete and apply as-is; **the landing is the Director's to route and the Operator's to authorize.**
Filed here so the work is a record, not a peer message ([[the record does not report its own
obsolescence]] — a draft that exists only in a bus message is invisible).

- [ ] **🟡 L1/L2/L3 drafts — `0-Inbox/2026-08-02-director-doc-class-L1-L3-drafts.md`. ALL MARKED
  INTERIM** (Level-2+ canon locks ruled under a stalled-builder constraint; `/llm-council` proposed
  for the permanent lock — wording may change; do NOT cite as settled canon).
  - **L1** `EMCC/framework/22-coding-workflow.md` — verdict-close ≠ merge act. Defect is in **two**
    places, not the one named: line 166 (step 8) **and line 20** (Roles: *"Director/PM — owns spec,
    plan approval, and sprint close"*). Line 156 is correct, left alone. Step 8 split into two rows
    so the merge act owns its own row and cannot be re-absorbed.
  - **L2** PM persona close-authority + P-AUTH clause — **template-first** (see below).
  - **L3** new § Blast classification: builder declares (an input, never a finding); Auditor
    classifies from the diff **first**; disagreement ⇒ PARK, never averaged.
- [ ] **🔴 Generator defect in `emcc_wire.py`'s distribution path — escalated by the Chief as ONE
  item across three seats.** Ours is (iii): a per-consumer persona edit **expires at the next wire**.
  Chief's (i) hardcoded capital-S repo token → eval keys miss silently; (ii) stale L0/L1 profile block
  inside regenerated `EMCC:MODULES` markers. Not this repo's code — tracked for visibility, since the
  same class is live here (`CLAUDE.librarian.md`).
- [ ] **🔴 Consumer PM personas are silently STALE against their template.** iSommelier
  `2026-06-03`/3892 B vs template `2026-06-15`/6764 B; the ~2,870-byte delta is the whole
  **No-implementer hard rule** + L0/L1 boundary + `LATTICE_AVAILABLE` check. **Nothing reports this
  drift** — no stamp, no manifest, no check. Directly relevant to `sync_from_kit`'s `SYNC-STAMP`
  contract, which is this repo's answer to exactly this problem and which the `emcc_wire.py` path
  does not have.
- [ ] **🟡 Line-ending evidence for the existing `.gitattributes` 🔴 (below) — now measured, not
  argued.** Across the 8 deployed PM personas: **5 CRLF / 3 LF against an LF template**. Plus `EMCC`
  HEAD `53050a0f` carries a **UTF-8 BOM in the git COMMIT SUBJECT** (`b'\xef\xbb\xbfdocs(hand...'`,
  byte-verified). So the distribution path **emits** the drift our own guard **cannot see**
  (`test_persona_dropin.py` is newline-blind via `read_text`). Chief's framing: *"drift guard exists"*
  is true; *"drift guard covers line-ending drift"* is false; and the generator actively produces what
  the guard cannot detect. **Two halves of one hole.**

## Engine defects — filed at EMCC 2026-07-27 (MOD-13/14/15), fixes owed by THIS repo

Found in the supplystationusa lane; the Director filed them so they are visible to a fresh room
(a defect living only in a peer message is invisible — filed beats mentioned). Filing did **not**
reassign them. One family: **mechanisms that appear to do work and don't.** Grouped because they
share a fix surface — whoever takes MOD-13 gets all three. Fixes route via PR (`_scripts/` is not
on the cert-push-guard coordination-plane allowlist).

- [x] **🔴 MOD-13 — `validate_topic_registry` reports success on ABSENT input.** With
  `_canon/topics.yaml` missing it emits `_dashboards/topic_registry_validation.md` reading
  *"All topic-registry checks passed. Errors: 0 Warnings: 0"* — **byte-identical to a real pass**;
  the only evidence is one stdout line no dashboard reader sees. Ranked highest of the three: it
  is kit code that **runs for real and Syncs**, so any consumer wiring it into a gate inherits a
  permanent green meaning "I found nothing to check". Generalises: any validator reporting success
  on absent input asserts something it never checked.
- [x] **🔴 MOD-14 — `cross_manual` is inert.** Documented in spec §2.5 as behaviour, type-checked
  by `_lib/topics.py` (46/57/210-213/251), stored on the `Topic` dataclass, and **read by no
  consumer** — `build_topic_index.py` and `cross_link_topics.py` never reference it. There is no
  folder scoping in the kit at all. Harm is **realised, not hypothetical**: two seats reasoned
  from it to opposite wrong conclusions in one session. Sharper than "unused field" — *the type
  check is itself a present-and-vacuous control*: passing it proves only that a value nobody reads
  has the right shape. Either wire it or delete it from schema **and** spec.
- [x] **🟡 MOD-15 — see-also truncation is silent.** `cross_link_topics.py:293-296` does
  `rank_related(...)[:max_links]` with no counter, no log, nothing in the `run()` summary. Filed
  **not cosmetic**: the cross-link graph *is* the routing substrate per `framework/18`, so a
  silently dropped see-also is a route that quietly does not exist.
- [ ] **🟢 Two related reference defects (lower priority, same lane):** (a) vendored
  `PROJECT_WIKI_BUILD_SPEC.md:748` ships a `[[Frontmatter-Schema]]` wikilink that resolves only
  inside Library's own wiki → a broken link + a permanent `citation_audit` finding in **every**
  consumer that syncs. Rule: **a portable artifact must not contain wikilinks at all** — `[[…]]`
  resolves against the consuming wiki's page set, a namespace the author cannot enumerate.
  (b) nothing under `_sources/` or `raw/` can be a wikilink target
  (`_lib/markdown.py::iter_content_pages` skips them), so a split-ingest source stub — which
  carries the withheld-field disclosure — has no resolvable location. Workaround shipped
  (relative links); engine has no story yet.

## 🔴 Line-ending identity is unasserted repo-wide — Library ships byte-identical files and has NO `.gitattributes` (filed 2026-07-28)

Surfaced by the Anvil PM finding the same gap in his repo; **Library's exposure is larger, because
Library is the kit that ships copies.** Verified here, not inherited from his report:

```
git ls-files .gitattributes **/.gitattributes   -> (nothing; the repo has NONE)
core.autocrlf   local: UNSET   global: UNSET   system: input
git check-attr text eol working-tree-encoding -- <canon schema>
    text: unspecified   eol: unspecified   working-tree-encoding: unspecified
```

`input` comes from the **Git-for-Windows installer**, not from this repo. So every byte-identity
claim Library makes holds **by machine accident**. A seat cloning onto a box with the commoner
`core.autocrlf=true` gets CRLF at checkout and every one of these changes meaning:

- **§9.9 `visual-evidence.schema.json`** — pinned byte-exact by Anvil's `visual-evidence.pin.test.ts`.
  Their pin goes red, Rule 9b correctly routes the seat to me, and I field a drift report caused by
  an installer default.
- **`INGEST_PROCEDURE.md` + `SEMANTIC_LINT_PROCEDURE.md`** — CLAUDE.md's verbatim discipline says
  these ship *byte-identical* into bootstrapped wikis. Nothing enforces the byte claim.
- **`.claude/personas/CLAUDE.librarian.md`** — generated, with a drift guard.

★ **AND THE DRIFT GUARD FAILS THE OPPOSITE WAY FROM ANVIL'S PIN — this is the sharp part.**
`tests/test_persona_dropin.py` compares via `read_text(encoding="utf-8")` (:66, :68). Python text
mode applies **universal newlines**, so `\r\n` is normalised to `\n` before the comparison. The
guard is therefore **newline-blind**: a CRLF-converted drop-in passes it. Anvil's byte-exact pin
false-**REDS** on line-ending drift; Library's text-mode guard false-**GREENS** on it. *Same
missing `.gitattributes`, two opposite symptoms, and only one of them announces itself.* Ours is
the quiet one — and Library is the side that SHIPS, so a CRLF-converted verbatim procedure would
clear our checks and then break the consumer's.

Fix (code → PR under framework/22, wants a seat other than mine):
1. Add `.gitattributes` marking the byte-pinned artifacts `-text` (no conversion either direction —
   what a byte-pinned artifact actually needs): the §9.9 schema, the two verbatim procedures, the
   persona drop-in, and `_template/` payloads.
2. Decide deliberately whether `test_persona_dropin` should assert BYTES (`read_bytes`) rather than
   normalised text — if "generated verbatim" is the claim, the guard must test the claim. Flag: this
   may turn a currently-green test red on some clones, which is the point.
3. Sweep for other byte-identity claims with text-mode checks (`sync_from_kit` verbatim overwrite,
   SYNC-STAMP manifest) — same shape, unexamined.

Anvil is filing the mirror atom (`.gitattributes -text` on their vendored copy) to the Director.
Ours is not a mirror: theirs protects one pinned file, ours protects everything the kit ships.

**★ Why this is not "tidy-up" — the detector we currently depend on is itself accident-conditioned
(Anvil PM, 2026-07-28).** With Library's guard newline-blind, Anvil's byte-exact pin is presently
the portfolio's *only* line-ending detector on the §9.9 schema. But that pin only functions while
**their** box keeps `core.autocrlf=input` — the same unasserted installer default. A seat installed
with the commoner `autocrlf=true` gets a pin that goes red on the CURRENT, CORRECT canon, i.e.
**permanently red — and a permanently-red check is indistinguishable from a broken one.** It gets
muted, waived, or "fixed" by re-stamping the pin to the local CRLF bytes, at which point the only
detector is not merely gone: **it reports green on converted bytes.** So the pair is: our guard
cannot fail on the drift it exists to catch, and theirs can be made to fail on everything, which
destroys it just as thoroughly. **Neither failure needs anyone to make a mistake — only a seat
installed with a different default.**

**Negative result, with its scope stated (verified 2026-07-28, whole-file reads not tails):** Library
is currently clean — every tracked `*.json`/`*.jsonl` (5 files incl. `tasks/orchestrator-log.jsonl`,
8/8 rows valid) plus all 7 ignored JSON files: **BOM=False, CR=0, all parse**; zero BOMs across
tracked `*.md`/`*.py`/`*.yaml`/`*.ts`/`*.txt`. **This proves the current state, NOT that the repo is
protected** — it is clean by the same `core.autocrlf=input` accident, and nothing here would stop or
report a BOM/CRLF arriving tomorrow. Prompted by the Anvil PM finding a UTF-8 BOM that had sat in
his `orchestrator-log.jsonl` since its first row on 2026-07-24, written by PS `>` redirection and
missed for four days because **every prior validation was `tail -3 | json.loads`** — he validated
the rows he had just written, never the file. Note the discriminator supports the shipping-side
thesis sideways: **his rot was in the UNTRACKED log; the tracked one was clean.** Ours is tracked
(it is on `cert_push_guard`'s `ALLOWED_MAIN_EXACT_FILES`), so it passes through diffs. *The artifact
outside every gate is where the encoding defect lives* — quiet because nothing reads it whole, the
same way ours is quiet because text mode normalises before comparing.

**Build note for fix-item 2** (Anvil PM, and it is right): put the reason bytes-not-text in the
**test body**, not the PR description — converting a green test to red will read as a regression to
anyone reviewing the diff later, and the PR scrolls away while the test file does not.

## MOD-2 pass on THIS repo — needs an INDEPENDENT seat (do NOT self-audit)

- [ ] **🟡 EMCC.Library dead-coverage sweep — assigned away from the Librarian seat on purpose.**
  I refused to be both the sweep's subject and its instrument (that would be a vacuous control,
  performed by the hunter). Strongest Shape-B candidates, **deliberately unassessed by me**:
  `tests/test_t1_p52_bootstrap_operation.py::EXPECTED_SCRIPT_COUNT` (= 27) and
  `EXPECTED_TOP_LEVEL_FOLDERS`. **Method is pinned** — sibling-adjacent `git worktree`, a watched
  `-v` baseline (target must show `ok`, not `skipped`), Rule 9 on every green falsifier, and
  **Rule 9b: run it as ADD A 28TH SCRIPT, not edit-the-constant.** Plus the applicability guard:
  read the actual side first — if it reads a fixture rather than enumerating the kit, 9b is **not
  applicable** and constant-vs-constant is itself the finding, established without running
  anything.

## Lane-6 — visual-evidence asset ingest (2026-07-24 → MERGED 2026-07-25/26; P0c DONE)

Whole registry-side asset pipeline + the operating persona stood up + landed (framework/22,
Windows-mandatory executes-clean). Merged in order #70 → #71 → #72 → #73; main GREEN 956 OK.
**Library fully asset-ready.** Details: `tasks/sessions.md` 2026-07-24 entry.

- [x] **🔴 B1 — fsync fix (`_move_asset` Windows EBADF).** DUAL PASS (Auditor + Grok, real
  Windows). **PR #70 MERGED** → `03c0a8a`.
- [x] **🔴 B2 — shared visual-evidence schema in §9 canon** (§9.9; sha256 `8c6eb411…`; Anvil
  vendors SHA-pinned). **PR #71 MERGED** → `21d4b17`.
- [x] **🔴 B3+B4+B5 — registry-side ingest** `validate_visual_evidence.py` (§9.9 walker+R1/R2+
  checks 1/3+recipe fold; §9.10 base-identity binding + style-bible) + game asset_classes.
  Auditor Regime-B PASS + **Grok real-Windows PASS** (`d2e9284`; 39+956 OK). **PR #72 MERGED**
  → `96ef6c1`.
- [x] **🔴 v1.5 persona op — base-identity registration + visual-evidence ingest** (+ regen
  drop-in). CODEX_LIBRARIAN.md v1.5 (Register-Base-Identity, Ingest-Visual-Asset + hard rules).
  Auditor Regime-B PASS (no findings) + **Grok chat-floor PASS** (drift+956 OK, Execute
  deferred-CISO — doc-class). **PR #73 MERGED** → `e978b77`.
- [x] **🟡 ★ DISCHARGED 2026-07-28 — `mechanical-pass-human-aesthetic` shipped EMCC-side.** Was
  filed 2026-07-26 as owed-before-any-real-Grok-Imagine-visual-asset-cert: `CERT_CLASSES` lacked
  the enum value, so P0b's visual-asset cert FAILED the pre-gate. **Both halves landed in EMCC
  PR #366 (`dir-20260726-validator-enum-build`) — i.e. it was already fixed on the same day this
  repo filed it as owed, and the entry has been stale ever since.** Director flagged the staleness
  2026-07-28; verified here against `EMCC/scripts/validate_cert_handoff.py` on EMCC main
  `95ae091` (not from memory): enum `CERT_CLASS_MECH` :136, class contract :78-83, decorrelation
  `human-attester` **enforced** :724-728, `certifier_model` must be EMPTY :729-732, `certifier_id`
  = human attester matching the ATTESTED line :750-753.
  **Two extra gates on this class that the original filing did not know about** — a re-run will
  meet them too: an asset-path ALLOWlist fence on the git range (:777-800 — non-asset paths,
  unverifiable/empty ranges all refuse) and a HIGH-risk refusal for aegis/security paths (:768).
  **Not a Library re-run:** no P0b drop exists under `0-Inbox/grok-audit/` (4 drops, all
  Library-authored) — P0b is Anvil-side (`iron-soul-anvil`, fwojames' `--strict-assets`), so
  re-running it against the new validator belongs to that repo. Carry-forward for whoever does:
  a pre-#366 drop will now fail for a *different* reason — most likely non-empty `certifier_model`
  or a model name in `certifier_id` — which is informative, not a regression.
- [ ] **🟢 Follow-up (deferred, no consumer yet):** base-identity `ast_id`
  backfill-on-registration path (design noted in §9.10; no consumer until real assets ingest
  post-G0/art).
- [x] **🟢 Anvil schema vendoring — trigger FIRED 2026-07-26, item was stale (closed 2026-07-28).**
  Read *"vendor the schema to iron-soul-anvil via Sync when fwojames' `--strict-assets` (P0b)
  MERGES … not yet."* It merged: `76f79a1` *"P0b: visual-evidence v0.1 mechanical floor
  (--strict-assets) (#3)"*, 2026-07-26, `git branch --contains` confirms it is **on Anvil main**.
  Vendoring already happened by hand, so no Sync action is owed. Verified by hash, not by report —
  Library canon `wiki.codex/git/codex/schemas/visual-evidence.schema.json` = sha256
  `8c6eb411faa8…52bd`, 5770 bytes. **Zero drift**, and the evidence is now the COMMITTED blob:
  `git show main:` / `origin/main:` / `HEAD:` on iron-soul-anvil all hash to `8c6eb411…52bd`,
  5770 bytes, `committed-main == canon → True`.
  **Correction to my own first pass (2026-07-28):** I originally reported "all three Anvil
  checkouts byte-identical" across `iron-soul-anvil` + `anvil-arena1-tip-wt` + `anvil-cli1-wt`.
  Two of those are **not checkouts** — no `.git` at all, and `git worktree list` returns exactly
  one entry. They are orphaned source copies that read as git identities purely by the `-wt`
  naming convention (the Anvil PM found the same thing independently: ~653M of them). So their
  agreement was never triangulation — it was two stale disk copies agreeing, presented in a
  phrasing that made the evidence sound broader than it was. The claim survives on better
  evidence, not on that one.
  **Second stale cross-repo item found today** — same class as the ★ cert-class blocker, same
  cause: the closing event happened in a repo this one cannot observe. Corollary 1 confirmed twice
  in one session.
- [ ] **🔴 Schema pin is ONE-DIRECTIONAL — canon→vendor drift is undetectable by either side.**
  Found while verifying the above; **this is Library's to fix, because Library is the single writer
  on the schema.** Anvil's `visual-evidence.pin.test.ts` is a *good* control — raw bytes, no newline
  translation, and it carries the right instruction (*"do NOT edit the pin to match; reconcile with
  Librarian"*, i.e. Rule 9b in the artifact). But it compares **Anvil's copy against a constant
  Anvil holds**, so it detects only *Anvil-side* edits. If **I** change the canonical §9.9 schema,
  the vendored file and the pin both stay at the old value, Anvil's suite stays **green**, and
  `grep 8c6eb411 EMCC.Library/` returns **nothing** — Library asserts its own schema's hash
  **nowhere** (confirmed: zero hits under `tests/` and `Biz.Automation/`). So the direction that is
  actually likely — canon moves, vendor doesn't — is unguarded at both ends, and the green pin
  reads as though it were covered. Shape-A: a control that cannot fail in the direction that
  matters. Fix belongs on the Library side (assert the canon hash + a documented reconcile path so
  a canon bump is forced to notice its vendors); it is code, so it routes via PR under framework/22,
  and it wants an independent seat since I am the writer it would be constraining.
  - **Second half, surfaced by the Anvil PM 2026-07-28 and verified here — the schema carries no
    machine-readable identity.** Top-level keys are exactly
    `['$schema','title','description','type','required','properties']`: **no `$id`, no `version`,
    no date** (also no `schema_version` / `last_updated` / `$comment`). REFINEMENT on the PM's
    read, and it makes the point worse rather than better: the version is not missing, it is
    **present and unaddressable** — `description` opens *"Shared visual-evidence sidecar schema
    v0.1 (council SHIP 2026-07-24)"*. A human opening the file sees a version and reasonably
    concludes it is versioned; no tool can compare it. Same family as everything else on this
    list — the *appearance* of a control with none of its function.
    Consequence: the hash fix above can only ever report **DIFFERENT** — never older/newer, never
    how far behind — so a drift alarm sends a human to eyeball two 5770-byte files. Ship `$id` +
    `version` in the SAME PR or the fix is half-blind.
  - **⚠ Ordering trap in that PR, noted before anyone builds it:** adding `$id`/`version` changes
    the schema bytes, which changes the sha256, which breaks Anvil's pin — i.e. **the fix is itself
    the first canon bump the missing reconcile path was supposed to handle**, and it will present
    as *"hash changed, version string unchanged (still v0.1)"*, which is exactly the shape a naive
    new control would flag as tampering. The reconcile path must handle a re-stamp explicitly, and
    Anvil must be told before it lands (PM v6u2ccqi has agreed to re-vendor on notice).

## Inbound gate item (2026-07-23) — game-scope activation

- [x] **🔴 Asset-registry GAME/ANVIL scope — gate run (2026-07-23): council PROCEED at proposal
  v1.2 scope.** Operator activated the §2b deferral (Iron Soul asset-creation loop = second
  consumer); transcript `EMCC/tasks/council/2026-07-23-asset-registry-scope.md`; verdict block in
  `0-Inbox/2026-07-21-librarian-marketing-extension-proposal.md` (v1.2). Rulings layer on the
  2026-07-21 v1.4 verdict (consistent on R2 carve-out, naming, zone validator).
- [ ] **🔴 Author the game-class spec amendment per the 2026-07-23 gate** (BEFORE any game-class
  implementation): (a) frame-set grouping/ordering semantics in the lineage model; (b) recipe as
  a first-class typed object incl. `tool_version`; (c) capture-at-generation-time rule
  (lineage populated-or-explicitly-null-with-reason, incl. interim `maps_index.json` rows at
  retro-registration); (d) game-dev `asset_class` values (sprite / identity / frame-set /
  game-audio). **Amendment class = OPERATOR CALL (flagged conflict):** v1.5 if additive (per the
  unanimous 2026-07-21 "v2.0 = breaking only" precedent) vs. the 2026-07-23 council's v2.0 call.
  Precondition: the two-chain paper walk (eddyandwolff cert flat + Iron Soul
  identity→frames→cinematic deep, real prompt as recipe) — its output confirms or widens (a)–(c).
- [ ] **🟡 R2 empirical spike (30 min, per gate Q1):** upload one real file to R2 with the
  stdlib-only sigv4 adapter → settles ugly-vs-untenable with evidence. Blocked on OP-5
  (credentials — Operator).
- [ ] **🟡 Two Q3 mechanical checks** join the validator/sweep family: public pointer-row leak
  lint + zone-anomaly hunt in the reconciliation sweep (sweeps never delete; orphans quarantined).
- [ ] **⚪ OPERATOR — deletion/takedown policy vs. URL permanence** (new open item from the gate:
  pilot corpus holds UGC/certs/personal photos; "immutable public URL" has no unpublish story).
- [ ] **⚪ OPERATOR — OP-5 R2 provisioning owner + trigger** sequenced against Herald P1 (gate
  flagged it as an unowned critical-path item).

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

- [x] **⚪→🔴 Anvil asset-registry onboarding — TRIGGER FIRED 2026-07-23; this item was STALE on
  main for six days (reconciled 2026-07-29 at the PR #69 merge).** It read *"DEFERRED until the
  Operator starts working on Anvil (trigger: JP says so; Operator-flagged 2026-07-21)"*. The
  Operator activated the §2b deferral on **2026-07-23** — game-dev asset classes entered gated
  scope and Iron Soul's asset-creation loop became the second named consumer — and the council
  gate returned **PROCEED at proposal v1.2 scope**. The correction was written the same day but
  sat unmerged on a **draft** branch, so main kept asserting the trigger had not fired while
  Lane-6 shipped a whole visual-evidence pipeline against Anvil on top of it.
  **Third stale item of this sweep, and the only one whose cause was our own unmerged branch** —
  the other two were closed by events in repos this one cannot observe. This one was fully
  visible and still missed, which is the sharper case: *a draft PR is a record that has been
  written and does not count yet, and nothing distinguishes it from one that was never written.*
  Live work is now tracked in the merged **§ Inbound gate item (2026-07-23) — game-scope
  activation** above (game-class spec amendment pending; amendment class v1.5-vs-v2.0 is an
  OPERATOR call). Original deferral text kept below for provenance:
  > When Anvil (`spade0704/iron-soul-anvil`
  — game engine for Iron Soul + future game-dev; assets created by Grok Imagine per its
  `docs/GROK_WORKFLOW.md`, engine loads-only from `assetsRoot`) goes active, extend the portfolio
  asset registry to manage its asset creation: register Grok Imagine outputs (identities →
  pose/variant frame-sets → cinematics) with IDs/tags/lineage/recipe-provenance + filing into the
  > engine's media-contract layout (`anvil/docs/design/09_ASSETS_AND_MEDIA.md`). Until then the
  > only cost is keeping the registry schema game-dev-extensible (noted in the v1.1 proposal §2b).
  > Do not build anything Anvil-specific before the trigger.

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
