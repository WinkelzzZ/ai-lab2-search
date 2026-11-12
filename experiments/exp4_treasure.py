"""实验四：综合题 —— 距离矩阵、H=1..4 的决策差异、访问顺序与置换缓存。"""

from __future__ import annotations

from typing import Dict, List

import common
import problem4_treasure as p4


def matrix_experiment() -> Dict[str, object]:
    man_matrix, man_runs = p4.distance_matrix("manhattan")
    zero_matrix, zero_runs = p4.distance_matrix("zero")
    assert man_matrix == zero_matrix, "两种启发式的代价矩阵必须一致（可采纳性自检）"
    rows = [
        {
            "pair": man_run["label"],
            "cost": man_run["cost"],
            "manhattan_expanded": man_run["expanded"],
            "manhattan_generated": man_run["generated"],
            "dijkstra_expanded": zero_run["expanded"],
        }
        for man_run, zero_run in zip(man_runs, zero_runs)
    ]
    symmetric = all(man_matrix[a][b] == man_matrix[b][a] for a in p4.POI_ORDER for b in p4.POI_ORDER)
    triangle = all(
        man_matrix[a][b] + man_matrix[b][c] >= man_matrix[a][c]
        for a in p4.POI_ORDER
        for b in p4.POI_ORDER
        for c in p4.POI_ORDER
    )
    return {
        "matrix": man_matrix,
        "formatted": p4.format_matrix(man_matrix),
        "rows": rows,
        "symmetric": symmetric,
        "triangle_inequality": triangle,
        "total_expanded_manhattan": sum(r["manhattan_expanded"] for r in rows),
        "total_expanded_dijkstra": sum(r["dijkstra_expanded"] for r in rows),
    }


def gain_table(matrix) -> List[Dict[str, object]]:
    state = p4.initial_state()
    rows = []
    for target in p4.TREASURE_ORDER:
        rows.append(
            {
                "treasure": target,
                "pos": p4.POI_POSITIONS[target],
                "value": p4.TREASURE_VALUE[target],
                "d(A,Ti)": matrix["A"][target],
                "Gain_A": p4.gain(state, "A", target, matrix),
                "d(B,Ti)": matrix["B"][target],
                "Gain_B": p4.gain(state, "B", target, matrix),
            }
        )
    return rows


def horizon_experiment(matrix) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for depth in (1, 2, 3, 4):
        for method in ("minimax", "alpha-beta"):
            out = p4.solve_game(depth, method=method, matrix=matrix)
            stats = out["stats"]
            rows.append(
                {
                    "H": depth,
                    "method": method,
                    "best_target": out["best_target"],
                    "best_value": out["best_value"],
                    "nodes": stats["nodes_visited"],
                    "leaves": stats["leaves_evaluated"],
                    "cutoffs": stats["cutoffs"],
                    "children_skipped": stats["children_skipped"],
                    "time_ms": round(stats["wall_time_ms"], 3),
                    "root_values": out["root_move_values"],
                    "pv": p4.principal_variation(depth, matrix),
                }
            )
    return rows


def ordering_experiment(matrix) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    baseline = p4.solve_game(4, "minimax", "natural", False, matrix)
    rows.append(
        {
            "ordering": "natural",
            "cache": False,
            "best_target": baseline["best_target"],
            "best_value": baseline["best_value"],
            "nodes": baseline["stats"]["nodes_visited"],
            "leaves": baseline["stats"]["leaves_evaluated"],
            "cutoffs": baseline["stats"]["cutoffs"],
            "children_skipped": baseline["stats"]["children_skipped"],
            "cache_hits": 0,
            "time_ms": round(baseline["stats"]["wall_time_ms"], 3),
            "method": "minimax",
        },
    )
    for ordering in ("natural", "greedy", "worst", "oracle"):
        for use_cache in (False, True):
            out = p4.solve_game(4, "alpha-beta", ordering, use_cache, matrix)
            stats = out["stats"]
            rows.append(
                {
                    "ordering": ordering,
                    "cache": use_cache,
                    "best_target": out["best_target"],
                    "best_value": out["best_value"],
                    "nodes": stats["nodes_visited"],
                    "leaves": stats["leaves_evaluated"],
                    "cutoffs": stats["cutoffs"],
                    "children_skipped": stats["children_skipped"],
                    "cache_hits": stats["cache_hits"],
                    "time_ms": round(stats["wall_time_ms"], 3),
                    "method": "alpha-beta",
                }
            )
    return rows


def depth_saturation(matrix) -> List[Dict[str, object]]:
    """H=4 已能看满 4 个宝藏，H>4 的结果应与 H=4 完全一致（无更多可展开的回合）。"""
    rows: List[Dict[str, object]] = []
    for depth in (4, 5, 6, 8):
        out = p4.solve_game(depth, matrix=matrix)
        rows.append(
            {
                "H": depth,
                "best_target": out["best_target"],
                "best_value": out["best_value"],
                "nodes": out["stats"]["nodes_visited"],
                "leaves": out["stats"]["leaves_evaluated"],
            }
        )
    return rows


def plot_horizon(rows: List[Dict[str, object]]) -> str:
    plt = common.setup_plt()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    by_depth: Dict[int, Dict[str, Dict[str, object]]] = {}
    for row in rows:
        by_depth.setdefault(row["H"], {})[row["method"]] = row
    depths = sorted(by_depth)
    axes[0].plot(depths, [by_depth[d]["minimax"]["best_value"] for d in depths], marker="o", label="Minimax")
    axes[0].plot(depths, [by_depth[d]["alpha-beta"]["best_value"] for d in depths], marker="s", ls="--", label="Alpha-Beta")
    for d in depths:
        axes[0].annotate(
            f"首步 {by_depth[d]['minimax']['best_target']}",
            (d, by_depth[d]["minimax"]["best_value"]),
            textcoords="offset points",
            xytext=(6, -12),
            fontsize=8,
            color="#d62728",
        )
    axes[0].set_xlabel("搜索深度 H")
    axes[0].set_ylabel("A 的最优收益差 U")
    axes[0].set_title("视野长度对决策的影响")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(depths, [by_depth[d]["minimax"]["nodes"] for d in depths], marker="o", label="Minimax 节点数")
    axes[1].plot(depths, [by_depth[d]["alpha-beta"]["nodes"] for d in depths], marker="s", label="Alpha-Beta 节点数")
    axes[1].plot(depths, [by_depth[d]["alpha-beta"]["leaves"] for d in depths], marker="^", label="Alpha-Beta 叶子评估数")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("搜索深度 H")
    axes[1].set_ylabel("搜索节点数（对数轴）")
    axes[1].set_title("Minimax 与 Alpha-Beta 的搜索开销")
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=8)

    out = common.figure_path("fig5_treasure_horizon.png")
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    matrix_data = matrix_experiment()
    matrix = matrix_data["matrix"]
    gains = gain_table(matrix)
    horizon = horizon_experiment(matrix)
    ordering = ordering_experiment(matrix)
    saturation = depth_saturation(matrix)
    common.save_json(
        "exp4_treasure.json",
        {
            "matrix": matrix_data,
            "gains": gains,
            "horizon": horizon,
            "ordering": ordering,
            "saturation": saturation,
            "expected": {"H2": {"best_target": "T2", "best_value": -1}, "H4": {"best_target": "T3", "best_value": 3}},
        },
    )
    common.save_csv("exp4_treasure_ordering.csv", ordering)
    plot_horizon(horizon)
    print(matrix_data["formatted"])
    print("对称:", matrix_data["symmetric"], "三角不等式:", matrix_data["triangle_inequality"])
    print("总扩展节点 Manhattan:", matrix_data["total_expanded_manhattan"], "Dijkstra:", matrix_data["total_expanded_dijkstra"])
    print()
    print(common.markdown_table(gains, ["treasure", "pos", "value", "d(A,Ti)", "Gain_A", "d(B,Ti)", "Gain_B"]))
    print()
    print(common.markdown_table(horizon, ["H", "method", "best_target", "best_value", "nodes", "leaves", "cutoffs", "children_skipped", "root_values"]))
    print()
    for row in horizon:
        if row["method"] == "minimax":
            print(f"PV H={row['H']}: {row['pv']}")
    print()
    print(common.markdown_table(ordering, ["method", "ordering", "cache", "best_target", "best_value", "nodes", "leaves", "cutoffs", "children_skipped", "cache_hits"]))
    print()
    print(common.markdown_table(saturation, ["H", "best_target", "best_value", "nodes", "leaves"]))
