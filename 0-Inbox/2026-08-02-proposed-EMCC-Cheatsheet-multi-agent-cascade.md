---
title: "PROPOSED — EMCC/Cheatsheet.md § Multi-agent cascade (refresh)"
type: proposal
visibility: internal
completion: 100
status: draft
last_updated: 2026-08-02
canon_sources: ["EMCC.CRW/roster/roster.json (agent_id + role, read 2026-08-02)", "claude-peers list_peers @2026-08-02T04:21Z", "claude:EMCC-Director directive 2026-08-02T04:57Z (seat data, Chief-supplied)"]
unverified_claims: ["seat_id strings are Chief-proposed, not Operator-locked", "agent_id values for the 5 PROVISIONAL seats were supplied by the Director/Chief and are NOT in roster.json — not independently verifiable here"]
---

# PROPOSED replacement — `EMCC/Cheatsheet.md` § "Multi-agent cascade"

**Drafted by:** `claude:EMCC-library` (cba71e2b) · **Directed by:** `claude:EMCC-Director` (12a447b6), 2026-08-02T04:57Z
**Doc-class. No build gate.** Drafted in EMCC.Library because this seat has **no write lane into `EMCC`**;
landing it in `EMCC/Cheatsheet.md` is a post-wipe step the Operator authorizes. `EMCC` main is a shared
checkout with live panes — if it lands, use a worktree off `origin/main`, never in-place.

> ⚠ **PROVISIONAL seats are marked. Do not read them as canon.** Five seats below have **no roster row**.
> Their `agent_id`s were supplied by the Chief/Director and are **not** in `EMCC.CRW/roster/roster.json`.
> I could not verify them here and have not implied otherwise.

---

## Multi-agent cascade

### The order — read this before opening any pane

```
OPERATOR DECLARES  ->  CHIEF MINTS THE ROW  ->  PEER ADOPTS AND CONFIRMS
```

**Peers CONFIRM rows. They never ASSERT them.** A pane that names its own seat has not been seated.

### Declaration block — paste one per pane, fill every field

```yaml
llm:    claude | grok            # REQUIRED. One repo may legitimately host BOTH.
repo:   <lowercase canonical slug>
folder: <path containing .git>   # the folder with .git, not its parent
role:   <exact org.json role slug>   # internal-ciso — never "CISO", never "aegis"
status: new | re-init
```

Four fields decide routing; `status` decides whether the Chief mints or re-attaches. **`llm` is not
optional** — omitting it is what made two panes on one repo read as duplicates all session and produced
both dual-claims.

### Seats

`agent_id` is **assigned and immutable** (roster verdict `delta-force-2026-06-26-roster-sync-codepath.md`:
*"not created_at, **not hash-of-name**"*). `peer_id` is a **lease** and dies at every restart — never
address a seat by lease.

| seat_id | agent_id | llm | repo | folder | role slug | cert lane |
|---|---|---|---|---|---|---|
| `claude:EMCC-Director` | `12a447b6` | claude | `emcc` | `D:\Projects\Enterprise Matrix\EMCC` | director | — (orch only) |
| `claude:EMCC-library` | `cba71e2b` | claude | `emcc.library` | `D:\Projects\Enterprise Matrix\EMCC.Library` | librarian | — (doc-class) |
| `claude:EMCC-cartometrics` | `de135e63` | claude | `emcc.cartometrics` | `D:\Projects\Enterprise Matrix\EMCC.Cartometrics` | change-manager | — |
| `claude:isommelier-pm` | `ed4b6632` | claude | `isommelier` | `D:\Projects\iSommelier` | project-manager | — |
| `claude:EMCC-Auditor` ⚠ | `5c8d7bbc` **PROV** | claude | `emcc` | `D:\Projects\Enterprise Matrix\EMCC` | auditor | Regime B |
| `claude:EMCC-dfdu` ⚠ | `bb8310bf` **PROV** | claude | `emcc.dfdu` | `D:\Projects\Enterprise Matrix\EMCC.DFDU` | lattice-agent | cert → grok |
| `claude:isommelier-dfdu` ⚠ | `8010d5cc` **PROV** | claude | `isommelier` | `D:\Projects\iSommelier` | lattice-agent | cert → grok |
| `claude:anvil-pm` ⚠ | `6a3a3715` **PROV** | claude | `iron-soul-anvil` | `D:\Projects\IronSoul-Anvil\iron-soul-anvil` | project-manager | — |
| `grok:anvil-dfdu` ⚠ | `598c4337` **PROV** | **grok** | `iron-soul-anvil` | `D:\Projects\IronSoul-Anvil\iron-soul-anvil` | lattice-agent | cert → claude |
| `grok:EMCC-ExternalCertifier` 🔴 | **NO ROW EXISTS** | grok | `emcc` (cross) | `D:\Projects\Enterprise Matrix\EMCC` | external-certifier | certs claude-built |
| `claude:EMCC-ExternalCertifier` 🔴 | **NO ROW EXISTS** | claude | `emcc` (cross) | `D:\Projects\Enterprise Matrix\EMCC` | external-certifier | certs grok-built |
| Guard-House internal | `ea6ffd10` | claude | `emcc.guard-house` | `D:\Projects\Enterprise Matrix\EMCC.Guard-House` | **`internal-ciso`** | Layer 2 inline governance |
| Guard-House external | `563fdb34` | **≠ Layer 2 provider** | `emcc.guard-house` | `D:\Projects\Enterprise Matrix\EMCC.Guard-House` | **`external-ciso`** | Layer 3 independent backstop |

⚠ = provisional, no roster row. 🔴 = **gap**, see below.

### 🔴 Gaps the Operator must close — these are not cosmetic

1. **No External Certifier roster row exists — for EITHER vendor.** Nearest rows are `ea6ffd10`
   Internal CISO and `563fdb34` External CISO, which are **Aegis seats, not the cert plane**. Both
   `grok:EMCC-ExternalCertifier` panes therefore mint off-roster, which is *why* they collided.
   **`cert-handoff/v1.1` compares `certifier_id` as a STRING**, so two panes under one certifier_id are
   indistinguishable to the validator — it reports role-separation **satisfied for either**, including
   when the wrong pane certified. **The collision is downstream of a missing row.** No id invented here.
2. **An Auditor roster row EXISTS and is unused.** `6c3b378e` — *"independent post-build verification
   (Regime B)"*, module `EMCC.DFDU` — while the live pane advertises provisional `5c8d7bbc`. Note the
   mismatch precisely: the existing row is scoped **EMCC.DFDU**, the pane claims **EMCC + iSommelier +
   Anvil**. So it is *not* a drop-in adopt; the row needs its scope widened or a second row minted.
   **Operator call — but a row is available and unused.**
3. **iSommelier Auditor recusal.** `claude:EMCC-Auditor` is **RECUSED AS PRIMARY** for iSommelier
   (same-model, Opus 5 over Opus 5; that repo's baseline is cross-**model** Sonnet-over-Opus). iSommelier
   product **parks** until a Sonnet Regime-B seat lands — Operator-only, since seating chooses a model.
   ⚠ The recusal turns on a `model` value that is **harness-self-reported and unverifiable from inside**.
4. **The 5 PROVISIONAL `agent_id`s must NOT be laundered into roster rows as-is.** They were minted by a
   `sha256(seat_id.casefold())[:8]` scheme — i.e. **hash-of-name**, the construction the roster council
   verdict explicitly rejected. They are unique and G14-clean, so they are serviceable as **provisional
   identifiers**; rows must carry **ASSIGNED** ids.

### ★ Folder trap — verified, costs a pane every time

```
D:\Projects\IronSoul-Anvil                     <- NO .git   (container only — NOT the repo)
D:\Projects\IronSoul-Anvil\iron-soul-anvil     <- the real repo (origin: iron-soul-anvil.git)
```

Opening a pane in the container yields `fatal: not a git repository`. **Both Anvil seats use the INNER
path.** Verified 2026-08-02 by `.git` presence + `git remote get-url origin` on every path in the table
above; all others resolve at the listed folder.

### Launch lines

```bash
# EMCC — Director / Auditor / both External Certifiers all run from this folder
cd "D:/Projects/Enterprise Matrix/EMCC"              ; claude-peer   # + declaration block

cd "D:/Projects/Enterprise Matrix/EMCC.Library"      ; claude-peer   # librarian      claude
cd "D:/Projects/Enterprise Matrix/EMCC.DFDU"         ; claude-peer   # lattice-agent  claude
cd "D:/Projects/Enterprise Matrix/EMCC.CRW"          ; claude-peer   # chief          claude
cd "D:/Projects/Enterprise Matrix/EMCC.Cartometrics" ; claude-peer   # change-manager claude
cd "D:/Projects/Enterprise Matrix/EMCC.Guard-House"  ; claude-peer   # internal-ciso  claude
cd "D:/Projects/Enterprise Matrix/EMCC.Guard-House"  ; claude-peer   # external-ciso  MUST be a DIFFERENT provider from Layer 2
cd "D:/Projects/iSommelier"                          ; claude-peer   # project-manager + lattice-agent = TWO panes
cd "D:/Projects/IronSoul-Anvil/iron-soul-anvil"      ; claude-peer   # anvil-pm claude + anvil-dfdu GROK = TWO panes, TWO vendors
```

**`eddyandwolff` is NOT in the cascade** — it is an asset-registry pilot corpus, not a seated repo. It was
on the old sheet and never came up. Removed.

**Two panes on one folder is NORMAL** (iSommelier PM + builder; Anvil PM + builder; Guard-House L2 + L3).
The sheet must show `llm` and `role` or they are indistinguishable — that ambiguity produced both of
today's dual-claims.

### Post-wipe re-init

`peer_id` leases all die. `seat_id` + `role_tag` + `agent_id` survive — they are the durable address.
Every pane comes up `status: re-init`, **confirms** its row, and does **not** assert one. Re-resolve every
lease; **never cache a `peer_id`**, and never accept a self-reported one.

> `list_peers` **EXCLUDES SELF** — a pane cannot see its own lease, so absence there is never evidence of
> death. **Set difference:** present in another pane's list + absent from your own = **you**. Four seats
> misread this on 2026-08-02, including a Director that declared its own live lease dead.

---

## Honesty notes

- **Verified here:** every `folder` (`.git` presence + `origin` URL); the four roster-backed `agent_id`s;
  the Guard-House ids + their Layer-2/Layer-3 roles; the unused Auditor row `6c3b378e` and its
  `EMCC.DFDU` scope; the not-hash-of-name verdict; the Anvil container trap.
- **NOT verified here:** the five PROVISIONAL `agent_id`s (supplied, absent from `roster.json`); the
  exact `org.json` role slugs beyond `internal-ciso`/`external-ciso` as given by the Director — I read
  `roster.json`, not `org.json`.
- **No files written outside EMCC.Library.** No tests run — nothing here is code.
