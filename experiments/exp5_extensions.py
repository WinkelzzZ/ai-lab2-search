"""实验五：创新与拓展 —— IDA* 对照、加权启发式、平局规则、宝藏价值敏感性。"""

from __future__ import annotations

import random
from typing import Dict, List

import common
import problem1_maze as p1
import problem4_treasure as p4
from astar import Grid, astar, manhattan
from ida_star import ida_star, weighted_heuristic
from exp1_maze import random_maze

SIZES = [(8, 8), (12, 12), (16, 16), (20, 20), (24, 24)]
TRIALS = 8


def _grid(maze: List[List[str]]) -> Grid:
    return p1.build_grid(maze)


def ida_vs_astar() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for rows_n, cols_n in SIZES:
        acc: Dict[str, List[float]] = {
            "astar_expanded": [],
            "astar_memory": [],
            "astar_time": [],
            "ida_generations": [],
            "ida_iterations": [],
            "ida_memory": [],
            "ida_best_g": [],
            "ida_time": [],
            "cost_agree": [],
        }
        for seed in range(TRIALS):
            maze = random_maze(rows_n, cols_n, 0.25, seed * 11 + 3)
            goal = (rows_n - 1, cols_n - 1)
            grid = _grid(maze)
            a = astar(grid, (0, 0), goal, lambda pos: manhattan(pos, goal), label="maze")
            if not a.found:
                continue
            i = ida_star(grid, (0, 0), goal, lambda pos: manhattan(pos, goal))
            acc["astar_expanded"].append(a.stats.expanded)
            acc["astar_memory"].append(a.stats.max_frontier + a.stats.expanded)
            acc["astar_time"].append(a.stats.wall_time_ms)
            acc["ida_generations"].append(i.generations)
            acc["ida_iterations"].append(i.iterations)
            acc["ida_memory"].append(i.peak_depth)
            acc["ida_best_g"].append(i.max_memory_states)
            acc["ida_time"].append(i.wall_time_ms)
            acc["cost_agree"].append(int(a.cost) == int(i.cost))
        n = len(acc["astar_expanded"])
        if n == 0:
            continue
        rows.append(
            {
                "size": f"{rows_n}x{cols_n}",
                "solved": n,
                "astar_expanded": round(sum(acc["astar_expanded"]) / n, 1),
                "astar_peak_states": round(sum(acc["astar_memory"]) / n, 1),
                "ida_generations": round(sum(acc["ida_generations"]) / n, 1),
                "ida_iterations": round(sum(acc["ida_iterations"]) / n, 1),
                "ida_peak_path_states": round(sum(acc["ida_memory"]) / n, 1),
                "ida_gmap_states": round(sum(acc["ida_best_g"]) / n, 1),
                "generations_ratio": round(sum(acc["ida_generations"]) / sum(acc["astar_expanded"]), 2),
                "path_depth_over_astar_states": round(
                    sum(acc["ida_memory"]) / sum(acc["astar_memory"]), 3
                ),
                "cost_identical": all(acc["cost_agree"]),
                "astar_ms": round(sum(acc["astar_time"]) / n, 3),
                "ida_ms": round(sum(acc["ida_time"]) / n, 3),
            }
        )
    return rows


def weighted_astar() -> List[Dict[str, object]]:
    weights = [1.0, 1.5, 2.0, 4.0, 8.0, 16.0]
    rows: List[Dict[str, object]] = []
    mazes = []
    for seed in range(20):
        maze = random_maze(16, 16, 0.25, seed * 5 + 1)
        goal = (15, 15)
        grid = _grid(maze)
        ref = astar(grid, (0, 0), goal, lambda pos: 0, label="ref")
        if ref.found:
            mazes.append((maze, goal, grid, ref.cost))
    for w in weights:
        expanded, costs, subopt = [], [], []
        for maze, goal, grid, opt in mazes:
            res = astar(
                grid,
                (0, 0),
                goal,
                weighted_heuristic(goal, w),
                label=f"w={w}",
                heuristic_name=f"w={w} x Manhattan",
            )
            expanded.append(res.stats.expanded)
            costs.append(res.cost)
            subopt.append(res.cost / opt)
        rows.append(
            {
                "weight": w,
                "instances": len(mazes),
                "avg_expanded": round(sum(expanded) / len(expanded), 1),
                "avg_cost": round(sum(costs) / len(costs), 2),
                "avg_suboptimality": round(sum(subopt) / len(subopt), 4),
                "worst_suboptimality": round(max(subopt), 4),
                "optimal_rate": round(sum(1 for s in subopt if s < 1.0001) / len(subopt), 3),
            }
        )
    return rows


def tie_break_experiment() -> List[Dict[str, object]]:
    modes = ("h", "deep", "shallow")
    rows: List[Dict[str, object]] = []
    for rows_n, cols_n in [(16, 16), (24, 24), (32, 32)]:
        per: Dict[str, List[int]] = {mode: [] for mode in modes}
        paths: Dict[str, List[int]] = {mode: [] for mode in modes}
        for seed in range(TRIALS):
            maze = random_maze(rows_n, cols_n, 0.25, seed * 17 + 7)
            goal = (rows_n - 1, cols_n - 1)
            for mode in modes:
                res = p1.search((0, 0), goal, maze, heuristic="manhattan", tie_break=mode)
                if res.stats.found:
                    per[mode].append(res.stats.expanded)
                    paths[mode].append(res.stats.path_length - 1)
        row: Dict[str, object] = {"size": f"{rows_n}x{rows_n}", "solved": len(per["h"])}
        for mode in modes:
            row[f"avg_expanded_{mode}"] = round(sum(per[mode]) / len(per[mode]), 1) if per[mode] else 0
            row[f"avg_steps_{mode}"] = round(sum(paths[mode]) / len(paths[mode]), 1) if paths[mode] else 0
        row["shallow_vs_deep_pct"] = (
            round(100 * (sum(per["shallow"]) / sum(per["deep"]) - 1), 1) if per["deep"] else 0
        )
        rows.append(row)
    return rows


def treasure_sensitivity() -> Dict[str, object]:
    matrix, _ = p4.distance_matrix()
    original = dict(p4.TREASURE_VALUE)
    rows: List[Dict[str, object]] = []
    for target in ("T2", "T3"):
        for value in range(1, 13):
            p4.TREASURE_VALUE[target] = value
            out = p4.solve_game(4, matrix=matrix)
            rows.append(
                {
                    "changed": target,
                    "new_value": value,
                    "H4_best_target": out["best_target"],
                    "H4_best_value": out["best_value"],
                    "H2_best_target": p4.solve_game(2, matrix=matrix)["best_target"],
                }
            )
        p4.TREASURE_VALUE.update(original)
    flips = {}
    for target in ("T2", "T3"):
        seq = [r for r in rows if r["changed"] == target]
        prev = None
        for r in seq:
            if prev is not None and r["H4_best_target"] != prev:
                flips[f"{target}_flip_at"] = r["new_value"]
            prev = r["H4_best_target"]
    return {"rows": rows, "flips": flips}


def plot_weighted(rows: List[Dict[str, object]]) -> str:
    plt = common.setup_plt()
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    xs = [r["weight"] for r in rows]
    ax.plot(xs, [r["avg_expanded"] for r in rows], marker="o", color="#1f77b4", label="平均扩展节点数")
    ax.set_xlabel("启发权重 w（h' = w x 曼哈顿距离）")
    ax.set_ylabel("平均扩展节点数")
    ax.set_title("加权 A*：解质量与搜索开销的权衡（16x16 随机迷宫）")
    ax.grid(alpha=0.3)
    ax2 = ax.twinx()
    ax2.plot(xs, [r["avg_suboptimality"] for r in rows], marker="s", color="#d62728", label="平均次优比")
    ax2.set_ylabel("平均次优比 cost / cost*")
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [l.get_label() for l in lines], fontsize=8)
    out = common.figure_path("fig6_weighted_astar.png")
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    ida_rows = ida_vs_astar()
    weighted_rows = weighted_astar()
    tie_rows = tie_break_experiment()
    sensitivity = treasure_sensitivity()
    common.save_json(
        "exp5_extensions.json",
        {
            "ida_vs_astar": ida_rows,
            "weighted_astar": weighted_rows,
            "tie_break": tie_rows,
            "treasure_sensitivity": sensitivity,
        },
    )
    common.save_csv("exp5_ida_vs_astar.csv", ida_rows)
    common.save_csv("exp5_weighted_astar.csv", weighted_rows)
    plot_weighted(weighted_rows)
    print(common.markdown_table(ida_rows, ["size", "solved", "astar_expanded", "astar_peak_states", "ida_generations", "ida_iterations", "ida_peak_path_states", "ida_gmap_states", "generations_ratio", "path_depth_over_astar_states", "cost_identical", "astar_ms", "ida_ms"]))
    print()
    print(common.markdown_table(weighted_rows, ["weight", "instances", "avg_expanded", "avg_cost", "avg_suboptimality", "worst_suboptimality", "optimal_rate"]))
    print()
    print(common.markdown_table(tie_rows, ["size", "solved", "avg_expanded_h", "avg_expanded_deep", "avg_expanded_shallow", "avg_steps_h", "shallow_vs_deep_pct"]))
    print()
    print(common.markdown_table(sensitivity["rows"], ["changed", "new_value", "H4_best_target", "H4_best_value", "H2_best_target"]))
    print("翻转阈值:", sensitivity["flips"])
