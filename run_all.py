"""实验二 统一测试入口：依次运行四道题并核对给定样例。

用法：
    python run_all.py
"""

from __future__ import annotations

import sys

# 避免在提交目录中生成 __pycache__
sys.dont_write_bytecode = True


def _configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def main() -> None:
    _configure_stdout()

    import problem1_maze
    import problem2_weighted_terrain
    import problem3_alpha_beta
    import problem4_treasure_game

    modules = [
        ("题目一 迷宫寻路", problem1_maze),
        ("题目二 加权地形", problem2_weighted_terrain),
        ("题目三 Alpha-Beta 剪枝", problem3_alpha_beta),
        ("题目四 宝藏分配", problem4_treasure_game),
    ]

    for title, module in modules:
        print("\n" + "=" * 72)
        print(title)
        print("=" * 72)
        module.main()

    print("\n" + "=" * 72)
    print("全部题目测试通过 ✓")
    print("=" * 72)


if __name__ == "__main__":
    main()
