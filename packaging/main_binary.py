"""PyInstaller entry point, auto-resolves data/config.json relat to the binary.

Frozen (dist/): sys.executable as binary; data/ sits next to it; game_engine
is already importable from the bundle - no sys.path manipulation needed.
Source (local test): fall back to repo root and insert src/ manually.
"""

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    base = Path(sys.executable).parent
else:
    base = Path(__file__).parent.parent
    sys.path.insert(0, str(base / "src"))

from game_engine.core import launch  # type: ignore

sys.exit(launch(base / "data" / "config.json"))  # type: ignore
