"""nonogram-lab: unique nonograms with a proven solution and a playable page."""

from __future__ import annotations

__version__ = "0.1.0"

from .generator import Puzzle, clues, derive, generate, solve  # noqa: E402
from .solver import grade, unique_puzzle  # noqa: E402

__all__ = ["__version__", "Puzzle", "clues", "derive", "generate", "grade", "solve", "unique_puzzle"]
