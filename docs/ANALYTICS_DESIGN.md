# Analytics Layer Design
## TransOrg AgentIQ Datathon - Track 3: AgriTech

**Created:** 2026-09-12  
**Status:** Design Complete — Implementation Pending  
**Source:** `data/cleaned/`  
**Output:** `analytics/`

---

## 1. DESIGN PRINCIPLES

1. **Single Source of Truth**: All analytics consume `data/cleaned/` exclusively.
2. **Explicit Exclusions**: Document what records are excluded and why.
3. **No Silent Assumptions**: Where data is insufficient, state the limitation clearly.
4. **Reproducibility**: Entire analytics layer runs with `python scripts/run_analytics.py`.
5. **Data Quality Transparency**: Every KPI reports records available, used, and excluded.

---

## 2. CORE KPI DEFINITIONS

### A. SUPPLY / ARRIVALS KPIs

#### A1. Total Crop Arrivals (Quintals)
- **Metric Name:** `total_arrivals_qtl`
- **Business Meaning:** Total quantity of crops that arrived at all mandis (in quintals).
- **Source Dataset:** `track3_mandi_arrivals_clean.csv`
- **Source Columns:** `quantity_quintals`
- **Filters:** 
  - `quantity_quintals IS NOT NULL`
  - `unit_status = 'resolved'`
- **Aggregation:** `SUM(quantity_quintals)`
- **Formula:** Direct sum of valid cleaned quantities
- **Grain:** Overall total
- **Missing Value Treatment:** Exclude NaN quantities
- **Unresolved Records Treatment:** Exclude rows where `unit_unresolvable = 1`
- **Expected Output:** Single numeric value (float)

#### A2. Total Farmers
- **Metric Name:** `total_farmers`
- **Business Meaning:** Total count of farmers who brought crops to mandis.
- **Source Dataset:** `track3_mandi_arrivals_clean.csv`
- **Source Columns:** `farmer_count`
- **Filters:** `farmer_count IS NOT NULL`
- **Aggregation:** `SUM(farmer_count)`
- **Formula:** Direct sum
- **Grain:** Overall total
- **Missing Value Treatment:** Exclude NaN farmer counts
- **Unresolved Records Treatment:** N/A
- **Expected Output:** Integer count

#### A3. Number of Arrival Records
- **Metric Name:** `arrival_record_count`
- **Business Meaning:** Total count of valid arrival transactions.
- **Source Dataset:** `track3_mandi_arrivals_clean.csv`
- **Source Columns:** All rows
- **Filters:** None (count all rows)
- **Aggregation:** `COUNT(*)`
- **Formula:** Row count
- **Grain:** Overall total
- **Missing Value Treatment:** N/A
- **Unresolved Records Treatment:** Count all records including unresolved
- **Expected Output:** Integer count

#### A4. Active Mandis
- **Metric Name:** `active_mandi_count`
- **Business Meaning:** Number of distinct mandis with at least one valid arrival record.
- **Source Dataset:** `track3_mandi_arrivals_clean.csv`
- **Source Columns:** `mandi_id`
- **Filters:** 
  - `mandi_id IS NOT NULL`
  - `mandi_id_status = 'normalized'`
- **Aggregation:** `COUNT(DISTINCT mandi_id)`
- **Formula:** Distinct count of canonical mandi IDs
- **Grain:** Overall total
- **Missing Value Treatment:** Exclude NULL mandi IDs
- **Unresolved Records Treatment:** Exclude unresolved IDs
- **Expected Output:** Integer count

---

### B. PRICE / MSP ANALYTICS

#### B1. Average Modal Price
- **Metric Name:** `avg_modal_price`
- **Business Meaning:** Average market price across all valid price records.
- **Source Dataset:** `track3_price_and_msp_clean.csv`
- **Source Columns:** `modal_price`
- **Filters:** 
  - `modal_price IS NOT NULL`
  - `modal_price_status = 'resolved'`
- **Aggregation:** `AVG(modal_price)`
- **Formula:** Mean of valid modal prices
- **Grain:** Overall average
- **Missing Value Treatment:** Exclude NaN prices
- **Unresolved Records Treatment:** Exclude non-resolved prices
- **Expected Output:** Float (₹ per quintal)

#### B2. Average MSP
- **Metric Name:** `avg_msp`
- **Business Meaning:** Average Minimum Support Price across all valid MSP records.
- **Source Dataset:** `track3_price_and_msp_clean.csv`
- **Source Columns:** `msp`
- **Filters:** 
  - `msp IS NOT NULL`
  - `msp_status = 'resolved'`
- **Aggregation:** `AVG(msp)`
- **Formula:** Mean of valid MSP values
- **Grain:** Overall average
- **Missing Value Treatment:** Exclude NaN MSP
- **Unresolved Records Treatment:** Exclude non-resolved MSP
- **Expected Output:** Float (₹ per quintal)

#### B3. Price Gap (Absolute)
- **Metric Name:** `price_gap`
- **Business Meaning:** Difference between modal price and MSP (modal - MSP).
- **Source Dataset:** `track3_price_and_msp_clean.csv`
- **Source Columns:** `modal_price`, `msp`
- **Filters:** 
  - Both `modal_price` and `msp` NOT NULL
  - Both status = 'resolved'
- **Aggregation:** Calculated per record, then averaged
- **Formula:** `modal_price - msp`
- **Grain:** Per record, then aggregate statistics
- **Missing Value Treatment:** Exclude if either value is NULL
- **Unresolved Records Treatment:** Exclude if either is unresolved
- **Expected Output:** Float (₹)

#### B4. Price Gap Percentage
- **Metric Name:** `price_gap_pct`
- **Business Meaning:** Percentage difference between modal price and MSP relative to MSP.
- **Source Dataset:** `track3_price_and_msp_clean.csv`
- **Source Columns:** `modal_price`, `msp`
- **Filters:** 
  - Both NOT NULL and resolved
  - `msp > 0` (avoid division by zero)
- **Aggregation:** Calculated per record
- **Formula:** `((modal_price - msp) / msp) * 100`
- **Grain:** Per record, then aggregate statistics
- **Missing Value Treatment:** Exclude if either NULL or MSP = 0
- **Unresolved Records Treatment:** Exclude if either unresolved
- **Expected Output:** Float (%)

#### B5. Price Crash Flag
- **Metric Name:** `price_below_msp_flag`
- **Business Meaning:** Binary indicator: 1 if modal_price < msp, else 0.
- **Source Dataset:** `track3_price_and_msp_clean.csv`
- **Source Columns:** `modal_price`, `msp`
- **Filters:** Both NOT NULL and resolved
- **Aggregation:** N/A (flag per record)
- **Formula:** `1 if modal_price < msp else 0`
- **Grain:** Per record
- **Missing Value Treatment:** Set to NULL if either price is NULL
- **Unresolved Records Treatment:** Set to NULL if either unresolved
- **Expected Output:** Integer (0 or 1 per record)

#### B6. Price Crash Count
- **Metric Name:** `price_crash_count`
- **Business Meaning:** Total number of instances where modal price < MSP.
- **Source Dataset:** Derived from `price_below_msp_flag`
- **Source Columns:** `price_below_msp_flag`
- **Filters:** `price_below_msp_flag = 1`
- **Aggregation:** `SUM(price_below_msp_flag)`
- **Formula:** Count of flag = 1
- **Grain:** Overall total
- **Missing Value Treatment:** Exclude NULL flags
- **Unresolved Records Treatment:** Already excluded in flag calculation
- **Expected Output:** Integer count

#### B7. Price Crash Rate
- **Metric Name:** `price_crash_rate`
- **Business Meaning:** Percentage of valid price records where modal < MSP.
- **Source Dataset:** Derived
- **Source Columns:** `price_below_msp_flag`
- **Filters:** Valid records with flag NOT NULL
- **Aggregation:** Ratio calculation
- **Formula:** `(price_crash_count / total_valid_price_records) * 100`
- **Grain:** Overall percentage
- **Missing Value Treatment:** Exclude NULL flags from denominator
- **Unresolved Records Treatment:** Already excluded
- **Expected Output:** Float (%)

---

### C. MANDI-LEVEL ANALYTICS

**Output Table:** `analytics/mandi_kpis.csv`

**Grain:** One row per mandi

**Columns:**
1. `mandi_id` — Canonical mandi ID
2. `mandi_name` — Mandi name (from master)
3. `district` — District (from master)
4. `state` — State (from master)
5. `total_arrival_qty_qtl` — SUM of valid quantity_quintals
6. `arrival_record_count` — COUNT of arrival records
7. `farmer_count` — SUM of farmer_count
8. `avg_modal_price` — AVG of modal_price for this mandi
9. `avg_msp` — AVG of msp for this mandi
10. `price_below_msp_count` — COUNT of price crash instances
11. `price_below_msp_rate` — Percentage (price_below_msp_count / valid_price_records)
12. `arrival_volume_rank` — Rank by total_arrival_qty_qtl (DESC)
13. `price_performance_rank` — Rank by avg_modal_price (DESC)
14. `price_crash_rate_rank` — Rank by price_below_msp_rate (ASC — lower is better)

**Filters:**
- Include all mandis present in arrivals or price datasets
- Exclude mandis with zero valid records across both datasets

**Missing Value Treatment:**
- If mandi has no price records, set price metrics to NULL
- If mandi has no arrival records, set arrival metrics to 0/NULL

**Ranking Treatment:**
- Only rank mandis with at least 10 valid records in the relevant metric
- Otherwise set rank to NULL

---

### D. CROP-LEVEL ANALYTICS

**Output Table:** `analytics/crop_kpis.csv`

**Grain:** One row per canonical crop

**Columns:**
1. `crop_name` — Canonical crop name
2. `total_arrivals_qtl` — SUM of valid quantity
3. `pct_of_total_arrivals` — Percentage of overall arrivals
4. `arrival_record_count` — COUNT of arrival records
5. `farmer_count` — SUM of farmers
6. `avg_modal_price` — AVG modal price
7. `avg_msp` — AVG MSP
8. `price_gap` — AVG(modal_price - msp)
9. `price_gap_pct` — AVG price gap percentage
10. `price_crash_count` — COUNT of below-MSP instances
11. `price_crash_rate` — Percentage
12. `arrival_volume_rank` — Rank by total_arrivals_qtl (DESC)
13. `price_vulnerability_score` — Composite: high arrivals + high crash rate

**Filters:**
- **EXCLUDE** `crop_name = 'REQUIRES_INVESTIGATION'` from primary rankings
- Create separate summary row for unresolved crops

**Missing Value Treatment:**
- If crop has no price records, set price metrics to NULL

**Ranking Treatment:**
- Rank only canonical crops (exclude `REQUIRES_INVESTIGATION`)

---

### E. DAILY TIME-SERIES ANALYTICS

**Output Table:** `analytics/daily_kpis.csv`

**Grain:** One row per date

**Columns:**
1. `date` — Calendar date
2. `daily_arrivals_qtl` — SUM of arrivals for that date
3. `daily_farmer_count` — SUM of farmers
4. `daily_avg_modal_price` — AVG modal price
5. `daily_avg_msp` — AVG MSP
6. `daily_price_crash_count` — COUNT of below-MSP instances
7. `daily_price_crash_rate` — Percentage
8. `arrival_record_count` — COUNT of arrival records

**Filters:**
- **EXCLUDE** records where date could not be parsed (NaT)
- **EXCLUDE** records where `date_ambiguous = 1` if that flag exists

**Missing Value Treatment:**
- If no arrivals for a date, arrival metrics = 0
- If no prices for a date, price metrics = NULL

**Date Handling:**
- Parse dates from arrivals and price datasets
- Document count of excluded ambiguous/unparseable dates

---

### F. TRANSPORT / LOGISTICS ANALYTICS

**Output Table:** `analytics/transport_kpis.csv`

**Grain:** Overall summary + per-warehouse

#### Overall Metrics:
1. `avg_transit_hours` — AVG(transit_hours_clean)
2. `median_transit_hours` — MEDIAN(transit_hours_clean)
3. `avg_distance_km` — AVG(distance_km)
4. `total_trips` — COUNT(*)
5. `valid_transit_trips` — COUNT where transit_hours_clean NOT NULL
6. `valid_distance_trips` — COUNT where distance_km NOT NULL

#### Per-Warehouse Metrics:
**Output Table:** `analytics/warehouse_kpis.csv`

**Grain:** One row per destination_warehouse

**Columns:**
1. `destination_warehouse`
2. `trip_count`
3. `avg_transit_hours`
4. `median_transit_hours`
5. `p75_transit_hours` — 75th percentile
6. `p90_transit_hours` — 90th percentile
7. `avg_distance_km`
8. `long_transit_count` — COUNT where transit > p90 overall
9. `long_transit_rate` — Percentage

**Delay Definition:**
- **NO ARBITRARY THRESHOLD INVENTED**
- Instead: identify "long transit" trips as those > 90th percentile of overall transit distribution
- Label as "long transit" or "anomalous" rather than "delay"
- Document the p90 threshold in the output

**Filters:**
- Exclude records where `negative_transit_flag = 1`
- Use only `transit_hours_clean` (negatives already removed)

---

### G. WEATHER ANALYTICS

**Output Table:** `analytics/weather_daily.csv`

**Grain:** One row per date

**Columns:**
1. `date` — Extracted from timestamp
2. `avg_temperature_celsius`
3. `min_temperature_celsius`
4. `max_temperature_celsius`
5. `total_rainfall_mm`
6. `avg_rainfall_mm`
7. `max_rainfall_mm`
8. `avg_humidity_pct`
9. `rainfall_day_flag` — 1 if total_rainfall > 0, else 0
10. `sensor_count` — COUNT DISTINCT sensors reporting that day

**Filters:**
- Exclude records where `negative_rainfall_flag = 1`
- Use only valid `temperature_celsius` and `rainfall_mm`

**Weather-Arrival Correlation Table:** `analytics/weather_arrival_analysis.csv`

**Grain:** Date-level correlation analysis

**Columns:**
1. `date`
2. `total_arrivals_qtl` — From arrivals
3. `total_rainfall_mm` — From weather
4. `avg_temperature_celsius` — From weather
5. `avg_humidity_pct` — From weather

**Analysis Metrics (separate summary row):**
1. `rainfall_arrival_correlation` — Pearson correlation(rainfall, arrivals)
2. `temperature_arrival_correlation` — Pearson correlation(temp, arrivals)
3. `humidity_arrival_correlation` — Pearson correlation(humidity, arrivals)
4. `p_value_rainfall` — Statistical significance
5. `p_value_temperature`
6. `p_value_humidity`

**CRITICAL LIMITATION:**
> "Weather-to-mandi attribution is UNSUPPORTED. The supplied data does not provide a legitimate sensor-to-mandi or sensor-to-district mapping. Weather impact is analyzed at date level only. Correlations represent associations observed in the data, not causal relationships."

---

## 3. ADVANCED INSIGHTS

**Output Table:** `analytics/executive_insights.csv`

**Grain:** One row per insight

**Columns:**
1. `insight_id`
2. `insight_category` — Supply / Price / Logistics / Weather / Concentration
3. `insight_title` — Short title
4. `metric_name` — Key metric used
5. `metric_value` — Calculated value
6. `comparison_baseline` — Comparison reference
7. `business_implication` — What this means
8. `severity` — High / Medium / Low
9. `supporting_data` — Additional context
10. `data_quality_note` — Any caveats

### Insight Definitions:

#### I1. Supply Concentration
- **Title:** "Top N mandis contribute X% of total arrivals"
- **Metric:** Cumulative percentage of arrivals from top 5, 10, 20 mandis
- **Formula:** `SUM(top_N_arrivals) / total_arrivals * 100`
- **Severity:** High if top 5 > 50%

#### I2. Crop Concentration
- **Title:** "Top N crops represent X% of total arrivals"
- **Metric:** Cumulative percentage by crop
- **Formula:** Similar to supply concentration
- **Severity:** High if top 3 crops > 70%

#### I3. Price Vulnerability (High Volume + High Crash Rate)
- **Title:** "Crop X has high arrivals but Y% below-MSP rate"
- **Metric:** Crops with:
  - `total_arrivals_qtl` > median AND
  - `price_crash_rate` > 30%
- **Severity:** High for each crop meeting criteria

#### I4. Mandi Vulnerability
- **Title:** "Mandi X has high volume but Y% price crash rate"
- **Metric:** Mandis with:
  - `total_arrivals_qtl` > median AND
  - `price_crash_rate` > 30%
- **Severity:** High

#### I5. Logistics Bottlenecks
- **Title:** "Warehouse X has median transit time Z hours above overall median"
- **Metric:** Warehouses where:
  - `median_transit_hours` > overall_median * 1.5
- **Severity:** Medium

#### I6. Weather-Associated Supply Changes
- **Title:** "High-rainfall days (>X mm) associated with Y% lower/higher arrivals"
- **Metric:** Compare average arrivals on:
  - High rainfall days (>75th percentile) vs
  - Low rainfall days (<25th percentile)
- **Formula:** `(avg_arrivals_high_rain - avg_arrivals_low_rain) / avg_arrivals_low_rain * 100`
- **Severity:** Medium if difference > 20%

#### I7. Price Volatility
- **Title:** "Crop X shows high price variability (StdDev = Y)"
- **Metric:** Crops with:
  - Sufficient time-series data (>20 price records)
  - `std_dev(modal_price) / mean(modal_price)` > 0.3 (coefficient of variation)
- **Severity:** Medium

#### I8. Unresolved Data Impact
- **Title:** "X% of arrival records have unresolvable units"
- **Metric:** `unit_unresolvable_count / total_records * 100`
- **Severity:** Informational (data quality flag)

---

## 4. VALIDATION RULES

**Output:** `reports/ANALYTICS_VALIDATION_REPORT.txt`

### Validation Checks:

1. **Arrival Reconciliation**
   - SUM of crop-level arrivals = Overall total arrivals (within rounding)
   - SUM of mandi-level arrivals = Overall total arrivals

2. **Percentage Checks**
   - Crop percentage shares sum to ~100%
   - Mandi percentage shares sum to ~100%

3. **No Invalid Negatives**
   - All KPIs with inherently non-negative semantics are >= 0
   - Transit hours, distances, prices, quantities all >= 0

4. **Division by Zero**
   - No percentages calculated where denominator = 0
   - Document where rates could not be calculated

5. **Price Relationships**
   - `price_crash_count` <= `total_valid_price_records`
   - `price_crash_rate` between 0 and 100

6. **Unresolved Handling**
   - Document count of `REQUIRES_INVESTIGATION` crop records excluded from rankings
   - Document count of ambiguous dates excluded from time-series

7. **Weather Limitation**
   - Verify no output claims sensor-to-mandi mapping
   - All weather analysis is date-level only

8. **Record Counts**
   - For each major KPI, report:
     - Records available
     - Records used
     - Records excluded
     - Reason for exclusion

---

## 5. OUTPUT ARCHITECTURE

```
analytics/
├── mandi_kpis.csv
├── crop_kpis.csv
├── daily_kpis.csv
├── price_msp_analysis.csv
├── transport_kpis.csv
├── warehouse_kpis.csv
├── weather_daily.csv
├── weather_arrival_analysis.csv
├── executive_insights.csv
└── data_quality_summary.csv
```

Each output file includes metadata header (if CSV supports comments) or companion `.meta.txt` file stating:
- Generation timestamp
- Source datasets
- Record counts
- Exclusions applied

---

## 6. IMPLEMENTATION SCRIPT

**Script:** `scripts/run_analytics.py`

**Execution:** `python scripts/run_analytics.py`

**Steps:**
1. Load all cleaned datasets from `data/cleaned/`
2. Validate cleaned data integrity
3. Calculate all core KPIs (sections A-G)
4. Generate advanced insights
5. Write outputs to `analytics/`
6. Run validation checks
7. Generate `reports/ANALYTICS_VALIDATION_REPORT.txt`
8. Print summary to console

**Dependencies:**
- pandas, numpy (already installed)
- scipy (for Pearson correlation p-values)

---

## 7. LIMITATIONS & ASSUMPTIONS

### Limitations:
1. **Weather-to-Mandi**: No legitimate sensor-to-mandi/district mapping exists; all weather analysis is date-level aggregation only.
2. **Unresolved Crops**: 13 crop variants remain `REQUIRES_INVESTIGATION`; excluded from primary rankings but counted separately.
3. **Unresolved Units**: 20,607 arrival records have unresolvable units; excluded from quantity calculations.
4. **Ambiguous Dates**: Records with unparseable or ambiguous dates excluded from time-series.
5. **Transport Delay**: No business-defined delay threshold; using statistical approach (p90) instead.

### Assumptions:
1. **Crop Classification**: Canonical crop mappings from Step 5 are correct.
2. **Mandi Normalization**: Normalized mandi IDs are accurate.
3. **Price Definition**: "Price crash" defined as `modal_price < msp` (no additional margin).
4. **Farmer Count**: Assumed additive (each arrival record represents distinct farmer transactions).
5. **Correlation ≠ Causation**: Weather-arrival correlations are associations only.

---

## 8. NEXT STEPS (POST-IMPLEMENTATION)

After `scripts/run_analytics.py` executes successfully:
1. Review `reports/ANALYTICS_VALIDATION_REPORT.txt`
2. Verify all validation checks pass
3. Inspect `analytics/executive_insights.csv` for business insights
4. Document any unexpected findings
5. Update README if necessary
6. **STOP** — do not proceed to dashboard until explicitly instructed

---

**END OF ANALYTICS DESIGN DOCUMENT**
