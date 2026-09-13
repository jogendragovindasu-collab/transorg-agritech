"""
agent/tools/mandi.py
-------------------
Mandi-level analytics from mandi_kpis.csv.
"""
from pathlib import Path
import pandas as pd

ANALYTICS_DIR = Path("analytics")


def get_mandi_analysis(params: dict) -> dict:
    mandi_df = pd.read_csv(ANALYTICS_DIR / "mandi_kpis.csv")
    top_5 = mandi_df.nlargest(5, "total_arrival_qty_qtl")
    top_5_mandis = ", ".join(top_5["mandi_name"].tolist())
    top_5_volume = float(top_5["total_arrival_qty_qtl"].sum())
    total_volume = float(mandi_df["total_arrival_qty_qtl"].sum())
    concentration_pct = (top_5_volume / total_volume * 100) if total_volume > 0 else 0.0

    # Identify high-volume + high crash mandis (demonstration for datathon requirement)
    high_risk = mandi_df[mandi_df["price_below_msp_rate"] > 30].sort_values("total_arrival_qty_qtl", ascending=False)
    if len(high_risk) > 0:
        top_risk = high_risk.iloc[0]
        risk_evidence = f"{top_risk['mandi_name']} ({top_risk['district']}, {top_risk['state']}) has {top_risk['total_arrival_qty_qtl']:,.0f} Qtl arrivals with {top_risk['price_below_msp_rate']:.1f}% below-MSP rate."
    else:
        risk_evidence = "No mandi exceeds 30% below-MSP rate in validated analytics."

    return {
        "summary": f"Top 5 mandis contribute {concentration_pct:.1f}% of total arrivals. Key high-volume/high-risk mandi identified.",
        "metrics": {
            "top_5_concentration_pct": float(concentration_pct),
            "total_active_mandis": int(len(mandi_df)),
            "highest_volume_mandi": top_5.iloc[0]["mandi_name"] if len(top_5) > 0 else "N/A",
            "highest_volume_qtl": float(top_5.iloc[0]["total_arrival_qty_qtl"]) if len(top_5) > 0 else 0.0,
        },
        "source": "analytics/mandi_kpis.csv",
        "evidence": risk_evidence,
        "limitations": "Mandi-level weather attribution unsupported (no sensor-to-district mapping). Volume and price crash rates derived from cleaned, validated records only.",
        "business_implication": "Investigate high-volume/high-crash mandis (e.g., priority monitoring, farmer price support review) to reduce supply-chain vulnerability.",
        "chart_type_hint": "horizontal_bar"
    }
