"""通用 A* 搜索核心，题目一、二、四共用。

状态为网格坐标，g 为累计进入代价，h 默认取曼哈顿距离，f = g + h。
带权地图通过 h_scale 传入最小正进入代价，保证 h 可采纳。
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

Coord = Tuple[int, int]
DIRECTIONS: Tuple[Coord, ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))


@dataclass
class SearchResult:
    path: List[Coord]
    cost: int          # 不可达时为 -1
    expanded: int      # 有效弹出的节点数
    generated: int     # 进入过优先队列的节点数


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def grid_cell_cost(cell: object) -> Optional[int]:
    """通用地图代价：X 不可通行；S/E 为 0；A/B/T 为 1；数字为地形权值。"""
    text = str(cell).strip()
    if text == "X":
        return None
    if text in ("S", "E"):
        return 0
    if text in ("A", "B") or text.startswith("T"):
        return 1
    return int(text)


def min_step_cost(grid: Sequence[Sequence[object]]) -> int:
    """非起终点格的最小进入代价 c_min；无正权地形时返回 0。"""
    best: Optional[int] = None
    for row in grid:
        for cell in row:
            if str(cell).strip() in ("S", "E", "X"):
                continue
            cost = grid_cell_cost(cell)
            if cost is None:
                continue
            best = cost if best is None else min(best, cost)
    if best is None:
        return 1
    return max(0, best)


def astar(
    grid: Sequence[Sequence[object]],
    start: Coord,
    goal: Coord,
    cost_fn: Callable[[object], Optional[int]] = grid_cell_cost,
    heuristic: str = "manhattan",
    h_scale: int = 1,
) -> SearchResult:
    """A* 搜索，返回路径、代价和搜索量。

    cost_fn(cell) 返回进入该格的代价，None 表示不可通行；
    heuristic="zero" 时退化为一致代价搜索，用于对照实验。
    """
    rows = len(grid)
    if rows == 0 or len(grid[0]) == 0:
        return SearchResult([], -1, 0, 0)
    cols = len(grid[0])
    start = (int(start[0]), int(start[1]))
    goal = (int(goal[0]), int(goal[1]))

    def walkable(pos: Coord) -> bool:
        r, c = pos
        return 0 <= r < rows and 0 <= c < cols and cost_fn(grid[r][c]) is not None

    if not walkable(start) or not walkable(goal):
        return SearchResult([], -1, 0, 0)

    def h(pos: Coord) -> int:
        if heuristic == "manhattan":
            return h_scale * manhattan(pos, goal)
        if heuristic == "zero":
            return 0
        raise ValueError(f"未知启发函数: {heuristic}")

    g_score: Dict[Coord, int] = {start: 0}
    came_from: Dict[Coord, Coord] = {}
    closed = set()
    counter = 0
    h0 = h(start)
    # 堆元素：(f, h, 计数器, g, 坐标)；f 相同时优先展开更接近终点的节点
    open_heap: List[Tuple[int, int, int, int, Coord]] = [(h0, h0, 0, 0, start)]
    expanded = 0
    generated = 1

    while open_heap:
        _, _, _, g, node = heapq.heappop(open_heap)
        if node in closed or g > g_score.get(node, math.inf):
            continue

        expanded += 1
        if node == goal:
            path = [goal]
            while path[-1] != start:
                path.append(came_from[path[-1]])
            path.reverse()
            return SearchResult(path, g, expanded, generated)

        closed.add(node)
        r, c = node
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if not walkable(nxt) or nxt in closed:
                continue

            step = cost_fn(grid[nr][nc])
            assert step is not None
            new_g = g + step
            if new_g >= g_score.get(nxt, math.inf):
                continue

            g_score[nxt] = new_g
            came_from[nxt] = node
            counter += 1
            h_next = h(nxt)
            heapq.heappush(open_heap, (new_g + h_next, h_next, counter, new_g, nxt))
            generated += 1

    return SearchResult([], -1, expanded, generated)
