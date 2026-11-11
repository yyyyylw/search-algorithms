"""实验二 题目一：迷宫寻路（A*）。

输入：起点、终点、二维地图（S/E/. /X）。
输出：最短路径坐标序列；无解返回 []。
"""

from __future__ import annotations

import sys
from typing import List, Optional, Sequence, Tuple

from astar_core import astar

Coord = Tuple[int, int]

SAMPLE_GRID: List[List[str]] = [
    ["S", ".", ".", "X", "."],
    [".", "X", ".", ".", "."],
    [".", "X", ".", "X", "."],
    [".", ".", ".", "X", "E"],
    ["X", "X", ".", ".", "."],
]
SAMPLE_START: Coord = (0, 0)
SAMPLE_GOAL: Coord = (3, 4)
SAMPLE_PATH: List[Coord] = [
    (0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)
]


def unit_cost(cell: object) -> Optional[int]:
    """题目一中所有非障碍格的进入代价均为 1。"""
    return None if str(cell).upper() == "X" else 1


def a_star_maze(
    grid: Sequence[Sequence[str]],
    start: Coord,
    goal: Coord,
    heuristic: str = "manhattan",
) -> List[Coord]:
    return astar(grid, start, goal, unit_cost, heuristic).path


def solve(start: Coord, goal: Coord, grid: Sequence[Sequence[str]]) -> List[Coord]:
    """按题目输入顺序封装：起点、终点、地图。"""
    return a_star_maze(grid, start, goal)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    result = astar(SAMPLE_GRID, SAMPLE_START, SAMPLE_GOAL, unit_cost)
    print("题目一：迷宫寻路")
    print(f"路径: {result.path}")
    print(f"步数: {result.cost}")
    assert result.path == SAMPLE_PATH and result.cost == 7

    print("\n启发函数对照：")
    print(f"{'heuristic':<12}{'expanded':>10}{'generated':>11}{'cost':>6}")
    stats = {}
    for name in ("zero", "manhattan"):
        res = astar(SAMPLE_GRID, SAMPLE_START, SAMPLE_GOAL, unit_cost, name)
        stats[name] = res
        print(f"{name:<12}{res.expanded:>10}{res.generated:>11}{res.cost:>6}")
        assert res.path == SAMPLE_PATH and res.cost == 7

    assert stats["manhattan"].expanded <= stats["zero"].expanded

    assert a_star_maze([["S", "X"], ["X", "E"]], (0, 0), (1, 1)) == []
    assert a_star_maze(SAMPLE_GRID, SAMPLE_START, SAMPLE_START) == [SAMPLE_START]
    print("\n无解返回 []，起点等于终点返回 [start]")
    print("题目一 测试通过 ✓")


if __name__ == "__main__":
    main()
