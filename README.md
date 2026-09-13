# 🌾 TransOrg AgentIQ Datathon — Track 3: AgriTech
## Mandi-to-Market Supply Chain Optimizer

### Cleaning Pipeline — Step 5 Completed

### Project Status (Day 1 — All Steps)
- [x] Raw data profiling (5 datasets, 6 files)
- [x] Cleaning design (`docs/CLEANING_DESIGN.md`) + Pipeline (`scripts/run_cleaning.py`)
- [x] Cleaned datasets (`data/cleaned/` — 5 files) + Mappings + Audit
- [x] Analytics design (`docs/ANALYTICS_DESIGN.md`) + Pipeline (`scripts/run_analytics.py`)
- [x] Analytics outputs (`analytics/` — 10 files) + Validation Report
- [x] Dashboard design (`docs/DASHBOARD_DESIGN.md`) + Implementation (`dashboard/app.py`)
- [x] Unit tests: `tests/test_cleaning.py`, `tests/test_dashboard_data.py`
- [x] Raw file integrity verified (not modified)

### Step 6 — Analytics Layer
Run: `python scripts/run_analytics.py`
Outputs: `analytics/` (10 CSV files), `reports/ANALYTICS_VALIDATION_REPORT.txt`
Key KPIs: 1,300,773 Qtl total arrivals | 40.34% price crash rate | 57 active mandis | 12.94h avg transit | Weak weather-arrival correlation (date-level only, no sensor-to-mandi mapping)

### Dataset Summary (Raw → Cleaned)

| Dataset | Raw Rows | Cleaned Rows | Duplicates Removed | Key Flags |
|---|---|---|---|---|
| mandi_master | 60 | 60 | 0 | 4 missing district/state |
| mandi_arrivals | 25750 | 25750 | 0 | 5143 quantity converted; 1261 negative quantities flagged; 20607 unit unresolvable |
| price_and_msp | 12000 | 12000 | 0 | 9576 min_price converted; 1235 missing mandi_id |
| transport_logistics | 10400 | 10400 | 0 | 1032 distance converted (km); 563 negative transit flagged |
| weather_sensors | 15000 | 15000 | 0 | 15000 temp converted (°C); 12691 rain converted (mm); 1518 negative rainfall |

### Reproduce the Pipeline
```bash
python scripts/run_cleaning.py
```
Reads only: `data/raw/`
Writes to: `data/cleaned/`, `docs/mappings/`, `docs/audit/`, `reports/`

### Key Design Decisions
- **Quantity**: Converts embedded units (KG → 0.01 Qtl, Tonne/MT → 10.0 Qtl, Qtl unchanged). Negative quantities set to NaN + `negative_quantity_flag = 1` (never zero).
- **Distance**: Converts embedded units (miles × 1.60934 → km). Missing/unresolvable units flagged (`distance_unit_unresolvable`). Never assumes km.
- **Temperature**: Fahrenheit converted to Celsius `(F - 32) * 5/9`.
- **Rainfall**: Inches converted to mm (× 25.4). Negative rainfall set to NaN + `negative_rainfall_flag = 1`.
- **Price**: Currency symbols (₹, Rs, Rs., INR) and commas removed; converted to float.
- **Mandi IDs**: 342 raw variants normalized to `MANDI001`–`MANDI057` (mapping: `docs/mappings/mandi_id_mapping.csv`).
- **Crop Names**: 36 variants mapped; 27 confirmed to 6 groups; 9 unresolved (`REQUIRES_INVESTIGATION`) preserved in `docs/mappings/crop_mapping.csv`.
- **Duplicates**: Exact duplicate rows removed; counts preserved in audit.
- **Negative Values**: Never converted to zero. Original preserved in `*_raw` columns; cleaned set to NaN with audit flag.
- **Weather-to-Mandi Mapping**: UNSUPPORTED (no sensor→district/mandi mapping exists). Date-level weather aggregation only.
- **Ambiguous Dates**: Not silently interpreted; preserved with `date_ambiguous = 1` and parsed `NaT`.

### Limitations
- No sensor-to-district/mandi mapping exists in organizer data; mandi-level weather attribution is unsupported.
- 9 unresolved crop variants require domain expertise for canonical mapping.
- 20607 arrival quantity records have unresolvable embedded units (preserved, not guessed).
- 1235 price records have missing `mandi_id`.

### Files Created/Modified in Step 5
- `scripts/run_cleaning.py` — pipeline script
- `tests/test_cleaning.py` — transformation tests
- `docs/mappings/mandi_id_mapping.csv`
- `docs/mappings/crop_mapping.csv`
- `docs/audit/cleaning_audit_summary.json`
- `reports/CLEANING_VALIDATION_REPORT.txt`
- `README.md` — updated (this file)
- `data/cleaned/*.csv` (5 cleaned datasets)

### Step 7 — Executive Dashboard
Run: `streamlit run dashboard/app.py`
Structure: Executive Overview (KPIs + Insights + Supply Trend), Data Rescue Impact, Weather Intelligence
Architecture: `dashboard/app.py` → `analytics/` (no raw data access, no analytics duplication)
Key Sections: 6 Hero KPIs | Executive Insights Cards | Supply Concentration | Price Vulnerability Matrix | Warehouse Transit | Weather-Arrival Correlation | Data Rescue Before/After
Design: Professional, minimal clutter, semantic colors, statistical rigor (p90 method documented, correlation p-values shown), limitation transparency (weather-to-mandi unsupported)

### Step 8 — Agentic Agri Intelligence Layer
Run: `python -m unittest tests/test_agent.py` (offline; no API key required)  
Architecture: `agent/core.py` → deterministic pipeline (intent parser → router → analytics tool → validator → chart selector → explanation)  
Key Sections: 10 Supported Intents (OVERVIEW, SUPPLY_TREND, MANDI_ANALYSIS, CROP_ANALYSIS, PRICE_MSP, PRICE_RISK, LOGISTICS, WEATHER, DATA_QUALITY, EXECUTIVE_INSIGHTS) + Safe Unsupported Fallback  
Grounding: All answers derived exclusively from `analytics/*.csv`; no fabricated metrics  
Chart Selection: Deterministic mapping (PRICE_RISK → scatter, SUPPLY_TREND → line, LOGISTICS → bar, WEATHER → dual-axis with correlation note, DATA_QUALITY → transformation bar)  
Safeguards: No unsupported weather-to-mandi/district mapping claimed (date-level only). Statistical P90 method documented (21.7h). Correlation does not imply causation explicitly stated. Data rescue exclusions (20,607 unresolvable records, 80%) referenced. Cautious business language enforced.
Design: `docs/AGENT_DESIGN.md`. Tools: `agent/tools/*.py`. Tests: `tests/test_agent.py` (12/12 pass). Report: `reports/AGENT_EVALUATION_REPORT.txt`.

### Safety Verification (All Steps)
- `data/raw/` untouched (original file modification times preserved: 2026-09-12 17:31).
- No AI agent, chatbot, LLM API, LangChain, or GraphRAG added (not required for Step 7).
- No unsupported weather-to-mandi/district mapping claimed.
- No fabricated recommendations — all insights derived from `analytics/` outputs.
- No fake "real-time" claims.
- All exclusions (unresolved crops, unresolvable units, negative values) documented.

### Reproduce Commands
```bash
# Cleaning
python scripts/run_cleaning.py

# Analytics
python scripts/run_analytics.py

# Tests
python -m unittest tests/test_cleaning.py
python tests/test_dashboard_data.py

# Dashboard
streamlit run dashboard/app.py
```

### Files Created (All Steps)
**Cleaning:** `scripts/run_cleaning.py`, `tests/test_cleaning.py`, `docs/mappings/*.csv`, `docs/audit/*.json`, `reports/CLEANING_VALIDATION_REPORT.txt`
**Analytics:** `docs/ANALYTICS_DESIGN.md`, `scripts/run_analytics.py`, `reports/ANALYTICS_VALIDATION_REPORT.txt`, `analytics/*.csv`
**Dashboard:** `docs/DASHBOARD_DESIGN.md`, `dashboard/app.py`, `dashboard/components/*.py`, `dashboard/utils/*.py`, `tests/test_dashboard_data.py`, `reports/DASHBOARD_VALIDATION_REPORT.txt`
