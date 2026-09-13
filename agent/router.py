"""Intent router — maps validated intent to deterministic tool handler.

No arbitrary Python execution. Only registered functions from agent/tools
are invoked. Unsupported queries get safe fallback.
"""
from agent.intent_parser import STRICT_INTENTS

# Registered tool mapping (deterministic only)
TOOL_MAP = {
    "OVERVIEW": "agent.tools.overview.get_overview",
    "PRICE_RISK": "agent.tools.price.get_price_risk",
    "MANDI_ANALYSIS": "agent.tools.mandi.get_mandi_analysis",
    "SUPPLY_TREND": "agent.tools.supply.get_supply_trend",
    "CROP_ANALYSIS": "agent.tools.crop.get_crop_analysis",
    "PRICE_MSP": "agent.tools.price.get_price_msp_analysis",
    "LOGISTICS": "agent.tools.logistics.get_logistics_analysis",
    "WEATHER": "agent.tools.weather.get_weather_analysis",
    "DATA_QUALITY": "agent.tools.data_quality.get_data_quality",
    "EXECUTIVE_INSIGHTS": "agent.tools.executive_insights.get_insights",
}

UNSUPPORTED_FALLBACK = {
    "intent": "UNSUPPORTED",
    "summary": "This query is out of scope or unsupported with the current validated analytics dataset.",
    "evidence": "No validated metric matches the request.",
    "interpretation": "The agent only responds to questions backed by analytics/ CSV outputs.",
    "business_implication": "Consider reformulating with supported keywords (e.g., price risk, mandi, weather at date level, logistics, data quality, executive insights, supply, crop analysis).",
    "limitations": "Unsupported or ambiguous query; no arbitrary execution allowed.",
    "source": "agent/router fallback",
    "methodology": "Safe unsupported query handler — no fabrication.",
    "metrics": {},
}


class RouterError(Exception):
    pass


def route_intent(intent: str) -> dict:
    """Return registered tool reference and handler info.

    Args:
        intent: One of STRICT_INTENTS.

    Returns:
        dict with: intent, tool_path, handler_name, is_registered.
    """
    if intent not in STRICT_INTENTS:
        return {
            "intent": "UNSUPPORTED",
            "tool_path": None,
            "handler_name": None,
            "is_registered": False,
            "fallback": UNSUPPORTED_FALLBACK,
        }

    tool_path = TOOL_MAP.get(intent)
    handler_name = None
    if tool_path:
        handler_name = tool_path.split(".")[-1]  # e.g., get_overview
    return {
        "intent": intent,
        "tool_path": tool_path,
        "handler_name": handler_name,
        "is_registered": intent in TOOL_MAP,
        "fallback": UNSUPPORTED_FALLBACK if not handler_name else None,
    }
