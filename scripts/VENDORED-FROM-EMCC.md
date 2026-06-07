# Vendored from EMCC — do not hand-edit

These files are the task-orchestration runtime + caller skills, vendored from `spade0704/EMCC`
so a single-repo Routine clone is self-sufficient (framework/19-task-orchestration.md). They are
**OVERWRITE-vendored**: re-run `python <EMCC>/scripts/emcc_wire.py <this-repo> --routine` to update.
Do not hand-edit — fixes belong in EMCC, then re-cascade.

Vendored scripts: task_state.py, orchestrator_log.py, task_driver.py, render_board.py
Vendored skills:  run-routine, process-feedback

Usage: score eligible Backlog tasks in `tasks/todo.md` (a `DFTS: N` note, N<4 for autonomous),
then a Routine runs `/run-routine` (kill-switch -> route_scored -> select_next -> claim -> draft a
DRAFT PR; never merges). Generate the board view with `python scripts/render_board.py`.
