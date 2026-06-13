# Delta Force — canon roster.yaml scaffold (dir-20260613h-canon-scaffold)

- **Date:** 2026-06-13
- **Repo:** EMCC.Library (Codex engine)
- **DFTS:** Level-2+ — hard trigger fires (modifies the documented `sync_from_kit.py` contract = breaking-contract change; touches complex sync logic). Council convened.
- **Model policy:** Fable 5 unavailable at run time → fell back to highest-available (Opus 4.8) for all 5 advisors.

## Framed decision

P13 `check_concept_coverage` hard-requires `_canon/roster.yaml` with an `entities:` list; missing → exit 2 (orchestrator reports failed sub-script). Confirmed missing fleet-wide in 2/2 consumers (eddyandwolff, isommelier). Empty-but-valid skeleton = `entities: []` (verified parses to `[]` under the stdlib YAML-subset parser; `load_config_yaml` returns `[]`).

**Forks:** (1) scaffold via bootstrap-only / sync-only / both; (2) skeleton from a shipped kit template file vs a hardcoded string; (3) is a create-if-absent `_canon` sync scaffold a contract breach of the documented "NEVER TOUCHED" `_canon/` boundary, or just existing MERGE-NEW semantics applied to one more file.

## Advisor responses (unmasked)

**The Breaker** — Hunts failure modes. Six concrete hazards: (1) sync is non-transactional — a stale `_canon` file/dir collision would die mid-run after OVERWRITE lanes already wrote, leaving a half-synced consumer with a lying SYNC-STAMP; (2) validator exit-2 is OVERLOADED (FileNotFoundError/IsADirectoryError/PermissionError/OSError all → 2), so scaffolding the file narrows nothing observably for malformed-roster cases; (3) bare `entities:` vs `entities: []` parse-equivalence is a trap for the next editor — ship explicit `[]`; a future edit to `None` would throw `TypeError`, NOT in the except tuple → uncaught; (4) **empty `entities: []` poisons sibling validators** (validate_canon_integrity, validate_topic_registry, build_canon_drift_report) → false-GREEN: a loud exit-2 becomes a silent "all good" while the consumer has zero canon; (5) MERGE-NEW resurrects an intentionally-deleted roster every sync, no opt-out; (6) the whole safety rests on one `if action.kind != "OVERWRITE"` constant adjacent to a destructive copy — one copy-paste slip wipes consumer canon. Test the empty-roster path through all four downstream validators.

**The Simplifier** — The skeleton is `entities: []\n`, an invariant constant with no `{projectname}` token → a template file is unearned (adds artifact + source path + copy lane + round-trip test). Hardcode it. Fixing the 2 existing repos is not a code problem — two manual write-if-absent drops, zero engine change. bootstrap keeps future consumers green (one line beside the existing `.gitkeep`). Don't dignify a "MERGE-NEW canon scaffold concept" — bootstrap covers new, hand covers the two old. The unearned abstraction is treating "two existing repos" as "all future repos."

**The Surgeon** — In-scope: bootstrap emits `entities: []` for future consumers + a one-off fix for the 2 existing. Out-of-scope creep: (a) a new MERGE-NEW `_canon` sync lane — opening a NEVER-TOUCHED load-bearing invariant for a one-time gap; a *lane is general by nature* and invites taxonomy.yaml/timeline.yaml "while we're here" (validator needs only roster.yaml); (b) a shipped template file vs hardcoded 2-line string (grows the SYNC-STAMP/manifest hash surface); (c) the cross_refs false-positive — directive itself said skip if it widens scope; it does (different subsystem). Minimum cut: bootstrap writes `entities: []`; one-shot write-if-absent backfills the 2 consumers; sync contract untouched.

**The Reviewer** — If sync said "NEVER TOUCHED" but also wrote `_canon`, a future dev freezes or "fixes" the contradiction. IF sync were used, name it `SCAFFOLD_IF_ABSENT` not "MERGE-NEW" (merge implies field-union; this is a one-shot non-destructive birth). The emitted file MUST carry a header comment so `entities: []` isn't read as data loss. Prefers a shipped template (one Glob answers "where's the skeleton") over a hidden hardcoded heredoc. Drop `.gitkeep` when emitting roster.yaml (two "I exist" markers = leftover bug). Pin the validator→scaffolder link with a test or it drifts.

**The Pragmatist** — Bootstrap only. Hardcoded stub. Manual one-off for the 2 known consumers. No new sync lane. Add `_stub_roster(projectname)->str` returning `entities: []` (+ header comment), wire beside `_canon/.gitkeep`; matches the existing `_stub_*` family → trivial review. One test: assert roster.yaml emitted + parses to `entities == []` + P13 exits 0 on fresh output. Re-sync the 2 existing by hand — `entities: []` is content they own. `_canon/` NEVER-TOUCHED is load-bearing; even write-if-absent erodes the boundary and invites review friction for exactly 2 consumers. Future consumers get it via bootstrap — the only mechanism that *should* seed canon (creation, not sync).

## Chairman synthesis

**Agreement (strong, 4–5 of 5):**
- **bootstrap.py is the right and only place to seed canon** — it is the project-creation act; sync is for live consumers and must not seed canon.
- **Hardcoded `entities: []` string**, matching the existing `_stub_*` family — NOT a shipped template file (unearned for an invariant 2-line constant).
- **Do NOT open a sync `_canon` lane.** `_canon/` NEVER-TOUCHED is load-bearing (Surgeon: a lane invites taxonomy/timeline creep; Breaker: stakes canon integrity on one classification constant next to a destructive copy). The contract risk dwarfs the convenience for 2 known repos.
- **Fix the 2 existing consumers by a one-off write-if-absent**, not via sync machinery.

**Clash + resolution:** Reviewer preferred a shipped template + `SCAFFOLD_IF_ABSENT` lane — but both presume sync involvement. With no sync lane (consensus), the template argument collapses to the Simplifier/Surgeon position: hardcoded string. Reviewer's header-comment recommendation is ADOPTED regardless.

**Blind spots caught (carried into build):**
- **False-green (Breaker):** empty roster makes P13 + sibling canon validators pass while canon is genuinely empty. Mitigation within scope: the header comment states the file is an empty stub to be populated, AND the delivery_result surfaces this honestly to the Operator (scaffold ≠ populated canon). Not hidden.
- **Explicit `entities: []` (Breaker):** ship the explicit empty-list form; add a parser/loader assertion it yields `[]` (already verified empirically).
- **Header comment (Reviewer):** emitted roster carries a "SAFE TO EDIT / auto-scaffolded / sync won't overwrite" comment.
- **.gitkeep:** KEEP it (lower scope — `test_full_emits_wikisys_underscore_folders` asserts `_canon/.gitkeep`; all 4 underscore dirs share the pattern). Reviewer's drop-it is cosmetic and would break an existing test for no functional gain. Documented trade-off.

**Recommendation (PROCEED):**
1. `bootstrap.py`: add `_stub_roster_yaml()` (hardcoded commented `entities: []`); emit `_canon/roster.yaml` alongside the existing `_canon/.gitkeep`.
2. Test in `test_bootstrap_canonical.py`: roster.yaml emitted + parses to `entities == []` + P13 `check_concept_coverage` exits 0 on fresh bootstrap output.
3. Existing 2 consumers (eddyandwolff, isommelier): one-off write-if-absent of the same skeleton; run P13; commit each.
4. **Do NOT** touch the `sync_from_kit.py` contract. **Do NOT** fold in the cross_refs false-positive (separate ticket).
5. Surface the false-green caveat to the Director/Operator.

**First step:** write `_stub_roster_yaml()` + the test asserting P13 exit 0 on fresh output.
