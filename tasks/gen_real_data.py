"""Generate the realistic ETL workbench: a file-system data tree + deterministic ground truth.

Covers the three real ETL workflow classes:
- t008_batch_merge:       discover 12 monthly sales files -> clean -> merge -> combined CSV
- t009_aggregate_report:  total sales per supplier from the cleaned monthly data (a real report)
- t010_file_organize:     move a folder of CSVs into processed/ (file-system organisation)
- t011_cleanup_master:    dedupe + clean a messy customer master file (recurring cleanup)

Ground truth is COMPUTED by running the same DataStore code the agent calls, with
known-correct arguments — never hand-typed. Messiness is planted (mixed date
formats, currency strings, duplicate rows, decoy files), and the expected outputs
are what the deterministic backend produces on those files.

Usage:  python tasks/gen_real_data.py            # build everything
        python tasks/gen_real_data.py --task t010  # rebuild one task's fixtures (used as reset_cmd)
"""
import csv
import random
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from automation.datastore import DataStore

ROOT = Path(__file__).resolve().parent
REALDATA = ROOT / "realdata"
SALES_DIR = REALDATA / "sales"
ARCHIVED = SALES_DIR / "archived"

SUPPLIERS = ["Acme Supplies", "Beta Goods", "Gamma Traders", "Delta Wholesale", "Epsilon Import"]
PRODUCTS = ["Widget", "Gadget", "Doohickey", "Sprocket", "Flange", "Gizmo", "Cog", "Bolt"]
MONTH_FILES = [f"2024-{m:02d}_sales.csv" for m in range(1, 13)]  # the 12 real monthly files




def write_task(spec: dict):
    """Write {name}/task.json for a workbench task."""
    out = ROOT / spec["name"]
    out.mkdir(exist_ok=True)
    (out / "task.json").write_text(
        __import__("json").dumps(spec, indent=2), encoding="utf-8")

def gen_month_file(rng, month):
    """One monthly sales file. Jan-Apr: US dates + some currency amounts; May-Dec: ISO + plain."""
    n = rng.randint(250, 400)
    us_dates = month <= 4
    currency = month <= 2
    rows = []
    for _ in range(n):
        d = date(2024, month, rng.randint(1, 28))
        dt = d.strftime("%m/%d/%Y") if us_dates else d.isoformat()
        amount = rng.randint(500, 9000) + round(rng.random(), 2)
        amount_s = f"${amount:,.2f}" if currency else f"{amount:.2f}"
        rows.append([
            dt,
            f"C{rng.randint(1, 40)}",
            rng.choice(PRODUCTS),
            rng.choice(SUPPLIERS),
            amount_s,
        ])
    rows.extend(r for r in rows if rng.random() < 0.05)  # planted duplicate rows
    rng.shuffle(rows)
    return rows


def build_sales_tree():
    if SALES_DIR.exists():
        shutil.rmtree(SALES_DIR)
    SALES_DIR.mkdir(parents=True)
    rng = random.Random(20240921)  # fixed seed -> reproducible dataset
    for i, name in enumerate(MONTH_FILES, start=1):
        with (SALES_DIR / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Date", "CustomerID", "Product", "Supplier", "Amount"])
            w.writerows(gen_month_file(rng, i))
    # decoy 1: leftover duplicate of March (name contains 'extra' -> must be skipped)
    with (SALES_DIR / "2024-03_extra_sales.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date", "CustomerID", "Product", "Supplier", "Amount"])
        w.writerows(gen_month_file(random.Random(777), 3))
    # decoy 2: old year in archived/ subfolder (must be skipped — it is 2023 data)
    ARCHIVED.mkdir()
    with (ARCHIVED / "2023-12_old_sales.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date", "CustomerID", "Product", "Supplier", "Amount"])
        for _ in range(120):
            d = date(2023, 12, random.Random(99).randint(1, 28))
            w.writerow([d.strftime("%Y/%m/%d"), f"C{random.Random(1).randint(1, 40)}",
                        random.Random(2).choice(PRODUCTS), random.Random(3).choice(SUPPLIERS),
                        f"{random.Random(4).random() * 5000:.2f}"])


def build_customers():
    REALDATA.mkdir(exist_ok=True)
    rng = random.Random(555)
    base = [(f"C{i}", f"Customer Name {i}", rng.choice(["North", "South", "East", "West"]))
            for i in range(1, 41)]
    rows = []
    for cid, name, region in base:
        rows.append([cid, name, region])
        if rng.random() < 0.35:            # ~35% duplicated once
            rows.append([cid, name, region])
        elif rng.random() < 0.15:          # ~15% duplicated twice
            rows.append([cid, name, region])
            rows.append([cid, name, region])
    rng.shuffle(rows)
    with (REALDATA / "customers.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Customer ID", "Name", "Region"])
        w.writerows(rows)


def compute_t008():
    """expected: clean (ISO dates, numeric amounts) then merge the 12 real files."""
    ds = DataStore(":memory:")
    names = []
    for name in MONTH_FILES:
        t = name.replace("-", "_").removesuffix("_sales.csv")  # m01, m02, ...
        ds.load_csv(str(SALES_DIR / name), t)
        ds.clean_dates(t, "Date")
        ds.cast_column(t, "Amount")
        names.append(t)
    ds.merge_tables(names, "combined")
    out = ROOT / "t008_batch_merge"
    out.mkdir(exist_ok=True)
    ds.save_table("combined", str(out / "expected.csv"))
    write_task({
        "name": "t008_batch_merge",
        "prompt": (
            "In tasks/realdata/sales/ there are 12 monthly sales CSV files named like "
            "'2024-01_sales.csv'. IGNORE the archived/ subfolder and any file whose name "
            "contains 'extra'. Load each monthly file into its own table (e.g. "
            "'2024-01_sales.csv' into table m01, '2024-02_sales.csv' into m02, and so on). "
            "In EVERY loaded table, normalize the Date column to ISO format (YYYY-MM-DD) "
            "with clean_dates and cast the Amount column to number with cast_column. "
            "Then combine ALL 12 tables into one table named 'combined' with merge_tables "
            "(pass all 12 table names). Save the 'combined' table to "
            "tasks/t008_batch_merge/out.csv"
        ),
        "out_path": "tasks/t008_batch_merge/out.csv",
        "max_steps": 60,
    })
    print("t008 expected:", out / "expected.csv", f"({ds._count('combined')} rows)")


def compute_t009():
    """expected: total sales (sum of Amount) per Supplier over the whole year."""
    out = ROOT / "t009_aggregate_report"
    out.mkdir(exist_ok=True)
    ds = DataStore(":memory:")
    names = []
    for name in MONTH_FILES:
        t = name.replace("-", "_").removesuffix("_sales.csv")
        ds.load_csv(str(SALES_DIR / name), t)
        ds.clean_dates(t, "Date")
        ds.cast_column(t, "Amount")
        names.append(t)
    combined = out / "combined_clean.csv"  # the merged clean dataset the task starts from
    ds.merge_tables(names, "combined")
    ds.save_table("combined", str(combined))
    ds.aggregate("combined", "Supplier", "Amount", "sum", "report")
    ds.save_table("report", str(out / "expected.csv"))
    write_task({
        "name": "t009_aggregate_report",
        "prompt": (
            "Load tasks/t009_aggregate_report/combined_clean.csv into a table named "
            "'combined'. Aggregate the total sales per Supplier (sum of Amount) into a "
            "table named 'report'. Save the 'report' table to "
            "tasks/t009_aggregate_report/out.csv"
        ),
        "out_path": "tasks/t009_aggregate_report/out.csv",
    })
    print("t009 expected:", out / "expected.csv", f"({ds._count('report')} suppliers)")


def compute_t010():
    """fixtures: the 12 monthly files in input/ (reset per run); expected = all in processed/."""
    out = ROOT / "t010_file_organize"
    inp = out / "input"
    proc = out / "processed"
    if out.exists():
        shutil.rmtree(out)
    inp.mkdir(parents=True)
    proc.mkdir()
    for name in MONTH_FILES:
        shutil.copy2(SALES_DIR / name, inp / name)
    spec = {
        "name": "t010_file_organize",
        "prompt": (
            "In tasks/t010_file_organize/input/ there are 12 monthly CSV files. "
            "Move EVERY CSV file from input/ into tasks/t010_file_organize/processed/ "
            "using move_file. When all 12 files are moved, give your final answer."
        ),
        "out_dir": "tasks/t010_file_organize/processed",
        "expected_files": MONTH_FILES,
        "max_steps": 30,
        "reset_cmd": "python tasks/gen_real_data.py --task t010",
    }
    write_task(spec)
    print("t010 fixtures + task.json written")


def compute_t011():
    """expected: duplicate-free customer master with 'Customer ID' renamed to customer_id."""
    out = ROOT / "t011_cleanup_master"
    out.mkdir(exist_ok=True)
    shutil.copy2(REALDATA / "customers.csv", out / "customers.csv")
    ds = DataStore(":memory:")
    ds.load_csv(str(out / "customers.csv"), "cust")
    ds.dedupe("cust", "clean")
    ds.rename_column("clean", "Customer ID", "customer_id")
    ds.save_table("clean", str(out / "expected.csv"))
    write_task({
        "name": "t011_cleanup_master",
        "prompt": (
            "Load tasks/t011_cleanup_master/customers.csv into a table named 'cust'. "
            "Remove all duplicate rows with dedupe into a new table named 'clean'. "
            "Rename the 'Customer ID' column to 'customer_id'. Save the clean table to "
            "tasks/t011_cleanup_master/out.csv"
        ),
        "out_path": "tasks/t011_cleanup_master/out.csv",
    })
    print("t011 expected:", out / "expected.csv", f"({ds._count('clean')} unique customers)")


def main():
    task = None
    if len(sys.argv) > 2 and sys.argv[1] == "--task":
        task = sys.argv[2]
    if task in (None, "t008"):
        build_sales_tree()
        build_customers()
        compute_t008()
    if task in (None, "t009"):
        compute_t009()
    if task in (None, "t010"):
        compute_t010()
    if task in (None, "t011"):
        compute_t011()
    print("done.")


if __name__ == "__main__":
    main()