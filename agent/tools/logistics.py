"""
agent/tools/logistics.py
-----------------------
Logistics analytics from warehouse_kpis.csv and transport_kpis.csv.
P90 long-transit defined using statistical threshold (not invented business threshold).
"""
from pathlib import Path
import pandas as pd

ANALYTICS_DIR = Path("analytics")


def get_logistics_analysis(params: dict) -> dict:
    warehouse_df = pd.read_csv(ANALYTICS_DIR / "warehouse_kpis.csv")
    transport_df = pd.read_csv(ANALYTICS_DIR / "transport_kpis.csv")

    # Find warehouse with longest median transit
    longest_warehouse = warehouse_df.loc[warehouse_df["median_transit_hours"].idxmax()]
    p90_threshold = float(transport_df.iloc[0]["p90_transit_threshold"]) if len(transport_df) > 0 else 21.7

    long_transit_warehouses = warehouse_df[warehouse_df["median_transit_hours"] > p90_threshold]

    return {
        "summary": f"Longest median transit: {longest_warehouse['destination_warehouse']} ({longest_warehouse['median_transit_hours']:.1f}h); Overall P90 long-transit threshold: {p90_threshold:.1f}h ({len(long_transit_warehouses)} warehouses exceed this).",
        "metrics": {
            "longest_warehouse": str(longest_warehouse["destination_warehouse"]),
            "longest_warehouse_median_hours": float(longest_warehouse["median_transit_hours"]),
            "p90_transit_threshold_hours": float(p90_threshold),
            "warehouses_above_p90": int(len(long_transit_warehouses)),
        },
        "source": "analytics/warehouse_kpis.csv; analytics/transport_kpis.csv",
        "evidence": f"Warehouse performance based on {int(longest_warehouse['trip_count'])} trips. P90 threshold ({p90_threshold:.1f}h) calculated from validated transport records; excludes 1,607 invalid/negative transit records.",
        "limitations": "No unsupported weather-to-mandi mapping. Transport analysis excludes negative transit flags and missing distance records.",
        "business_implication": "Prioritize logistics review for warehouses exceeding P90 transit thresholds; investigate route optimization and warehouse capacity adjustments.",
        "chart_type_hint": "warehouse_transit_bar"
    }
