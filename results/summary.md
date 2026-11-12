# 实验二 全部实验输出

## test_problems

```
[PASS] test_problem1_expected_path
[PASS] test_problem1_no_path_returns_empty
[PASS] test_problem2_expected_cost
[PASS] test_problem2_no_path_returns_minus_one
[PASS] test_problem3_expected_value
[PASS] test_problem4_expected_outputs
[PASS] test_problem4_minimax_agrees_with_alphabeta
全部通过
```

## exp1_maze

```
| heuristic | tie_break | expanded | generated | max_frontier | steps | time_ms |
|---|---|---|---|---|---|---|
| h=0 (Dijkstra) | h | 17 | 18 | 3 | 7 | 0.154 |
| Manhattan | h | 14 | 17 | 4 | 7 | 0.099 |
| Manhattan | deep | 14 | 17 | 4 | 7 | 0.091 |
| Manhattan | shallow | 14 | 16 | 3 | 7 | 0.087 |
| greedy best-first(只看 h) | - | 11 | 13 | 3 | 9 | 0.071 |
无解用例输出: []

| size | heuristic | solved | avg_expanded | avg_steps | avg_time_ms |
|---|---|---|---|---|---|
| 8x8 | h=0 | 7/10 | 37.6 | 14.57 | 0.335 |
| 8x8 | Manhattan | 7/10 | 19.2 | 14.57 | 0.231 |
| 8x8 | Greedy | 7/10 | 17.6 | 16.29 | 0.155 |
| 16x16 | h=0 | 7/10 | 164.0 | 30.0 | 1.605 |
| 16x16 | Manhattan | 7/10 | 66.4 | 30.0 | 0.803 |
| 16x16 | Greedy | 7/10 | 62.8 | 34.86 | 0.551 |
| 24x24 | h=0 | 7/10 | 342.4 | 46.0 | 3.069 |
| 24x24 | Manhattan | 7/10 | 92.7 | 46.0 | 1.122 |
| 24x24 | Greedy | 7/10 | 82.9 | 52.0 | 0.76 |
| 32x32 | h=0 | 10/10 | 750.3 | 62.2 | 6.33 |
| 32x32 | Manhattan | 10/10 | 128.2 | 62.2 | 1.269 |
| 32x32 | Greedy | 10/10 | 89.1 | 77.2 | 0.795 |
| 48x48 | h=0 | 7/10 | 1205.5 | 94.0 | 7.787 |
| 48x48 | Manhattan | 7/10 | 132.6 | 94.0 | 1.084 |
| 48x48 | Greedy | 7/10 | 88.6 | 113.14 | 0.602 |
```

## exp2_terrain

```
| heuristic | cost | optimal | expanded | generated | time_ms |
|---|---|---|---|---|---|
| h=0 (Dijkstra) | 7 | True | 15 | 24 | 0.278 |
| Manhattan x c_min | 7 | True | 9 | 16 | 0.15 |
| Manhattan(free-goal) x c_min | 7 | True | 9 | 16 | 0.139 |
无解用例: -1
8x8 平均扩展节点: {'zero': 44.2, 'manhattan': 36.4, 'manhattan_free': 36.5}
min=1（题面地形）            实例=120 naive最优=120 次优=0 naive==fixed比例=0.75 扩展差范围=[-1, 0]
min=2（无平原地带）           实例=120 naive最优=120 次优=0 naive==fixed比例=0.6917 扩展差范围=[-1, 0]
min=1 权重更多             实例=60 naive最优=60 次优=0 naive==fixed比例=0.9167 扩展差范围=[-1, 0]
min=1 含障碍 X            实例=65 naive最优=65 次优=0 naive==fixed比例=0.8923 扩展差范围=[-1, 0]

| heuristic | cost | expanded |
|---|---|---|
| h=0 (Dijkstra) | 8 | 17 |
| Manhattan x c_min | 8 | 9 |
| Manhattan(free-goal) x c_min | 8 | 11 |
```

## exp3_alphabeta

```
官方树 minimax: {'value': 5, 'method': 'minimax', 'nodes_visited': 15, 'leaves_evaluated': 8, 'internal_visited': 7, 'cutoffs': 0, 'children_skipped': 0, 'leaves_skipped': 0, 'total_leaves': 8, 'total_nodes': 15, 'leaf_skip_ratio': 0.0}
官方树 alpha-beta: {'value': 5, 'method': 'alpha-beta', 'nodes_visited': 14, 'leaves_evaluated': 7, 'internal_visited': 7, 'cutoffs': 2, 'children_skipped': 1, 'leaves_skipped': 1, 'total_leaves': 8, 'total_nodes': 15, 'leaf_skip_ratio': 0.125}

| depth | branching | total_leaves | minimax_leaves | ab_natural_leaves | ab_best_first_leaves | ab_worst_first_leaves | perfect_order_theory | saving_natural_pct | saving_best_pct | values_agree |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 3 | 27 | 27.0 | 20.6 | 11.0 | 27.0 | 11 | 23.7 | 59.3 | 25/25 |
| 3 | 4 | 64 | 64.0 | 42.76 | 19.0 | 64.0 | 19 | 33.2 | 70.3 | 25/25 |
| 4 | 3 | 81 | 81.0 | 43.32 | 17.0 | 78.64 | 17 | 46.5 | 79.0 | 25/25 |
| 4 | 4 | 256 | 256.0 | 113.4 | 31.0 | 245.2 | 31 | 55.7 | 87.9 | 25/25 |
```

## exp4_treasure

```
A     B    T1    T2    T3    T4
   A     0    12    10     4     8     8
   B    12     0     8     8     4    10
  T1    10     8     0     6     6    12
  T2     4     8     6     0     6     6
  T3     8     4     6     6     0     6
  T4     8    10    12     6     6     0
对称: True 三角不等式: True
总扩展节点 Manhattan: 275 Dijkstra: 680

| treasure | pos | value | d(A,Ti) | Gain_A | d(B,Ti) | Gain_B |
|---|---|---|---|---|---|---|
| T1 | (0, 6) | 9 | 10 | -1 | 8 | 1 |
| T2 | (2, 2) | 6 | 4 | 2 | 8 | -2 |
| T3 | (4, 4) | 7 | 8 | -1 | 4 | 3 |
| T4 | (6, 0) | 7 | 8 | -1 | 10 | -3 |

| H | method | best_target | best_value | nodes | leaves | cutoffs | children_skipped | root_values |
|---|---|---|---|---|---|---|---|---|
| 1 | minimax | T2 | 2 | 4 | 4 | 0 | 0 | {'T1': -1, 'T2': 2, 'T3': -1, 'T4': -1} |
| 1 | alpha-beta | T2 | 2 | 4 | 4 | 0 | 0 | {'T1': -1, 'T2': 2, 'T3': -1, 'T4': -1} |
| 2 | minimax | T2 | -1 | 16 | 12 | 0 | 0 | {'T1': -4, 'T2': -1, 'T3': -2, 'T4': -4} |
| 2 | alpha-beta | T2 | -1 | 12 | 8 | 2 | 4 | {'T1': -4, 'T2': -1, 'T3': -2, 'T4': -4} |
| 3 | minimax | T2 | 2 | 40 | 24 | 0 | 0 | {'T1': -4, 'T2': 2, 'T3': -1, 'T4': -4} |
| 3 | alpha-beta | T2 | 2 | 25 | 13 | 5 | 7 | {'T1': -4, 'T2': 2, 'T3': -1, 'T4': -4} |
| 4 | minimax | T3 | 3 | 64 | 24 | 0 | 0 | {'T1': -5, 'T2': 1, 'T3': 3, 'T4': -7} |
| 4 | alpha-beta | T3 | 3 | 46 | 16 | 12 | 6 | {'T1': -5, 'T2': 1, 'T3': 3, 'T4': -7} |

PV H=1: [('A', 'T2', 2)]
PV H=2: [('A', 'T2', -1), ('B', 'T3', -1)]
PV H=3: [('A', 'T2', 2), ('B', 'T1', 2), ('A', 'T3', 2)]
PV H=4: [('A', 'T3', 3), ('B', 'T1', 3), ('A', 'T2', 3), ('B', 'T4', 3)]

| method | ordering | cache | best_target | best_value | nodes | leaves | cutoffs | children_skipped | cache_hits |
|---|---|---|---|---|---|---|---|---|---|
| minimax | natural | False | T3 | 3 | 64 | 24 | 0 | 0 | 0 |
| alpha-beta | natural | False | T3 | 3 | 46 | 16 | 12 | 6 | 0 |
| alpha-beta | natural | True | T3 | 3 | 46 | 16 | 12 | 6 | 0 |
| alpha-beta | greedy | False | T3 | 3 | 49 | 18 | 13 | 3 | 0 |
| alpha-beta | greedy | True | T3 | 3 | 49 | 18 | 13 | 3 | 0 |
| alpha-beta | worst | False | T3 | 3 | 38 | 13 | 11 | 7 | 0 |
| alpha-beta | worst | True | T3 | 3 | 38 | 13 | 11 | 7 | 0 |
| alpha-beta | oracle | False | T3 | 3 | 30 | 10 | 12 | 8 | 0 |
| alpha-beta | oracle | True | T3 | 3 | 30 | 10 | 12 | 8 | 0 |

| H | best_target | best_value | nodes | leaves |
|---|---|---|---|---|
| 4 | T3 | 3 | 46 | 16 |
| 5 | T3 | 3 | 46 | 16 |
| 6 | T3 | 3 | 46 | 16 |
| 8 | T3 | 3 | 46 | 16 |
```

## exp5_extensions

```
| size | solved | astar_expanded | astar_peak_states | ida_generations | ida_iterations | ida_peak_path_states | ida_gmap_states | generations_ratio | path_depth_over_astar_states | cost_identical | astar_ms | ida_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8x8 | 7 | 20.6 | 31.4 | 30.0 | 1.1 | 15.3 | 24.3 | 1.46 | 0.486 | True | 0.216 | 0.188 |
| 12x12 | 6 | 32.7 | 52.7 | 46.8 | 1.0 | 23.0 | 42.3 | 1.43 | 0.437 | True | 0.237 | 0.229 |
| 16x16 | 2 | 55.5 | 85.0 | 82.0 | 1.0 | 31.0 | 71.0 | 1.48 | 0.365 | True | 0.466 | 0.375 |
| 20x20 | 5 | 66.4 | 107.2 | 97.2 | 1.0 | 39.0 | 86.6 | 1.46 | 0.364 | True | 0.731 | 0.545 |
| 24x24 | 6 | 72.7 | 124.3 | 109.8 | 1.0 | 47.0 | 96.5 | 1.51 | 0.378 | True | 0.712 | 0.536 |

| weight | instances | avg_expanded | avg_cost | avg_suboptimality | worst_suboptimality | optimal_rate |
|---|---|---|---|---|---|---|
| 1.0 | 12 | 55.2 | 30.17 | 1.0 | 1.0 | 1.0 |
| 1.5 | 12 | 41.9 | 31.0 | 1.0274 | 1.0667 | 0.583 |
| 2.0 | 12 | 40.4 | 32.17 | 1.0663 | 1.2667 | 0.333 |
| 4.0 | 12 | 39.2 | 33.0 | 1.0941 | 1.2667 | 0.167 |
| 8.0 | 12 | 39.2 | 33.0 | 1.0941 | 1.2667 | 0.167 |
| 16.0 | 12 | 39.2 | 33.0 | 1.0941 | 1.2667 | 0.167 |

| size | solved | avg_expanded_h | avg_expanded_deep | avg_expanded_shallow | avg_steps_h | shallow_vs_deep_pct |
|---|---|---|---|---|---|---|
| 16x16 | 5 | 45.2 | 45.2 | 118.2 | 30.0 | 161.5 |
| 24x24 | 5 | 90.2 | 90.2 | 256.4 | 46.0 | 184.3 |
| 32x32 | 5 | 189.0 | 189.0 | 462.8 | 62.8 | 144.9 |

| changed | new_value | H4_best_target | H4_best_value | H2_best_target |
|---|---|---|---|---|
| T2 | 1 | T3 | 4 | T3 |
| T2 | 2 | T3 | 3 | T3 |
| T2 | 3 | T3 | 2 | T3 |
| T2 | 4 | T3 | 1 | T3 |
| T2 | 5 | T3 | 2 | T2 |
| T2 | 6 | T3 | 3 | T2 |
| T2 | 7 | T2 | 2 | T2 |
| T2 | 8 | T2 | 3 | T2 |
| T2 | 9 | T2 | 4 | T2 |
| T2 | 10 | T2 | 5 | T2 |
| T2 | 11 | T2 | 6 | T2 |
| T2 | 12 | T2 | 7 | T2 |
| T3 | 1 | T2 | 7 | T1 |
| T3 | 2 | T2 | 6 | T1 |
| T3 | 3 | T2 | 5 | T2 |
| T3 | 4 | T2 | 4 | T2 |
| T3 | 5 | T2 | 3 | T2 |
| T3 | 6 | T2 | 2 | T2 |
| T3 | 7 | T3 | 3 | T2 |
| T3 | 8 | T3 | 4 | T3 |
| T3 | 9 | T3 | 5 | T3 |
| T3 | 10 | T3 | 6 | T3 |
| T3 | 11 | T3 | 7 | T3 |
| T3 | 12 | T3 | 8 | T3 |
翻转阈值: {'T2_flip_at': 7, 'T3_flip_at': 7}
```
