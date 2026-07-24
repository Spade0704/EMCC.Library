# Codex §9 shared schemas

Canonical data schemas owned by Codex §9 (the portfolio asset registry). Consumers
**vendor** these SHA-pinned via Sync and code against the vendored copy — never a
divergent second definition.

## `visual-evidence.schema.json`

Shared visual-evidence sidecar standard **v0.1** (LLM Council SHIP 2026-07-24,
`EMCC/tasks/council/2026-07-24-visual-evidence-standard.md`). One artifact consumed by
BOTH `pnpm anvil test --strict-assets` (game-build mechanical floor, checks 1–6) AND
Codex §9 registry ingest. JSON-Schema draft-07, **stdlib-safe subset** (Library's
validator is a hand-rolled stdlib walker — no `jsonschema` pip): only
`type`/`required`/`enum`/`properties` + simple nested objects/arrays; NO `$ref`, `allOf`,
`oneOf`, `if-then`, regex `pattern`, or remote refs. See CODEX_BUILD_SPEC_v1_4 §9.9.

- **content sha256:** `8c6eb411faa8d0ff31afe0440dc60554dc5875212049d0e462323f8e763452bd`
  — the value Anvil pins when vendoring. Recompute on any change; a new value = a schema
  version bump (co-sign both sides).
- **Rules code-enforced (not in schema):** R1 `base_asset_ref` XOR fresh-gen; R2
  `aesthetic_signoff.name` non-empty. `cert_class` is cert-handoff-only (never a sidecar
  field); enum `{mechanical-pass-human-aesthetic, mechanical-fail}`; "certified" banned.
- **Builders:** Codex §9 (owner) — Librarian / EMCC.Library; Anvil `--strict-assets`
  consumer — fwojames / iron-soul-anvil.
