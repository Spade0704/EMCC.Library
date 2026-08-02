---
title: "Director doc-class drafts — L1/L2/L3 (INTERIM)"
type: proposal
visibility: internal
completion: 100
status: draft
last_updated: 2026-08-02
canon_sources: ["EMCC/framework/22-coding-workflow.md @53050a0f", "EMCC/templates/consumer-project/.claude/personas/CLAUDE.project-manager.md @53050a0f", "iSommelier/.claude/personas/CLAUDE.project-manager.md @1c1d108"]
unverified_claims: []
---

# Director doc-class drafts — L1 / L2 / L3

**Author:** claude:EMCC-library (agent_id cba71e2b) · **Directed by:** claude:EMCC-Director (12a447b6), 2026-08-02T04:16Z
**Class:** doc-class draft only. No code. No product. Human merges.

> ⚠ **ALL THREE ARE MARKED INTERIM** per the Director's instruction. They are Level-2+ canon locks
> ruled under a stalled-builder constraint; `/llm-council` is being proposed to the Operator for the
> permanent lock and **the wording may change**. Do not cite these as settled canon.

> **Drafts live here, not in the target repos.** L1/L3 target `EMCC/`, L2 targets `iSommelier/` (and
> see the finding — really `EMCC/templates/`). All three are outside `EMCC.Library`. No write lane is
> registered for this seat; per the Chief's standing rule, path-ownership collisions are raised, not
> self-resolved. Text is complete and ready to apply.

---

## L1 — `EMCC/framework/22-coding-workflow.md`: verdict-close ≠ merge act

**Verified against `@53050a0f` (EMCC main, clean).** The conflation is real and sits at **line 166**.

### ★ Finding: the defect is in TWO places, not one

The Director named the §7/§8 table row. A sweep for close-authority language found the same defect
also asserted in the **Roles** section:

| line | current text | status |
|---|---|---|
| 20 | `- **Director/PM** — owns spec, plan approval, and **sprint close**. Operator's chat counterpart.` | **ALSO WRONG** — not named in the directive |
| 156 | `\| 1. Spec / framework \| Director/PM (+operator) \| …` | **CORRECT, leave alone** — spec authoring is legitimately shared |
| 166 | `\| 8. Close \| Director/PM \| **DUAL PASS required** … \| merge + tasks/sessions.md \|` | wrong (as directed) |

Fixing only line 166 leaves line 20 asserting the PM owns sprint close — the precise claim the
ruling denies, in the section a reader hits *first*. Both fixed in one pass, as instructed.

### Proposed line 20

```markdown
- **Director** — owns spec, plan approval, and the dual-PASS **verdict-close**. Operator's chat
  counterpart. Does **not** merge and does **not** build. **PM** co-owns spec + plan approval for its
  own project; the PM does **not** close the dual-PASS verdict. (INTERIM — see §Close authority.)
```

### Proposed line 166

```markdown
| 8. Verdict-close | Director (NOT PM) | **DUAL PASS required** (Auditor + cross-vendor cert) | verdict logged + `tasks/sessions.md` |
| 8a. Merge | **Human Operator ONLY** | the Director closes the verdict; it does not merge | merge commit / PR merge |
```

Splitting into two rows rather than rewording one is deliberate: the merge act gets its own row with
its own owner, so it cannot be re-absorbed into the close row by a later editor.

### Wording note — the Director's quotation is a paraphrase

The directive cites iSommelier as already splitting these, quoted as *"Human merges; the Director
does not."* That exact string does **not** appear in iSommelier. The real, council-locked phrasings
are (`.claude/skills/process-feedback/SKILL.md:3,10,25`, `run-routine/SKILL.md:3,22`):

- *"NEVER auto-merges; the human merges everything."*
- *"The output is **always a DRAFT PR**. The human merges everything (council-locked)."*
- *"…is never ceded; that's why the human merges."*
- plus `human-at-merge` used as a term of art throughout `0-Inbox/grok-audit/*`.

Drafted against the **actual** wording, not the paraphrase. Flagging rather than silently
substituting: the two mean the same thing here, but adopting a paraphrase as canon is how a
verbatim source drifts.

### Suggested anchor for §Close authority

```markdown
### Close authority (INTERIM — ruled 2026-08-02 under a stalled-builder constraint; `/llm-council` pending)

Three acts, three owners, never merged into one:
1. **Verdict-close** — Director ONLY. Requires DUAL PASS (Auditor + cross-vendor cert).
2. **Merge** — Human Operator ONLY. No agent merges, ever, regardless of verdict.
3. **Build** — Lattice ONLY. Neither the PM nor the Director codes.

A dual-PASS verdict is a *finding*, not permission to merge. The Director's close ends the gate; it
does not touch the branch.
```

---

## L2 — iSommelier PM persona: close-authority clause + P-AUTH condition

**The directive's premise is confirmed.** `iSommelier/.claude/personas/CLAUDE.project-manager.md`
(`last_updated: 2026-06-03`, 3892 bytes, `@1c1d108`) is **silent on close authority** — verified by
whole-file read, not by search. Its three-tier chain is at **:16** (Director → PM → module agents),
with the routing hops at **:35** (fan out) and **:37** (aggregate/escalate). Nothing in it mentions
dual-PASS, merge, or who closes.

### 🔴 ★ FINDING — THIS FILE IS A DISTRIBUTED ARTIFACT. EDITING IT IS THE GENERATED-FILE TRAP.

Line 46 of the iSommelier copy declares it:

> *Distributed by EMCC `scripts/emcc_bootstrap.py` / `scripts/emcc_wire.py`. `iSommelier` is
> substituted at scaffold time. Per-project; one Project Manager instance per consumer project.*

The canonical source is **`EMCC/templates/consumer-project/.claude/personas/CLAUDE.project-manager.md`**
(`{{PROJECT_NAME}}` placeholders). Hand-editing the iSommelier copy means:

1. **It fixes 1 of 8 consumers.** Eight live copies on disk, and I checked every one for close-
   authority language — **all eight silent**:

   | consumer | sha256[:12] | bytes | BOM | CR | close-authority? |
   |---|---|---|---|---|---|
   | **TEMPLATE** (canonical) | `e0998229c25b` | 6764 | no | 0 | **no** |
   | AI-Factors | `c7aec441fa53` | 3892 | no | 46 | no |
   | eddyandwolff | `a6c6c3565c91` | 3906 | no | 46 | no |
   | EMCC.Gateway | `24b1a94e1a4c` | 3860 | no | 0 | no |
   | EMCC.Marketing | `989dbdb6b0fb` | 6746 | no | 0 | no |
   | Iron Soul | `cf36c5f7dd79` | 3885 | no | 46 | no |
   | **iSommelier** | `0af252d7a69c` | 3892 | no | 46 | no |
   | Mentor | `908b0c58af68` | 3864 | no | 46 | no |
   | residehub | `1aa55110c758` | 3885 | no | 46 | no |

   (Hashes differ legitimately — `{{PROJECT_NAME}}` is substituted per repo. Byte-size is the
   comparable signal.)

2. **A later `emcc_wire.py` run silently reverts the clause.** Same class as this repo's own
   `.claude/personas/CLAUDE.librarian.md` trap: edit the canonical source, redistribute.

3. **★ iSommelier's copy is not merely silent — it is 12 days STALE and missing a whole HARD RULE.**
   Template `last_updated: 2026-06-15` / 6764 bytes vs iSommelier `2026-06-03` / 3892 bytes. The
   ~2,870-byte delta is not cosmetic. The template carries, and **iSommelier does not**:
   - **§ "No-implementer hard rule (enforced delegate-or-escalate)"** (template :42-56) — the
     structural fix for *"a PM coded a hard bug itself for ~1h because its implementer tier was never
     instantiated and the gap was silent"* (`tasks/council/2026-06-15-pm-workflow-role-model.md`).
   - **:23** — the gate-bound boundary: PM may do **L0/L1 only**; any L2+ code task, or *any* code
     task with no live Lattice implementer, is FORBIDDEN.
   - **:35 step 1b** — the startup `LATTICE_AVAILABLE = true|false` implementer-availability check.

   So iSommelier's PM is running today **without the no-implementer hard rule**, which is a strictly
   larger hole than the close-authority silence the directive was filed against — and it is the same
   family: *the PM's non-delegable boundaries are unstated, so they are unarbitrable.* The
   directive's own diagnosis, one layer down.

   ⚠ **Consequence for L2 as scoped:** patching close-authority onto the stale iSommelier copy
   produces a file that is *newly divergent from the template in one way while still missing three
   things* — and it would look updated (`last_updated` bumped) while remaining the most out-of-date
   PM persona in the portfolio. **Recommend: apply to the TEMPLATE, then re-wire iSommelier**, which
   closes both holes at once and fixes the other seven consumers. Director's call — flagging, not
   deciding.

### Proposed clause (drafted for the TEMPLATE, `{{PROJECT_NAME}}` form; drops in after the three-tier chain at :16)

```markdown
## Close authority — what is NOT delegable to this PM (INTERIM RULING 1, 2026-08-02)

> **INTERIM.** Ruled by claude:EMCC-Director under a stalled-builder constraint; `/llm-council` is
> proposed for the permanent lock and the wording may change. Do not cite as settled canon.

**What the PM MAY do — the three-tier chain STANDS.** This PM directs its own project's module
agents **directly** (chain above; fan-out and aggregation in the operating loop). `framework/22`
does **not** supersede that routing hop — f/22 is simply *silent* on it, and silence is not
supersession.

**Four things are NON-DELEGABLE to the PM:**

| # | Act | Owner | Never |
|---|---|---|---|
| 1 | **Dual-PASS verdict-close** | **Director ONLY** | the PM does not close a dual-PASS verdict |
| 2 | **Merge** | **Human Operator ONLY** | no agent merges — not the PM, not the Director |
| 3 | **Building** | **Lattice ONLY** | neither the PM nor the Director codes |
| 4 | **Auditor independence** | Auditor ≠ builder | the PM never runs, overrides, or re-roles the Auditor |

**P-AUTH condition on PM tasking.** PM tasking authorizes product work **only** as a flat
`kind: directive_assignment` row in **{{PROJECT_NAME}}'s OWN `tasks/orchestrator-log.jsonl`**, with
`directive_ref` resolving **in that same repo's log**. A directive that resolves only in another
repo's log, or only in a peer message, does not authorize product work here.
```

---

## L3 — NEW canon entry: HIGH-BLAST predicate (independence as mechanism)

Placed so `framework/22`'s workflow table can reference it — proposed as a new section in
`framework/22-coding-workflow.md` adjacent to the §7a Auditor row, referenced from the table as
`(blast class — see §Blast classification)`.

```markdown
### Blast classification (INTERIM — RATIFIED 2026-08-02; `/llm-council` pending for permanent lock)

**Predicate.** HIGH-BLAST is classified **twice, independently**, and disagreement PARKS the atom.

1. **The builder DECLARES** a blast class in the cert handoff. A declaration is an input to the gate,
   never a finding.
2. **The Auditor CLASSIFIES INDEPENDENTLY** — and this is the mechanism, not a courtesy:
   **the Auditor's classification must be reached without the builder's declared class anchoring it.**
   The Auditor forms its class from the diff and the blast surface, then compares. Reading the
   builder's number first and then "agreeing" is not an independent classification; it is the
   builder's classification with a second name on it.
3. **Disagreement ⇒ PARK.** Not the builder's call. Not the Auditor's unilateral call.
   **Never averaged, never split, never rounded to the lower class.** A parked atom escalates to the
   Director for routing; it does not proceed at either party's number.

**Why the independence is written as a mechanism.** An anchored classification is a control that
cannot fail in the direction that matters: if the builder's declaration sets the Auditor's frame,
then a HIGH-blast change declared LOW gets a second signature attesting LOW, and the gate reports
two agreeing classifications where it has one classification counted twice. The two-party structure
then reads as corroboration while providing none.

**Consequence:** an Auditor that cannot show it classified before reading the declaration has not
satisfied this predicate, and its agreement carries no independent weight.
```

---

## Deliberately NOT written (per the directive)

- **`director_id` controlled vocabulary (RULING 2)** — HELD. Its permanent form is exactly what goes
  to council. Not drafted, not sketched.
- **Any `pm_id` field** — NOT drafted. A schema change is a build; unauthorized for this seat and
  for this class.

## Side finding — outside this directive, inside this seat's lane

`EMCC` HEAD `53050a0f` carries a **leading UTF-8 BOM (`ef bb bf`) in the git commit SUBJECT**:
`b'\xef\xbb\xbfdocs(hand...'`. Verified by reading the bytes, not by eyeballing the log. Cosmetic in
isolation, but it is the same PowerShell-redirection encoding family already filed in this repo's
`tasks/todo.md` (the 🔴 line-ending/BOM item) and the one the Anvil PM hit in `orchestrator-log.jsonl`.
Reported, not acted on — EMCC's history is not mine to touch.

Related, same sweep: **5 of 8** deployed PM personas are CRLF (`CR=46`) and **3 are LF** (`CR=0`),
against an **LF** template. The distribution path is already producing mixed line endings across
consumers. Consistent with the unasserted-line-ending-identity 🔴; no `.gitattributes` anywhere in
the chain.

## Honesty notes

- **Everything above was read, not recalled.** f/22 lines 20/156/166/167 and the two persona files
  were opened; the eight-copy table is hashed output; the BOM is byte-level.
- **The `-wt-*` directories ARE real worktrees this time.** `git worktree list` in iSommelier returns
  all 10 with branches attached. Checked because this exact naming convention previously read as
  git identities when two of them had no `.git` at all — the check was warranted and came back clean.
- **No test suite was run.** Nothing here is code; nothing green is claimed.
- **No file in `EMCC/` or `iSommelier/` was modified.**
