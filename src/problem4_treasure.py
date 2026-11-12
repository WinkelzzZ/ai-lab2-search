"""题目四：竞争环境下的宝藏分配（A* 距离矩阵 + Minimax / Alpha-Beta）。

状态 = (A 位置, B 位置, 剩余宝藏集合, Score_A, Score_B, 当前玩家)。
Gain(p, Ti) = V_i - d(p, Ti)，d 由 A* 预先算好的 6x6 代价矩阵查表得到。
到达搜索深度或宝藏取完时，评价值 U = Score_A - Score_B。
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from astar import Coord, Grid, astar, manhattan

MAP_CELLS: List[List[str]] = [
    ["A", "1", "1", "X", "2", "1", "T1"],
    ["1", "X", "6", "X", "1", "X", "1"],
    ["1", "1", "T2", "1", "1", "1", "1"],
    ["X", "1", "X", "8", "X", "1", "X"],
    ["1", "1", "1", "1", "T3", "1", "1"],
    ["1", "X", "9", "X", "1", "X", "1"],
    ["T4", "1", "1", "X", "1", "1", "B"],
]

TREASURE_VALUE: Dict[str, int] = {"T1": 9, "T2": 6, "T3": 7, "T4": 7}
POI_POSITIONS: Dict[str, Coord] = {
    "A": (0, 0),
    "B": (6, 6),
    "T1": (0, 6),
    "T2": (2, 2),
    "T3": (4, 4),
    "T4": (6, 0),
}
POI_ORDER: List[str] = ["A", "B", "T1", "T2", "T3", "T4"]
TREASURE_ORDER: List[str] = ["T1", "T2", "T3", "T4"]
INF = float("inf")


def enter_cost(cell: str) -> int:
    if cell == "X":
        return 0
    if cell in POI_POSITIONS:  # A、B、T 所在格代价为 1
        return 1
    return int(cell)


def build_grid() -> Grid:
    return Grid(MAP_CELLS, blocked="X", enter_cost=enter_cost)


# ---------------------------------------------------------------- 1. 距离矩阵

def distance_matrix(heuristic: str = "manhattan") -> Tuple[Dict[str, Dict[str, int]], List[dict]]:
    """用 A* 计算 A、B、T1..T4 两两之间的最小移动代价。"""
    grid = build_grid()
    h_name = "Manhattan" if heuristic == "manhattan" else "h=0 (Dijkstra)"
    matrix: Dict[str, Dict[str, int]] = {}
    runs: List[dict] = []
    for src in POI_ORDER:
        matrix[src] = {}
        for dst in POI_ORDER:
            if src == dst:
                matrix[src][dst] = 0
                continue
            goal = POI_POSITIONS[dst]
            if heuristic == "manhattan":
                h_fn = lambda pos, g=goal: manhattan(pos, g)
            else:
                h_fn = lambda pos: 0
            result = astar(
                grid,
                POI_POSITIONS[src],
                goal,
                h_fn,
                label=f"d({src},{dst})",
                heuristic_name=h_name,
            )
            matrix[src][dst] = int(result.cost) if result.found else -1
            runs.append({"src": src, "dst": dst, "cost": matrix[src][dst], **result.stats.as_dict()})
    return matrix, runs


def format_matrix(matrix: Dict[str, Dict[str, int]]) -> str:
    header = "     " + "  ".join(f"{name:>4}" for name in POI_ORDER)
    lines = [header]
    for src in POI_ORDER:
        row = "  ".join(f"{matrix[src][dst]:>4}" for dst in POI_ORDER)
        lines.append(f"{src:>4}  {row}")
    return "\n".join(lines)


# ---------------------------------------------------------------- 2. 博弈状态

@dataclass(frozen=True)
class GameState:
    pos_a: Coord
    pos_b: Coord
    remaining: Tuple[str, ...]
    score_a: int = 0
    score_b: int = 0

    @property
    def utility(self) -> int:
        return self.score_a - self.score_b

    def key(self, depth: int, maximizing: bool) -> Tuple:
        return (self.pos_a, self.pos_b, self.remaining, depth, maximizing)


def initial_state() -> GameState:
    return GameState(
        pos_a=POI_POSITIONS["A"],
        pos_b=POI_POSITIONS["B"],
        remaining=TREASURE_ORDER,
    )


def label_of(pos: Coord, player: str) -> str:
    """当前坐标在距离矩阵中的行名：未拿宝藏前是 A/B，拿过之后是所在宝藏格名。"""
    for name in TREASURE_ORDER:
        if POI_POSITIONS[name] == pos:
            return name
    return "A" if player == "A" else "B"


def gain(state: GameState, player: str, target: str, matrix) -> int:
    pos = state.pos_a if player == "A" else state.pos_b
    return TREASURE_VALUE[target] - matrix[label_of(pos, player)][target]


def apply_move(state: GameState, player: str, target: str, matrix) -> GameState:
    g = gain(state, player, target, matrix)
    pos = POI_POSITIONS[target]
    rest = tuple(t for t in state.remaining if t != target)
    if player == "A":
        return GameState(pos, state.pos_b, rest, state.score_a + g, state.score_b)
    return GameState(state.pos_a, pos, rest, state.score_a, state.score_b + g)


def ordered_moves(state: GameState, player: str, matrix, ordering: str, depth: int = 0) -> List[str]:
    """子节点访问顺序。

    natural：按 T1..T4 固定顺序；
    greedy：本方即时收益优先（A 取大、B 取小）；
    worst：与 greedy 相反；
    oracle：按子树真实博弈值排序（上帝视角，给出剪枝效率上界，本身要额外做完整搜索）。
    """
    moves = [t for t in TREASURE_ORDER if t in state.remaining]
    if ordering == "natural":
        return moves
    if ordering == "oracle":
        maximizing = player == "A"
        values = {
            target: _search(
                apply_move(state, player, target, matrix),
                depth - 1,
                -INF,
                INF,
                not maximizing,
                matrix,
                GameStats(method="oracle-sort"),
                False,
                "natural",
                None,
            )
            for target in moves
        }
        return sorted(moves, key=lambda t: values[t], reverse=maximizing)
    gains = {t: gain(state, player, t, matrix) for t in moves}
    reverse = (player == "A") == (ordering == "greedy")
    return sorted(moves, key=lambda t: gains[t], reverse=reverse)


# ---------------------------------------------------------------- 3. 搜索

@dataclass
class GameStats:
    method: str = "alpha-beta"
    ordering: str = "natural"
    depth: int = 0
    nodes_visited: int = 0
    leaves_evaluated: int = 0
    cutoffs: int = 0
    children_skipped: int = 0
    cache_hits: int = 0
    wall_time_ms: float = 0.0

    def as_dict(self) -> Dict[str, object]:
        return {
            "method": self.method,
            "ordering": self.ordering,
            "depth": self.depth,
            "nodes_visited": self.nodes_visited,
            "leaves_evaluated": self.leaves_evaluated,
            "cutoffs": self.cutoffs,
            "children_skipped": self.children_skipped,
            "cache_hits": self.cache_hits,
            "wall_time_ms": round(self.wall_time_ms, 4),
        }


def _search(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    matrix,
    stats: GameStats,
    use_alpha: bool,
    ordering: str,
    cache: Optional[Dict[Tuple, int]],
) -> int:
    stats.nodes_visited += 1
    if depth == 0 or not state.remaining:
        stats.leaves_evaluated += 1
        return state.utility

    key = state.key(depth, maximizing)
    base = state.utility
    if cache is not None and key in cache:
        stats.cache_hits += 1
        return base + cache[key]

    player = "A" if maximizing else "B"
    moves = ordered_moves(state, player, matrix, ordering, depth)
    best = -INF if maximizing else INF
    last_index = -1
    cutoff = False
    for index, target in enumerate(moves):
        last_index = index
        child = apply_move(state, player, target, matrix)
        value = _search(
            child,
            depth - 1,
            alpha,
            beta,
            not maximizing,
            matrix,
            stats,
            use_alpha,
            ordering,
            cache,
        )
        if maximizing:
            best = max(best, value)
            if use_alpha:
                alpha = max(alpha, best)
        else:
            best = min(best, value)
            if use_alpha:
                beta = min(beta, best)
        if use_alpha and alpha >= beta:
            cutoff = True
            break

    if cutoff:
        stats.cutoffs += 1
        stats.children_skipped += len(moves) - 1 - last_index
    if cache is not None:
        cache[key] = int(best) - base
    return int(best)


def _root_children(state: GameState, matrix, ordering: str, depth: int) -> List[str]:
    return ordered_moves(state, "A", matrix, ordering, depth)


def solve_game(
    depth: int,
    method: str = "alpha-beta",
    ordering: str = "natural",
    use_cache: bool = False,
    matrix=None,
) -> Dict[str, object]:
    """返回 A 的最优首步与最优收益差，形如 {"best_target": "T2", "best_value": -1}。"""
    if matrix is None:
        matrix, _ = distance_matrix()
    stats = GameStats(method=method, ordering=ordering, depth=depth)
    cache: Optional[Dict[Tuple, int]] = {} if use_cache else None
    state = initial_state()
    t0 = time.perf_counter()
    best_target, best_value = None, -INF
    alpha, beta = -INF, INF
    for target in _root_children(state, matrix, ordering, depth):
        child = apply_move(state, "A", target, matrix)
        value = _search(
            child,
            depth - 1,
            alpha,
            beta,
            False,
            matrix,
            stats,
            method == "alpha-beta",
            ordering,
            cache,
        )
        if value > best_value:
            best_value, best_target = value, target
        if method == "alpha-beta":
            alpha = max(alpha, best_value)
    stats.wall_time_ms = (time.perf_counter() - t0) * 1000
    return {
        "best_target": best_target,
        "best_value": int(best_value),
        "H": depth,
        "stats": stats.as_dict(),
        "root_move_values": root_move_values(depth, method, ordering, matrix),
    }


def root_move_values(
    depth: int, method: str = "alpha-beta", ordering: str = "natural", matrix=None
) -> Dict[str, int]:
    """逐个计算 A 每个首步的博弈值（开区间，不剪枝窗口），用于报告中的决策对比表。"""
    if matrix is None:
        matrix, _ = distance_matrix()
    state = initial_state()
    values: Dict[str, int] = {}
    for target in TREASURE_ORDER:
        child = apply_move(state, "A", target, matrix)
        values[target] = _search(
            child,
            depth - 1,
            -INF,
            INF,
            False,
            matrix,
            GameStats(method=method, ordering=ordering, depth=depth),
            method == "alpha-beta",
            ordering,
            None,
        )
    return values


def principal_variation(depth: int, matrix=None) -> List[Tuple[str, str, int]]:
    """最优应对序列：每层重新做完整 Minimax，避免剪枝把 PV 兄弟分支藏起来。"""
    if matrix is None:
        matrix, _ = distance_matrix()
    sequence: List[Tuple[str, str, int]] = []
    state = initial_state()
    maximizing = True
    for remaining_depth in range(depth, 0, -1):
        player = "A" if maximizing else "B"
        scores = {
            target: _search(
                apply_move(state, player, target, matrix),
                remaining_depth - 1,
                -INF,
                INF,
                not maximizing,
                matrix,
                GameStats(method="minimax"),
                False,
                "natural",
                None,
            )
            for target in state.remaining
        }
        best = (max if maximizing else min)(scores, key=scores.get)
        sequence.append((player, best, int(scores[best])))
        state = apply_move(state, player, best, matrix)
        maximizing = not maximizing
    return sequence


if __name__ == "__main__":
    matrix, runs = distance_matrix()
    print(format_matrix(matrix))
    for h in (2, 4):
        out = solve_game(h)
        print(
            f'H={h} => {{"best_target": {json.dumps(out["best_target"])}, '
            f'"best_value": {out["best_value"]}}}  nodes={out["stats"]["nodes_visited"]}'
        )
