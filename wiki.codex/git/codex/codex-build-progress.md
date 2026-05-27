# Codex v1.0 — Build Progress

> Snapshot of where we are and what's left. Pair with `tasks/todo.md` (active sprint, Goal-Driven) and `codex-build-plan.html` (readiness scoring per item). This file is the bird's-eye view; those two are the day-to-day.
>
> Updated EOD 2026-05-01.

> **Working with four surfaces (added 2026-05-05):** Codex is built collaboratively across You (director), Claude Chat (strategist/planner), Claude Cowork (framework editor), and Claude Code (builder/tester). Each surface has a distinct write lane per `CLAUDE.md > WRITE_AUTHORITY`. Cowork edits framework files (this file included); Code writes scripts, tests, and generated content. Reads are unrestricted. See `CLAUDE.md > R_WORKFLOW` for the full Develop and Build flows.

## Where we are now

**Phase 0 — Complete.** Workflow scaffolding (CLAUDE.md, tasks/, .claude/skills/) is in place.
**Phase 1 — In progress.** 4 of 54 items done (~7.4%). P4 (`collect_open_questions.py`) shipped 2026-05-01 with 11 tests green; total project test count is **22, all passing**. **P5** (`build_completion_dashboard.py`) is next-task GO — Goal-Driven plan to land in `tasks/todo.md` In Progress before any code.
**Phase 2 — Not started.** Begins after P54 self-test passes; first consuming project is Iron Soul.

## Progress at a glance

| Sprint | Range | Items | Status | Done |
|---|---|---|---|---|
| **Phase 0** — Workflow scaffolding | 0.A–0.H | 8 | ✅ Complete (1 deferred, 2 N/A) | 5/5 applicable |
| **Sprint T1** — Foundation | P1–P3 | 3 | ✅ Complete | 3/3 |
| **Sprint T2** — Scripts & scaffolds | P4–P20 | 17 | 🟡 P4 done, P5 next | 1/17 |
| **Sprint T3** — Configs & canon | P21–P31 | 11 | ⚪ Not started | 0/11 |
| **Sprint T4** — Templates & procedures | P32–P49 | 18 | ⚪ Not started | 0/18 |
| **Sprint T5** — Entry points & self-test | P50–P54 | 5 | ⚪ Not started | 0/5 |
| **Phase 1 total** | P1–P54 | **54** | **🟡 In progress** | **4/54 (~7.4%)** |
| **Phase 2** — First consuming wiki | — | — | ⚪ Not started | — |

---

## Phase 0 — Workflow Scaffolding ✅

| | Step | Status | Note |
|---|---|---|---|
| 0.A | Documentation skeleton (CLAUDE.md, tasks/*.md) | ✅ | Synergized from Workflow Foundation v1.2 + Codex working notes |
| 0.B | Claude Code skills (.claude/skills/) | ✅ | Folder exists; verify protocol followed per CLAUDE.md. Skill files (verify.md, go.md) optional, not authored — Claude Code runs commands directly from D_VERIFICATION. |
| 0.C | Opus 4.7 config | N/A | Defaults used |
| 0.D | Verification wiring | ✅ | Stages 1, 3, 5 only (compileall + unittest + self-test bootstrap). No formatter, no build step. |
| 0.E | First real session | ✅ | Session 002 = P1 |
| 0.F | Parallel session test | — | Skipped (single session per turn) |
| 0.G | GitHub ↔ Project sync | Deferred | No remote (decided 2026-05-01). Revisit if/when Codex goes public. |
| 0.H | Project-specific adaptations | ✅ | All Rooms populated, lessons.md seeded with 5 conventions + aggregator-return-contract entry |

---

## Phase 1 — Codex v1.0 Build (P1 → P54)

### Sprint T1 — Foundation (P1–P3) ✅

Everything downstream imports from here. Done first because nothing else can compile without it.

- [x] **P1** — `_scripts/_lib/frontmatter.py` (Session 002; YAML-subset parser; 11 tests, all green)
- [x] **P2** — `CHANGELOG.md` (Session 003; `# v1.0 — <pending>`, date swapped at P54)
- [x] **P3** — `PROJECT_WIKI_BUILD_SPEC.md` (Session 003; byte-copy of spec; hash verified)

### Sprint T2 — Scripts & Scaffolds (P4–P20) 🟡 1/17

The actual logic of Codex. 15 automation scripts + 2 scaffold helpers. Order is dependency-driven: simplest aggregator first (validates the script template), validators next, complex tools last, orchestrator + sync at the end.

- [x] **P4** — `collect_open_questions.py` (Session 004; 11 tests; pinned the aggregator API `run(wiki_root: Path) -> dict`, the 5-field dashboard frontmatter, the bold-label summary lines, and the filename-stem wikilink convention — all four inherited by P5–P19)
- [ ] **P5** — `build_completion_dashboard.py` 🔵 **NEXT** — red/yellow/green roll-up; same walker + dashboard format as P4, banded by completion (ready ≥ 80, solid 55–79, outlined 30–54, gap < 30)
- [ ] **P6** — `validate_terminology.py` — forbidden-terms scan
- [ ] **P7** — `validate_canon_integrity.py` — `status: ready` enforcement
- [ ] **P8** — `validate_reveal_conceit.py` — public-page leak scan
- [ ] **P9** — `check_cross_refs.py` — broken `[[wikilinks]]` + orphans
- [ ] **P10** — `check_cascade.py` — source vs derived mtime
- [ ] **P11** — `check_framework_briefing_sync.py` — framework ↔ public_pair
- [ ] **P12** — `check_canon_consistency.py` — page-vs-canon + page-vs-page
- [ ] **P13** — `check_concept_coverage.py` — entities mentioned but no page (NEW v1.1)
- [ ] **P14** — `steel_thread_tracker.py` — multi-layer feature manifest
- [ ] **P15** — `build_canon_drift_report.py` — canon snapshot + diff
- [ ] **P16** — `delta_source_docs.py` — source diff + cascade impact
- [ ] **P17** — `scaffold_brain_dump.py` — scaffold helper
- [ ] **P18** — `scaffold_source.py` — scaffold helper (NEW v1.1)
- [ ] **P19** — `update_dashboards.py` — orchestrator (runs all aggregators + validators; consumes the `dashboard_path: Path` return key from every aggregator P4–P18)
- [ ] **P20** — `sync_from_kit.py` — pull infrastructure into a wiki

### Sprint T3 — Configs & Canon (P21–P31) ⚪ 0/11

Empty templates with commented examples. No logic. Each is structurally valid (`rules: []` for empty lists) and parseable by `_lib/frontmatter.py`.

- [ ] **P21** — `_config/README.md`
- [ ] **P22** — `_config/forbidden_terms.yaml`
- [ ] **P23** — `_config/reveal_leak_patterns.yaml`
- [ ] **P24** — `_config/cascade_map.yaml`
- [ ] **P25** — `_config/steel_threads.yaml`
- [ ] **P26** — `_config/concept_coverage.yaml` (NEW v1.1, optional)
- [ ] **P27** — `_canon/README.md`
- [ ] **P28** — `_canon/counts.yaml`
- [ ] **P29** — `_canon/roster.yaml`
- [ ] **P30** — `_canon/taxonomy.yaml`
- [ ] **P31** — `_canon/timeline.yaml`

### Sprint T4 — Templates & Procedures (P32–P49) ⚪ 0/18

Page templates `bootstrap.py` copies into every new wiki. P32 + P33 ship verbatim from the procedure files at the install root — never paraphrase.

**`_context/` files:**
- [ ] **P32** — `_context/INGEST_PROCEDURE.md` (verbatim from `INGEST_PROCEDURE.md`)
- [ ] **P33** — `_context/SEMANTIC_LINT_PROCEDURE.md` (verbatim)
- [ ] **P34** — `_context/CLAUDE_CONTEXT_RULES.md` (per-project; must include the 4 Q&A Behavior rules)

**Page templates:**
- [ ] **P35** — `Home.md`
- [ ] **P36** — `00-Start-Here/Project-Overview.md`
- [ ] **P37** — `00-Start-Here/How-to-Use-This-Wiki.md`
- [ ] **P38** — `00-Start-Here/Glossary.md`
- [ ] **P39** — `00-Start-Here/Terminology-Rules.md`
- [ ] **P40** — `04-Contributing/Update-Cascade.md`
- [ ] **P41** — `04-Contributing/File-Routing.md`
- [ ] **P42** — `04-Contributing/Style-Guide.md`

**Workflow folders & logs:**
- [ ] **P43** — `_brain_dump/README.md`
- [ ] **P44** — `_decisions/README.md`
- [ ] **P45** — `_decisions/ingest-log.md` (NEW v1.1)
- [ ] **P46** — `_inbox/README.md`
- [ ] **P47** — `_sources/README.md` (NEW v1.1)
- [ ] **P48** — `_sources/raw/README.md` (NEW v1.1)

**Confidential tier:**
- [ ] **P49** — `_confidential/Confidential_Profile.md`

### Sprint T5 — Entry Points & Self-Test (P50–P54) ⚪ 0/5

The bits that turn the folder of scripts into a usable tool. P50 is the big one — it's what consumes everything T1–T4 produced.

- [ ] **P50** — `bootstrap.py` (the scaffolder; replaces `|` with `/` in template filenames)
- [ ] **P51** — `README.md` (Codex-level docs; quickstart + pointer to spec)
- [ ] **P52** — Bootstrap operation test (spec §4.1)
- [ ] **P53** — Sync operation test (spec §4.2)
- [ ] **P54** — Ingest operation test (spec §4.3) + final self-test bootstrap (spec §7 Phase 6)

**P54 is the gate.** When it passes, we update `CHANGELOG.md` first line from `# v1.0 — <pending>` to the actual completion date. Codex is then v1.0 done.

---

## Phase 2 — First Consuming Wiki ⚪

Begins after P54 passes. Codex itself is then frozen until v1.1 work; Phase 2 is using the tool.

- [ ] Bootstrap Iron Soul wiki at `D:\Claude Projects\Code Name Iron Soul\wiki\`
- [ ] Customize: `01-*` domain folders, `_canon/*.yaml`, `_confidential/`, `_context/CLAUDE_CONTEXT_RULES.md`, `Home.md`
- [ ] Run dashboards (`python _scripts/update_dashboards.py`) — confirm 0 errors
- [ ] Ingest first source (sets the precedent for ingest discipline)
- [ ] Stress-test all three operations end-to-end against a real project
- [ ] Lessons feed back: anything awkward → Codex v1.1 backlog (deferred items: framework-export tooling, the deferred `check_concept_coverage` "dedicated page" signal, anything else surfaced)

---

## Notes on what each sprint produces

- **T1** = the foundation library + version + spec copy. Nothing in T2–T5 can compile without `_lib/frontmatter.py`.
- **T2** = the actual *logic* of Codex. By the end of T2 you can run validators against a wiki — but the wiki has to come from somewhere (testing fixture during T2; real bootstrap at P50). P4 established the precedents (aggregator API, dashboard format, summary-line shape, wikilink convention) that the rest of T2 inherits.
- **T3** = empty templates with structural validity. No logic, just files that need to exist for `bootstrap.py` to copy them.
- **T4** = page templates. Same story — files that get copied. The two procedure files (P32, P33) are the only items in this sprint that are byte-sensitive.
- **T5** = `bootstrap.py` (P50) brings everything together; the README explains what to do with it; P52–P54 prove the three operations actually work end-to-end.

## Working rhythm

Each P-item:
1. Pre-plan questions if the spec has buildable ambiguity (only some items)
2. Goal-Driven plan in `tasks/todo.md` In Progress
3. Plan reviewed in chat → GO
4. Build + test in isolation
5. `/verify` Stage 1 + Stage 3 (Stage 5 only at P54)
6. EOD: update `CLAUDE.md` `R_STATE`, append to `tasks/sessions.md`, move item to `D_DONE`, clear `In Progress`
7. Stop. Wait for next-task GO.

Trivial items (P2, P3, P21 README files, etc.) batch into single turns. Complex items (validators, P50) get full Goal-Driven treatment.
