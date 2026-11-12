# 当代人工智能实验课 · 实验二（搜索算法）

A* 与 Alpha-Beta 剪枝的实现、测试与对照实验。全部结果可用一条命令复现。

## 环境

- Python 3.10+（开发环境 3.12.7，Windows 11）
- 算法实现零第三方依赖，只用标准库 `heapq` / `dataclasses`
- `matplotlib` 仅用于生成 `results/figures/` 里的图表（缺失时实验数据仍会正常输出）

## 目录结构

```
src/
  astar.py                 通用 A* 内核（Grid、代价函数、启发函数、平局规则、过程统计）
  ida_star.py              拓展实验用 IDA*
  problem1_maze.py         题目一 迷宫寻路    接口 solve_maze(start, goal, map) -> List[Tuple[int,int]]
  problem2_terrain.py      题目二 加权地形    接口 solve_terrain(start, goal, map) -> int
  problem3_alphabeta.py    题目三 Alpha-Beta  接口 solve(root) -> int，TreeNode / build_from_dict
  problem4_treasure.py     题目四 综合题      distance_matrix / solve_game(H) / principal_variation
tests/
  test_problems.py         官方测试用例自检（7 个断言，兼容 pytest）
experiments/
  run_all.py               一键跑完自检 + 5 组对照实验，汇总 results/summary.md
  exp1_maze.py             启发函数 / 平局规则 / 规模 / 贪心对照
  exp2_terrain.py          代价累计、可采纳性 365 例扫描、终点代价两种读法对照
  exp3_alphabeta.py        剪枝轨迹、访问顺序与理论下界对照
  exp4_treasure.py         距离矩阵、H=1..4 决策差异、顺序与置换缓存、深度饱和
  exp5_extensions.py       IDA* 对照、加权 A*、平局规则放大验证、宝藏价值敏感性
results/                   实验输出（json / csv / figures）
docs/
  实验二报告.pdf / .docx    提交用报告（4 页，符合「不超过 5 页」要求）
  实验二报告_5页.md          上述报告的源文件
  实验二报告_详细版.*         21 页完整版（含全部数据表与推导，供自查，不用于提交）
  report5.css                报告排版样式
```

## 报告重新导出（改完 GitHub 链接后执行）

```bash
cd docs
"D:/Anaconda/Library/bin/pandoc.exe" 实验二报告_5页.md -o _tmp.html --standalone --embed-resources --resource-path=. --css=report5.css
"C:/Program Files/Google/Chrome/Application/chrome.exe" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="实验二报告.pdf" "file:///<绝对路径>/docs/_tmp.html"
del _tmp.html
```

## 运行

```bash
# 1) 官方测试用例
python tests/test_problems.py

# 2) 单题直接运行（打印题面用例的输入输出）
python src/problem1_maze.py
python src/problem2_terrain.py
python src/problem3_alphabeta.py
python src/problem4_treasure.py

# 3) 全部对照实验 + 图表 + 汇总
python experiments/run_all.py

# 4) 报告由 Markdown 导出（可选，需 pandoc）
#    cd docs && pandoc 实验二报告.md -o 实验二报告.docx --resource-path=.
```

Windows 控制台若中文输出乱码，先执行 `set PYTHONIOENCODING=utf-8`。

## 官方用例结果

| 题目 | 预期 | 实测 |
|---|---|---|
| 一 迷宫寻路 | 8 个坐标的最短路径 | `[(0,0),(0,1),(0,2),(1,2),(1,3),(1,4),(2,4),(3,4)]` |
| 一 无解分支 | `[]` | `[]` |
| 二 加权地形 | `7` | `7` |
| 二 无解分支 | `-1` | `-1` |
| 三 Alpha-Beta | `5` | `5`（Minimax 同为 5） |
| 四 H=2 | `{"best_target":"T2","best_value":-1}` | 一致 |
| 四 H=4 | `{"best_target":"T3","best_value":3}` | 一致 |

## 说明

- A* 的 `g/h/f`、扩展数、生成数、open 表峰值、耗时都在 `SearchStats` 里统一采集，报告中的所有性能数字都来自这些计数器，不是估计值。
- 题目二把终点 E 的进入代价按题面说明记为 0；`manhattan` 与 `manhattan_free` 两种启发式都保留，用于讨论可采纳性。
- 题目三同时支持题面的 `TreeNode`（按层深奇偶判定 MAX/MIN）与 JSON 里的 `is_maximizing_player` 标记。
- 题目四的距离矩阵由 A* 现场计算，并自检对称性、三角不等式，以及与 Dijkstra（h=0）结果一致。
