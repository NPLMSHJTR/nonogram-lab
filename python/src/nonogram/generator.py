"""Generate nonograms and prove that each has exactly one solution.

A nonogram is a binary grid with run-length clues for every row and column. The
generator draws a random grid, derives the clues, and then hands the clues — never
the grid — to the solver. If the solver finds exactly one solution and it matches
the original grid, the puzzle is well-formed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Puzzle:
    size: int
    rows: list[list[int]]
    columns: list[list[int]]
    solution: list[list[int]]


def clues(line: list[int]) -> list[int]:
    runs: list[int] = []
    current = 0
    for cell in line:
        if cell:
            current += 1
        elif current:
            runs.append(current)
            current = 0
    if current:
        runs.append(current)
    return runs or [0]


def derive(grid: list[list[int]]) -> tuple[list[list[int]], list[list[int]]]:
    size = len(grid)
    rows = [clues(row) for row in grid]
    columns = [clues([grid[row][column] for row in range(size)]) for column in range(size)]
    return rows, columns


def generate(size: int = 10, density: float = 0.55, seed: int = 0) -> Puzzle:
    rng = random.Random(seed)
    while True:
        grid = [[1 if rng.random() < density else 0 for _ in range(size)] for _ in range(size)]
        filled = sum(sum(row) for row in grid)
        if size * size * 0.25 <= filled <= size * size * 0.75:
            break
    rows, columns = derive(grid)
    return Puzzle(size, rows, columns, grid)


@lru_cache(maxsize=4096)
def line_patterns(size: int, clue: tuple[int, ...]) -> tuple[int, ...]:
    """Every bitmask of a line consistent with the clue."""
    if clue == (0,):
        return (0,)
    patterns: list[int] = []

    def place(position: int, index: int, mask: int) -> None:
        if index == len(clue):
            patterns.append(mask)
            return
        remaining = sum(clue[index:]) + (len(clue) - index - 1)
        latest = size - remaining
        for start in range(position, latest + 1):
            block = mask
            for offset in range(clue[index]):
                block |= 1 << (start + offset)
            next_position = start + clue[index] + 1
            if index == len(clue) - 1:
                patterns.append(block)
            else:
                place(next_position, index + 1, block)

    place(0, 0, 0)
    return tuple(sorted(set(patterns)))


def propagate(grid: list[list[int]], rows: list[list[int]], columns: list[list[int]]) -> bool:
    """Fill forced cells until nothing changes. Returns False on contradiction."""
    size = len(grid)
    mask = (1 << size) - 1
    changed = True
    while changed:
        changed = False
        for index in range(size):
            row = grid[index]
            filled = sum(1 << column for column in range(size) if row[column] == 1)
            empty = sum(1 << column for column in range(size) if row[column] == 0)
            candidates = [
                pattern
                for pattern in line_patterns(size, tuple(rows[index]))
                if pattern & filled == filled and pattern & empty == 0
            ]
            if not candidates:
                return False
            common = mask
            union = 0
            for pattern in candidates:
                common &= pattern
                union |= pattern
            for column in range(size):
                if row[column] == -1:
                    bit = 1 << column
                    if common & bit:
                        row[column] = 1
                        changed = True
                    elif not union & bit:
                        row[column] = 0
                        changed = True
        for column in range(size):
            filled = sum(1 << row for row in range(size) if grid[row][column] == 1)
            empty = sum(1 << row for row in range(size) if grid[row][column] == 0)
            candidates = [
                pattern
                for pattern in line_patterns(size, tuple(columns[column]))
                if pattern & filled == filled and pattern & empty == 0
            ]
            if not candidates:
                return False
            common = mask
            union = 0
            for pattern in candidates:
                common &= pattern
                union |= pattern
            for row_index in range(size):
                if grid[row_index][column] == -1:
                    bit = 1 << row_index
                    if common & bit:
                        grid[row_index][column] = 1
                        changed = True
                    elif not union & bit:
                        grid[row_index][column] = 0
                        changed = True
    return True


def solve(
    puzzle: Puzzle, limit: int = 2, budget: int = 5000, reverse: bool = False
) -> tuple[list[list[list[int]]], int]:
    """Return (solutions up to limit, branch count used for the first one)."""
    size = puzzle.size
    solutions: list[list[list[int]]] = []
    branches = 0
    nodes = 0

    def search(grid: list[list[int]]) -> bool:
        nonlocal branches, nodes
        nodes += 1
        if nodes > budget:
            raise RuntimeError("search budget exceeded")
        if not propagate(grid, puzzle.rows, puzzle.columns):
            return False
        target = None
        cells = (
            [(row, column) for row in range(size) for column in range(size)]
            if not reverse
            else [(row, column) for row in range(size - 1, -1, -1) for column in range(size - 1, -1, -1)]
        )
        for row, column in cells:
            if grid[row][column] == -1:
                target = (row, column)
                break
        if target is None:
            solutions.append([row[:] for row in grid])
            return len(solutions) >= limit
        row, column = target
        for value in (1, 0):
            branches += 1
            copy = [line[:] for line in grid]
            copy[row][column] = value
            if search(copy):
                return True
        return False

    search([[-1] * size for _ in range(size)])
    return solutions, branches
