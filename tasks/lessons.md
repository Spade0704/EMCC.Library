# Lessons — EMCC.Library

> Architectural lessons captured across sessions. **Auditor NO READ** per `EMCC.DFDU/personas/CLAUDE.auditor.md` independence rule (`documents/lattice/02-PRINCIPLES-AND-WORKFLOW.md` §B). The Auditor judges artifacts, not accumulated patterns.

---

## L1 — Marker-walk beats `parent.parent` for cross-context path resolution (post-MI-17, 2026-05-27)

**Context:** Codex scripts originally hardcoded `WIKI_ROOT = Path(__file__).resolve().parent.parent` (or `.parent.parent.parent` for `_lib/`). Worked under project-codex's flat layout where `_scripts/` lived at the wiki root. Broke at Library install post-S002 when scripts moved to `Biz.Automation/wikisys.library/_scripts/` — the count-the-parents walk now resolves to `wikisys.library/`, not Library's repo root.

**Lesson:** Filesystem markers (sentinel files at the target directory) survive restructures; `parent.parent` chains do not. Three-case marker-walk implementation:

1. v1.0-shape wiki: ancestor with `Home.md` → that's the wiki root
2. v1.1-shape install: ancestor with `CLAUDE.md` AND `wiki.<name>/git/Home.md` → that wiki's `git/` is the content root
3. Library-style install (no consumer wikis): ancestor with `CLAUDE.md` + `module.json` → repo root

PR #10 lifted this into `_lib/frontmatter.py::find_wiki_root()` as the public API; all 17 scripts now `from _lib import frontmatter; WIKI_ROOT = frontmatter.find_wiki_root()`.

**Generalization rule:** When a script needs to find a directory whose path is not statically known relative to the script, **walk ancestors looking for a marker file**, never count `.parent` chains. If you find yourself writing `Path(__file__).resolve().parent.parent.parent`, that's the smell.

---

## L2 — Validators can be silently broken AND silently wrong (MI-17 → MI-18 cascade, 2026-05-27)

**Context:** `check_concept_coverage.py` had been "passing" against `WIKI_ROOT = parent.parent` (resolving to `Biz.Automation/wikisys.library/`) for all of S002 close. After MI-17 landed (PR #10) and WIKI_ROOT correctly resolved to `wiki.codex/git/`, the script immediately failed loudly: `FileNotFoundError: required canon file missing: wiki.codex/git/_canon/roster.yaml`. Until MI-17, the script was being run against the wrong tree AND reporting no errors — because the wrong tree had no concept-coverage data to check.

**Lesson:** A passing validator under broken inputs is worse than a failing one. After any path-resolution / restructure / discovery-layer change, **run all validators end-to-end against real content** before declaring the change done. Unit tests for `find_wiki_root()` would have caught the MI-17 break (and did, in `test_wiki_root_resolves_correctly`), but they did NOT catch the downstream consequence — that 16 other scripts were running against the wrong tree and silently producing wrong outputs. End-to-end validation surfaces what unit tests miss.

**Practice:** Post-restructure verification recipe must include "run every dashboard / validator script against the canonical dogfood tree, eyeball outputs for emptiness or wrongness, not just exit code."

---

## L3 — System/content split needs uniform marker-walk treatment (MI-18, 2026-05-27)

**Context:** S002 restructured Library into system-side (`Biz.Automation/wikisys.library/_canon/`, `_config/`, `_decisions/`, etc.) and content-side (`wiki.codex/git/`). MI-17 solved discovery for the content root via marker-walk. MI-18 surfaced because `_canon/` is now system-side under v1.1 but content-side under v1.0 — scripts that read `WIKI_ROOT / "_canon"` work on v1.0 wikis (Mentor) but fail on v1.1 installs (Library).

**Lesson:** Once you adopt the system/content split, **every shared resource needs its own layout-aware discovery function**, not just `find_wiki_root()`. Candidates: `find_canon_dir()`, `find_decisions_dir()`, `find_config_dir()`. Same marker-walk pattern; same `_lib/` foundation; same back-compat shim for v1.0 wikis.

**Recommendation locked into MIGRATION-ISSUES.md MI-18 option (c):** factor canon-discovery into `_lib/canon.py` (or extend `_lib/frontmatter.py`) so scripts call `find_canon_dir(wiki_root)` instead of `wiki_root / "_canon"`. S004 Phase D consolidates this fix.

**Generalization:** Any time a refactor splits one canonical location into two (or more) context-dependent locations, the FIRST thing to add is the discovery function. Do not let scripts hardcode either path; both will rot.

---

## L4 — Banner-at-current-path beats archive-relocation for staleness disposition (S003a/b, 2026-05-27)

**Context:** S002c audit produced 9 ARCHIVE-class files. Two options: (1) move them to an `_archive/` tree (clean separation, but breaks every cross-reference + cross-link validator), or (2) leave them in place with an archive banner at the top (preserves cross-link surface; one-line discoverability).

**Lesson:** Banner-at-current-path won S003a/b because:
- `check_cross_refs.py` keeps validating linkable paths (no false-positive broken-link surface)
- Operator + agent search results still find the file at its expected location
- Banner makes the archived status discoverable on read
- One commit per file = clean per-file blame; relocation would have been one bulk commit

Exception: Lattice 2.0 launchers/ DID get moved to `_archive/launchers/` because they were a folder of related artifacts with zero inbound cross-links — wholesale relocation was clean. **Rule of thumb:** relocate only when the entire subtree is dead AND has no inbound links; banner everything else.

---
