import json
from reliability import AuditLog, validate_tool_call, with_retry

CALC = {"name": "calculator", "description": "eval math",
        "parameters": {"type": "object",
                       "properties": {"expression": {"type": "string"}},
                       "required": ["expression"]}}

def test_audit_log_appends(tmp_path):
    log = AuditLog(path=str(tmp_path / "a.jsonl"))
    log.log("tool_exec", tool="calculator", ok=True)
    rec = json.loads((tmp_path / "a.jsonl").read_text().strip())
    assert rec["tool"] == "calculator" and rec["ok"] is True

def test_validate_ok():
    assert validate_tool_call(CALC, {"expression": "2+2"}) == []

def test_validate_missing_required():
    assert validate_tool_call(CALC, {})

def test_validate_unknown_arg():
    assert validate_tool_call(CALC, {"expression": "1", "bogus": 2})

def test_with_retry():
    calls = []
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("transient")
        return "ok"
    assert with_retry(flaky, attempts=3, delay=0) == "ok"
    assert len(calls) == 3
