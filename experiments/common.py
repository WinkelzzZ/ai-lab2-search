"""实验脚本公共工具：路径注入、结果落盘、绘图设置。"""

from __future__ import annotations

import csv
import json
import os
import sys
from typing import Dict, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
RESULTS = os.path.join(ROOT, "results")
FIGURES = os.path.join(RESULTS, "figures")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
os.makedirs(FIGURES, exist_ok=True)


def save_json(name: str, obj: object) -> str:
    path = os.path.join(RESULTS, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, default=str)
    return path


def save_csv(name: str, rows: List[Dict[str, object]]) -> str:
    if not rows:
        return ""
    path = os.path.join(RESULTS, name)
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
                 for k, v in row.items()}
            )
    return path


def markdown_table(rows: List[Dict[str, object]], columns: List[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def setup_plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 130
    plt.rcParams["savefig.bbox"] = "tight"
    return plt


def figure_path(name: str) -> str:
    return os.path.join(FIGURES, name)
