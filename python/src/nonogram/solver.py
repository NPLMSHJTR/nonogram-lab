"""Uniqueness-first puzzle construction and difficulty grading."""

from __future__ import annotations

from .generator import Puzzle, generate, solve


def unique_puzzle(
    size: int = 10, density: float = 0.55, seed: int = 0, attempts: int = 60
) -> tuple[Puzzle, int]:
    """Return a puzzle whose clue set has exactly one solution.

    Random grids often admit several solutions; rejection sampling is cheaper than
    repairing clues, and the solver is the only judge.
    """
    last_error: Exception | None = None
    for attempt in range(attempts):
        puzzle = generate(size=size, density=density, seed=seed * 1000 + attempt)
        try:
            solutions, branches = solve(puzzle, limit=2, budget=50_000)
        except RuntimeError as error:
            last_error = error
            continue
        if len(solutions) == 1 and solutions[0] == puzzle.solution:
            return puzzle, branches
    raise RuntimeError(f"no unique puzzle for seed {seed}: {last_error}")


def grade(branches: int) -> str:
    if branches == 0:
        return "logic only"
    if branches <= 4:
        return "light search"
    return "deep search"
