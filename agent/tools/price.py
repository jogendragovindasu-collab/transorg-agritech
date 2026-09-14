"""
agent/tools/price.py
-------------------
Price and MSP analytics from crop_kpis.csv and price_msp_analysis.csv.
"""
from pathlib import Path
import pandas as pd

ANALYTICS_DIR = Path("analytics")


def get_price_msp_analysis(params: dict) -> dict:
    # Load the validated price/MSP analysis data
    df = pd.read_csv(ANALYTICS_DIR / "price_msp_analysis.csv")

    # Extract crop from params if provided
    requested_crop = None
    if params.get("crop") and len(params["crop"]) > 0:
        # Take the first crop mentioned (assuming single crop query)
        requested_crop = params["crop"][0]
        # Filter data for this crop (case-insensitive match)
        mask = df["crop_name"].str.lower() == requested_crop.lower()
        if mask.any():
            df = df[mask]
        else:
            # If crop not found, fall back to full data and note in limitations
            requested_crop = None  # Reset to indicate fallback

    # Calculate averages
    avg_price = float(df["modal_price"].mean()) if not df.empty else 0.0
    avg_msp = float(df["msp"].mean()) if not df.empty else 0.0
    avg_gap = float((df["modal_price"] - df["msp"]).mean()) if not df.empty else 0.0

    # Determine source description
    if requested_crop and not df.empty:
        source_desc = f"analytics/price_msp_analysis.csv (filtered for {requested_crop})"
        evidence_desc = f"Based on validated price/MSP records for {requested_crop} ({len(df)} records)"
    else:
        source_desc = "analytics/price_msp_analysis.csv"
        evidence_desc = f"Calculated from {len(df)} price/MSP records using validated cleaned data"

    # Build summary
    if requested_crop and not df.empty:
        summary = f"{requested_crop}: Average modal price = Rs. {avg_price:,.0f}; Average MSP = Rs. {avg_msp:,.0f}; Average price gap above MSP = Rs. {avg_gap:,.0f}."
    else:
        summary = f"Average modal price: Rs. {avg_price:,.0f}; Average MSP: Rs. {avg_msp:,.0f}; Average price gap above MSP: Rs. {avg_gap:,.0f}."

    return {
        "summary": summary,
        "metrics": {
            "avg_modal_price": avg_price,
            "avg_msp": avg_msp,
            "avg_price_gap": avg_gap,
            "records_analyzed": int(len(df)),
        },
        "source": source_desc,
        "evidence": evidence_desc,
        "limitations": "Price gap reflects modal price minus MSP; negative values indicate below-MSP trading. No unsupported external market price data used. If crop not found in data, falls back to overall average.",
        "business_implication": "Consistent above-MSP gaps suggest market support effectiveness; investigate crops with high crash rates for targeted farmer support. For specific crops, compare their price gap to the overall average.",
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
