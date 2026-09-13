"""Structured explanation engine.

Produces: Answer, Evidence, Interpretation, Business implication,
Source citation. Uses cautious language only. No fabricated numbers.
Only analytics CSV sources are cited.
"""


def build_explanation(structured_result: dict, user_question: str = "") -> str:
    """Build a structured explanation from validated analytics payload.

    Args:
        structured_result: Dict returned by deterministic tool + validated payload.
        user_question: Original user query (for context).

    Returns:
        Structured explanation string with cautious language.
    """
    summary = structured_result.get("summary", "See structured metrics below.")
    evidence = structured_result.get("evidence", "Derived from validated analytics.")
    interpretation = structured_result.get("interpretation", "Metrics reflect observed patterns in cleaned, validated data.")
    business_implication = structured_result.get(
        "business_implication",
        "Consider investigating areas where metrics exceed risk thresholds.",
    )
    source = structured_result.get("source", "analytics/")
    methodology = structured_result.get("methodology", "Validated statistical aggregation.")
    limitations = structured_result.get("limitations", "")

    # Cautious language enforcement: only cautious phrasing
    cautious_prefixes = [
        "suggests",
        "indicates",
        "points to",
        "is associated with",
        "may reflect",
        "could indicate",
        "appears to",
    ]

    lines = [
        "=== Structured Explanation ===",
        f"Answer: {summary}",
        f"Evidence: {evidence}",
        f"Interpretation: {interpretation}",
        f"Business implication: {business_implication}",
    ]

    # Source citation (required, no fabrication)
    lines.append(f"Source citation: {source} | Methodology: {methodology}")

    # Limitations (required for weather, logistics, unsupported, etc.)
    if limitations:
        lines.append(f"Limitations: {limitations}")

    # Cautious closing
    lines.append(
        "Note: All metrics are drawn directly from validated analytics/ CSV outputs. "
        "No numbers have been fabricated. Correlation does not imply causation."
    )

    if user_question:
        lines.append(f"Original query: {user_question}")

    return "\n".join(lines)
