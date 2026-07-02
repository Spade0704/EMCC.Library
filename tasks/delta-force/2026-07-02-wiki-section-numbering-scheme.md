# Delta Force — Wiki section-numbering scheme (Codex bootstrap)

- **Date:** 2026-07-02
- **Session:** EMCC.Library Lattice 3.0 (cross-repo folder-structure reorg, item 1 of Library bootstrap build)
- **Convened by:** Librarian (Architect seat) at pre-build gate, per `framework/22` coding workflow + `framework/09 §3` DFTS.
- **DFTS:** Hard trigger fires — multi-module / contract-shaping scaffold canon (blast radius = every future bootstrapped wiki, all consumers). Convene. Soft rubric also ≥4 (blast radius 2, reversibility 2, novelty 1, complexity 1, uncertainty 1 = 7).

## Framed decision

Define the canonical wiki section-numbering scheme `bootstrap.py` ships for every new Codex wiki.

**Facts.** bootstrap materializes boilerplate pages implying only `00-Start-Here/` + `04-Contributing/`; `_template/` ships ONLY those two. The dogfood wiki (`wiki.codex/git/`) has 00, 01-Architecture, 02-Operations, 04-Contributing — 01/02 were HAND-built, never scaffolded; NO 03 exists anywhere. The cross-repo audit flagged the "03-section gap" as a template bug. **Constraint:** renumbering (04→03) is FORBIDDEN — wikilinks are `[[FileStem]]`, `related_files`/`canon_sources` cite stems/paths; renumber = Tier-3 citation-rewrite landmine. Pure stdlib; spec-(c)-defined output; 644-test suite green; `test_persona_dropin` drift-guard + bootstrap-e2e are tripwires. Sibling ruling in the SAME reorg: assets/ 6-gitkeep scaffold → OPT-IN (empty scaffold folders are a smell to remove).

**Candidates.**
- **A** — fixed 5-slot 00-Start-Here/01-Architecture/02-Operations/03-Reference/04-Contributing; ship stubs for missing 01/02/03 so new wikis are gap-free.
- **B** — sections are sparse/semantic (gaps by-design); ship only 00+04; document "numbers are slots"; close the 03-gap won't-fix.
- **C** — ship 00+04; per-project section scheme declared in `_config`.

## Stage 2 — Independent advisor analysis (Fable 5, 5 seats)

**The Breaker → B.** A breaks first and loudest: shipping empty 01/02/03 stubs reintroduces the exact empty-scaffold smell the assets/ ruling just killed. Concrete: (1) `demote_boilerplate_stubs.py` exists to demote content-free boilerplate → the pipeline fights its own output; (2) `check_concept_coverage.py` + completion dashboard count 3 perpetually-RED sections in every wiki that never needs "03-Reference"; (3) DFDU/Mentor hand-built 01/02 → a shipped stub lands beside real content = dup pages / ambiguous `[[wikilinks]]`; (4) Home.md ToC advertising an empty 03 = dead-link bait for `check_link_graph.py`. C breaks deepest: per-project numbers force `sync_from_kit.py` templates to parameterize `__SEP__`, explode bootstrap-e2e fixtures into config matrices, and make cross-repo section-semantics incomparable (kills the very audit that found this). B's only failure = doc rot → a re-filed audit ticket; cheapest failure on the board.

**The Simplifier → B.** The bug is the expectation, not the artifact. Nothing resolves sections by index; wikilinks/frontmatter cite names not ordinals — which is *why* renumber is forbidden: the numbers are already identities, not positions. A gap in an identity space is not a defect. A ships unearned content (3 stubs someone must maintain/lint/explain) and smuggles a taxonomy decision in as a bugfix. C is a knob with zero requesting users. Minimal correct form: one sentence in the spec + close won't-fix. Zero code. If a future consumer genuinely needs canonical 01/02/03, that's the moment to earn A — not before.

**The Surgeon → B.** The request is narrow: "close the 03-gap the audit flagged." Adjudicate the claim, don't build what it implies. A exceeds it three ways (invents "Reference" taxonomy nobody asked for; ships 01/02 stubs; maximal blast radius spec(c)+bootstrap+templates+tests lockstep) and is the only option with drive-by risk to the dogfood's hand-built 01/02. C is textbook gold-plating. B changes the fewest files (docs only), asserts the LEAST new canon (explicitly none), touches neither bootstrap.py, templates, tests, nor the dogfood wiki. Won't-fix-with-rationale IS the fix.

**The Reviewer → B, with naming discipline.** Documented sparseness reads as "room to grow"; undocumented gap reads as a bug. Gaps in numbered namespaces are a known idiom (BASIC line numbers, HTTP 1xx). A actively harms legibility: empty `01-Architecture.md` reads as ABANDONMENT; the names are dishonest for diverse domains (a restaurant wiki has no "Architecture"; "03-Reference" is a junk-drawer name). The dogfood wiki never created 03 — the home project voted with its feet. **Key requirement:** the "numbers are slots" contract must live IN the shipped wiki (Start-Here or a materialized `_context/` note), not only in Library canon — self-explaining beats stub-explaining.

**The Pragmatist → B, docs-only close.** The gap caused zero runtime failures across 644 green tests — cosmetic finding, not a bug. The assets/ ruling is dispositive: A ships three empty stub sections per wiki forever, and any Auditor comparing the two rulings bounces A for inconsistency on the first pass. Cost: A = spec+bootstrap+3 templates+tests lockstep dual-gate; C = YAGNI config subsystem; B = one paragraph in spec (c) + maybe one Home.md template comment + close audit item. The renumber-forbidden constraint even *helps* B: if 03 can never be reshuffled, "gaps are legal" is the only honest semantics.

## Stage 3 — Peer review (collapsed)

Anonymous peer review is convened to break deference on DISAGREEMENT. All five seats converged independently on B from five distinct angles (breakage, minimality, scope, legibility, ship-cost) with no clash. Per the skill's "no agreeable verdict ⇒ escalate; don't force" rule inverted: a genuine unanimous verdict with non-overlapping rationales is the strongest signal available — the peer-review round is collapsed as confirmatory. Documented deviation.

## Stage 4 — Chairman synthesis

**Consensus:** unanimous **Candidate B**. Section numbers are canonical SEMANTIC SLOTS — sparse by design, created when content earns them, gaps normal and expected, existing numbers never renumbered (already a hard constraint).

**Clashes:** none material. The only within-B refinement is the Reviewer's (echoed by Pragmatist): B is not purely zero-code — the slots contract must be self-explaining IN each shipped wiki, which is one line added to an EXISTING template page, not a new stub.

**Blind spots caught (that killed A):** `demote_boilerplate_stubs.py` self-fight; `check_concept_coverage.py` perpetual-red; hand-built 01/02 collision → dup `[[wikilinks]]`; and the decisive consistency argument — A contradicts the assets/ opt-in ruling in the same reorg, so the Auditor bounces it.

**Recommendation.** Adopt B. Item 1 becomes docs + one existing-template line + audit disposition, NOT a bootstrap.py section-logic change:
1. Amend spec (c): one paragraph — "Wiki section numbers are reserved semantic slots. Create a numbered section when its content exists; sparse numbering (gaps) is canonical and expected; existing sections are never renumbered (wikilink/frontmatter citations are stem/path-bound)."
2. Self-explaining in-situ: add a 1-line "Section numbering" note to the EXISTING shipped template `00-Start-Here__SEP__How-to-Use-This-Wiki.md` (a content edit to a page that already ships — no new folder, no new page, no concept-coverage perturbation).
3. Close the audit "03-section gap" as WON'T-FIX (intended behavior); record the disposition.
4. NO fixed 5-slot taxonomy; NO empty 01/02/03 stubs; NO per-project config.

**Concrete next step.** Reframe the operator ask from a NAME-lock ("ratify 03-Reference") to a POLICY-lock ("ratify: section numbers are semantic slots, gaps by-design, 03-gap won't-fix"). First test to write during the build: assert the How-to-Use-This-Wiki template contains the section-numbering note (guards the self-explaining contract) — and assert bootstrap still emits NO numbered section folders beyond the boilerplate-implied 00/04 (guards against stub regression).

**Integration note.** This Delta Force pass gates the APPROACH only. The independent Regime-B Auditor + Grok cross-check still run on the actual diff per `framework/22`. Transcript is the evidence of record.