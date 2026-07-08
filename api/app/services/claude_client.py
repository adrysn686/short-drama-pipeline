"""Anthropic Claude client for the Story Bible and Script agents — architecture doc §2-3.

Uses forced structured output (tool-use) so callers get a validated Pydantic
model back, never raw prose to parse.
"""
from ..config import get_settings


def generate_structured(system_prompt: str, user_prompt: str, schema: dict, model: str = "claude-opus-4-8") -> dict:
    # TODO: call the Anthropic API with tools=[{"input_schema": schema, ...}]
    # and tool_choice forcing that tool, return the validated tool input.
    settings = get_settings()
    raise NotImplementedError
