"""Agent core layer — deterministic analytics query engine.

Exports the public API used by dashboard/app.py and tests.
Only analytics/ CSV data is used; no arbitrary Python execution.
"""
from agent.core import AgentCore
from agent.llm import LLMProvider
from agent.intent_parser import parse_intent, STRICT_INTENTS
from agent.router import route_intent, UNSUPPORTED_FALLBACK
from agent.result_validator import validate_result
from agent.chart_selector import select_chart
from agent.explanation import build_explanation

__all__ = [
    "AgentCore",
    "LLMProvider",
    "parse_intent",
    "STRICT_INTENTS",
    "route_intent",
    "UNSUPPORTED_FALLBACK",
    "validate_result",
    "select_chart",
    "build_explanation",
]
