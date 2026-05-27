# _archive — Codex automation scripts retired in S003b (2026-05-27)

This folder holds Codex automation artifacts retired during the
S003b archive sweep. Contents are **historical reference only** —
not invoked by Codex v1.1, not on any active code path.

## launchers/ — Lattice 2.0 Nexus 4-persona PowerShell launchers (5 files)

Retired because Lattice has moved to **3.0 single-agent** per
`EMCC.DFDU/documents/lattice/01-LATTICE-AGENT.md`. The launchers
encoded the Lattice 2.0 Nexus pattern (Architect / Auditor /
Craftsman / Scribe — four concurrent personas spawned via
PowerShell wrappers).

**Why archive rather than delete:**

- Real lessons encoded: Windows env-propagation footgun
  (`setx` ≠ instant); launcher inline-`$env:` workaround pattern.
- `tasks/lessons.md` references these scripts as historical anchors.
- Deleting would forfeit the trace of WHY the 2.0 → 3.0 transition
  was necessary.

**Pre-archive paths** (project-codex original) — hardcoded to
`D:\Claude Projects\Project Codex\<Persona>\_scripts\launchers\` —
no longer valid; the 4-clone layout has been archived in
project-codex per S001 A1 disposition. References inside the
PowerShell scripts to `lattice-bridge.py` and
`lattice_session_start.py` point at files that STAY in the
project-codex archive (not in Library).

**Pointer to current model:**

- Lattice 3.0 single-agent operating contract:
  `EMCC.DFDU/documents/lattice/01-LATTICE-AGENT.md`
- Lattice 3.0 audit regime decision tree:
  `EMCC.DFDU/documents/lattice/05-AUDIT-REGIMES.md`

**Disposition decided by:** S003b sprint per audit recommendation in
`tasks/plans/library-staleness-audit-2026-05-27.md` §"ARCHIVE" §"Next sprint recommendation S003b".

**Decided not to delete because:** operator brief biases against
deletion; archive preserves the historical lessons trace.
