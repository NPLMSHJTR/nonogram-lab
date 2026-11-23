"""Build a self-contained player page.

The page embeds clues only, never the solution. Winning is decided by recomputing
the clues of the player's grid and comparing them with the puzzle, which is the
actual rule of the game and keeps the answer out of the HTML source.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>nonogram-lab</title>
<style>
 :root{--bg:#0b1020;--panel:#121a2c;--line:#26314a;--text:#e6ecf6;--muted:#8fa0b8;--fill:#60a5fa;--mark:#f87171}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 ui-sans-serif,system-ui,sans-serif}
 header{padding:22px 24px;border-bottom:1px solid var(--line);display:flex;gap:20px;align-items:baseline;flex-wrap:wrap}
 h1{font-size:18px;margin:0}
 .sub{color:var(--muted);font-size:13px}
 main{padding:22px 24px;display:flex;gap:28px;flex-wrap:wrap;align-items:flex-start}
 .board{display:grid;grid-template-columns:auto auto;gap:4px}
 .clues-top{display:grid;gap:2px}
 .clues-left{display:grid;gap:2px}
 .corner{}
 .grid{display:grid;border:1px solid var(--line);background:var(--line);gap:1px}
 .cell{width:30px;height:30px;background:var(--panel);cursor:pointer;user-select:none}
 .cell.fill{background:var(--fill)}
 .cell.mark{background:var(--panel);position:relative}
 .cell.mark::after{content:"×";position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--mark);font-size:20px;line-height:1}
 .cell:hover{outline:1px solid var(--fill)}
 .clue{display:flex;align-items:center;justify-content:flex-end;color:var(--muted);font-size:12px;padding:0 4px;min-height:14px}
 .clue.done{color:#4ade80}
 .clues-top .clue{flex-direction:column;justify-content:flex-end;min-width:30px;min-height:56px}
 .side{max-width:280px}
 .stat{color:var(--muted);font-size:13px;margin:6px 0}
 .stat b{color:var(--text);font-variant-numeric:tabular-nums}
 button{margin-top:12px;padding:9px 14px;border-radius:8px;border:0;background:var(--fill);color:#06101f;font-weight:600;cursor:pointer}
 select{margin-top:8px;width:100%;padding:8px;border-radius:8px;background:var(--panel);color:var(--text);border:1px solid var(--line)}
 .win{color:#4ade80;font-weight:600}
</style></head><body>
<header>
 <h1>nonogram-lab</h1>
 <div class="sub">Every puzzle has exactly one solution · left click fills · right click marks</div>
</header>
<main>
 <div class="board">
  <div class="corner"></div><div class="clues-top" id="top"></div>
  <div class="clues-left" id="left"></div><div class="grid" id="grid"></div>
 </div>
 <aside class="side">
  <div class="stat">puzzle <b id="pid"></b> · seed <b id="seed"></b></div>
  <div class="stat">time <b id="time">0:00</b> · filled <b id="filled">0</b>/<b id="total">0</b></div>
  <div class="stat" id="status">Left click to fill, right click to mark.</div>
  <select id="picker"></select>
  <button id="new">Load puzzle</button>
 </aside>
</main>
<script>
const PUZZLES = __DATA__;
let current = 0, grid = [], timer = null, seconds = 0;
const gridEl = document.getElementById("grid");
const topEl = document.getElementById("top");
const leftEl = document.getElementById("left");

function exactClues(line){
  const runs=[]; let run=0;
  for(const cell of line){ if(cell===1) run++; else if(run){ runs.push(run); run=0; } }
  if(run) runs.push(run);
  return runs.length?runs:[0];
}
function same(a,b){ return a.length===b.length && a.every((v,i)=>v===b[i]); }
function load(index){
  current = index;
  const p = PUZZLES[index];
  document.getElementById("pid").textContent = p.id;
  document.getElementById("seed").textContent = p.seed;
  document.getElementById("total").textContent = p.filled;
  grid = Array.from({length:p.size},()=>Array(p.size).fill(0));
  seconds = 0; document.getElementById("time").textContent = "0:00";
  document.getElementById("status").className = "stat";
  document.getElementById("status").textContent = "Left click to fill, right click to mark.";
  clearInterval(timer);
  timer = setInterval(()=>{ seconds++; document.getElementById("time").textContent =
    Math.floor(seconds/60)+":"+String(seconds%60).padStart(2,"0"); }, 1000);

  gridEl.style.gridTemplateColumns = `repeat(${p.size}, 30px)`;
  gridEl.innerHTML = "";
  for(let r=0;r<p.size;r++) for(let c=0;c<p.size;c++){
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.dataset.row = r; cell.dataset.col = c;
    cell.addEventListener("click", ()=>paint(r,c,1));
    cell.addEventListener("contextmenu", (e)=>{ e.preventDefault(); paint(r,c,2); });
    gridEl.appendChild(cell);
  }

  topEl.style.gridTemplateColumns = `repeat(${p.size}, 30px)`;
  topEl.innerHTML = p.columns.map((clue, c)=>`<div class="clue" data-col="${c}">${clue.join("<br>")}</div>`).join("");
  leftEl.style.gridTemplateRows = `repeat(${p.size}, 30px)`;
  leftEl.innerHTML = p.rows.map((clue,r)=>`<div class="clue" data-row="${r}">${clue.join(" ")}</div>`).join("");
  draw();
}

function paint(row, col, value){
  const p = PUZZLES[current];
  grid[row][col] = grid[row][col] === value ? 0 : value;
  draw();
}

function draw(){
  const p = PUZZLES[current];
  const cells = gridEl.children;
  let filled = 0;
  for(let r=0;r<p.size;r++) for(let c=0;c<p.size;c++){
    const cell = cells[r*p.size+c];
    cell.className = "cell" + (grid[r][c]===1?" fill":grid[r][c]===2?" mark":"");
    if(grid[r][c]===1) filled++;
  }
  document.getElementById("filled").textContent = filled;

  for(let r=0;r<p.size;r++){
    const clueEl = leftEl.children[r];
    const done = same(exactClues(grid[r]), p.rows[r]);
    clueEl.className = "clue" + (done?" done":"");
  }
  for(let c=0;c<p.size;c++){
    const column = grid.map(row=>row[c]);
    const done = same(exactClues(column), p.columns[c]);
    topEl.children[c].className = "clue" + (done?" done":"");
  }

  const rowsOk = p.rows.every((clue,r)=>same(exactClues(grid[r]), clue));
  const colsOk = p.columns.every((clue,c)=>same(exactClues(grid.map(row=>row[c])), clue));
  if(rowsOk && colsOk){
    clearInterval(timer);
    const status = document.getElementById("status");
    status.className = "stat win";
    status.textContent = "Solved in " + Math.floor(seconds/60) + ":" + String(seconds%60).padStart(2,"0");
  }
}

const picker = document.getElementById("picker");
picker.innerHTML = PUZZLES.map((p,i)=>`<option value="${i}">${p.id} · seed ${p.seed}</option>`).join("");
document.getElementById("new").onclick = ()=>load(Number(picker.value));
load(0);
</script></body></html>
"""


def build(puzzles: list[dict[str, Any]], out: Path) -> Path:
    payload = []
    for puzzle in puzzles:
        rows = puzzle["rows"]
        columns = puzzle["columns"]
        payload.append(
            {
                "id": puzzle["id"],
                "seed": puzzle["seed"],
                "size": puzzle["size"],
                "rows": rows,
                "columns": columns,
                "filled": sum(sum(clue) for clue in rows),
            }
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(TEMPLATE.replace("__DATA__", json.dumps(payload)), encoding="utf-8")
    return out
