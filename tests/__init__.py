"""Test package init: ensure _scripts/ is on sys.path for unittest discovery."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_scripts"))
