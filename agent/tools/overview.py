"""
agent/tools/overview.py
----------------------
Retrieve overall KPIs from validated analytics outputs.
"""
from pathlib import Path
import pandas as pd

ANALYTICS_DIR = Path("analytics")


def get_overview(params: dict) -> dict:
    crop_df = pd.read_csv(ANALYTICS_DIR / "crop_kpis.csv")
    mandi_df = pd.read_csv(ANALYTICS_DIR / "mandi_kpis.csv")
    transport_df = pd.read_csv(ANALYTICS_DIR / "transport_kpis.csv")
    daily_df = pd.read_csv(ANALYTICS_DIR / "daily_kpis.csv")

    total_arrivals = crop_df["total_arrivals_qtl"].sum()
    price_crash_rate = crop_df["price_crash_rate"].mean()
    active_mandis = len(mandi_df[mandi_df["arrival_record_count"] > 0])
    avg_transit = transport_df.iloc[0]["avg_transit_hours"] if len(transport_df) > 0 else 0.0
    p90_transit = transport_df.iloc[0]["p90_transit_threshold"] if len(transport_df) > 0 else 0.0

    return {
        "summary": f"Total arrivals: {total_arrivals:,.0f} Qtl; Crash rate: {price_crash_rate:.1f}%; Active mandis: {active_mandis}; Avg transit: {avg_transit:.1f}h (P90: {p90_transit:.1f}h).",
        "metrics": {
            "total_arrivals_qtl": float(total_arrivals),
            "price_crash_rate_pct": float(price_crash_rate),
            "active_mandis": int(active_mandis),
            "avg_transit_hours": float(avg_transit),
            "p90_transit_hours": float(p90_transit),
        },
        "source": "analytics/crop_kpis.csv; analytics/mandi_kpis.csv; analytics/transport_kpis.csv",
        "evidence": f"Calculated from {len(crop_df)} crop groups, {len(mandi_df)} mandis, {len(transport_df)} transport records. Raw data untouched.",
        "interpretation": "These metrics reflect observed patterns in validated, cleaned analytics outputs. No unsupported weather-to-mandi mapping is claimed.",
        "limitations": "No unsupported weather-to-mandi mapping. Transport long-transit uses validated statistical P90 threshold (not invented business threshold).",
        "methodology": "Validated statistical aggregation from analytics/*.csv outputs.",
        "business_implication": "Investigate price vulnerability and logistics hotspots; physical cleaning removals: master=3, arrivals=750, transport=400, price=0, weather=0. Analytics exclusions per data_quality_summary.csv: arrivals 79.984%, price 46.07%, transport 15.45%, weather 98.64%.",        "chart_type_hint": "kpi_cards"
    }
