---
title: "Ingest Procedure"
type: context_rules
visibility: internal
completion: 100
status: ready
last_updated: 2026-05-21
dependencies: ["SEMANTIC_LINT_PROCEDURE.md"]
canon_sources: ["PROJECT_WIKI_BUILD_SPEC.md §4.3 (Codex v1.1)"]
unverified_claims: []
---

# Ingest Procedure

**Audience:** Claude Code, when the user says "ingest `_inbox/<source>`" or "ingest the new source."

**Authority:** This procedure is how Codex integrates new source material into the wiki. Bootstrap and Sync are infrastructure operations; Ingest is how the wiki actually grows. Section 4.3 of `PROJECT_WIKI_BUILD_SPEC.md` is the summary; this file is the full contract.

## Source formats

Sources may be: markdown (`.md`), plaintext (`.txt`), PDF (`.pdf`), or web archives copied into markdown via the Obsidian Web Clipper or similar. Claude Code reads all of these natively.

For non-markdown sources (PDFs especially), `scaffold_source.py` creates a **sidecar `.md`** in `_inbox/` next to the binary file. The sidecar carries the frontmatter (`source:`, `ingested_date:`, `status:`) and a pointer to the binary. Ingest reads the binary on demand and treats the sidecar as the canonical entry. On archive, both the binary and the sidecar move to `_sources/raw/`.

## Hard rules

1. **Never write to `_canon/*.yaml` without explicit confirmation.** Canon is ground truth; a mistake there contaminates every validator downstream. Propose the YAML entry, show the exact diff, wait for approval.
2. **Never silently overwrite a page or a canon entry.** If an extracted fact contradicts existing content, flag it. The user chooses between overwrite, quarantine to `_brain_dump/`, or no-op.
3. **Never touch `_scripts/`, `_config/`, `_confidential/`, `04-Contributing/`, or unrelated content pages.** Ingest only adds or updates pages derived from the current source.
4. **Cite every new claim.** Pages created or updated by Ingest must list the archived source in `canon_sources` with a section reference where possible (e.g. `_sources/raw/spec-v2.pdf §3.2`).
5. **Archive is irreversible.** Once a source moves from `_inbox/` to `_sources/raw/`, it is read-only. Re-ingestion of a revised source uses `delta_source_docs.py`, not a fresh Ingest.
6. **One source per Ingest run.** If the user names multiple sources, ingest them serially — each produces its own ingest-log entry.
7. **Versioned sources do not overwrite predecessors.** When `spec-v2.pdf` arrives, `spec-v1.pdf` stays in `_sources/raw/` untouched. The ingest log records the supersession; `delta_source_docs.py` shows the cascade.

## The procedure

### 1. Read

Open `_inbox/<source>` (or its sidecar, for binaries). Confirm the frontmatter includes `source`, `ingested_date`, and `status: pending_triage`. If any field is missing, stop and tell the user to run `python _scripts/scaffold_source.py` first.

For PDFs, read the binary directly. For sources over ~5k words, announce the size and offer `--dry-run` first. For sources over ~20k words, recommend splitting before Ingest.

If the source appears to supersede an existing source in `_sources/raw/` (matching base name with version suffix, or user explicitly says "v2 of X"), run `delta_source_docs.py` against the predecessor before extraction. The delta report informs the routing plan in Step 3.

### 2. Extract

Walk the source and extract candidate items. Classify each:

- **Canon-worthy** — numbers that will appear in more than one page, named entities with canonical forms, timeline or version events, taxonomic classifications, recurring topical themes. Destination: `_canon/counts.yaml`, `_canon/roster.yaml`, `_canon/timeline.yaml`, `_canon/taxonomy.yaml`, or `_canon/topics.yaml`.
- **Page-worthy** — a concept, framework, entity, or process substantial enough to deserve its own page (roughly: anything you'd reasonably link to from multiple other pages).
- **Mention-worthy** — a fact, detail, or cross-reference that belongs in an existing page but doesn't warrant a page of its own.
- **Noise** — filler, stylistic phrasing, or content out of scope for this wiki. Drop silently.

Present the classified lists to the user before writing anything. The user may reclassify any item.

### 3. Route

After the user confirms the extraction plan:

- **Canon-worthy** → show the proposed YAML entry; on approval, append to the relevant `_canon/*.yaml`. One approval per canon file per Ingest run is acceptable — don't ask twenty times in a row.
- **Page-worthy** → create the new page under the correct domain folder (`01-*`, `02-*`, etc.). Use the full frontmatter schema from Section 2.3 of the build spec. Set `status: outlined` unless the source is authoritative enough for `solid`. Include `canon_sources: ["_sources/raw/<source> §<section>"]`.
- **Mention-worthy** → edit the target page; cite the source in the page's `canon_sources` list (add if not present). Update `last_updated` to today.
- **Contradicts existing content** → do not write. Add an entry to the ingest log's "contradictions" section naming both sides of the disagreement. Let the user decide the resolution.
- **Supersession case** → for facts updated by a v2 source, the old `canon_sources` citation pointing at v1 stays in place (history preserved); the new citation pointing at v2 is added. The page itself is updated to reflect the new fact.

### 4. Link

Add `[[wikilinks]]` between the new/updated pages and existing related pages. If a new top-level concept was introduced (a new folder under the domain tree), add a one-line reference to `Home.md`. Otherwise, do not touch `Home.md`.

### 5. Archive

Move `_inbox/<source>` → `_sources/raw/<source>`. For binaries with sidecars, move both. Update the sidecar (or the source itself, if markdown):

```yaml
status: ingested
ingested_date: <today>
```

`_sources/raw/` is read-only after this point. Do not edit archived sources directly; if the source has a new version, scaffold it as a new inbox entry and run Ingest again.

### 6. Log

Append to `_decisions/ingest-log.md`:

```markdown
## YYYY-MM-DD — <source filename>

- **Source:** `_sources/raw/<source>`
- **Supersedes:** `_sources/raw/<predecessor>` (if applicable)
- **Pages created:** [[Page-A]], [[Page-B]]
- **Pages updated:** [[Page-C]] (added section on X), [[Page-D]] (updated table)
- **Canon entries added:** `counts.yaml: foo = 42`; `roster.yaml: Bar-Entity`
- **Contradictions flagged:** <list, or "none">
- **Notes:** <anything the user should know>
```

### 7. Validate

Run `python _scripts/update_dashboards.py`. Confirm zero new validator errors, dashboards regenerated, no broken links introduced.
Pages carrying `topics:` frontmatter are checked by `validate_topic_registry.py` in this pass; unresolved topic values surface as errors — resolve them before declaring Ingest complete. If the run surfaces issues, fix them before declaring Ingest complete.

## Refuse to run if

- The inbox source lacks required frontmatter.
- There are uncommitted git changes from an unrelated session (override with `--force` or confirm with the user).
- Canon contradictions are detected and the user has not chosen a resolution.
- `_scripts/` has been edited since the last Sync (the wiki is drifting from Codex; run Sync first).

## Edge cases

- **Source partially in scope.** Ingest the in-scope parts; note skipped sections in the ingest log.
- **Source contradicts multiple pages.** List every contradiction; do not cascade an overwrite across pages.
- **User revises the extraction plan.** Re-do Steps 2–3 with the updated plan. Do not proceed from a stale plan.
- **Dry-run.** `--dry-run` stops after Step 3; print the full routing plan and exit without writing.
- **PDF without selectable text** (scanned image). Tell the user. Do not attempt OCR — Codex is dependency-free. The user must provide a text version.
- **Source is a v2 of an already-ingested source.** Always run `delta_source_docs.py` first. Use its output to scope the routing plan.

## Reminder

Ingest is where facts enter the wiki. Treat every write as load-bearing. When in doubt, propose rather than write.
