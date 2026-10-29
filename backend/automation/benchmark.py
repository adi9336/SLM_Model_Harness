"""Run each task N times; report match-rate (reliability) across repeats."""
import argparse
import os
import subprocess
from pathlib import Path

from harness import Agent
from automation.datastore import DataStore
from automation.etl_tools import ETL_TOOLS, make_callables
from automation.tasks import load_task, score, score_files
from reliability import AuditLog


def run_once(task_dir, verbose=False):
    spec = load_task(task_dir)
    # File-mutating tasks (e.g. move_file) rebuild their fixtures per repeat.
    if spec.get("reset_cmd"):
        subprocess.run(spec["reset_cmd"], shell=True, check=True, capture_output=True)
    if spec.get("out_path"):
        Path(spec["out_path"]).unlink(missing_ok=True)  # remove stale output for a clean score
    store = DataStore("etl.db")  # persistent; tools drop+create tables (idempotent)
    store.reset()
    # The completion guard needs a concrete target: out.csv, or the out dir for
    # file-organisation tasks.
    out_target = spec.get("out_path") or spec.get("out_dir")
    agent = Agent(
        verbose=verbose,
        tools=ETL_TOOLS,
        tool_callables=make_callables(store),
        audit=AuditLog(path=f"{spec['name']}.audit.jsonl"),
        xlam_primary=(os.environ.get("FORMATTER_MODE") == "xlam"),
        max_steps=spec.get("max_steps"),
    )
    agent.run(spec["prompt"], required_output=out_target,
              required_min_files=len(spec["expected_files"]) if spec.get("expected_files") else None)
    if "expected_files" in spec:
        return score_files(spec["out_dir"], spec["expected_files"])["match"]
    return score(spec["out_path"], spec["expected"])["match"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_dirs", nargs="+")
    ap.add_argument("-n", type=int, default=5, help="repeats per task")
    args = ap.parse_args()
    for td in args.task_dirs:
        results = [run_once(td) for _ in range(args.n)]
        rate = sum(results) / len(results)
        print(f"{td}: match {sum(results)}/{len(results)} = {rate:.0%}")


if __name__ == "__main__":
    main()