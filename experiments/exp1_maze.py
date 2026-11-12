"""实验一：迷宫寻路的对照实验（启发函数、平局规则、规模、贪心对照）。"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

import common
import problem1_maze as p1
from astar import greedy_best_first, manhattan
from problem1_maze import TEST_GOAL, TEST_MAP, TEST_START

SIZES: List[Tuple[int, int]] = [(8, 8), (16, 16), (24, 24), (32, 32), (48, 48)]
WALL_PROB = 0.25
SEEDS = 10


def random_maze(rows: int, cols: int, p_wall: float, seed: int) -> List[List[str]]:
    rng = random.Random(seed)
    grid = [
        ["X" if rng.random() < p_wall else "." for _ in range(cols)] for _ in range(rows)
    ]
    grid[0][0] = "S"
    grid[rows - 1][cols - 1] = "E"
    return grid


def official_case() -> Dict[str, object]:
    rows: List[Dict[str, object]] = []
    for heuristic in ("zero", "manhattan"):
        res = p1.search(TEST_START, TEST_GOAL, TEST_MAP, heuristic=heuristic)
        rows.append(
            {
                "heuristic": res.stats.heuristic,
                "tie_break": "h",
                "expanded": res.stats.expanded,
                "generated": res.stats.generated,
                "max_frontier": res.stats.max_frontier,
                "path_length": res.stats.path_length,
                "steps": res.stats.path_length - 1,
                "found": res.stats.found,
                "time_ms": res.stats.wall_time_ms,
                "path": res.path,
            }
        )
    for tie in ("deep", "shallow"):
        res = p1.search(TEST_START, TEST_GOAL, TEST_MAP, "manhattan", tie_break=tie)
        rows.append(
            {
                "heuristic": res.stats.heuristic,
                "tie_break": tie,
                "expanded": res.stats.expanded,
                "generated": res.stats.generated,
                "max_frontier": res.stats.max_frontier,
                "path_length": res.stats.path_length,
                "steps": res.stats.path_length - 1,
                "found": res.stats.found,
                "time_ms": round(res.stats.wall_time_ms, 3),
                "path": res.path,
            }
        )
    grid = p1.build_grid(TEST_MAP)
    greedy = greedy_best_first(grid, TEST_START, TEST_GOAL, lambda pos: manhattan(pos, TEST_GOAL))
    rows.append(
        {
            "heuristic": "greedy best-first(只看 h)",
            "tie_break": "-",
            "expanded": greedy.stats.expanded,
            "generated": greedy.stats.generated,
            "max_frontier": greedy.stats.max_frontier,
            "path_length": greedy.stats.path_length,
            "steps": greedy.stats.path_length - 1,
            "found": greedy.stats.found,
            "time_ms": round(greedy.stats.wall_time_ms, 3),
            "path": greedy.path,
        }
    )
    for row in rows[:2]:
        row["time_ms"] = round(row["time_ms"], 3)
    return {"rows": rows, "expected": p1.EXPECTED_PATH, "no_path_case": p1.solve_maze((0, 0), (3, 4), p1.NO_PATH_MAP)}


def scaling_experiment() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for rows_n, cols_n in SIZES:
        for seed in range(SEEDS):
            maze = random_maze(rows_n, cols_n, WALL_PROB, seed)
            goal = (rows_n - 1, cols_n - 1)
            grid = p1.build_grid(maze)
            for heuristic, name in (("zero", "h=0"), ("manhattan", "Manhattan")):
                res = p1.search((0, 0), goal, maze, heuristic=heuristic)
                rows.append(
                    {
                        "size": f"{rows_n}x{cols_n}",
                        "seed": seed,
                        "heuristic": name,
                        "found": res.stats.found,
                        "expanded": res.stats.expanded,
                        "generated": res.stats.generated,
                        "steps": max(0, res.stats.path_length - 1),
                        "time_ms": res.stats.wall_time_ms,
                    }
                )
            greedy = greedy_best_first(grid, (0, 0), goal, lambda pos, g=goal: manhattan(pos, g))
            rows.append(
                {
                    "size": f"{rows_n}x{cols_n}",
                    "seed": seed,
                    "heuristic": "Greedy",
                    "found": greedy.stats.found,
                    "expanded": greedy.stats.expanded,
                    "generated": greedy.stats.generated,
                    "steps": max(0, greedy.stats.path_length - 1),
                    "time_ms": greedy.stats.wall_time_ms,
                }
            )
    return rows


def aggregate(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    buckets: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
    for row in rows:
        buckets.setdefault((row["size"], row["heuristic"]), []).append(row)  # type: ignore[arg-type]
    out: List[Dict[str, object]] = []
    for (size, heuristic), group in buckets.items():
        solved = [g for g in group if g["found"]]
        out.append(
            {
                "size": size,
                "heuristic": heuristic,
                "solved": f"{len(solved)}/{len(group)}",
                "avg_expanded": round(sum(g["expanded"] for g in group) / len(group), 1),  # type: ignore[operator]
                "avg_expanded_solved": round(sum(g["expanded"] for g in solved) / len(solved), 1)  # type: ignore[operator]
                if solved
                else 0,
                "avg_steps": round(sum(g["steps"] for g in solved) / len(solved), 2)  # type: ignore[operator]
                if solved
                else 0,
                "avg_time_ms": round(sum(g["time_ms"] for g in group) / len(group), 3),  # type: ignore[operator]
            }
        )
    order = {"h=0": 0, "Manhattan": 1, "Greedy": 2}
    out.sort(key=lambda r: (SIZES.index(tuple(int(x) for x in r["size"].split("x"))), order[r["heuristic"]]))  # type: ignore[arg-type]
    return out


def plot_scaling(agg: List[Dict[str, object]]) -> str:
    plt = common.setup_plt()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sizes = [r["size"] for r in agg if r["heuristic"] == "h=0"]
    for heuristic, marker in (("h=0", "o"), ("Manhattan", "s"), ("Greedy", "^")):
        subset = [r for r in agg if r["heuristic"] == heuristic]
        index = {r["size"]: r for r in subset}
        axes[0].plot(
            sizes, [index[s]["avg_expanded"] for s in sizes], marker=marker, label=heuristic
        )
        axes[1].plot(
            sizes, [index[s]["avg_steps"] for s in sizes], marker=marker, label=heuristic
        )
    axes[0].set_title("平均扩展节点数 vs 迷宫规模")
    axes[0].set_ylabel("expanded / 实例")
    axes[1].set_title("平均路径长度 vs 迷宫规模")
    axes[1].set_xlabel("网格尺寸 (p_wall=0.25, 10 个随机种子)")
    for ax in axes:
        ax.grid(alpha=0.3)
        ax.legend()
    path = common.figure_path("fig2_maze_scaling.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_official_path(rows: List[Dict[str, object]]) -> str:
    plt = common.setup_plt()
    path = rows[1]["path"]  # Manhattan 解
    fig, ax = plt.subplots(figsize=(4.6, 4.6))
    rows_n, cols_n = len(TEST_MAP), len(TEST_MAP[0])
    for r in range(rows_n):
        for c in range(cols_n):
            cell = TEST_MAP[r][c]
            color = {"X": "#4b4b4b", ".": "#f2f2f2", "S": "#79c7f3", "E": "#f4a259"}.get(cell, "#f2f2f2")
            ax.add_patch(plt.Rectangle((c, rows_n - 1 - r), 1, 1, facecolor=color, edgecolor="white"))
            ax.text(c + 0.5, rows_n - 1 - r + 0.5, cell, ha="center", va="center", fontsize=9)
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        ax.annotate(
            "",
            xy=(c2 + 0.5, rows_n - 1 - r2 + 0.5),
            xytext=(c1 + 0.5, rows_n - 1 - r1 + 0.5),
            arrowprops=dict(arrowstyle="-|>", color="#d62728", lw=1.8, shrinkA=6, shrinkB=6),
        )
    for step, (r, c) in enumerate(path):
        ax.text(c + 0.78, rows_n - 1 - r + 0.78, str(step), color="#d62728", fontsize=8)
    ax.set_xlim(0, cols_n)
    ax.set_ylim(0, rows_n)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"题目一 A* 最短路径（{len(path) - 1} 步）")
    out = common.figure_path("fig1_maze_path.png")
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    official = official_case()
    scaling_rows = scaling_experiment()
    agg = aggregate(scaling_rows)
    common.save_json(
        "exp1_maze.json",
        {"official": official, "scaling_rows": scaling_rows, "aggregate": agg},
    )
    common.save_csv("exp1_maze_scaling.csv", agg)
    plot_official_path(official["rows"])
    plot_scaling(agg)
    print(common.markdown_table(official["rows"], ["heuristic", "tie_break", "expanded", "generated", "max_frontier", "steps", "time_ms"]))
    print("无解用例输出:", official["no_path_case"])
    print()
    print(common.markdown_table(agg, ["size", "heuristic", "solved", "avg_expanded", "avg_steps", "avg_time_ms"]))
