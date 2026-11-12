"""实验三：Minimax 与 Alpha-Beta —— 剪枝轨迹、访问顺序对剪枝效率的影响。"""

from __future__ import annotations

import copy
import random
from typing import Dict, List

import common
import problem3_alphabeta as p3
from problem3_alphabeta import TreeStats

CONFIGS = [(3, 3), (3, 4), (4, 3), (4, 4)]
TRIALS = 25


def official_case() -> Dict[str, object]:
    root = p3.build_test_tree()
    total_nodes, total_leaves = p3.count_tree(root)
    mm_stats = TreeStats(method="minimax", total_nodes=total_nodes, total_leaves=total_leaves)
    ab_stats = TreeStats(method="alpha-beta", total_nodes=total_nodes, total_leaves=total_leaves)
    trace: List[dict] = []
    mm_value = p3.minimax(root, stats=mm_stats)
    ab_value = p3.alphabeta(root, stats=ab_stats, trace=trace)
    return {
        "tree": {"total_nodes": total_nodes, "total_leaves": total_leaves},
        "minimax": {"value": mm_value, **mm_stats.as_dict()},
        "alpha_beta": {"value": ab_value, **ab_stats.as_dict()},
        "trace": trace,
        "json_input_value": p3.minimax(p3.build_from_dict(p3.TEST_JSON)),
    }


def ordering_experiment() -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for depth, branching in CONFIGS:
        samples = {"minimax": [], "ab_natural": [], "ab_best_first": [], "ab_worst_first": []}
        agree = 0
        for seed in range(TRIALS):
            rng = random.Random(seed)
            base = p3.random_tree(depth, branching, rng)
            total_leaves = p3.count_tree(base)[1]

            stats = TreeStats(method="minimax")
            mm_value = p3.minimax(base, stats=stats)
            samples["minimax"].append(stats.leaves_evaluated)
            found_values = [mm_value]

            for label, tree in (
                ("ab_natural", copy.deepcopy(base)),
                ("ab_best_first", p3.sort_by_minimax(copy.deepcopy(base))),
                ("ab_worst_first", p3.sort_reversed_minimax(copy.deepcopy(base))),
            ):
                stats = TreeStats(method="alpha-beta")
                found_values.append(p3.alphabeta(tree, stats=stats))
                samples[label].append(stats.leaves_evaluated)
            agree += len(set(found_values)) == 1

        ideal = (
            2 * branching ** (depth // 2) - 1
            if depth % 2 == 0
            else branching ** ((depth + 1) // 2) + branching ** ((depth - 1) // 2) - 1
        )  # 完美排序下 alpha-beta 的叶子数理论下界
        rows.append(
            {
                "depth": depth,
                "branching": branching,
                "total_leaves": total_leaves,
                "minimax_leaves": round(sum(samples["minimax"]) / TRIALS, 2),
                "ab_natural_leaves": round(sum(samples["ab_natural"]) / TRIALS, 2),
                "ab_best_first_leaves": round(sum(samples["ab_best_first"]) / TRIALS, 2),
                "ab_worst_first_leaves": round(sum(samples["ab_worst_first"]) / TRIALS, 2),
                "perfect_order_theory": ideal,
                "saving_natural_pct": round(
                    100 * (1 - sum(samples["ab_natural"]) / sum(samples["minimax"])), 1
                ),
                "saving_best_pct": round(
                    100 * (1 - sum(samples["ab_best_first"]) / sum(samples["minimax"])), 1
                ),
                "saving_worst_pct": round(
                    100 * (1 - sum(samples["ab_worst_first"]) / sum(samples["minimax"])), 1
                ),
                "values_agree": f"{agree}/{TRIALS}",
            }
        )
    return rows


def plot_ordering(rows: List[Dict[str, object]]) -> str:
    plt = common.setup_plt()
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    labels = ["minimax_leaves", "ab_natural_leaves", "ab_best_first_leaves", "ab_worst_first_leaves"]
    names = ["Minimax 全遍历", "Alpha-Beta 原顺序", "Alpha-Beta 理想顺序", "Alpha-Beta 最坏顺序"]
    x = range(len(rows))
    width = 0.2
    for offset, (label, name) in enumerate(zip(labels, names)):
        ax.bar([i + (offset - 1.5) * width for i in x], [row[label] for row in rows], width, label=name)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"d={r['depth']}, b={r['branching']}\n(共 {r['total_leaves']} 叶)" for r in rows])
    ax.set_ylabel("平均求值的叶子数")
    ax.set_title(f"访问顺序对 Alpha-Beta 剪枝效率的影响（{TRIALS} 个随机树平均）")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    out = common.figure_path("fig4_alphabeta_ordering.png")
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    official = official_case()
    rows = ordering_experiment()
    common.save_json("exp3_alphabeta.json", {"official": official, "ordering": rows})
    common.save_csv("exp3_alphabeta_ordering.csv", rows)
    plot_ordering(rows)
    print("官方树 minimax:", official["minimax"])
    print("官方树 alpha-beta:", official["alpha_beta"])
    print()
    print(common.markdown_table(
        rows,
        ["depth", "branching", "total_leaves", "minimax_leaves", "ab_natural_leaves",
         "ab_best_first_leaves", "ab_worst_first_leaves", "perfect_order_theory",
         "saving_natural_pct", "saving_best_pct", "values_agree"],
    ))
