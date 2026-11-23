#!/usr/bin/env python3
"""Run nonogram-lab: generate, prove uniqueness, build the player."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if shutil.which("node") is None:
        print("node is required for the cross-check", file=sys.stderr)
        return 2
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "python" / "src")
    command = [sys.executable, "-m", "nonogram", "run", "--workdir", "nonogram-run"]
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True, env=env)
    print()
    print(f"player: {ROOT / 'nonogram-run' / 'player.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
