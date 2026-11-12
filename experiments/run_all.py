"""一键复现：自检 + 全部对照实验 + 汇总 results/summary.md。

用法：python experiments/run_all.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

import common

SCRIPTS = ["test_problems", "exp1_maze", "exp2_terrain", "exp3_alphabeta", "exp4_treasure", "exp5_extensions"]


def run_module(name: str) -> str:
    folder = "tests" if name == "test_problems" else "experiments"
    target = os.path.join(common.ROOT, folder, f"{name}.py")
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, target],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=common.ROOT,
    )
    elapsed = time.perf_counter() - t0
    if proc.returncode != 0:
        raise RuntimeError(f"{name} 失败:\n{proc.stdout}\n{proc.stderr}")
    print(f"[OK] {name}  ({elapsed:.2f}s)")
    return proc.stdout


if __name__ == "__main__":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    chunks = []
    for script in SCRIPTS:
        out = run_module(script)
        chunks.append(f"## {script}\n\n```\n{out.strip()}\n```\n")
    summary = "# 实验二 全部实验输出\n\n" + "\n".join(chunks)
    with open(os.path.join(common.RESULTS, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write(summary)
    print("汇总写入 results/summary.md")
