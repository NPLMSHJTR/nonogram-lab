"""Generate a puzzle set, prove uniqueness, and cross-check clues in TypeScript.

Uniqueness is established by the solver; to guard against a branching-order bug,
each puzzle is solved a second time with the opposite cell order. The TypeScript
renderer then recomputes every clue from the solution, which is an independent
implementation of the run-length rule.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from .generator import solve
from .solver import grade, unique_puzzle

ROOT = Path(__file__).resolve().parents[3]


def run(workdir: Path, count: int = 60, size: int = 10, seed: int = 0) -> dict[str, Any]:
    workdir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    puzzles = []
    failures = []
    branches_total = 0
    logic_only = 0
    max_branches = 0
    for index in range(count):
        puzzle, branches = unique_puzzle(size=size, seed=seed + index)
        solutions, _ = solve(puzzle, limit=2, budget=50_000, reverse=True)
        unique_again = len(solutions) == 1 and solutions[0] == puzzle.solution
        if not unique_again:
            failures.append({"seed": seed + index, "reason": "second search disagreed"})
        branches_total += branches
        logic_only += branches == 0
        max_branches = max(max_branches, branches)
        puzzles.append(
            {
                "id": f"p{index:03d}",
                "seed": seed + index,
                "size": puzzle.size,
                "rows": puzzle.rows,
                "columns": puzzle.columns,
                "solution": puzzle.solution,
                "branches": branches,
                "grade": grade(branches),
            }
        )
    elapsed = time.perf_counter() - started

    data_path = workdir / "puzzles.json"
    data_path.write_text(json.dumps({"puzzles": puzzles}, separators=(",", ":")) + "\n", encoding="utf-8")

    render = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            str(ROOT / "src" / "render.ts"),
            "--input",
            str(data_path),
            "--out",
            str(workdir / "render.txt"),
        ],
        capture_output=True,
        text=True,
    )
    clues_match = render.returncode == 0
    rendered = (workdir / "render.txt").read_text(encoding="utf-8") if clues_match else ""

    return {
        "puzzles": count,
        "size": size,
        "unique": count - len(failures),
        "failures": failures,
        "logic_only": logic_only,
        "average_branches": round(branches_total / count, 2),
        "max_branches": max_branches,
        "generation_s": round(elapsed, 3),
        "clues_match_typescript": clues_match,
        "render_error": render.stderr[-300:] if not clues_match else "",
        "render_preview": rendered[:1200],
        "checks": {
            "all_unique": not failures,
            "typescript_clues_match": clues_match,
        },
    }
