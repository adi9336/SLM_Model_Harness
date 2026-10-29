from harness import Agent
from automation.etl_tools import ETL_TOOLS


def test_priority_prompt_has_no_schemas():
    """NFR-4: tool JSON schemas never enter the priority model's prompt."""
    a = Agent(tools=ETL_TOOLS, tool_callables={})
    prompt = a._system_prompt()
    assert "load_csv" in prompt           # tool name present
    assert '"parameters"' not in prompt   # schema internals never leaked
    assert '"properties"' not in prompt
    assert '"required"' not in prompt
