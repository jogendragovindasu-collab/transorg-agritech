# Agent Design — Step 8: Agri Intelligence Agent
## TransOrg AgentIQ Datathon — Track 3: AgriTech

**Status:** Implementation Phase  
**Date:** 2026-09-12  
**Grounding Source:** `analytics/` (primary), `data/cleaned/` (secondary)  

---

## 1. Agent Objective

The Agri Intelligence Agent converts validated analytics outputs into accessible, natural-language business intelligence. Its purpose is NOT to replace the analyst but to accelerate their access to grounded answers, charts, and business implications.

The agent must:
- Understand structured user intent.
- Route to deterministic analytical tools.
- Generate validated visualizations.
- Provide explanations grounded exclusively in project analytics.

---

## 2. Architecture

```
Natural Language Input
    ↓
Intent Parser (keyword + structured extraction + optional LLM)
    ↓
Intent Validator (supported intents only; unsupported → safe fallback)
    ↓
Tool Router (deterministic mapping: intent → analytics function)
    ↓
Analytics Tool (reads analytics CSV; never generates synthetic numbers)
    ↓
Result Validator (checks schema, source citation, numeric sanity)
    ↓
Chart Selector (deterministic chart mapping based on payload)
    ↓
Grounded Explanation Generator (structured narrative from validated results)
    ↓
Response (Answer + Metrics + Chart + Business Implication + Source)
```

---

## 3. Intents Supported

1. OVERVIEW
2. SUPPLY_TREND
3. MANDI_ANALYSIS
4. CROP_ANALYSIS
5. PRICE_MSP
6. PRICE_RISK
7. LOGISTICS
8. WEATHER
9. DATA_QUALITY
10. EXECUTIVE_INSIGHTS
11. UNSUPPORTED (safe fallback)

---

## 4. Intent Schema

```json
{
  "intent": "PRICE_RISK",
  "crop": "Wheat",
  "mandi": null,
  "district": null,
  "date_start": null,
  "date_end": null,
  "requested_visualization": null,
  "comparison_target": null
}
```

---

## 5. Grounding Strategy

- All numbers retrieved from `analytics/*.csv` directly.
- No LLM-generated estimates for any KPI.
- If a metric is missing from analytics: return explicit "not available" with explanation.
- Chart data comes exclusively from validated analytics outputs.

---

## 6. Hallucination Prevention

- No fabrication of unsupported metrics.
- No unsupported weather-to-mandi mapping claims.
- Clear distinction: correlation ≠ causation.
- All explanations include source file references.

---

## 7. Unsupported Question Handling

Example responses (deterministic text):
- "The supplied data does not provide a legitimate sensor-to-mandi/district mapping, so weather analysis is available only at date level."
- "This agent is grounded in the supplied TransOrg dataset and does not use external market data."
- "I can analyze supply, mandi performance, crop prices, MSP risk, logistics, weather relationships, and data quality."

---

## 8. Business Recommendation Safety

All recommendations use cautious language: investigate, monitor, consider reviewing, associated with.
No unsupported causal claims allowed.

---

## 9. Model Provider & Cost Safety

- LLM provider kept modular (`agent/llm.py`).
- Environment variable `LLM_API_KEY` controls API access.
- If no key is set or API unavailable, agent falls back to deterministic keyword-based parsing and pre-formulated explanation templates.
- Only small structured payloads (not full datasets) are sent to the LLM.

---

## 10. Limitations

- Agent is constrained to 10 supported intents; unsupported queries return safe fallbacks.
- Weather analysis is date-level only (no sensor-to-mandi mapping exists in organizer data).
- No real-time data connection; answers derived from static validated analytics.
- No multi-agent autonomous loops; single transparent pipeline.

---

## 11. Evaluation Criteria

- Intent parsing accuracy.
- Tool routing accuracy.
- Chart selection correctness.
- Result validation pass rate.
- Explanation ground-truth alignment.
- Zero unsupported claims detected in output review.
