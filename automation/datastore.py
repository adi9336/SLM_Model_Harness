"""Deterministic SQLite backend for the ETL agent. All CSV values load as TEXT."""
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

_DEFAULT_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m/%d/%y"]


class DataStore:
    def __init__(self, db_path: str = ":memory:"):
        # pass a file path (e.g. "etl.db") for a real, persistent database
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if hasattr(self, "conn") and self.conn:
            self.conn.close()
            self.conn = None

    def reset(self):
        names = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for (n,) in names:
            self.conn.execute(f'DROP TABLE IF EXISTS "{n}"')
        self.conn.commit()

    def _cols(self, table):
        cur = self.conn.execute(f'SELECT * FROM "{table}" LIMIT 0')
        return [d[0] for d in cur.description]

    def _count(self, table):
        return self.conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

    def load_csv(self, path, table):
        path = Path(path)
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            self.conn.execute(f'DROP TABLE IF EXISTS "{table}"')
            self.conn.execute(f'CREATE TABLE "{table}" ("' + '", "'.join(cols) + '")')
            for row in reader:
                placeholders = ",".join(["?"] * len(cols))
                self.conn.execute(f'INSERT INTO "{table}" VALUES ({placeholders})', [row[c] for c in cols])
        self.conn.commit()
        return {"table": table, "rows": self._count(table), "columns": cols}

    def preview(self, table, limit=5):
        rows = self.conn.execute(f'SELECT * FROM "{table}" LIMIT ?', (limit,)).fetchall()
        return {"columns": self._cols(table), "rows": [list(r) for r in rows]}

    def save_table(self, table, path):
        path = Path(path)
        cols = self._cols(table)
        rows = self.conn.execute(f'SELECT * FROM "{table}"').fetchall()
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for r in rows:
                w.writerow(list(r))
        return {"path": str(path), "rows": len(rows)}

    def clean_dates(self, table, column, formats=None):
        formats = formats or _DEFAULT_FORMATS
        cols = self._cols(table)
        if column not in cols:
            raise ValueError(f"column {column!r} not in {cols}")
        rows = self.conn.execute(f'SELECT rowid AS rid, "{column}" AS v FROM "{table}"').fetchall()
        fixed = failed = 0
        for r in rows:
            parsed = None
            if r["v"]:
                for fmt in formats:
                    try:
                        parsed = datetime.strptime(str(r["v"]).strip(), fmt)
                        break
                    except ValueError:
                        continue
            if parsed:
                self.conn.execute(f'UPDATE "{table}" SET "{column}"=? WHERE rowid=?', (parsed.date().isoformat(), r["rid"]))
                fixed += 1
            else:
                failed += 1
        self.conn.commit()
        return {"table": table, "fixed": fixed, "failed": failed}

    def join_tables(self, left, right, left_on, right_on, how="inner", out_table="joined"):
        how_map = {"inner": "INNER", "left": "LEFT", "right": "RIGHT"}
        if how not in how_map:
            raise ValueError(f"how must be one of {sorted(how_map)}")
        self.conn.execute(f'DROP TABLE IF EXISTS "{out_table}"')
        self.conn.execute(
            f'CREATE TABLE "{out_table}" AS SELECT * FROM "{left}" {how_map[how]} '
            f'JOIN "{right}" ON "{left}"."{left_on}" = "{right}"."{right_on}"'
        )
        self.conn.commit()
        return {"table": out_table, "rows": self._count(out_table)}

    def aggregate(self, table, group_by, agg_column, agg_func="sum", out_table="agg"):
        funcs = {"sum": "SUM", "avg": "AVG", "count": "COUNT", "min": "MIN", "max": "MAX"}
        if agg_func not in funcs:
            raise ValueError(f"agg_func must be one of {sorted(funcs)}")
        self.conn.execute(f'DROP TABLE IF EXISTS "{out_table}"')
        self.conn.execute(
            f'CREATE TABLE "{out_table}" AS SELECT "{group_by}", '
            f'{funcs[agg_func]}("{agg_column}") AS "{agg_func}_{agg_column}" '
            f'FROM "{table}" GROUP BY "{group_by}"'
        )
        self.conn.commit()
        return {"table": out_table, "rows": self._count(out_table)}

    def merge_tables(self, tables, out_table="merged"):
        """Append rows from tables with identical columns into one table (UNION ALL)."""
        if not tables:
            raise ValueError("tables must be a non-empty list of table names")
        quoted = " UNION ALL ".join(f'SELECT * FROM "{t}"' for t in tables)
        self.conn.execute(f'DROP TABLE IF EXISTS "{out_table}"')
        self.conn.execute(f'CREATE TABLE "{out_table}" AS {quoted}')
        self.conn.commit()
        return {"table": out_table, "rows": self._count(out_table)}

    def filter_rows(self, table, column, operator, value, out_table=None):
        ops = {"=": "=", "!=": "!=", "<": "<", ">": ">", "<=": "<=", ">=": ">="}
        if operator not in ops:
            raise ValueError(f"operator must be one of {sorted(ops)}")
        cols = self._cols(table)
        if column not in cols:
            raise ValueError(f"column {column!r} not in {cols}")
        out = out_table or table
        self.conn.execute(f'DROP TABLE IF EXISTS "{out}"')
        # Coerce numeric values so comparison is numeric (SQLite ranks TEXT > REAL,
        # so 'amount > "100"' on a numeric column is always false).
        try:
            val = float(value)
            if val.is_integer():
                val = int(val)
        except (ValueError, TypeError):
            val = str(value)
        self.conn.execute(
            f'CREATE TABLE "{out}" AS SELECT * FROM "{table}" '
            f'WHERE "{column}" {ops[operator]} ?',
            (val,),
        )
        self.conn.commit()
        return {"table": out, "rows": self._count(out)}

    def cast_column(self, table, column, type="number"):
        if type not in ("number", "integer", "text"):
            raise ValueError("type must be number, integer, or text")
        cols = self._cols(table)
        if column not in cols:
            raise ValueError(f"column {column!r} not in {cols}")
        rows = self.conn.execute(f'SELECT rowid AS rid, "{column}" AS v FROM "{table}"').fetchall()
        fixed = failed = 0
        for r in rows:
            v = r["v"]
            if type in ("number", "integer"):
                s = str(v).strip().replace("$", "").replace(",", "")
                try:
                    num = float(s) if type == "number" else int(float(s))
                except ValueError:
                    failed += 1
                    continue
                self.conn.execute(f'UPDATE "{table}" SET "{column}"=? WHERE rowid=?', (num, r["rid"]))
                fixed += 1
            else:  # text
                self.conn.execute(f'UPDATE "{table}" SET "{column}"=? WHERE rowid=?', (str(v).strip(), r["rid"]))
                fixed += 1
        self.conn.commit()
        return {"table": table, "fixed": fixed, "failed": failed}

    def dedupe(self, table, out_table=None):
        out = out_table or table
        if out == table:
            tmp = f"{table}__dedupe_tmp"
            self.conn.execute(f'DROP TABLE IF EXISTS "{tmp}"')
            self.conn.execute(f'CREATE TABLE "{tmp}" AS SELECT DISTINCT * FROM "{table}"')
            self.conn.execute(f'DROP TABLE "{table}"')
            self.conn.execute(f'ALTER TABLE "{tmp}" RENAME TO "{table}"')
        else:
            self.conn.execute(f'DROP TABLE IF EXISTS "{out}"')
            self.conn.execute(f'CREATE TABLE "{out}" AS SELECT DISTINCT * FROM "{table}"')
        self.conn.commit()
        return {"table": out, "rows": self._count(out)}

    def rename_column(self, table, old, new):
        cols = self._cols(table)
        if old not in cols:
            raise ValueError(f"column {old!r} not in {cols}")
        self.conn.execute(f'ALTER TABLE "{table}" RENAME COLUMN "{old}" TO "{new}"')
        self.conn.commit()
        return {"table": table, "renamed": [old, new]}
