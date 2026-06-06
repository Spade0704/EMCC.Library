# QA Sweep — caution-lint (`check_consequence`)

**Date:** 2026-06-06
**Scope:** `Biz.Automation/wikisys.library/_scripts/_lib/doc_lint.py` (`check_consequence` + `ConsequenceResult` + `_count_frontmatter_key`) and `tests/test_consequence_lint.py`.
**Pairs with:** pre-build gate `EMCC.DFDU/tasks/delta-force/2026-06-06-caution-lint.md`.
**Verdict:** **PASS-WITH-FIXES** (1 critical + 1 high security fix applied, with regressions; readability gaps closed). Independent Lattice Auditor (Regime B) still owed before canon promotion.

## Stage 1 — DFTS + decomposition
DFTS **borderline-low** (additive, read-only, report-only default, no shared state, no data model) — but it is a *safety-tier classifier* where fail-open is the failure that matters, so a right-sized sweep was run: **Correctness**, **Security/fail-closed**, **Readability** (concurrency N/A — pure function). Components: (a) tier resolution + fail-safe; (b) cite requirement + enforce/report-only routing; (c) read-only guarantee; (d) naming/idiom.

## Stage 2 — Auditor findings
Correctness auditor hit a session limit mid-run; its domain (fail-safe tier resolution) was independently fuzzed sound by the security auditor (list/null/`~`/empty/`medium`/Cyrillic/no-fm/unclosed all → HIGH `field_present=False`).

| # | Sev | Finding | Disposition |
|---|---|---|---|
| 1 | **CRITICAL** | Unguarded `path.read_text("utf-8")` *raises* on missing/non-UTF-8 file → a raise in a build gate is **fail-open**: caller loop aborts and skips every page after the poison file (confirmed with a 3-file sim where `03_federal_ssusa` HIGH/no-cite was never evaluated). | **FIXED** — read wrapped in `try/except (OSError, UnicodeDecodeError)`; unreadable → `consequence="high"`, routed through enforce/report-only (error if enforce, warning if report-only). Never raises. |
| 2 | **HIGH** | Subset parser is last-wins; a trailing duplicate `consequence: low` after `consequence: high` silently flips a HIGH page to LOW (`ok=True`). | **FIXED** — `_count_frontmatter_key()`; a duplicate top-level `consequence:` → ambiguous → fail-safe HIGH with a specific message. |
| 3 | MEDIUM | `enforced` result field unused/unasserted (only field with zero coverage). | **FIXED** — kept (useful caller metadata) + asserted (`test_enforced_field_echoes_input`). |
| 4 | LOW | No test for the no-frontmatter (body-only) page — the most likely un-migrated input. | **FIXED** — `test_no_frontmatter_body_only_resolves_high_failsafe`. |
| 5 | MEDIUM | `consequence: low # comment` opts out; LOW audit-trail blind spot. | **DEFERRED** — defense-in-depth audit-trail (record raw opt-out line); scope creep for a spike. Noted for canon promotion. |
| 6 | LOW | Indented `consequence:` accepted as top-level (parser quirk in `frontmatter.py`). | **DEFERRED** — lives in the shared parser; more invasive than the spike. Noted. |
| 7 | LOW | `field_present` name reads like "field exists" (it means "recognized tier declared"); magic strings `"high"/"low"`. | **DEFERRED** — rename + constants at canon promotion (provisional-naming step). |

Positives recorded: pattern-conformant with the `*Result`/`check_*` family; honest about provisional `consequence` naming; fail-safe message discoverable + asserted; read-only claim backed by a byte-identity test.

## Stage 3 — tests + live simulation
- `python -m unittest tests.test_consequence_lint` → **13/13** (was 8; +5 regressions).
- `python -m unittest discover -s tests -t .` → **644/644** (6 skipped); no regressions (was 639).
- **Live gate-loop sim** over `{HIGH/no-cite, poison non-utf8, HIGH/no-cite, dup-key-flip}` with `enforce=True`: **4/4 pages evaluated, no crash** (fail-open fixed); poison flagged HIGH-unverified; both downstream HIGH pages reached; duplicate-key page held at HIGH.

## Stage 4 — fixes
One consolidated pass on `doc_lint.py` (read guard + `_count_frontmatter_key` + duplicate message branch) and `tests/test_consequence_lint.py` (+5 regressions). Re-ran Stage 3 to green.

## Stage 5 — verdict + lessons
**PASS-WITH-FIXES.** Deferred items (5–7) are non-blocking and routed to canon promotion. Recurring defect classes appended to `tasks/lessons.md`:
1. **Unguarded I/O in a gate function = fail-open** — a build/safety gate that can raise will abort the caller's loop and silently skip downstream items. Guard I/O; fail *closed* to the safe tier; never let a gate raise.
2. **Subset-YAML last-wins enables silent key-flip** — a duplicate safety-critical key (e.g. `consequence`) can override the intended value. Detect duplicates for safety fields → treat as ambiguous → fail-safe.
