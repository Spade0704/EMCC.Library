# Ingest Log

Append-only record of every Ingest operation. New entries land **above** the example block but **below** this header. Each entry follows the format in `_context/INGEST_PROCEDURE.md` §6.

<!--
Example entry format — delete this comment block once the first real entry lands.

## YYYY-MM-DD — <source filename>

- **Source:** `_sources/raw/<source>`
- **Supersedes:** `_sources/raw/<predecessor>` (if applicable)
- **Pages created:** [[Page-A]], [[Page-B]]
- **Pages updated:** [[Page-C]] (added section on X), [[Page-D]] (updated table)
- **Canon entries added:** `counts.yaml: foo = 42`; `roster.yaml: Bar-Entity`
- **Contradictions flagged:** <list, or "none">
- **Notes:** <anything the user should know>
-->
