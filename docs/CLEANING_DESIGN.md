# CLEANING DESIGN DOCUMENT — TransOrg AgentIQ Datathon — Track 3: AgriTech
# Phase: Day 1 — Step 4 (Cleaning Design ONLY — NO IMPLEMENTATION)
# Constraint: ZERO modifications to data/raw/. ZERO cleaned datasets produced.

---

# PRINCIPLE STATEMENT

- Raw data in `data/raw/` is NEVER overwritten, deleted, renamed, or moved.
- Every transformation must reference an explicit mapping table or reproducible rule.
- Every dropped/altered record must be countable and explainable (audit column or log entry).
- No silent imputation of business-critical values.
- Before/after provenance preserved for judge review.
- This document is DESIGN ONLY. No code executes transformations against raw files.

---

# A. CLEANING ARCHITECTURE

```
Raw (data/raw/)  →  Read-only load  →  Audit/provenance layer  →  Design rules (this doc)
                                                         ↓
                                              Mapping tables (docs/mappings/)
                                                         ↓
                                              Validation rules (docs/validation/)
                                                         ↓
                                              Cleaned design output spec (docs/CLEANING_DESIGN.md)
                                                         ↓
                                              Implementation deferred to user approval
```

Pipeline stages (design order):
1. Load raw (read-only)
2. Profile (done — Step 3)
3. Design rules (this document)
4. Create mapping tables (design spec only)
5. Apply transformations (NOT executed)
6. Validate outputs (design checks only)
7. Export cleaned + audit trail (NOT executed)

---

# B. DATASET-BY-DATASET CLEANING RULES

---
## B1. track3_mandi_master.csv (Master — 60 rows, 6 cols)

### B1.1 Mandi ID Standardization (Rule 1)
- **Problem**: No issue in master itself; master uses `MANDI###` format consistently. Child datasets have 342 raw variants.
- **Detection**: Child datasets show `MANDI001`, `MANDI-001`, `mandi_001`, `M001`, `001` (Step 3 Section B).
- **Transformation/action**: Design mapping: all child variants → master format `MANDI###` (3-digit, zero-padded, uppercase, `MANDI` prefix, no separator except the fixed `MANDI`). Example: `mandi_049` → `MANDI049`; `026` → `MANDI026`.
- **Reason**: Single canonical key enables 100% join coverage (verified in Step 3 Section I).
- **Validation check**: After mapping, normalize child `mandi_id` and confirm 57 unique values; confirm 100% overlap with master `mandi_id`.

### B1.2 Duplicate Rows (Rule 14 / 15 / Conflicting IDs — Rule 15)
- **Problem**: 3 exact full-row duplicates detected (Step 3 Section D).
- **Detection**: `df.duplicated().sum()` = 3.
- **Transformation/action**: Design: flag exact duplicates with audit column `is_duplicate` = 1; drop only after confirming zero conflicting attributes. If conflict detected (same ID, different district/state), do NOT drop — escalate to business rule.
- **Reason**: Exact duplicates are safe to remove; conflicting duplicates are not.
- **Validation check**: After removal, 57 unique master IDs remain; 0 exact duplicates; 0 conflicting-ID cases (Step 3 confirms zero conflicts).

### B1.3 Missing Values (Rule 13)
- **Problem**: `district`: 4 missing (6.67%); `state`: 4 missing (6.67%); `mandi_type`: 11 missing (18.33%); `total_area_acres`: 6 missing (10.0%).
- **Detection**: Missing-value counts from Step 3 Section E.
- **Transformation/action**:
  - `district` / `state`: Do NOT invent from name. Design: keep as `NaN` but add `missing_district` / `missing_state` audit flags. If district/state can be derived from a validated external reference (not in dataset), apply only with documented assumption.
  - `mandi_type`: Keeps as `NaN` with flag; business rule required (APMC / Private / etc.).
  - `total_area_acres`: Keeps as `NaN`; no derivation possible from other master columns.
- **Reason**: These are business-critical attributes; silent imputation creates false geographic/type data.
- **Validation check**: Missing-value percentages preserved in audit; no values changed without documented assumption.

---
## B2. track3_mandi_arrivals.csv (Arrivals — 25,750 rows, 8 cols)

### B2.1 Mandi ID Standardization (Rule 1 — Child Side)
- Apply the same mapping design as B1.1: all 342 raw variants → `MANDI###`.
- Validation: 57 unique normalized IDs; 100% overlap with master.

### B2.2 Crop Name Standardization (Rule 2)
- **Problem**: 36 raw crop variants (Step 3 Section G). Obvious groups: Wheat (7), Corn (2), Sugarcane (4), Cotton (4), Mustard (4), Paddy (2); 13 ungrouped.
- **Detection**: Raw value frequency analysis.
- **Transformation/action**: Design mapping table (`docs/mappings/crop_mapping.csv`) with columns:
  - `raw_crop_name` → `canonical_crop` → `mapping_rule` (explicit / domain / requires_review)
  - Explicit mappings: `गेहूं` → `Wheat`; `Kanak` → `Wheat`; `Ganne` → `Sugarcane`; `गन्ना` → `Sugarcane`; `Kapas` → `Cotton`; `कपास` → `Cotton`; `Sarso` → `Mustard`; `सरसों` → `Mustard`; etc.
  - The 13 ungrouped variants mapped to `REQUIRES_INVESTIGATION` — NOT assigned to a canonical group without domain confirmation.
- **Reason**: Prevents false grouping; preserves auditability.
- **Validation check**: After mapping, count unique `canonical_crop`; verify 6 confirmed groups + ungrouped count matches 13; no raw value mapped twice to different canonical names (collision check).

### B2.3 Date/Time Parsing (Rule 3)
- **Problem**: 1512 unique date format patterns in `date` column (Step 3 Section A). Formats include `DD-MM-YYYY`, `YYYY-MM-DD`, `MM.DD.YYYY`, etc.
- **Detection**: Regex pattern grouping by detected format strings.
- **Transformation/action**: Design parsing order (explicit, not hardcoded chain):
  1. Try `YYYY-MM-DD` (ISO, unambiguous).
  2. Try `DD-MM-YYYY` (most common Indian format).
  3. For genuinely ambiguous formats (`01-07-2026`, `02.03.2026`):
     - `date_ambiguous` = 1 (always set for ambiguous patterns)
     - `date_raw` preserved (original string, untouched)
     - `date_parsed` = NaT (NOT interpreted as DD-MM-YYYY by default)
     - ONLY if an explicit, documented business rule supports DD-MM-YYYY interpretation for this dataset: apply parsed date with `date_interpreted_by_rule` = 1; otherwise remain NaT.
     - Report count of ambiguous records separately.
  4. If unparseable: `date_parsed` = NaT, `date_parse_failed` = 1.
- **Reason**: Explicit parsing hierarchy prevents silent misinterpretation.
- **Validation check**: Count parse failures; count ambiguous flags; verify no `date_parsed` values conflict with `date_raw` without documented assumption.

### B2.4 Unit Standardization — Quantity → Quintals (Rule 5)
- **Problem**: 14 quantity-unit variants (`T`, `Qtl`, `KG`, `Q`, `qtl`, `Quintals`, `tonnes`, `kg`, `quintal`, `KGS`, `MT`, `Kgs`, `Tonnes`, `Kilo`) (Step 3 Section F).
- **Detection**: `unit` column frequency analysis.
- **Transformation/action**: Design mapping (`docs/mappings/quantity_units.csv`):
  - `quintal` / `Qtl` / `qtl` / `Quintals` / `Q` → conversion_factor = 1.0 (quintals, standard)
  - `tonnes` / `T` / `Tonnes` / `MT` → conversion_factor = 10.0 (1 tonne = 10 quintals; value × 10)
  - `KG` / `kg` / `KGS` / `Kgs` / `Kilo` → conversion_factor = 0.01 (1 kg = 0.01 quintals; value × 0.01)
- **Evidence inspection (before design)**: 5143 missing-unit rows inspected via `docs/missing_unit_inspect.csv`. The `arrival_quantity` value contains embedded unit text (e.g., `'415.88 qtl'`, `'36,654.0 KG'`, `'22,697.0 KG'`). The embedded unit provides direct evidence. No assumption required.
- **Primary production rule (single branch, no user selection)**:
  1. Extract embedded unit from `arrival_quantity` string.
  2. Apply conversion_factor (see mapping above) to numeric part.
  3. If embedded unit unparseable or quantity string contains no recognized unit: `quantity_quintals` = NaN; `unit_unresolvable` = 1; `arrival_quantity_raw` preserved; record counted separately.
  4. NEVER invent `Qtl`. No silent assumption. If no evidence exists, unresolved — not filled.
- **Reason**: Evidence-based only. Unresolved records preserved for audit (judge can verify no silent filling).
- **Validation check**: `quantity_quintals` numeric for all resolved; count `unit_unresolvable` = exact unparseable count; `arrival_quantity_raw` preserved for every row.

### B2.5 Negative Arrival Quantities (Rule 10)
- **Problem**: 1,261 rows with negative `arrival_quantity` (4.9%) (Step 3 Section C / Section 4).
- **Detection**: `numeric_data < 0` filter.
- **Primary production rule (single branch — NOT user-selectable)**:
  - `negative_quantity_flag` = 1 (preserved in audit)
  - `arrival_quantity` (cleaned numeric column) = NaN for these 1261 records
  - `arrival_quantity_raw` preserved (original value, including negative, retained for audit)
  - NEVER set to 0. NEVER silently delete. NEVER leave unchanged in the primary cleaned dataset.
  - Count retained: 1261.
- **Reason**: Negative crop arrival is physically impossible. The production cleaned dataset must not contain impossible values; audit trail preserves original for review.
- **Validation check**: `negative_quantity_flag` count = 1261; `arrival_quantity_raw` preserved for all 1261; primary cleaned quantity column contains NaN (not 0, not original negative); audit log records all 1261 with reason.

### B2.6 Missing Values — Arrivals Columns (Rule 13)
- **Problem**: `variety`: 3735 missing (14.5%); `unit`: 5143 missing (19.97%); `farmer_count`: 3899 missing (15.14%); `arrival_id`: 484 missing (1.88%).
- **Design per column**:
  - `arrival_id`: If missing, generate surrogate `SURROGATE_ARR_###` (sequential, documented). Flag `surrogate_id` = 1.
  - `variety`: Keep as `NaN`; add `missing_variety` flag. Do NOT invent variety.
  - `unit`: Evidence-based extraction from `arrival_quantity` string (see B2.4 revised). If embedded unit unparseable: `quantity_quintals` = NaN; `unit_unresolvable` = 1. NEVER assume `Qtl`. If both quantity and embedded unit missing: `missing_quantity_system` = 1.
  - `farmer_count`: Keep `NaN`; add `missing_farmer_count` flag.
- **Validation check**: Every missing-value action produces a countable audit column; no silent filling.

### B2.7 Exact Duplicate Rows (Rule 14)
- **Problem**: 750 exact full-row duplicates (Step 3 Section D).
- **Transformation/action**: Design: flag `is_duplicate` = 1 for duplicates; drop only after confirming zero conflicts; keep first occurrence; log count of dropped = 750.
- **Reason**: Exact duplicates do not add information.
- **Validation check**: After design application, `is_duplicate` count = 0 in cleaned data; original 750 preserved in audit log.

---
## B3. track3_price_and_msp.json (Price — 12,000 rows, 9 cols)

### B3.1 Mandi ID Standardization (Rule 1 — Child Side)
- Same mapping design: all variants → `MANDI###`.
- Validation: 57 unique normalized IDs; 100% master overlap (Step 3 Section I).

### B3.2 Currency/Price → Numeric (Rule 9)
- **Problem**: Price columns (`min_price`, `max_price`, `modal_price`, `msp`) contain embedded currency symbols (`₹`, `Rs.`, `INR`, `/-`) and commas (Step 3 Section F / Section 3).
- **Detection**: String patterns with currency markers.
- **Transformation/action**: Design mapping table (`docs/mappings/price_formats.csv`):
  - Remove symbols: `₹`, `Rs.`, `INR`, `,`, `/-`, whitespace.
  - Convert to float. Preserve `min_price_raw` audit column.
- **Reason**: Numeric comparison requires clean values.
- **Validation check**: All price columns numeric after cleaning; verify no empty strings remain; count of converted = 12,000 (0 lost — Step 3 confirms 0 missing in price value rows).

### B3.3 Date Parsing (Rule 3 — Price Side)
- Same design as B2.3: 276 format variants; parse using same hierarchy; ambiguous dates flagged.

### B3.4 Missing Values — Price (Rule 13)
- `mandi_id`: 1235 missing (10.3%). Design: keep `NaN`; add `missing_mandi_id_price` flag. Do NOT invent mandi from district alone (district → mandi is many-to-one; requires assumption).
- `district`: 773 missing (6.4%). Design: same — flag only; no invention.
- Validation: audit flags count exactly 1235 and 773.

---
## B4. track3_transport_logistics.csv (Transport — 10,400 rows, 10 cols)

### B4.1 Mandi ID Standardization (Rule 1 — Child Side)
- Same mapping: 342 raw → 57 canonical; 100% overlap.

### B4.2 Distance → Kilometers (Rule 8)
- **Problem**: Distance units: `km` (83.4%, 7815) and `miles` (16.6%, 1553) (Step 3 Section F).
- **Transformation/action**: Design mapping (`docs/mappings/distance_units.csv`):
  - `km` → value × 1 (standard)
  - `miles` → value × 1.60934 (conversion factor)
- **Evidence inspection (before design)**: 1032 missing `distance_unit` rows inspected. `distance` values contain embedded units (e.g., `'316.5 KM'`, `'196.7 KM'`, `'842.6 KM'`, `'644.4 KM'`). Evidence exists directly in value string. Present-unit comparison confirms `km` = 83.4% (7815 rows), `miles` = 16.6% (1553 rows), distance range ~52.3–1429.8 km.
- **Primary production rule (single branch)**:
  1. Extract embedded unit from `distance` string.
  2. If `km` or `KM`: `distance_km` = numeric value (conversion_factor 1.0).
  3. If `miles`: `distance_km` = value × 1.60934.
  4. If no embedded unit found or unparseable: `distance_km` = NaN; `distance_unit_unresolvable` = 1; `distance_raw` preserved; count reported separately.
  5. NEVER assume `km`. If no embedded evidence, unresolved.
- **Reason**: Direct evidence from value string; no silent assumption required.
- **Validation check**: All resolved `distance_km` numeric; `distance_unit_unresolvable` count = exact unparseable; `distance_raw` preserved.

### B4.3 Date/Time Parsing (Rule 3 — Transport)
- `departure_time`: 9315 unique formats.
- `arrival_time`: 8353 unique formats; 1053 missing (10.1%).
- Design same parsing hierarchy; ambiguous dates flagged; missing `arrival_time` preserved with `missing_arrival_time` = 1.

### B4.4 Negative Transit Hours (Rule 11)
- **Problem**: 563 rows with negative `transit_hours` (5.4%) (Step 3 Section C).
- **Detection**: `numeric < 0`.
- **Primary production rule (single branch)**:
  - `negative_transit_flag` = 1 (audit column preserved)
  - `transit_hours` (cleaned) = NaN for these 563 records
  - `transit_hours_raw` preserved (original negative value retained for audit)
  - NEVER set to 0. NEVER leave unchanged. NEVER silently delete.
  - Count = 563.
- **Reason**: Negative transit hours physically impossible. Production dataset must exclude impossible values; audit trail preserves original.
- **Validation check**: Flag count = 563; cleaned `transit_hours` = NaN for all flagged; `transit_hours_raw` preserved; audit log records 563.

### B4.5 Vehicle Number Standardization (Rule 16)
- **Problem**: 1622 missing (15.6%); format inconsistencies — lowercase present in 2083 records (23.7%); length 12 (1530, 17.4%) vs 13 (7248, 82.6%) (Step 3 Section H).
- **Transformation/action**: Design standard format (`docs/mappings/vehicle_format.md`):
  - Convert to uppercase.
  - Normalize spacing: remove extra spaces; standard separator `-` (e.g., `PB-62-CD-5129`).
  - If lowercase or irregular spacing found, add `vehicle_format_corrected` = 1.
  - Missing: `missing_vehicle_no` = 1; do NOT invent.
- **Reason**: Consistent identification; audit trail for format changes.
- **Validation check**: All non-null `vehicle_no` uppercase after correction; count of corrected records = count of original lowercase/irregular records.

### B4.6 Missing Values — Transport (Rule 13)
- `arrival_time`: 1053 missing (10.1%) — flag; no invention from `departure_time` + `transit_hours` (would assume perfect consistency, which is not guaranteed).
- `transit_hours`: 518 missing (5.0%) — flag; design branch: if `departure_time` and `arrival_time` exist, `transit_hours` CAN be derived (explicit derivation allowed with audit `derived_transit_hours` = 1); otherwise keep `NaN`.
- `distance_unit`: 1032 missing (9.9%) — if `distance` present, assume `km` (dominant unit, 83.4%) with `unit_assumed_km` = 1; document.
- `vehicle_no`: 1622 missing — flag only.
- `driver_id`: 1551 missing — flag only.
- Validation: Each missing column has audit flag; derived values have `derived_` flag.

### B4.7 Exact Duplicate Rows (Rule 14)
- 400 exact duplicates; same design as B1.2 / B2.7.

---
## B5. track3_weather_sensors.xlsx (Weather — 15,000 rows, 7 cols)

### B5.1 Temperature → Celsius (Rule 6)
- **Problem**: Temperature column contains both raw numbers and strings with embedded units (e.g., `'30.3°C'`, `'21.8°C'`, `92.5` with `temp_unit` = `°F`); `temp_unit` has 8 variants (Step 3 Section F / Section 3).
- **Transformation/action**: Design mapping (`docs/mappings/temp_units.csv`):
  - If `temperature` is pure number: use `temp_unit` column to determine conversion (`C`/`°C`/`Celsius` → value; `F`/`°F`/`Fahrenheit` → (value − 32) × 5/9; `f`/`c` lowercase → same as uppercase).
  - If `temperature` contains embedded unit (e.g., `'30.3°C'`): parse numeric part; convert to Celsius; set `temperature_extracted` = cleaned value; preserve `temperature_raw`.
  - If `temp_unit` missing but embedded unit present: extract from embedded string; add `temp_unit_extracted` = 1.
- **Reason**: Consistent Celsius metric.
- **Validation check**: All `temperature_celsius` numeric; verify no embedded strings remain; count converted vs extracted.

### B5.2 Rainfall → Millimeters (Rule 7)
- **Problem**: `rainfall` numeric; `rain_unit` has 6 variants (`mm`, `MM`, `millimeters`, `inches`, `in`, `inch`) (Step 3 Section F).
- **Transformation/action**: Design mapping (`docs/mappings/rain_units.csv`):
  - `mm` / `MM` / `millimeters` → value × 1
  - `in` / `inches` / `inch` → value × 25.4
  - `rainfall` column numeric; `rain_unit` standardizes to `mm`.
- **Reason**: Consistent rainfall metric.
- **Validation check**: `rainfall_mm` numeric; no remaining non-`mm` units.

### B5.3 Negative Rainfall (Rule 12)
- **Problem**: 1518 rows with negative `rainfall` (10.1%) (Step 3 Section C / Section 4). Range: −50.0 to 50.0.
- **Detection**: `rainfall < 0`.
- **Primary production rule (single branch)**:
  - `negative_rainfall_flag` = 1 (audit column preserved)
  - `rainfall` (cleaned) = NaN for these 1518 records
  - `rainfall_raw` preserved (original negative value, range −50.0 to 50.0, retained for audit)
  - NEVER set to 0. NEVER leave unchanged in production cleaned dataset. NEVER silently delete.
  - Count = 1518.
- **Reason**: Negative rainfall physically impossible. Production dataset excludes impossible values; audit preserves original.
- **Validation check**: Flag count = 1518; cleaned `rainfall` = NaN for all flagged; `rainfall_raw` preserved; audit log records 1518.

### B5.4 Timezone / Timestamp Handling (Rule 4 — UTC → IST)
- **Problem**: Weather timestamps have `UTC` and `IST` variants mixed (Step 3 Section A).
- **Detection**: Timestamp pattern analysis showing time zone markers.
- **Transformation/action**: Design:
  - Identify `timestamp` containing `UTC`: parse as UTC; convert to IST (`UTC + 5:30`); preserve `timestamp_utc_raw` and `timestamp_ist_converted`.
  - Identify `timestamp` already in IST: keep as IST but standardize format to `YYYY-MM-DD HH:MM:SS IST`.
  - Add audit column: `timezone_source` (`UTC` / `IST` / `unknown`).
- **Reason**: Consistent Indian time zone for cross-dataset alignment.
- **Validation check**: All `timestamp_ist` in standard format; `timezone_source` documented for every row; conversion factor verified (5h 30m).

### B5.5 Missing Values — Weather (Rule 13)
- `timestamp`: 1555 missing (10.4%) — flag `missing_timestamp`; no invention from other rows.
- `temp_unit`: 2263 missing (15.1%) — if `temperature` contains embedded unit (e.g., `'30.3°C'`), extract; else flag `missing_temp_unit`. Do NOT assume Celsius without evidence.
- `rainfall`: 791 missing (5.3%) — flag; no derivation from humidity.
- `rain_unit`: 791 missing (5.3%) — if `rainfall` non-null and `rain_unit` missing: assume `mm` (dominant, 31.4% `mm` + 21.4% `MM` = 52.8%) with `rain_unit_assumed_mm` = 1; document assumption.
- `humidity_percent`: 1500 missing (10.0%) — flag only; no derivation from temperature or rainfall.

---

# C. COLUMN-BY-COLUMN RULES (Cross-reference index)

| Dataset | Column | Rule # | Design Action | Audit/Flag |
|---|---|---|---|---|
| master | mandi_id | 1 | Confirm standard format (`MANDI###`) | None (already clean) |
| master | mandi_name | — | No change (57 unique) | — |
| master | district | 13 | Keep missing; flag | `missing_district_master` |
| master | state | 13 | Keep missing; flag | `missing_state_master` |
| master | mandi_type | 13 | Keep missing; flag | `missing_mandi_type` |
| master | total_area_acres | 13 | Keep missing; flag | `missing_area_acres` |
| arrivals | arrival_id | 13 | Surrogate if missing; flag | `surrogate_id` |
| arrivals | mandi_id | 1 | Map 342 → `MANDI###` | `mandi_id_raw` preserved |
| arrivals | date | 3 | Parse; ambiguous flagged | `date_raw`, `date_ambiguous` |
| arrivals | crop | 2 | Map to canonical; ungrouped flagged | `crop_raw`, `crop_mapping_applied` |
| arrivals | variety | 13 | Keep missing; flag | `missing_variety` |
| arrivals | arrival_quantity | 5 / 10 | Convert to quintals; negative flagged | `quantity_raw`, `negative_quantity_flag` |
| arrivals | unit | 5 / 13 | Convert; assume if missing | `unit_raw`, `unit_assumed` |
| arrivals | farmer_count | 13 | Keep missing; flag | `missing_farmer_count` |
| price | mandi_id | 1 | Map to `MANDI###` | `mandi_id_raw` |
| price | date | 3 | Parse; ambiguous flagged | `date_raw` |
| price | crop_name | 2 | Same crop mapping | `crop_raw` |
| price | district | 13 | Keep missing; flag | `missing_district_price` |
| price | min_price / max_price / modal_price / msp | 9 | Remove currency; numeric | `*_price_raw` |
| transport | mandi_id | 1 | Map to `MANDI###` | `mandi_id_raw` |
| transport | source_warehouse / destination_warehouse | — | Standardize to consistent case; no mapping table needed unless domain rules specified | — |
| transport | departure_time / arrival_time | 3 / 13 | Parse; missing arrival_time flagged | `*_time_raw` |
| transport | distance | 8 | Convert `miles` → km (×1.60934) | `distance_raw`, `distance_unit_raw` |
| transport | distance_unit | 8 / 13 | Standardize; assume `km` if missing (with flag) | `unit_assumed_km` |
| transport | transit_hours | 11 | Negative flagged; derived from times if possible | `negative_transit_flag`, `derived_transit_hours` |
| transport | vehicle_no | 16 | Uppercase; normalize spacing; missing flagged | `vehicle_format_corrected`, `missing_vehicle_no` |
| transport | driver_id | 13 | Keep missing; flag | `missing_driver_id` |
| weather | sensor_id | — | Confirm as identifier; no standardization needed unless patterns vary | — |
| weather | timestamp | 4 | Convert UTC → IST; standard format; missing flagged | `timestamp_utc_raw`, `timestamp_ist_converted` |
| weather | temperature | 6 | Convert to Celsius; extract embedded unit | `temperature_raw`, `temperature_celsius` |
| weather | temp_unit | 6 / 13 | Standardize to `C`; extract if embedded | `temp_unit_extracted`, `missing_temp_unit` |
| weather | rainfall | 7 / 12 | Convert to mm; negative flagged | `rainfall_raw`, `rainfall_mm` |
| weather | rain_unit | 7 / 13 | Standardize to `mm`; assume `mm` if missing | `rain_unit_assumed_mm` |
| weather | humidity_percent | 13 | Keep missing; flag | `missing_humidity` |

---

# D. MAPPING TABLES REQUIRED (Design spec — NOT created yet)

Each mapping table to be stored in `docs/mappings/` (CSV format, reproducible):

1. `mandi_id_mapping.csv`: `raw_variant` → `canonical_id` (57 rows, covers 342 variants)
2. `crop_name_mapping.csv`: `raw_crop` → `canonical_crop` → `mapping_rule` (`explicit` / `requires_review`)
3. `quantity_units.csv`: `raw_unit` → `conversion_factor` → `standard_unit`
4. `distance_units.csv`: `raw_unit` → `conversion_factor` → `standard_unit`
5. `temp_units.csv`: `raw_unit` / `embedded_string` → `conversion_method`
6. `rain_units.csv`: `raw_unit` → `conversion_factor` → `standard_unit`
7. `price_formats.csv`: `raw_pattern_example` → `clean_action`
8. `date_formats.csv`: `detected_pattern` → `parsing_order` → `business_rule_note`

---

# E. NEGATIVE-VALUE TREATMENT (Detailed Design)

| Category | Count | % | Design Action | Audit / Validation |
|---|---|---|---|---|
| arrival_quantity (<0) | 1261 | 4.9% | `negative_quantity_flag` = 1; design branch: investigate / confirm error / drop with audit count; original preserved in `quantity_raw` | Count = 1261; no silent removal |
| transit_hours (<0) | 563 | 5.4% | `negative_transit_flag` = 1; same branch design | Count = 563 |
| rainfall (<0) | 1518 | 10.1% | `negative_rainfall_flag` = 1; same branch design; range −50.0 to 50.0 preserved | Count = 1518; original preserved |

Principle: Negative values are NEVER set to zero. They are either flagged (investigation branch) or explicitly marked as removed (with audit count) — never silently corrected.

---

# F. MISSING-VALUE TREATMENT (Detailed Design)

| Column | Dataset | Missing Count | Design Treatment | Audit / Validation |
|---|---|---|---|---|
| arrival_id | arrivals | 484 | Surrogate `SURROGATE_ARR_###` with `surrogate_id` flag | Count of surrogates = 484 |
| variety | arrivals | 3735 | `missing_variety` flag; keep `NaN` | Count preserved |
| unit | arrivals | 5143 | Extract embedded unit from `arrival_quantity` string. If unparseable: `quantity_quintals` = NaN; `unit_unresolvable` = 1. NEVER assume `Qtl`. | Unresolved count = exact unparseable |
| farmer_count | arrivals | 3899 | `missing_farmer_count` flag | Count preserved |
| mandi_id | price | 1235 | `missing_mandi_id_price` flag; do NOT invent from district | Count = 1235 |
| district | price | 773 | `missing_district_price` flag | Count = 773 |
| arrival_time | transport | 1053 | `missing_arrival_time` flag | Count = 1053 |
| transit_hours | transport | 518 | If times exist: `derived_transit_hours` = 1; else `missing_transit_hours` | Derived count documented |
| distance_unit | transport | 1032 | Extract embedded unit from `distance` value string. If unparseable: `distance_km` = NaN; `distance_unit_unresolvable` = 1. NEVER assume `km`. | Unresolved count = exact unparseable |
| vehicle_no | transport | 1622 | `missing_vehicle_no` flag | Count preserved |
| driver_id | transport | 1551 | `missing_driver_id` flag | Count preserved |
| district | master | 4 | `missing_district_master` flag | Count = 4 |
| state | master | 4 | `missing_state_master` flag | Count = 4 |
| mandi_type | master | 11 | `missing_mandi_type` flag | Count = 11 |
| total_area_acres | master | 6 | `missing_area_acres` flag | Count = 6 |
| timestamp | weather | 1555 | `missing_timestamp` flag | Count = 1555 |
| temp_unit | weather | 2263 | Extract from embedded string if present (`temp_unit_extracted`); else `missing_temp_unit` | Extracted count documented |
| rainfall | weather | 791 | `missing_rainfall` flag | Count = 791 |
| rain_unit | weather | 791 | Extract from embedded `rainfall` value or `rain_unit` column. If `rain_unit` missing but `rainfall` non-null: assume `mm` ONLY if `rain_unit` column is explicitly present as empty (not unparseable). If truly unresolvable: `rainfall_mm` = NaN; `rain_unit_unresolvable` = 1. Do NOT invent `mm` without evidence. | Unresolved count documented |
| humidity_percent | weather | 1500 | `missing_humidity` flag | Count = 1500 |

Principle: No business-critical value is silently filled. Every assumption produces an audit column.

---

# G. DUPLICATE TREATMENT (Detailed Design)

### G1. Exact Duplicate Rows
- **Detection**: `duplicated()` check on full row.
- **Design action**: Add audit column `is_duplicate` (1 for duplicates). Drop only after confirming zero conflicts (same ID, same all attributes). Keep first occurrence; drop rest. Log count.
- **Audit**: `duplicate_dropped` column (0 for kept; 1 for dropped). Original count preserved in audit log.
- **Affected counts**: arrivals 750; transport 400; master 3; price 0; weather 0.

### G2. Conflicting Duplicate IDs (Rule 15)
- **Detection**: Group by `mandi_id` (or other key); check if same ID has different values in any other column.
- **Design action**: If conflict found: do NOT drop; escalate to business rule (`conflicting_id_flag` = 1); preserve both records; document conflict.
- **Validation**: Confirm zero conflicts exist in all datasets (Step 3 Section 5 confirms: zero ID collisions with conflicting attributes). Design accounts for future conflicts.

---

# H. JOIN STRATEGY (Rule 18 / Section I)

### H1. Direct Joins (100% verified in Step 3 Section I)
```
mandi_master.mandi_id (57 unique, 0 missing)
    → mandi_arrivals.mandi_id (57 unique normalized, 100% overlap)
    → price_and_msp.mandi_id (57 unique normalized, 100% overlap)
    → transport_logistics.mandi_id (57 unique normalized, 100% overlap)
```
- **Join type**: Left join from master; inner join optional based on analysis need.
- **Key**: Normalized `MANDI###` after cleaning design applied.
- **Audit**: `join_key_normalized` preserved; `join_match_confirmed` flag.

### H2. Weather-to-District/Mandi Mapping (Rule 19 — EXPLICIT LIMITATION)
- **Problem**: Weather dataset (`track3_weather_sensors.xlsx`) does not contain `mandi_id` or `district`; it contains `sensor_id` only (Step 3 Section I / Section 9). No `sensor_id` → `district` or `mandi_id` mapping exists in any supplied organizer data or dataset notes.
- **Design decision (explicit)**:
  - NO `sensor_to_district_mapping.csv` is invented or created.
  - Mandi-level weather attribution is UNSUPPORTED by the available data.
  - Analysis must use date-level weather aggregation only (aggregate by `date` across all sensors, or by `date` + `timezone` if needed).
  - Do NOT claim that a particular mandi experienced a particular sensor's weather.
  - This limitation must be documented in the final README/deliverable.
- **Reason**: No evidence exists to support a sensor-to-mandi mapping. Inventing one would create false associations.
- **Audit/validation**: `weather_mandi_join_supported` = 0 (flag confirming no mandi-level join performed); `date_level_aggregation_only` = 1; final README includes an explicit limitation statement.

---

# I. VALIDATION CHECKS (Rule 20 — Post-Cleaning Design)

Every cleaned dataset design includes these validation checks (not executed — design spec):

1. **Row count audit**: Original count → cleaned count → dropped count (must match audit log).
2. **Column type audit**: Every column must match intended data type (numeric for quantity/price/temp/rain/distance; datetime for dates; string for categorical/IDs).
3. **Unique value audit**: Confirm unique counts match expected (57 mandi IDs; 36 → reduced crop groups).
4. **Negative value audit**: Confirm negative flags preserved or removed with count; confirm no negative values remain in cleaned dataset unless explicitly retained with flag.
5. **Missing value audit**: Confirm audit flags exist; confirm counts preserved; confirm assumptions documented.
6. **Mapping audit**: Confirm mapping tables cover 100% of transformed values (no unmapped values silently dropped).
7. **Cross-dataset join audit**: Confirm join keys overlap at 100% (or document missing coverage); confirm no false joins from unmapped IDs.
8. **Audit trail completeness**: Confirm `raw_` columns preserved for every transformed column; confirm `audit_` / `flag_` columns exist for every transformation.

---

# J. CLEANING AUDIT / PROVENANCE STRATEGY

Every cleaned output design must include these audit columns (not executed):

- `source_file`: Original file name.
- `row_index_raw`: Original row index in raw file (for traceability).
- `record_audit_id`: Unique identifier for the cleaned record (linkable to audit log).
- For every transformed column: `*_raw` (original value preserved) + `*_cleaned` (new value) + `*_audit_flag` (if assumption/derivation/drop applied).
- `cleaning_version`: Version identifier of this design document (for reproducibility).
- `cleaning_timestamp`: Timestamp of when cleaning would be applied (design placeholder).

Audit log file (design spec): `docs/audit/cleaning_audit_log.csv` — one row per dropped/altered/derived record with reason, original index, and transformation applied.

---

# K. EXPECTED OUTPUT DATASETS (Design Spec — NOT CREATED)

These datasets are specified by design but NOT produced in this step:

| Output File | Source | Design Description | Audit Columns Included |
|---|---|---|---|
| `cleaned/track3_mandi_master_clean.csv` | master | 57 rows; duplicates removed; missing flags; standard IDs confirmed | `is_duplicate`, `missing_*` flags |
| `cleaned/track3_mandi_arrivals_clean.csv` | arrivals | 25,750 − duplicates (750) = ~25,000; standard mandi IDs; normalized crops (6 groups + ungrouped flagged); quantity in quintals; dates parsed; negative flags; missing flags; audit columns | All audit columns per design |
| `cleaned/track3_price_and_msp_clean.csv` | price (JSON → CSV design) | 12,000 rows; standard mandi IDs; prices numeric (currency removed); dates parsed; missing flags; audit columns | All audit columns |
| `cleaned/track3_transport_logistics_clean.csv` | transport | 10,400 − duplicates (400) = ~10,000; standard IDs; distance in km; dates parsed; transit negative flags; vehicle standardized; missing flags | All audit columns |
| `cleaned/track3_weather_sensors_clean.csv` | weather (XLSX → CSV design) | 15,000 rows; timestamp in IST; temperature Celsius; rainfall mm; negative rainfall flags; missing flags; timezone source documented | All audit columns |
| `mappings/*.csv` | Design spec | Mapping tables for mandi, crop, units, formats, dates | — |
| `docs/audit/cleaning_audit_log.csv` | Design spec | One row per altered/dropped record with reason | — |

---

# L. RISKS AND ASSUMPTIONS

1. **Ambiguous date formats** (Rule 3, revised): `DD-MM-YYYY` vs `MM-DD-YYYY` ambiguous for `01-07-2026`, `02.03.2026`. Design: `date_ambiguous` = 1; `date_raw` preserved; `date_parsed` = NaT unless explicit business rule supports DD-MM-YYYY (documented). Count of ambiguous reported. No silent interpretation.
2. **Crop name groups** (Rule 2): 13 raw variants ungrouped; remain `REQUIRES_INVESTIGATION`. No false grouping.
3. **Weather-to-district mapping** (Rule 19, revised): NO `sensor_id` → `district`/`mandi_id` mapping exists in organizer data or notes. Mandi-level weather attribution is UNSUPPORTED. Analysis uses date-level aggregation only. Final README must document this limitation explicitly (`weather_mandi_join_supported` = 0).
4. **Negative rainfall interpretation** (Rule 12, revised — single branch): `negative_rainfall_flag` = 1; `rainfall_raw` preserved; `rainfall` (cleaned) = NaN. NEVER 0. Count = 1518. Original preserved in audit.
5. **Quantity unit assumption for missing units** (Rule 5, revised — NO assumption): Evidence inspected: 5143 missing-unit rows have embedded units in `arrival_quantity` string (e.g., `'415.88 qtl'`, `'36,654.0 KG'`). Design: extract embedded unit; apply conversion_factor. If unparseable: `quantity_quintals` = NaN; `unit_unresolvable` = 1. NEVER assume `Qtl`. Unresolved records preserved separately.
6. **Quantity conversion factor** (Rule 5, corrected): `conversion_factor` clearly defined — quintal = 1.0; tonne/MT = 10.0; kg = 0.01. NO 0.1 error.
7. **Distance unit assumption** (Rule 8 / Section F, revised — NO assumption): Evidence inspected: 1032 missing `distance_unit` rows have embedded units (`'316.5 KM'`, `'196.7 KM'`). Design: extract embedded unit; apply conversion. If unparseable: `distance_km` = NaN; `distance_unit_unresolvable` = 1. NEVER assume `km`.
8. **Negative value policy** (Rules 10/11/12, revised — single production branch): Negative arrival qty (1261) → NaN + flag; negative transit (563) → NaN + flag; negative rainfall (1518) → NaN + flag. NEVER 0. Original in audit. Counts preserved.
9. **No raw data modification**: Confirmed — 6 files untouched in `data/raw/`. Zero cleaned datasets. Zero execution.
10. **Reproducibility / audit**: Every rule references explicit mapping table or documented evidence. `*_raw` + `*_cleaned` + `audit_flag` for every transformed column. Audit log (`docs/audit/cleaning_audit_log.csv`) specified.

---

# DOCUMENT CONTROL

| Field | Value |
|---|---|
| Title | CLEANING DESIGN DOCUMENT |
| Project | TransOrg AgentIQ Datathon — Track 3: AgriTech |
| Phase | Day 1 — Step 4 (Cleaning Design ONLY) |
| Status | DESIGN COMPLETE — NO IMPLEMENTATION EXECUTED |
| Raw files modified | NONE |
| Cleaned datasets created | NONE |
| Design rules covered | 20 rules (1–20, all sections) |
| Sections | A (Architecture), B (Dataset rules), C (Column rules), D (Mappings), E (Negative), F (Missing), G (Duplicates), H (Joins), I (Validation), J (Audit), K (Output), L (Risks) |

---

# STOP — DESIGN ONLY — NO CLEANING EXECUTION

This document specifies the complete cleaning pipeline design. It does NOT:
- Modify any file in `data/raw/`
- Create any cleaned dataset file
- Execute any transformation code
- Delete, rename, or overwrite any raw value
- Produce mapping table files (design spec only)

Awaiting user approval to proceed to cleaning implementation (Step 5 or as directed).
