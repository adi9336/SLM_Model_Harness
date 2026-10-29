"""FastAPI Web Server for Two-Level Agent Architecture.

Provides:
- Web dashboard serving an interactive UI.
- Task catalog endpoint.
- Server-Sent Events (SSE) streaming endpoint for live execution visualization.
- System diagnostics & ground-truth verification.
"""

import asyncio
import csv
import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

import urllib.request
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import config
from agent import Agent
from automation.datastore import DataStore
from automation.etl_tools import ETL_TOOLS, make_callables
from automation.tasks import load_task, score, score_files
from reliability import AuditLog

app = FastAPI(title="Two-Level Agent Harness", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
TASKS_DIR = Path(__file__).parent / "tasks"

TASK_META = [
    {
        "id": "t001_clean_dates",
        "name": "ETL: Date Standardization",
        "category": "ETL Pipeline",
        "dir": "tasks/t001_clean_dates",
        "description": "Parses inconsistent and messy date formats across sales records, normalizes to ISO 8601, and writes out.csv.",
        "icon": "calendar",
        "input_file": "sales.csv",
        "output_file": "out.csv",
    },
    {
        "id": "t002_join",
        "name": "ETL: Multi-Table Relational Join",
        "category": "ETL Pipeline",
        "dir": "tasks/t002_join",
        "description": "Performs an inner join between sales.csv and accounts.csv on cust_id = customer_id without key-swapping errors.",
        "icon": "link-2",
        "input_file": "sales.csv, accounts.csv",
        "output_file": "out.csv",
    },
    {
        "id": "t004_cast_aggregate",
        "name": "ETL: Currency Cast & Aggregation",
        "category": "ETL Pipeline",
        "dir": "tasks/t004_cast_aggregate",
        "description": "Casts string amounts to numeric and computes total sales grouped by CustomerID with zero parameter loss.",
        "icon": "calculator",
        "input_file": "orders.csv",
        "output_file": "out.csv",
    },
    {
        "id": "t007_rename_dedupe",
        "name": "DevOps: Header Rename & Deduplication",
        "category": "DevOps Pipeline",
        "dir": "tasks/t007_rename_dedupe",
        "description": "Normalizes column names, removes redundant duplicate entries, and guarantees high-fidelity persistence.",
        "icon": "filter",
        "input_file": "orders.csv",
        "output_file": "out.csv",
    },
    {
        "id": "t010_file_organize",
        "name": "DevOps: Directory Organization & Batching",
        "category": "DevOps Pipeline",
        "dir": "tasks/t010_file_organize",
        "description": "Sorts 12 monthly sales CSV partitions from input/ into processed/ without getting trapped in file inspection loops.",
        "icon": "folder-archive",
        "input_file": "12 monthly CSV partitions",
        "output_file": "processed/ (12 files)",
    },
]


@app.get("/api/tasks")
def list_tasks():
    enriched = []
    for item in TASK_META:
        task_dir = Path(item["dir"])
        task_json = task_dir / "task.json"
        prompt = ""
        if task_json.exists():
            try:
                spec = json.loads(task_json.read_text(encoding="utf-8"))
                prompt = spec.get("prompt", "")
            except Exception:
                pass
        enriched.append({**item, "prompt": prompt})
    return enriched


@app.get("/api/status")
def get_system_status():
    ollama_running = False
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            ollama_running = resp.status == 200
    except Exception:
        ollama_running = False

    tinker_active = bool(config.TINKER_API_KEY.strip())
    active_backend = (
        f"Tinker Cloud API ({config.TINKER_MODEL})"
        if tinker_active
        else (f"Local Ollama ({config.PRIORITY_MODEL})" if ollama_running else "High-Resilience Demo Engine (Offline Safe)")
    )

    return {
        "status": "online",
        "architecture": "Two-Level Agent Architecture",
        "tinker_active": tinker_active,
        "tinker_model": config.TINKER_MODEL,
        "active_backend": active_backend,
        "reasoner_model": config.TINKER_MODEL if tinker_active else config.PRIORITY_MODEL,
        "formatter_model": config.FORMATTER_MODEL,
        "ollama_local_online": ollama_running,
        "on_premise": not tinker_active,
        "guards_enabled": [
            "Single-Tool Gating",
            "Deterministic Repair Pass",
            "De-dup Guard",
            "Query-Streak Guard",
            "Deliverable Completion Guard",
        ],
    }


@app.post("/api/config/tinker")
def configure_tinker(payload: Dict[str, str]):
    """Dynamically set or update Tinker API key and model."""
    key = payload.get("api_key", "").strip()
    model = payload.get("model", "").strip()
    if key:
        config.TINKER_API_KEY = key
    if model:
        config.TINKER_MODEL = model
    return {
        "success": True,
        "tinker_active": bool(config.TINKER_API_KEY),
        "model": config.TINKER_MODEL,
    }


@app.get("/api/preview/{task_id}")
def preview_output(task_id: str):
    item = next((t for t in TASK_META if t["id"] == task_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")

    out_file = Path(item["dir"]) / "out.csv"
    if not out_file.exists():
        return {"exists": False, "rows": []}

    rows = []
    try:
        with open(out_file, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, r in enumerate(reader):
                if i > 25:
                    break
                rows.append(r)
        return {"exists": True, "rows": rows}
    except Exception as e:
        return {"exists": True, "error": str(e), "rows": []}


@app.get("/api/stream/{task_id}")
def stream_execution(
    task_id: str,
    live: bool = Query(False, description="Whether to call live local Ollama"),
    delay: float = Query(0.4, description="Animation pacing delay in seconds"),
):
    item = next((t for t in TASK_META if t["id"] == task_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")

    task_dir = item["dir"]
    spec = load_task(task_dir)
    task_name = spec.get("name", Path(task_dir).name)

    # Prepare event queue
    q: queue.Queue = queue.Queue()

    def event_reporter(phase: str, title: str, payload=None):
        event_data = {
            "phase": phase,
            "title": title,
            "payload": payload if payload is not None else "",
            "timestamp": time.time(),
        }
        q.put(event_data)

    def run_worker():
        try:
            # Reset stale output
            if spec.get("reset_cmd"):
                cmd = spec["reset_cmd"]
                if cmd.startswith("python "):
                    cmd = f'"{sys.executable}" ' + cmd[7:]
                subprocess.run(cmd, shell=True, check=True, capture_output=True)
            if spec.get("out_path"):
                Path(spec["out_path"]).unlink(missing_ok=True)

            db_path = f"{task_name}.db"
            store = DataStore(db_path)
            store.reset()

            audit = AuditLog(path=f"{task_name}.audit.jsonl")

            out_target = spec.get("out_path") or spec.get("out_dir")
            req_files = len(spec["expected_files"]) if spec.get("expected_files") else None

            agent = Agent(
                verbose=False,
                tools=ETL_TOOLS,
                tool_callables=make_callables(store),
                audit=audit,
                xlam_primary=True,
                max_steps=spec.get("max_steps", 12),
                demo_mode=not live,
                pacing_delay=delay,
                reporter=event_reporter,
            )

            start = time.time()
            agent.run(spec["prompt"], required_output=out_target, required_min_files=req_files)
            duration = time.time() - start

            # Score result
            if "expected_files" in spec:
                score_res = score_files(spec["out_dir"], spec["expected_files"])
            else:
                score_res = score(spec["out_path"], spec["expected"])

            # Preview rows
            preview_rows = []
            if spec.get("out_path") and Path(spec["out_path"]).exists():
                with open(spec["out_path"], "r", encoding="utf-8") as f:
                    rdr = csv.reader(f)
                    for idx, row in enumerate(rdr):
                        if idx > 15:
                            break
                        preview_rows.append(row)

            store.close()

            q.put(
                {
                    "phase": "SCORECARD",
                    "title": "Ground-Truth Evaluation Scorecard",
                    "payload": {
                        "match": score_res.get("match", False),
                        "duration": round(duration, 2),
                        "tool_calls": len(agent.history) // 2,
                        "details": score_res,
                        "preview_rows": preview_rows,
                        "artifact": out_target,
                    },
                }
            )
        except Exception as e:
            q.put({"phase": "ERROR", "title": "Execution Error", "payload": str(e)})
        finally:
            q.put(None)  # Sentinel

    thread = threading.Thread(target=run_worker, daemon=True)
    thread.start()

    def event_stream():
        while True:
            item = q.get()
            if item is None:
                yield "event: end\ndata: {}\n\n"
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/")
def get_dashboard():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Two-Level Agent Server Running. Static UI not found.</h1>")


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def start():
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    start()

