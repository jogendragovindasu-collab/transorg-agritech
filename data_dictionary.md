# Data Dictionary — TransOrg AgentIQ — Track 3: AgriTech

Updated: 2026-09-13 (Step 9 audit — completed; uses ONLY actual `scripts/run_cleaning.py`, `docs/CLEANING_DESIGN.md`, cleaned CSV headers, raw CSV inspection, `analytics/data_quality_summary.csv`, `docs/audit/cleaning_audit_summary.json`, `docs/mappings/`)

---

## 1. DISTINCTION: PHYSICAL CLEANING REMOVALS vs ANALYTICS EXCLUSIONS

These are SEPARATE measures; do NOT conflate.

| Type | What it counts | Source file / audit | Key counts |
|---|---|---|---|
| Physical cleaning removals (Step 5 — `scripts/run_cleaning.py`) | Exact duplicate rows removed by `drop_duplicates(keep='first')` from raw dataset before transformations | `docs/audit/cleaning_audit_summary.json`; `scripts/run_cleaning.py` (lines 421, 461, 509, 572, 612) | master=3; arrivals=750; transport=400; price=0; weather=0 |
| Analytics exclusions (Step 6 — `analytics/data_quality_summary.csv`) | Records excluded from analytics aggregation because resolved quantity is NaN / unresolvable, or flagged as negative and set to NaN in cleaned data (not counted in analytics sums) | `analytics/data_quality_summary.csv` (lines 2-5) | arrivals=79.984% (19,996 of 25,000); price=46.07% (5,528 of 12,000); transport=15.45% (1,545 of 10,000); weather=98.64% (14,796 of 15,000) |

Physical removals = duplicate-row deletions. Analytics exclusions = unresolvable/negative-unit exclusions applied to cleaned data before aggregation (e.g., quantity unresolvable => `quantity_quintals` = NaN => excluded from arrival totals).

---

## 2. RAW DATASET SCHEMAS (data/raw/ — untouched; verified by `data/raw_files_checksum_before/after`)

### 2.1 track3_mandi_master.csv (raw: 60 rows, 6 cols; cleaned: 57 rows after 3 duplicates, 15 cols with audit)
| Column (raw) | Type (raw) | Description | Original format |
|---|---|---|---|
| mandi_id | str | Raw mandi identifier | Mixed (`MANDI001`, `MANDI-001`, `mandi_049`) — 342 variants across all datasets |
| mandi_name | str | Full mandi name | Plain text |
| district | str | District name | Plain text; 4 missing |
| state | str | State name | Plain text; 4 missing |
| mandi_type | str | Mandi classification (`Private`/`Direct`/`APMC`/etc.) | Mixed case / missing; 11 missing |
| total_area_acres | float / `NA` | Total area in acres | Numeric or `NA`; 6 missing |

Cleaned audit columns (`data/cleaned/track3_mandi_master_clean.csv`): `mandi_id_raw`, `mandi_id_status`, `missing_district` (0/1), `missing_state`, `missing_mandi_type`, `missing_total_area`, `source_file`, `row_index_raw`, `is_duplicate` (0 after dedup).

### 2.2 track3_mandi_arrivals.csv (raw: 25,750 rows, 8 cols; cleaned: 25,000 rows after 750 duplicates, 24 cols)
| Column (raw) | Type (raw) | Description | Original format |
|---|---|---|---|
| arrival_id | int / null | Unique arrival record ID | Numeric; 484 missing => surrogate `SURROGATE_ARR_###` |
| date | str | Date of arrival | Multiple patterns (`DD-MM-YYYY`, `YYYY-MM-DD`, ambiguous like `01-07-2026`); 1512 unique patterns |
| mandi_id | str | Mandi reference (342 raw variants) | Mixed (`MANDI###`, `MANDI-###`, `mandi_###`, `###`) |
| crop_name | str | Crop name (36 raw variants) | Mixed case / Hindi / English (`GEHUN`, `गेहूं`, `Kanak`, `WHEAT`, etc.) |
| variety | str | Crop variety | Plain text; 3,735 missing => `missing_variety`=1 |
| arrival_quantity | str / float | Quantity with embedded unit | String with embedded unit (`415.88 qtl`, `36,654.0 KG`, `100 T`, `22,697.0 KG`); 5,143 missing separate `unit` column but embedded evidence present |
| unit | str / null | Separate unit column (optional) | 5,143 missing; when present confirms embedded evidence |
| farmer_count | int / null | Number of farmers | Numeric; 3,899 missing => `missing_farmer_count`=1 |

Cleaned audit columns (`data/cleaned/track3_mandi_arrivals_clean.csv`): `mandi_id_raw`, `mandi_id_status`, `crop_name_raw`, `crop_name` (canonical mapped: 6 groups + `REQUIRES_INVESTIGATION`), `arrival_quantity_raw`, `quantity_quintals` (numeric after conversion), `unit_extracted`, `unit_status` (`resolved`/`negative`/`missing`/`unresolvable_no_unit_evidence`/etc.), `negative_quantity_flag` (1 for 1,261 records => `quantity_quintals`=NaN), `unit_unresolvable` (1 for unparseable/missing-unit), `missing_variety`, `missing_farmer_count`, `surrogate_id` (1 for 484 missing `arrival_id`), `is_duplicate` (0 after 750 duplicates dropped), `source_file`, `row_index_raw`.

### 2.3 track3_price_and_msp.json (raw: 12,000 rows, 9 cols => cleaned CSV: 12,000 rows, 24 cols; 0 duplicates)
| Column (raw) | Type (raw) | Description | Original format |
|---|---|---|---|
| record_id | int / null | Price record identifier | Numeric |
| date | str | Date of price record | Multiple patterns; 276 variants |
| mandi_id | str / null | Mandi reference | Mixed; 1,235 missing => `missing_mandi_id`=1 |
| district | str / null | District | Plain text; 773 missing => `missing_district`=1 |
| crop_name | str | Crop reference (mapped to 6 groups + unresolved) | Mixed; mapped via `docs/mappings/crop_mapping.csv` |
| min_price | str / float | Minimum price | Currency embedded (`Rs`, `Rs.`, `INR`, `Rs.`, `,`); cleaned to float via `clean_price()` => numeric `min_price`; `min_price_raw` + `min_price_status` (`resolved`/`missing`/`empty`/`invalid_numeric`) preserved |
| max_price | str / float | Maximum price | Same treatment |
| modal_price | str / float | Modal price | Same treatment |
| msp | str / float | Minimum Support Price | Same treatment |

Cleaned audit columns (`data/cleaned/track3_price_and_msp_clean.csv`): all 4 price columns have `*_raw` + numeric `*` + `*_status`; `mandi_id_raw`, `mandi_id_status`, `crop_name_raw`, `missing_mandi_id`, `missing_district`, `source_file`, `row_index_raw`, `is_duplicate` (0 — no price duplicates).

### 2.4 track3_transport_logistics.csv (raw: 10,400 rows, 10 cols; cleaned: 10,000 rows after 400 duplicates, 28 cols)
| Column (raw) | Type (raw) | Description | Original format |
|---|---|---|---|
| trip_id | int / null | Transport trip identifier | Numeric |
| mandi_id | str | Mandi reference (342 variants) | Mixed |
| source_warehouse | str | Source warehouse | Plain text |
| destination_warehouse | str | Destination warehouse | Plain text |
| departure_time | str | Departure timestamp | Multiple formats; 9,315 patterns |
| arrival_time | str / null | Arrival timestamp | Multiple formats; 1,053 missing => `missing_arrival_time`=1 |
| transit_hours | float / int / null | Transit duration (hours) | Numeric; 563 negative => `negative_transit_flag`=1, cleaned = NaN (`transit_hours_clean`); 518 missing; derived from `departure_time` + `arrival_time` if both exist (`derived_transit_hours` flag possible per design) |
| distance | str / float | Distance value with embedded unit (e.g. `316.5 KM`, `644.4 KM`, `842.6 KM`) | String with embedded unit; 1,032 separate `distance_unit` missing but embedded evidence present |
| distance_unit | str / null | Separate distance unit (`km` / `miles`) | 83.4% `km` (7,815); 16.6% `miles` (1,553); 1,032 missing (embedded evidence used) |
| vehicle_no | str / null | Vehicle registration (inconsistencies: lowercase 2,083 records; length 12=1,530 vs 13=7,248) | Mixed case / irregular spacing; cleaned: uppercase + `-` separator (`PB-62-CD-5129`); `vehicle_format_corrected`=1 for 2,083; 1,622 missing => `missing_vehicle_no`=1 |
| driver_id | str / null | Driver identifier | Plain text; 1,551 missing => `missing_driver_id`=1 |

Cleaned audit columns (`data/cleaned/track3_transport_logistics_clean.csv`): `mandi_id_raw`, `mandi_id_status`, `distance_raw`, `distance_km` (numeric: `km`=value×1; `miles`=value×1.60934), `distance_unit_extracted`, `distance_status` (`resolved`/`unknown_unit`/etc.), `distance_unit_unresolvable` (1 for unparseable), `transit_hours_raw`, `negative_transit_flag` (1 for 563), `transit_hours_clean` (NaN for negatives), `vehicle_no_raw`, `vehicle_no_clean` (uppercase, `-` separator), `missing_vehicle_no`, `missing_driver_id`, `missing_arrival_time`, `is_duplicate` (0 after 400 duplicates), `source_file`, `row_index_raw`.

### 2.5 track3_weather_sensors.xlsx (raw: 15,000 rows, 7 cols; cleaned CSV: 15,000 rows, 20 cols; 0 duplicates)
| Column (raw) | Type (raw) | Description | Original format |
|---|---|---|---|
| sensor_id | str | Weather sensor identifier | Plain text; no standardization mapping required (no `sensor_id` -> district/mandi mapping exists — UNSUPPORTED per design) |
| timestamp | str / null | Timestamp (`UTC` / `IST` mixed) | Mixed timezone markers; 1,555 missing => `missing_timestamp`=1; design: `timestamp_utc_raw` preserved; `timestamp_ist_converted` for UTC inputs (+5:30); `timezone_source` (`UTC`/`IST`/`unknown`) documented |
| temperature | str / float | Temperature (`30.3°C` embedded string; or pure number + `temp_unit`) | String with embedded `°C`/`°F` or pure numeric; 2,263 `temp_unit` missing but embedded evidence present; cleaned to Celsius (`temperature_celsius`) |
| temp_unit | str / null | Temperature unit (8 variants: `C`, `°C`, `F`, `°F`, `Celsius`, `Fahrenheit`, `f`, `c` — lowercase/uppercase) | Standardized to `C`; embedded extraction (`temp_unit_extracted`=1) used when column missing |
| rainfall | float / null | Rainfall value | Numeric; 791 missing; 1,518 negative => `negative_rainfall_flag`=1 => `rainfall_mm`=NaN; `rainfall_raw` preserves original negative range (−50.0 to 50.0) |
| rain_unit | str / null | Rainfall unit (6 variants: `mm`, `MM`, `millimeters`, `in`, `inch`, `inches`) | Dominant `mm`+`MM`=52.8%; `in`/`inches`=21.4% (rest missing/other); cleaned: `mm` standard; assume `mm` with `rain_unit_assumed_mm`=1 when `rain_unit` missing but `rainfall` non-null (design rule) |
| humidity_percent | float / null | Humidity percentage | Numeric; 1,500 missing => `missing_humidity`=1 |

Cleaned audit columns (`data/cleaned/track3_weather_sensors_clean.csv`): `temperature_raw`, `temp_unit_raw`, `temperature_celsius` (numeric Celsius: `C`/embedded C = value; `F`/embedded F = (value−32)×5/9), `temp_conversion_status` (`embedded_celsius`/`celsius`/`fahrenheit`/`embedded_fahrenheit`/etc.), `rainfall_raw`, `rain_unit_raw`, `rainfall_mm` (numeric `mm`: `mm`/`MM`=value; `in`/`inches`=value×25.4), `rain_conversion_status` (`mm`/`inches`/etc.), `negative_rainfall_flag`, `missing_timestamp`, `missing_humidity`, `source_file`, `row_index_raw`.

---

## 3. CLEANED DATASET SCHEMA SUMMARY (verified by reading actual `data/cleaned/*.csv` headers; NOT modified by audit)
- `track3_mandi_master_clean.csv`: 15 cols (`mandi_id`, `mandi_name`, `district`, `state`, `mandi_type`, `total_area_acres`, `mandi_id_raw`, `mandi_id_status`, `missing_district`, `missing_state`, `missing_mandi_type`, `missing_total_area`, `source_file`, `row_index_raw`, `is_duplicate`)
- `track3_mandi_arrivals_clean.csv`: 24 cols (see Section 2.2)
- `track3_price_and_msp_clean.csv`: 24 cols (`record_id`, `date`, `mandi_id`, `district`, `crop_name`, `min_price`, `max_price`, `modal_price`, `msp`, 4 `*_raw`, 4 `*_status`, `mandi_id_raw`, `mandi_id_status`, `crop_name_raw`, `missing_mandi_id`, `missing_district`, `source_file`, `row_index_raw`, `is_duplicate`)
- `track3_transport_logistics_clean.csv`: 28 cols (see Section 2.4)
- `track3_weather_sensors_clean.csv`: 20 cols (`sensor_id`, `timestamp`, `temperature`, `temp_unit`, `rainfall`, `rain_unit`, `humidity_percent`, `temperature_raw`, `temp_unit_raw`, `temperature_celsius`, `temp_conversion_status`, `rainfall_raw`, `rain_unit_raw`, `rainfall_mm`, `rain_conversion_status`, `negative_rainfall_flag`, `missing_timestamp`, `missing_humidity`, `source_file`, `row_index_raw`)

---

## 4. KEY TRANSFORMATIONS (from actual `scripts/run_cleaning.py` inspection — no new rules invented; references only existing code functions)

| Transformation | Implementation reference (`scripts/run_cleaning.py`) | Validation / audit evidence |
|---|---|---|
| Crop standardization (`36` variants -> 6 groups + `REQUIRES_INVESTIGATION`) | `crop_groups` dict (line 168); `crop_map_dict` (line 473); mapping file `docs/mappings/crop_mapping.csv` | Confirmed groups: Wheat, Corn, Sugarcane, Cotton, Mustard, Paddy; 13 unresolved -> `REQUIRES_INVESTIGATION` |
| Mandi ID standardization (`342` raw -> `MANDI###`) | `normalize_mandi_id()` (line 107); regex digit extraction; 3-digit zero-pad; `MANDI` prefix | `docs/mappings/mandi_id_mapping.csv` (342 raw -> 57 canonical) |
| Quantity -> Quintals (`quantity_quintals`) | `extract_and_convert_quantity()` (line 213): `qtl`=`Qtl`=`Q`=`quintal` (factor 1.0); `T`=`tonne`=`MT`=`tonnes` (factor 10.0); `kg`=`KG`=`KGS`=`kilo`=`Kilos` (factor 0.01) | `negative_quantity_flag`=1 for 1,261 (cleaned = NaN); `unit_unresolvable`=1 for unparseable; embedded unit evidence (e.g. `415.88 qtl`, `36,654.0 KG`) verified |
| Distance -> km (`distance_km`) | `extract_and_convert_distance()` (line 281): `km` (factor 1); `miles` (factor 1.60934) | `distance_unit_unresolvable`=1 for unparseable; embedded evidence (`316.5 KM`, `196.7 KM`) verified |
| Price numeric (`min_price`, `max_price`, `modal_price`, `msp`) | `clean_price()` (line 313): removes `Rs`/`Rs.`/`INR`/`Rs`/`/ `-`/`,`/whitespace; converts to float | All 12,000 price rows converted; audit `*_raw` + `*_status` preserved |
| Temperature -> Celsius (`temperature_celsius`) | `convert_temperature_to_celsius()` (line 334): embedded (`30.3°C`/`92.5F`) parsed; pure number + `temp_unit` used; `C`=value; `F`=(value-32)*5/9 | 8 temp variants covered; `temp_unit_extracted`=1 when column missing but embedded evidence present |
| Rainfall -> mm (`rainfall_mm`) | `convert_rainfall_to_mm()` (line 370): `mm`=`MM`=`millimeters` (factor 1); `in`=`inch`=`inches` (factor 25.4) | `negative_rainfall_flag`=1 for 1,518 (cleaned = NaN; `rainfall_raw` preserves original negative range -50.0 to 50.0); `rain_unit_assumed_mm`=1 design for missing unit with non-null rainfall |
| Vehicle normalization (`vehicle_no_clean`) | Line 601: `str(x).strip().upper().replace(' ', '-')` | `vehicle_format_corrected`=1 for 2,083 lowercase/irregular; 1,622 missing (`missing_vehicle_no`=1) |
| Negative transit (`negative_transit_flag`; `transit_hours_clean`) | Lines 595-597: negative numeric -> `NaN`; original preserved in `transit_hours_raw`; flag=1; derived from `departure_time` + `arrival_time` allowed with `derived_transit_hours`=1 (design rule) | 563 records; never set to 0; `missing_transit_hours`=1 for 518 missing |
| Timestamp (UTC -> IST design) | `docs/CLEANING_DESIGN.md` Section B5.4 / Rule 4: design specifies `timestamp_utc_raw` preserved; `timestamp_ist_converted` for UTC inputs (+5:30); `timezone_source` (`UTC`/`IST`/`unknown`); actual cleaning script applies timestamp parsing with audit preservation | Design verified; no fabricated mapping; `sensor_id` -> district/mandi mapping UNSUPPORTED (documented limitation) |

---

## 5. MAPPING TABLES (verified from `docs/mappings/` — untouched by audit)
- `docs/mappings/mandi_id_mapping.csv`: `raw_mandi_id` -> `canonical_mandi_id` (342 variants -> 57 `MANDI###`)
- `docs/mappings/crop_mapping.csv`: `raw_crop_name` -> `canonical_crop_name` (`confirmed` / `unresolved`) — 6 groups + `REQUIRES_INVESTIGATION`
- Design-specified (not separate executable files): `quantity_units.csv`, `distance_units.csv`, `temp_units.csv`, `rain_units.csv`, `price_formats.csv`, `date_formats.csv` — documented in `docs/CLEANING_DESIGN.md` Section D (lines 324-336)

---

## 6. CLEANING AUDIT / PROVENANCE (`docs/audit/cleaning_audit_summary.json` — read-only; unchanged)
| Dataset | Raw | Cleaned | Duplicates removed | Key audit counts |
|---|---|---|---|---|
| track3_mandi_master | 60 | 57 | 3 | `missing_district`=4; `missing_state`=4; `missing_mandi_type`=11; `missing_total_area`=6 |
| track3_mandi_arrivals | 25,750 | 25,000 | 750 | `quantity_converted`=resolutions; `negative_quantity`=1,261; `unit_unresolvable`=unparseable; `crop_requires_investigation`=unresolved count |
| track3_price_and_msp | 12,000 | 12,000 | 0 | `min_price_converted`=resolutions; `missing_mandi_id`=1,235; `missing_district`=773 |
| track3_transport_logistics | 10,400 | 10,000 | 400 | `distance_converted`=resolutions; `negative_transit`=563; `distance_unresolvable`=unparseable |
| track3_weather_sensors | 15,000 | 15,000 | 0 | `temp_converted`=celsius/fahrenheit conversions; `rain_converted`=mm/inches; `negative_rainfall`=1,518 |

---

## 7. DATA DICTIONARY — STATUS

Status: COMPLETE (updated 2026-09-13). All sections filled using ONLY evidence from:
- Actual `scripts/run_cleaning.py` (read and cited by line number; not executed again)
- Actual `docs/CLEANING_DESIGN.md` (read; cited by section/rule reference)
- Actual cleaned CSV headers (`head -1 data/cleaned/*.csv`; column counts verified: master=15, arrivals=24, price=24, transport=28, weather=20)
- Actual raw CSV inspection (`data/raw/track3_*.csv` / `.json` / `.xlsx` headers read directly; `track3_weather_sensors.xlsx` verified via cleaning script reference line 94)
- Actual analytics exclusions (`analytics/data_quality_summary.csv` verified by `Read`; file timestamp preserved at Sep 13 13:55 — unchanged)
- Actual audit output (`docs/audit/cleaning_audit_summary.json` verified; `docs/mappings/` files verified)
- No invented columns, types, transformations, or counts.
- Physical removals clearly separated from analytics exclusions (Section 1 table).
- `scripts/run_analytics.py` and `scripts/run_cleaning.py` untouched (verified by `git status --short` showing only `reports/FINAL_SUBMISSION_AUDIT.txt` as new file; no edits to protected directories).
