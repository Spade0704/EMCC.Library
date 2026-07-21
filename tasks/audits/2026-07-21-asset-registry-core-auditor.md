# audit_result — asset-registry v1.4 CORE (Regime B) — VERDICT: concerns (proceed)

- Target: commit `c87f323` · Directive `dir-20260721-library-asset-registry-core` (builder
  `lattice:EMCC.Library/registry-builder-01` ≠ director — verified) · Auditor: independent
  fresh-context persona (NO-READ honored; read-only)
- ALL acceptance criteria Met, independently re-run: 917 tests OK (skipped=7; zero pre-existing
  broken); 43/43 module tests; gate-mandated crash-resume test green in isolation; evidence file
  matches; schema 17-for-17 verbatim vs §9.1; §9.2 allocator conformant (atomic counter,
  scan-recovery-only, stale-lock surfaced-never-broken — lockfile survives, test-proven); shared
  frontmatter lib only (no second parser); opaque git-zone index rows (leak-assertion test);
  zero network imports (AST test + import-block read); sync_from_kit exclusion effective in both
  lanes, test-proven; exactly 6 files; crash tests simulate real windows (disk-state assertions,
  not mocks). Builder's pre-move zone check judged SPEC-ALIGNED (§9.4 rationale extends to the
  move), not scope creep.
- **W1 (warning):** representability refusals (newline / both-quotes / nested-recipe) fire at
  the commit point — AFTER the ID burn and the physical move — so a refused entry's FILE leaves
  the inbox and sits as a zone-correct orphan until manifest-fix retry (idempotent-move recovers
  cleanly) or the deferred §9.6 sweep. Bends the plain §9.3 "stays in the inbox" reading (slot
  stays flagged; file doesn't). No leak, no loss. Fix at follow-up: representability check in
  the structural pre-pass (before ID/move).
- **W2 (warning):** newline-name refusal verified manually correct but has NO committed
  regression test; the three refusal tests also don't assert the file stayed in the inbox.
- Info: lock "serialize" = refuse-and-surface (operator retry), matching the gate's
  never-auto-break intent; identical-content doubles ride the deferred reconcile (by design).
- Disposition: proceed to Grok cert; W1+W2 folded into the follow-up build item.
