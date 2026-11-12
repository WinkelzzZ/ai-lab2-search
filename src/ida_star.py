"""拓展实验用：IDA*（迭代加深 A*）。

与 A* 的对照点：open/closed 表不再常驻内存，代价是同一路径片段会被反复生成。
用于报告里“内存-时间权衡”的证据。
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from astar import Coord, Grid, manhattan

FOUND = object()


@dataclass
class IDAResult:
    path: List[Coord]
    cost: float
    iterations: int
    generations: int
    peak_depth: int
    max_memory_states: int
    wall_time_ms: float

    def as_dict(self) -> Dict[str, object]:
        return {
            "iterations": self.iterations,
            "generations": self.generations,
            "peak_depth": self.peak_depth,
            "max_memory_states": self.max_memory_states,
            "path_cost": self.cost,
            "path_length": len(self.path),
            "found": bool(self.path),
            "wall_time_ms": round(self.wall_time_ms, 4),
        }


def ida_star(grid: Grid, start: Coord, goal: Coord, heuristic: Callable[[Coord], int]) -> IDAResult:
    t0 = time.perf_counter()
    threshold = heuristic(start)
    iterations = 0
    generations = 0
    peak_depth = 0
    best_g: Dict[Coord, int] = {start: 0}
    result_path: List[Coord] = []

    def search(path: List[Coord], g_cost: int, threshold: float) -> float:
        nonlocal generations, peak_depth, result_path
        generations += 1
        peak_depth = max(peak_depth, len(path))
        current = path[-1]
        f = g_cost + heuristic(current)
        if f > threshold:
            return f
        if current == goal:
            result_path = list(path)
            return FOUND  # type: ignore[return-value]
        min_next = float("inf")
        for nxt in grid.neighbors(current):
            step = grid.enter_cost(nxt)
            tentative = g_cost + step
            if tentative >= best_g.get(nxt, float("inf")):
                continue
            best_g[nxt] = tentative
            path.append(nxt)
            t = search(path, tentative, threshold)
            path.pop()
            if t is FOUND:
                return FOUND  # type: ignore[return-value]
            if t < min_next:
                min_next = t
        return min_next

    while True:
        iterations += 1
        best_g = {start: 0}
        t = search([start], 0, threshold)
        if t is FOUND:
            break
        if t == float("inf"):
            threshold = float("inf")
            break
        threshold = t
        if iterations > 200:
            break

    cost = _path_cost(grid, result_path) if result_path else -1
    return IDAResult(
        path=result_path,
        cost=cost,
        iterations=iterations,
        generations=generations,
        peak_depth=peak_depth,
        max_memory_states=len(best_g),
        wall_time_ms=(time.perf_counter() - t0) * 1000,
    )


def _path_cost(grid: Grid, path: List[Coord]) -> int:
    return sum(grid.enter_cost(pos) for pos in path[1:])


def weighted_heuristic(goal: Coord, weight: float, unit_cost: int = 1):
    return lambda pos: int(weight * manhattan(pos, goal) * unit_cost)
