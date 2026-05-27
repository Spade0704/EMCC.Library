# Raw Sources

**Permanent, read-only archive** of every source that has been ingested into the wiki.

## How files land here

Files arrive via Ingest. On successful completion of `_context/INGEST_PROCEDURE.md` §5, the source moves from `_inbox/` to `_sources/raw/`, and its frontmatter is updated:

```
status: ingested
ingested_date: <YYYY-MM-DD>
```

After this point the file is **read-only**. Do not edit archived sources in place.

## `canon_sources` discipline

Every wiki page that derives facts from a source cites the source in its frontmatter:

```
canon_sources: ["_sources/raw/<source>.md §<section>"]
```

Paths in `canon_sources` always point here, never at `_inbox/`. A `status: ready` page (completion ≥ 80) must have non-empty `canon_sources`.

## Versioning

When a source has a new version, scaffold it as a new inbox entry — do not overwrite the prior version. The old version stays here for history; both versions can be cited from the same page (the old citation preserved, the new added).

For supersession analysis, run `python _scripts/delta_source_docs.py <old> <new>` before re-ingesting.
