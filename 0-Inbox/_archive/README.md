# 0-Inbox archive

Triaged-out inbox docs, moved here (move-not-delete, git-tracked, reversible) rather than deleted,
per the Codex do-not-delete rule. A `_`-prefixed sub-directory, so inbox-health scans that use
top-level `iterdir()` + `is_file()` skip it — archived files stop counting against inbox health while
remaining recoverable. Restore a file by `git mv`-ing it back up to `0-Inbox/`.

First populated 2026-06-15 (dir-20260615-all-repo-inbox-organize):

| Archived doc | Reason |
|---|---|
| `PLAN-cross-link-promotion-2026-06-13.md` | Architect plan for the **Codex v1.3.1 cross-link-at-scale** sprint — BUILT 2026-06-13b (`4dce454`, Auditor SHIP-WITH-FIXES). Core gaps 1–4 shipped (P18.3 cap+ranking, dup-stem disambiguation, `backfill_topics.py`, Librarian v1.3.1 op). Plan value spent; the 3 remaining ⚪ low-pri tails (plugin-wire, dotted-code backfill, dry-Sync zero-diff) are tracked independently in `tasks/todo.md` §"Sprint — Codex v1.3.1 cross-link at scale". Lessons recorded in `tasks/lessons.md` §"Cross-link engine gaps surfaced by the Aviation consumer". |
