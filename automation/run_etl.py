"""Run the ETL agent on one task and score the output against ground truth."""
import argparse
import os

from harness import Agent
from automation.datastore import DataStore
from automation.etl_tools import ETL_TOOLS, make_callables
from automation.tasks import load_task, score, score_files
from reliability import AuditLog


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_dir")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    spec = load_task(args.task_dir)
    store = DataStore("etl.db")  # real persistent SQLite file, survives the run
    audit = AuditLog(path=f"{spec['name']}.audit.jsonl")
    agent = Agent(
        verbose=args.verbose,
        tools=ETL_TOOLS,
        tool_callables=make_callables(store),
        audit=audit,
        xlam_primary=(os.environ.get("FORMATTER_MODE") == "xlam"),
        max_steps=spec.get("max_steps"),
    )
    out_target = spec.get("out_path") or spec.get("out_dir")
    agent.run(spec["prompt"], required_output=out_target,
              required_min_files=len(spec["expected_files"]) if spec.get("expected_files") else None)
    if "expected_files" in spec:
        print("SCORE:", score_files(spec["out_dir"], spec["expected_files"]))
    else:
        print("SCORE:", score(spec["out_path"], spec["expected"]))


if __name__ == "__main__":
    main()