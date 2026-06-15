# Architect Plan — Cross-link engine promotion (from Aviation consumer)

> Status: DRAFT plan, awaiting operator sign-off + Auditor verdict (Level-2 Lattice).
> Origin: Aviation `wiki.etihad` topic cross-linking (2026-06-13). Lessons recorded
> in `tasks/lessons.md` §"Cross-link engine gaps surfaced by the Aviation consumer".
> Spec authority: `wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md` — **spec wins**;
> §2.5 (cross_link.yaml schema) + §2.7 (marker contract + link format + plug-in).

## Goal

Fold the genuinely-generic improvements proven in Aviation into the Codex engine +
Librarian, so future consumers get them via Sync — WITHOUT changing behavior for
existing consumers (DFDU, Mentor). All new behavior is **opt-in / collision-triggered**.

## Scope classification

Level-2+ (cross-module: edits engine scripts + spec + Librarian persona; propagates to
all consumers via `sync_from_kit.py`; must keep the 644-test suite green). Requires
Architect plan (this doc) + Auditor verdict per `EMCC.DFDU/documents/lattice/05-AUDIT-REGIMES.md`.

## Gap → fix mapping (the six lessons)

| # | Gap | Proposed fix | Spec touch | Default |
|---|-----|--------------|-----------|---------|
| 1 | P18.2 assigns topics / P18.3 writes See-also; consumer grabs P18.3 (dumb) | Document the split + when-to-run in `CODEX_LIBRARIAN.md`; make P18.3 read `cross_link.yaml` | §2.5 prose | n/a |
| 2 | `max_links_per_page` enforced nowhere | Apply cap in P18.3 where the See-also list is built; rank by shared-topic-count → cross-container before truncating | none (config already specced) | cap stays 8; **0 = uncapped** for back-compat |
| 3 | No duplicate-stem disambiguation (`[[Stem]]` ambiguous) | When a stem occurs in >1 content page wiki-wide, emit `[[rel/path\|Stem (CONTAINER)]]` | **§2.7 amendment** (allow path-qualified link form) | collision-triggered only → no-op on wikis with unique stems |
| 4 | Plug-in hook is dead code | Either (a) wire + test `load_plugin` end-to-end, or (b) remove it from the schema until wired | §2.5/§2.7 prose | decide in review |
| 5 | No bulk topic-backfill for pre-existing wikis | Add a generic, config-driven backfill tagger to the kit (path-derived + keyword); per-project normalization map stays project-local | new script + spec §? | new opt-in script |
| 6 | Coarse taxonomy → low-value links | Guidance only: `topics.yaml` authoring note (pair broad parent + finer child topics) | spec/Librarian prose | n/a |

## Design decisions to confirm in review

1. **Ranking key for the cap (gap 2).** Proposed: `(-shared_topic_count, -cross_container, path)`. Cross-container = a page in a different top-level section/manual ranks higher (surfaces the QRH↔FCOM↔FCTM jump). Confirm this is the right default vs TF-IDF-similarity ranking (P18.2 already computes TF-IDF — could reuse).
2. **Where the cap lives (gap 1+2).** Option A: P18.3 reads `cross_link.yaml` and self-caps (minimal change, fixes the file consumers actually use). Option B: make P18.3 consume P18.2's computed+capped related-set instead of re-deriving (bigger; removes the duplication but couples the two). Recommend A now, B as a follow-up de-dup.
3. **Plug-in (gap 4): wire vs retire.** Wiring it makes Aviation's ranking a clean plug-in (no engine fork). Retiring it removes a false affordance. Recommend wire+test (it's the spec-blessed extension point).
4. **Backfill tagger home (gap 5).** Ship as `_scripts/backfill_topics.py` (generic) reading a project `_config/topic_backfill.yaml` (rules + normalization map). Aviation's `system_map.yaml` becomes that project config. Confirm naming + config schema.

## Spec amendment (§2.7) — duplicate-stem link form

Add: "When a link target's stem is unique across the wiki, render `[[Stem]]` (default).
When the stem occurs in more than one content page, render a path-qualified link
`[[<wiki-relative-path-without-ext>|<Stem> (<top-level-container>)]]` so the reference
resolves unambiguously. Disambiguation is collision-triggered; wikis with unique stems
are unaffected (byte-identical output)." Keep the marker contract (`codex:see-also:start/end`)
and idempotency requirement unchanged.

## Test plan (keep 644 green; add)

- P18.3 cap: fixture with N>cap same-topic pages → exactly `cap` links, ranked order asserted; `cap=0` → uncapped (back-compat).
- Dup-stem: fixture with colliding stems across two folders → path-qualified links; fixture with unique stems → byte-identical to pre-change output (no regression).
- Config read: P18.3 honors `cross_link.yaml` `max_links_per_page`; malformed config → graceful default.
- Plug-in (if wired): happy path + import-error + bad-return → degrade per §2.7.
- Backfill tagger: path-derived + keyword + normalization-map → expected topics; idempotent re-run; no-fm page handling.
- Idempotency suite extended for all of the above.

## Sync impact

`sync_from_kit.py` ships `_scripts/*`, `_config/*` (templates), `PROJECT_WIKI_BUILD_SPEC`,
and the Librarian drop-in to consumers. After merge: DFDU/Mentor get the new code but
**unchanged behavior** (cap default preserved, dup-stem no-op on unique stems, backfill is
a new opt-in script). Verify with a dry Sync + their existing wiki regen producing zero diffs.

## Sequencing

1. (this doc) Plan + lessons — **done**, awaiting sign-off.
2. Boot Lattice session; Architect ratifies; Auditor regime decision.
3. Implement gap 2 + 3 (smallest, highest value: cap + dup-stem in P18.3) + tests.
4. Implement gap 1 (Librarian when-to-run + P18.3 config read) + gap 6 (authoring guidance).
5. Decide + implement gap 4 (plug-in wire/retire).
6. Implement gap 5 (backfill tagger) + spec note.
7. Bake routing guidance into `PROJECT_WIKI_BUILD_SPEC` + Librarian (the "CLAUDE.md template" half of the Aviation routing change).
8. Run full suite; dry Sync to DFDU/Mentor (zero-diff check); update `module.json` if version bumps.
9. Aviation drops its local `cross_link.py` fork, Syncs the engine, re-runs (idempotent check).

## Open questions for operator/Auditor

- Cap ranking: shared-topic-count+cross-container (proposed) vs reuse P18.2 TF-IDF?
- Plug-in: wire or retire?
- Is a §2.7 spec amendment acceptable, or should dup-stem be a consumer-only render override (keep spec pure)?
- Backfill tagger: kit-generic now, or leave consumer-local until a 2nd consumer needs it (rule-of-three)?
