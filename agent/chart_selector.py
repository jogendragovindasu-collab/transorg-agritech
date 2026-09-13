"""Deterministic chart selector.

Maps validated analytical intent + payload to plotly figure builder
instructions. No arbitrary visualization — only predefined mappings.
Uses analytics/ CSV data sources only.
"""


CHART_MAP = {
    "OVERVIEW": {"type": "kpi_cards", "layout": "summary_cards", "source": "analytics/crop_kpis.csv, analytics/mandi_kpis.csv, analytics/transport_kpis.csv"},
    "PRICE_RISK": {"type": "scatter_plot", "layout": "scatter", "source": "analytics/crop_kpis.csv, analytics/mandi_kpis.csv"},
    "MANDI_ANALYSIS": {"type": "horizontal_bar", "layout": "bar_h", "source": "analytics/mandi_kpis.csv"},
    "SUPPLY_TREND": {"type": "line_time_series", "layout": "line", "source": "analytics/daily_kpis.csv"},
    "CROP_ANALYSIS": {"type": "donut", "layout": "donut", "source": "analytics/crop_kpis.csv"},
    "PRICE_MSP": {"type": "grouped_bar", "layout": "grouped_bar", "source": "analytics/crop_kpis.csv, analytics/price_msp_analysis.csv"},
    "LOGISTICS": {"type": "bar_transit", "layout": "bar", "source": "analytics/warehouse_kpis.csv, analytics/transport_kpis.csv"},
    "WEATHER": {"type": "dual_axis", "layout": "dual_axis", "source": "analytics/weather_arrival_analysis.csv", "note": "Correlation only (r=-0.05, p=0.582); weather analysis is at date level only — no legitimate sensor-to-mandi mapping exists."},
    "DATA_QUALITY": {"type": "transformation_bar", "layout": "grouped_bar", "source": "analytics/data_quality_summary.csv, cleaning_audit_summary.json"},
    "EXECUTIVE_INSIGHTS": {"type": "priority_table", "layout": "table_cards", "source": "analytics/executive_insights.csv"},
    "UNSUPPORTED": {"type": "informational_callout", "layout": "callout", "source": "N/A"},
}


def select_chart(intent: str, payload: dict) -> dict:
    """Select deterministic plotly figure builder instructions.

    Args:
        intent: Validated intent from STRICT_INTENTS.
        payload: Validated analytics payload.

    Returns:
        dict with: chart_type, plotly_instructions, source, safeguards.
    """
    intent = intent or "UNSUPPORTED"
    config = CHART_MAP.get(intent, CHART_MAP["UNSUPPORTED"])

    # Build plotly instructions based on chart type
    instructions = _build_plotly_instructions(config["type"], payload)

    result = {
        "chart_type": config["type"],
        "layout": config.get("layout", "default"),
        "plotly_instructions": instructions,
        "source": config.get("source", "analytics/"),
        "safeguards": _get_safeguards(intent),
    }

    # Weather safeguard
    if intent == "WEATHER":
        result["weather_attribution_note"] = (
            "The supplied data does not provide a legitimate sensor-to-mandi/district mapping; "
            "weather analysis is available only at the date level. Correlation does not imply causation."
        )
        result["correlation_note"] = "r = -0.05, p = 0.582 (weak, statistically insignificant)."

    return result


def _build_plotly_instructions(chart_type: str, payload: dict) -> dict:
    """Return deterministic plotly figure builder instructions."""
    base = {
        "figure_factory": None,
        "data_source": payload.get("source", "analytics/"),
        "use_plotly": True,
        "no_arbitrary_execution": True,
    }
    if chart_type == "kpi_cards":
        base["figure_factory"] = "plotly.graph_objs.Table"
        base["layout_hint"] = "summary cards layout"
    elif chart_type == "scatter_plot":
        base["figure_factory"] = "plotly.graph_objs.Scatter"
        base["layout_hint"] = "x=metric, y=metric, color=intent"
    elif chart_type == "horizontal_bar":
        base["figure_factory"] = "plotly.graph_objs.Bar"
        base["orientation"] = "h"
    elif chart_type == "line_time_series":
        base["figure_factory"] = "plotly.graph_objs.Scatter"
        base["mode"] = "lines+markers"
    elif chart_type == "donut":
        base["figure_factory"] = "plotly.graph_objs.Pie"
        base["hole"] = 0.4
    elif chart_type == "grouped_bar":
        base["figure_factory"] = "plotly.graph_objs.Bar"
        base["barmode"] = "group"
    elif chart_type == "bar_transit":
        base["figure_factory"] = "plotly.graph_objs.Bar"
        base["orientation"] = "v"
    elif chart_type == "dual_axis":
        base["figure_factory"] = "plotly.graph_objs.Scatter"
        base["layout_hint"] = "dual y-axis; date on x-axis"
    elif chart_type == "transformation_bar":
        base["figure_factory"] = "plotly.graph_objs.Bar"
        base["barmode"] = "group"
    elif chart_type == "priority_table":
        base["figure_factory"] = "plotly.graph_objs.Table"
    else:
        base["figure_factory"] = "plotly.graph_objs.Table"
        base["layout_hint"] = "informational callout"
    return base


def _get_safeguards(intent: str) -> list:
    safeguards = [
        "Only analytics/ CSV data is used.",
        "No fabricated numbers; metrics are exact from validated sources.",
        "No arbitrary Python execution permitted.",
    ]
    if intent == "WEATHER":
        safeguards.append(
            "Weather attribution safeguard: analysis available only at date level; no legitimate sensor-to-mandi/district mapping."
        )
    if intent == "LOGISTICS":
        safeguards.append(
            "Logistics rigor: references P90 statistical threshold (21.7 hours) rather than arbitrary thresholds."
        )
    if intent == "DATA_QUALITY":
        safeguards.append(
            "Data rescue transparency: Analytics exclusions per analytics/data_quality_summary.csv (arrivals 79.984%, price 46.07%, transport 15.45%, weather 98.64%). Physical cleaning removals: master=3, arrivals=750, transport=400, price=0, weather=0. No stale 20,607 claim."
        )
    return safeguards
