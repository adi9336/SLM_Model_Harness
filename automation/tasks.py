"""Ground-truth task suite: load a task, score the output table against expected."""
import csv
import json
from pathlib import Path


def load_task(task_dir):
    task_dir = Path(task_dir)
    spec = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    spec["dir"] = str(task_dir)
    spec["expected"] = str(task_dir / "expected.csv")
    return spec


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        return [], []
    return rows[0], sorted(tuple(r) for r in rows[1:])


def score(actual_csv, expected_csv):
    if not Path(actual_csv).exists():
        return {"match": False, "cols_match": False, "rows_match": False, "missing": True}
    a_cols, a_rows = _read_csv(actual_csv)
    e_cols, e_rows = _read_csv(expected_csv)
    return {
        "match": a_cols == e_cols and a_rows == e_rows,
        "cols_match": a_cols == e_cols,
        "rows_match": a_rows == e_rows,
    }


def score_files(actual_dir, expected_names):
    """File-organisation tasks (e.g. moved files): compare the CSV set in a dir."""
    actual_dir = Path(actual_dir)
    actual = sorted(p.name for p in actual_dir.glob("*.csv")) if actual_dir.exists() else []
    expected = sorted(expected_names)
    return {"match": actual == expected, "actual": actual, "expected": expected}