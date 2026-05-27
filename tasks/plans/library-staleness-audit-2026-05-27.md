# Library Staleness Audit — 2026-05-27

> Sprint **S002c** (read-only analysis). Audit of every markdown / HTML / PowerShell doc in Library against the post-S002 v1.1 canonical layout. Branch `claude/library-staleness-audit-q3x9k`; this file is the only write. No commits, no push.

## Summary

- **29 files audited** (excluding the 7 canonical Codex spec docs under `wiki.codex/git/codex/`, the canonical `Index.md` / `CLAUDE.md` / `README.md` / `module.json` / `SOURCE-HISTORY.md` / `MIGRATION-ISSUES.md` / `REORGANIZATION-INSTRUCTIONS.md` / tasks state files / `.github/workflows/test.yml` / `.gitignore`, and tests/* code).
- **7 KEEP-AS-IS** (template stubs awaiting content fill + the canonical wiki-internal Sources README).
- **13 UPDATE** (refresh canon_sources paths from `_sources/raw/` → `wiki.codex/git/raw/`; rewrite content for v1.1 CLI / scaffold-only bootstrap / script count / new audit scripts; sync template-side persona with canonical).
- **9 ARCHIVE** (content superseded by newer canonical docs; preserve with banner pointing at the supersession).
- **0 DELETE** (operator brief biases against deletion; archive is the most aggressive disposition this sweep applies).
- **0 MOVE** (apart from optional §S001 architect-notes condensation noted under Risk).

**Estimated cleanup sprint scope: medium.** Recommend splitting across two sub-sprints (see Next sprint recommendation).

---

## Per-file disposition

### KEEP-AS-IS (7 files)

- **`wiki.codex/git/00-Start-Here/Project-Overview.md`** — bootstrap template stub (`completion: 0`, `status: gap`, `last_updated: <YYYY-MM-DD>` placeholder). Content empty / "Replace this section…" prose. Preserve until Codex-documents-Codex content sprint fills it.
- **`wiki.codex/git/00-Start-Here/How-to-Use-This-Wiki.md`** — same template-stub state.
- **`wiki.codex/git/00-Start-Here/Glossary.md`** — same template-stub state.
- **`wiki.codex/git/00-Start-Here/Terminology-Rules.md`** — same template-stub state.
- **`wiki.codex/git/04-Contributing/File-Routing.md`** — same template-stub state.
- **`wiki.codex/git/04-Contributing/Style-Guide.md`** — same template-stub state.
- **`wiki.codex/git/04-Contributing/Update-Cascade.md`** — same template-stub state.

> Note: All 7 stubs share `completion: 0` + `status: gap` + the `<YYYY-MM-DD>` last_updated placeholder. They are pre-filled bootstrap output, not stale content. Deleting them would break the dogfood wiki's structural expectations (validators count gap pages against total). Leave them until they're filled or until a sprint explicitly retires the dogfood wiki's onboarding/contributing sections.

> **One canonical wiki-internal doc — also KEEP-AS-IS:** `wiki.codex/git/raw/README.md` — confirmed current (60+ lines documenting Sources/Raw ingest semantics, canon_sources discipline, versioning). Brief excluded `wiki.codex/git/codex/*` from audit scope but this file lives under `raw/` not `codex/`; flag it KEEP-AS-IS rather than miss surfacing.

### UPDATE (13 files)

| File | Stale element(s) | Recommended update |
|---|---|---|
| `wiki.codex/git/Home.md` | `canon_sources: ["_sources/raw/CODEX_BUILD_SPEC_v1_3.md §1"]`; pre-S002 last_updated; landing page may need v1.1 surface mention | Refresh canon_sources → `wiki.codex/git/raw/...` (or `wiki.codex/git/codex/...` if citing spec doc not source archive); bump last_updated; add one paragraph on v1.1 layout |
| `wiki.codex/git/01-Architecture/Cross-Link-Generation.md` | canon_sources path stale | Refresh canon_sources; content otherwise stable |
| `wiki.codex/git/01-Architecture/Design-Principles.md` | canon_sources path stale | Refresh canon_sources; 13 principles content stable |
| `wiki.codex/git/01-Architecture/Frontmatter-Schema.md` | canon_sources path stale | Refresh canon_sources; v1.3 schema body still authoritative |
| `wiki.codex/git/01-Architecture/Reference-Implementation.md` | canon_sources path stale | Refresh canon_sources; Iron Soul reference content stable |
| `wiki.codex/git/01-Architecture/Overview.md` | canon_sources path stale; "Codex v1.0" framing pre-dates v1.1 | Refresh canon_sources; add §"v1.1 update arc" pointing at S002 changes + portfolio spec; update unverified_claims (v1.2 vs v1.3 footer mismatch may now be resolved upstream) |
| `wiki.codex/git/01-Architecture/Configuration-Files.md` | Describes `_config/` + `_canon/` at wiki root; post-S002 these live at `Biz.Automation/wikisys.library/_*/`; canon_sources path stale | Rewrite to reflect v1.1 location (path now under wikisys.<name>/); canon_sources refresh; describe both Library install side AND consumer-wiki side post-Sync delivery |
| `wiki.codex/git/01-Architecture/Automation-Scripts.md` | Title "(15 + 3)" — actual count post-S002 is 22 (17 P-indexed + 5 new S002 audit scripts); "master copies in `_codex/_scripts/`" — no longer exists; canon_sources path stale | Retitle "(17 + 5 audit scripts)"; rewrite location section to `Biz.Automation/wikisys.library/_scripts/`; add 5 new S002 scripts (audit_doc_pairing, audit_gitignore, route_inbox, audit_assets, audit_local_split); canon_sources refresh |
| `wiki.codex/git/02-Operations/Bootstrap.md` | Shows `python bootstrap.py <target-wiki-path>` — v1.1 changed to `<projectname>` positional + `--full/--minimal/--code/--website` flags; scaffold-only contract (no script copy); canon_sources path stale | Full rewrite of CLI section; add scaffold-only-vs-v1.0-script-copy contrast; reference MI-16 sync gap; canon_sources refresh |
| `wiki.codex/git/02-Operations/Sync.md` | `python _scripts/sync_from_kit.py` — now at `Biz.Automation/wikisys.library/_scripts/`; MI-16 v1.0-contract carry not surfaced (sync broken against v1.1-bootstrapped wikis); canon_sources path stale | Update invocation path; add §"v1.1 known limitation" mirroring README.md (sync still at v1.0 contract); canon_sources refresh |
| `wiki.codex/git/02-Operations/Ingest.md` | `_scripts/scaffold_source.py` path stale; canon_sources path stale | Update invocation paths; canon_sources refresh; Ingest body still procedurally accurate |
| `wiki.codex/git/02-Operations/Quickstart.md` | For v1.0 ("after Codex v1.0 is in production"); v1.1 CLI differs; canon_sources stale | Rewrite for v1.1 (new CLI + scaffold-only contract); canon_sources refresh |
| `wiki.codex/git/codex/Obsidian-Setup-Guide.md` | References `documents/lattice/` (no longer in Library — moved to EMCC.DFDU per Session 1 archive disposition); references `Sources/Raw/` (now `wiki.codex/git/raw/`); 583-byte stub | Rewrite folder-structure section to match v1.1 (`wiki.codex/git/`, `Biz.Automation/wikisys.library/`); remove `documents/lattice/` reference (consumer wiki for this is now in DFDU repo) |
| `Biz.Automation/wikisys.library/_template/.claude__SEP__personas__SEP__CLAUDE.librarian.md` | 65 lines vs canonical `.claude/personas/CLAUDE.librarian.md` 93 lines; missing S002 B7 v1.1 extension (3 new ops + 5 Mentor patterns + Telegram contract); last_updated 2026-05-21 | Sync template body with canonical (drop in the +28 lines added in S002 B7); bump last_updated to 2026-05-27. **OBS-4 in S002 Auditor envelope flagged this drift risk** — Library is the first observed instance; consumers will inherit stale persona until sync runs. |

### ARCHIVE (9 files)

| File | Superseded by | Suggested archive location |
|---|---|---|
| `wiki.codex/git/01-Architecture/Folder-Architecture.md` | `tasks/plans/portfolio-folder-structure-spec.md` §(a) + spec (b) per-project punchlists. "Three folder roles" model was the Codex-internal precursor; F1-F12 portfolio resolution is the authoritative v1.1 model. Operator explicitly flagged this. | `wiki.codex/git/_archive/01-Architecture/Folder-Architecture.md` + 4-line banner pointing at the spec |
| `wiki.codex/git/01-Architecture/Wiki-Structure.md` | `tasks/plans/portfolio-folder-structure-spec.md` §(c) (canonical bootstrap output tree). Old `<project>/wiki/` shape no longer produced. | Same archive location as above |
| `wiki.codex/git/01-Architecture/File-Manifest.md` | `Index.md` ROOT_INDEX + `REORGANIZATION-INSTRUCTIONS.md`. `_codex/` layout no longer exists; superseded by `Biz.Automation/wikisys.library/`. | Same archive location |
| `wiki.codex/git/02-Operations/Build-Workflow.md` | Codex v1.0 is built. The 8-phase build-Codex workflow describes the construction of the tool itself, complete as of `project-codex` SHA `c106155` (2026-05-22) → Library extraction Session 1 (2026-05-27). Now historical. | `wiki.codex/git/_archive/02-Operations/Build-Workflow.md` |
| `wiki.codex/git/02-Operations/Claude-Behavior-Rules.md` | Rules-when-building-Codex section. Codex built. Runtime rules now live in the Librarian persona (`wiki.codex/git/codex/CODEX_LIBRARIAN.md` + `.claude/personas/CLAUDE.librarian.md`). | Same archive location |
| `wiki.codex/git/codex/codex-build-progress.md` | Session 1 + S002 close entries in `tasks/sessions.md` carry the post-extraction build state. The 7.4%-complete EOD-2026-05-01 snapshot is pre-extraction project-codex history. | `wiki.codex/git/_archive/codex/codex-build-progress.md` |
| `wiki.codex/git/codex/codex-build-plan.html` | P1-P54 build priorities; mostly shipped in Codex v1.0 (per project-codex `ccf21b7`). Visual readiness-scoring dashboard from the build phase. Historical reference value remains; not stale-in-error. | `wiki.codex/git/_archive/codex/codex-build-plan.html` OR keep at current location with a 1-line "Build-phase historical reference — superseded by REORGANIZATION-INSTRUCTIONS.md + tasks/sessions.md S001/S002" banner |
| `0-Inbox/codex-wiki-folder-org-principle.md` | `tasks/plans/portfolio-folder-structure-spec.md` (the document's principle was absorbed into the spec; F1-F12 resolution extends the audience/git/confidentiality axes the inbox doc named). Already supersedes the inbox doc's "Phase 1 logical NOW; Phase 2 physical regroup DEFERRED" — Phase 2 shipped as S002. | `wiki.codex/git/_archive/_inbox/codex-wiki-folder-org-principle.md` with banner cross-linking the spec |
| `Biz.Automation/wikisys.library/_scripts/launchers/` (4 .ps1 + README.md = 5 files) | Lattice 2.0 Nexus 4-persona model. Lattice has moved to 3.0 single-agent per `EMCC.DFDU/documents/lattice/01-LATTICE-AGENT.md`. Hardcoded paths under `D:\Claude Projects\Project Codex\...` no longer valid (paths point at the now-archived project-codex 4-clone layout). References `lattice-bridge.py` and `lattice_session_start.py` — files that STAY in project-codex archive per Session 1 A1 disposition. | `Biz.Automation/wikisys.library/_scripts/_archive/launchers/` (5 files); add an `_archive/README.md` documenting the Lattice 2.0 → 3.0 transition rationale and cross-linking `EMCC.DFDU/documents/lattice/01-LATTICE-AGENT.md`. |

> **Why archive rather than delete launchers?** They encode real lessons (Windows env-propagation footgun; setx ≠ instant; launcher inline-`$env:` pattern). `tasks/lessons.md` references them. Deleting forfeits the historical trace. Archive preserves with a sunset banner.

### DELETE (0 files)

No deletions recommended. Lean toward archive per the brief's bias.

### MOVE (0 files — see Risk notes below for one optional condensation)

No standalone moves recommended. Optional: condense `tasks/architect-notes.md §S001-codex-extraction` (lines 236-386, 150 lines covering a closed sprint) to a 5-10 line summary with a pointer at `tasks/sessions.md` Session 1 CLOSED entry. Reduces architect-notes noise post-S001-close. **Defer** — operator's preference for `tasks/archive.md` rollup may take precedence; surface as an open option.

---

## Risk notes

### Dependency-frontmatter cascades on archives

The 5 architecture-folder ARCHIVE candidates (`Folder-Architecture.md`, `Wiki-Structure.md`, `File-Manifest.md`, `Build-Workflow.md`, `Claude-Behavior-Rules.md`) are referenced as `dependencies:` from sibling architecture/operations docs:

- `dependencies: ["01-Architecture/Folder-Architecture", "01-Architecture/Wiki-Structure"]` appears in 4+ docs
- `dependencies: ["01-Architecture/File-Manifest"]` appears in 3+ docs
- `dependencies: ["02-Operations/Build-Workflow", "02-Operations/Claude-Behavior-Rules"]` appears across operations docs

Moving these to `wiki.codex/git/_archive/...` will break the `[[wikilink]]` chain that Codex's cross-link validator (`check_cross_refs.py`) catches. Two options:

- (a) **Update dependent frontmatter in same sprint** — refresh `dependencies:` paths everywhere to the archive location (mechanical but touches ~12 files).
- (b) **Leave archives at current paths with a top-banner** noting supersession; cross-link validator stays green; readers see the banner before content.

Recommend (b) — banner-at-current-path. Less churn. Operator can re-evaluate full archive-relocation in a later structural-cleanup sprint.

### Updates touching canonical spec content

The 13 UPDATE candidates DO touch the dogfood wiki's content (which IS the canonical spec for "Codex documenting Codex"). But none touch the 7 authoritative spec docs at `wiki.codex/git/codex/*` (those are explicitly out of scope). Updates touch:

- **Canon_sources path refresh** — purely mechanical; no spec semantic change. Low risk.
- **Bootstrap.md / Sync.md / Quickstart.md content rewrite** — describes v1.1 CLI + scaffold-only contract. Should be authored by someone familiar with the new bootstrap.py behavior + MI-16 sync carry. Medium risk if a casual rewriter misses the MI-16 nuance.
- **Configuration-Files.md / Automation-Scripts.md** — describes wikisys.library structure. Should cross-reference Index.md + REORGANIZATION-INSTRUCTIONS.md to keep the three docs consistent.
- **Obsidian-Setup-Guide.md** — references `documents/lattice/` which no longer exists in Library. CAVEAT: this doc is in `wiki.codex/git/codex/` which the brief excluded from audit scope as "authoritative." Surfacing it as UPDATE here because the documents/lattice/ reference is genuinely stale (path moved to DFDU repo, not Library); the doc itself is small (583 bytes / 26 lines) and the fix is a 3-line edit. Operator can override this disposition to KEEP-AS-IS if "spec doc verbatim" discipline takes precedence over stale-path repair.
- **Persona template sync** — bringing template-side persona to byte-equal with canonical. Mechanical (`cp .claude/personas/CLAUDE.librarian.md Biz.Automation/wikisys.library/_template/.claude__SEP__personas__SEP__CLAUDE.librarian.md`). Risk: template files use `__SEP__` encoding for path delimiters, so the file CONTENT is just the persona body — direct copy works. Verify with `diff` after.

### Moves conflicting with REORGANIZATION-INSTRUCTIONS.md manifest

No proposed archives or moves conflict with the manifest. The 9 archive candidates all archive into new `_archive/` subfolders, which aren't pattern-named in `REORGANIZATION-INSTRUCTIONS.md`. If the cleanup sprint formalizes `_archive/` as a recognized pattern, suggest adding a new row (P9 or P10) to the patterns table.

### Inbox triage signal

`0-Inbox/codex-wiki-folder-org-principle.md` has been in inbox since 2026-05-22 (carried from project-codex Session 1 rename). Its content is now fully absorbed into `tasks/plans/portfolio-folder-structure-spec.md`. Archiving it clears the inbox. After this audit, `0-Inbox/` would be empty — a clean Librarian-discipline signal that triage is current.

---

## Next sprint recommendation

**Scope: medium.** Recommend splitting into two consecutive sub-sprints with no operator decision required between them.

### S003a — Path-refresh + persona-template sync (quick wins; ~1 day)

13 UPDATE candidates + persona template sync. All mechanical or near-mechanical. Single PR. Per-file edits:

- 9 docs: refresh `canon_sources:` paths from `_sources/raw/` → `wiki.codex/git/raw/`
- 5 docs (Configuration-Files, Automation-Scripts, Bootstrap, Sync, Ingest, Quickstart, Home): body rewrites for v1.1 paths + CLI + MI-16 carry surface
- Obsidian-Setup-Guide: drop `documents/lattice/` reference (small doc; 3-line edit)
- Persona template: byte-equal with canonical (cp + verify)

Risk: low. No semantic spec changes. Operator review on the body-rewrite candidates (Bootstrap.md + Sync.md particularly — those have to track MI-16 nuance correctly).

### S003b — Archive sweep + banner placement (~1 day)

9 ARCHIVE candidates. Choose disposition (a) update-dependents OR (b) banner-at-current-path. **Recommend (b) banner-at-current-path** for first sweep — preserves cross-link validator green + minimal churn. Per-file work:

- Add a 4-line banner at the top of each archive candidate:
  ```
  > **ARCHIVED 2026-XX-XX:** Content historical; superseded by `<superseding-doc>`.
  > Preserved for reference; do not update. Cross-link from current docs at your own risk.
  > See `tasks/sessions.md` S00X close entry for the archival decision context.
  > Original content below this line.
  ```
- For `0-Inbox/codex-wiki-folder-org-principle.md`: move to `wiki.codex/git/_archive/_inbox/...` so the inbox empties (different from banner-at-current-path because inbox triage discipline IS the archival signal). Update dependents = 0 because the inbox doc has no inbound `[[wikilinks]]`.
- For launchers/: archive the whole `launchers/` folder to `_archive/launchers/`. No dependents in tracked code (Lattice 3.0 single-agent doesn't invoke them); confirm via `grep -r launchers` (sweep showed only `tasks/lessons.md` references — those stay as historical anchors).

Risk: low if (b) chosen; medium if (a) chosen (12-file frontmatter cascade).

### Deferred to a later sprint (NOT in S003a/S003b)

- Filling the 7 KEEP-AS-IS template stubs (Codex-documents-Codex content sprint).
- Optional condensation of `tasks/architect-notes.md §S001` to a 5-10 line summary.
- Promotion of `_archive/` as a formal pattern row (P9 / P10) in `REORGANIZATION-INSTRUCTIONS.md`.

### One-sprint alternative

If operator prefers a single sprint, combine S003a + S003b. Estimated 2 days; risk profile combines but is still low under disposition (b) for archives. Single PR but bigger surface; harder per-commit review.

**Default recommendation: split.** S003a is a clear, low-risk cleanup that retires the most-cited staleness (path refs in 13 docs + persona drift). S003b adds the archive surface, which is more about content-policy than mechanical edits and warrants its own review.
