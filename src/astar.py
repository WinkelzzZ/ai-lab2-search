"""通用 A* 搜索内核（题目一 / 题目二 / 题目四共用）。

状态 = 网格坐标 (row, col)；f(n) = g(n) + h(n)；open 表用最小堆维护。
代价函数与启发函数以回调注入，因此四邻域无权迷宫和加权地形只是两组不同参数。
"""

from __future__ import annotations

import heapq
import itertools
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

Coord = Tuple[int, int]
CostFn = Callable[[Coord, Coord], int]
HeurFn = Callable[[Coord], int]

# 上下左右四方向，顺序固定为 上/下/左/右，保证结果可复现
NEIGHBORS_4: Tuple[Tuple[int, int], ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))


@dataclass
class SearchStats:
    """一次搜索的过程指标，供实验报告统计使用。"""

    label: str = ""
    heuristic: str = ""
    expanded: int = 0        # 从 open 表取出并进入 closed 表的节点数
    generated: int = 0       # 入队次数（含更优路径的重新入队）
    popped_stale: int = 0    # 弹出时已在 closed 表中的废弃条目数
    max_frontier: int = 0    # open 表历史最大长度
    path_cost: float = -1    # 解代价，-1 表示无解
    path_length: int = 0     # 解路径上的坐标个数
    found: bool = False
    wall_time_ms: float = 0.0

    def as_dict(self) -> Dict[str, object]:
        return {
            "label": self.label,
            "heuristic": self.heuristic,
            "expanded": self.expanded,
            "generated": self.generated,
            "popped_stale": self.popped_stale,
            "max_frontier": self.max_frontier,
            "path_cost": self.path_cost,
            "path_length": self.path_length,
            "found": self.found,
            "wall_time_ms": round(self.wall_time_ms, 4),
        }


@dataclass
class AStarResult:
    path: List[Coord]
    cost: float
    stats: SearchStats

    @property
    def found(self) -> bool:
        return self.stats.found


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Grid:
    """把二维字符/数字表封装成带可通行性和进入代价的地图。"""

    def __init__(
        self,
        cells: Sequence[Sequence[object]],
        blocked: str = "X",
        enter_cost: Callable[[object], int] = None,
    ) -> None:
        self.cells = [[str(v).strip() for v in row] for row in cells]
        self.rows = len(self.cells)
        self.cols = len(self.cells[0]) if self.rows else 0
        self.blocked = blocked
        self._enter_cost = enter_cost or (lambda v: 1)

    def in_bounds(self, pos: Coord) -> bool:
        return 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols

    def passable(self, pos: Coord) -> bool:
        return self.in_bounds(pos) and self.cells[pos[0]][pos[1]] != self.blocked

    def enter_cost(self, pos: Coord) -> int:
        v = self.cells[pos[0]][pos[1]]
        return self._enter_cost(v)

    def neighbors(self, pos: Coord) -> List[Coord]:
        return [
            (pos[0] + dr, pos[1] + dc)
            for dr, dc in NEIGHBORS_4
            if self.passable((pos[0] + dr, pos[1] + dc))
        ]

    def min_step_cost(self, exclude: Tuple[Coord, ...] = ()) -> int:
        costs = [
            self.enter_cost((r, c))
            for r in range(self.rows)
            for c in range(self.cols)
            if self.passable((r, c)) and (r, c) not in exclude
        ]
        return min(costs) if costs else 1


def astar(
    grid: Grid,
    start: Coord,
    goal: Coord,
    heuristic: HeurFn,
    *,
    label: str = "",
    heuristic_name: str = "h",
    tie_break: str = "h",
    cost_fn: Optional[CostFn] = None,
) -> AStarResult:
    """A* 主循环。

    tie_break（f 相同时的第二关键字，升序取队首）:
      - "h": 取 h 小的，等价于优先更深的节点
      - "deep"/"g": 取 g 大的（更先“一条路走到底”）
      - "shallow": 取 g 小的（更先靠近起点，广度倾向）
    cost_fn: 进入邻居的代价，默认取地图单元格代价。
    """
    if tie_break not in ("h", "g", "deep", "shallow"):
        raise ValueError(f"unknown tie_break: {tie_break}")
    stats = SearchStats(label=label, heuristic=heuristic_name)
    t0 = time.perf_counter()

    if not grid.passable(start) or not grid.passable(goal):
        stats.wall_time_ms = (time.perf_counter() - t0) * 1000
        return AStarResult([], -1, stats)

    step_cost = cost_fn or (lambda cur, nxt: grid.enter_cost(nxt))

    def tie_key(_g: int, h: int) -> int:
        if tie_break in ("g", "deep"):
            return -_g
        if tie_break == "shallow":
            return _g
        return h

    counter = itertools.count()
    g_score: Dict[Coord, int] = {start: 0}
    came_from: Dict[Coord, Coord] = {}
    closed: set[Coord] = set()

    h0 = heuristic(start)
    open_heap: List[Tuple[int, int, int, Coord]] = [
        (h0, tie_key(0, h0), next(counter), start)
    ]
    stats.generated = 1
    stats.max_frontier = 1

    while open_heap:
        f, _tie, _seq, current = heapq.heappop(open_heap)
        if current in closed:
            stats.popped_stale += 1
            continue
        closed.add(current)
        stats.expanded += 1

        if current == goal:
            path = _reconstruct(came_from, current)
            stats.path_cost = g_score[current]
            stats.path_length = len(path)
            stats.found = True
            stats.wall_time_ms = (time.perf_counter() - t0) * 1000
            return AStarResult(path, g_score[current], stats)

        for nxt in grid.neighbors(current):
            if nxt in closed:
                continue
            tentative_g = g_score[current] + step_cost(current, nxt)
            if tentative_g < g_score.get(nxt, float("inf")):
                g_score[nxt] = tentative_g
                came_from[nxt] = current
                h = heuristic(nxt)
                heapq.heappush(
                    open_heap, (tentative_g + h, tie_key(tentative_g, h), next(counter), nxt)
                )
                stats.generated += 1
                stats.max_frontier = max(stats.max_frontier, len(open_heap))

    stats.wall_time_ms = (time.perf_counter() - t0) * 1000
    return AStarResult([], -1, stats)


def _reconstruct(came_from: Dict[Coord, Coord], current: Coord) -> List[Coord]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def greedy_best_first(grid: Grid, start: Coord, goal: Coord, heuristic: HeurFn) -> AStarResult:
    """贪心最佳优先（只看 h）：用作报告里的对照组，说明不可采纳/不完备风险。"""
    stats = SearchStats(label="greedy", heuristic="h only")
    t0 = time.perf_counter()
    counter = itertools.count()
    open_heap = [(heuristic(start), next(counter), start)]
    came_from: Dict[Coord, Coord] = {}
    closed: set[Coord] = set()
    stats.generated = 1
    while open_heap:
        _h, _seq, current = heapq.heappop(open_heap)
        if current in closed:
            stats.popped_stale += 1
            continue
        closed.add(current)
        stats.expanded += 1
        if current == goal:
            path = _reconstruct(came_from, current)
            cost = sum(grid.enter_cost(p) for p in path[1:])
            stats.found = True
            stats.path_cost = cost
            stats.path_length = len(path)
            stats.max_frontier = max(stats.max_frontier, len(open_heap))
            stats.wall_time_ms = (time.perf_counter() - t0) * 1000
            return AStarResult(path, cost, stats)
        for nxt in grid.neighbors(current):
            if nxt in closed:
                continue
            came_from[nxt] = current
            heapq.heappush(open_heap, (heuristic(nxt), next(counter), nxt))
            stats.generated += 1
            stats.max_frontier = max(stats.max_frontier, len(open_heap))
    stats.wall_time_ms = (time.perf_counter() - t0) * 1000
    return AStarResult([], -1, stats)
