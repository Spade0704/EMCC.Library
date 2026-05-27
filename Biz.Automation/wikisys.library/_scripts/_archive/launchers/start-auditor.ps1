# Lattice persona launcher — Auditor.
# Closes backlog #59: sets the 3 required env vars inline so they propagate
# to the `claude` child process regardless of setx / registry state.
# Reference: tasks/lessons.md 2026-05-12 (bus-root + Windows-env entries).

Set-Location "D:\Claude Projects\Project Codex\Project Codex (Auditor)"
$env:AGENT_PROJECT  = "codex"
$env:AGENT_BUS_ROOT = "D:\Claude Projects\.lattice\codex\bus"
$env:AGENT_ROLE     = "auditor"
claude
