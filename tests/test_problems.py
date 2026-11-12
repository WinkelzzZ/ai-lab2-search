"""官方测试用例自检：python tests/test_problems.py（也兼容 pytest）。"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import problem1_maze as p1  # noqa: E402
import problem2_terrain as p2  # noqa: E402
import problem3_alphabeta as p3  # noqa: E402
import problem4_treasure as p4  # noqa: E402


def test_problem1_expected_path():
    path = p1.solve_maze(p1.TEST_START, p1.TEST_GOAL, p1.TEST_MAP)
    assert p1._path_is_valid(path, p1.TEST_GOAL, p1.TEST_MAP), path
    assert len(path) == len(p1.EXPECTED_PATH), (path, p1.EXPECTED_PATH)


def test_problem1_no_path_returns_empty():
    assert p1.solve_maze((0, 0), (3, 4), p1.NO_PATH_MAP) == []


def test_problem2_expected_cost():
    assert p2.solve_terrain(p2.TEST_START, p2.TEST_GOAL, p2.TEST_MAP) == 7


def test_problem2_no_path_returns_minus_one():
    assert p2.solve_terrain((0, 0), (3, 3), p2.NO_PATH_MAP) == -1


def test_problem3_expected_value():
    assert p3.solve(p3.build_test_tree()) == 5
    assert p3.minimax(p3.build_from_dict(p3.TEST_JSON)) == 5


def test_problem4_expected_outputs():
    matrix, _ = p4.distance_matrix()
    assert matrix["A"]["T2"] == 4 and matrix["B"]["T3"] == 4
    h2 = p4.solve_game(2, matrix=matrix)
    h4 = p4.solve_game(4, matrix=matrix)
    assert (h2["best_target"], h2["best_value"]) == ("T2", -1), h2
    assert (h4["best_target"], h4["best_value"]) == ("T3", 3), h4


def test_problem4_minimax_agrees_with_alphabeta():
    matrix, _ = p4.distance_matrix()
    for depth in (1, 2, 3, 4):
        ab = p4.solve_game(depth, method="alpha-beta", matrix=matrix)
        mm = p4.solve_game(depth, method="minimax", matrix=matrix)
        assert ab["best_value"] == mm["best_value"], (depth, ab, mm)


def _run_all() -> int:
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"[PASS] {name}")
        except AssertionError as exc:
            failures += 1
            print(f"[FAIL] {name}: {exc or '断言失败'}")
    return failures


if __name__ == "__main__":
    failed = _run_all()
    print("全部通过" if failed == 0 else f"{failed} 个用例失败")
    sys.exit(1 if failed else 0)
