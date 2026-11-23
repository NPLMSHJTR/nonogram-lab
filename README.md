# nonogram-lab

**中文简介** — 生成数织（Nonogram）谜题，并为每一道题**证明它恰好只有一个解**；60 道 10×10 的题目里，58 道仅靠行列逻辑就能推出，不需要猜。附一个单文件可玩网页：只内嵌提示、不内嵌答案，胜负由“盘面算出的提示是否等于题目提示”判定。

**English** — Generate nonograms and prove that each one has exactly one solution. Of sixty 10×10 puzzles, 58 are solvable by line logic alone. A self-contained player page embeds clues only — never the answer — and decides a win by recomputing the clues from your grid.

```console
$ python scripts/demo.py
nonogram-lab 0.1.0  60 puzzles  10x10
unique 60/60  logic-only 58/60  avg branches 0.07
typescript clues: match
player: nonogram-run/player.html
```

Open `nonogram-run/player.html` in a browser to play.

## Why "proven unique" matters

Most generated puzzle sets are checked by eye or not at all. A board with two
solutions is not a puzzle: two players can fill it differently and both be right.
This generator refuses to ship such a board — the solver enumerates solutions and
keeps a puzzle only when the count is exactly one and the solution matches the grid
it was drawn from.

Uniqueness is checked twice: once with ascending cell order, once with descending.
That does not prove the solver correct, but it catches branching-order bugs that a
single run would hide.

## How the solver works

1. Pre-compute every line pattern consistent with a clue (`line_patterns`).
2. Propagate: for each row and column, intersect the patterns still compatible with
   the current cells; cells filled in all patterns become filled, cells empty in all
   become empty. Repeat until stable.
3. If stuck, branch on the first unknown cell and recurse.
4. Count solutions up to two — two is enough to reject a puzzle.

Difficulty is graded by the number of branches needed for the first solution:
`logic only` (0), `light search` (≤4), `deep search` (>4).

## Results

| Metric | Value |
| --- | --- |
| Puzzles | 60 (10×10) |
| Exactly one solution | 60/60 |
| Solvable by line logic alone | 58/60 |
| Average branches to first solution | 0.07 |
| Worst case | 2 branches |
| Generate + verify time | 0.05 s |
| TypeScript clue recomputation | all match |

The skew toward "logic only" is intentional: guessing is the least enjoyable part
of a nonogram. A harder set is a matter of grid size and density, not a different
algorithm.

## Cross-language check

The Python generator computes clues from the grid. `src/render.ts` independently
recomputes every row and column clue from the solution and exits non-zero on a
mismatch, so the run-length rule is implemented twice. The same file renders an
ASCII preview used in the report.

## Playing

- Left click fills a cell; click again to clear.
- Right click marks a cell with × (a note to yourself).
- A clue turns green when its line is satisfied.
- The timer stops when every row and column matches.

The page embeds `rows` and `columns` only. There is no solution array in the HTML,
so reading the source does not spoil the puzzle.

## Limits

- **10×10 in the demo.** Bigger boards work but slow the uniqueness proof; 15×15
  is the practical ceiling for this solver.
- **Easy by design.** 58/60 need no search; players looking for brutal puzzles
  should lower the density or raise the size.
- **No save state.** Reloading restarts the timer; there is no progress storage.
- **DOM rendering.** The player is plain HTML/CSS/JS, not a canvas engine, which
  keeps it readable but caps the grid size that stays comfortable.

## Repository layout

```
python/src/nonogram/generator.py  clues, line patterns, propagation, search
python/src/nonogram/solver.py     unique-puzzle rejection sampling, grading
python/src/nonogram/web.py        single-file player builder
src/render.ts                     independent clue check and ASCII preview
scripts/demo.py                   generate, verify, and build the player
```

## Development

```bash
PYTHONPATH=python/src python -m unittest discover -s python/tests -t python/tests -v
cd python && pip install -e ".[dev]" && ruff check . && mypy
```

## License

MIT. See [LICENSE](LICENSE).
