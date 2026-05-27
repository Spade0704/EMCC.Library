# Brain Dump

This folder holds **quarantined unvalidated ideas** — anything that has not been promoted to canon. Content here is **NOT canonical** and must not be cited as ground truth elsewhere in the wiki.

## When to write here

Use `_brain_dump/` for half-formed ideas that aren't ready for a real page yet, hypotheses awaiting evidence, speculation that might or might not pan out, and "maybe this is true" claims that haven't been validated against sources. Anything you'd otherwise hesitate to put on a regular page because you don't yet trust it.

## `dump_status` lifecycle

Every brain dump entry adds a `dump_status` field to its frontmatter (spec §2.3, brain-dump extension). The lifecycle:

- `exploring` — actively being worked on; provisional.
- `validated` — confirmed against a source; ready for promotion.
- `migrated` — promoted to a canonical page; populate `migrated_to: [...]` with the destination.
- `superseded` — replaced by a newer idea; left here for history.
- `rejected` — investigated and disproven; left here as a record.

When an entry reaches `migrated`, the canonical page lives elsewhere — this folder retains the original speculation for audit-trail purposes.

## Rules

- Brain dump entries are **never** cited in `canon_sources` on other pages.
- Brain dump entries do **not** count toward the wiki's completion score.
- Validators and dashboards skip this folder by default.
- When sharing the wiki externally, exclude this folder.

Use the scaffolder to create a new entry:

```
python _scripts/scaffold_brain_dump.py "<one-line title>"
```
