---
title: "EMCC Reusable Patterns — Index"
type: overview
visibility: internal
completion: 35
status: outlined
last_updated: 2026-05-30
dependencies: []
public_pair: null
blocking_questions: ["Should these graduate into a dedicated EMCC reusable-pattern module (with its own canon), or a shared emcc_flutter_kit Dart package?"]
topics: []
related_files: []
tags: []
canon_sources: []
unverified_claims: []
---

# EMCC Reusable Patterns

Cross-project engineering patterns **lifted** from EMCC consumer apps and generalized so any
future consumer can reuse the design instead of re-deriving it. These are **descriptive specs
+ reference snippets**, not shipped runtime — EMCC ships no Dart today (DFDU and Library are
Python/Markdown). When a second Flutter consumer exists, the highest-value patterns here become
candidates for a shared `emcc_flutter_kit` Dart package.

**Placement, deliberate.** These docs live at repo-root `patterns/`, *not* inside
`wiki.codex/git/`. The Codex dogfood wiki's `_canon/` is reserved for "Codex documenting Codex,"
and its cross-link orchestrator keys on generic words (e.g. "sync", "ingest", "bootstrap") — so
app-domain pages placed inside it bleed into Codex's topic graph and perturb verbatim-protected
files. Hosting them here keeps Codex's canon pure while still delivering Codex-format pattern
docs in EMCC. If they graduate to a first-class module, give them their own wiki + canon.

Provenance: first batch extracted 2026-05-30 from the `tat_app` consumer during the TAT
audit/modernization pass. Brand-specific terminology generalized.

| Pattern | What it solves |
|---|---|
| `Decision-Scoring.md` | Rank a work queue by a tunable weighted score instead of one field |
| `Opportunistic-Bundling.md` | Surface "while you're here, also do X" batches by shared context |
| `Offline-First-Sync.md` | Local-cache-first reads + a durable write queue that flushes on reconnect |
| `Soft-Delete-Signal-Preservation.md` | "Park, don't delete" + preserve the behavioral signal of a deletion |
| `AI-Memory-And-Insight-Extraction.md` | Per-user memory schema + privacy-validated extraction + model routing |
| `Neurodivergent-First-UX.md` | UX principles for executive-function support |
