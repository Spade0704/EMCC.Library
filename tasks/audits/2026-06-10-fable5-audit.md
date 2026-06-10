# Fable 5 Audit — EMCC.Library — 2026-06-10

Auditor: Fable 5 (principal-engineer deep audit, 16-repo portfolio pass). Read-only except this file. HEAD: `3c68138` (2026-06-08), working tree clean.

## Executive Summary

**Grade: B+.** The Codex engine itself is in excellent shape — 644/644 tests pass in ~1.2s (verified, 6 skipped), the stdlib-only claim is true across every script (verified by import sweep), the persona drift guard is real and deterministic, and the migration registry (MI-01..MI-19) is unusually honest and complete. The grade caps at B+ because the module's core mission — being the canonical upstream for vendored consumer engines — relies on a **purely manual Sync with no version stamping**, and it is demonstrably failing: 6 of 7 sampled consumers run `doc_lint.py` exactly one revision behind canon (only `tat_app` is current), and the MI-19 "CURRENT" list is already wrong at byte level because it used a feature probe instead of byte-equality. Second structural gap: the OBS-4 persona drift guard protects only Library's own drop-in — consumer `CLAUDE.librarian.md` drop-ins are ungoverned (3 distinct hashes in the wild, one consumer missing it entirely), and `generate_persona_dropin.py` cannot even run in a consumer because the canonical lives at a path consumers don't have. Top risks: (1) silent consumer engine drift, (2) ungoverned consumer persona drift, (3) Session 14's caution-lint shipped with the Regime-B Auditor verdict still owed. Top opportunities: (1) a `codex_engine_version` stamp + `--check` mode in Sync (already proposed in MI-19, delta-force PROCEED on record), (2) extend the generated-artifact pattern to consumer persona delivery via Sync, (3) a 10-minute CLAUDE.md ROOT_INDEX refresh (5 stale rows found in 8 samples).

## Ranked Action List

| # | Action | Class | Finding |
|---|---|---|---|
| 1 | Build the version-stamp + staleness `--check` into `sync_from_kit.py` (delta-force already PROCEED); re-sync the 6 stale consumers | **act-now** | LIB-01 |
| 2 | Make Sync deliver/generate the consumer Librarian persona drop-in (or document the consumer regeneration path) | **act-now** | LIB-02 |
| 3 | Dispatch the owed Regime-B Auditor on the Session 14 caution-lint diff before `consequence` canon promotion | **act-now** | LIB-03 |
| 4 | Refresh CLAUDE.md ROOT_INDEX stale rows (test count, MI range, _scripts/_config counts, 0-Inbox row) | **act-now** (10 min) | LIB-04 |
| 5 | Wire `generate_persona_dropin.py --check` + a Sync byte-equality scan into CI / a scheduled Routine | **automate** | LIB-01/02 |
| 6 | Add `_archive/` to Sync's copytree ignore so Lattice-2.0 launchers stop shipping to consumers | **automate** (one-liner) | LIB-05 |
| 7 | Harden `_parse_value` against `--5`-class crashes; decide MERGE-NEW staleness reporting | **automate** | LIB-06/07 |
| 8 | Import-time `WIKI_ROOT` resolution; `#`-in-unquoted-value truncation | **ignore** (documented subset; markers cover real layouts) | LIB-08/06 |

## Repo Map

- **`bootstrap.py`** (575 lines, root) — v1.1 scaffold-only consumer bootstrapper (`bootstrap.py:2-9`); modes `--full/--minimal/--code/--website`; idempotency + outside-cwd refusal (`bootstrap.py:339-358`).
- **`Biz.Automation/wikisys.library/_scripts/`** — the Codex engine: 26 root `.py` (P-indexed validators/dashboards/audits + `sync_from_kit.py` + `generate_persona_dropin.py`), `_lib/` (8 files: `frontmatter.py` 664L YAML-subset parser + marker-walk discovery family, `doc_lint.py` 567L, `cli.py`, `config_loader.py`, `dashboard.py`, `markdown.py`, `topics.py`), `_archive/launchers/` (4 Lattice-2.0 `.ps1`).
- **`Biz.Automation/wikisys.library/{_template,_config,_canon,_context,_decisions}/`** — 26 templates; 7 YAML configs + README; canon YAMLs; context rules + the 4 shipped procedure docs; ingest log.
- **`wiki.codex/git/`** — dogfood wiki (Home.md + 00/01/02/04 domains + `raw/`) and **`codex/`** = protocol canon (`CODEX_BUILD_SPEC_v1_3.md`, `INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`, `CODEX_LIBRARIAN.md`, `PROJECT_WIKI_BUILD_SPEC.md`). `wiki.codex/local/` not present on disk (per-machine, gitignored).
- **`tests/`** — 46 `.py` files, stdlib `unittest`; 644 tests / 6 skipped (5 = MI-16 retired v1.0-shape modules skipping at import + 1 in-suite skip).
- **`.claude/personas/`** — `CLAUDE.librarian.md` (GENERATED) + `CLAUDE.auditor.md` (DFDU verbatim carry).
- **`scripts/`** — EMCC-vendored task-orchestration runtime (OVERWRITE-vendored, `scripts/VENDORED-FROM-EMCC.md:1-6`).
- **Governance/state** — `CLAUDE.md`, `Index.md` (3-zone), `module.json` (v1.1.0 producer marker; no `emcc.modules.json` by design), `MIGRATION-ISSUES.md` (MI-01..MI-19), `REORGANIZATION-INSTRUCTIONS.md` + per-project manifest, `tasks/*`, `patterns/` (tat_app-lifted pattern pages), `ui/manifest.json`, `.github/workflows/test.yml`.

## Audit Report

### Dimension: Sync mechanism & consumer drift (the module's core mission)

**LIB-01 — Sync is manual + unversioned; 6 of 7 sampled consumers run a stale engine — HIGH**
- **What:** `sync_from_kit.py` has no version stamp and no staleness check; nothing triggers a re-sync. Byte-comparison of `_lib/doc_lint.py` across consumers (2026-06-10): Project-Mentor, eddyandwolff, supplystationusa, isommelier, EMCC, EMCC.DFDU all carry `76acd58c…` — exactly the pre-Session-14 revision (`git show 405064e~1` hash matches) — while canon is `e889e5c7…` (last modified commit `405064e`, 2026-06-06, the caution-lint + fail-open fix). Only tat_app is current. MI-19's blast-radius scan (`MIGRATION-ISSUES.md:268-276`) classified most of these "CURRENT" because its signal was a *feature probe* (`find_wiki_content_root` present), not byte-equality — so the registry's own current/stale labels are already wrong at byte level.
- **Where:** `Biz.Automation/wikisys.library/_scripts/sync_from_kit.py:1-74` (contract; no stamp anywhere); `MIGRATION-ISSUES.md:286-291` (the version-stamp follow-up, still OPEN).
- **Why:** Stale consumers silently miss the Session-14 **fail-open gate fix** (unreadable page aborted gate loops, skipping downstream HIGH pages) and the duplicate-key HIGH→LOW flip fix — exactly the class of defect the caution-lint exists to prevent. FACT (hashes, scan method, OPEN status) / JUDGMENT: yes, purely-manual Sync is the root cause of portfolio-wide engine drift; the fix is already designed (MI-19 follow-up, delta-force PROCEED per Session 14) but not built. **Confidence: Verified.** roadmap_tag: MI-19.

**LIB-02 — Consumer Librarian persona drop-ins are ungoverned (OBS-4 guard covers Library only) — HIGH**
- **What:** Library's own `.claude/personas/CLAUDE.librarian.md` is generated + drift-guarded (verified: 8/8 tests in `tests/test_persona_dropin.py` pass; on-disk file matches deterministic render). But Sync NEVER touches consumer `.claude/*` (`sync_from_kit.py:46`), and `generate_persona_dropin.py` resolves the canonical via `install.glob("wiki.*/git/codex/CODEX_LIBRARIAN.md")` (`generate_persona_dropin.py:113-115`) — a path that exists only in Library; consumers receive `CODEX_LIBRARIAN.md` into `_context/` (`sync_from_kit.py:21-22`), so the generator returns exit 2 in any consumer. Observed in the wild: Mentor `ec719216…`, supplystationusa + isommelier `8eb5e3df…`, Library `fe1d404c…` (3 distinct revisions), eddyandwolff has **no** Librarian drop-in at all.
- **Where:** `generate_persona_dropin.py:106-131`; `sync_from_kit.py:43-46`; consumer `.claude/personas/` hashes above.
- **Why:** Consumers operate "as the Librarian" off divergent persona texts — the exact drift class OBS-4 was closed to prevent, reopened one ring outward. FACT (hashes, code paths) / JUDGMENT (severity). **Confidence: Verified.** roadmap_tag: OBS-4-residual; related open item `tasks/todo.md:118` (content-side drop-in generation).

**LIB-03 — Session 14 caution-lint shipped with the Regime-B Auditor verdict still owed — MEDIUM**
- **What:** Session 14 (Level-2+ engine code: `check_consequence` + fail-open fix) self-discloses "**Owed:** independent Lattice Auditor (Regime B) on the diff before canon promotion" (`tasks/sessions.md` Session 14 entry). Library declares `LATTICE_PROFILE: l2-plus / AUDITOR_MODE: persona` (`CLAUDE.md` live profile), which makes the Auditor mandatory for Level-2+ work. No later session records the dispatch.
- **Where:** `tasks/sessions.md` Session 14 "Verified/Owed"; `_lib/doc_lint.py:297-385`.
- **Why:** The code passed qa-sweep and 644 tests, but the repo's own governance says the verdict is a precondition for canon promotion of `consequence` — process debt that blocks the roadmap item. FACT (owed status is self-disclosed) / JUDGMENT (it should land before canon promotion). **Confidence: Verified.** roadmap_tag: session-14-owed-audit.

### Dimension: Documentation accuracy

**LIB-04 — CLAUDE.md ROOT_INDEX has 5 stale rows (of ~8 sampled) — MEDIUM**
- **What:** (a) `tests/` row says "~589 tests" — actual 644 (verified run); (b) `MIGRATION-ISSUES.md` row says "(MI-01..MI-16)" — registry reaches MI-19; (c) `_scripts/` row says "20 root `.py` … + 5 launcher `.ps1`" — actual 26 root `.py`, and 4 `.ps1` which live archived under `_scripts/_archive/launchers/`, not active; (d) `_config/` row says "5 YAML config files + README + cross_link.yaml" — actual 7 YAMLs + README (`stale_paths.yaml`, `steel_threads.yaml` unlisted); (e) `0-Inbox/` row ("Triage area…") — directory does not exist on disk. Accurate rows sampled: `_template/` 26 templates ✓; `bootstrap.py` description ✓ (`bootstrap.py:13`); generated-persona row ✓; `module.json` v1.1.0 ✓.
- **Where:** `CLAUDE.md` §ROOT_INDEX (rows for tests/, MIGRATION-ISSUES.md, _scripts/, _config/, 0-Inbox/).
- **Why:** Library is the portfolio's documentation-discipline exemplar; its own counts drifting undercuts the "tasks files are canonical, CLAUDE.md routes" doctrine and misleads sessions sizing the suite. FACT. **Confidence: Verified.** roadmap_tag: none (new).

### Dimension: Sync semantics correctness

**LIB-05 — Sync ships `_scripts/_archive/` (Lattice-2.0 PowerShell launchers) into every consumer — LOW**
- **What:** The `_scripts/` OVERWRITE action is a whole-dir `copytree` ignoring only `__pycache__` (`sync_from_kit.py:271-275`); `_archive/launchers/start-{architect,craftsman,auditor,scribe}.ps1` (retired Lattice-2.0 Nexus artifacts) therefore land in every consumer's vendored engine.
- **Why:** Dead protocol artifacts in 10+ consumer repos; harmless but confusing payload, and contradicts "the engine ships what the engine needs." FACT (code path) / JUDGMENT (worth a one-line ignore-pattern). **Confidence: Verified.**

**LIB-06 — MERGE-NEW-ONLY means config/template fixes never reach existing consumers, with no staleness signal — LOW (design trade-off)**
- **What:** `_config/` + `_template/` sync as MERGE-NEW (skip if target exists, `sync_from_kit.py:232-247`). Correct for preserving customization, but an upstream fix to a shipped template/config (e.g. a corrected `forbidden_terms.yaml` default) silently never propagates, and Sync emits no "differs from upstream" report for skipped files.
- **Why:** Combined with LIB-01 this makes consumer template staleness unbounded and invisible. JUDGMENT (the semantics are intentional and documented; the gap is the missing diff report). **Confidence: Verified** (semantics) / **Inferred** (impact).

### Dimension: YAML-subset parser robustness

**LIB-07 — `_parse_value` crashes on `--5`-class scalars; unquoted `#` truncates values — LOW**
- **What:** `s.lstrip("-").isdigit()` accepts `--5`, then `int("--5")` raises uncaught `ValueError` (verified live: `_parse_value('--5')` → ValueError). Separately, `_strip_eol_comment` splits on `#` without requiring preceding whitespace, so `title: My #1 page` parses to `{'title': 'My'}` (verified live) — YAML-conformant for ` #`, but surprising for authors and silently lossy.
- **Where:** `_lib/frontmatter.py:427` (int branch), `:371-386` (comment strip).
- **Why:** A single malformed frontmatter line can raise out of `load_page` inside validator walks (an exception, not a finding); the lessons file itself classifies raise-in-gate as fail-open. Both inputs are outside the documented subset (`frontmatter.py:8-11`), so severity stays LOW. FACT. **Confidence: Verified.**

**LIB-08 — Module-level `WIKI_ROOT = find_wiki_root()` runs at import time — LOW**
- **What:** `frontmatter.py:63` resolves WIKI_ROOT when the module is imported; in any context lacking the three markers (Home.md / CLAUDE.md+module.json / CLAUDE.md+emcc.modules.json) the import itself raises `RuntimeError` (`frontmatter.py:49-54`), making the whole `_lib` unimportable.
- **Why:** All real layouts carry a marker and the failure is loud, so this is fragility, not a bug. FACT (code) / JUDGMENT (acceptable). **Confidence: Verified.**

### Healthy dimensions (one sentence each)

- **Stdlib-only claim:** TRUE — full import sweep across `_scripts/`, `bootstrap.py`, `scripts/`, `tests/` shows only stdlib + intra-repo modules (no yaml/requests/etc.); `python -m compileall` clean, exit 0. Verified.
- **Test suite:** `python -m unittest discover -s tests -t .` → **Ran 644, OK (skipped=6)** in 1.2s; tests are behavior-style against synthetic fixtures (e.g. `test_sync_from_kit.py` builds a full fake Library install + consumer and asserts target paths/exit codes/guard trips, 64 asserts/17 tests), not execution-only smoke. Verified.
- **CI:** `.github/workflows/test.yml` runs exactly the declared runner (`python -m unittest discover -s tests -t .`, Python 3.11, no pip step) — matches CLAUDE.md and spec §7 Phase 3. Verified.
- **Persona drift guard (Library-side):** `generate_persona_dropin.py` is a pure function of the canonical (`last_updated` sourced from canonical frontmatter, `generate_persona_dropin.py:62-87`); `tests/test_persona_dropin.py` exists, is in the suite, 8/8 pass including the on-disk byte-match test — generation confirmed deterministic by static comparison, no regeneration performed. Verified.
- **Zone safety:** `git ls-files wiki.codex/local/` → 0 tracked files; rule `wiki.*/local/` at `.gitignore:75` confirmed effective via `git check-ignore`. Verified.
- **bootstrap.py:** scaffold-only contract per MI-16 with real safety rails (outside-cwd refusal, non-empty refusal, `--dry-run`, never clobbers existing stubs `bootstrap.py:398`); 22 canonical-shape tests green. Verified.
- **Manifest coherence:** Library carries `module.json` (producer marker) and deliberately no `emcc.modules.json` (consumer marker) — consistent with the marker-walk design (`frontmatter.py:69-71`) and the S006 EMCC decision. Verified.
- **Auditor persona:** byte-equal to expected DFDU canonical (`8850091…`, refreshed at `0afac29` "L4 anti-fabrication step"); sampled consumers (Mentor, eddyandwolff) carry the same bytes. Verified.

### Strengths

1. **The marker-walk discovery family** (`find_wiki_root` / `find_wiki_content_root` / `find_{canon,config,decisions}_dir`) is a textbook structural cure for a path-convention migration — tested against both v1.0 and v1.1 fixture layouts, with the install-root/content-root distinction explicitly documented (`frontmatter.py:223-260`).
2. **MIGRATION-ISSUES.md is exemplary** — append-only, self-correcting (A2 revocation recorded with the reasoning error named), with per-issue test-count deltas; MI-19 even records its own scan method, which is what made LIB-01's method critique possible.
3. **Fail-safe engineering culture** — `check_consequence` defaults unknown/missing/unreadable to HIGH and explicitly documents why raise-in-gate is fail-open (`doc_lint.py:320-336`); the qa-sweep that caught it is logged with regression tests.
4. **Determinism as a design principle** — the lessons file generalizes "deterministic generation is a prerequisite for drift guards," and the persona generator implements it correctly.
5. **Sync guard rails** — git-clean guard (trips on no-git/not-a-repo too), source pre-flight, dry-run, distinct exit codes 0-4, dual `__pycache__` defense (`sync_from_kit.py:56-68,263-286`).

## Improvement Strategy

**Theme 1 — Close the drift loop: make staleness detectable, then automatic (LIB-01, LIB-06).**
Build the MI-19 follow-up: `sync_from_kit.py` writes a `codex_engine_version` stamp (content hash of the shipped `_scripts/` tree + Library HEAD SHA) into each consumer, plus a `--check` mode that compares stamp vs canon and reports per-file drift including MERGE-NEW-skipped files that differ upstream. Then a scheduled Routine (the vendored `scripts/task_driver.py` machinery already exists in-repo) runs `--check` across consumers and drafts re-sync PRs. *Trade-off:* the stamp adds a tracked file to every consumer and a hash-discipline burden on Library releases; alternative (full byte-scan each time) is simpler but O(consumers × files) and needs cross-repo read access. *Done signal:* `sync --check` exits non-zero on the 6 known-stale consumers today, zero after re-sync; MI-19 flipped RESOLVED; no consumer >1 release behind at the next portfolio audit.

**Theme 2 — Govern consumer personas like Library's own (LIB-02).**
Either (a) Sync renders + OVERWRITEs the consumer's `.claude/personas/CLAUDE.librarian.md` from the shipped `_context/CODEX_LIBRARIAN.md` (extends the proven generated-artifact pattern; one new OVERWRITE action), or (b) teach `generate_persona_dropin.py` a consumer-mode canonical lookup (`_context/CODEX_LIBRARIAN.md` fallback) and have consumer CI run `--check`. *Trade-off:* (a) violates the current ".claude/* never touched" contract — needs an explicit carve-out documented in the docstring NEVER-list; (b) keeps the contract but stays manual (re-creating LIB-01 one ring out). Recommend (a) with the carve-out. *Done signal:* all persona-carrying consumers byte-converge on one generated revision; eddyandwolff's missing drop-in materializes via `/sync`.

**Theme 3 — Pay the governance debt before canon promotion (LIB-03).**
Dispatch the owed Regime-B Auditor on the Session 14 diff; only then promote `consequence`/verbatim-policy to Codex canon (the todo.md inbound-handoff backlog). *Trade-off:* none real — this is the repo's own declared rule; skipping it normalizes "owed" verdicts. *Done signal:* sessions.md records the verdict; canon promotion PR cites it.

**Theme 4 — Keep the map honest cheaply (LIB-04).**
Refresh the 5 stale ROOT_INDEX rows, and consider generating the volatile counts (test count, MI range, script counts) via a tiny audit script (the repo already has 5 `audit_*.py` — an `audit_root_index.py` fits the house pattern) rather than hand-maintaining. *Trade-off:* another generator to maintain vs. accepting periodic manual drift; given two snapshots have already drifted (~589 → 644), generation wins. *Done signal:* ROOT_INDEX counts match disk at next audit without a hand edit in between.

## Task Plan

**Milestone 0 — Hygiene (≤1 session, no design decisions)**
- Refresh CLAUDE.md ROOT_INDEX rows: tests 644, MI-01..MI-19, 26 root `.py` / 4 archived `.ps1`, 7 config YAMLs; delete or materialize the `0-Inbox/` row. (LIB-04)
- Add `"_archive"` to the Sync copytree ignore patterns + 1 test asserting consumers don't receive it. (LIB-05)
- Guard the `int()` branch in `_parse_value` (try/except → fall through to string) + 2 regression tests (`--5`, `-`). (LIB-07)

**Milestone 1 — Drift detection (1 sprint; delta-force already PROCEED)**
- `sync_from_kit.py`: write `codex_engine_version` stamp on every sync; add `--check` (compare stamp + per-file hash incl. MERGE-NEW-skipped upstream diffs); tests for stamp write, check-clean, check-stale, skipped-but-differs report. (LIB-01, LIB-06)
- Re-sync the 6 stale consumers (operator-go per repo; eddyandwolff first per MI-19, then Mentor/supplystationusa/isommelier/EMCC/EMCC.DFDU); flip MI-19 → RESOLVED.

**Milestone 2 — Persona governance (1 sprint, gated)**
- Council/delta-force the `.claude/*` carve-out decision; implement Sync persona delivery (Theme 2 option a) + consumer-mode `--check`; converge all consumer drop-ins; close the `tasks/todo.md:118` content-side item in the same arc. (LIB-02)

**Milestone 3 — Automation + canon (ongoing)**
- Scheduled Routine running cross-consumer `sync --check` + drafting re-sync PRs; dispatch the owed Session-14 Auditor; then the canon promotion of `consequence` + verbatim-only policy (todo.md inbound-handoff backlog). (LIB-01, LIB-03)

### Quick Wins
1. ROOT_INDEX row refresh — 10 minutes, kills 5 verified doc inaccuracies. (LIB-04)
2. `ignore=shutil.ignore_patterns("__pycache__", "_archive")` — one line + one test. (LIB-05)
3. `try: return int(s) except ValueError: pass` — one guard + two tests. (LIB-07)

### Top-3 sketches

**1. Version stamp + `--check` (LIB-01)** — in `sync_from_kit.py`:
```python
def _engine_fingerprint(scripts_dir: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(scripts_dir.rglob("*.py")):
        if "__pycache__" in p.parts or "_archive" in p.parts: continue
        h.update(p.relative_to(scripts_dir).as_posix().encode()); h.update(p.read_bytes())
    return h.hexdigest()
```
After a successful real-run, write `Biz.Automation/wikisys.<consumer>/_scripts/CODEX_ENGINE_VERSION` containing `fingerprint=<hex>\nsynced_from=<library HEAD sha if resolvable>\n`. `--check`: recompute fingerprint of both sides, compare, also diff MERGE-NEW targets vs sources; exit 0 in-sync / 1 stale. New action kind keeps the existing plan/print machinery.

**2. Sync-delivered consumer persona (LIB-02)** — add to `_build_plan` an OVERWRITE action `target=.claude/personas/CLAUDE.librarian.md`, `source=rendered`, where the content is `generate_persona_dropin.render_dropin(codex_librarian_text, "Biz.Automation/wikisys.<consumer>/_context/CODEX_LIBRARIAN.md")` (import the existing pure renderer; write via a `content` field on Action since there's no source file). Document the `.claude/` carve-out in the docstring NEVER-list with an explicit exception line.

**3. `audit_root_index.py` (LIB-04)** — house-pattern audit script: parse CLAUDE.md ROOT_INDEX table rows containing countable claims (regex `~?(\d+) (tests|root .py|templates|YAML)` + `MI-01\.\.MI-(\d+)`), recompute from disk (`unittest` discovery count via `loader.discover().countTestCases()`, `len(glob)`, max MI number in MIGRATION-ISSUES.md), emit findings to `wikisys.library/_dashboards/root_index_audit.md`; repo-guard test asserts 0 mismatches.

## Open Questions

1. **Persona delivery contract:** is the `.claude/* never touched` rule (sync_from_kit.py:46) operator-locked, or can Sync get a carve-out for the generated Librarian drop-in? (Blocks Milestone 2.)
2. **MERGE-NEW staleness policy:** when a consumer's `_config/` file differs from upstream, should `--check` report it (noise risk: legitimate customization) or only report files that are byte-equal to an *older* upstream revision (needs the version history)?
3. **MI-19 scan standard:** should the registry's blast-radius method be amended to byte-equality (this audit shows the feature-probe "CURRENT" list is wrong for 6 repos), or is feature-parity the intended bar?
4. **eddyandwolff:** MI-19 says it was re-synced ("now re-synced", `MIGRATION-ISSUES.md` MI-19 verified-blast-radius), yet its `doc_lint.py` is still at the stale revision and it has no Librarian drop-in — did that re-sync land on `main`? Unverified which is true.
5. **Skip accounting:** 5 MI-16 retired modules + 3 in-suite `s` markers appear in dot-output but the runner reports skipped=6 — exact composition not itemized (cosmetic; suite is OK either way).

## Appendix: Machine-Readable Findings

```yaml
findings:
  - id: LIB-01
    dimension: sync-and-consumer-drift
    severity: high
    confidence: verified
    priority: act-now
    files:
      - Biz.Automation/wikisys.library/_scripts/sync_from_kit.py:1-74
      - Biz.Automation/wikisys.library/_scripts/_lib/doc_lint.py
      - MIGRATION-ISSUES.md:286-291
    summary: >-
      Sync is purely manual with no version stamp; 6/7 sampled consumers
      (Mentor, eddyandwolff, supplystationusa, isommelier, EMCC, EMCC.DFDU)
      carry doc_lint.py at exactly the pre-Session-14 revision (76acd58c... =
      git show 405064e~1) vs canonical e889e5c7...; only tat_app is current.
      MI-19's feature-probe scan mislabels these CURRENT. Stale consumers lack
      the fail-open gate fix.
    roadmap_tag: MI-19
  - id: LIB-02
    dimension: persona-governance
    severity: high
    confidence: verified
    priority: act-now
    files:
      - Biz.Automation/wikisys.library/_scripts/generate_persona_dropin.py:106-131
      - Biz.Automation/wikisys.library/_scripts/sync_from_kit.py:43-46
    summary: >-
      OBS-4 drift guard covers only Library's own Librarian drop-in. Sync never
      touches consumer .claude/*, and generate_persona_dropin.py cannot resolve
      the canonical in a consumer (expects wiki.*/git/codex/, consumers have
      _context/). In the wild: 3 distinct drop-in hashes (Library fe1d404c,
      Mentor ec719216, supplystationusa+isommelier 8eb5e3df); eddyandwolff has none.
    roadmap_tag: OBS-4-residual
  - id: LIB-03
    dimension: governance-process
    severity: medium
    confidence: verified
    priority: act-now
    files:
      - tasks/sessions.md (Session 14)
      - Biz.Automation/wikisys.library/_scripts/_lib/doc_lint.py:297-385
    summary: >-
      Session 14 Level-2+ engine change (caution-lint) shipped with the
      mandatory Regime-B Auditor verdict self-declared as owed; no later
      session records the dispatch. Blocks the consequence-field canon promotion.
    roadmap_tag: session-14-owed-audit
  - id: LIB-04
    dimension: doc-accuracy
    severity: medium
    confidence: verified
    priority: act-now
    files:
      - CLAUDE.md (ROOT_INDEX)
    summary: >-
      5 of 8 sampled ROOT_INDEX rows stale: tests "~589" vs 644 actual;
      "MI-01..MI-16" vs MI-19; "20 root .py + 5 launcher .ps1" vs 26 root .py
      + 4 archived .ps1; "_config 5 YAML" vs 7; 0-Inbox/ row but no such dir on disk.
    roadmap_tag: null
  - id: LIB-05
    dimension: sync-semantics
    severity: low
    confidence: verified
    priority: automate
    files:
      - Biz.Automation/wikisys.library/_scripts/sync_from_kit.py:271-275
      - Biz.Automation/wikisys.library/_scripts/_archive/launchers/
    summary: >-
      Sync's _scripts copytree ignores only __pycache__, so 4 retired
      Lattice-2.0 PowerShell launchers under _archive/ ship into every consumer.
    roadmap_tag: null
  - id: LIB-06
    dimension: sync-semantics
    severity: low
    confidence: verified
    priority: automate
    files:
      - Biz.Automation/wikisys.library/_scripts/sync_from_kit.py:232-247
    summary: >-
      MERGE-NEW-ONLY for _config/_template means upstream fixes never reach
      existing consumers and Sync emits no differs-from-upstream signal for
      skipped files; intentional semantics, missing staleness report.
    roadmap_tag: MI-19
  - id: LIB-07
    dimension: parser-robustness
    severity: low
    confidence: verified
    priority: automate
    files:
      - Biz.Automation/wikisys.library/_scripts/_lib/frontmatter.py:427
      - Biz.Automation/wikisys.library/_scripts/_lib/frontmatter.py:371-386
    summary: >-
      _parse_value raises uncaught ValueError on '--5'-class scalars (verified
      live); unquoted '#' truncates values (title: My #1 page -> 'My'). Outside
      the documented subset; raise-in-walk is the repo's own fail-open class.
    roadmap_tag: null
  - id: LIB-08
    dimension: parser-robustness
    severity: low
    confidence: verified
    priority: ignore
    files:
      - Biz.Automation/wikisys.library/_scripts/_lib/frontmatter.py:63
    summary: >-
      Module-level WIKI_ROOT resolution at import time makes _lib unimportable
      outside a marker-bearing tree; loud failure, all real layouts covered.
    roadmap_tag: null
canonical_artifacts:
  - path: wiki.codex/git/codex/INGEST_PROCEDURE.md
    sha256: 5262c3b608b2d5714451a4fc6ae8c2f06376a381822f1851e9585e1a1ba37edd
    note: matches expected ~5262c3b6 prefix from consumer-side checks
  - path: wiki.codex/git/codex/SEMANTIC_LINT_PROCEDURE.md
    sha256: 1c9545eb1b3f8140914c7b82911a7b0b299054bebfb1fca31f914c32df73cb40
    note: matches expected ~1c9545eb prefix
  - path: .claude/personas/CLAUDE.librarian.md
    sha256: fe1d404c1c71d75102452f34ef43c5465fbe289a02f56a80cd479ad7cb09e140
    note: GENERATED drop-in; matches expected ~fe1d404c; byte-matches deterministic render of CODEX_LIBRARIAN.md (test_persona_dropin 8/8)
  - path: .claude/personas/CLAUDE.auditor.md
    sha256: 885009115c0d532727a2351ff2420704a03f9887969bed5bb73c878535a69bd3
    note: exact match to expected DFDU-canonical hash; consumers Mentor + eddyandwolff byte-equal
  - path: Biz.Automation/wikisys.library/_scripts/_lib/doc_lint.py
    sha256: e889e5c78e5ba452495b1b9bf85a87d18d1d195a49c0752ee0a99a1312296937
    last_modified_commit: "405064e 2026-06-06 Session 14: caution-lint spike + qa-sweep hardening + MI-19 advisory (#29)"
    consumers_behind: [Project-Mentor, eddyandwolff, supplystationusa, isommelier, EMCC, EMCC.DFDU]
    consumers_current: [tat_app]
    stale_consumer_sha256_prefix: 76acd58c52876a7c (= 405064e~1 revision)
cross_repo:
  auditor_persona: byte-equal-to-DFDU-canonical (885009115c0d5327...); consumers sampled byte-equal
  modules_manifest: module.json v1.1.0 present (producer marker); emcc.modules.json absent by design — coherent with marker-walk contract (frontmatter.py:69-71)
  local_zone_tracked_files: 0 (git ls-files wiki.codex/local/ empty; rule .gitignore:75 wiki.*/local/ verified via git check-ignore)
test_run:
  commands:
    - "python -m unittest discover -s tests -t .  (from /home/user/EMCC.Library)"
    - "python -m compileall -q Biz.Automation/wikisys.library/_scripts bootstrap.py scripts tests"
    - "python -m unittest tests.test_persona_dropin -v"
  results:
    - "unittest discover: Ran 644 tests in 1.184s — OK (skipped=6); re-run confirmed 644 OK (skipped=6) in 1.296s"
    - "compileall: exit 0, no errors"
    - "test_persona_dropin: 8/8 OK (includes on-disk byte-match drift guard)"
```
