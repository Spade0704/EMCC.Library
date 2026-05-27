# Lattice persona launchers

PowerShell entry-points for spawning each Lattice persona's Claude Code (CC) pane with the correct env vars and working directory in one click.

## Purpose

Closes backlog #59 — env-propagation footgun observed during Project Codex sprint S031 bus-root drift recovery. See `tasks/lessons.md` 2026-05-12 entries:

- **"Bridge bus-root env-default footgun (bidirectional)"** — bus-root divergence between panes silently routes messages to the wrong inbox.
- **"Windows env propagation: setx ≠ instant; PowerShell child-process inheritance"** — `setx` writes the user-env registry but already-open PS sessions inherit only their pre-`setx` env when spawning `claude`.

Each script sets `AGENT_PROJECT` + `AGENT_BUS_ROOT` + `AGENT_ROLE` **inline** via `$env:VAR = "value"` immediately before invoking `claude`. Inline assignment guarantees child-process inheritance regardless of `setx` / registry state.

## Usage

Three equivalent entry-points:

1. **Right-click → "Run with PowerShell"** in File Explorer on the `.ps1` file.
2. **From any PowerShell window:**
   ```powershell
   & "D:\Claude Projects\Project Codex\Project Codex (Craftsman)\_scripts\launchers\start-craftsman.ps1"
   ```
3. **Pin to taskbar / Start menu** — create a shortcut with target:
   ```
   powershell.exe -ExecutionPolicy Bypass -File "<full path to start-<role>.ps1>"
   ```
   The `-ExecutionPolicy Bypass` flag covers the default `RemoteSigned` policy on most Windows installs without requiring a one-time `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

Four scripts ship, one per persona role:

| Script | Role | Clone directory |
|---|---|---|
| `start-architect.ps1` | architect | `Project Codex (Architect)` |
| `start-craftsman.ps1` | craftsman | `Project Codex (Craftsman)` |
| `start-auditor.ps1`   | auditor   | `Project Codex (Auditor)`   |
| `start-scribe.ps1`    | scribe    | `Project Codex (Scribe)`    |

Env-var values use lowercase role names (matching `lattice-bridge.py` ROLES tuple); path segments use capitalized role names (matching existing clone-dir layout).

## Caveat — paths hardcoded to JP's machine layout

Each script encodes absolute paths under `D:\Claude Projects\Project Codex\...` and a bus root at `D:\Claude Projects\.lattice\codex\bus`. These match the canonical Project Codex four-clone Windows layout owned by JP.

Fork + customize for other operator setups. Template-ization (placeholder substitution at install-time) is a deferred v0.2.x forward-pointer; not in S032 scope.

## Verification

After launching, the new CC pane's first `python _scripts/lattice-bridge.py status` call should report the matching role's `last_seen` heartbeat under the configured `bus_root`. If env vars didn't propagate, the bridge will hard-fail per Lesson #24 STANDARD (S040-T0) with an actionable error message naming `AGENT_BUS_ROOT` + suggesting the launcher path + explicit-set alternative.

**Post-S040-T0:** The bridge silent-fallback to `~/.lattice/<AGENT_PROJECT>/bus` was removed. Any non-launcher invocation without explicit `$env:AGENT_BUS_ROOT` set will hard-fail at boundary entry instead of silently routing to HOME-relative path. Launchers are now the de-facto mandatory spawn path; manual `$env:AGENT_BUS_ROOT = "<path>"` assignment before `claude` invocation is the only supported alternative.

If the bridge hard-fails: verify the script was run via one of the three entry-points above (not just copy-pasted into an existing PS window where outer-scope `$env:*` assignments don't propagate downward without an explicit child-process spawn). Reference: `tasks/lessons.md` Lesson #24 STANDARD for full discipline + 2-incident-codification history (S029 2026-05-09 + S039-T5a 2026-05-17).
