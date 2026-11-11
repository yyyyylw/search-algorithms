"""实验二 题目二：加权地形上的 A*。

进入格子的代价等于该格地形权值；X 不可通行；E 的进入代价为 0。
启发函数取 h = c_min * Manhattan，c_min 为最小正进入代价，保证可采纳。
输出最小总代价，无解返回 -1。
"""

from __future__ import annotations

import sys
from typing import List, Sequence, Tuple

from astar_core import SearchResult, astar, grid_cell_cost, min_step_cost

Coord = Tuple[int, int]

SAMPLE_GRID: List[List[object]] = [
    ["S", 1, 1, 8, 1],
    [1, 8, 3, 1, 1],
    [1, 8, 1, 8, 1],
    [1, 1, 1, 8, 1],
    [8, 8, 1, 1, "E"],
]
SAMPLE_START: Coord = (0, 0)
SAMPLE_GOAL: Coord = (4, 4)
SAMPLE_PATH: List[Coord] = [
    (0, 0), (1, 0), (2, 0), (3, 0), (3, 1),
    (3, 2), (4, 2), (4, 3), (4, 4),
]
SAMPLE_COST = 7


def a_star_weighted(
    grid: Sequence[Sequence[object]],
    start: Coord,
    goal: Coord,
    heuristic: str = "manhattan",
) -> SearchResult:
    return astar(
        grid, start, goal, grid_cell_cost, heuristic, h_scale=min_step_cost(grid)
    )


def min_path_cost(
    grid: Sequence[Sequence[object]],
    start: Coord,
    goal: Coord,
    heuristic: str = "manhattan",
) -> int:
    return a_star_weighted(grid, start, goal, heuristic).cost


def solve(start: Coord, goal: Coord, grid: Sequence[Sequence[object]]) -> int:
    """按题目输入顺序封装：起点、终点、地图。"""
    return min_path_cost(grid, start, goal)


def path_total_cost(grid: Sequence[Sequence[object]], path: Sequence[Coord]) -> int:
    total = 0
    for r, c in path[1:]:
        cost = grid_cell_cost(grid[r][c])
        assert cost is not None
        total += cost
    return total


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    result = a_star_weighted(SAMPLE_GRID, SAMPLE_START, SAMPLE_GOAL)
    print("题目二：加权地形")
    print(f"路径: {result.path}")
    print(f"最小总代价: {result.cost}")
    assert result.path == SAMPLE_PATH and result.cost == SAMPLE_COST
    assert path_total_cost(SAMPLE_GRID, result.path) == result.cost

    print("进入代价累计:")
    cumulative = 0
    for i, (r, c) in enumerate(result.path):
        if i:
            step = grid_cell_cost(SAMPLE_GRID[r][c])
            assert step is not None
            cumulative += step
            print(f"  ({r},{c}) +{step} -> {cumulative}")
    assert cumulative == SAMPLE_COST

    print("\n启发函数对照：")
    print(f"{'heuristic':<12}{'expanded':>10}{'generated':>11}{'cost':>6}")
    stats = {}
    for name in ("zero", "manhattan"):
        res = a_star_weighted(SAMPLE_GRID, SAMPLE_START, SAMPLE_GOAL, name)
        stats[name] = res
        print(f"{name:<12}{res.expanded:>10}{res.generated:>11}{res.cost:>6}")
        assert res.cost == SAMPLE_COST
    assert stats["manhattan"].expanded <= stats["zero"].expanded

    assert min_path_cost([["S", "X"], ["X", "E"]], (0, 0), (1, 1)) == -1
    assert min_path_cost(SAMPLE_GRID, SAMPLE_START, SAMPLE_START) == 0
    print("无解返回 -1，起点等于终点返回 0")
    print("题目二 测试通过 ✓")


if __name__ == "__main__":
    main()
