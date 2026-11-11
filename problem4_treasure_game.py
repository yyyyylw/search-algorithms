"""实验二 题目四：竞争环境下的宝藏分配（A* + 博弈搜索）。

A（MAX）与 B（MIN）按 A→B→A→B 争夺 T1~T4：
    Gain(p, Ti) = Vi - d(p, Ti)
    U = Score_A - Score_B
A 最大化 U，B 最小化 U；到达深度或宝藏取完时返回当前 U。

输出：
    6x6 距离矩阵；H=2、H=4 时 A 的最优首步与收益差。
预期：
    H=2 => {"best_target": "T2", "best_value": -1}
    H=4 => {"best_target": "T3", "best_value": 3}
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

from astar_core import Coord, astar, grid_cell_cost, min_step_cost

GRID: List[List[str]] = [
    ["A", "1", "1", "X", "2", "1", "T1"],
    ["1", "X", "6", "X", "1", "X", "1"],
    ["1", "1", "T2", "1", "1", "1", "1"],
    ["X", "1", "X", "8", "X", "1", "X"],
    ["1", "1", "1", "1", "T3", "1", "1"],
    ["1", "X", "9", "X", "1", "X", "1"],
    ["T4", "1", "1", "X", "1", "1", "B"],
]
START_A: Coord = (0, 0)
START_B: Coord = (6, 6)
TREASURES: Tuple[str, ...] = ("T1", "T2", "T3", "T4")
VALUES: Dict[str, int] = {"T1": 9, "T2": 6, "T3": 7, "T4": 7}
TREASURE_POS: Dict[str, Coord] = {
    "T1": (0, 6), "T2": (2, 2), "T3": (4, 4), "T4": (6, 0)
}
POINTS: Dict[str, Coord] = {"A": START_A, "B": START_B, **TREASURE_POS}
NAMES: Tuple[str, ...] = ("A", "B", "T1", "T2", "T3", "T4")
NAME_BY_POS: Dict[Coord, str] = {pos: name for name, pos in POINTS.items()}

EXPECTED_DISTANCE: Dict[str, List[int]] = {
    "A": [0, 12, 10, 4, 8, 8],
    "B": [12, 0, 8, 8, 4, 10],
    "T1": [10, 8, 0, 6, 6, 12],
    "T2": [4, 8, 6, 0, 6, 6],
    "T3": [8, 4, 6, 6, 0, 6],
    "T4": [8, 10, 12, 6, 6, 0],
}
EXPECTED_RESULTS: Dict[int, Dict[str, object]] = {
    2: {"best_target": "T2", "best_value": -1},
    4: {"best_target": "T3", "best_value": 3},
}
H_SCALE = min_step_cost(GRID)


def build_distance_matrix() -> Dict[str, Dict[str, int]]:
    """A* 计算 A、B、T1~T4 两两之间的最小移动代价。"""
    matrix: Dict[str, Dict[str, int]] = {}
    for source in NAMES:
        matrix[source] = {}
        for target in NAMES:
            result = astar(
                GRID, POINTS[source], POINTS[target], grid_cell_cost,
                h_scale=H_SCALE,
            )
            if result.cost < 0:
                raise RuntimeError(f"{source} -> {target} 不可达")
            matrix[source][target] = result.cost
    return matrix


def distance(
    matrix: Dict[str, Dict[str, int]],
    position: Coord,
    treasure: str,
) -> int:
    return matrix[NAME_BY_POS[position]][treasure]


@dataclass(frozen=True)
class GameState:
    """双方位置、剩余宝藏、累计收益、当前玩家。"""

    pos_a: Coord
    pos_b: Coord
    remaining: Tuple[str, ...]
    score_a: int
    score_b: int
    player: str

    def evaluation(self) -> int:
        return self.score_a - self.score_b


@dataclass
class Stats:
    nodes: int = 0
    cutoffs: int = 0
    pruned: int = 0


def initial_state() -> GameState:
    return GameState(START_A, START_B, tuple(TREASURES), 0, 0, "A")


def successors(
    state: GameState,
    matrix: Dict[str, Dict[str, int]],
) -> Iterator[Tuple[str, int, GameState]]:
    """生成 (宝藏, 本次收益, 后继状态)。"""
    if state.player == "A":
        for t in state.remaining:
            gain = VALUES[t] - distance(matrix, state.pos_a, t)
            rest = tuple(x for x in state.remaining if x != t)
            yield t, gain, GameState(
                TREASURE_POS[t], state.pos_b, rest,
                state.score_a + gain, state.score_b, "B",
            )
    else:
        for t in state.remaining:
            gain = VALUES[t] - distance(matrix, state.pos_b, t)
            rest = tuple(x for x in state.remaining if x != t)
            yield t, gain, GameState(
                state.pos_a, TREASURE_POS[t], rest,
                state.score_a, state.score_b + gain, "A",
            )


def ordered_moves(
    state: GameState,
    matrix: Dict[str, Dict[str, int]],
    order: str,
) -> List[Tuple[str, int, GameState]]:
    """canonical: T1~T4；reverse: 反转；gain: 按本次收益降序。"""
    moves = list(successors(state, matrix))
    if order == "reverse":
        moves.reverse()
    elif order == "gain":
        moves.sort(key=lambda item: item[1], reverse=True)
    elif order != "canonical":
        raise ValueError(f"未知顺序: {order}")
    return moves


def minimax(
    state: GameState,
    depth: int,
    matrix: Dict[str, Dict[str, int]],
    stats: Stats,
    order: str = "canonical",
) -> Tuple[int, Optional[str]]:
    stats.nodes += 1
    if depth <= 0 or not state.remaining:
        return state.evaluation(), None

    moves = ordered_moves(state, matrix, order)
    best_move: Optional[str] = None
    if state.player == "A":
        best = -math.inf
        for t, _, child in moves:
            value, _ = minimax(child, depth - 1, matrix, stats, order)
            if value > best:
                best, best_move = value, t
        return int(best), best_move

    best = math.inf
    for t, _, child in moves:
        value, _ = minimax(child, depth - 1, matrix, stats, order)
        if value < best:
            best, best_move = value, t
    return int(best), best_move


def alpha_beta(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    matrix: Dict[str, Dict[str, int]],
    stats: Stats,
    order: str = "canonical",
) -> Tuple[int, Optional[str]]:
    stats.nodes += 1
    if depth <= 0 or not state.remaining:
        return state.evaluation(), None

    moves = ordered_moves(state, matrix, order)
    best_move: Optional[str] = None

    if state.player == "A":
        best = -math.inf
        for i, (t, _, child) in enumerate(moves):
            value, _ = alpha_beta(child, depth - 1, alpha, beta, matrix, stats, order)
            if value > best:
                best, best_move = value, t
            alpha = max(alpha, best)
            if alpha >= beta:
                if i + 1 < len(moves):
                    stats.cutoffs += 1
                    stats.pruned += len(moves) - i - 1
                break
        return int(best), best_move

    best = math.inf
    for i, (t, _, child) in enumerate(moves):
        value, _ = alpha_beta(child, depth - 1, alpha, beta, matrix, stats, order)
        if value < best:
            best, best_move = value, t
        beta = min(beta, best)
        if beta <= alpha:
            if i + 1 < len(moves):
                stats.cutoffs += 1
                stats.pruned += len(moves) - i - 1
            break
    return int(best), best_move


def search(
    depth: int,
    algorithm: str = "alpha_beta",
    order: str = "canonical",
    matrix: Optional[Dict[str, Dict[str, int]]] = None,
) -> Dict[str, object]:
    if depth <= 0:
        raise ValueError("深度必须为正整数")
    matrix = matrix or build_distance_matrix()
    stats = Stats()
    state = initial_state()

    if algorithm == "minimax":
        value, move = minimax(state, depth, matrix, stats, order)
    elif algorithm == "alpha_beta":
        value, move = alpha_beta(state, depth, -math.inf, math.inf, matrix, stats, order)
    else:
        raise ValueError(f"未知算法: {algorithm}")

    return {
        "best_target": move,
        "best_value": value,
        "nodes": stats.nodes,
        "cutoffs": stats.cutoffs,
        "pruned": stats.pruned,
    }


def solve(depth: int) -> Dict[str, object]:
    result = search(depth)
    return {"best_target": result["best_target"], "best_value": result["best_value"]}


def principal_variation(
    depth: int,
    matrix: Dict[str, Dict[str, int]],
) -> Tuple[List[Tuple[str, str, int, int]], int]:
    """双方最优对抗下的主变例。"""
    state = initial_state()
    line: List[Tuple[str, str, int, int]] = []
    for remaining_depth in range(depth, 0, -1):
        if not state.remaining:
            break
        _, move = minimax(state, remaining_depth, matrix, Stats())
        if move is None:
            break
        for t, gain, child in ordered_moves(state, matrix, "canonical"):
            if t == move:
                line.append((state.player, t, gain, child.evaluation()))
                state = child
                break
    return line, state.evaluation()


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    print("题目四：竞争环境下的宝藏分配")
    matrix = build_distance_matrix()

    print("\n6x6 距离矩阵：")
    print("      " + "".join(f"{n:>6}" for n in NAMES))
    for source in NAMES:
        print(f"{source:>4}: " + "".join(f"{matrix[source][t]:>6}" for t in NAMES))
        assert [matrix[source][t] for t in NAMES] == EXPECTED_DISTANCE[source]

    print("\nA/B 即时收益：")
    for player in ("A", "B"):
        gains = {t: VALUES[t] - matrix[player][t] for t in TREASURES}
        print(f"  {player}: {gains}")

    print("\nH=2 / H=4 结果：")
    for h in (2, 4):
        expected = EXPECTED_RESULTS[h]
        for algorithm in ("minimax", "alpha_beta"):
            result = search(h, algorithm, matrix=matrix)
            print(f"  H={h} {algorithm:<10} target={result['best_target']}, "
                  f"value={result['best_value']}, nodes={result['nodes']}, "
                  f"cutoffs={result['cutoffs']}, pruned={result['pruned']}")
            assert result["best_value"] == expected["best_value"]
        assert search(h, "minimax", matrix=matrix)["best_target"] == expected["best_target"]
        assert search(h, "alpha_beta", matrix=matrix)["best_target"] == expected["best_target"]
        print(f'  => {{"best_target": "{expected["best_target"]}", '
              f'"best_value": {expected["best_value"]}}}')

    print("\n访问顺序对照：")
    print(f"{'H':<3}{'algorithm':<12}{'order':<10}{'target':<7}"
          f"{'value':>6}{'nodes':>7}{'cutoffs':>9}{'pruned':>8}")
    for h in (2, 4):
        for algorithm in ("minimax", "alpha_beta"):
            for order in ("canonical", "gain", "reverse"):
                r = search(h, algorithm, order, matrix)
                print(f"{h:<3}{algorithm:<12}{order:<10}{str(r['best_target']):<7}"
                      f"{r['best_value']:>6}{r['nodes']:>7}{r['cutoffs']:>9}{r['pruned']:>8}")
                if algorithm == "alpha_beta":
                    assert r["best_value"] == EXPECTED_RESULTS[h]["best_value"]

    print("\n主变例：")
    for h in (2, 4):
        line, final = principal_variation(h, matrix)
        text = " -> ".join(
            f"{p}取{t}({g:+d}, U={u})" for p, t, g, u in line
        )
        print(f"  H={h}: {text} -> 终局 U={final}")
        assert final == EXPECTED_RESULTS[h]["best_value"]

    print("题目四 测试通过 ✓")


if __name__ == "__main__":
    main()
