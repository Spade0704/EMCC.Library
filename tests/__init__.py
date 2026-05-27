"""Test package init: ensure _scripts/ is on sys.path for unittest discovery.

S002 / Codex v1.1: source-of-truth moved from `<repo>/_scripts/` to
`<repo>/Biz.Automation/wikisys.library/_scripts/`. See
REORGANIZATION-INSTRUCTIONS.md pattern P1.
"""

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent
        / "Biz.Automation" / "wikisys.library" / "_scripts"
    ),
)
