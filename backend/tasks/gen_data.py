"""Generate realistic ETL task fixtures and their deterministic expected outputs.

Ground truth is computed by running the KNOWN-CORRECT DataStore calls, so every
expected.csv is machine-verified (not hand-typed) and uses the same code path
the agent will run — float precision and column naming match exactly.
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # project root

from automation.datastore import DataStore

HERE = Path(__file__).parent


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)  # csv.writer quotes "$1,234.56" correctly
        for r in rows:
            w.writerow(r)


def _make_task(name, prompt, input_rows, compute):
    d = HERE / name
    d.mkdir(parents=True, exist_ok=True)
    _write_csv(d / "orders.csv", input_rows)

    out_path = f"tasks/{name}/out.csv"
    (d / "task.json").write_text(
        json.dumps({"name": name, "prompt": prompt, "out_path": out_path}, indent=2),
        encoding="utf-8",
    )

    # Deterministic ground truth: run the correct calls, save expected.csv.
    ds = DataStore(":memory:")
    out_table = compute(ds, d)
    ds.save_table(out_table, str(d / "expected.csv"))
    print(f"  {name}: expected rows = {ds._count(out_table)}")


def main():
    print("generating realistic fixtures...")

    _make_task(
        "t004_cast_aggregate",
        "Load tasks/t004_cast_aggregate/orders.csv into a table named 'orders'. "
        "Cast the 'amount' column to number. Aggregate the total amount per CustomerID "
        "(sum of amount) into a table named 'agg'. Save the 'agg' table to "
        "tasks/t004_cast_aggregate/out.csv",
        [["order_id", "CustomerID", "amount"],
         ["1", "C101", "$1,234.56"],
         ["2", "C102", "$99.00"],
         ["3", "C101", "$250.00"],
         ["4", "C103", "$1,500.00"]],
        lambda ds, d: (ds.load_csv(d / "orders.csv", "orders"),
                       ds.cast_column("orders", "amount", "number"),
                       ds.aggregate("orders", "CustomerID", "amount", "sum", "agg"))[-1]["table"],
    )

    _make_task(
        "t005_clean_cast",
        "Load tasks/t005_clean_cast/orders.csv into a table named 'orders'. "
        "Clean the 'order_date' column. Cast the 'amount' column to number. "
        "Save the 'orders' table to tasks/t005_clean_cast/out.csv",
        [["order_id", "amount", "order_date"],
         ["1", "$1,234.56", "01/15/2024"],
         ["2", "$99.00", "2024-02-20"],
         ["3", "$250.00", "15/03/2024"]],
        lambda ds, d: (ds.load_csv(d / "orders.csv", "orders"),
                       ds.clean_dates("orders", "order_date"),
                       ds.cast_column("orders", "amount", "number"),
                       "orders")[-1],
    )

    _make_task(
        "t006_filter",
        "Load tasks/t006_filter/orders.csv into a table named 'orders'. "
        "Cast the 'amount' column to number. Filter rows where amount is greater "
        "than 100 into a table named 'big'. Save the 'big' table to "
        "tasks/t006_filter/out.csv",
        [["order_id", "amount"],
         ["1", "$1,234.56"],
         ["2", "$99.00"],
         ["3", "$250.00"],
         ["4", "$75.50"]],
        lambda ds, d: (ds.load_csv(d / "orders.csv", "orders"),
                       ds.cast_column("orders", "amount", "number"),
                       ds.filter_rows("orders", "amount", ">", 100, "big"))[-1]["table"],
    )

    _make_task(
        "t007_rename_dedupe",
        "Load tasks/t007_rename_dedupe/orders.csv into a table named 'orders'. "
        "Rename the 'Customer ID' column to 'customer_id'. Remove duplicate rows "
        "into a table named 'clean'. Save the 'clean' table to "
        "tasks/t007_rename_dedupe/out.csv",
        [["Order ID", "Customer ID", "Amount"],
         ["1", "C101", "100"],
         ["2", "C102", "200"],
         ["1", "C101", "100"]],
        lambda ds, d: (ds.load_csv(d / "orders.csv", "orders"),
                       ds.rename_column("orders", "Customer ID", "customer_id"),
                       ds.dedupe("orders", "clean"))[-1]["table"],
    )

    print("done.")


if __name__ == "__main__":
    main()
