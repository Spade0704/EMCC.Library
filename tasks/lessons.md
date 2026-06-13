# Lessons — EMCC.Library

> Architectural lessons captured across sessions. **Auditor NO READ** per `EMCC.DFDU/personas/CLAUDE.auditor.md` independence rule (`documents/lattice/02-PRINCIPLES-AND-WORKFLOW.md` §B). The Auditor judges artifacts, not accumulated patterns.

---

## CLAUDE.md → wiki migration (anatomy standard, framework/20; tat_app pilot 2026-06-07/08)

When the Librarian migrates an over-long `CLAUDE.md` by routing its reference content into the wiki (per `EMCC/framework/20-claude-md-anatomy.md`), these held:

**Move verbatim via a throwaway slice script, not by hand.** The reference rooms were hundreds of lines of schemas/prompts. Hand-copying invites transcription/fidelity loss. A small one-shot Python script that slices the exact line ranges out of `CLAUDE.md` and appends them to the target pages is *move-not-copy* with zero drift. Delete the script after; never commit it. Locate boundaries by **content markers** (the room/drawer header text), not hardcoded line numbers — the file shifts under you between increments.

**Rules stay, reference routes.** The win is not "shrink the file" — it is separating always-on instruction from task-conditional reference. Leave the load-bearing **invariants** inline as a short pointer block (e.g. "DB-is-memory; soft-delete; PII-strip") and move only the detailed schema/table/prose. A room becomes: header + `! MOVED to [[Page]]` + invariants.

**The canon relationship inverts — fix the framing both ways.** Overview pages that cited `CLAUDE.md` rooms in `canon_sources` (derived-from-CLAUDE.md) become the *canonical home* after the move. Append the moved detail under a clear `## Canonical detail — moved from CLAUDE.md <room> (date)` heading, and **update the repo `Index.md` drill-to** so routes point at the wiki page, not the now-emptied room. A stale drill-to ("→ CLAUDE.md R_DATA") is the main hazard: it sends the next session to a room that no longer holds the detail.

**Operational state is duplication, not knowledge — archive it, don't wiki it and don't drop it.** A `R_STATE`/"current progress" room duplicating `tasks/` does not belong in the wiki (it isn't reference knowledge) nor inline (it drifts). Replace it with a pointer to `tasks/` (the canonical source, matching the DFDU/Library pattern) and preserve the stale snapshot in `tasks/archive.md` — honors don't-delete without leaving a drift source.

**Nav test before declaring done.** After the move, verify: every `CLAUDE.md` route resolves to a real page that actually contains the moved content (grep a known string); the `<!-- EMCC:MODULES:BEGIN/END -->` managed block is byte-intact; and **zero** moved content is left orphaned inline. Re-measure with `EMCC/scripts/inventory_repo.py` `claude_md_health` (honesty-in-first-50 + under soft budget). Pilot one repo, pass the nav test, then do the next — don't batch repos.

**Appended page content still owes a later Codex pass where the wiki is initialized.** The raw append does not run `cross_link_topics`/semantic-lint (and must not — running `update_dashboards.py` to "see" it is a *write*, per the orchestrator-side-effects lesson below). In a Codex-initialized wiki, a later lint/cross-link pass reconciles `related_files`/see-also; in a scaffold-only wiki (e.g. tat_app), the append stands until tooling is initialized.

---

## Install-root vs content-root, and orchestrator side-effects (Post-S004 carry closure)

**Install-root ≠ content-root.** `find_wiki_root()` returns the *install* root for a v1.1 layout (so the `find_*_dir()` helpers can reach system-side `wikisys.*/_canon/`). But content pages and generated dashboards live on the *content* side (`wiki.<name>/git/`). Scripts that conflate the two write dashboards to `<install>/_dashboards/` (a non-gitignored repo-root leak) and page-walk the entire repo. Lesson: a script's "root" has (at least) two distinct meanings post-split — be explicit about which. Added `find_wiki_content_root()` as the companion to `find_wiki_root()`; the MI-18 `find_*_dir()` helpers already walk up to install root so they work from either start.

**Orchestrator side-effects during exploration are dangerous.** Running `update_dashboards.py` to "see what it does" silently rewrote `<!-- codex:see-also -->` blocks into 25+ tracked content pages (the `cross_link_topics` pipeline step mutates pages based on `wiki_root`). On a fresh clone this looked like spurious modifications. Lesson: treat the dashboard orchestrator as a *write* operation, not a read; never run it to probe. Use read-only single scripts (e.g. `build_completion_dashboard.py`) or `--json` modes for probing.

**Deterministic generation is a prerequisite for drift guards.** A generated artifact whose content depends on wall-clock time (e.g. `last_updated: <today>`) cannot be drift-checked by regenerate-and-compare — the guard would fail the next day with no real drift. `generate_persona_dropin.py` sources `last_updated` from the canonical's own frontmatter, making generation a pure function of the canonical. Same principle applies to any "regenerate to verify" CI guard.

**Allow-list audits must exempt their own definition files.** The stale-path sweep (`audit_doc_pairing.py --stale-paths`) flagged its own pattern-list and config file. A user-supplied allow-list that *replaces* the default would re-expose them. Fix: a small `_STALE_ALWAYS_ALLOWLIST` merged unconditionally for the files that DEFINE the patterns. Lesson: any "find forbidden strings" audit needs a non-overridable self-exemption for the files that legitimately enumerate the forbidden strings.

## Marker-walk discovery family (S004, MI-18 closure)

When a v1.0→v1.1 layout migration moves `_canon/`, `_decisions/`, `_config/` from wiki root to system-side (`Biz.Automation/wikisys.<name>/_*`), every script reading `wiki_root / "_<dir>"` breaks silently. Symptoms: empty dashboard sections, missing customization, false-positive regressions that hide as "validators OK" because they take no input.

The fix landed as a discovery-helper family in `_lib/frontmatter.py`:

- `_find_install_root(start_path)` — walks ancestors for `CLAUDE.md + module.json` (Library install) or `CLAUDE.md + emcc.modules.json` (v1.1 consumer install).
- `find_canon_dir(start_path=None)` — `<start>/_canon/` if exists (v1.0 wiki) → else walks to install root + globs `Biz.Automation/wikisys.*/_canon/`.
- `find_decisions_dir(start_path=None)` — same pattern for `_decisions/`.
- `find_config_dir(start_path=None)` — same pattern for `_config/` (added Phase E carry when Mentor's `concept_coverage.yaml::exclude_entities` customization went unread).

**Pattern lesson**: when a v1.x folder convention moves any infrastructure-prefix dir, prefer marker-walk helper at `_lib/` over per-script path hardcoding. Test against BOTH layouts (v1.0 fixture + v1.1 fixture). 12 scripts retrofitted in S004; tests at `tests/_lib/test_frontmatter.py::TestCanonAndDecisionsLookup` cover both fixtures across all 3 helpers.

**Consumer marker subtlety**: Library uses `module.json` for identity (module/producer). Consumers use `emcc.modules.json` (referencing producers). Marker-walk MUST recognize both; otherwise consumer-side install detection fails and `find_*_dir` falls back to v1.0 lookup (incorrect for v1.1 consumers).

## Walker convention shift on P-pattern folder moves (S004, walker fix)

`markdown.py::iter_content_pages` originally excluded only `_*`-prefixed path components (legacy convention: `_canon/`, `_dashboards/`, `_archive/`, etc.). Post-S004 B4 moved Mentor's `_sources/raw/` → `wiki.mentor/git/raw/` per spec P3. The new unprefixed `raw/` was suddenly walked as content pages, inflating Mentor's cross-link denominator from 28→56, dropping coverage 54%→27%.

**Lesson**: when a P-pattern folder move STRIPS an underscore prefix (P3: `_sources/raw/` → `raw/`), walker code is silently affected. Audit all content walkers (`iter_content_pages` + similar `rglob` patterns) after any spec move that changes folder naming convention. S004 fix added explicit `raw/` exclusion alongside `_*` rule; test row in `IterContentPagesTests` codifies the v1.1 canonical exclusion set.

## Sync v1.0 → v1.1 contract change (S004, MI-16 closure)

The v1.0 sync contract targeted `<wiki>/_scripts/`, `<wiki>/_context/`, `<wiki>/_config/`, `<wiki>/_template/` (all at wiki root) + `<wiki>/04-Contributing/PROJECT_WIKI_BUILD_SPEC.md`. v1.1 splits these into system-side (`<consumer>/Biz.Automation/wikisys.<consumer>/_*`) + content-side (`<consumer>/wiki.<consumer>/git/codex/PROJECT_WIKI_BUILD_SPEC.md`).

Invocation pattern changed too: was `cd <wiki>` then `python _scripts/sync_from_kit.py <codex>` (run from inside the wiki). Now `cd <consumer-root>` then `python <library>/Biz.Automation/wikisys.library/_scripts/sync_from_kit.py <library>` (run from consumer ROOT, NOT inside `wiki.<name>/`).

**Lesson**: when a sync contract changes both source paths AND target paths AND invocation cwd, rewrite the tests fixture from scratch — don't try to patch v1.0 tests to v1.1. The `_make_wiki` → `_make_consumer` rename + helper rewrite was cleaner than mechanical path-string replacement. Test discipline: add TestConsumerDiscovery class explicitly covering zero-matches refusal + multi-match refusal + `--consumer-name` override.

**v1.0-shape retirement decision**: S004 retired v1.0-shape consumer support outright. Pre-S004 wikis must (a) migrate to v1.1 first per Mentor S004 playbook, or (b) freeze at v1.0 using a pre-S004 build of `sync_from_kit.py` (preserved at git SHA `8c2193c` on `main`). Cleaner than a compat-detect mode that would double the contract surface forever.

## Auditor `concerns` is the productive middle (S004 Phase F)

Lattice 3.0 Regime B Auditor dispatched at S004 close. Verdict `concerns` (not `pass`, not `blocking`). 3 actionable findings:

- F10: MI-16 registry header at `MIGRATION-ISSUES.md` L64 still read "deferred to S004" despite C-commit pledge "Registry update in Phase E5". E5 commit flipped only MI-18.
- F11: 3 stale `wiki/_inbox/` + `wiki_legacy_2026-05-25/` (project-root) refs remained in active Mentor content (Home.md L85+L91 + File-Routing.md L108+L110). Architect plan §S004 R3 mitigation ("grep for `wiki/_` prefix in moved page bodies; rewrite to `wiki.mentor/git/...`") did NOT execute mid-B.
- F12: `_dashboards/` tracked in BOTH `wiki.mentor/git/_dashboards/` and `Biz.Automation/wikisys.mentor/_dashboards/` with diverging content (10/15 files differ). Architect-notes acknowledged ambiguity as carry but two tracked locations = structural duplication.

All 3 addressed inline (F10 Library `7ea0441` + F11/F12 Mentor `4e985bc`); sprint closed.

**Lesson**: planned mitigations in architect-notes (R1-R5 risk register) are ASPIRATIONAL until executed in a specific commit. Auditor fresh-eyes catches "planned but didn't execute" gaps that the Agent (who wrote the plan) is blind to. Especially for cross-file sweeps like F11: easy to miss 3 stale refs across 2 files when the focus is on the 30 files moved.

**Persona portability**: third Auditor dispatch in Library (S001 + S002 + S004). DFDU `CLAUDE.auditor.md` 116-line persona embedded inline each time. Confirms persona portability across sessions + cross-repo audit capability (S004 was Library+Mentor cross-repo).

## Cross-repo branch synchronization (S004)

S004 was the first cross-repo Lattice sprint on Library (S001 + S002 were Library-only). Branch name `claude/s004-mentor-v1.1-migration-na3hg` created on BOTH repos at Phase A. Commits flowed in parallel by Phase: A on both → B (Mentor only B1-B10) → C (Library) → D (Library) → E (Library) → F (both).

**Lesson**: same branch name on both repos lets `gh pr create` ship two PRs that the operator can review side-by-side. Pre-migration SHAs (`8c2193c` Library, `932e3ee` Mentor) recorded in BOTH architect plans as rollback anchors. If one PR merges and the other doesn't, both anchors stay reachable.

**Telegram contract**: Soft compliance per CLAUDE.md `mcp__plugin_telegram_telegram__reply` — tool not loaded in this session; auto-summary skipped per design (log + continue, never block). Auto-summary contract is operational scaffolding, not workflow-blocking infrastructure.

---

## Cross-arc patterns (from MI-17 → MI-18 cascade, PR #5 → #11 stabilization)

Captured in PR #11 (post-MI-17 housekeeping) and preserved through the S004 rebase as generalized architectural patterns. S004's per-phase lessons above are deep-dives on specific implementations; these are the cross-arc abstractions. L1 + L3 from PR #11 were dropped as subsumed by S004's "Marker-walk discovery family" (above) which covers the same ground more comprehensively.

### Validators can be silently broken AND silently wrong (MI-17 → MI-18 cascade)

**Context:** `check_concept_coverage.py` had been "passing" against `WIKI_ROOT = parent.parent` (resolving to `Biz.Automation/wikisys.library/`) for all of S002 close. After MI-17 landed (PR #10) and WIKI_ROOT correctly resolved, the script immediately failed loudly: `FileNotFoundError: required canon file missing`. Until MI-17, the script was running against the wrong tree AND reporting no errors — because the wrong tree had no concept-coverage data to check.

**Lesson:** A passing validator under broken inputs is worse than a failing one. After any path-resolution / restructure / discovery-layer change, **run all validators end-to-end against real content** before declaring the change done. Unit tests for `find_wiki_root()` caught the MI-17 break but did NOT catch the downstream consequence — that 16 other scripts were running against the wrong tree and silently producing wrong outputs. End-to-end validation surfaces what unit tests miss.

**Practice:** Post-restructure verification recipe must include "run every dashboard / validator script against the canonical dogfood tree, eyeball outputs for emptiness or wrongness, not just exit code." S004 Phase E adopted this practice and discovered `find_config_dir` was missing alongside `find_canon_dir` / `find_decisions_dir` — the same family was incomplete until end-to-end run.

### Banner-at-current-path beats archive-relocation for staleness disposition (S003a/b)

**Context:** S002c audit produced 9 ARCHIVE-class files. Two options: (1) move them to an `_archive/` tree (clean separation, but breaks every cross-reference + cross-link validator), or (2) leave them in place with an archive banner at the top (preserves cross-link surface; one-line discoverability).

**Lesson:** Banner-at-current-path won S003a/b because:
- `check_cross_refs.py` keeps validating linkable paths (no false-positive broken-link surface)
- Operator + agent search results still find the file at its expected location
- Banner makes the archived status discoverable on read
- One commit per file = clean per-file blame; relocation would have been one bulk commit

Exception: Lattice 2.0 launchers/ DID get moved to `_archive/launchers/` because they were a folder of related artifacts with zero inbound cross-links — wholesale relocation was clean. **Rule of thumb:** relocate only when the entire subtree is dead AND has no inbound links; banner everything else.

## QA-sweep findings (2026-06-06, caution-lint spike)

- **Unguarded I/O in a gate function = fail-open.** A build/safety-gate function that can `raise` (e.g. an unguarded `read_text("utf-8")` on a missing/non-utf-8 file) will abort the caller's loop and silently skip every downstream item — the opposite of fail-safe. Guard I/O in gate functions; on failure return a result at the *safe* tier (HIGH/deny); never let a gate raise. Caught in `check_consequence` (a poison file skipped a downstream federal HIGH page in a live sim).
- **Subset-YAML last-wins enables a silent safety-key flip.** The frontmatter subset parser keeps the last value for a repeated key, so a duplicate `consequence: low` appended after `consequence: high` flipped a HIGH page to LOW with no warning. For safety-critical fields, detect duplicate top-level keys and treat as ambiguous → fail-safe (don't trust last-wins).

## Cross-link engine gaps surfaced by the Aviation consumer (2026-06-13, wiki.etihad topic cross-linking)

The Aviation wiki (4248 pre-existing pages, no `topics.yaml` registry) needed cross-manual topic linking (QRH ↔ FCOM ↔ FCTM, e.g. all `smoke` pages). Building it consumer-local against the shipped engine surfaced six engine/spec gaps. Each is a candidate library fix; defaults must stay opt-in so DFDU/Mentor are unaffected.

- **Two linkers, and a consumer naturally grabs the wrong one.** `build_topic_index.py` (P18.2) *assigns* `topics:` (TF-IDF over a `topics.yaml` registry, holds the cap + plugin hook). `cross_link_topics.py` (P18.3) *writes* the `See also` blocks + `related_files:` and does a flat topic-set union — **no cap, no ranking, no plugin, reads no config.** A consumer wanting "cross-linking" reaches for the file literally named `cross_link_topics` and gets the dumb path. Lesson: P18.3 must read `cross_link.yaml` and honor the cap/ranking, or the split must be documented loudly in `CODEX_LIBRARIAN.md` (when to run which).
- **`max_links_per_page` is dead config — enforced nowhere.** Declared in `_config/cross_link.yaml` + the hardcoded defaults (default 8) but neither `update_page_frontmatter` (P18.2) nor `cross_link_topics` (P18.3) applies it. A broad topic (Aviation's `auto-flight` = 897 pages off one ATA chapter) yields an 897-link See-also block. Lesson: wire the cap where the See-also list is built (P18.3), ranked by shared-topic-count then cross-container so the cap keeps the *most related*, not an arbitrary slice.
- **No duplicate-stem disambiguation.** Spec §2.7 renders `[[Stem]]`. Wikis that legitimately carry same-named pages across folders/manuals (QRH `SMOKE_DET_FAULT` vs FCOM `SMOKE_DET_FAULT`) get an ambiguous wikilink that Obsidian can't resolve. Fix candidate: when a stem occurs in >1 content page wiki-wide, emit a path-qualified `[[rel/path|Stem (CONTAINER)]]` — a §2.7 amendment. Triggers only on real collisions, so it's safe for single-occurrence wikis.
- **The plugin hook is "dead code this cycle."** `load_plugin`/`blend_results` exist with a documented `link(pages)->dict` contract, but `plugin.module_path` defaults null and the path is never exercised/tested. The sanctioned extension point for custom ranking (exactly Aviation's cross-manual logic) is unusable. Lesson: either wire+test the plugin path or stop advertising it in the config schema.
- **No bulk topic-backfill for pre-existing wikis.** The engine assumes topics arrive at ingest via TF-IDF against `topics.yaml`. A consumer retro-fitting thousands of already-built pages with no registry has no tool — Aviation built a path-derived (ATA-folder normalization map) + keyword tagger. Candidate: a generic, config-driven backfill tagger in the kit; the per-project normalization map stays project-local.
- **Coarse taxonomy yields low-value links regardless of cap.** A page tagged only with one broad ATA-chapter topic gets a bounded-but-arbitrary See-also (no finer topic to rank by). The cap prevents noise but can't manufacture relevance. Lesson for `topics.yaml` authors: granularity is the lever; pair broad parent topics with finer child topics (Aviation: `smoke` + `smoke-cargo`/`smoke-avionics`) so ranking has signal.
