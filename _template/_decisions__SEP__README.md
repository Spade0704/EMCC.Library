# Decisions

This folder holds **append-only logs** of consequential events:

- `ingest-log.md` — every Ingest operation; see `_context/INGEST_PROCEDURE.md` §6.
- Project-specific decision logs as needed (architecture choices, scope changes, naming verdicts, etc.).

## Append-only convention

Entries are only ever added, never edited or removed. Each entry is dated. If a decision is later reversed, write a new entry explaining the reversal — do not silently overwrite the original.

This folder is the one infrastructure folder that is reasonable to share externally alongside wiki content — the audit trail is often valuable to collaborators.
