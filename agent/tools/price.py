"""
agent/tools/price.py
-------------------
Price and MSP analytics from crop_kpis.csv and price_msp_analysis.csv.
"""
from pathlib import Path
import pandas as pd

ANALYTICS_DIR = Path("analytics")


def get_price_msp_analysis(params: dict) -> dict:
    crop_df = pd.read_csv(ANALYTICS_DIR / "crop_kpis.csv")
    avg_price = float(crop_df["avg_modal_price"].mean())
    avg_msp = float(crop_df["avg_msp"].mean())
    avg_gap = float((crop_df["avg_modal_price"] - crop_df["avg_msp"]).mean())

    return {
        "summary": f"Average modal price: Rs. {avg_price:,.0f}; Average MSP: Rs. {avg_msp:,.0f}; Average price gap above MSP: Rs. {avg_gap:,.0f}.",
        "metrics": {
            "avg_modal_price": avg_price,
            "avg_msp": avg_msp,
            "avg_price_gap": avg_gap,
            "crop_groups_analyzed": int(len(crop_df)),
        },
        "source": "analytics/crop_kpis.csv",
        "evidence": f"Calculated from {len(crop_df)} canonical crop groups using validated cleaned price records (excludes invalid numeric / unresolved prices).",
        "limitations": "Price crash rate reflects below-MSP trading frequency, not absolute loss magnitude. No unsupported external market price data used.",
        "business_implication": "Consistent above-MSP gaps suggest market support effectiveness; investigate crops with high crash rates for targeted farmer support.",
        "chart_type_hint": "grouped_bar"
    }


def get_price_risk(params: dict) -> dict:
    crop_df = pd.read_csv(ANALYTICS_DIR / "crop_kpis.csv")
    # Sort by crash rate descending to show highest risk
    sorted_df = crop_df.sort_values("price_crash_rate", ascending=False)
    top_risk = sorted_df.iloc[0]
    crash_rate = float(top_risk["price_crash_rate"])
    volume = float(top_risk["total_arrivals_qtl"])

    # Identify volume vs crash rate vulnerability
    high_vol_high_risk = crop_df[(crop_df["total_arrivals_qtl"] > crop_df["total_arrivals_qtl"].median()) & (crop_df["price_crash_rate"] > 30)]

    return {
        "summary": f"Highest price risk crop: {top_risk['crop_name']} — {crash_rate:.1f}% below-MSP rate across {volume:,.0f} Qtl. {len(high_vol_high_risk)} high-volume/high-crash crops identified.",
        "metrics": {
            "highest_risk_crop": top_risk["crop_name"],
            "highest_crash_rate_pct": crash_rate,
            "highest_risk_volume_qtl": volume,
            "high_volume_high_risk_count": int(len(high_vol_high_risk)),
        },
        "source": "analytics/crop_kpis.csv",
        "evidence": f"Based on validated price records (excludes missing/invalid modal prices and MSP). Top risk: {top_risk['crop_name']}. High volume + high crash crops: {len(high_vol_high_risk)}.",
        "interpretation": "Price vulnerability reflects frequency of below-MSP trading, not total economic loss. This is an observed association in validated cleaned data.",
        "business_implication": "Investigate price vulnerability for high-volume/high-crash crops; prioritize monitoring and potential MSP adjustment or market intervention.",
        "limitations": "Price vulnerability reflects frequency of below-MSP transactions (crash rate), not total economic loss. Unresolved crop variants excluded from analysis.",
        "methodology": "Validated statistical aggregation from analytics/crop_kpis.csv.",
        "chart_type_hint": "scatter_matrix"
    }
