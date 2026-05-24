# `_canon/` — Ground-Truth Reference Directory

This directory holds the wiki's authoritative reference for named entities, canonical counts, taxonomic classifications, and timeline milestones. Validators read these files as ground truth when checking pages for contradictions.

## Ground truth is the floor, not the ceiling

`_canon/` captures the verified floor — facts already validated against archived sources. It is **not** a closed set. Pages may introduce new entities pending canon promotion; propose additions via the brain-dump or ingest flow (user-confirmed canon writes) per spec Principle #6 ("Ingest proposes, humans dispose"). Canon writes require user confirmation; contradictions are flagged, never silently overwritten.

## Files

**`counts.yaml`** — Every canonical number that appears more than once across the wiki (population counts, vessel dimensions, episode counts, etc.). Consolidating numbers here lets validators enforce cross-page consistency: if page A says "1,200 colonists" and page B says "1,500 colonists", the page-vs-canon checker flags the disagreement.

**`roster.yaml`** — Named entities (characters, factions, locations, technologies) with canonical names plus alias lists. Aliases let pages refer to the same entity by multiple names without tripping consistency checks. Consumed by `_scripts/check_concept_coverage.py` for entity-coverage scanning (detects entities mentioned across pages but lacking a dedicated page).

**`taxonomy.yaml`** — Structured classifications used by the project (ship classes, character roles, faction tiers, episode arcs — schema is project-defined and flexible). Use this when classifications need a single source of truth instead of being implicit in page titles or tags.

**`timeline.yaml`** — Milestones, version numbers, in-universe dates, and progression parameters. Anything ordered along a time axis lives here once it appears in more than one page.

## Consumers

Four scripts read `_canon/` as their ground-truth source:

1. **`_scripts/check_canon_consistency.py`** — page-vs-canon mode flags pages that contradict canonical values (enforced); page-vs-page mode flags pages that contradict each other when canon does not arbitrate (informational).
2. **`_scripts/validate_canon_integrity.py`** — enforces that any page with `status: ready` has a non-empty `canon_sources` list and an empty `unverified_claims` list.
3. **`_scripts/build_canon_drift_report.py`** — snapshots `_canon/` and diffs against prior snapshots over time, surfacing silent canon mutations.
4. **`_scripts/check_concept_coverage.py`** — reads `roster.yaml` to detect entities with N+ page mentions but no dedicated page (`min_mentions` configurable via `_config/concept_coverage.yaml`).

## Path-citation discipline

Page frontmatter `canon_sources[]` entries cite paths under `_sources/raw/` (the permanent, read-only archive), never `_inbox/` (the ephemeral triage area). Sources move from `_inbox/` to `_sources/raw/` on successful ingest; cite the destination path, not the holding-pen path.
