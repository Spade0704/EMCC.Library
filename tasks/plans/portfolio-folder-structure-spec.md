# Portfolio Folder-Structure Spec (refined draft → Codex v1.1)

## Context

Codex v1.1 ships a `bootstrap.py` that generates the consumer-project layout
for every project in the operator's portfolio — including the EMCC
modules, which are now in scope (scope expanded after first plan review).
The operator's first-draft tree raised nine open questions (F1–F9). Round
two added three more: a wiki public/private split (F10), an `assets/`
root folder (F11), and a `website/` root folder (F12). This document
inventories the portfolio across all eight repos, addresses each open
question, and outputs the refined spec in three sections:

  (a) Canonical Structure Spec
  (b) Migration Paths per Existing Project
  (c) bootstrap.py Output Spec

---

## Portfolio Inventory

### Consumer projects (operator's apps & content)

| Project | Stage | Frame today | Notes |
|---|---|---|---|
| **tat_app** | Active code (Flutter) + dogfooded | `Tasks/` (cap T), lowercase task files + `archive/` folder; `.claude/` at root w/ skills; root `CLAUDE.md` v2.5 (ROOT_INDEX + R_* drawers); `docs/grok/` for AI specs | Memory-architecture benchmark; no separate Index.md (embedded) |
| **aviation** | Active code (Python) | Everything nested in `etihad-wiki/`; `build_wiki/` Python package = automation; `output/` = wiki content; `.claude/` nested; no tasks/ | Project = role (aviation); wiki = subject (etihad). Wiki-name vs project-name divergence is real |
| **aviation-career** | Thin braindump | One folder `competencies/` + `README.md`; no CLAUDE.md, no tasks, no automation | Doesn't fit "wiki + automation + tasks" — minimal frame only |
| **eddyandwolff** | Active wiki + dogfooded automation | `git/` vs `Local/` project-root zoning (public/private split); `git/INDEX.md` separate from CLAUDE.md; `Biz_*.md` umbrellas; `git/automation/` with Pascal_Case subfolders; `git/website/` (Squarespace clone + drafts); `git/brand_assets/`; `Grok/` parallel Obsidian vault | **Strongest precedent for separate Index.md, for public/private zoning, AND for website/ as a top-level concept** |
| **isommelier** | Active code (Next.js) + dogfooded | `mvp/` = Next.js app (isommelier.co); `tasks/` (lower t); `nexus/lattice/` agent framework; `docs/` flat + `docs/Archive/`; `business/`, `scripts/`, `specs/`, `types/`, `research/`, `assets/`; root CLAUDE.md w/ ROOT_INDEX | Code-heavy; multiple code-adjacent root folders need slotting |

### EMCC modules (orchestration infrastructure)

| Module | Role | Frame today |
|---|---|---|
| **EMCC** | Orchestration root — Director + Migrator agents; portfolio scanner; consumer-project bootstrap | `0-Inbox/` (hyphen ✓), `tasks/` (todo/sessions), `scripts/` (Python automations), `Documentation/`, `templates/`, `_blueprints/`; `CLAUDE.md`, `PROJECT_INDEX.md`, `README.md`, `EMCC.md`, `FRAMEWORK.md`, `ROADMAP.md`, `module.json`-adjacent files; no `.claude/`, no `wiki.*/` |
| **EMCC.DFDU** | Lattice 3.0 protocol module | `0-Inbox/` (hyphen ✓), `tasks/` (todo/sessions/lessons/archive + architect-notes, spec-readiness-tracker), `documents/lattice/` (12 numbered canonical docs), `documents/lattice-2.0-legacy/`, `documents/argot/`, `scripts/`, `schemas/`, `personas/`, `tests/`; `CLAUDE.md`, `TIERS.md`, `MIGRATION-ISSUES.md`, `SOURCE-HISTORY.md`, `module.json`. `.lattice/` gitignored runtime. **No `wiki/`** |
| **EMCC.Library** | Codex protocol module — hosts the Codex wiki itself | `0. Inbox/` (period+space — older convention), **`wiki.codex/`** with: `Home.md`, `00-Start-Here/`, `01-Architecture/`, `02-Operations/`, `04-Contributing/`, and underscore system folders `_canon/`, `_config/`, `_context/`, `_decisions/`, `_scripts/`, `_sources/raw/`, `_brain_dump/` (last is gitignored), plus `.claude/personas/` *inside* the wiki. Status: `not-ready` (awaits EMCC Step 2 SHIP) | **The operator's draft IS a generalization of `wiki.codex/`'s pattern.** Splitting `wiki.codex/`'s underscore folders into a separate `wikisys.<name>/` (system) and `wiki.<name>/` (content) is the refactor proposed. |

### Cross-cutting observations

- **Dot convention is portfolio-wide** at the repo level: `EMCC.DFDU`, `EMCC.Library`, `EMCC.Guard-House` (planned). Operator's draft (`Biz.Automation`, `wikisys.<name>`, `wiki.<name>`) extends this convention into folder names.
- **Inbox naming has split:** EMCC + EMCC.DFDU use `0-Inbox/` (hyphen). EMCC.Library uses `0. Inbox/` (period+space). The hyphen form is the **more recent** convention and is what the operator's draft adopted. Canonical: `0-Inbox/`.
- **No `.claude/` at the project root** in EMCC modules (only consumer apps). Pattern is "active workspace projects get `.claude/`; specs/docs modules don't."
- **`wiki.codex/` already proves the dot-named wiki pattern.** Adopt it portfolio-wide.
- **Task file convention split:** Title-Case (`Todo.md`) was operator's draft; existing portfolio mostly lowercase (`todo.md`). EMCC and EMCC.DFDU use lowercase (`tasks/todo.md`, `tasks/sessions.md`). **Reconsidered:** match what the larger half of the portfolio already does → **lowercase** (`todo.md`, `sessions.md`, `lessons.md`, `archive.md`). Operator's draft overruled in favor of existing portfolio consistency.
- **Index.md vs CLAUDE.md split:** eddyandwolff is the only project that splits them. EMCC has `PROJECT_INDEX.md` as the directory. Most projects embed the index in CLAUDE.md.
- **Public/private zoning is real and load-bearing:** eddyandwolff's `git/` vs `Local/` zoning encodes a security boundary (financial docs, contracts, bank statements cannot leak to GitHub). The operator's new F10 request extends this concept into `wiki.<name>/` granularity.
- **Website as a category exists** in eddyandwolff (`git/website/`). Squarespace clone + careers page + content drafts live together. This justifies a root-level `website/` folder when applicable.
- **Assets as a category exists** in eddyandwolff (`git/brand_assets/`) and isommelier (`assets/`). Justifies a root-level `assets/` folder.

---

## Open Questions — Resolved

### F1. `.claude/` location → **stays at project root, never under Biz.Automation.**

Claude Code's auto-loader looks for `.claude/` from the working directory
upward. A nested `Biz.Automation/.claude/` is never discovered unless the
user `cd`s into it. Confirmed by every active workspace project on disk.
Optional mirror folder `Biz.Automation/_personas/` allowed for human
reference; the auto-loaded directory is non-relocatable.

### F2. `Index.md` purpose → **root-level file-map; CLAUDE.md = rules+persona; both allowed to embed.**

- **`CLAUDE.md`** — operating rules, hard constraints, persona, memory
  architecture (R_* / D_* drawers), read-order.
- **`Index.md`** — file-map / routing table (markdown table of folders +
  key files with one-line purpose). eddyandwolff's `git/INDEX.md` is the
  canonical example. EMCC's `PROJECT_INDEX.md` is an older variant.

**Canonical filename: `Index.md`** (mixed case, matches `CLAUDE.md`'s
casing). `PROJECT_INDEX.md` deprecated → rename target.

**Variance:** thin projects may embed Index as a top section of
CLAUDE.md (matches tat_app + isommelier's existing pattern). Bootstrap
generates the separate file; projects collapse if they choose.

### F3. `0-Inbox` naming → **`0-Inbox/` (hyphen, capital I).**

EMCC + EMCC.DFDU already use this form (the more recent convention).
EMCC.Library's `0. Inbox/` is the older form and is a migration target.
`_inbox` rejected (sorts wrong); `0. Inbox` rejected (space).

### F5. Frame-container separator → **dots, portfolio-wide.**

EMCC.DFDU, EMCC.Library, EMCC.Guard-House already use dots at the repo
level (`EMCC.DFDU`). `wiki.codex/` in EMCC.Library already uses dots at
the folder level. Operator's draft (`Biz.Automation`, `wikisys.<name>`,
`wiki.<name>`, `<name>.doc/`) extends an existing convention — adopt.

Scope of the dot convention (mandatory for these container patterns):

- `Biz.Automation/`
- `wikisys.<projectname>/`
- `wiki.<projectname>/`
- `<automationname>.doc/`

Names inside these containers (automation names, topic names, file names)
follow project-internal convention — no imposition.

### F6. `wikisys.<projectname>/` internals → **mirror Codex underscore folders.**

`wiki.codex/` already has `_scripts/`, `_config/`, `_canon/`, `_context/`,
`_decisions/`, `_sources/raw/`. The new `wikisys.<projectname>/` is the
**refactored extraction** of these system folders out of `wiki.codex/`
into a separate container, leaving `wiki.codex/` (renamed `wiki.<name>/`)
as content-only.

```
Biz.Automation/wikisys.<projectname>/
    _scripts/       # build/extract/audit scripts (aviation's build_wiki/ goes here)
    _templates/     # markdown/page/topic templates
    _config/        # extractor configs, keywords.yaml, etc.
    _canon/         # source-of-truth lists, verified claims, glossaries
    _context/       # OPTIONAL — context rules, ingest/lint procedures (Codex pattern)
    _decisions/     # OPTIONAL — decision log, ingest-log (Codex pattern)
```

`_context/` and `_decisions/` are Codex-pattern optionals; only
EMCC.Library uses them today. Other projects add as needed.

### F7 / F8. `raw/` and `ideas/` location → **under `wiki.<name>/git/`** (see F10).

After F10's public/private split, both `raw/` and `ideas/` live under
the public side: `wiki.<projectname>/git/raw/` and
`wiki.<projectname>/git/ideas/`. Operator's simpler names (vs Codex's
`_sources/raw/`, `_brain_dump/`) are kept — the Codex underscore names
stay inside `wikisys.<name>/` (system layer).

### F9. `<automationname>.doc/` → **naming-only contract; auto-discovery via wikisys script later.**

Pairing convention:

- `Biz.Automation/<automationname>/` — the automation (scripts, configs).
- `wiki.<projectname>/git/<automationname>.doc/` — paired docs.

The `.doc` suffix is the discovery signal. A `wikisys/_scripts/audit_doc_pairing.py`
can warn on unpaired automations — Codex v1.1 nice-to-have, not required
for the folder convention to work.

### F10. Wiki public/private split → **`wiki.<name>/git/` (public) + `wiki.<name>/local/` (private).**

Operator's round-two request. Implements per-wiki zoning analogous to
eddyandwolff's project-root `git/` vs `Local/` zoning, but at finer
granularity.

```
wiki.<projectname>/
    local/                          # private; gitignored
        <topicname>/                # confidential topic folders
        <automationname>.doc/       # OPTIONAL — confidential automation docs
    git/                            # public; committed to GitHub
        raw/                        # source files (PDFs, transcripts)
        ideas/                      # brainstorming, unfiled notes
        <topicname>/                # public topic folders
        <automationname>.doc/       # automation docs (paired with Biz.Automation/<name>/)
```

**Casing decision:** both `local/` and `git/` are lowercase. Operator's
draft wrote `Git.` (capital G, trailing period) but the period reads as
punctuation, and lowercase matches eddyandwolff's existing project-root
`git/` zone naming. Lowercase across both for symmetry.

**Gitignore mechanics:** `.gitignore` at project root excludes
`wiki.*/local/`. Bootstrap emits the rule.

**Coexistence with project-root zoning (eddyandwolff case):** when a
project also has project-root `Local/` (for non-wiki confidential files
— corporate, finance, bank statements), both forms coexist:

- Project-root `Local/` — non-wiki confidential (legal, financial, contracts)
- `wiki.<name>/local/` — confidential wiki pages (internal-only ops notes)

Both are gitignored; they're at different scopes.

### F11. `/assets/` root folder → **OPTIONAL root folder, single tree, gitignore heavy patterns.**

Operator's round-two addition. Holds logos, branding guidelines, photos,
videos, generated assets, design files.

```
assets/
    logos/              # SVG/PNG logos, favicons
    brand/              # brand-guidelines.md, color palette, fonts
    photos/             # photography
    videos/             # video files (typically gitignored — see below)
    designs/            # mockups, Figma exports, PSDs
    generated/          # AI-generated images, derived assets
```

**Subfolder names are project-internal convention** — operator can use
whatever suits each project (eddyandwolff's `brand_assets/` becomes
`assets/brand/`; isommelier's `assets/Sammie/` becomes `assets/photos/Sammie/`
or stays case-by-case).

**Gitignore guidance** (bootstrap emits suggestions):

```
# Heavy assets — by extension
assets/**/*.mp4
assets/**/*.mov
assets/**/*.psd
# Optional: gitignore everything under photos/ and videos/ entirely
# assets/photos/
# assets/videos/
```

**Public/private split for assets:** NOT a separate `assets/git/` +
`assets/local/`. Instead:

- Public, small (logos, brand guidelines, icons): `assets/`
- Private or heavy: gitignored within `assets/`, OR placed under
  `wiki.<name>/local/assets/` for confidential design work, OR placed
  under project-root `Local/09_Assets_Heavy/` (eddyandwolff-style).

Spec doesn't impose; project picks based on size + sensitivity.

### F12. `/website/` root folder → **OPTIONAL root folder for projects whose primary deliverable is a website.**

Operator's round-two addition. eddyandwolff already has `git/website/`
(Squarespace local clone + careers HTML + content drafts).

```
website/
    <stack>/            # e.g. squarespace/, nextjs/, static-html/
    drafts/             # pre-publish content drafts (markdown)
    content_standards.md
    README-<page>.md    # per-page setup notes if needed
```

**Subfolder names project-internal** — eddyandwolff uses `E+W Website/`
for the Squarespace clone; isommelier would use `mvp/` for the Next.js
app.

**`website/` vs `<product-code-root>/` distinction:**

| If the primary public output is… | Use folder |
|---|---|
| A website (Squarespace, Next.js site, static HTML, WordPress) | `website/` |
| A mobile app (Flutter, React Native) | `<product-code-root>/` (e.g. `lib/` for Flutter) |
| A library / CLI / package | `<product-code-root>/` (e.g. `src/`, `build_wiki/`, etc.) |
| A protocol spec module (EMCC.DFDU pattern) | No code root — use `wiki.<name>/git/` for the spec docs + `Biz.Automation/wikisys.<name>/_scripts/` for runtime |

For isommelier — the Next.js app IS the website, so `mvp/` → `website/`
on migration (operator's call; both names work).

For tat_app — the Flutter app is not a website; keep `lib/` and platform
folders as `<product-code-root>/`. No `website/` folder.

Both `website/` and `<product-code-root>/` are **out-of-frame** (the
portfolio frame wraps around them, never relocates them).

---

# (a) Canonical Structure Spec

## Tree

```
<projectname>/
│
├── 0-Inbox/                          # RECOMMENDED — files awaiting Librarian sort
│
├── Biz.Automation/                   # OPTIONAL — present when project has automations
│   ├── wikisys.<projectname>/        # REQUIRED if Biz.Automation/ exists
│   │   ├── _scripts/                 # build/extract/audit scripts
│   │   ├── _templates/               # markdown/page templates
│   │   ├── _config/                  # extractor configs, keywords, etc.
│   │   ├── _canon/                   # source-of-truth lists, glossaries
│   │   ├── _context/                 # OPTIONAL — context rules (Codex pattern)
│   │   └── _decisions/               # OPTIONAL — decision log (Codex pattern)
│   └── <automationname>/             # one folder per automation
│
├── wiki.<projectname>/                # OPTIONAL — present when project has wiki content
│   ├── local/                        # private; gitignored
│   │   ├── <topicname>/              # confidential topics
│   │   └── <automationname>.doc/     # OPTIONAL — confidential automation docs
│   └── git/                          # public; committed
│       ├── raw/                      # source files (PDFs, transcripts)
│       ├── ideas/                    # brainstorming
│       ├── <topicname>/              # public topics
│       └── <automationname>.doc/     # automation docs (paired with Biz.Automation/<name>/)
│
├── tasks/                            # REQUIRED — workflow tracking
│   ├── todo.md                       # active work
│   ├── sessions.md                   # dated session log, newest at top
│   ├── lessons.md                    # extracted rules / lessons learned
│   └── archive.md                    # completed-work archive (file OR folder)
│
├── assets/                           # OPTIONAL — logos, brand, photos, videos, designs
│   ├── logos/
│   ├── brand/
│   ├── photos/
│   ├── videos/
│   ├── designs/
│   └── generated/
│
├── website/                          # OPTIONAL — public-website code/content
│   └── <stack>/                      # e.g. squarespace/, nextjs/, static-html/
│
├── <product-code-root>/              # OPTIONAL — non-website product code
│                                     # e.g. lib/ (Flutter), build_wiki/ (Python pkg),
│                                     # scripts/ (CLI). Multiple roots allowed.
│
├── .claude/                          # OPTIONAL — Claude Code config (workspace projects)
│   ├── settings.json
│   ├── skills/
│   └── personas/                     # OPTIONAL
│
├── Local/                            # OPTIONAL — project-root private zone (eddyandwolff pattern)
│                                     # Never committed; never readable by Claude.
│                                     # Use for legal/financial/corporate non-wiki files.
│
├── Index.md                          # RECOMMENDED — file-map / routing table
├── CLAUDE.md                         # REQUIRED — rules, persona, memory architecture
├── Cheatsheet.md                     # RECOMMENDED — quick reference
└── .gitignore                        # REQUIRED
```

## Per-folder purpose statements

| Folder / file | Purpose |
|---|---|
| `0-Inbox/` | Drop zone. Librarian sorts into `wiki.<name>/git/` topics or `tasks/`. Empty after each pass. |
| `Biz.Automation/` | All project automations. Container only; never holds files at its root. |
| `Biz.Automation/wikisys.<projectname>/` | Wiki-system engine. Scripts, templates, configs, canon for `wiki.<projectname>/`. Mirrors Codex's underscore folders. |
| `Biz.Automation/<automationname>/` | One folder per automation. Project-internal naming free (Pascal_Case in eddyandwolff, lower in others). |
| `wiki.<projectname>/local/` | Private wiki content. Gitignored. For confidential pages, internal-only ops notes, draft material with sensitive content. |
| `wiki.<projectname>/git/` | Public wiki content. Committed. Default destination for all knowledge content. |
| `wiki.<projectname>/git/raw/` | Source materials (PDFs, transcripts, exports). Public OK by default; move to `local/raw/` if confidential. |
| `wiki.<projectname>/git/ideas/` | Brainstorming, unfiled rough notes. |
| `wiki.<projectname>/git/<topicname>/` | One folder per topic. Naming free (e.g. `FCOM/` for aviation manuals, `marketing/` for business). |
| `wiki.<projectname>/git/<automationname>.doc/` | Paired docs for `Biz.Automation/<automationname>/`. `.doc` suffix is the pairing contract. |
| `tasks/todo.md` | Active work, goal-driven format. |
| `tasks/sessions.md` | Dated session log; newest at top; ✓/Δ/!/Next markers. |
| `tasks/lessons.md` | Rules extracted from bugs and reviews. |
| `tasks/archive.md` | Completed work. File by default; may upgrade to `archive/` folder when archive grows large (>~50KB). |
| `assets/` | Logos, brand, photos, videos, design files, generated assets. Subfolders project-internal. Heavy/sensitive files gitignored per `.gitignore` rules. |
| `website/` | Public-website code/content. Stack-specific subfolders. Out of portfolio frame. |
| `<product-code-root>/` | Non-website product code (Flutter `lib/`, Python package, CLI). Out of frame. Multiple roots allowed. |
| `.claude/` | Claude Code's auto-loaded directory. Settings, skills, personas. Project root only. |
| `Local/` | Project-root private zone. eddyandwolff pattern. For non-wiki confidential files (corporate, financial, contracts). Never committed, never readable by Claude. |
| `Index.md` | File-map / routing table. Markdown table. |
| `CLAUDE.md` | Operating rules, hard constraints, persona, memory architecture. |
| `Cheatsheet.md` | Quick reference for the operator. |
| `.gitignore` | Excludes secrets, build artifacts, OS files, `wiki.*/local/`, optionally `Local/`, optionally heavy `assets/` patterns. |

## Variance allowance (required / recommended / optional)

| Element | Status | Variance permitted |
|---|---|---|
| `CLAUDE.md` (root) | **REQUIRED** | None on existence; content project-specific. |
| `.gitignore` (root) | **REQUIRED** | None on existence; must exclude `wiki.*/local/` if `wiki.*/` exists. |
| `tasks/` w/ `todo.md`/`sessions.md`/`lessons.md`/`archive.md` | **REQUIRED** | **Lowercase filenames** (matches EMCC/DFDU/isommelier/tat_app). `archive.md` may upgrade to `archive/` folder when >50KB. |
| `Index.md` (root) | **RECOMMENDED** | May be embedded as a top section in CLAUDE.md (matches tat_app/isommelier). Bootstrap emits separate; projects may collapse. `PROJECT_INDEX.md` and `INDEX.md` (all-caps) are migration targets → rename to `Index.md`. |
| `Cheatsheet.md` (root) | **RECOMMENDED** | May be omitted for thin projects. Casing must match `CLAUDE.md`/`Index.md` (mixed case, capital first letter). |
| `0-Inbox/` (root) | **RECOMMENDED** | Capital I, hyphen, zero-prefix mandatory. `0. Inbox`, `_inbox`, `inbox/` rejected → migration targets. |
| `.claude/` (root) | **OPTIONAL** | Must be at project root if present. Bootstrap does NOT create. Workspace projects (tat_app, isommelier) have it; spec/docs modules (EMCC.Library) usually don't. |
| `Biz.Automation/` | **OPTIONAL** | Omit if no automations. |
| `Biz.Automation/wikisys.<projectname>/` | **REQUIRED if `Biz.Automation/` exists** | Underscore subfolders canonical; project may add additional `_*` siblings (`_context/`, `_decisions/` follow Codex). |
| `wiki.<projectname>/` | **OPTIONAL** | Omit if pure code project with no docs. Strict `wiki.<projectname>/` naming **with one allowed variance**: subject-named wikis (`wiki.<subject>/`) permitted when the project name is a role/container and the wiki content is subject-specific. Examples: `wiki.etihad/` inside `aviation/`; `wiki.codex/` inside `EMCC.Library/`. Stronger default: `wiki.<projectname>/` matching the project folder. |
| `wiki.<name>/git/` + `wiki.<name>/local/` | **REQUIRED if `wiki.<name>/` exists** | Both subfolders mandatory once the wiki exists. `local/` may be empty (`.gitkeep`). |
| `wiki.<name>/git/raw/` and `/ideas/` | RECOMMENDED if `wiki.<name>/git/` exists | May be empty / `.gitkeep`. |
| `assets/` (root) | OPTIONAL | Subfolders project-internal. Add to project when first brand/photo lands. |
| `website/` (root) | OPTIONAL | Only when project ships a public website. Excludes mobile apps and CLIs. |
| `<product-code-root>/` | OPTIONAL | Out of frame. Code projects keep language-native layout untouched. Multiple roots allowed. |
| `Local/` (root) | OPTIONAL | eddyandwolff pattern. Project-root private zone, never committed. Use for non-wiki confidential files. Coexists with `wiki.*/local/`. |
| Dot-separated frame containers (`Biz.Automation`, `wikisys.*`, `wiki.*`, `*.doc`) | Convention **mandatory** for these four | Internal names project-free. |

## EMCC modules — how the spec applies

EMCC modules are NOT consumer projects, but the operator's scope
expansion requires they fit the same frame. They fit naturally with two
observations:

1. **The "wiki" of a spec module IS its protocol documentation.** DFDU's
   `documents/lattice/` becomes `wiki.dfdu/git/lattice/` (or
   `wiki.lattice/git/`). Library's `wiki.codex/` is already there;
   migrates to `wiki.library/git/<codex topics>/` (or keeps the
   subject-named `wiki.codex/` under the variance allowance).
2. **Module-runtime code (`scripts/`, `schemas/`, `personas/`, `tests/`)
   is `<product-code-root>/`-equivalent** — out of frame. EMCC.DFDU
   keeps `scripts/`, `schemas/`, `tests/` exactly where they are.
   `personas/` either stays as code-adjacent OR moves under
   `.claude/personas/` if the module starts running Claude Code sessions
   in its own root.

EMCC's `module.json`, `TIERS.md`, `MIGRATION-ISSUES.md`,
`SOURCE-HISTORY.md` — module-specific files at root. They're allowed as
project-specific root files (the spec doesn't ban additional root files;
it only requires CLAUDE.md and .gitignore).

---

# (b) Migration Paths per Existing Project

Each project gets a concrete punchlist. None destructive; every original
file is moved, not deleted.

## tat_app — Yes-with-light-adaptation

1. Rename `Tasks/` → `tasks/`.
2. Task files already lowercase (`todo.md`/`sessions.md`/`lessons.md`) —
   no rename needed. Promote `Tasks/archive/` folder to `tasks/archive/`
   (variance form retained, already in use).
3. Add `tasks/archive.md` as a stub IF current archive folder is empty;
   otherwise keep folder form.
4. Create `0-Inbox/.gitkeep`.
5. Create `Biz.Automation/wikisys.tat_app/{_scripts,_templates,_config,_canon}/.gitkeep`.
   Existing `.claude/skills/` (verify-flutter, go) STAY at `.claude/skills/`
   (workspace tooling, not portfolio automations).
6. Create `wiki.tat_app/git/{raw,ideas}/`. Move `docs/grok/*` →
   `wiki.tat_app/git/grok.doc/` (treating Grok integration as the
   AI-automation pairing). Alternative: keep `docs/grok/` as
   out-of-frame product docs — both defensible.
7. Create `wiki.tat_app/local/.gitkeep`.
8. Add `wiki.*/local/` to `.gitignore`.
9. Optionally extract ROOT_INDEX from CLAUDE.md into separate `Index.md`
   (variance permits embedded — recommend keep embedded; CLAUDE.md is
   battle-tested).
10. Add root `Cheatsheet.md`.
11. `lib/`, `android/`, `ios/`, etc., stay as `<product-code-root>/`
    (multi-root, all out-of-frame).
12. No `website/` folder (tat_app is a mobile app).
13. No `assets/` folder unless brand assets exist; check
    `lib/images/` — Flutter image assets stay code-adjacent.

## aviation — Yes-with-significant-adaptation

Project name (`aviation`) is the role; content is Etihad A320. Wiki
naming uses the subject-named variance: `wiki.etihad/`.

1. Move `etihad-wiki/build_wiki/` (Python pkg) →
   `Biz.Automation/wikisys.aviation/_scripts/`.
2. Move `etihad-wiki/build_wiki.py`, `check_pdf.py`,
   `requirements.txt` → `Biz.Automation/wikisys.aviation/_scripts/`.
3. Move `etihad-wiki/keywords.yaml` →
   `Biz.Automation/wikisys.aviation/_config/keywords.yaml`.
4. Move `etihad-wiki/output/` contents → `wiki.etihad/git/`. Manual
   codes (`FCOM/`, `FCTM/`, `OMA/`, `QRH/`, `EEP/`, `_assets/`) become
   topic folders directly under `wiki.etihad/git/`.
5. Move `etihad-wiki/output/CLAUDE.md` → keep at
   `wiki.etihad/git/CLAUDE.md` (wiki-side AI-lookup nav). Create root
   `CLAUDE.md` for project-level operating rules.
6. Move `etihad-wiki/.claude/` → root `.claude/`.
7. Move `etihad-wiki/README.md` → `Biz.Automation/wikisys.aviation/README.md`
   (tool-specific docs stay with the tool).
8. Create `0-Inbox/`, `tasks/todo.md`, `tasks/sessions.md`,
   `tasks/lessons.md`, `tasks/archive.md`.
9. Create root `Index.md`, root `Cheatsheet.md`.
10. Move PDF sources (currently gitignored) → `wiki.etihad/git/raw/` if
    public-OK, OR `wiki.etihad/local/raw/` if Etihad licensing requires.
    **Defer to operator** — likely `local/raw/` given source licensing.
11. Create `wiki.etihad/git/ideas/`, `wiki.etihad/local/.gitkeep`.
12. Create paired `wiki.etihad/git/build_wiki.doc/` (extracted from
    `etihad-wiki/README.md`).
13. Update `.gitignore` to include `wiki.*/local/`.
14. Delete the now-empty `etihad-wiki/` shell.
15. Move root `test-edit.md` → `0-Inbox/`.
16. No `website/`, no `assets/` (aviation is a Python CLI + content
    project).

## aviation-career — Yes-clean (minimal frame only)

1. Create `tasks/{todo,sessions,lessons,archive}.md`.
2. Create root `CLAUDE.md` (minimal — describe as personal braindump).
3. Create root `Index.md`.
4. Create `0-Inbox/.gitkeep`.
5. Move `competencies/` → `wiki.aviation-career/git/competencies/`.
6. Create `wiki.aviation-career/local/.gitkeep`.
7. Add `wiki.*/local/` to `.gitignore`.
8. **Skip** `Biz.Automation/`, `wikisys.*/`, `assets/`, `website/`,
   `Cheatsheet.md` (nothing to put in them).

## eddyandwolff — Yes-with-significant-adaptation (zoning preserved)

Project-root zoning (`git/` public vs `Local/` private) preserved as
variance allowance. Canonical frame nests inside `git/`.

1. Keep `git/` as the public zone wrapper. Canonical frame inside:
   `git/0-Inbox/`, `git/tasks/`, `git/Biz.Automation/`,
   `git/wiki.eddyandwolff/`, `git/assets/`, `git/website/`,
   `git/CLAUDE.md`, `git/Index.md`, `git/Cheatsheet.md`.
2. Move `git/automation/{Finance_Ops_Automation,Receipt_Processing,Sync_Buildspec,Inbox_Consolidation}/`
   → `git/Biz.Automation/`. Pascal_Case naming preserved.
3. Move `git/automation/_future/{Lightspeed,Deputy,Stripe,Xero,Airwallex}_Sync/`,
   `_future/GHL_Integration/` → `git/Biz.Automation/_future/`.
4. Create `git/Biz.Automation/wikisys.eddyandwolff/{_scripts,_templates,_config,_canon}/`.
   Cross-cutting infrastructure scripts migrate here; per-automation
   scripts stay nested under `git/Biz.Automation/<name>/scripts/`.
5. Move `git/Biz_Marketing.md`, `Biz_Operations.md`, `Biz_Automation.md`,
   `Biz_Finance.md` → `git/wiki.eddyandwolff/git/` as topic-umbrella
   files. (Yes: `git/wiki.eddyandwolff/git/` — the outer `git/` is the
   project zone wrapper, the inner `git/` is the wiki public-side.
   Awkward, but the doubled name is correct per the spec.)
6. Move `git/reference/`, `git/operations/recipes/`, `git/operations/checklists/`,
   `git/marketing/Digital_Presence/` → `git/wiki.eddyandwolff/git/<topic>/`
   (topic folders under wiki public-side).
7. Move `git/brand_assets/` → `git/assets/brand/` (renaming subfolder
   under the canonical `assets/` root). Logos go to `git/assets/logos/`.
8. Move `git/website/E+W Website/`, `git/website/drafts/`,
   `git/website/README-CAREERS.md`, `git/website/content_standards.md`
   → `git/website/` (already correct; keep structure).
9. Pair each `git/Biz.Automation/<name>/` with
   `git/wiki.eddyandwolff/git/<name>.doc/` for human docs.
10. Rename `git/JP_CHEATSHEET.md` → `git/Cheatsheet.md`.
11. Rename `git/INDEX.md` → `git/Index.md` (case-only rename: 2-step
    via tmp name on Linux).
12. Create `git/tasks/todo.md`/`sessions.md`/`lessons.md`/`archive.md`.
    Existing `git/tasks/` content gets distributed by Librarian.
13. Create `git/0-Inbox/.gitkeep`.
14. `Grok/` and `.obsidian/` at project root: OUT OF FRAME. Operator's
    parallel Obsidian vault. Leave them.
15. `Local/` (project-root private zone): UNTOUCHED. `.gitignore`
    continues to exclude. This is the canonical example of the
    project-root `Local/` variance.
16. Create `git/wiki.eddyandwolff/local/.gitkeep` if any wiki content
    needs to be confidential at the wiki level (separate from
    project-root `Local/`).

## isommelier — Yes-with-significant-adaptation (code + frame coexist)

1. `mvp/` → `website/mvp/` (Next.js app is the public website at
   isommelier.co). Alternative: rename top folder to `website/` and
   move Next.js root files up — operator's call.
2. Task files already lowercase. Add `tasks/archive.md` (currently
   absent).
3. `.claude/` stays at root.
4. `nexus/lattice/` → `Biz.Automation/nexus/` (the Nexus Lattice
   framework — Architect/Craftsman/Auditor agents).
5. Create `Biz.Automation/wikisys.isommelier/{_scripts,_templates,_config,_canon}/`.
   `setup-claude-plugin.ps1` (root) → `Biz.Automation/wikisys.isommelier/_scripts/`.
6. Database/seed scripts in current root `scripts/` → stay at root as
   code-adjacent (database seeds belong to mvp). Optionally move to
   `website/mvp/scripts/`.
7. `docs/` → `wiki.isommelier/git/`. The 15+ spec files in `docs/`
   become topic folders or files under `wiki.isommelier/git/`.
   `docs/Archive/` → `wiki.isommelier/git/_archive/` (or distribute
   into topic archives).
8. `specs/` → `wiki.isommelier/git/specs/`. `research/` →
   `wiki.isommelier/git/research/`. `types/` stays at root
   (TypeScript types imported by `mvp/`).
9. `business/` → `wiki.isommelier/local/business/` if strategy PDFs are
   confidential, else `wiki.isommelier/git/business/`. Likely
   confidential (blue-ocean strategy, org structure) → `local/`.
10. `assets/` at root: keep, add canonical subfolders (`assets/logos/`,
    `assets/photos/`, `assets/brand/`). Existing `assets/Assets/Sammie/`,
    `assets/E+W Assets/` get reorganized — Sammie photos →
    `assets/photos/sammie/`; brand assets → `assets/brand/`.
11. Root files: `BUGS.md` → `tasks/lessons.md` (append) or
    `wiki.isommelier/git/bugs/`. `20260419_Isommelier_Night.md` →
    `wiki.isommelier/git/sessions/`. `iSommelier_Workflow_Cheatsheet_v2.txt`
    → `Cheatsheet.md` (rename + convert .txt → .md; version suffix
    dropped, git history is the version log).
12. Create root `Index.md` (extract from CLAUDE.md or embed — variance
    permits).
13. Create `0-Inbox/.gitkeep`.
14. Add `wiki.*/local/` to `.gitignore`.

## EMCC — Yes-with-significant-adaptation

EMCC is the orchestration root; applies the spec but with
module-specific files preserved at root.

1. `0-Inbox/` already correct (hyphen form).
2. `tasks/` already correct. Existing `tasks/self-build-log.jsonl`
   stays — it's a project-specific log file, not part of the canonical
   four. Add `tasks/lessons.md`, `tasks/archive.md` if absent.
3. `scripts/` → `Biz.Automation/wikisys.emcc/_scripts/`
   (`auto_scan.py`, `memory_sync.py`, `self_audit.py`,
   `task_processor.py`, `emcc_bootstrap.py`). These are EMCC's
   self-orchestration automations.
4. `templates/` → `Biz.Automation/wikisys.emcc/_templates/` (consumer-project
   + department-starter templates).
5. `_blueprints/` → `wiki.emcc/git/_blueprints/` (portfolio scan
   summaries, mined patterns, verified claims register — these are
   wiki-content-adjacent). Alternative: `Biz.Automation/wikisys.emcc/_canon/`
   for verified-claims since it's a source-of-truth list.
6. `Documentation/` → `wiki.emcc/git/documentation/` (operator
   guides, vision specs).
7. `ai-trinity-chatroom/` → `wiki.emcc/git/_archive/ai-trinity-chatroom/`
   (superseded pre-Lattice scaffolding, marked as archive).
8. `orchestrator-mockup.html` → `website/orchestrator-mockup/` if it
   becomes the Command Center UI deliverable. Currently a single
   prototype file — could stay at root or move into
   `wiki.emcc/git/command-center/`.
9. Root files `EMCC.md`, `EMCC-MEMORY.md`, `FRAMEWORK.md`,
   `BUILD_INSTRUCTIONS.md`, `ROADMAP.md`, `ENTERPRISE_AI_AGENT_PLATFORM_ROADMAP.md`
   → either keep at root (module-specific root files, allowed) OR
   move into `wiki.emcc/git/` as topic files (`framework.md`,
   `roadmap.md`). Recommend: move `*-MEMORY.md` and `*-ROADMAP.md`
   into the wiki; keep `EMCC.md`, `FRAMEWORK.md`, `BUILD_INSTRUCTIONS.md`
   at root as bootstrap-required reads.
10. Rename `PROJECT_INDEX.md` → `Index.md` (case rename via tmp).
11. Add `Cheatsheet.md` at root.
12. No `.claude/` (EMCC is not yet a workspace project; add when
    Director/Migrator agents have Claude Code skills).
13. No `assets/` initially (no branding yet); add when EMCC ships its UI.
14. `website/` reserved for the Command Center UI when it lands
    (`_blueprints/command-center/` is the current prototype location).

## EMCC.DFDU — Yes-with-light-adaptation

1. `0-Inbox/` already correct.
2. `tasks/` already correct (todo/sessions/lessons/archive/architect-notes/
   spec-readiness-tracker + plans subdir). Canonical four preserved;
   extras allowed as project-specific.
3. `documents/lattice/` (12 canonical docs) → `wiki.dfdu/git/lattice/`.
   Numbered-doc naming (`00-README.md` through `13-TELEGRAM-INTEGRATION.md`)
   preserved.
4. `documents/lattice-2.0-legacy/` → `wiki.dfdu/git/_archive/lattice-2.0-legacy/`.
5. `documents/argot/` → `wiki.dfdu/git/argot/`.
6. `scripts/` → `<product-code-root>` (out of frame — keep at root).
   These are runtime infrastructure (`lattice-bridge.py`,
   `lattice_session_start.py`), not portfolio automations.
   **Alternative:** rename to `Biz.Automation/dfdu-runtime/` if the
   operator wants them under the canonical automation frame —
   defensible either way. Recommend `<product-code-root>/` (stay at
   root) because they're imported as Python modules.
7. `schemas/` → stay at root (code-adjacent — JSON Schema
   definitions consumed by `scripts/`).
8. `personas/` → `wiki.dfdu/git/personas/` (Auditor persona is a
   doc/template, not runtime code).
9. `tests/` → stay at root (pytest convention).
10. Root files `module.json`, `TIERS.md`, `MIGRATION-ISSUES.md`,
    `SOURCE-HISTORY.md`, `CLAUDE.md`, `README.md` → keep at root.
    `module.json` is module-required.
11. Add root `Index.md`, `Cheatsheet.md`.
12. No `Biz.Automation/wikisys.dfdu/` initially — DFDU is itself an
    automation/protocol module; it doesn't HOST automations for its
    own wiki. If/when it adds wiki-build scripts, add `wikisys.dfdu/`.
13. No `.claude/` (not a workspace project).
14. `.lattice/` (runtime, gitignored) stays — module-specific runtime.

## EMCC.Library — Yes-with-significant-adaptation (Session 1 already shipped half; S002/v1.1 handles the rest)

EMCC.Library hosts both the **Codex MODULE source files** (extracted from
project-codex in master-plan Step 3 / Session 1, commits `094e8a3 →
ab94fc7` on branch `claude/lattice-3-production-check-Rdkfu`, pushed
2026-05-27) AND the **`wiki.codex/` dogfood** (Codex documenting Codex —
the prior-art reference from which this whole spec was generalized).

Two parallel underscore-folder hierarchies exist post-Session-1:
Library-root-level Codex source (e.g. `_scripts/`, `_template/`,
`_config/`, `Sources/`) AND wiki.codex/-internal dogfood (e.g.
`wiki.codex/_canon/`, `_config/`, `_context/`, `_decisions/`,
`_brain_dump/`). This punchlist resolves both into the canonical layout.

`wiki.codex/` keeps the subject-named variance (project=Library,
wiki=codex). All other re-layout follows the canonical spec.

### Done in Session 1 (DO NOT REDO)

- ✅ Rename `0. Inbox/` → `0-Inbox/` (commit `094e8a3`).
- ✅ Create `tasks/{todo,sessions,lessons,archive}.md` (commit `094e8a3`).
- ✅ Create root `CLAUDE.md`, `module.json`, `SOURCE-HISTORY.md`,
     `MIGRATION-ISSUES.md`, `.github/workflows/test.yml`,
     `.claude/personas/CLAUDE.{auditor,librarian}.md` (commit `814d765`).
- ✅ Move Codex MODULE source files from project-codex into Library root
     (commit `dc1e7a9`, 148 files): `_scripts/`, `_template/`, `_config/`,
     `Sources/`, `tests/`, `documents/codex/`, root-level Codex spec docs
     (`CODEX_BUILD_SPEC_v1_3.md`, `CODEX_LIBRARIAN.md`,
     `INGEST_PROCEDURE.md`, `SEMANTIC_LINT_PROCEDURE.md`,
     `PROJECT_WIKI_BUILD_SPEC.md`, `Obsidian-Setup-Guide.md`,
     `codex-build-plan.html`, `bootstrap.py`).
- ✅ `.claude/personas/CLAUDE.librarian.md` at root (no `.claude/` nested
     under `wiki.codex/` anymore). Path preserved at `.claude/personas/`
     to keep `bootstrap.py` + `test_phase6_full_chain_e2e.py` green per
     AC8.
- ✅ Module status flipped: EMCC `templates/consumer-project/emcc.modules.json`
     `library.status` `not-ready` → `ready` (EMCC commit `b10c766`).

### S002 / Codex v1.1 — remaining work

#### Module source files at Library root → `Biz.Automation/wikisys.library/`

1. Move `_scripts/` → `Biz.Automation/wikisys.library/_scripts/`
   (27 .py: 20 root scripts + `_lib/` 7 modules + `launchers/`).
2. Move `_template/` → `Biz.Automation/wikisys.library/_template/`
   (26 templates). **Canonical singular `_template/`** to match Codex's
   existing folder name; canonical tree at lines 261–319 currently shows
   `_templates/` plural — to be amended in same edit.
3. Move `_config/` → `Biz.Automation/wikisys.library/_config/`
   (5 YAML + README).
4. Move `Sources/Raw/` → `wiki.codex/git/raw/` per F7/F8
   (operator-friendly name on content side; NOT extracted to wikisys
   side — F7/F8 resolution: `_sources/` is not in the canonical
   wikisys tree).
5. `tests/` STAYS at root as `<product-code-root>`-equivalent (matches
   DFDU's `tests/` disposition + Codex's stdlib-only pytest convention).

#### Codex spec docs at root → `wiki.codex/git/codex/`

Per the DFDU analogy (`documents/lattice/` → `wiki.dfdu/git/lattice/`),
Codex's authoritative spec docs become a topic folder under the wiki
content side.

6. Move to `wiki.codex/git/codex/`:
   - `CODEX_BUILD_SPEC_v1_3.md`
   - `CODEX_LIBRARIAN.md`
   - `INGEST_PROCEDURE.md` (note: bootstrap.py ships a copy into each
     bootstrapped wiki's `_context/INGEST_PROCEDURE.md`; the
     `wiki.codex/git/codex/` location is the canonical source that
     `wikisys.library/_context/` mirrors)
   - `SEMANTIC_LINT_PROCEDURE.md` (same dual-location as INGEST)
   - `PROJECT_WIKI_BUILD_SPEC.md`
   - `Obsidian-Setup-Guide.md`
   - `codex-build-plan.html`
7. Move `documents/codex/` contents (Codex PDF + cheatsheet +
   build-progress md) → `wiki.codex/git/codex/`.
8. `bootstrap.py` STAYS at root (entry script; matches the
   `bootstrap.py <projectname>` invocation per section c).

#### wiki.codex/ internal restructure (dogfood wiki)

9. `wiki.codex/00-Start-Here/`, `01-Architecture/`, `02-Operations/`,
   `04-Contributing/` → `wiki.codex/git/00-Start-Here/`, etc.
10. `wiki.codex/Home.md` → `wiki.codex/git/Home.md`.
11. `wiki.codex/_canon/`, `_config/`, `_context/`, `_decisions/`,
    `_scripts/` (if any), `_sources/raw/` → **system files extract to**
    `Biz.Automation/wikisys.library/_canon/`, `_config/`, `_context/`,
    `_decisions/`. Note: `wiki.codex/_config/` merges with the root-level
    `_config/` (both extract to the same destination). `_sources/raw/`
    content moves to `wiki.codex/git/raw/` per F7/F8 (NOT to
    `wikisys.library/_sources/raw/`).
12. `wiki.codex/_brain_dump/` (gitignored) → `wiki.codex/local/ideas/`.

#### Final wiki.codex/ structure

```
wiki.codex/
    local/
        ideas/                 (formerly _brain_dump/)
    git/
        Home.md
        00-Start-Here/
        01-Architecture/
        02-Operations/
        04-Contributing/
        raw/                   (formerly _sources/raw/ + Sources/Raw/)
        codex/                 (formerly root-level spec docs + documents/codex/)
            CODEX_BUILD_SPEC_v1_3.md
            CODEX_LIBRARIAN.md
            INGEST_PROCEDURE.md
            SEMANTIC_LINT_PROCEDURE.md
            PROJECT_WIKI_BUILD_SPEC.md
            Obsidian-Setup-Guide.md
            codex-build-plan.html
            Codex_Project_Documentation.pdf
            Codex_Workflow_Cheatsheet_v1.txt
            codex-build-progress.md
```

#### Final Biz.Automation/wikisys.library/ structure

```
Biz.Automation/wikisys.library/
    _scripts/              (from /_scripts/)
    _template/             (from /_template/; singular form canonical)
    _config/               (merged from /_config/ + wiki.codex/_config/)
    _canon/                (from wiki.codex/_canon/)
    _context/              (from wiki.codex/_context/; runtime-loaded by bootstrap.py + Librarian)
    _decisions/            (from wiki.codex/_decisions/)
```

#### Misc cleanup

13. Create root `Index.md` (extract ROOT_INDEX from CLAUDE.md or fresh
    authoring).
14. Create root `Cheatsheet.md`.
15. Update `.gitignore`: add `wiki.*/local/` pattern; remove existing
    `wiki.codex/_brain_dump/` rule (subsumed by `local/`). Keep existing
    `wiki.codex/_dashboards/`, `wiki.codex/_inbox/`,
    `wiki.codex/_confidential/` rules (wiki-internal artifacts unchanged
    by this restructure).
16. After restructure: `bootstrap.py /tmp/v1.1-validation-wiki` must
    continue to succeed end-to-end (Session 1's AC2 verification
    recipe). bootstrap.py's path lookups for `_template/`, `_config/`,
    `_context/`, `Sources/Raw/` may need updates to point at
    `Biz.Automation/wikisys.library/_template/` etc. — this IS a
    `bootstrap.py` code change; falls outside Session 1's AC8 (which
    forbade Codex code changes during pure extraction) but is in scope
    for v1.1 update.

### S002 dispatch consideration

The implementation session should run under Lattice 3.0 Regime B (L2+,
Auditor on-demand) — same as Session 1 — because:

- Cross-module restructure touches ~50 file moves
- Codex spec-doc placement is a Level-2+ semantic decision
- `bootstrap.py` path lookups require code changes (departs from
  Session 1's AC8 verbatim discipline)
- The 5 P0/P1 new scripts (`audit_doc_pairing.py`, `audit_gitignore.py`,
  `route_inbox.py`, `audit_assets.py`, `audit_local_split.py`) ship in
  the same session
- `CODEX_LIBRARIAN.md` + `.claude/personas/CLAUDE.librarian.md` extend
  with the 3 new operations (Inbox-Sort, Pairing-Audit,
  Cross-Project-Scan)

Acceptance criteria for S002:

- All file moves applied per items 1–12
- `bootstrap.py /tmp/v1.1-validation-wiki --full` produces the canonical
  tree exactly per section (c); all stubs land
- `bootstrap.py /tmp/v1.1-validation-wiki --minimal | --code | --website`
  also produce expected outputs
- All Session-1-relocated tests still pass post-restructure (~615 tests;
  `bootstrap.py` test fixtures may need path updates)
- 5 P0/P1 new scripts shipped in `wikisys.library/_scripts/` with tests
- `CODEX_LIBRARIAN.md` extended with 3 new operations
- Library `module.json` version bump to v1.1
- MI-10/11/12/13 (S001 deferrals in Library `MIGRATION-ISSUES.md`)
  resolved or explicitly carried to v1.2

## Mentor (planned) — Greenfield bootstrap target

No on-disk migration. `bootstrap.py mentor` generates the canonical
tree directly (see section c).

---

# (c) bootstrap.py Output Spec

## Invocation

```
bootstrap.py <projectname> [--minimal | --code | --website | --full]
```

- `<projectname>` — required. Used as folder name and as suffix for
  `wikisys.<name>/` and `wiki.<name>/`. Filesystem-safe characters only.
- `--minimal` — thin braindump (aviation-career style). Root files +
  `tasks/` + `0-Inbox/` + `wiki.<name>/git/` only.
- `--code` — product-code project (Flutter, Python pkg, CLI). Creates
  `<product-code-root>/.gitkeep` placeholder + code-aware `.gitignore`.
- `--website` — public-website project (Next.js, Squarespace). Creates
  `website/.gitkeep` placeholder + web-aware `.gitignore`.
- `--full` — default. Full canonical tree.

## Default output for `bootstrap.py mentor` (`--full`)

```
mentor/
├── 0-Inbox/.gitkeep
├── Biz.Automation/
│   ├── wikisys.mentor/
│   │   ├── _scripts/.gitkeep
│   │   ├── _templates/.gitkeep
│   │   ├── _config/.gitkeep
│   │   └── _canon/.gitkeep
│   └── .gitkeep
├── wiki.mentor/
│   ├── local/.gitkeep
│   └── git/
│       ├── raw/.gitkeep
│       └── ideas/.gitkeep
├── tasks/
│   ├── todo.md
│   ├── sessions.md
│   ├── lessons.md
│   └── archive.md
├── assets/
│   ├── logos/.gitkeep
│   ├── brand/.gitkeep
│   ├── photos/.gitkeep
│   ├── videos/.gitkeep
│   ├── designs/.gitkeep
│   └── generated/.gitkeep
├── Index.md
├── CLAUDE.md
├── Cheatsheet.md
└── .gitignore
```

## `--minimal` output

```
mentor/
├── 0-Inbox/.gitkeep
├── wiki.mentor/
│   ├── local/.gitkeep
│   └── git/.gitkeep
├── tasks/
│   ├── todo.md
│   ├── sessions.md
│   ├── lessons.md
│   └── archive.md
├── Index.md
├── CLAUDE.md
└── .gitignore
```

## `--code` adds

```
mentor/<product-code-root>/.gitkeep
```

Plus `.gitignore` additions: `node_modules/`, `__pycache__/`, `build/`,
`dist/`, `target/`, `*.egg-info/`.

## `--website` adds

```
mentor/website/.gitkeep
```

Plus `.gitignore` additions: `node_modules/`, `.next/`, `dist/`,
`build/`, `.vercel/`.

## File stubs

### `CLAUDE.md`

```markdown
# CLAUDE.md — <projectname>

[One-line description of what this project is.]

## Read order (every new conversation)

1. **`Index.md`** — file map + routing table.
2. **`tasks/todo.md`** — current sprint.
3. **`tasks/lessons.md`** — rules. Re-read before any code change.

## Hard rules

- [Project-specific non-negotiables.]
- Do not delete anything. Move to `tasks/archive.md` or `0-Inbox/`.
- Confidential content goes in `wiki.<projectname>/local/`. Public content goes in `wiki.<projectname>/git/`. Never confuse.

## Memory architecture

[R_* drawer pattern. Copy from tat_app or isommelier as starting point.]
```

### `Index.md`

```markdown
# INDEX

Route lookups via this file. Read BEFORE searching the project.

## Top-level

| Folder / file | Purpose |
|---|---|
| `0-Inbox/` | Files awaiting Librarian sort. |
| `Biz.Automation/` | Project automations. |
| `Biz.Automation/wikisys.<projectname>/` | Wiki-system engine. |
| `wiki.<projectname>/local/` | Confidential wiki content (gitignored). |
| `wiki.<projectname>/git/` | Public wiki content. |
| `tasks/` | Workflow tracking. |
| `assets/` | Logos, brand, photos, videos, designs. |
| `Index.md` | This file. |
| `CLAUDE.md` | Operating rules + memory. |
| `Cheatsheet.md` | Quick reference. |

## Wiki topics

[One row per topic as the wiki grows. Note local vs git per row.]

## Automations

[One row per automation. Pair each with its `<name>.doc/` folder under `wiki.<projectname>/git/`.]
```

### `tasks/todo.md`

```markdown
# Todo

## Active

- [ ] Bootstrap'd <date>. Replace with actual work.

## Backlog

(empty)
```

### `tasks/sessions.md`

```markdown
# Sessions

Newest at top. Markers: ✓ verified | Δ changed | ! blocker | Next pointer.

## <date> — Bootstrap

- ✓ Project initialized via `bootstrap.py <projectname>`.
- Next: define hard rules in CLAUDE.md, populate Index.md.
```

### `tasks/lessons.md`

```markdown
# Lessons

Rules extracted from work in this project. Re-read before any code change.

(empty — add rules as learned)
```

### `tasks/archive.md`

```markdown
# Archive

Completed work. Newest at top.

(empty)
```

### `Cheatsheet.md`

```markdown
# Cheatsheet — <projectname>

## Paths

- Repo: [local path]
- GitHub: [url]

## Commands

[Add as automations land.]
```

### `.gitignore` (default `--full`)

```
# OS
.DS_Store
Thumbs.db

# Secrets
.env
.env.local
*.key
*.pem

# Editor
.vscode/
.idea/

# Wiki — private zone (gitignored)
wiki.*/local/

# Project-root private zone (uncomment if using eddyandwolff-style zoning)
# Local/

# Assets — heavy patterns (uncomment as needed)
# assets/**/*.mp4
# assets/**/*.mov
# assets/**/*.psd
# assets/photos/
# assets/videos/
```

## Idempotency + safety rules

1. **Refuse to overwrite.** If `<projectname>/` exists and is non-empty,
   exit with error. `--force` required to override.
2. **Refuse outside cwd.** Only writes into a child of the current
   directory.
3. **No `git init`.** Tree only. First commit is operator's call.
4. **No `.claude/` creation.** Operator wires Claude Code per project.
5. **No network calls.** Offline.

## Post-bootstrap checklist (printed by bootstrap.py)

```
Created <projectname>/ with the canonical portfolio frame.

Next steps:
  1. cd <projectname>
  2. Edit CLAUDE.md: one-line description + hard rules.
  3. Edit Index.md: rows for any non-stub folders you add.
  4. Initialize Claude Code: copy a sibling project's .claude/ or run claude init.
  5. git init && git add -A && git commit -m "bootstrap"
  6. First real session: populate tasks/todo.md with the actual first task.

Notes:
  - wiki.<projectname>/local/ is gitignored. Use it for confidential content.
  - assets/ has heavy-file patterns commented in .gitignore — uncomment as needed.
  - If your project ships a public website, use the --website flag (or add website/ manually).
  - If your project ships product code (mobile app, CLI, library), use --code (or add <product-code-root>/ manually).
```

---

# (d) Librarian Agent + Codex Scripts — Design

The operator's round-three follow-on: given the new folder spec, design
the Library module's Librarian AI agent and the deterministic scripts
that support it. **Most of this work is already done in prior art** —
Codex already ships 21 scripts and a comprehensive Librarian persona
(`CODEX_LIBRARIAN.md` + `.claude/personas/CLAUDE.librarian.md`). The
remaining work is (i) mapping the existing system onto the new folder
names, (ii) identifying gaps the new structure introduces, and
(iii) articulating the script-vs-agent split with concrete examples.

## Prior art (what's already shipped)

**21 deterministic scripts** at `wiki.codex/_scripts/` (will move to
`Biz.Automation/wikisys.library/_scripts/` per migration):

| Category | Scripts |
|---|---|
| Build / generate | `build_topic_index.py`, `build_completion_dashboard.py`, `build_canon_drift_report.py`, `cross_link_topics.py`, `update_dashboards.py` |
| Validate / lint | `validate_terminology.py`, `validate_canon_integrity.py`, `validate_reveal_conceit.py`, `validate_topic_registry.py`, `check_framework_briefing_sync.py`, `check_cascade.py`, `check_canon_consistency.py`, `check_cross_refs.py`, `check_concept_coverage.py` |
| Scaffold | `scaffold_source.py`, `scaffold_brain_dump.py`, `sync_from_kit.py` |
| Analyze | `delta_source_docs.py`, `collect_open_questions.py`, `steel_thread_tracker.py` |
| Library (`_lib/`) | `doc_lint.py`, `topics.py`, `markdown.py`, `config_loader.py`, `dashboard.py`, `frontmatter.py` |

**Three canonical operations** (per `CODEX_BUILD_SPEC_v1_2.md` §4):

- **Bootstrap** (§4.1) — one-time wiki creation. Runs `bootstrap.py`.
- **Sync** (§4.2) — infrastructure refresh from Codex into a live wiki.
  Runs `sync_from_kit.py`. Verifies precedence (some files overwrite
  verbatim; `_context/CLAUDE_CONTEXT_RULES.md` never touched).
- **Ingest** (§4.3) — most frequent. Claude-driven. Integrates new
  source documents into a wiki. Read `_inbox/<source>` → extract
  candidates → route to canon/page/mention → archive to `_sources/raw/`
  → log to `_decisions/ingest-log.md` → run `update_dashboards.py`.

Plus a **Maintenance loop** (per-trigger): scan `_dashboards/*.md`,
pick highest-priority finding, propose fix, await user direction.

**Hard rules** (verbatim from `CODEX_LIBRARIAN.md`): ingest proposes /
humans dispose, source wins over wiki, `_inbox/` ephemeral /
`_sources/raw/` permanent, frontmatter is the API, visibility direction
internal → public never reverse, halt-loud on ambiguity, paired writes
atomic, one Librarian per wiki at a time.

The Librarian persona is **fully specified**. The script suite is
**comprehensive** for single-wiki operations. The new portfolio spec
adds work above-and-beyond this baseline.

## What the new spec changes for the Librarian

The new folder structure introduces **five concepts Codex's current
implementation doesn't yet handle**:

### Change 1: Two inboxes, not one

| Layer | Existing Codex | New spec |
|---|---|---|
| Project-root inbox | (none) | `0-Inbox/` — drops anywhere in the portfolio, route to wiki, tasks, assets, website, or product code |
| Wiki-internal inbox | `wiki.codex/_inbox/` (gitignored) | (subsumed; project-root inbox feeds the wiki via Librarian sort) |

The new project-root `0-Inbox/` is **broader** than Codex's wiki-internal
`_inbox/`. A `0-Inbox/` drop might be a wiki source (route to
`wiki.<name>/git/raw/`), a task (route to `tasks/todo.md`), a brand
asset (route to `assets/logos/`), a website draft (route to
`website/drafts/`), or a code artifact (route to `<product-code-root>/`).
Librarian must classify by **destination zone**, not just by topic.

### Change 2: Local vs Git split (visibility classification at write-time)

| Layer | Existing Codex | New spec |
|---|---|---|
| Confidential | `wiki.codex/_confidential/` (single folder) | `wiki.<name>/local/` (full mirror of `git/` substructure: topics, automation docs, raw, ideas) |
| Public | (rest of wiki) | `wiki.<name>/git/` |

Codex already has `validate_reveal_conceit.py` that **validates** public
pages don't leak internal terms. The new split asks Librarian to
**decide at write-time** whether content belongs in `local/` or `git/`.
This is a stronger classifier than "is this leaking?" — it's "is this
sensitive?"

### Change 3: Automation-doc pairing contract

Every `Biz.Automation/<name>/` is expected to have a paired
`wiki.<name>/git/<name>.doc/` folder. Existing Codex doesn't have this
contract — automations and docs aren't co-named in Codex's wiki today.

### Change 4: Cross-project scope (Phase 2)

EMCC sessions log already mentions Librarian Phase 2: cross-project
inbox / index / strategic ops, mediated by EMCC. Today, Librarian is
single-wiki. Phase 2 needs an orchestration layer that runs Librarian
against multiple wikis, surfaces cross-project patterns, mines reusable
content. EMCC's `scripts/auto_scan.py` is the seed.

### Change 5: Non-wiki zones (tasks, assets, website, product code)

Codex's Librarian only owns wiki content. The new spec extends the
Librarian's surface to include sort-routing decisions for non-wiki
zones (deciding "this `0-Inbox/` drop is a task, not a wiki page") but
NOT ownership of those zones. Tasks remain operator-owned; assets stay
flat; website stays out-of-frame. Librarian's surface widens for
**triage**, not for **maintenance**.

## Script-vs-Agent split (definitive table)

The split principle: **scripts emit findings + apply mechanical
transforms; the Librarian AI agent makes judgment calls and applies
content writes that require classification.** Existing Codex follows
this principle; new spec extends it.

| Operation | Owner | Why |
|---|---|---|
| **File operations: mkdir, mv, rm, rename** | Script | Mechanical. Once destination decided, no judgment. |
| **Frontmatter parsing + emission** | Script (`_lib/frontmatter.py`) | YAML is deterministic. |
| **Frontmatter validation** (required fields present?) | Script (`validate_canon_integrity.py`) | Schema check. |
| **Index generation** (scan folders → emit markdown table) | Script (`build_topic_index.py`) | Filesystem scan + template. |
| **Cross-link block generation** (`<!-- codex:see-also -->`) | Script (`cross_link_topics.py`) | Topic-graph traversal. |
| **Dashboard generation** (status counts, drift reports) | Script (`build_completion_dashboard.py`, `update_dashboards.py`) | Aggregation. |
| **Terminology consistency check** | Script (`validate_terminology.py`) | Token matching against canon lists. |
| **Visibility-leak detection** (public page references internal term?) | Script (`validate_reveal_conceit.py`) | Pattern match. |
| **Doc-pairing audit** (every automation has a `.doc/` partner?) | Script — **NEW** (`audit_doc_pairing.py`) | Filesystem scan. Gap. |
| **Gitignore enforcement** (is `wiki.*/local/` excluded?) | Script — **NEW** (`audit_gitignore.py`) | Pattern match. Gap. |
| **Heavy-asset detection** (files in `assets/` exceeding size threshold) | Script — **NEW** (`audit_assets.py`) | File-size scan. Gap. |
| **Stale-file detection** (files untouched for N days) | Script — extend `collect_open_questions.py` | Filesystem mtime scan. |
| **Search index** (full-text or topic-tag index for fast lookup) | Script — **NEW** if needed (`build_search_index.py`) | Aggregation. Gap (low priority). |
| **Backup / snapshot** | Script — out of scope (use git) | Git is the backup. |
| **Project bootstrap** (`bootstrap.py`) | Script (defined in section c above) | Mechanical scaffolding. |
| **Wiki Sync** (refresh wiki infrastructure from Codex canonical) | Script (`sync_from_kit.py`) | Verbatim file copy with precedence rules. |
| — | — | — |
| **`0-Inbox/` sort — classify destination zone** (wiki / tasks / assets / website / code) | **Agent** | Semantic judgment. "Is this a task or a content drop?" |
| **`0-Inbox/` sort — classify topic** within a destination zone | **Agent** | Semantic judgment. "Which topic folder?" |
| **Visibility classification** (this content belongs in `local/` or `git/`?) | **Agent** | Sensitivity judgment. Includes user confirmation on borderline cases. |
| **Frontmatter authoring** (set `status`, `completion`, `canon_sources`, `topics`) | **Agent** | Semantic judgment per page. |
| **Canon proposals** (extracted fact → canon YAML update) | **Agent** (proposes; user disposes) | Per `CODEX_LIBRARIAN.md` hard rule. |
| **Status-band promotion** (gap → outlined → solid → ready) | **Agent** | Content-readiness assessment. |
| **Cross-link suggestion** (which pages **should** see-also each other — beyond auto-generated) | **Agent** | Semantic relatedness. |
| **Topic taxonomy evolution** (split a folder, merge two folders, propose new topic) | **Agent** | Curatorial judgment. User confirms. |
| **Source-conflict adjudication** (new source contradicts canon) | **Agent** (halt-loud; surface both) | Per hard rule. |
| **Drift resolution** (Sync detects template drift) | **Agent** (proposes; user disposes) | Per hard rule. |
| **Brain-dump promotion** (`_brain_dump/` entry → canon or wiki page; now `wiki.*/local/ideas/`) | **Agent** | Per spec Principle #9 (explicit promotion). |
| **Public-version drafting** (internal page → public version, strip terms) | **Agent** + script (`validate_reveal_conceit.py` gates) | Drafting is agent; gating is script. |
| **Ingest execution** (full §4.3 loop) | **Agent** | Per `CODEX_LIBRARIAN.md`. |
| **Maintenance loop** (read dashboards, propose fixes) | **Agent** | Per `CODEX_LIBRARIAN.md` §Loop. |
| **Cross-project pattern mining** (Phase 2) | **Agent** (via EMCC orchestration) | Cross-wiki semantic comparison. |

## New scripts needed (gap-fill for the new spec)

Scripts that current Codex doesn't have and the new structure requires.
Listed in priority order:

1. **`audit_doc_pairing.py`** (priority: P0 — required for the new spec)
   - Scan `Biz.Automation/*/` and `wiki.<name>/git/*.doc/`.
   - Report unpaired automations (automation with no `.doc/` folder).
   - Report orphan doc folders (`.doc/` with no matching automation).
   - Emit findings to `_dashboards/doc-pairing.md`.

2. **`audit_gitignore.py`** (priority: P0)
   - Verify `.gitignore` excludes `wiki.*/local/` when `wiki.*/` exists.
   - Verify `.gitignore` excludes `Local/` if the project uses project-root zoning.
   - Verify common heavy-asset patterns are excluded.
   - Emit findings to `_dashboards/gitignore.md`.

3. **`route_inbox.py`** (priority: P0 — supports the new `0-Inbox/` operation)
   - **Half script, half agent contract.** The script enumerates
     `0-Inbox/` contents and emits a per-file `route_candidates.json`
     with deterministic metadata (filename, extension, size, mtime,
     mime, first-N-bytes hash). The Librarian agent reads this manifest
     to make routing decisions, then calls back into the script to
     execute the move.
   - Two phases: `route_inbox.py scan` (script-side, emits manifest)
     and `route_inbox.py execute <manifest>` (script-side, applies
     moves once agent has populated destinations).

4. **`audit_assets.py`** (priority: P1)
   - Scan `assets/` for files exceeding size threshold (configurable;
     default 5MB).
   - Cross-reference `.gitignore` — flag heavy files not excluded.
   - Detect probable duplicates (same hash, different paths).
   - Emit findings to `_dashboards/assets.md`.

5. **`audit_local_split.py`** (priority: P1)
   - Scan `wiki.<name>/local/` and `wiki.<name>/git/` for **misclassification
     suspects**: pages in `git/` that contain canon-marked-internal terms;
     pages in `local/` that contain only public content (could be
     promoted).
   - Surface as findings (Librarian agent confirms / rejects).
   - Hooks into existing `validate_reveal_conceit.py`.

6. **`sync_to_emcc.py`** (priority: P2 — Librarian Phase 2)
   - Push wiki metadata to EMCC's master memory (`EMCC-MEMORY.md`).
   - Push topic registry, doc-pairing status, completion dashboard
     summary.
   - Enables EMCC's `auto_scan.py` to aggregate cross-project state.

## New Librarian operations (extending the three existing)

The existing operations (Bootstrap, Sync, Ingest, Maintenance) stay.
Three new operations are added:

### Operation 4: **Inbox-Sort** (NEW — replaces / extends Codex's `_inbox/` ingest)

**Surface:** project-root `0-Inbox/`.

**Loop:**
1. Run `route_inbox.py scan` → read manifest.
2. For each file, classify destination zone:
   - **Wiki source material** (PDF, transcript, exported doc) → `wiki.<name>/git/raw/` OR `wiki.<name>/local/raw/`.
   - **Wiki page draft** (markdown with topic-relevant content) → `wiki.<name>/git/<topic>/` OR `wiki.<name>/local/<topic>/`.
   - **Task / todo / session note** → `tasks/todo.md` (append) or `tasks/sessions.md` (append-dated).
   - **Brand asset** (logo, image) → `assets/<subfolder>/`.
   - **Website content** (draft post, page copy) → `website/drafts/`.
   - **Code artifact** (script, snippet) → escalate; ask operator to clarify.
   - **Junk / scratch** → propose deletion; await user.
3. For each classified file: assess visibility (`local/` vs `git/`).
   For wiki sources: default to `local/raw/` if the source has any
   sensitivity signal (financial, legal, person names with PII); default
   to `git/raw/` for public-license content.
4. Emit a routing proposal to user: filename → destination + visibility +
   rationale.
5. User confirms (or amends).
6. Run `route_inbox.py execute <manifest>` to apply moves.
7. For wiki destinations, hand off to **Ingest** operation per spec §4.3.

**Halt-loud triggers:** unclassifiable file (extension or content
doesn't match any zone); ambiguous visibility (operator must decide).

### Operation 5: **Pairing-Audit** (NEW)

**Surface:** `Biz.Automation/*/` paired with `wiki.<name>/git/*.doc/`.

**Loop:**
1. Run `audit_doc_pairing.py` → read findings.
2. For each unpaired automation: propose creating `wiki.<name>/git/<name>.doc/`
   with stub README pointing to the automation's spec.
3. For each orphan doc folder: propose either creating the matching
   automation, OR archiving the doc folder to `wiki.<name>/git/_archive/`.
4. User confirms each proposal.
5. Apply.

### Operation 6: **Cross-Project-Scan** (NEW — Phase 2, EMCC-mediated)

**Surface:** all consumer projects in the portfolio, accessed via EMCC.

**Loop:**
1. EMCC's `auto_scan.py` aggregates per-project state (topic
   registries, doc-pairing status, completion dashboards).
2. Librarian receives aggregated state via `_blueprints/latest-scan-summary.md`.
3. Librarian proposes cross-project work:
   - **Reusable content extraction** — topic appears in 3+ projects;
     extract to portfolio-wide shared topic (lives where? EMCC's
     `_blueprints/`? An EMCC.Library shared wiki?).
   - **Naming inconsistency** — same concept named differently across
     projects; propose canonical name.
   - **Stale projects** — projects with no recent `tasks/sessions.md`
     entries.
   - **Doc-pairing portfolio sweep** — projects with multiple unpaired
     automations; prioritize for `Pairing-Audit`.
4. Proposals fed to operator via EMCC's Director surface (not directly;
   Phase 2 wiring).

**Halt-loud triggers:** cross-project conflict (two projects assert
contradictory canon for shared concept); user must adjudicate.

## Workflow: when scripts run, when Librarian runs, escalation

**Scripts run autonomously** (or on operator command):

- Bootstrap, Sync — operator-triggered, one-time + occasional.
- Validators, audits, dashboards — operator-triggered, OR on a
  scheduled hook (e.g., daily, weekly), OR pre-commit.
- Findings written to `_dashboards/*.md`. No user interruption.

**Librarian runs interactively** (operator + agent session):

- Ingest — when a new source lands in `0-Inbox/` or
  `wiki.*/git/raw/` (or `local/raw/`). Operator-triggered with
  "Librarian, ingest this source" or similar.
- Inbox-Sort — when `0-Inbox/` has accumulated drops. Operator
  triggers "Librarian, sort the inbox."
- Maintenance — operator triggers "Librarian, do a maintenance pass"
  → agent reads dashboards, picks highest-priority finding, proposes
  fix.
- Pairing-Audit — operator triggers "Librarian, audit doc pairing."
- Promotion (visibility, status-band, canon proposals) — typically
  arise within Ingest or Maintenance.

**Librarian runs autonomously (Phase 2 only):**

- Cross-Project-Scan via EMCC — scheduled (e.g., weekly).
- Produces a portfolio-state summary; operator reviews next session.

**Escalation contract** (when Librarian halts-loud):

1. Librarian writes the ambiguity + options to the active conversation
   ("Source contradicts canon entry X; here are both versions; choose").
2. Operator chooses or amends.
3. Librarian executes choice.
4. Logs decision to `_decisions/ingest-log.md` (or new `_decisions/sort-log.md`
   for Inbox-Sort operation).

**No autonomous canon writes. No autonomous classification overrides.
No autonomous file deletions.** These are the bright lines from
`CODEX_LIBRARIAN.md` and they extend to all new operations.

## Phase 1 vs Phase 2 scope

**Phase 1** (current EMCC Step 2 — Library extraction blocking issue):

- Library module ships `Biz.Automation/wikisys.library/_scripts/` with
  all 21 existing scripts.
- Library ships `.claude/personas/CLAUDE.librarian.md` as the
  Librarian drop-in (already on disk; just needs migration to project
  root per EMCC.Library punchlist).
- Operations 1-3 (Bootstrap, Sync, Ingest) work end-to-end.
- Operation 4 (Maintenance) works.
- New scripts P0 + P1 (`audit_doc_pairing.py`, `audit_gitignore.py`,
  `route_inbox.py`, `audit_assets.py`, `audit_local_split.py`) ship in
  Phase 1.
- New operations 4-5 (Inbox-Sort, Pairing-Audit) ship in Phase 1.
- Single-wiki, single-project scope.

**Phase 2** (EMCC Step 4 — Connect DFDU + Library to EMCC):

- EMCC's `_blueprints/latest-scan-summary.md` becomes the
  cross-project state surface.
- `sync_to_emcc.py` lands in Library.
- Operation 6 (Cross-Project-Scan) ships.
- Librarian gains cross-wiki visibility (read-only across projects).
- Director agent (EMCC's surface) routes user intent to Librarian
  when the user asks about wiki state across projects.

**Phase 2 is not blocked by the folder spec.** The spec works
identically in Phase 1 and Phase 2; Phase 2 adds an orchestration
layer above it.

## Deployment plan

1. Ship the folder spec (section a) and bootstrap.py (section c) —
   Codex v1.1.
2. Migrate EMCC.Library first using its own punchlist (section b).
   The migration is self-consistent: Library's `wiki.codex/` becomes
   the prior-art reference, then restructures itself into the new
   spec.
3. Add the five new scripts (`audit_doc_pairing.py` etc.) to
   `Biz.Automation/wikisys.library/_scripts/`.
4. Extend `CODEX_LIBRARIAN.md` and `.claude/personas/CLAUDE.librarian.md`
   with the three new operations (Inbox-Sort, Pairing-Audit,
   Cross-Project-Scan).
5. Test on Mentor (greenfield) — fresh bootstrap, then drop test files
   into `0-Inbox/` and run Inbox-Sort.
6. Roll out to other consumer projects per their migration punchlists.
7. Phase 2 (EMCC orchestration) ships after Phase 1 stabilizes — not
   blocking.

---

# Verification

The spec is a specification document, not code. Verification:

1. **Originating room sign-off** on F1–F12 resolutions, the seven
   migration paths (5 consumer + 3 EMCC modules + Mentor greenfield),
   and the bootstrap.py output spec.
2. **Codex v1.1 implementation** of `bootstrap.py` per section (c).
   Acceptance test: `bootstrap.py mentor --full` produces the default
   tree exactly, with all stub file contents matching.
3. **Migration dry-run per project** — run each project's punchlist
   without moving files first, verify path mappings. Each project is
   independently shippable.
4. **Real-world test** — Mentor is the first greenfield consumer of
   `bootstrap.py`. Spec is validated when Mentor reaches "first useful
   CLAUDE.md + first wiki topic + first sessions.md entry" using only
   bootstrap output as scaffold.
5. **Backward compatibility** — eddyandwolff and EMCC.Library
   migrations both involve the most structural change. Run their
   migrations after Mentor proves bootstrap; they are the gnarliest
   cases and shouldn't be the first attempts.
