# 实验二：搜索算法（A* + Minimax / Alpha-Beta）

作者：杨乐文　学号：10243330408

## 一、项目概述

本实验完成四道搜索题：

- **题目一**：5×5 网格 A* 迷宫寻路，输出 S 到 E 的最短路径；
- **题目二**：加权地形 A*，输出最小移动代价；
- **题目三**：Minimax / Alpha-Beta 求博弈树根节点（MAX）的最佳得分；
- **题目四**：A* 计算距离矩阵，再用博弈搜索求 A 在 H=2、H=4 下的最优首步。

给定样例的预期结果为：题目一 7 步路径，题目二代价 7，题目三得分 5，题目四 H=2 的 T2/−1、H=4 的 T3/3。

## 二、文件说明

| 文件 | 说明 |
|---|---|
| `astar_core.py` | 共享 A* 核心：g/h/f、优先队列、closed 表、路径恢复 |
| `problem1_maze.py` | 题目一：迷宫寻路（单位代价） |
| `problem2_weighted_terrain.py` | 题目二：加权地形最小代价 |
| `problem3_alpha_beta.py` | 题目三：Minimax / Alpha-Beta 与访问顺序对照 |
| `problem4_treasure_game.py` | 题目四：6×6 距离矩阵 + H=2/H=4 博弈搜索 |
| `run_all.py` | 依次运行四题并核对给定样例 |
| `实验二报告.docx` | 实验报告可编辑版（3 页，仿实验一版式） |
| `实验二报告.pdf` | 实验报告 PDF（由 Word 从 DOCX 导出） |
| `实验二报告.md` | 实验报告 Markdown 源 |
| `make_report_docx.py` | Markdown → DOCX（宋体正文、黑体标题、浅蓝表头、图注） |
| `export_docx_pdf.py` | 用本机 Word 将 DOCX 导出为 PDF |
| `make_chart.py` | 生成报告用的两张节点数对照图 |
| `report_assets/fig_nodes.png` | 图 1：启发函数与 Alpha-Beta 节点数 |
| `report_assets/fig_orders.png` | 图 2：题目四不同访问顺序的节点数 |
| `实验二报告.zip` | 报告 PDF 的提交压缩包 |
| `提交GitHub流程.md` | 本机 GitHub 认证、代理、推送与报告生成链 |
| `.gitignore` | 排除缓存、报告和图片，保持仓库只含代码 |

## 三、环境要求

- Python ≥3.9（开发环境：Python 3.13.7）
- 算法代码仅使用标准库，无第三方依赖
- 报告生成额外需要 `python-docx`、`pywin32`（Windows + Microsoft Word）

```bash
pip install python-docx pywin32
```

## 四、运行方式

```bash
python run_all.py
```

也可单独运行任一题目文件，例如 `python problem4_treasure_game.py`。每个文件的 `main()` 都包含给定样例、结果打印和断言自检。

重新生成报告：

```bash
python make_chart.py          # 生成两张图
python make_report_docx.py    # 生成 实验二报告.docx
python export_docx_pdf.py     # 用 Word 导出 实验二报告.pdf
```

## 五、实验设置与可复现性

- 四个方向、候选宝藏顺序和堆内平局规则固定，无随机性，重复运行结果一致。
- A* 的 `heuristic="zero"` 可直接复现 h=0 对照；`h_scale` 用于带权地图的 c_min 缩放。
- 题目四的深度 H 表示从 A 首步开始的层数：H=2 为 A、B 各一步，H=4 为完整四回合。
- 统计指标：路径搜索用 expanded/generated，博弈搜索用 visited/cutoffs/pruned；所有数据由程序直接打印。
- 四个题目文件共用 `astar_core.py`，重复 A* 实现已消除，四题文件合计约 23 KB（重构前约 46 KB）。

## 六、实验结果摘要

| 题目 | 关键结果 | 对照实验 |
|---|---|---|
| 题目一 | 7 步最短路径 | h=0/曼哈顿：expanded 17→14 |
| 题目二 | 最小代价 7 | h=0/曼哈顿：expanded 15→9 |
| 题目三 | 根值 5 | 样例树 15→14 节点；宽树 13→9 节点 |
| 题目四 | H=2：T2/−1；H=4：T3/3 | Alpha-Beta：17→13、65→47 节点 |

## 七、实验报告说明

`实验二报告.pdf` 共 3 页，版式仿照实验一报告：标题居中、宋体正文、黑体标题、浅蓝表头、图注；正文含 8 个部分、5 张表、2 张图。作者信息沿用实验一（杨乐文，10243330408）；如需修改，编辑 `实验二报告.md` 顶部后重新运行 `make_report_docx.py` 和 `export_docx_pdf.py`。

## 八、GitHub 推送

本机已用 GitHub CLI 令牌登录账号 `yyyyylw`，`gh auth status` 可直接确认；`git push` 必须走本地代理 `127.0.0.1:7892`（端口以查询结果为准）。完整命令、踩坑记录和报告生成链见 `提交GitHub流程.md`。
