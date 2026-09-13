"""
agent/tools/crop.py
------------------
Crop-level analytics from crop_kpis.csv.
"""
from pathlib import Path
import pandas as pd

ANALYTICS_DIR = Path("analytics")


def get_crop_analysis(params: dict) -> dict:
    crop_df = pd.read_csv(ANALYTICS_DIR / "crop_kpis.csv")
    total_arrivals = float(crop_df["total_arrivals_qtl"].sum())
    top_crop = crop_df.iloc[0]
    top_3_pct = float(crop_df.head(3)["pct_of_total_arrivals"].sum())

    return {
        "summary": f"Canonical crop analysis covers {len(crop_df)} groups representing {total_arrivals:,.0f} Qtl. Top 3 crops account for {top_3_pct:.1f}% of total arrivals.",
        "metrics": {
            "total_canonical_crops": int(len(crop_df)),
            "total_arrivals_qtl": total_arrivals,
            "top_3_concentration_pct": float(top_3_pct),
            "top_crop_name": top_crop["crop_name"],
            "top_crop_arrivals_qtl": float(top_crop["total_arrivals_qtl"]),
        },
        "source": "analytics/crop_kpis.csv",
        "evidence": f"Top crop: {top_crop['crop_name']} ({top_crop['total_arrivals_qtl']:,.0f} Qtl, {top_crop['pct_of_total_arrivals']:.1f}%). Unresolved crop variants excluded (see data_quality_summary.csv).",
        "limitations": "Crop mapping excludes 9 unresolved variants (REQUIRES_INVESTIGATION). No unsupported weather-to-mandi attribution claimed.",
        "business_implication": "High crop concentration increases price vulnerability; investigate diversification options and MSP alignment for dominant crops.",
        "chart_type_hint": "donut_bar"
    }
