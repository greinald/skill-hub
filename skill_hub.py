#!/usr/bin/env python3
"""Direct entry point for people who clone the repository."""

import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).parent / "skills" / "skill-hub" / "scripts" / "skill_hub.py"),
    run_name="__main__",
)
