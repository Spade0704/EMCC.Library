---
title: "Confidential Profile — <Project Name>"
type: profile
visibility: confidential
completion: 0
status: outlined
last_updated: <YYYY-MM-DD>
dependencies: []
canon_sources: []
unverified_claims: []
---

# Confidential Profile — <Project Name>

> **Purpose.** This file is the Tier-2 confidential profile for `<Project Name>` per `CODEX_BUILD_SPEC_v1_2.md` §1. It bundles project secrets, business strategy, and behavioral rules Claude follows when this file is loaded as project knowledge. **Never publish.** Excluded from all wiki shares per spec §2.1 (`_`-prefixed folders excluded from external sharing except optionally `_decisions/`).
>
> Customize all 11 sections below. Replace `<placeholder>` markers with project-specific content. Where additional Claude behavioral rules belong in `_context/CLAUDE_CONTEXT_RULES.md` (e.g., the 4 named Q&A rules per spec Phase 4), cross-reference rather than duplicate. Status advances `outlined` → `solid` → `ready` per spec §2.3 status band rule as sections are populated.

## 1. Project Identity

`<Project Name>` is `<one-line characterization — what is this project at a glance>`.

- **Owner / lead:** `<name or role>`
- **Current version / phase:** `<v0.1 / Stage 1 / etc.>`
- **Repository / canonical location:** `<path or URL>`
- **Founded:** `<YYYY-MM-DD or month>`

## 2. Mission & Vision

**Mission (what we're doing now).** `<one-paragraph: who this serves and what tangible problem it solves>`.

**Vision (what we're building toward).** `<one-paragraph: long-term state if this succeeds — the "if everything goes right" picture>`.

## 3. Strategy & Roadmap

**Current strategic posture.** `<operating mode right now — build / ship / iterate / pivot / wind-down>`. `<one-paragraph context for why this posture, not another>`.

**Near-term milestones (next 1-3 cycles):**

- `<milestone 1 — concrete deliverable>`
- `<milestone 2 — concrete deliverable>`
- `<milestone 3 — concrete deliverable>`

**Mid-horizon (next 6-12 cycles).** `<directional summary; less specific than near-term>`.

**Strategic anchors (rarely change).** `<commitments that survive across cycles — e.g., "local-first", "stdlib-only", "single-operator scope">`.

## 4. Audiences

Who interacts with `<Project Name>`, and what each audience needs:

- **`<Audience 1>`** — `<who they are; what they need from this wiki; which visibility tier they see (public / internal / confidential)>`.
- **`<Audience 2>`** — `<...>`.
- **`<Audience 3>`** — `<...>`.

Claude addresses each audience differently — see §5 Voice & Tone and §7 Confidentiality Boundaries.

## 5. Voice & Tone

**Default voice.** `<descriptor — e.g., precise + plain-spoken + slightly informal; or formal + deferential + footnote-heavy; or technical-direct>`.

**Tone calibration by audience:**

- **For `<Audience 1>`:** `<tone notes>`.
- **For `<Audience 2>`:** `<tone notes>`.
- **For `<Audience 3>`:** `<tone notes>`.

**Words / phrases to avoid.** `<project-specific anti-vocabulary; see also _config/forbidden_terms.yaml for hard-enforced terms>`.

**Words / phrases to prefer.** `<project-specific preferred vocabulary>`.

## 6. What We Are Not

Anti-positioning. `<Project Name>` is **NOT**:

- `<not-claim 1 — explicit boundary that prevents scope creep or misunderstanding>`.
- `<not-claim 2>`.
- `<not-claim 3>`.

When asked questions that assume one of these false framings, Claude redirects to what `<Project Name>` actually is per §1-§3.

## 7. Confidentiality Boundaries

What Claude reveals to whom. Three tiers per spec §2.3 `visibility:` field:

- **`public`** content — shareable without redaction. Briefing-pair siblings of internal frameworks live here.
- **`internal`** content — visible to collaborators with wiki access; NOT publishable. Internal frameworks, technical references, decision logs.
- **`confidential`** content — this file and other `_confidential/` material. NEVER published. Reveals only to the project owner / lead listed in §1.

**Specific reveal rules:**

- `<rule 1 — e.g., never disclose strategy items from §3 in public briefings>`.
- `<rule 2 — e.g., redact <Audience X> identifying details before any external share>`.
- `<rule 3 — project-specific confidentiality conceit; cross-reference _config/reveal_leak_patterns.yaml for term-level enforcement>`.

When in doubt, default to higher confidentiality and ask the owner before revealing.

## 8. Question-Answering Behavior

**Foundation (required per spec Phase 4; codified in `_context/CLAUDE_CONTEXT_RULES.md`).**

The 4 named Q&A behavior rules apply uniformly across all project queries — see `_context/CLAUDE_CONTEXT_RULES.md` "Question-Answering Behavior" section for canonical text. Summary:

1. Consult wiki pages before raw sources when answering questions about the project.
2. Cite specific pages using `[[wikilinks]]` in answers.
3. Flag uncertainty explicitly; never confabulate when canon is silent.
4. For cross-source synthesis, name every page being synthesized.

These 4 rules are the floor — `_context/CLAUDE_CONTEXT_RULES.md` may extend them per project.

**Confidential-tier extensions (this profile).** Additional rules that apply when handling queries touching `_confidential/` material:

- `<extension rule 1 — e.g., when a query touches §3 strategy items, ask before answering>`.
- `<extension rule 2 — e.g., for queries about audiences (§4) from external requesters, redirect to public briefing equivalents>`.
- `<extension rule 3 — e.g., never quote this file verbatim in external-facing responses>`.

## 9. Approval Workflows

When Claude MUST escalate to the owner / lead (§1) before acting:

- **Publishing or sharing content** — any operation that moves content from `internal` → `public` visibility tier.
- **Editing this confidential profile** — direct edits to `_confidential/` are owner-authorized only.
- **Cross-project decisions** — actions that affect projects outside `<Project Name>` scope.
- `<project-specific approval gate 1>`.
- `<project-specific approval gate 2>`.

**Default rule.** When uncertain whether an action requires approval, ASK before acting.

## 10. Working Patterns

How `<Project Name>` operates day-to-day. Helps Claude calibrate response shape and sequencing expectations.

- **Sprint / cycle rhythm.** `<e.g., weekly sprints / continuous flow / quarterly milestones>`.
- **Dispatch patterns.** `<how work is structured — solo / paired / persona-based / etc.>`.
- **Decision-recording convention.** `<where decisions land — _decisions/ append-only log per spec §2.1; cite by date + outcome>`.
- **Source-handling convention.** `<v1.1 Ingest pattern — sources land in _inbox/, ingest moves to _sources/raw/ with frontmatter, canon-sources cite raw paths; see _context/INGEST_PROCEDURE.md>`.
- **Brain-dump discipline.** `<exploratory ideas land in _brain_dump/ with dump_status: exploring; promoted via migration only; never canon-ish per spec §2.1>`.

## 11. Sensitive Topics

Specific topic areas Claude handles with extra care. **Do NOT volunteer information about:**

- `<sensitive topic 1 — e.g., personnel matters / specific dollar amounts / partner identities>`.
- `<sensitive topic 2>`.
- `<sensitive topic 3>`.

**Redirect patterns.** When directly asked about a sensitive topic:

- `<sensitive topic 1>` → `<redirect script or scope-acknowledgment>`.
- `<sensitive topic 2>` → `<redirect script>`.

**Hard NEVERS** (regardless of who asks):

- `<absolute prohibition 1>`.
- `<absolute prohibition 2>`.

---

*Template ships in `_template/_confidential__SEP__Confidential_Profile.md`. At bootstrap, `bootstrap.py` (P50) substitutes `__SEP__` → `/`, landing the customized file at `<wiki>/_confidential/Confidential_Profile.md`. After bootstrap, populate all 11 sections with project-specific content. Status advances `outlined` → `solid` → `ready` per spec §2.3 as completeness grows. Never publish.*
