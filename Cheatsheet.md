# Cheatsheet — EMCC.Library

> Operator (JP) quick reference. Standardized across EMCC projects. Commands are PowerShell (Windows).

## Paths
- Repo (local): `<fill, e.g. D:\Claude Projects\EMCC.Library>`
- GitHub: https://github.com/Spade0704/EMCC.Library
- Set once (user env): `$env:EMCC_ROOT` = EMCC clone, `$env:EMCC_LIBRARY_ROOT` = EMCC.Library clone.

## EMCC module skills — install once per clone
```powershell
claude plugin marketplace add "$env:EMCC_ROOT\marketplace" --scope project
claude plugin install emcc-lattice@emcc --scope project   # Lattice: /research /build /update_doc
claude plugin install emcc-codex@emcc   --scope project   # Codex:   /ingest /lint /maintain /sync
```

## Git (PowerShell)
```powershell
$br = git rev-parse --abbrev-ref HEAD            # current branch
git status -sb                                   # status + ahead/behind
git pull  origin $br                             # pull
git push -u origin $br                           # push
```

## SHA check (in sync with origin?)
```powershell
git fetch origin
git rev-parse --short HEAD                        # local SHA
git rev-parse --short "origin/$br"                # remote SHA
git rev-list --left-right --count "HEAD...origin/$br"   # <ahead> <behind>
```

## Codex wiki — sync tooling + dashboards (PowerShell)
```powershell
# Library IS the Codex source — sync_from_kit ships OUT to consumers, not into Library.
# Regenerate Library's own dogfood dashboards:
python ".\Biz.Automation\wikisys.library\_scripts\update_dashboards.py"
```

## Open Claude Code with Telegram auto-summary (PowerShell)
```powershell
$env:TELEGRAM_BOT_TOKEN = "<bot-token>"   # secret — persist once: setx TELEGRAM_BOT_TOKEN "<bot-token>"
$env:TELEGRAM_CHAT_ID   = "1415844818"
claude                                    # launch CC here; decision_needed escalations hit Telegram
```
