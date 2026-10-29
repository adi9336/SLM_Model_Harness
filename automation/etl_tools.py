"""ETL toolset: OpenAI-format schemas + callables bound to a shared DataStore."""
import csv
import json
import shutil
from pathlib import Path

from automation.datastore import DataStore

ETL_TOOLS = [
 {
  "type": "function",
  "function": {
   "name": "list_files",
   "description": "List CSV files in a directory.",
   "parameters": {
    "type": "object",
    "properties": {
     "directory": {
      "type": "string",
      "description": "Directory path"
     }
    },
    "required": [
     "directory"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "inspect_file",
   "description": "Show the header and first rows of a CSV file without loading it.",
   "parameters": {
    "type": "object",
    "properties": {
     "path": {
      "type": "string",
      "description": "Full CSV file path INCLUDING the filename, e.g. 'tasks/t004_cast_aggregate/orders.csv' — never a bare filename"
     }
    },
    "required": [
     "path"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "load_csv",
   "description": "Load a CSV file into a named table.",
   "parameters": {
    "type": "object",
    "properties": {
     "path": {
      "type": "string",
      "description": "Full input CSV file path INCLUDING the filename, e.g. 'tasks/t004_cast_aggregate/orders.csv' — never a bare filename"
     },
     "table": {
      "type": "string",
      "description": "Table name"
     }
    },
    "required": [
     "path",
     "table"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "preview_table",
   "description": "Show columns and first rows of a loaded table.",
   "parameters": {
    "type": "object",
    "properties": {
     "table": {
      "type": "string"
     },
     "limit": {
      "type": "integer",
      "description": "Max rows (default 5)"
     }
    },
    "required": [
     "table"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "clean_dates",
   "description": "Normalize a date column to ISO YYYY-MM-DD (tries common formats). Returns fixed/failed counts.",
   "parameters": {
    "type": "object",
    "properties": {
     "table": {
      "type": "string"
     },
     "column": {
      "type": "string"
     }
    },
    "required": [
     "table",
     "column"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "join_tables",
   "description": "Join two tables into a new table. Output columns = left columns then right columns.",
   "parameters": {
    "type": "object",
    "properties": {
     "left": {
      "type": "string"
     },
     "right": {
      "type": "string"
     },
     "left_on": {
      "type": "string"
     },
     "right_on": {
      "type": "string"
     },
     "how": {
      "type": "string",
      "enum": [
       "inner",
       "left",
       "right"
      ]
     },
     "out_table": {
      "type": "string"
     }
    },
    "required": [
     "left",
     "right",
     "left_on",
     "right_on",
     "out_table"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "aggregate",
   "description": "Group by a column and aggregate another. Output column is named <agg_func>_<agg_column> (e.g. sum_amount).",
   "parameters": {
    "type": "object",
    "properties": {
     "table": {
      "type": "string"
     },
     "group_by": {
      "type": "string"
     },
     "agg_column": {
      "type": "string"
     },
     "agg_func": {
      "type": "string",
      "enum": [
       "sum",
       "avg",
       "count",
       "min",
       "max"
      ]
     },
     "out_table": {
      "type": "string"
     }
    },
    "required": [
     "table",
     "group_by",
     "agg_column",
     "agg_func",
     "out_table"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "save_table",
   "description": "Write a table to a CSV file.",
   "parameters": {
    "type": "object",
    "properties": {
     "table": {
      "type": "string",
      "description": "Table name"
     },
     "path": {
      "type": "string",
      "description": "Full output CSV file path INCLUDING the filename, e.g. 'tasks/t001_clean_dates/out.csv'"
     }
    },
    "required": [
     "table",
     "path"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "filter_rows",
   "description": "Filter a table to rows where a column matches a condition (e.g. column=amount, operator='>', value=100).",
   "parameters": {
    "type": "object",
    "properties": {
     "table": {
      "type": "string"
     },
     "column": {
      "type": "string"
     },
     "operator": {
      "type": "string",
      "enum": [
       "=",
       "!=",
       "<",
       ">",
       "<=",
       ">="
      ]
     },
     "value": {
      "type": "string",
      "description": "Value to compare against"
     },
     "out_table": {
      "type": "string"
     }
    },
    "required": [
     "table",
     "column",
     "operator",
     "value",
     "out_table"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "cast_column",
   "description": "Cast a column to a type: 'number' strips $ and commas ('$1,234.56' -> 1234.56), 'text' trims whitespace.",
   "parameters": {
    "type": "object",
    "properties": {
     "table": {
      "type": "string"
     },
     "column": {
      "type": "string"
     },
     "type": {
      "type": "string",
      "enum": [
       "number",
       "integer",
       "text"
      ]
     }
    },
    "required": [
     "table",
     "column",
     "type"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "dedupe",
   "description": "Remove duplicate rows from a table.",
   "parameters": {
    "type": "object",
    "properties": {
     "table": {
      "type": "string"
     },
     "out_table": {
      "type": "string"
     }
    },
    "required": [
     "table",
     "out_table"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "rename_column",
   "description": "Rename a column in a table.",
   "parameters": {
    "type": "object",
    "properties": {
     "table": {
      "type": "string"
     },
     "old": {
      "type": "string"
     },
     "new": {
      "type": "string"
     }
    },
    "required": [
     "table",
     "old",
     "new"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "merge_tables",
   "description": "Combine multiple tables with identical columns into ONE table by appending all rows.",
   "parameters": {
    "type": "object",
    "properties": {
     "tables": {
      "type": "array",
      "items": {
       "type": "string"
      },
      "description": "List of existing table names to combine, e.g. ['m01', 'm02', 'm03']"
     },
     "out_table": {
      "type": "string",
      "description": "Name of the new combined table"
     }
    },
    "required": [
     "tables",
     "out_table"
    ]
   }
  }
 },
 {
  "type": "function",
  "function": {
   "name": "move_file",
   "description": "Move a file to a destination folder or full target path.",
   "parameters": {
    "type": "object",
    "properties": {
     "path": {
      "type": "string",
      "description": "Full current file path INCLUDING filename, e.g. 'tasks/realdata/sales/2024-01_sales.csv'"
     },
     "dest": {
      "type": "string",
      "description": "Destination folder or full path, e.g. 'tasks/t010_file_organize/processed'"
     }
    },
    "required": [
     "path",
     "dest"
    ]
   }
  }
 }
]


def make_callables(store: DataStore) -> dict:
    """Return name->callable dict bound to the given DataStore."""
    def list_files(directory):
        return {"files": sorted(str(p) for p in Path(directory).glob("*.csv"))}

    def inspect_file(path):
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            header = next(r, [])
            sample = [next(r, None) for _ in range(5)]
        return {"columns": header, "sample_rows": [s for s in sample if s is not None]}

    def move_file(path, dest):
        src = Path(path)
        dst = Path(dest)
        if not dst.suffix:  # dest is a folder -> keep the filename
            dst = dst / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return {"moved": str(src), "to": str(dst)}

    return {
        "list_files": list_files,
        "inspect_file": inspect_file,
        "load_csv": store.load_csv,
        "preview_table": store.preview,
        "clean_dates": store.clean_dates,
        "join_tables": store.join_tables,
        "aggregate": store.aggregate,
        "save_table": store.save_table,
        "filter_rows": store.filter_rows,
        "cast_column": store.cast_column,
        "dedupe": store.dedupe,
        "rename_column": store.rename_column,
        "merge_tables": store.merge_tables,
        "move_file": move_file,
    }
