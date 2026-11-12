"""题目一：迷宫寻路（无权四邻域 A*）。

网格字符：'S' 起点、'E' 终点、'.' 通路、'X' 障碍。每移动一格 g-cost 为 1，
因此曼哈顿距离 h(n)=|Δrow|+|Δcol| 既可采纳又一致（consistent）。
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from astar import AStarResult, Coord, Grid, astar, manhattan

HEURISTICS: Dict[str, str] = {"zero": "h=0 (Dijkstra)", "manhattan": "Manhattan"}


def build_grid(map_cells: List[List[str]]) -> Grid:
    return Grid(map_cells, blocked="X")


def make_heuristic(goal: Coord, name: str = "manhattan"):
    if name == "zero":
        return lambda pos: 0, "h=0 (Dijkstra)"
    if name == "manhattan":
        return (lambda pos: manhattan(pos, goal)), "Manhattan"
    raise ValueError(f"unknown heuristic: {name}")


def search(
    start: Coord,
    goal: Coord,
    map_cells: List[List[str]],
    heuristic: str = "manhattan",
    tie_break: str = "h",
    label: str = "maze",
) -> AStarResult:
    h_fn, h_name = make_heuristic(goal, heuristic)
    grid = build_grid(map_cells)
    return astar(
        grid,
        start,
        goal,
        h_fn,
        label=label,
        heuristic_name=h_name,
        tie_break=tie_break,
    )


def solve_maze(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    map_cells: List[List[str]],
    heuristic: str = "manhattan",
) -> List[Tuple[int, int]]:
    """按题目要求的接口返回最短路径坐标序列；无解返回 []。"""
    return search(start, goal, map_cells, heuristic=heuristic).path


def solve_maze_with_stats(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    map_cells: List[List[str]],
    heuristic: str = "manhattan",
    tie_break: str = "h",
    label: str = "maze",
) -> Tuple[List[Tuple[int, int]], int, Dict[str, object]]:
    result = search(start, goal, map_cells, heuristic, tie_break, label)
    return result.path, len(result.path) - 1, result.stats.as_dict()


TEST_START: Coord = (0, 0)
TEST_GOAL: Coord = (3, 4)
TEST_MAP: List[List[str]] = [
    ["S", ".", ".", "X", "."],
    [".", "X", ".", ".", "."],
    [".", "X", ".", "X", "."],
    [".", ".", ".", "X", "E"],
    ["X", "X", ".", ".", "."],
]
EXPECTED_PATH = [
    (0, 0),
    (0, 1),
    (0, 2),
    (1, 2),
    (1, 3),
    (1, 4),
    (2, 4),
    (3, 4),
]

NO_PATH_MAP: List[List[str]] = [
    ["S", ".", "X", ".", "."],
    ["X", "X", "X", ".", "X"],
    [".", ".", ".", ".", "."],
    [".", "X", "X", "X", "E"],
]


def _path_is_valid(path: List[Coord], goal: Coord, map_cells: List[List[str]]) -> bool:
    """校验路径逐步相邻、不穿墙、终点正确（用于测试与实验自检）。"""
    if not path or path[-1] != goal:
        return False
    for a, b in zip(path, path[1:]):
        if manhattan(a, b) != 1:
            return False
        if map_cells[b[0]][b[1]] == "X":
            return False
    return map_cells[path[0][0]][path[0][1]] != "X"


if __name__ == "__main__":
    path = solve_maze(TEST_START, TEST_GOAL, TEST_MAP)
    print("输入: start=%s goal=%s" % (TEST_START, TEST_GOAL))
    print("输出:", path)
    print("与预期一致(同长度最短路径):", len(path) == len(EXPECTED_PATH))
    print("无解用例输出:", solve_maze((0, 0), (3, 4), NO_PATH_MAP))
