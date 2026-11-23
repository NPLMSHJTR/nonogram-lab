"""Tests for clue derivation and line patterns."""

from __future__ import annotations

import unittest

from nonogram.generator import clues, derive, line_patterns, solve
from nonogram.solver import grade, unique_puzzle


class ClueTests(unittest.TestCase):
    def test_runs_are_counted(self) -> None:
        self.assertEqual(clues([1, 1, 0, 1, 0, 0, 1, 1, 1]), [2, 1, 3])

    def test_empty_line_is_zero(self) -> None:
        self.assertEqual(clues([0, 0, 0]), [0])

    def test_derive_both_directions(self) -> None:
        grid = [[1, 0], [1, 1]]
        rows, columns = derive(grid)
        self.assertEqual(rows, [[1], [2]])
        self.assertEqual(columns, [[2], [1]])


class PatternTests(unittest.TestCase):
    def test_patterns_match_the_line_length(self) -> None:
        patterns = line_patterns(5, (2, 1))
        self.assertTrue(patterns)
        for pattern in patterns:
            bits = [(pattern >> index) & 1 for index in range(5)]
            self.assertEqual(clues(bits), [2, 1])

    def test_zero_clue_has_one_pattern(self) -> None:
        self.assertEqual(line_patterns(5, (0,)), (0,))


class PuzzleTests(unittest.TestCase):
    def test_generated_puzzle_is_unique(self) -> None:
        puzzle, branches = unique_puzzle(size=8, seed=2)
        solutions, _ = solve(puzzle, limit=2, budget=20_000)
        self.assertEqual(len(solutions), 1)
        self.assertEqual(solutions[0], puzzle.solution)
        self.assertGreaterEqual(branches, 0)

    def test_grade_thresholds(self) -> None:
        self.assertEqual(grade(0), "logic only")
        self.assertEqual(grade(3), "light search")
        self.assertEqual(grade(9), "deep search")


if __name__ == "__main__":
    unittest.main()
