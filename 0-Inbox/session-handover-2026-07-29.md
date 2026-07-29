# Session handover — EMCC.Library (Librarian seat) — 2026-07-29

Bridge doc for a fresh room. Transient: the durable record is `tasks/sessions.md`
(2026-07-28 entry) + `tasks/todo.md`. This file points and deltas; it does not mirror canon.

Covers the 2026-07-28 Librarian session and the 2026-07-29 close-out (housekeeping + this
handover). **Scope: EMCC.Library only.** EMCC, EMCC.DFDU, EMCC.CRW and iron-soul-anvil each had
a live seat during this session; they were deliberately not touched. That was a lane decision,
not an omission.

---

## Read first (in this order)

1. `CLAUDE.md` — operating rules (spec wins; stdlib only; verbatim discipline; never self-code
   under framework/22).
2. `Index.md` — the 3-zone router. Route, do not grep.
3. `tasks/sessions.md` — the **2026-07-28** entry. Longest and most load-bearing.
4. `tasks/todo.md` — two RED items are new and both are ours.
5. `tasks/lessons.md` — the top two lessons were written this session and one was corrected
   by a peer the same day. Read both, including the correction.

---

## State of main

`main` is clean, synced, and green: **956 tests OK (skipped=6)**, plus 8/8 CI jobs across
Python 3.10-3.13. HEAD = `94f0d39`.

Shipped this session (all coordination-plane, direct-to-main, zero code files changed):

| Range | What |
|---|---|
| `5708dbd..2555fd7` | 9 commits: two stale cross-repo items closed, six findings filed, two lessons written, session recorded |
| `94f0d39` | **PR #69 merged + branch deleted** (was a draft, open since 2026-07-23) |

No open PRs. No local or remote branches other than `main`.

---

## Locked decisions — DO NOT re-litigate

- **The Librarian seat does not build.** Under framework/22 every build routes to a Lattice peer;
  the Auditor must be independent of the builder. Both RED items below are code and were
  deliberately **filed, not built**.
- **No self-audit of this repo.** The MOD-2 dead-coverage sweep of EMCC.Library stays with an
  independent seat. This was raised unprompted on 2026-07-27 and the Director routed it away.
  Do not "just check it quickly" — being both the sweep's subject and its instrument is a vacuous
  control.
- **MOD-14 leads MOD-13/14/15.** Settled with the Director 2026-07-28: for *sequencing*, realised
  harm outranks blast radius. MOD-13 keeps its higher severity; it is simply not first.
- **The `mechanical-pass-human-aesthetic` blocker is DISCHARGED.** Shipped in EMCC PR #366 on
  2026-07-26. Verified against `validate_cert_handoff.py` at EMCC main `95ae091`. Do not re-file.
- **P0b's cert re-run is Anvil's, not ours.** No P0b drop exists under `0-Inbox/grok-audit/`.
  Confirmed and re-routed by the Director.
- **The push-bypass line is BY DESIGN.** Pushing an allowlisted file to `main` prints
  `remote: Bypassed rule violations ... Changes must be made through a pull request`. Portfolio
  Path-B fence, 22/22 repos: require-PR carries an intentional admin bypass; history-protection
  has none and binds admins. **Four seats have now read this as a failure. You are not the fifth.**
- **Anvil vendoring needs no Sync action.** Already vendored by hand and byte-identical.
- **Anvil game scope is ACTIVE** (Operator, 2026-07-23; council PROCEED at proposal v1.2). The old
  "DEFERRED until JP says so" line was stale for six days and is now reconciled.

---

## Next, in order

1. **[RED] Line-ending identity is unasserted repo-wide.** The repo has **no `.gitattributes`**;
   `core.autocrlf` is UNSET locally and globally, `system: input` — the Git-for-Windows installer.
   Every byte-identity claim the kit makes currently holds by machine accident: the section 9.9
   schema, both verbatim-shipped procedures, the persona drop-in, `_template/` payloads.
   The sharp part: `tests/test_persona_dropin.py` compares via `read_text` (:66, :68), and Python
   text mode normalises CRLF to LF, so **our guard is newline-blind and false-GREENS** on exactly
   the drift it exists to catch — while Anvil's byte-exact pin false-REDS on it. Same missing
   `.gitattributes`, opposite symptoms; **ours is the quiet one, and we are the side that ships.**
   Three-part fix is written out in `tasks/todo.md`. Code, so PR under framework/22, and it wants
   a seat other than the Librarian since it constrains the writer.
2. **[AMBER] The section 9.9 schema has no machine-readable identity** — no `$id`, no `version`,
   no date. The version exists only as prose `v0.1` inside `description`: **present and
   unaddressable**, which is worse than absent. Ship `$id` + `version` in the SAME PR as item 1 or
   the detector can only ever report DIFFERENT, never older/newer.
   **Ordering trap:** stamping them changes the bytes, which breaks Anvil's pin. The fix is its
   own first exercise of the reconcile path, and it presents as "hash changed, version unchanged" —
   the signature a naive control would flag as tampering. Anvil PM `v6u2ccqi` has pre-recorded the
   red as EXPECTED and will re-vendor on notice.
3. **Asset-registry v1.4 CORE — Grok slot still OPEN, unrouted.** Built, Auditor concerns-proceed.
   Cert drop staged at `0-Inbox/grok-audit/2026-07-21-asset-registry-core.md`. The Director knows
   and chose not to route it during the census.
4. **MOD-13/14/15** — engine defects filed at EMCC, fixes owed by this repo. MOD-14 first.
5. **MOD-2 sweep of this repo** — independent seat only. Method is pinned in `tasks/todo.md`
   including the Rule 9b applicability guard.
6. **Game-class spec amendment** per the newly merged 2026-07-23 gate. **Amendment class is an
   OPERATOR call** — v1.5-additive per the 2026-07-21 precedent vs the 2026-07-23 council's v2.0.
   Two more OPERATOR items came in with that merge: deletion/takedown policy vs URL permanence,
   and OP-5 R2 provisioning ownership.

---

## Standing commitment to another repo

**Section 9.9 must not move without telling the Anvil PM (`v6u2ccqi`) first.** Their pin is
currently the portfolio's only line-ending detector on that schema — and it only functions while
their box keeps `core.autocrlf=input`. A seat installed with `autocrlf=true` gets a permanently-red
pin, which gets muted or re-stamped to local CRLF bytes, after which **the only detector reports
green on converted bytes.** This is a promise from a seat, not a control, which is why item 1 exists.

---

## How to operate

- Advertise on `claude-peers` at session start: `[ROLE:librarian][REPO:EMCC.Library]`
  (framework/09 section 4.2).
- Coordination plane (`tasks/todo.md`, `tasks/sessions.md`, `tasks/lessons.md`,
  `tasks/audits/`, `0-Inbox/grok-audit/`, `0-Inbox/session-handover-*.md`) pushes direct to `main`.
  **Everything else, including all code and `0-Inbox/` docs generally, must go via PR** —
  `cert_push_guard` enforces this and it refused a push during this very close-out. That refusal
  was correct.
- Verify with `python -m unittest discover -s tests -t .` from the repo root. Baseline 956/6.

---

## Gotchas the next room would otherwise rediscover

- **Never hash a git blob through a PowerShell redirect.** `git show <ref>:<path> > $tmp` in PS 5.1
  re-encodes (CRLF + BOM). It reported false drift on a schema we own during this session. Use
  `subprocess.run([...], capture_output=True).stdout` or compare blob OIDs with
  `git rev-parse <ref>:<path>`.
- **When a suspicious number equals the line count, suspect the instrument before the artifact.**
  Two seats hit this within one hour, in two different shells. Line-oriented instruments fail
  line-shaped.
- **A later measurement does not outrank an earlier stronger one just by being later.**
- **Two directories under `D:\Projects\IronSoul-Anvil` ending in `-wt` are NOT worktrees** — no
  `.git`, unregistered. Hashing them proves nothing about Anvil's tracked state. Read the committed
  blob instead.
- **Use `git commit -F <file>`**, not `-m`, for multi-line messages in PS 5.1.
- The Codex frontmatter parser is a YAML subset; block-list sequences silently become `None`.

---

## RESUME-PROMPT

**Resuming EMCC.Library as the Librarian.** Read first: `CLAUDE.md`, then `Index.md`, then the
**2026-07-28** entry in `tasks/sessions.md`, then `tasks/todo.md` (top two RED items), then the top
two entries of `tasks/lessons.md`. Advertise `[ROLE:librarian][REPO:EMCC.Library]` on claude-peers.

**State:** `main` clean and green at `94f0d39` — 956 tests OK (skipped=6), 8/8 CI. No open PRs, no
branches but `main`. Last session changed zero code files: it closed three stale backlog items,
filed six findings, and merged draft PR #69 (game/Anvil scope activation + the 2026-07-23 gate
verdict).

**Do not re-litigate:** the Librarian seat does not build (framework/22 — route builds to a Lattice
peer); no self-audit of this repo's MOD-2 sweep; MOD-14 leads MOD-13/14/15 on realised harm; the
`mechanical-pass-human-aesthetic` blocker is discharged (EMCC PR #366); P0b's cert re-run is
Anvil's; Anvil game scope is ACTIVE since 2026-07-23; and the
`remote: Bypassed rule violations` line on push is BY DESIGN — four seats have already misread it,
do not become the fifth.

**Next, in order:** (1) the RED line-ending item — no `.gitattributes` anywhere, and
`test_persona_dropin` compares with `read_text` so it is newline-blind and false-GREENS on the drift
it exists to catch, while Anvil's pin false-REDS; we are the side that ships, so ours is the
dangerous half. (2) Ship `$id` + `version` on the section 9.9 schema in that same PR — the version
currently exists only as prose `v0.1` in `description`, and stamping it will break Anvil's pin once,
by design and pre-agreed. (3) The asset-registry v1.4 CORE Grok slot is still open and unrouted.
(4) MOD-14 then MOD-13/15. (5) The MOD-2 sweep stays with an independent seat.

**Both (1) and (2) are code: file and route them under framework/22, do not build them from this
seat** — they constrain the writer. Coordination-plane files push direct to `main`; everything else
goes via PR, and `cert_push_guard` will refuse otherwise.

**Standing promise:** do not move the section 9.9 schema without messaging the Anvil PM
(`v6u2ccqi`) first.

**Gotcha that cost real time:** never hash a git blob through a PowerShell redirect — PS 5.1
re-encodes and it produced false drift on a schema we own. Use binary `subprocess` stdout or
`git rev-parse <ref>:<path>`.
