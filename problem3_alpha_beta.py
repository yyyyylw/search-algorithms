"""实验二 题目三：Minimax 与 Alpha-Beta 剪枝。

输入 {"tree_structure": ...} 形式的博弈树，叶节点含 value，
内部节点含 children 与 is_maximizing_player。
输出根节点（MAX）在最优对抗下的得分。
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TreeNode:
    value: Optional[int] = None
    children: List["TreeNode"] = field(default_factory=list)
    is_maximizing_player: Optional[bool] = None


@dataclass
class Stats:
    visited: int = 0
    cutoffs: int = 0
    pruned: int = 0


def build_tree(data: Dict[str, Any], default_max: bool = True) -> TreeNode:
    """把题目 JSON 转为 TreeNode；未给出玩家标记时按层交替推断。"""
    if "tree_structure" in data:
        data = data["tree_structure"]

    def build(node: Dict[str, Any], is_max: bool) -> TreeNode:
        is_max = bool(node.get("is_maximizing_player", is_max))
        children = [build(child, not is_max) for child in (node.get("children") or [])]
        return TreeNode(node.get("value"), children, is_max)

    return build(data, default_max)


def _leaf(node: TreeNode) -> int:
    if node.value is None:
        raise ValueError("叶子节点缺少 value")
    return int(node.value)


def minimax(node: TreeNode, stats: Optional[Stats] = None) -> int:
    stats = stats or Stats()
    stats.visited += 1
    if not node.children:
        return _leaf(node)

    values = [minimax(child, stats) for child in node.children]
    return max(values) if node.is_maximizing_player else min(values)


def alpha_beta(
    node: TreeNode,
    alpha: float = -math.inf,
    beta: float = math.inf,
    stats: Optional[Stats] = None,
) -> int:
    stats = stats or Stats()
    stats.visited += 1
    if not node.children:
        return _leaf(node)

    children = node.children
    if node.is_maximizing_player:
        value = -math.inf
        for i, child in enumerate(children):
            value = max(value, alpha_beta(child, alpha, beta, stats))
            alpha = max(alpha, value)
            if alpha >= beta:
                if i + 1 < len(children):
                    stats.cutoffs += 1
                    stats.pruned += len(children) - i - 1
                break
        return int(value)

    value = math.inf
    for i, child in enumerate(children):
        value = min(value, alpha_beta(child, alpha, beta, stats))
        beta = min(beta, value)
        if beta <= alpha:
            if i + 1 < len(children):
                stats.cutoffs += 1
                stats.pruned += len(children) - i - 1
            break
    return int(value)


def solve(data: Dict[str, Any]) -> int:
    """对外接口：返回 MAX 玩家的最佳得分。"""
    return alpha_beta(build_tree(data))


def run(root: TreeNode, use_alpha_beta: bool) -> Tuple[int, Stats]:
    stats = Stats()
    value = alpha_beta(root, stats=stats) if use_alpha_beta else minimax(root, stats)
    return value, stats


def reverse_children(node: TreeNode) -> None:
    node.children.reverse()
    for child in node.children:
        reverse_children(child)


def _value(node: TreeNode) -> int:
    if not node.children:
        return _leaf(node)
    values = [_value(child) for child in node.children]
    return max(values) if node.is_maximizing_player else min(values)


def sort_children(node: TreeNode) -> None:
    """按子树真实 Minimax 值排序：MAX 降序、MIN 升序（理想顺序）。"""
    for child in node.children:
        sort_children(child)
    node.children.sort(key=_value, reverse=bool(node.is_maximizing_player))


SAMPLE_TREE: Dict[str, Any] = {
    "tree_structure": {
        "is_maximizing_player": True,
        "children": [
            {"is_maximizing_player": False, "children": [
                {"is_maximizing_player": True, "children": [{"value": 3}, {"value": 5}]},
                {"is_maximizing_player": True, "children": [{"value": 6}, {"value": 9}]},
            ]},
            {"is_maximizing_player": False, "children": [
                {"is_maximizing_player": True, "children": [{"value": 6}, {"value": 9}]},
                {"is_maximizing_player": True, "children": [{"value": 1}, {"value": 2}]},
            ]},
        ],
    }
}


def wide_tree() -> TreeNode:
    """3 个 MIN、每个 3 个叶子的宽树，用于放大剪枝差异。"""
    root = TreeNode(is_maximizing_player=True)
    for values in ([3, 5, 9], [1, 9, 9], [2, 8, 9]):
        node = TreeNode(is_maximizing_player=False)
        node.children = [TreeNode(value=v, is_maximizing_player=True) for v in values]
        root.children.append(node)
    return root


def show(name: str, root: TreeNode, use_alpha_beta: bool) -> Tuple[int, Stats]:
    value, stats = run(root, use_alpha_beta)
    print(f"{name:<26}value={value:<3} visited={stats.visited:<3} "
          f"cutoffs={stats.cutoffs:<2} pruned={stats.pruned}")
    return value, stats


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    print("题目三：Minimax 与 Alpha-Beta")
    assert solve(SAMPLE_TREE) == 5
    print("样例树结果:", solve(SAMPLE_TREE))

    print("\n样例树：")
    show("Minimax", build_tree(SAMPLE_TREE), False)
    show("Alpha-Beta 原始顺序", build_tree(SAMPLE_TREE), True)
    reversed_tree = build_tree(SAMPLE_TREE)
    reverse_children(reversed_tree)
    show("Alpha-Beta 反转顺序", reversed_tree, True)
    ideal_tree = build_tree(SAMPLE_TREE)
    sort_children(ideal_tree)
    show("Alpha-Beta 理想顺序", ideal_tree, True)

    print("\n宽树（3x3）：")
    show("Minimax", wide_tree(), False)
    show("Alpha-Beta 原始顺序", wide_tree(), True)
    reversed_wide = wide_tree()
    reverse_children(reversed_wide)
    show("Alpha-Beta 反转顺序", reversed_wide, True)
    ideal_wide = wide_tree()
    sort_children(ideal_wide)
    show("Alpha-Beta 理想顺序", ideal_wide, True)

    assert alpha_beta(build_tree(SAMPLE_TREE)) == 5
    assert alpha_beta(wide_tree()) == 3
    print("题目三 测试通过 ✓")


if __name__ == "__main__":
    main()
