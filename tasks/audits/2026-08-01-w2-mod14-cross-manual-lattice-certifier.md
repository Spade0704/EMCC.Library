# CERT VERDICT - W2-MOD-14 cross_manual consume (PR #76)

- **Verdict:** CERT_FAIL (one blocking finding, B1; the wiring is correct and well tested - the
  DEFAULT it activates silently deletes 48% of this repo's own cross-link graph)
- **Loop:** LOOP-DEFINITION-wave-e-w2-rest-certifier (WAVE-E Phase J)
- **Seat checklist:** EMCC `tasks/checklists/wave-e-w2-rest-certifier.md`
- **Certifier:** claude:EMCC-ExternalCertifier (certifier_id: claude, certifier_model: claude)
- **Builder:** grok:EMCC-dfdu (builder_llm/builder_model: grok) - CF3 decorrelation holds
- **Auditor:** grok:EMCC-Auditor, AUDITOR_PASS
- **Handoff:** `0-Inbox/grok-audit/2026-08-01-w2-mod14-cross-manual.md`, attempt 1
- **Certified range examined:** 3782f5ea..dfacbfa (product `f619595`; tip **pushed**)
- **Date:** 2026-08-01

## Summary

The engineering is good. `cross_manual` really was inert before this atom - I proved that rather
than reading it - and it is now a real consumer, gated in the right place, with tests that red when
I disable the gate, when I stop the registry loading, or when I flip the default. Criteria 1, 2 and
3 all pass on their own terms, and MOD-15 is correctly not bundled.

I am failing on the consequence nobody measured. The schema default for `cross_manual` is **false**,
no topic in the real registry sets it, and this atom is what turns that dormant default into
enforcement. Running the shipped script the way it is meant to be run - `python
cross_link_topics.py`, no arguments, which resolves to this module's own `wiki.codex/git` - deletes
**300 of 630 `related_files` edges (48%)** across 23 of 27 pages, every one of them cross-container,
`Home.md` alone losing 22. The run prints nothing and exits 0.

That is a silent mass edge drop shipped in the same wave as MOD-15, whose entire subject is that
silent edge drops are unacceptable - and MOD-15's warning does not cover this path.

## Pre-gate (CF2, CF4, CF8)

```
cd EMCC.Library && python <EMCC>/scripts/validate_cert_handoff.py 0-Inbox/grok-audit/2026-08-01-w2-mod14-cross-manual.md
PASS
exit 0
```

`status: pending` + `auditor_verdict: PASS` + `auditor_id` + `auditor_ref` present. On the previous
tick this handoff read `awaiting_auditor` on `origin/grok/w2-mod14-cross-manual-consume` and I
refused it per CF8 without opening product. One atom this tick (CF1).

**Zero involvement:** I did not build, audit or advise this atom. First contact with the product
diff was this cert.

## Product pins (identical at product f619595 and tip dfacbfa)

| Path | sha256 |
|---|---|
| Biz.Automation/wikisys.library/_scripts/cross_link_topics.py | 4a63cd1831be19af... |
| tests/test_cross_link_topics.py | 54418cb795c8f533... |

Changed paths in range: one product script, the test file, plus handoff / auditor / evidence /
sample docs and the orchestrator log. **MOD-15 is not bundled** - `grep -c
"fail_on_truncation\|truncation_events"` on this branch's `cross_link_topics.py` returns **0**,
which is criterion 4's no-bundling requirement checked as a fact.

## Floors RUN by certifier (detached worktree at dfacbfa; live tree never mutated)

| Floor | Command | Result | Exit |
|---|---|---|---|
| Declared | `python -m unittest tests.test_cross_link_topics -q` | **Ran 52, OK** | 0 |
| CI-equivalent | `python -m unittest discover -s tests -t .` | **Ran 962, OK (skipped=6)** | 0 |

Builder and Auditor claim of "52 OK" reproduces exactly.

## PREM-1 - was `cross_manual` actually inert?

Not taken from the evidence. Ran the **pre-atom** script (`origin/main`) in its own worktree against
a fixture whose registry declares `cross_manual: false`, with pages in two containers:

```
PRE-ATOM, registry says cross_manual: false
   cross-container [[C]] in A's see-also: True     <- the flag was ignored
   same-container  [[B]] in A's see-also: True
```

Post-atom the same shape excludes `[[C]]`. The field was genuinely dead config and this atom is what
gives it teeth. That part of the atom's story is true.

## Falsifiers (isolated worktree, proof-of-application, restored)

| Probe | Mutation | Applied | Suite |
|---|---|---|---|
| **P1** | gate disabled (`allow_cross` always True) | YES | FAILED (failures=3): `test_cross_manual_false_same_container_only`, `test_falsifier_ignoring_flag_would_include_cross`, `test_run_loads_cross_manual_from_topics_yaml` |
| **P2** | registry never loaded (`if False:` on the `topics.yaml` branch) | YES | FAILED (failures=1): `test_run_loads_cross_manual_from_topics_yaml` |
| **P3** | invert the default (unknown topic denies cross) | YES | FAILED (failures=1): `test_run_honors_disambiguate` |
| **P4** | present map + topic **absent from it** now denies cross | YES | **Ran 52, OK, exit 0** - see C1 |

P1 and P2 are the good news: the gate and the registry load are both load-bearing. P3 shows the
allow-by-default behaviour is pinned, though by a pre-existing test rather than a new one. P4 is the
gap - see C1.

## Criteria

| # | Criterion | Result |
|---|---|---|
| 1 | `cross_manual` read by a real consumer with tests | **PASS on its face** - real consumer, 5 new tests, PREM-1 proves prior vacuity. But see B1: consuming a never-configured field with a restrictive default is a data migration, not just a wiring change |
| 2 | Type-check alone is not the only control | **PASS** - the control is now behavioural, verified by P1/P2 |
| 3 | Falsifier proves prior vacuity or new consumer fails closed | **PASS** - PREM-1 above |
| 4 | dual-PASS + human merge; do not bundle MOD-15 | not bundled (verified); dual-PASS blocked by B1 |

## BLOCKING finding

**B1 - the atom activates a dormant restrictive default and silently removes 48% of this repo's own
cross-link graph.**

*The setup.* `Topic.cross_manual` defaults to `False` (`_lib/topics.py:57`, `raw.get("cross_manual",
False)` at :210). The only real registry in the repo,
`Biz.Automation/wikisys.library/_canon/topics.yaml`, has **10 topics and sets `cross_manual` on none
of them** - the single occurrence of the string in that file is a comment listing optional keys. So
all 10 inherit `False` by omission. Before this atom that was harmless, because the field was inert
(PREM-1). This atom makes it binding.

*The measurement.* Two detached worktrees, `origin/main` and `dfacbfa`, each running the shipped
entry point with no arguments - `python cross_link_topics.py`, which resolves `WIKI_ROOT` via
`find_wiki_content_root()` to `wiki.codex/git`, this module's only wiki and the one holding its
canon (`module.json` -> `canon_docs: wiki.codex/git/codex/CODEX_BUILD_SPEC_v1_3.md`):

```
pages with related_files: pre=27 post=27
TOTAL EDGES  pre=630  post=330  removed=300  (48% of the graph)
pages whose edge set CHANGED: 23 of 27
removed edges that are CROSS-container: 300 ; SAME-container: 0

worst-hit pages
   -22 edges  Home.md
   -19 edges  04-Contributing/Style-Guide.md
   -19 edges  00-Start-Here/Glossary.md
   -18 edges  00-Start-Here/Project-Overview.md
   -16 edges  02-Operations/Sync.md
```

Both runs exit 0. Neither prints a warning. `Cross-Link-Generation.md` goes from 19 related files to
10, dropping `Home.md`, `Glossary`, and every `02-Operations/` page.

*Why it matters beyond the number.* framework/18 makes this graph the routing substrate - load one
page, then expand one hop via `related_files`/wikilinks. Cutting every cross-container edge is
precisely the hop that crosses from Start-Here or Home into Architecture or Operations. Halving it
is a change to how the wiki is navigated, and it arrives as a side effect of a schema default nobody
chose.

*Why it is a certifier stop and not a taste objection.* Three things together:
1. **Nobody opted in.** Not one topic declares `cross_manual: false`. The restriction comes from an
   omitted optional key.
2. **It is silent.** No warning, no counter in the summary dict, exit 0. The only new field in the
   returned dict is `topic_cross_manual_loaded`, which reports that the registry was read - not that
   anything was dropped.
3. **The wave's other atom exists to forbid exactly this.** W2-MOD-15 makes see-also truncation loud
   - and its WARNING instruments only the `max_links` slice. A drop through the `cross_manual` gate
   happens earlier, inside `compute_related_files`, and MOD-15 never sees it. So after both atoms
   land, one class of silent edge drop is fixed and a second, larger one is introduced.

*Surgical fix - the behaviour work all stands; this is about default and visibility:*
1. **Make the drop loud** (mirror MOD-15's shape): count candidates refused by the gate, emit a
   stderr WARNING naming the page and topic, and return the count in the summary dict. Silent is the
   part that is not defensible whichever default is chosen.
2. **Decide the default deliberately.** Either treat "topic present in the registry with
   `cross_manual` unset" as **allow-cross**, so the restriction is opt-in and this change is a no-op
   until someone asks for it - which matches the back-compat intent already documented for unknown
   topics - or keep deny-by-default and ship the migration: set `cross_manual: true` explicitly on
   the 10 existing topics plus a note, so the 300 edges are removed by a decision rather than by
   omission. This is the Director's policy call, not mine; my finding is only that it must not be an
   accident.
3. **Pin whichever is chosen with a test** that exercises the registry-present / field-unset shape,
   which today is unlocked (P4).

Rework is **this atom only** (CF9). The gate placement, the alias handling, the registry-load
failure path, the `None`-map back-compat and all 52 tests stand as-is.

## Non-blocking carries

**C1 - the documented back-compat branch has no test.** The docstring promises *"Topics absent from
the map keep pre-MOD-14 back-compat (allow cross)"*. There are two such branches: map is `None`, and
map present but topic missing from it. Only the first is covered
(`test_no_registry_map_back_compat_allows_cross` passes no map at all). P4 changed the second to
deny-cross and all 52 tests stayed green. One test with a present-but-partial map closes it.

**C2 - the registry-load failure path warns, the gate itself does not.** A malformed `topics.yaml`
prints `WARNING: topics.yaml unreadable for cross_manual ...` and falls back to allow-cross, which is
the right instinct and fails open loudly. The same instinct is missing from the gate's own drops -
which is half of B1.

**C3 - declared range ends at the product commit.** The handoff declares `3782f5ea..f619595`, and
`f619595` **is** the product commit, so the declared range excludes the handoff-range commit and the
auditor artifact. I examined through `dfacbfa`; both product blobs identical at both. Tenth
consecutive atom with this shape.

**C4 - tip is pushed.** `origin/grok/w2-mod14-cross-manual-consume` is at `dfacbfa`, so PR #76 shows
the `auditor_ref` artifact. Worth recording because the unpushed-tip carry has been near-universal in
this programme; this atom does not have it.

**C5 - `cert_class` correctly still `parked-awaiting-cross-model`** with an accurate caveat. No
action.

## Disposition - CERT_FAIL

- **CF1** Handoff NOT marked done-with-PASS. Left `status: pending` for Lattice rework; I did not
  edit the immutable body.
- **CF2** Enqueue **W2-MOD-14 only** -> Lattice rework. MOD-15 is separately at CERT_FAIL on its own
  finding; the two must not be reworked as one PR.
- **CF3** Fail reason is surgical and named above with the measurement that produced it.
- Did not merge. Did not Director dual-PASS close.

## Explicit refuses

- Did not build product, act as Regime-B Auditor, merge, or dual-PASS close (CF5/CF6).
- Did not certify while the handoff read `awaiting_auditor` (CF8), and did not certify two atoms in
  one tick (CF1).
- **Did not report my first A/B measurement.** I ran the script in both worktrees, diffed
  `Biz.Automation/wikisys.library`, got zero differences, and nearly recorded "no live impact". It
  was wrong: with no argument the script resolves `WIKI_ROOT` to `wiki.codex/git`, so I had compared
  a tree the run never touched. The `git status` of the worktrees showed 23 and 22 modified files
  under `wiki.codex/`, which is what caught it. Re-ran against the actual target. A clean sweep over
  the wrong subset reads exactly like full coverage.
- Did not accept "real consumer with tests" as sufficient; asked what the consumer does to real
  content and measured it.
- Did not take the atom's claim that the field was inert - ran the pre-atom script against a
  registry that sets it.
- Did not stop at the three probes that redded; ran P4 to find the branch that does not.
- Did not fail the atom on the wiring, which P1/P2 show is genuinely load-bearing.
- Probe residue: mutations applied only in throwaway detached worktrees, reverted after each run;
  all three worktrees force-removed and pruned. The live EMCC.Library tree is clean at `76067cc`
  (only my two untracked verdict files).
