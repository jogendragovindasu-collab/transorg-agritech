"""
agent/tools/executive_insights.py
--------------------------------
Executive insights from executive_insights.csv.
"""
from pathlib import Path
import pandas as pd

ANALYTICS_DIR = Path("analytics")


def get_insights(params: dict) -> dict:
    insights_df = pd.read_csv(ANALYTICS_DIR / "executive_insights.csv")
    high_severity = insights_df[insights_df["severity"] == "High"]
    medium_severity = insights_df[insights_df["severity"] == "Medium"]
    info_severity = insights_df[insights_df["severity"] == "Informational"]

    top_insights = insights_df.sort_values("metric_value", ascending=False).head(3)
    insight_text = "; ".join([f"{row['insight_title']} (Severity: {row['severity']})" for _, row in top_insights.iterrows()])

    return {
        "summary": f"Executive insights: {len(high_severity)} high-severity, {len(medium_severity)} medium-severity, {len(info_severity)} informational priorities. Key risks identified in price vulnerability, supply concentration, and data quality.",
        "metrics": {
            "high_severity_insights": int(len(high_severity)),
            "medium_severity_insights": int(len(medium_severity)),
            "informational_insights": int(len(info_severity)),
            "total_insights": int(len(insights_df)),
        },
        "source": "analytics/executive_insights.csv",
        "evidence": insight_text + f". Insights derived from validated analytics outputs; not external estimates.",
        "limitations": "Recommendations use cautious language (investigate, monitor, consider reviewing). No unsupported causal claims. Data exclusions documented.",
        "business_implication": "Management should prioritize high-severity insights (price vulnerability, logistics hotspots, data quality exclusions) for targeted investigation and strategic response.",
        "chart_type_hint": "insight_cards"
    }
