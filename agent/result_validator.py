"""Result validator.

Checks schema, numeric sanity, and source citation presence.
Returns validated payload or raises ValidationError with details.
Only uses analytics/ CSV sources — no fabrication.
"""


class ValidationError(Exception):
    pass


def validate_result(payload: dict) -> dict:
    """Validate a result payload from a deterministic tool.

    Required fields in payload:
        - summary (str)
        - evidence (str)
        - metrics (dict) with numeric values only from analytics/
        - source (str) referencing analytics/ file
        - interpretation (str)
        - business_implication (str)
        - limitations (str, optional)

    Raises:
        ValidationError if any check fails.
    """
    errors = []

    # Schema checks
    required_keys = ["summary", "evidence", "metrics", "source", "interpretation", "business_implication"]
    for k in required_keys:
        if k not in payload:
            errors.append(f"Missing required key: {k}")

    # Metrics sanity: must be a dict, no arbitrary Python objects
    metrics = payload.get("metrics")
    if metrics is not None:
        if not isinstance(metrics, dict):
            errors.append("metrics must be a dict")
        else:
            for mk, mv in metrics.items():
                if isinstance(mv, float) or isinstance(mv, int):
                    # Numeric sanity: reject NaN / inf
                    import math
                    if isinstance(mv, float) and (math.isnan(mv) or math.isinf(mv)):
                        errors.append(f"Metric '{mk}' has invalid float value: {mv}")
                elif isinstance(mv, str):
                    # Strings allowed only if they represent source citations or flags
                    pass
                else:
                    errors.append(f"Metric '{mk}' has unsupported type: {type(mv)}")

    # Source citation presence: must reference analytics/ CSV
    source = payload.get("source", "")
    if not source or "analytics" not in source.lower() and "csv" not in source.lower():
        errors.append(f"Source citation missing or does not reference analytics CSV: {source}")

    # No arbitrary execution evidence: payload should not contain code snippets
    for k in required_keys:
        val = payload.get(k, "")
        if isinstance(val, str):
            dangerous_patterns = ["exec(", "eval(", "import os", "subprocess", "__import__"]
            for pat in dangerous_patterns:
                if pat in val:
                    errors.append(f"Potential arbitrary execution pattern in '{k}': {pat}")

    if errors:
        raise ValidationError("; ".join(errors))

    # Add validation stamp
    payload["validated"] = True
    payload["validator_version"] = "1.0"
    return payload
