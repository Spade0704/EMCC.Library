# SYNC-STAMP Contract — kit version stamp + drift vocabulary

**Canon** (spec wins). Landed 2026-06-10 by the M-A structural Sync build; pre-build gate `EMCC.DFDU/tasks/delta-force/2026-06-10-ma-structural-sync.md`. Registry entry: `MIGRATION-ISSUES.md` MI-20 (closes MI-19's version-staleness follow-up).

The systemic problem this contract remedies: Sync output carried no version stamp and Sync is manual, so consumer staleness was unbounded and invisible (10 of 15 consumer repos were found carrying stale vendored Codex tooling). MERGE-NEW semantics stand unchanged (C2 council); this contract adds the missing half — VISIBILITY.

## 1. The stamp

`sync_from_kit.py` ends every fully-successful real-run with a dedicated final action that writes:

```
Biz.Automation/wikisys.<consumer>/SYNC-STAMP.json
```

No underscore prefix — the stamp is metadata ABOUT the kit, not kit content (underscore dirs read as kit). It sits outside both the `_scripts/` rmtree lane and the `_config/`/`_template/` MERGE-NEW lane, so every sync REWRITES it (never frozen, never deleted mid-sync).

### Schema

```json
{
  "kit_commit": "<Library HEAD SHA at sync time, or null>",
  "synced_at": "<UTC ISO-8601, e.g. 2026-06-10T12:34:56+00:00>",
  "manifest": {
    "<consumer-relative posix relpath>": "<sha256 of the bytes as delivered>"
  }
}
```

- **`kit_commit`** is a commit SHA, not a version label (Library has no release-tag discipline and is not pip-packaged — MI-13; the SHA is the truth). `null` when the Library install path is not a git checkout (sync WARNs).
- **`manifest`** covers the **OVERWRITE-lane files only**: the `_scripts/` tree (recursively, `__pycache__` excluded) + the four verbatim spec docs (`PROJECT_WIKI_BUILD_SPEC.md` into the wiki's `codex/` dir; `INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`, `CODEX_LIBRARIAN.md` into `_context/`). MERGE-NEW/SKIP targets (`_config/`, `_template/`) are consumer-owned after first sync — "modified" is expected there, not drift — and are deliberately not manifested.
- **The stamp IS the kit manifest.** There is no separate upstream manifest artifact; upstream comparison goes through `git show <kit_commit>:<library-path>` against the Library checkout.

### Lifecycle

| Event | Stamp behavior |
|---|---|
| Real-run, all actions OK | Written (rewritten if present) as the FINAL action |
| Real-run, any action FAILED | NOT written (`[STAMP] skipped` reported); a stamp asserts a fully-delivered kit |
| `--dry-run` | Never written |
| Stamp write itself fails | The run fails (exit 1) |
| Library checkout dirty at sync time | Stamp written, but sync WARNs: `kit_commit` records HEAD while delivered bytes may differ — downstream upstream-comparisons may misreport |

## 2. Drift vocabulary (three states, never blended)

Consumed by `EMCC/scripts/check_drift.py` (**report-only**: zero write paths, no `--fix`, no auto-invoke — the remedy is always an explicit operator-run sync/wire). The states are independent and co-occurring; a file can be STALE **and** MODIFIED — both are reported.

| State | Meaning | Detection |
|---|---|---|
| **STALE** | The kit moved on upstream. | Whole-kit: `kit_commit != Library HEAD`. Per-file: `git show <kit_commit>:<library-path>` differs from the upstream file now (fallback when the commit is unreachable: stamped hash vs upstream-now, disclosed). |
| **MODIFIED** | A consumer-side edit (or deletion) in the OVERWRITE lane — the next sync would clobber it. This is the LIB-NEW-B pre-clobber warning: surface consumer modifications BEFORE a sync eats them. | sha256 of the consumer file now != the stamped as-delivered hash. |
| **PERSONA-DRIFT** | A carried persona no longer matches its generator/template output. | Consumer `.claude/personas/CLAUDE.librarian.md` vs Library's GENERATED drop-in (the `generate_persona_dropin.py` output — Library generates, `emcc_wire` copies by path); consumer `CLAUDE.auditor.md` vs EMCC's vendored template. |

Additional reported conditions (informational, not drift): **NO-STAMP** (consumer not yet synced by a stamping kit — also covers an unparseable stamp, which is treated as "no valid stamp" because an interrupted sync may truncate it), and `kit_commit: null` (whole-kit staleness unknown).

Note the SKIP-line distinction: sync's `[SKIP] ... (existing file preserved - not compared to upstream)` means MERGE-NEW preserved a consumer file — SKIP does **not** mean up-to-date. `check_drift` is the missing comparator for the OVERWRITE lane; MERGE-NEW files stay consumer-owned by design.

## 3. Path mapping (consumer relpath -> Library source)

`check_drift` derives the upstream path structurally from the sync delivery map:

| Consumer relpath | Library source |
|---|---|
| `Biz.Automation/wikisys.<name>/_context/<procedure>.md` | `wiki.codex/git/codex/<procedure>.md` |
| `Biz.Automation/wikisys.<name>/<rest>` | `Biz.Automation/wikisys.library/<rest>` |
| `wiki.<name>/git/codex/<file>` | `wiki.codex/git/codex/<file>` |

## 4. Fences (locked at the M-A gate)

- `check_drift` stays report-only forever-by-default: the moment it writes, it is auto-sync (Lock-2 / M-B territory).
- The stamp must never gain a lane that subjects it to MERGE-NEW freezing or `_scripts/` rmtree.
- MERGE-NEW semantics are locked (C2 council) — the stamp adds visibility, not new write behavior.
- Library resolves by path (`EMCC_LIBRARY_ROOT` or the portfolio sibling layout), never `import librarian` (MI-13).
