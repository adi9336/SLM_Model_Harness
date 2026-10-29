"""Reliability primitives: append-only audit log, tool-call schema validation, retry."""
import json
import time
from pathlib import Path

import jsonschema


class AuditLog:
    def __init__(self, path: str = "audit.jsonl"):
        self.path = Path(path)

    def log(self, event: str, **fields):
        rec = {"ts": time.time(), "event": event, **fields}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")


def validate_tool_call(tool_schema: dict, args: dict) -> list:
    """Return list of violations (empty == valid). Rejects unknown args."""
    schema = {**tool_schema.get("parameters", {}), "additionalProperties": False}
    validator = jsonschema.Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(args), key=str)]


def with_retry(fn, attempts: int = 3, delay: float = 1.0, exceptions=(Exception,)):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except exceptions as e:
            last = e
            if i < attempts - 1:
                time.sleep(delay * (i + 1))
    raise last
