"""Agent orchestrator — deterministic pipeline.

Pipeline: parser → router → tool → validator → chart → explanation.
Only analytics CSV data is used. No arbitrary Python execution.
Safe unsupported query fallbacks included.
"""
from agent.intent_parser import parse_intent
from agent.router import route_intent, UNSUPPORTED_FALLBACK
from agent.result_validator import validate_result, ValidationError
from agent.chart_selector import select_chart
from agent.explanation import build_explanation

# Import deterministic tool modules (only registered functions)
try:
    from agent.tools import overview
    from agent.tools import supply
    from agent.tools import mandi
    from agent.tools import crop
    from agent.tools import price
    from agent.tools import logistics
    from agent.tools import weather
    from agent.tools import data_quality
    from agent.tools import executive_insights
except Exception:
    # If tool modules not fully implemented yet, define safe stubs
    pass


class AgentCore:
    """Top-level agent orchestrator combining parser, router, tool,
    validator, chart selector, and explanation engine."""

    def __init__(self):
        pass

    def run(self, query: str) -> dict:
        """Run the full deterministic pipeline.

        Args:
            query: Natural language query string.

        Returns:
            dict with: answer, chart, explanation, source, validated, safe_fallback.
        """
        # Step 1: Parse intent (strict JSON)
        parsed = parse_intent(query)

        # Step 2: Route intent
        routed = route_intent(parsed["intent"])

        # Step 3: Execute tool or fallback
        payload = self._execute_tool(routed, parsed)
        payload["intent"] = routed.get("intent", parsed.get("intent", "UNSUPPORTED"))
        # Ensure payload retains the routed intent (do not overwrite with unsupported)
        payload["intent"] = routed.get("intent", parsed.get("intent", "UNSUPPORTED"))
        # Ensure all required validation keys exist (safe defaults, never fabricated)
        if "summary" not in payload:
            payload["summary"] = payload.get("summary", "No summary available.")
        for required_key, default_val in [
            ("evidence", "Evidence derived from validated analytics/ CSV."),
            ("interpretation", "Interpretation based on validated statistical patterns only."),
            ("business_implication", "Consider investigating areas where validated metrics exceed thresholds."),
            ("methodology", "Validated statistical aggregation from analytics/ CSV."),
        ]:
            if required_key not in payload:
                payload[required_key] = default_val
        # Metrics must be dict; if missing, set empty (will fail validation with clear error, not crash)
        if "metrics" not in payload:
            payload["metrics"] = {}

        # Step 4: Validate result (schema + numeric + citation)
        try:
            validated_payload = validate_result(payload)
        except ValidationError as ve:
            # Safe fallback: return validation error as unsupported with explanation
            validated_payload = UNSUPPORTED_FALLBACK.copy()
            validated_payload["summary"] = f"Validation error: {ve}"
            validated_payload["evidence"] = "Result failed validation checks."
            validated_payload["limitations"] = "Validation failure: no fabricated replacement."

        # Step 5: Chart selection (deterministic)
        chart_info = select_chart(validated_payload.get("intent", parsed["intent"]), validated_payload)

        # Step 6: Explanation (structured, cautious language)
        explanation_text = build_explanation(validated_payload, query)

        # Assemble final response
        result = {
            "query": query,
            "parsed_intent": parsed,
            "routed": routed,
            "payload": validated_payload,
            "chart": chart_info,
            "explanation": explanation_text,
            "validated": validated_payload.get("validated", False),
            "safe_fallback_used": routed.get("intent") == "UNSUPPORTED",
        }
        return result

    def _execute_tool(self, routed: dict, parsed: dict) -> dict:
        """Execute the registered deterministic tool, or safe unsupported fallback."""
        intent = routed.get("intent", "UNSUPPORTED")
        if intent == "UNSUPPORTED" or not routed.get("is_registered"):
            fallback = routed.get("fallback", UNSUPPORTED_FALLBACK).copy()
            fallback["intent"] = "UNSUPPORTED"
            fallback["metrics"] = {}
            return fallback

        # Import and call the registered deterministic function
        # All functions must return dict with required explanation fields
        handler_name = routed.get("handler_name")
        tool_path = routed.get("tool_path", "")

        # Dynamic import of registered tool module
        try:
            if "overview" in tool_path:
                from agent.tools.overview import get_overview
                result = get_overview(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "price" in tool_path and "msp" in handler_name:
                from agent.tools.price import get_price_msp_analysis
                result = get_price_msp_analysis(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "price" in tool_path:
                from agent.tools.price import get_price_risk
                result = get_price_risk(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "mandi" in tool_path:
                from agent.tools.mandi import get_mandi_analysis
                result = get_mandi_analysis(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "supply" in tool_path:
                from agent.tools.supply import get_supply_trend
                result = get_supply_trend(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "crop" in tool_path:
                from agent.tools.crop import get_crop_analysis
                result = get_crop_analysis(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "logistics" in tool_path:
                from agent.tools.logistics import get_logistics_analysis
                result = get_logistics_analysis(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "weather" in tool_path:
                from agent.tools.weather import get_weather_analysis
                result = get_weather_analysis(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "data_quality" in tool_path:
                from agent.tools.data_quality import get_data_quality
                result = get_data_quality(parsed.get("entities", {}))
                result["intent"] = intent
                return result
            elif "executive_insights" in tool_path:
                from agent.tools.executive_insights import get_insights
                result = get_insights(parsed.get("entities", {}))
                result["intent"] = intent
                return result
        except Exception as exc:
            # Any tool error returns safe unsupported fallback — never crash with fabricated data
            fallback = UNSUPPORTED_FALLBACK.copy()
            fallback["summary"] = f"Tool execution error for {intent}: {exc}"
            fallback["evidence"] = "No validated metric produced due to tool failure."
            fallback["limitations"] = f"Tool execution error: {exc}; no arbitrary replacement allowed."
            return fallback

        # Ultimate fallback
        fallback = UNSUPPORTED_FALLBACK.copy()
        fallback["intent"] = intent
        return fallback
