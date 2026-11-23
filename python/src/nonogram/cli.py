"""Command-line interface for nonogram-lab."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .harness import run
from .web import build

EXIT_OK = 0
EXIT_ERROR = 2


def cmd_run(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir)
    result = run(workdir, count=args.count, size=args.size, seed=args.seed)
    puzzles = json.loads((workdir / "puzzles.json").read_text(encoding="utf-8"))["puzzles"]
    player = build(puzzles, workdir / "player.html")

    lines = [
        "# nonogram-lab report",
        "",
        f"- puzzles: {result['puzzles']} ({result['size']}×{result['size']})",
        f"- exactly one solution: {result['unique']}/{result['puzzles']}",
        f"- solvable by line logic alone: {result['logic_only']}/{result['puzzles']}",
        f"- average branches to first solution: {result['average_branches']}",
        f"- worst case branches: {result['max_branches']}",
        f"- generation and verification: {result['generation_s']} s",
        f"- TypeScript clue recomputation: {'match' if result['clues_match_typescript'] else 'MISMATCH'}",
        "",
        "Uniqueness is established by the solver, then re-checked with the opposite",
        "branching order. The TypeScript renderer recomputes every clue from the",
        "solution, so the run-length rule is implemented twice.",
    ]
    report = workdir / "reports" / "report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    print(f"nonogram-lab {__version__}  {result['puzzles']} puzzles  {result['size']}x{result['size']}")
    print(
        f"unique {result['unique']}/{result['puzzles']}  logic-only {result['logic_only']}/{result['puzzles']}  "  # noqa: E501
        f"avg branches {result['average_branches']}"
    )
    print(f"typescript clues: {'match' if result['clues_match_typescript'] else 'MISMATCH'}")
    print(f"player: {player}")
    print(f"report: {report}")
    return EXIT_OK if all(result["checks"].values()) else EXIT_ERROR


def cmd_web(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    out = build(payload["puzzles"], Path(args.out))
    print(f"wrote {out}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nonogram", description="Generate unique nonograms and a playable page."
    )
    parser.add_argument("--version", action="version", version=f"nonogram-lab {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_cmd = subparsers.add_parser("run", help="generate puzzles, prove uniqueness, build the player")
    run_cmd.add_argument("--count", type=int, default=60)
    run_cmd.add_argument("--size", type=int, default=10)
    run_cmd.add_argument("--seed", type=int, default=0)
    run_cmd.add_argument("--workdir", default="nonogram-run")
    run_cmd.set_defaults(func=cmd_run)

    web_cmd = subparsers.add_parser("web", help="rebuild the player from an existing puzzle file")
    web_cmd.add_argument("--input", required=True)
    web_cmd.add_argument("--out", default="player.html")
    web_cmd.set_defaults(func=cmd_web)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, OSError) as error:
        print(f"nonogram: {error}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
