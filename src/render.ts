#!/usr/bin/env node
/**
 * Independently recompute nonogram clues from the solution and render ASCII.
 *
 * If this disagrees with the Python-generated clues, one of the two run-length
 * implementations is wrong; the harness fails on a non-zero exit.
 *
 * Usage: node --experimental-strip-types src/render.ts --input puzzles.json --out render.txt
 */

import { readFileSync, writeFileSync } from "node:fs";

type Puzzle = {
  id: string;
  size: number;
  rows: number[][];
  columns: number[][];
  solution: number[][];
};

const args = process.argv.slice(2);
const value = (name: string, fallback: string): string => {
  const index = args.indexOf(`--${name}`);
  return index >= 0 && args[index + 1] ? args[index + 1] : fallback;
};

const payload = JSON.parse(readFileSync(value("input", "puzzles.json"), "utf8")) as { puzzles: Puzzle[] };

function clues(line: number[]): number[] {
  const runs: number[] = [];
  let current = 0;
  for (const cell of line) {
    if (cell) current += 1;
    else if (current) {
      runs.push(current);
      current = 0;
    }
  }
  if (current) runs.push(current);
  return runs.length ? runs : [0];
}

const same = (a: number[], b: number[]): boolean => a.length === b.length && a.every((v, i) => v === b[i]);
let failures = 0;
const lines: string[] = [];

for (const puzzle of payload.puzzles) {
  for (let row = 0; row < puzzle.size; row++) {
    if (!same(clues(puzzle.solution[row]), puzzle.rows[row])) {
      failures += 1;
      lines.push(`MISMATCH ${puzzle.id} row ${row}`);
    }
  }
  for (let column = 0; column < puzzle.size; column++) {
    const columnValues = puzzle.solution.map((row) => row[column]);
    if (!same(clues(columnValues), puzzle.columns[column])) {
      failures += 1;
      lines.push(`MISMATCH ${puzzle.id} column ${column}`);
    }
  }
  lines.push(`${puzzle.id} seed=${puzzle.seed}`);
  lines.push("  " + puzzle.columns.map((clue) => `[${clue.join(" ")}]`).join(" "));
  for (let row = 0; row < puzzle.size; row++) {
    const left = puzzle.rows[row].join(" ").padStart(8);
    const cells = puzzle.solution[row].map((cell) => (cell ? "##" : "..")).join("");
    lines.push(`${left} | ${cells}`);
  }
}

writeFileSync(value("out", "render.txt"), lines.join("\n") + "\n", "utf8");
if (failures > 0) {
  console.error(`${failures} clue mismatches between TypeScript and the stored puzzles`);
  process.exit(1);
}
console.log(`rendered ${payload.puzzles.length} puzzles, all clues match`);
