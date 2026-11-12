"""题目二：加权地形 A*。

单元格为数字（进入代价）、'S'/'E'/'X'。规则：从 A 到相邻 B 的代价等于进入 B 的权值，
且按题面说明终点 E 的进入代价记为 0（“最后一步没有代价”）。

启发函数三种：
  zero        h=0，退化为 Dijkstra，一定最优；
  manhattan   h=曼哈顿距离×最小格代价，忽略“终点免费”，最多高估 1 个最小代价，严格说不可采纳；
  manhattan_free  h=max(0,(曼哈顿距离-1)×最小格代价)，把终点免费计入，可采纳。
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from astar import AStarResult, Coord, Grid, astar, manhattan

SPECIAL_ENTER_COST = {"S": 1, "E": 0, "X": 0}


def enter_cost(cell: str) -> int:
    if cell in SPECIAL_ENTER_COST:
        return SPECIAL_ENTER_COST[cell]
    return int(cell)


def build_grid(map_cells: List[List[str]]) -> Grid:
    return Grid(map_cells, blocked="X", enter_cost=enter_cost)


def make_heuristic(grid: Grid, goal: Coord, name: str):
    c_min = grid.min_step_cost(exclude=(goal,))
    if name == "zero":
        return (lambda pos: 0), "h=0 (Dijkstra)", c_min
    if name == "manhattan":
        return (lambda pos: manhattan(pos, goal) * c_min), "Manhattan x c_min", c_min
    if name == "manhattan_free":
        return (
            lambda pos: max(0, manhattan(pos, goal) - 1) * c_min,
            "Manhattan(free-goal) x c_min",
            c_min,
        )
    raise ValueError(f"unknown heuristic: {name}")


def search(
    start: Coord,
    goal: Coord,
    map_cells: List[List[str]],
    heuristic: str = "manhattan_free",
    tie_break: str = "h",
    label: str = "terrain",
) -> AStarResult:
    grid = build_grid(map_cells)
    h_fn, h_name, _c_min = make_heuristic(grid, goal, heuristic)
    return astar(
        grid, start, goal, h_fn, label=label, heuristic_name=h_name, tie_break=tie_break
    )


def solve_terrain(
    start: Tuple[int, int],
    goal: Tuple[int, int],
    map_cells: List[List[str]],
    heuristic: str = "manhattan_free",
) -> int:
    """按题目要求返回最小总代价；无解返回 -1。"""
    return search(start, goal, map_cells, heuristic=heuristic).cost


def path_cost_breakdown(result: AStarResult, map_cells: List[List[str]]) -> List[Dict[str, object]]:
    """逐步列出进入坐标、该格代价与累计代价，用于报告中的代价累计表。"""
    rows: List[Dict[str, object]] = []
    total = 0
    for i, (r, c) in enumerate(result.path):
        step = 0 if i == 0 else enter_cost(map_cells[r][c])
        total += step
        rows.append(
            {
                "step": i,
                "pos": (r, c),
                "cell": map_cells[r][c],
                "step_cost": step,
                "g": total,
                "h": manhattan((r, c), result.path[-1]),
            }
        )
    return rows


TEST_START: Coord = (0, 0)
TEST_GOAL: Coord = (4, 4)
TEST_MAP: List[List[str]] = [
    ["S", "1", "1", "8", "1"],
    ["1", "8", "3", "1", "1"],
    ["1", "8", "1", "8", "1"],
    ["1", "1", "1", "8", "1"],
    ["8", "8", "1", "1", "E"],
]
EXPECTED_COST = 7
EXPECTED_PATH = [
    (0, 0),
    (1, 0),
    (2, 0),
    (3, 0),
    (3, 1),
    (3, 2),
    (4, 2),
    (4, 3),
    (4, 4),
]

NO_PATH_MAP: List[List[str]] = [
    ["S", "1", "X", "1"],
    ["1", "X", "X", "1"],
    ["1", "X", "1", "1"],
    ["X", "X", "1", "E"],
]

if __name__ == "__main__":
    for name in ("zero", "manhattan", "manhattan_free"):
        res = search(TEST_START, TEST_GOAL, TEST_MAP, heuristic=name)
        print(
            f"{name:15s} cost={res.cost} expanded={res.stats.expanded} "
            f"generated={res.stats.generated} path={res.path}"
        )
    print("无解用例:", solve_terrain((0, 0), (3, 3), NO_PATH_MAP))
