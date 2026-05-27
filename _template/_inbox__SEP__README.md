# Inbox

**Ephemeral holding pen** for sources that have arrived but have not yet been ingested.

## Lifecycle

1. A new source lands here — usually via `python _scripts/scaffold_source.py <path-or-url>`, which creates `_inbox/<basename>.md` with `status: pending_triage` frontmatter.
2. Claude runs Ingest (see `_context/INGEST_PROCEDURE.md`) against the source.
3. On successful Ingest, the source moves from `_inbox/` to `_sources/raw/`, becomes read-only, and its frontmatter updates to `status: ingested`.

## Relationship to `_sources/raw/`

- `_inbox/` is **ephemeral**. Anything here is waiting in line.
- `_sources/raw/` is **permanent and read-only**. Anything there has been ingested.
- `canon_sources` citations on wiki pages always point at `_sources/raw/`, never at `_inbox/`.

## Rules

- Sources without required frontmatter (`source`, `ingested_date`, `status: pending_triage`) cannot be ingested. Run `scaffold_source.py` first.
- Do not edit content already in `_sources/raw/` from this folder. If a source has a new version, scaffold it as a new inbox entry and re-run Ingest.
- Validators skip this folder by default.
