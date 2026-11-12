"""实验二：加权地形 —— 启发函数可采纳性对照 + 代价累计过程。"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

import common
import problem2_terrain as p2
from problem2_terrain import EXPECTED_COST, TEST_GOAL, TEST_MAP, TEST_START

HEURISTICS = ("zero", "manhattan", "manhattan_free")


def official_case() -> Dict[str, object]:
    rows: List[Dict[str, object]] = []
    for heuristic in HEURISTICS:
        res = p2.search(TEST_START, TEST_GOAL, TEST_MAP, heuristic=heuristic)
        rows.append(
            {
                "heuristic": res.stats.heuristic,
                "cost": res.cost,
                "optimal": res.cost == EXPECTED_COST,
                "expanded": res.stats.expanded,
                "generated": res.stats.generated,
                "max_frontier": res.stats.max_frontier,
                "time_ms": round(res.stats.wall_time_ms, 3),
                "path": res.path,
            }
        )
    ref = p2.search(TEST_START, TEST_GOAL, TEST_MAP, heuristic="zero")
    return {
        "rows": rows,
        "breakdown": p2.path_cost_breakdown(ref, TEST_MAP),
        "matches_expected_path": ref.path == p2.EXPECTED_PATH,
        "no_path_case": p2.solve_terrain((0, 0), (3, 3), p2.NO_PATH_MAP),
    }


def random_terrain(rows: int, cols: int, weights: List[int], seed: int, p_wall: float = 0.0) -> List[List[str]]:
    rng = random.Random(seed)
    grid = []
    for r in range(rows):
        line = []
        for c in range(cols):
            if rng.random() < p_wall:
                line.append("X")
            else:
                line.append(str(rng.choice(weights)))
        grid.append(line)
    grid[0][0] = "S"
    grid[rows - 1][cols - 1] = "E"
    return grid


def admissibility_sweep(weights: List[int], sizes: List[Tuple[int, int]], trials: int, tag: str, p_wall: float = 0.0) -> Dict[str, object]:
    """随机地形上比较 naive Manhattan 与 h=0（Dijkstra）的最优代价，并比较 naive 与修正 h 的搜索量。"""
    mismatches: List[Dict[str, object]] = []
    solved = same_expansion = same_cost = 0
    exp_diffs: List[int] = []
    for rows, cols in sizes:
        for seed in range(trials):
            maze = random_terrain(rows, cols, weights, seed * 7 + 13, p_wall)
            goal = (rows - 1, cols - 1)
            exact = p2.search((0, 0), goal, maze, heuristic="zero")
            naive = p2.search((0, 0), goal, maze, heuristic="manhattan")
            fixed = p2.search((0, 0), goal, maze, heuristic="manhattan_free")
            if not exact.found:
                continue
            solved += 1
            if naive.cost == exact.cost:
                same_cost += 1
            else:
                mismatches.append(
                    {
                        "tag": tag,
                        "size": f"{rows}x{cols}",
                        "seed": seed * 7 + 13,
                        "optimal_cost": exact.cost,
                        "naive_cost": naive.cost,
                        "fixed_cost": fixed.cost,
                        "gap": naive.cost - exact.cost,
                        "map": maze,
                        "naive_expanded": naive.stats.expanded,
                        "exact_expanded": exact.stats.expanded,
                    }
                )
            if naive.stats.expanded == fixed.stats.expanded and naive.cost == fixed.cost:
                same_expansion += 1
            exp_diffs.append(naive.stats.expanded - fixed.stats.expanded)
    return {
        "tag": tag,
        "weights": weights,
        "p_wall": p_wall,
        "instances": solved,
        "naive_optimal_count": same_cost,
        "mismatches": len(mismatches),
        "mismatch_rate": round(len(mismatches) / solved, 4) if solved else 0.0,
        "max_gap": max((m["gap"] for m in mismatches), default=0),
        "naive_equals_fixed_rate": round(same_expansion / solved, 4) if solved else 0.0,
        "expansion_diff_range": [min(exp_diffs, default=0), max(exp_diffs, default=0)],
        "examples": mismatches[:3],
    }


def expansion_table(weights: List[int], size: Tuple[int, int], trials: int) -> List[Dict[str, object]]:
    rows_n, cols_n = size
    rows: List[Dict[str, object]] = []
    for seed in range(trials):
        maze = random_terrain(rows_n, cols_n, weights, seed * 3 + 5, p_wall=0.15)
        goal = (rows_n - 1, cols_n - 1)
        sample: Dict[str, object] = {"seed": seed * 3 + 5}
        for heuristic in HEURISTICS:
            res = p2.search((0, 0), goal, maze, heuristic=heuristic)
            sample[f"{heuristic}_expanded"] = res.stats.expanded
            sample[f"{heuristic}_cost"] = res.cost
        rows.append(sample)
    return rows


def goal_cost_variant() -> Dict[str, object]:
    """把 E 的进入代价从 0 改为 1（另一种可能的题面读法），比较三种启发式。"""
    variant = [row[:] for row in TEST_MAP]
    variant[TEST_GOAL[0]][TEST_GOAL[1]] = "1"
    out: List[Dict[str, object]] = []
    for heuristic in HEURISTICS:
        res = p2.search(TEST_START, TEST_GOAL, variant, heuristic=heuristic)
        out.append(
            {
                "heuristic": res.stats.heuristic,
                "cost": res.cost,
                "expanded": res.stats.expanded,
                "path": res.path,
            }
        )
    return {"rows": out}


def plot_breakdown(breakdown: List[Dict[str, object]]) -> str:
    plt = common.setup_plt()
    steps = [row["step"] for row in breakdown]
    g = [row["g"] for row in breakdown]
    h = [row["h"] for row in breakdown]
    step_cost = [row["step_cost"] for row in breakdown]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(steps, step_cost, color="#9ecae1", label="进入该格的代价")
    ax.plot(steps, g, marker="o", color="#d62728", label="g（累计代价）")
    ax.plot(steps, h, marker="s", color="#2ca02c", label="h（到 E 的曼哈顿距离）")
    ax.plot(steps, [a + b for a, b in zip(g, h)], marker="^", ls="--", color="#1f77b4", label="f = g + h")
    for x, (gv, cell) in enumerate(zip(g, [row["cell"] for row in breakdown])):
        ax.text(x, gv + 0.15, str(cell), ha="center", fontsize=8, color="#555555")
    ax.set_xticks(steps)
    ax.set_xlabel("路径上的第 k 个坐标")
    ax.set_ylabel("代价")
    ax.set_title("题目二最优解的代价累计过程（S→E，E 进入代价记 0）")
    ax.grid(alpha=0.3)
    ax.legend(ncol=2, fontsize=8)
    out = common.figure_path("fig3_terrain_profile.png")
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    official = official_case()
    sweeps = [
        admissibility_sweep([1, 3, 8], [(4, 4), (5, 5), (6, 6)], 40, "min=1（题面地形）"),
        admissibility_sweep([2, 3, 8], [(4, 4), (5, 5), (6, 6)], 40, "min=2（无平原地带）"),
        admissibility_sweep([1, 2, 5, 9], [(5, 5), (7, 7)], 30, "min=1 权重更多"),
        admissibility_sweep([1, 1, 1, 3, 8], [(6, 6), (8, 8)], 40, "min=1 含障碍 X", p_wall=0.2),
    ]
    expansions = expansion_table([1, 3, 8], (8, 8), 25)
    avg = {
        heuristic: round(sum(row[f"{heuristic}_expanded"] for row in expansions) / len(expansions), 1)
        for heuristic in HEURISTICS
    }
    variant = goal_cost_variant()
    common.save_json(
        "exp2_terrain.json",
        {
            "official": official,
            "admissibility_sweeps": sweeps,
            "expansion_8x8_rows": expansions,
            "expansion_8x8_avg": avg,
            "goal_cost_variant": variant,
        },
    )
    plot_breakdown(official["breakdown"])
    print(common.markdown_table(official["rows"], ["heuristic", "cost", "optimal", "expanded", "generated", "time_ms"]))
    print("无解用例:", official["no_path_case"])
    print("8x8 平均扩展节点:", avg)
    for sweep in sweeps:
        print(
            f"{sweep['tag']:22s} 实例={sweep['instances']} naive最优={sweep['naive_optimal_count']} "
            f"次优={sweep['mismatches']} naive==fixed比例={sweep['naive_equals_fixed_rate']} "
            f"扩展差范围={sweep['expansion_diff_range']}"
        )
    print()
    print(common.markdown_table(variant["rows"], ["heuristic", "cost", "expanded"]))
