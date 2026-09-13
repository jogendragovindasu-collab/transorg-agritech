"""Modular LLM with deterministic fallback.

Reads LLM_API_KEY from environment. If unavailable, all parsing and
explanation fall back to deterministic keyword/rule-based logic.
No arbitrary code execution. Only analytics CSV data is referenced.
"""
import os

LLM_API_KEY = os.environ.get("LLM_API_KEY", None)


class LLMProvider:
    """Simple wrapper: attempts LLM mode when key present,
    otherwise provides deterministic fallback behavior."""

    def __init__(self):
        self.api_key = LLM_API_KEY
        self.available = bool(self.api_key)

    def is_available(self):
        return self.available

    def explain(self, structured_result: dict, user_question: str) -> str:
        """Generate explanation from structured analytics result only."""
        # Deterministic fallback uses explanation module.
        # If LLM available, we would send structured payload; here we
        # keep it transparent and safe by always using structured output.
        from agent.explanation import build_explanation
        return build_explanation(structured_result, user_question)
