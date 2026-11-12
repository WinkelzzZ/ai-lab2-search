"""题目三：极大极小博弈树 + Alpha-Beta 剪枝。

叶子节点存 value，内部节点存 children；根为 MAX，层深奇偶决定玩家（偶数层 MAX、奇数层 MIN）。
若节点带有 is_maximizing_player 标记（JSON 输入），则优先使用标记。
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

INF = float("inf")


class TreeNode:
    def __init__(self, value=None, children=None):
        self.value = value  # 叶子节点的得分
        self.children = children if children is not None else []  # 子节点列表
        self.is_max: Optional[bool] = None  # 仅 JSON 构造时写入

    @property
    def is_leaf(self) -> bool:
        return not self.children

    def height(self) -> int:
        if self.is_leaf:
            return 0
        return 1 + max(child.height() for child in self.children)


@dataclass
class TreeStats:
    method: str = ""
    nodes_visited: int = 0        # 进入过函数的节点总数
    leaves_evaluated: int = 0     # 读取叶子价值的次数
    internal_visited: int = 0
    cutoffs: int = 0              # 发生 alpha/beta 剪枝的节点数
    children_skipped: int = 0     # 因剪枝未进入的子节点数
    leaves_skipped: int = 0       # 因剪枝未读取的叶子数（按子树规模估计）
    total_leaves: int = 0
    total_nodes: int = 0

    def as_dict(self) -> Dict[str, object]:
        ratio = (
            round(self.leaves_skipped / self.total_leaves, 4) if self.total_leaves else 0.0
        )
        return {
            "method": self.method,
            "nodes_visited": self.nodes_visited,
            "leaves_evaluated": self.leaves_evaluated,
            "internal_visited": self.internal_visited,
            "cutoffs": self.cutoffs,
            "children_skipped": self.children_skipped,
            "leaves_skipped": self.leaves_skipped,
            "total_leaves": self.total_leaves,
            "total_nodes": self.total_nodes,
            "leaf_skip_ratio": ratio,
        }


def count_tree(node: TreeNode) -> Tuple[int, int]:
    nodes, leaves = 0, 0
    stack = [node]
    while stack:
        cur = stack.pop()
        nodes += 1
        if cur.is_leaf:
            leaves += 1
        else:
            stack.extend(cur.children)
    return nodes, leaves


def _leaf_count(node: TreeNode) -> int:
    if node.is_leaf:
        return 1
    return sum(_leaf_count(child) for child in node.children)


def _is_max_node(node: TreeNode, depth: int) -> bool:
    if node.is_max is not None:
        return node.is_max
    return depth % 2 == 0


# ---------------------------------------------------------------- 基础搜索

def minimax(node: TreeNode, depth: int = 0, stats: Optional[TreeStats] = None) -> int:
    stats = stats if stats is not None else TreeStats(method="minimax")
    stats.nodes_visited += 1
    if node.is_leaf:
        stats.leaves_evaluated += 1
        return node.value
    stats.internal_visited += 1
    values = [minimax(child, depth + 1, stats) for child in node.children]
    return max(values) if _is_max_node(node, depth) else min(values)


def alphabeta(
    node: TreeNode,
    alpha: float = -INF,
    beta: float = INF,
    depth: int = 0,
    stats: Optional[TreeStats] = None,
    trace: Optional[List[dict]] = None,
    path: str = "root",
) -> int:
    stats = stats if stats is not None else TreeStats(method="alpha-beta")
    stats.nodes_visited += 1
    if node.is_leaf:
        stats.leaves_evaluated += 1
        if trace is not None:
            trace.append(
                {"path": path, "depth": depth, "kind": "leaf", "value": node.value,
                 "alpha": _num(alpha), "beta": _num(beta)}
            )
        return node.value
    stats.internal_visited += 1

    maximizing = _is_max_node(node, depth)
    best = -INF if maximizing else INF
    last_index = -1
    pruned_here = False
    for index, child in enumerate(node.children):
        last_index = index
        child_path = f"{path}.{index}"
        value = alphabeta(
            child, alpha, beta, depth + 1, stats, trace, child_path
        )
        if maximizing:
            best = max(best, value)
            alpha = max(alpha, best)
        else:
            best = min(best, value)
            beta = min(beta, best)
        if trace is not None:
            trace.append(
                {
                    "path": child_path,
                    "depth": depth + 1,
                    "kind": "return",
                    "parent": "MAX" if maximizing else "MIN",
                    "value": value,
                    "alpha": _num(alpha),
                    "beta": _num(beta),
                    "cut": alpha >= beta,
                }
            )
        if alpha >= beta:
            pruned_here = True
            break

    if pruned_here:
        stats.cutoffs += 1
        skipped_children = len(node.children) - 1 - last_index
        stats.children_skipped += skipped_children
        stats.leaves_skipped += sum(
            _leaf_count(c) for c in node.children[last_index + 1 :]
        )
    return int(best)


def _num(x: float) -> object:
    if x == INF:
        return "+inf"
    if x == -INF:
        return "-inf"
    return int(x)


def solve(root: TreeNode, stats: Optional[TreeStats] = None) -> int:
    """题目要求的接口：给定根节点，返回 MAX 玩家的最佳结果。"""
    if stats is None:
        return alphabeta(root)
    return alphabeta(root, stats=stats)


# ---------------------------------------------------------------- 输入构造

def build_from_dict(data: Dict[str, object]) -> TreeNode:
    """把题目三 JSON（tree_structure / is_maximizing_player / value / children）转成 TreeNode。"""
    if "tree_structure" in data:
        data = data["tree_structure"]  # type: ignore[assignment]

    def rec(node: Dict[str, object]) -> TreeNode:
        if "value" in node and node["value"] is not None:
            return TreeNode(value=int(node["value"]))
        children = [rec(child) for child in node.get("children", [])]  # type: ignore[arg-type]
        tree_node = TreeNode(children=children)
        if "is_maximizing_player" in node:
            tree_node.is_max = bool(node["is_maximizing_player"])
        return tree_node

    return rec(data)


def build_test_tree() -> TreeNode:
    """PDF 第 12 页给出的构建代码示例。"""
    leaf1, leaf2 = TreeNode(value=3), TreeNode(value=5)
    leaf3, leaf4 = TreeNode(value=6), TreeNode(value=9)
    leaf5, leaf6 = TreeNode(value=1), TreeNode(value=2)
    max1 = TreeNode(children=[leaf1, leaf2])
    max2 = TreeNode(children=[leaf3, leaf4])
    max3 = TreeNode(children=[leaf5, leaf6])
    min1 = TreeNode(children=[max1, max2])
    min2 = TreeNode(children=[max2, max3])
    return TreeNode(children=[min1, min2])


TEST_JSON: Dict[str, object] = {
    "tree_structure": {
        "is_maximizing_player": True,
        "children": [
            {
                "is_maximizing_player": False,
                "children": [
                    {
                        "is_maximizing_player": True,
                        "children": [{"value": 3}, {"value": 5}],
                    },
                    {
                        "is_maximizing_player": True,
                        "children": [{"value": 6}, {"value": 9}],
                    },
                ],
            },
            {
                "is_maximizing_player": False,
                "children": [
                    {
                        "is_maximizing_player": True,
                        "children": [{"value": 6}, {"value": 9}],
                    },
                    {
                        "is_maximizing_player": True,
                        "children": [{"value": 1}, {"value": 2}],
                    },
                ],
            },
        ],
    }
}


def random_tree(depth: int, branching: int, rng: random.Random) -> TreeNode:
    if depth == 0:
        return TreeNode(value=rng.randint(0, 99))
    return TreeNode(
        children=[random_tree(depth - 1, branching, rng) for _ in range(branching)]
    )


def _sorted_tree(node: TreeNode, best_first: bool = True) -> TreeNode:
    """按子树真实 minimax 值重排 children（上帝视角）。

    best_first=True：MAX 层把大值放前、MIN 层把小值放前（剪枝最多的理想顺序）；
    best_first=False：完全反过来，得到剪枝最少的顺序。
    排序时按“该子节点所在层的真实玩家”求值，避免把 MIN 层子节点误当成 MAX 层。
    """

    def rec(cur: TreeNode, cur_is_max: bool) -> None:
        for child in cur.children:
            rec(child, not cur_is_max)
        child_is_max = not cur_is_max
        if cur.is_leaf:
            return
        cur.children.sort(
            key=lambda c: minimax(c, depth=0 if child_is_max else 1),
            reverse=(cur_is_max == best_first),
        )

    rec(node, True)
    return node


def sort_by_minimax(node: TreeNode) -> TreeNode:
    return _sorted_tree(node, best_first=True)


def sort_reversed_minimax(node: TreeNode) -> TreeNode:
    return _sorted_tree(node, best_first=False)


if __name__ == "__main__":
    root = build_test_tree()
    total_nodes, total_leaves = count_tree(root)
    mm_stats = TreeStats(method="minimax", total_nodes=total_nodes, total_leaves=total_leaves)
    ab_stats = TreeStats(method="alpha-beta", total_nodes=total_nodes, total_leaves=total_leaves)
    print("Minimax   :", minimax(root, stats=mm_stats), mm_stats.as_dict())
    print("Alpha-Beta:", solve(root, ab_stats), ab_stats.as_dict())
    print("JSON 构造 :", minimax(build_from_dict(TEST_JSON)))
