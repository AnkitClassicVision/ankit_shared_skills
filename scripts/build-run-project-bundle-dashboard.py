#!/usr/bin/env python3
"""Repository-level wrapper for the Run Project Bundle dashboard builder."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "run-project-bundle-viewer" / "scripts" / "build_dashboard.py"

if __name__ == "__main__":
    sys.argv = [str(SCRIPT), *sys.argv[1:]]
    runpy.run_path(str(SCRIPT), run_name="__main__")
