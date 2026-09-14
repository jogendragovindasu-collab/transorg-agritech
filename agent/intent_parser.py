"""Structured intent parser.

Extracts intent, crop, mandi, and other entities using keyword rules
plus optional LLM parsing with strict deterministic fallback.
Returns strict JSON only — no arbitrary Python execution.
"""
import re
import json

STRICT_INTENTS = [
    "OVERVIEW",
    "PRICE_RISK",
    "MANDI_ANALYSIS",
    "SUPPLY_TREND",
    "CROP_ANALYSIS",
    "PRICE_MSP",
    "LOGISTICS",
    "WEATHER",
    "DATA_QUALITY",
    "EXECUTIVE_INSIGHTS",
    "UNSUPPORTED",
]

KEYWORD_MAP = {
    "weather": "WEATHER",
    "rain": "WEATHER",
    "rainfall": "WEATHER",
    "correlation": "WEATHER",
    "association": "WEATHER",
    "overview": "OVERVIEW",
    "summary": "OVERVIEW",
    "high-level": "OVERVIEW",
    "price risk": "PRICE_RISK",
    "below msp": "PRICE_RISK",
    "crash": "PRICE_RISK",
    "mandi": "MANDI_ANALYSIS",
    "mandis": "MANDI_ANALYSIS",
    "volume": "MANDI_ANALYSIS",
    "supply": "SUPPLY_TREND",
    "arrival": "SUPPLY_TREND",
    "trend": "SUPPLY_TREND",
    "crop": "CROP_ANALYSIS",
    "crops": "CROP_ANALYSIS",
    "wheat": "CROP_ANALYSIS",
    "cotton": "CROP_ANALYSIS",
    "rice": "CROP_ANALYSIS",
    "sugarcane": "CROP_ANALYSIS",
    "mustard": "CROP_ANALYSIS",
    "price": "PRICE_MSP",
    "price of": "PRICE_MSP",
    "msp": "PRICE_MSP",
    "price vs msp": "PRICE_MSP",
    "logistics": "LOGISTICS",
    "warehouse": "LOGISTICS",
    "transit": "LOGISTICS",
    "weather": "WEATHER",
    "rain": "WEATHER",
    "rainfall": "WEATHER",
    "correlation": "WEATHER",
    "association": "WEATHER",
    "data quality": "DATA_QUALITY",
    "cleaning": "DATA_QUALITY",
    "rescue": "DATA_QUALITY",
    "executive": "EXECUTIVE_INSIGHTS",
    "insight": "EXECUTIVE_INSIGHTS",
}

# Crop / mandi extraction keywords
CROP_NAMES = ["wheat", "cotton", "sugarcane", "mustard", "rice", "maize", "barley"]
MANDI_KEYWORDS = ["mandi", "market", "grain"]


class IntentParseError(Exception):
    pass


def parse_intent(query: str) -> dict:
    """Parse a natural-language query into strict JSON.

    Returns:
        dict with keys:
            intent: str (one of STRICT_INTENTS)
            entities: dict (crop: list[str], mandi: list[str], etc.)
            query_lower: str
            raw_query: str
            supported: bool
    """
    if not query or not isinstance(query, str):
        return {
            "intent": "UNSUPPORTED",
            "entities": {"crop": [], "mandi": [], "date": None},
            "query_lower": "",
            "raw_query": str(query),
            "supported": False,
        }

    query_lower = query.lower().strip()
    entities = {"crop": [], "mandi": [], "date": None}

    # Extract crop entities
    for crop in CROP_NAMES:
        if crop in query_lower:
            entities["crop"].append(crop.capitalize())
    if entities["crop"]:
        entities["crop"] = list(dict.fromkeys(entities["crop"]))

    # Extract mandi hints (simplified: look for capitalized words near mandi refs)
    # We do not invent mandi names; only detect presence.
    mandi_refs = ["jand", "jorhat", "tadipatri", "chapra", "bijapur", "south dumdum", "kurukshetra", "hisar"]
    for m in mandi_refs:
        if m in query_lower:
            entities["mandi"].append(m.capitalize())
    if entities["mandi"]:
        entities["mandi"] = list(dict.fromkeys(entities["mandi"]))

    # Prioritize price/MSP when price-related keywords appear (even with crop names present)
    matched_intent = None
    price_indicators = ["price", "price of", "msp"]
    if any(ind in query_lower for ind in price_indicators):
        # If price keyword is present, prefer PRICE_MSP (unless risk/crash keywords dominate)
        risk_indicators = ["price risk", "below msp", "crash"]
        has_risk_only = any(ind in query_lower for ind in risk_indicators)
        if not has_risk_only:
            matched_intent = "PRICE_MSP"

    # Intent classification — keyword rules first, then fallback
    if matched_intent is None:
        for kw, intent in KEYWORD_MAP.items():
            if kw in query_lower:
                matched_intent = intent
                break

    if matched_intent is None:
        # Try LLM-enhanced parsing if available (optional); always safe fallback
        matched_intent = _llm_intent_fallback(query_lower)

    # Block arbitrary/code requests: detect arbitrary/code indicators first
    arbitrary_indicators = ["generate", "execute", "python", "sql", "run", "script", "create", "build"]
    has_arbitrary = any(ind in query_lower for ind in arbitrary_indicators)
    # Block arbitrary/code requests: if query contains arbitrary indicators (generate sql, execute, etc.), force unsupported regardless of analytics keywords
    if has_arbitrary:
        matched_intent = "UNSUPPORTED"
    # Safety: reject arbitrary intent values
    if matched_intent not in STRICT_INTENTS:
        matched_intent = "UNSUPPORTED"

    # Unsupported safeguard: if no entities and no strong keyword, flag unsupported
    if matched_intent == "UNSUPPORTED" and not entities["crop"] and not entities["mandi"]:
        pass  # already unsupported

    return {
        "intent": matched_intent,
        "entities": entities,
        "query_lower": query_lower,
        "raw_query": query,
        "supported": matched_intent != "UNSUPPORTED",
    }


def _llm_intent_fallback(query_lower: str) -> str:
    """Optional LLM fallback; if unavailable, uses deterministic heuristics."""
    # Read optional LLM provider, but never rely on it for correctness.
    try:
        from agent.llm import LLMProvider
        provider = LLMProvider()
        if provider.is_available():
            # In a full system, this would call provider.parse(query).
            # Here we enforce deterministic fallback for reproducibility.
            pass
    except Exception:
        pass

    # Deterministic heuristics for common unsupported patterns
    unsupported_patterns = ["predict future", "forecast 2025", "generate sql", "execute", "code", "sql query", "run query", "python code"]
    for pat in unsupported_patterns:
        if pat in query_lower:
            return "UNSUPPORTED"

    # Strong unsupported detection for arbitrary/code requests
    arbitrary_indicators = ["generate", "execute", "python", "sql", "run", "script"]
    has_analytics_keyword = any(kw in query_lower for kw in KEYWORD_MAP.keys())
    if any(ind in query_lower for ind in arbitrary_indicators) and "analytics" not in query_lower:
        return "UNSUPPORTED"
    # If we reached here with a matched analytics keyword, keep it; otherwise unsupported
    # Note: matched_intent in this scope refers to the variable set in parse_intent before this call.
    # Since the LLM fallback is called only when matched_intent is None, we must handle both cases:
    # If no analytics keyword matched previously, this fallback should always return UNSUPPORTED.
    # Only if analytics keywords exist in the query but weren't matched by the first loop (edge case),
    # we could try to determine a best guess from keywords in query_lower directly.
    # For deterministic behavior: default to UNSUPPORTED when matched_intent is None at this point.
    return "UNSUPPORTED"
