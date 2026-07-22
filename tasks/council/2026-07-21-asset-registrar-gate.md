# LLM Council — Library gate: portfolio asset-registrar extension (proposal v1.1)

- **Date:** 2026-07-21
- **Decision:** Should Library ACCEPT the portfolio asset-registrar extension
  (`0-Inbox/2026-07-21-librarian-marketing-extension-proposal.md`, v1.1, role Operator-approved
  via Herald OP-4) as a Codex spec amendment — and on what MECHANICS: (a) asset-record store
  class + metadata schema, (b) the crash-safe filing loop, (c) R2 writer stdlib-sigv4 vs S3 SDK,
  (d) spec bump v1.3 → v1.4 vs v2.0, (e) naming "asset codex" vs "asset registry".
- **Council:** 5 advisors (Contrarian / First-Principles / Expansionist / Outsider / Executor),
  all seats + chairman on Fable 5; independent Stage-2 analysis → anonymous Stage-3 peer review
  (A=Outsider, B=Contrarian, C=Executor, D=First-Principles, E=Expansionist) → Stage-4 chairman
  synthesis.
- **VERDICT: PROCEED-WITH-CHANGES** (7 changes, §Synthesis (iv)/(v) below).
- **Scope note:** the ROLE was already Operator-locked (OP-4, expanded scope, eddyandwolff
  pilot); this gate ruled mechanics only. The v1.4 amendment itself is follow-up Level-2+
  Library work under Lattice 3.0 (Architect plan + Regime B persona Auditor) — this transcript
  is the pre-build gate record, not the amendment.

---

## Stage 1 — Framing (as put to the advisors)

EMCC.Library ships Codex (HARD stdlib-only; spec `CODEX_BUILD_SPEC_v1_3`) + the Librarian.
Operator approved (OP-4) expanding the Librarian into the portfolio-wide asset registrar: all
binary asset classes (UGC, professional photos, brand/logos, credentials, video/audio,
marketing deliverables) get stable opaque IDs (AST-#####), tags, normalized filenames, metadata
wiki pages; pilot corpus = eddyandwolff (large UGC sets in gitignored `wiki.*/local/`).
Mechanics on the table: (a) store class + schema (lineage `derived_from[]`/`recipe`,
`rights/consent`, extensible `asset_class`, zone-following privacy rule, retro-ingestion mode);
(b) crash-safe filing loop verbatim from Herald canon (ID → lineage → rename → ONE move → R2
write + URL mint for deliverables → codex write = COMMIT POINT → wiki update → inbox cleared
LAST); (c) R2 writer transport (precedent: the v1.3 R_ARCH carve-out — project-local plug-ins
sit outside the stdlib contract, failure-isolated log-and-degrade); (d) bump v1.4 vs v2.0;
(e) naming. Constraints: verbatim procedures untouched; no R2 credentials yet (OP-5); no
implementation in this gate; Herald P1 is the consuming deadline; prior council: lineage cannot
be retrofitted.

## Stage 2 — Independent submissions

### The Contrarian

Six months from now the eddyandwolff wiki has 3,000 AST records and the reconciliation sweep is
finding drift every run — because this design has three load-bearing seams that will tear.
First, the SigV4 seam. Hand-rolled SigV4 over urllib is where stdlib purism goes to die:
chunked uploads, retry/backoff, multipart for video files, clock-skew errors, region/endpoint
quirks on R2's S3 *approximation* — you're signing binary payloads, not linting Markdown. The
R_ARCH carve-out precedent doesn't fit: cross-link plug-ins are failure-isolated *degrade*
paths; the R2 writer sits BEFORE the COMMIT POINT in the filing loop, so its failure isn't
degradation, it's a stuck batch. A "log-and-degrade" component that gates the pipeline is a
contradiction. Worse: no credentials exist (OP-5), so the entire R2 leg ships untestable — a
crash-safe loop whose most fragile step has never once run before Herald P1 depends on it.
Second, the atomic-rename fiction. "Renames update referrers atomically or are
skipped-with-flag" — there is no atomic multi-file update on a filesystem; a crash
mid-referrer-rewrite leaves half-updated wikilinks, and the crash-safe loop's commit point
doesn't cover wiki updates (they happen *after* commit, explicitly). Retro-ingesting a large
gitignored local/ corpus means running this against files with no git safety net at all. Third,
the zone-following privacy rule is enforced by convention, not mechanism. One misclassified UGC
photo whose metadata page lands in git/ is a PII leak with consent implications, and the
design's only guard is "the schema has a zone field." Smaller failures: the extensible
asset_class vocab with a deferred consumer (Anvil) is speculative schema that will be wrong
when game-dev arrives; "asset codex" naming invites protocol-scope creep. If this proceeds:
v1.4 not v2.0, "asset registry," and the R2 writer moved *outside* the commit path or deferred
until credentials exist.

### The First-Principles Thinker

Strip to the root question: what is an asset registrar? It is a ledger — an append-mostly
record of identity, location, lineage, rights. The load-bearing invariant is identity stability
and lineage integrity; everything else (naming, spec versioning, transport) is decoration.
Judged from that root: The earlier council was right that lineage cannot be retrofitted — so
`derived_from[]`/recipe belongs in the schema from day one, even if Herald P1 barely uses it.
Ship the fields empty rather than absent. Same for rights/consent: a UGC corpus without consent
provenance is a liability ledger, not an asset ledger. These two are the non-negotiable core;
the rest of (a) is ordinary Codex frontmatter. (c) is where first principles bite. Ask: is R2
writing *part of the registrar*, or a *downstream consumer of it*? It is downstream — the codex
write is the commit point (b says so itself). Therefore R2 must sit outside the stdlib core,
exactly like the R_ARCH carve-out: an opt-in, failure-isolated plug-in. Given that, hand-rolled
SigV4 vs SDK is a false dilemma framed as purity-vs-pragmatism inside the core — but the
carve-out already exempts it from the purity contract. Take the SDK path *in the plug-in* only
if maintenance cost of SigV4 (chunked uploads, retries, clock skew) exceeds the dependency's;
hand-rolled SigV4 for simple PUTs is genuinely small. Either way the decision is local, not
spec-defining. (d): additive schema + a new record class + a carved-out writer = v1.4. Reserve
v2.0 for changes that break existing consumers; none exist here. (e): "asset registry." A codex
is curated prose; a registry is a ledger. Naming it "asset codex" flatters the protocol at the
cost of blurring the one distinction (record vs. page) the design depends on. P2-2 ingestion
and reconciliation sweeps are consumers of the ledger — sequence them after, never inside, this
gate.

### The Expansionist

The pilot corpus is a restaurant's photo dump, but look at what's actually being built: a
portfolio-wide content-addressable asset graph with lineage, rights, and zone-aware privacy.
That's not a Librarian side-feature — it's the substrate every future module needs. Price the
decisions against the adjacencies, not the pilot. **Lineage is the moat — over-invest there.**
The earlier council was right that it can't be retrofitted. `derived_from[]/recipe` is the seed
of a portfolio-wide provenance layer: Herald renders, Anvil game assets (sprites/frame-sets are
*pure* lineage — atlases derived from sources), marketing A/B variants, even AI-generation
audit trails (rights/consent + recipe = exactly what provenance regulation is converging on).
Make the lineage schema slightly richer than the pilot needs — recipe as structured data, not
freetext — because it's the one field where under-speccing now costs a migration later. **The
R2 writer wants to be a storage seam, not an R2 feature.** Hand-rolled SigV4 behind the R_ARCH
carve-out is fine, but name the interface generically (`remote_store`) — S3-compatible covers
R2, B2, MinIO, and any future consumer's bucket. One abstraction, N backends, zero SDK debt.
**P2-2 scheduled ingestion is the bigger opportunity in disguise.** Protocol-selected-by-
subfolder inbox watching is a general portfolio nervous system — the same loop ingests Bugbot
reports, Grok cert handoffs, email attachments from the email-director. Scope it as the generic
service it is; assets are merely its first protocol. **On the small calls:** v1.4 additive — a
major bump would falsely signal the core changed. "Asset codex" — the naming *is* the strategy;
sitting under Codex is what makes every consumer wiki an asset consumer for free. And
extensible `asset_class` vocab is the cheapest option value in the whole spec: keep it open,
validate against config, never enum-lock it. Approve mechanics; widen the seams.

### The Outsider

Someone explain to me why a wiki system for a restaurant's food photos has a hand-rolled YAML
parser and is about to get a hand-rolled AWS SigV4 implementation. From outside, "stdlib-only"
looks like it stopped being a means (portability, zero setup) and became an identity — you're
now proposing to reimplement cryptographic request signing, one of the classic "never roll your
own" categories, to preserve a purity rule the system itself already breaks via the R_ARCH
carve-out. If carve-outs exist, the R2 writer is the single most obvious carve-out candidate
imaginable: network I/O to a paid third-party cloud service is not "wiki core" by any
definition a newcomer would recognize. Use the escape hatch you built, or admit the rule is
theater. Second naive question: why is the *Librarian* the sole writer to a CDN? A
documentation persona minting public URLs for marketing deliverables smells like scope creep
wearing a robe. The metadata registry is clearly Codex-shaped work; the upload pipeline is
infrastructure. Fine to sequence them together, but naming-wise this pushes me toward "asset
registry" — a registry is what this actually is, and "asset codex" bets the branding on the
assumption that everything the Librarian touches must sound like Codex. Version bump: additive
fields, new record class, no changes to existing procedures — every industry convention says
minor. v1.4. Reserving v2.0 for a schema addition would make future *actual* breaking changes
illegible. What I'd protect as genuinely irreplaceable: the lineage graph (your own prior
council said it can't be retrofitted — so make derived_from mandatory-or-explicitly-empty from
record one, not optional) and the zone-following privacy rule, which is the one piece of design
here that's both novel and load-bearing. Everything else is conventional cataloging with
unconventional self-imposed handcuffs.

### The Executor

The smallest concrete move that proves this whole design is registering ~20 eddyandwolff UGC
assets by hand-simulating the filing loop — and every ruling should be tested against "does it
block or unblock that pilot before Herald P1." (a) Schema: ship it, but freeze only what the
pilot exercises. The lineage fields (derived_from[]/recipe) are the one non-retrofittable item
per prior council — those must land in v1 of the schema even if the pilot barely uses them.
Everything else (game-dev classes, Anvil) stays vocabulary-extensible, zero code now.
Zone-following privacy is a simple invariant; encode it as a validator check, not prose.
(b) Filing loop: adopt verbatim. It's proven Herald canon, and the commit-point ordering (codex
write = commit, inbox cleared last) is exactly what makes retro-ingestion crash-safe. Don't
redesign what already works. The "new version or new asset?" checkpoint is cheap and correct.
(c) R2: the R_ARCH carve-out is the right precedent and the practical answer. Hand-rolled SigV4
over stdlib urllib is ~150 lines, well-documented, and testable against a local S3-compatible
mock — but it doesn't matter yet because OP-5 (no credentials) blocks R2 regardless. Rule it a
carve-out plug-in, defer the SDK-vs-SigV4 fight to the build gate, and design the filing loop
so the R2 step is skippable-with-flag. That keeps Herald P1 unblocked: deliverables can
register with a `url: pending` field and mint later. (d) v1.4 additive. Nothing here breaks
existing wikis; v2.0 signaling would stall consumers for no benefit. (e) "Asset registry."
Avoids the Codex/codex-store naming collision that will bite every future grep and doc. P2-2
ingestion and reconciliation sweeps: in scope as specs, but sequence them after the pilot
proves the record store — the sweep is meaningless until there's something to reconcile. Next
step: write the v1.4 amendment + pilot 20 assets.

## Stage 3 — Anonymous peer reviews

*(Responses anonymized A=Outsider, B=Contrarian, C=Executor, D=First-Principles,
E=Expansionist; reviewer identity unmasked below.)*

**Contrarian:** Strongest: D — derives the rulings instead of asserting them; "is R2 part of
the registrar or downstream?" dissolves the SigV4 fight; "ship lineage fields empty rather than
absent" is the cleanest resolution of the non-retrofittable constraint. Biggest blind spot:
only B treats zone-following privacy as a live PII hazard; the set mostly prices it as a schema
field. Group miss: nobody stress-tested ID stability — AST-##### implies a global monotonic
counter; who allocates it across repos, concurrently, in a stdlib file-based system with no
lock service? Colliding IDs collapse the identity guarantee exactly where it matters; the
allocation mechanism, like lineage, cannot be retrofitted.

**First-Principles:** Strongest: B — alone stress-tested the design against its own text and
found the structural contradiction: the R2 write sits *before* the COMMIT POINT, so the
log-and-degrade carve-out framing (A, C, D lean on it) doesn't fit — a gating step can't be a
degrade path; plus untestable-under-OP-5 and the atomic-rename fiction. C's `url: pending`
skippable-with-flag is the one actionable fix; the synthesis should marry B and C. Blind spot:
zone-following treated as settled once stated — need a validator that fails the batch when a
local/ asset's metadata resolves to git/. Group miss: AST-##### claimed portfolio-wide with no
allocator; without a single allocator or per-repo namespace, collisions are guaranteed; ID
identity cannot be repaired later.

**Expansionist:** Strongest: B — the commit-point contradiction, atomic-rename fiction,
untestable-until-OP-5: the most concrete pre-build risks, tied to actual loop ordering. Blind
spot: the set splits 4–1 on naming but only E weighs adoption economics; and E never engages
B's commit-path problem — the expansive and skeptical halves talk past each other. Group miss:
retro-ingestion runs against a *gitignored* local/ corpus — no version control, no rollback for
renames; nobody proposes the obvious mitigation: a pre-flight manifest/backup snapshot of
local/ before the first batch, making the pilot itself crash-safe rather than just the loop's
happy path.

**Outsider:** Strongest: B — treats the mechanics as mechanics; R2-before-commit-point is the
sharpest single finding; atomic-referrer-rename and untestable-until-OP-5 are concrete,
falsifiable, and directly change the design. C's `url: pending` is the natural fix; together
they resolve (c). Blind spot: privacy enforcement got one good line (B's "convention, not
mechanism") and no follow-through — nobody specified *when* the zone check runs; it must run
pre-commit-point, or the leak is already committed. Group miss: ID assignment collision —
opaque stable IDs need an allocation mechanism (per-repo counter file? committed high-water
mark?); crash-safety of the *counter* is as non-retrofittable as the lineage graph.

**Executor:** Strongest: B — finds the actual contradiction rather than adjudicating the framed
choices; R2-before-commit-point means "carve-out log-and-degrade" and "crash-safe loop" are
mutually exclusive as specced; atomic-rename (no git safety net in local/) second. D
independently reaches the right structural fix (R2 is downstream of the ledger); pairs well
with B. Blind spot: A, D, E over-invest in SigV4-vs-SDK, a fight OP-5 makes unbuildable and
untestable right now; the executable ruling is "carve-out seam, decision deferred to the build
gate" — only C and partially D land there. Group miss: ID allocation mechanics — per-repo
counters collide across repos/concurrent sessions; a crash between ID-assign and codex-commit
can burn or duplicate IDs; belongs in this gate.

## Stage 4 — Chairman synthesis

**(i) Where the council agrees.** Consensus is unusually strong on four points. First, the
schema core: all five advisors accept (a)'s substance, and all five treat lineage
(`derived_from[]`/recipe) and rights/consent as the non-retrofittable heart of the design —
First-Principles' formulation "ship the fields empty rather than absent" and Outsider's
"mandatory-or-explicitly-empty from record one" are the same ruling. Second, the filing loop
(b) is sound Herald canon and its commit-point ordering is what makes retro-ingestion
survivable — adopt verbatim *except* for one structural amendment (below). Third, the version
bump: unanimous v1.4. Additive schema + new record class + a carved-out writer breaks no
existing consumer; spending v2.0 here would make future real breaking changes illegible.
Fourth, SigV4-vs-SDK is a false headline: once the R2 writer is ruled a carve-out plug-in, the
choice becomes a local build-gate decision — and OP-5 (no credentials) makes it unbuildable
this gate regardless. Only Executor and First-Principles landed cleanly on "carve-out seam now,
transport decision deferred"; that is the executable ruling.

**(ii) Where it clashes and why.** The real clash is Contrarian vs. the carve-out camp on (c),
and Contrarian wins on the mechanics: the R_ARCH precedent covers *failure-isolated,
log-and-degrade* plug-ins, but as specced the R2 write sits **before** the COMMIT POINT — a
gating step cannot be a degrade path. Three reviewers independently named this the sharpest
finding in the set. The resolution is Executor's: make the R2 step skippable-with-flag,
registering deliverables with `url: pending` and minting later, so the codex write remains the
sole commit point and the carve-out framing becomes honest. The other clash is Expansionist vs.
everyone on scope and naming (4–1 for "asset registry"). Expansionist's adoption-economics
argument for "asset codex" is real but loses: a codex is curated prose, a registry is a ledger,
and the design depends on exactly that record-vs-page distinction. Widen-the-seams ideas
(generic `remote_store` interface name, P2-2 as a general ingestion service) are worth carrying
as notes, not gate scope — Expansionist never engaged the commit-path problem, which is why the
expansive reading can't govern this gate.

**(iii) Blind spots caught in review.** Four, and the first is serious: **ID allocation**. Four
of five reviewers flagged that AST-##### claims portfolio-wide uniqueness with no allocator
specified — per-repo counters collide across repos and concurrent sessions, and a crash between
ID-assign and codex-commit burns or duplicates IDs. Identity stability is as non-retrofittable
as lineage; this belongs *in this gate*, not the build gate. Second, the **zone-following
privacy rule is prose, not mechanism**: it must be a validator that fails the batch
pre-commit-point when a `local/` asset's metadata resolves to `git/` — post-commit is already a
leak. Third, **retro-ingestion runs against a gitignored corpus with no rollback**: require a
pre-flight manifest/backup snapshot of `local/` before the first batch. Fourth, the
**atomic-rename fiction**: multi-file referrer updates cannot be atomic; skip-with-flag plus a
reconciliation sweep is the honest contract — say so in the spec.

**(iv) Per-question verdicts.**
- **(a) Accept with changes**: lineage and rights/consent mandatory-or-explicitly-empty;
  zone-following rule specified as a pre-commit-point validator check; asset_class stays
  config-extensible (never enum-locked), zero speculative game-dev fields now; **add an
  ID-allocation section** (single allocator or per-repo namespaced prefix, crash-safe
  assign-then-commit ordering).
- **(b) Accept with one amendment**: R2 write becomes skippable-with-flag (`url: pending`, mint
  later), preserving the codex write as sole COMMIT POINT; add the `local/` pre-flight snapshot
  requirement for retro-ingestion; document rename-referrer updates as skip-with-flag + sweep,
  not atomic.
- **(c) Carve-out plug-in** per the v1.3 R_ARCH precedent — outside the stdlib contract *and
  outside the commit path*. SigV4-vs-SDK deferred to the build gate when OP-5 clears;
  hand-rolled SigV4 is acceptable only for simple PUTs, and Outsider's "never roll your own
  signing" caution stands if scope grows to multipart/chunked.
- **(d) v1.4.**
- **(e) "Asset registry."** Record vs. page is the distinction the design lives on; don't blur
  it for branding.

**(v) Next step.** Write the v1.4 amendment incorporating the changes above — including the new
ID-allocation section and the zone validator — then hand-simulate the filing loop on ~20
eddyandwolff assets (with the `local/` snapshot taken first) to prove the record store before
Herald P1 consumes it. No implementation beyond the pilot simulation in this cycle.

**VERDICT: PROCEED-WITH-CHANGES** — (1) R2 write moved outside the commit path via
skippable-with-flag / `url: pending`; (2) ID-allocation mechanics specified in-gate
(collision-safe across repos/sessions, crash-safe ordering); (3) zone-following privacy encoded
as a pre-commit-point validator, not prose; (4) pre-flight snapshot of `local/` required before
retro-ingestion; (5) renames documented as skip-with-flag + reconciliation, not atomic;
(6) spec bump v1.4; (7) name locked as "asset registry" (Operator to ratify per taxonomy
discipline).

---

## Integration notes (Director)

- **Gate output:** clear recommendation → proceed. The v1.4 amendment authoring is the next
  Library work item — Level-2+ under Lattice 3.0 (Architect plan + Regime B persona Auditor
  post-build); this transcript is its pre-build gate evidence.
- **Escalations folded into the Operator queue:** the name "asset registry" (chairman change
  #7) needs Operator ratification per taxonomy discipline (Operator locks names; the proposal
  itself pre-flagged the naming question).
- **Cross-refs:** Herald spec §D C3/C9; `EMCC/tasks/council/2026-07-21-marketing-synthesis.md`
  (the originating council); proposal
  `0-Inbox/2026-07-21-librarian-marketing-extension-proposal.md` (v1.1).
