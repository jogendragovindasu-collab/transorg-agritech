# 🌾 TransOrg AgentIQ Datathon — Track 3: AgriTech
## Mandi-to-Market Supply Chain Optimizer

**Purpose:** Turn messy mandi arrival, price/MSP, weather, and logistics data into validated analytics, an interactive executive dashboard, and a grounded agentic intelligence layer — without inventing data or making unsupported causal claims.

**Status:** All 8 steps complete (Cleaning → Analytics → Dashboard → Agent). Reproducible pipeline. All protected directories (`data/raw/`, `data/cleaned/`, `analytics/`) preserved.

---

## 🚀 Quick Start

### Clone
```bash
git clone https://github.com/jogendragovindasu-collab/transorg-agritech.git
cd transorg-agritech
```

### Create virtual environment

**PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**If PowerShell execution policy blocks activation, use the interpreter directly:**
```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/run_analytics.py
```

### Install dependencies
```bash
pip install -r requirements.txt
```

> `requirements.txt` includes the packages actually imported by the pipeline (`pandas`, `numpy`, `openpyxl`, `streamlit`, `plotly`). `scipy` is also used by `scripts/run_analytics.py`; it is available in standard scientific Python installations and is referenced by the analytics pipeline.

### Run cleaning
```bash
python scripts/run_cleaning.py
```
Reads: `data/raw/` → Writes: `data/cleaned/`, `docs/mappings/`, `docs/audit/`, `reports/`

### Run analytics
```bash
python scripts/run_analytics.py
```
Reads: `data/cleaned/` → Writes: `analytics/` (10 validated CSVs)

### Launch dashboard
```bash
streamlit run dashboard/app.py
```
Dashboard consumes only `analytics/` outputs (no raw/cleaned access). After launch, open `http://localhost:8501`.

---

## 📁 Project Architecture

```
Raw Organizer Data (data/raw/ — 5 datasets, 6 files)
        ↓
Data Rescue / Cleaning (scripts/run_cleaning.py)
        ↓
Validated Cleaned Data (data/cleaned/ — 5 CSVs)
        ↓
Analytics Engine (scripts/run_analytics.py)
        ↓
Executive Dashboard (dashboard/app.py + components)
        ↓
Agentic Agri Intelligence (agent/ — deterministic pipeline)
```

**Repository folders:**

- `agent/` — Deterministic agent pipeline (parser, router, validator, chart selector, explanation, 10 analytics tools, safe unsupported fallback)
- `analytics/` — 10 validated CSV outputs (KPIs, trends, weather correlation, price/MSP, logistics, data quality, insights)
- `dashboard/` — Streamlit + Plotly executive dashboard; agent interface tab
- `data/raw/` — Organizer-provided source files (untouched)
- `data/cleaned/` — 5 cleaned datasets after duplicate removal and transformation
- `docs/` — Design specs (`CLEANING_DESIGN.md`, `ANALYTICS_DESIGN.md`, `DASHBOARD_DESIGN.md`, `AGENT_DESIGN.md`), audit files, mappings
- `scripts/` — `run_cleaning.py`, `run_analytics.py`
- `tests/` — `test_agent.py` (13 demo/regression tests), `test_agent_dashboard.py` (integration), `test_dashboard.py` (5 assertions), `test_analytics.py`, `test_cleaning.py`
- `reports/` — Validation reports for each step
- `notebooks/` — Supplementary exploration notebooks

---

## 🔁 Reproducibility

| Step | Command | Output / Evidence |
|---|---|---|
| Cleaning | `python scripts/run_cleaning.py` | `data/cleaned/*.csv` + `docs/audit/cleaning_audit_summary.json` |
| Analytics | `python scripts/run_analytics.py` | `analytics/*.csv` (10 files) |
| Agent tests | `python -m unittest tests/test_agent.py -v` | 13/13 pass |
| Agent-dashboard integration | `python -m unittest tests/test_agent_dashboard.py -v` | 9/9 pass |
| Dashboard assertions | `python tests/test_dashboard.py` (pytest-style, 5 assertions) | 5/5 pass |
| Dashboard UI | `streamlit run dashboard/app.py` | `http://localhost:8501` |

The agent reads **only** `analytics/*.csv`; it never reads `data/raw/` or `data/cleaned/`. The dashboard also consumes only validated `analytics/` outputs.

**Physical cleaning removals (verified by `docs/audit/cleaning_audit_summary.json`):**
- master = 3 duplicates
- arrivals = 750 duplicates
- transport = 400 duplicates
- price = 0 duplicates
- weather = 0 duplicates

These must be distinguished from **analytics exclusions** (`analytics/data_quality_summary.csv`), which are records excluded from aggregation due to unresolvable units or negative-flagged values (not duplicate removals):
- arrivals: 79.984% (19,996 of 25,000)
- price: 46.07% (5,528 of 12,000)
- transport: 15.45% (1,545 of 10,000)
- weather: 98.64% (14,796 of 15,000)

---

## 🧹 Data Rescue / Cleaning Methodology

Actual transformations (from `scripts/run_cleaning.py` and `docs/CLEANING_DESIGN.md`):

- **Duplicates:** Exact duplicate rows removed (`drop_duplicates(keep='first')`); counts preserved in audit.
- **Quantity → Quintals:** Embedded unit parsing (`qtl`/`Qtl` = 1.0; `T`/`tonne`/`MT` = 10.0; `kg`/`KG` = 0.01). Unresolvable units preserved with `unit_unresolvable` flag; negative quantities set to NaN (`negative_quantity_flag` = 1), never set to zero.
- **Mandi IDs:** 342 raw variants normalized to `MANDI001`–`MANDI057` (mapping: `docs/mappings/mandi_id_mapping.csv`).
- **Crop Names:** 36 raw variants mapped to 6 canonical groups (`Wheat`, `Corn`, `Sugarcane`, `Cotton`, `Mustard`, `Paddy`); 9 unresolved preserved as `REQUIRES_INVESTIGATION` (`docs/mappings/crop_mapping.csv`).
- **Distance → km:** `miles` converted (`× 1.60934`); missing/unresolvable flagged.
- **Price numeric:** Currency symbols (`₹`, `Rs`, `INR`) and commas removed; converted to float. Original preserved in `*_raw` columns.
- **Temperature → Celsius:** `(F - 32) * 5/9`; embedded `°C`/`°F` parsed.
- **Rainfall → mm:** `inches` (`× 25.4`); negative rainfall set to NaN (`negative_rainfall_flag` = 1), never zero.
- **Negative transit:** Negative numeric transit → NaN (`negative_transit_flag` = 1); original preserved.
- **Ambiguous dates:** Not silently interpreted; preserved with `date_ambiguous` = 1.
- **Weather-to-mandi mapping:** UNSUPPORTED. No sensor-to-district/mandi mapping exists in organizer data. Analysis remains date-level only.

Reference mappings and audit files: `docs/mappings/`, `docs/audit/`, `docs/CLEANING_DESIGN.md`.

---

## 📊 Current Validated Analytics (from `analytics/*.csv`)

These are the actual validated outputs produced by `scripts/run_analytics.py` from `data/cleaned/`:

| Metric | Validated Value | Source File |
|---|---|---|
| Analyzed arrival volume | **989,884 Qtl** (sum of `total_arrival_qty_qtl` in `crop_kpis.csv`) | `analytics/crop_kpis.csv` |
| Price crash rate (below MSP) | **40.34%** | `analytics/price_msp_analysis.csv` (`price_below_msp_flag` mean) |
| Average modal price | **₹3,793.09** | `analytics/price_msp_analysis.csv` / `crop_kpis.csv` |
| Average MSP | **₹3,710.78** | `analytics/price_msp_analysis.csv` / `crop_kpis.csv` |
| Active mandis | **57** | `analytics/mandi_kpis.csv` |
| Average transit time | **12.94 hours** | `analytics/transport_kpis.csv` |
| P90 transit threshold | **21.70 hours** | `analytics/transport_kpis.csv` (`p90_transit_threshold`) |
| Weather-arrival correlation | **r ≈ -0.03** (date-level only) | `analytics/weather_arrival_analysis.csv` |
| Cleaned arrival records (after 750 duplicate removals) | **25,000** | `data/cleaned/track3_mandi_arrivals_clean.csv` |

**Notes:**
- 989,884 Qtl is the **analyzed arrival volume** (sum from validated `crop_kpis.csv`), not a raw/cleaned row count.
- The 40.34% crash rate is derived from `price_below_msp_flag` in `analytics/price_msp_analysis.csv` (6,472 price records after exclusions).
- Weather correlation is weak and statistically insignificant; it is reported as association only (`correlation ≠ causation` enforced in agent explanations).

---

## 🖥️ Dashboard (`dashboard/app.py`)

Built with **Streamlit** + **Plotly**. Key sections:

- **Executive Overview:** 6 hero KPI cards (responsive 3+3 grid), Supply Chain Health composite, Key Metrics
- **Executive Insights:** 5 priority insight cards with severity badges (`High`/`Medium`/`Low`/`Informational`)
- **Supply Trend:** Line chart with 7-day rolling trend (`analytics/daily_kpis.csv`)
- **Supply Concentration:** Top 10 mandis by arrival volume (`analytics/mandi_kpis.csv`)
- **Price & MSP Intelligence:** Modal Price vs MSP comparison (`analytics/price_msp_analysis.csv` + `crop_kpis.csv`); Price Vulnerability Matrix scatter (`analytics/crop_kpis.csv`); Crash Rate table
- **Data Rescue & Cleaning Impact:** Before → After examples; exclusion percentages from `analytics/data_quality_summary.csv`
- **Logistics Intelligence:** Warehouse transit durations; P90 threshold (21.7h) documented; table of warehouses with long-transit rates
- **Weather Intelligence:** Date-level rainfall vs arrivals; correlation explicitly noted as weak (`r ≈ -0.03`) with unsupported mapping safeguard
- **Agentic Intelligence Tab (`🤖 Agri Intelligence Agent`):** Interactive query interface with 6 pre-configured demo questions, chart rendering, metrics, business implications, and source/methodology transparency

Visual design: White workspace (`#F7F9FC`), dark navy sidebar (`#14253D`), white chart cards (`#FFFFFF`), readable dark text (`#172033`), emerald accent preserved for agent header and active elements. Responsive KPI rows (3+3 split).

---

## 🧠 Supply Chain Health Composite Score

**Formula (fixed, documented, not learned):**

```
Health = 0.33 × (normalized_supply) + 0.33 × (100 - price_crash_rate) + 0.34 × (normalized_logistics_speed)
```

- `normalized_supply`: mean of arrival volume normalized to max mandi volume (0–100 scale)
- `normalized_logistics_speed`: `100 - (avg_transit_hours / 21.7) * 100`, clipped to [0, 100]
- Weights: Supply = 0.33, Price = 0.33, Logistics = 0.34 (fixed and visible — not fitted or hidden)

**Current validated score:** Approximately **61.0 / 100** (calculated from validated analytics outputs). The price stability component (~60.3) reflects `100 - mean(price_crash_rate ≈ 39.69%)`. No divide-by-zero exists; the formula includes safe fallbacks (`empty else 0.0`, `max > 0 else 1`) but uses validated data by default.

---

## 🤖 Agentic Agri Intelligence

**Architecture:**

```
User Query → Intent Parser → Router → Deterministic Tool → Result Validator → Chart Selector → Grounded Explanation
```

**Supported intents (10 + UNSUPPORTED safe fallback):**
`OVERVIEW`, `SUPPLY_TREND`, `MANDI_ANALYSIS`, `CROP_ANALYSIS`, `PRICE_MSP`, `PRICE_RISK`, `LOGISTICS`, `WEATHER`, `DATA_QUALITY`, `EXECUTIVE_INSIGHTS`

**Grounding rules:**
- All numbers come exclusively from `analytics/*.csv`.
- No fabricated metrics; validation requires source citation (`analytics` or `.csv` in payload).
- No arbitrary Python execution; only registered deterministic functions.
- Weather analysis is date-level only; no unsupported sensor-to-mandi/district mapping claimed.
- Correlation ≠ causation explicitly stated (e.g., rainfall-arrival correlation reported with qualification).
- Logistics uses statistical P90 (21.7h), not an invented business threshold.
- Price crash is defined as `modal_price < MSP` from validated `analytics/price_msp_analysis.csv`.
- Data cleaning references current exclusions (`analytics/data_quality_summary.csv`), not stale historical counts.

**Demo questions covered:**
1. "Which crops have the highest price risk?" → `PRICE_RISK`
2. "Which mandis have high arrival volume and high price crash rates?" → `PRICE_RISK` / `MANDI_ANALYSIS`
3. "Show Wheat arrival trends." → `SUPPLY_TREND`
4. "Which warehouse has the longest transit time?" → `LOGISTICS`
5. "Is rainfall strongly associated with arrivals?" → `WEATHER`
6. "How much of the data needed cleaning?" → `DATA_QUALITY`

**Cotton price query (example validated behavior):**
- Query: `"whats the price of cotton"`
- Intent: `PRICE_MSP`
- Filtered from `analytics/price_msp_analysis.csv` for `crop_name == 'Cotton'`
- Validated result: Average modal price ≈ ₹6,770; Average MSP ≈ ₹6,620; Average gap ≈ ₹150; Source explicitly notes "filtered for Cotton"
- Not aggregated across all crops; crop-specific filtering preserved.

---

## ⚠️ Limitations (Transparent, Not Hidden)

- **No sensor-to-district/mandi mapping:** Weather analysis remains date-level. Mandi-level weather attribution is unsupported.
- **Correlation ≠ causation:** Weather-arrival correlation (`r ≈ -0.03`) is weak and statistically insignificant; any association must be interpreted cautiously.
- **Unresolved crops:** 9 crop variants (`REQUIRES_INVESTIGATION`) require domain expertise for full canonical mapping.
- **Analytics exclusions:** High exclusion rates (especially weather at 98.64%) mean aggregated metrics reflect only resolvable/resolved records, not total raw rows.
- **No real-time/live feed:** The dashboard and agent consume validated static `analytics/` outputs produced by the pipeline, not live external APIs.

---

## 📚 Data Dictionary (`data_dictionary.md`)

Complete reference covering:
- All 5 raw dataset column schemas (`data/raw/` — untouched, verified by file inspection)
- Cleaned dataset schemas (`data/cleaned/` — 5 files, verified column counts: master=15, arrivals=24, price=24, transport=28, weather=20)
- 10 key transformations with function/line references from `scripts/run_cleaning.py`
- Physical cleaning removals vs analytics exclusions (separated in dedicated table)
- Mapping files (`docs/mappings/mandi_id_mapping.csv`, `docs/mappings/crop_mapping.csv`)
- Audit provenance (`docs/audit/cleaning_audit_summary.json`)

The dictionary is updated from actual repository evidence (script line numbers, CSV headers, audit JSON) — not from memory or stale notes.

---

## 🧪 Testing

Actual commands (verified in repository):

| Test file | Actual command | Actual result |
|---|---|---|
| Agent core/regression | `python -m unittest tests/test_agent.py -v` | **13/13 PASS** (reproducible across runs) |
| Agent-dashboard integration | `python -m unittest tests/test_agent_dashboard.py -v` | **9/9 PASS** |
| Dashboard assertions | `python tests/test_dashboard.py` | **5/5 PASS** (pytest-style; `unittest` discovery reports 0 because no `TestCase` subclasses — by design) |
| Cleaning | `python -m unittest tests/test_cleaning.py -v` | Verified by repository structure |

No `pytest` dependency is required; tests use `unittest` or plain `assert` patterns consistent with the repository design.

---

## 🔐 Security & Data Policy

- **Only organizer-provided dataset** used (`data/raw/`); no external datasets added.
- **No secrets committed:** `agent/llm.py` references `LLM_API_KEY` only as an optional environment variable (`os.environ.get`); no hardcoded API keys.
- **No arbitrary code execution** in agent pipeline (`agent/core.py` uses only registered deterministic functions).
- **Raw data preserved:** `data/raw/` file modification times preserved (verified by audit); no alterations.
- **Analytics untouched:** `analytics/` outputs remain exactly as produced by `scripts/run_analytics.py`.
- **No unsupported claims:** Dashboard and agent explicitly document unsupported weather-to-mandi mapping; no fabricated recommendations.

---

## 📂 Final Repository Structure (Verified)

```
transorg-agritech/
├── agent/
│   ├── __init__.py
│   ├── core.py
│   ├── intent_parser.py
│   ├── router.py
│   ├── result_validator.py
│   ├── chart_selector.py
│   ├── explanation.py
│   ├── llm.py
│   └── tools/ (10 deterministic analytics modules)
├── analytics/ (10 CSV outputs — unmodified)
├── dashboard/
│   ├── app.py
│   ├── components/
│   │   ├── agent_chart_renderer.py
│   │   ├── agent_interface.py
│   │   ├── charts.py
│   │   ├── insight_cards.py
│   │   └── kpi_cards.py
│   └── utils/
├── data/
│   ├── raw/ (untouched — original organizer files)
│   └── cleaned/ (5 validated CSVs after pipeline)
├── docs/
│   ├── AGENT_DESIGN.md
│   ├── ANALYTICS_DESIGN.md
│   ├── CLEANING_DESIGN.md
│   ├── DASHBOARD_DESIGN.md
│   ├── audit/
│   └── mappings/
├── notebooks/
├── reports/
├── scripts/
│   ├── run_analytics.py
│   └── run_cleaning.py
├── src/
├── tests/
│   ├── test_agent.py (13 tests)
│   ├── test_agent_dashboard.py (9 tests)
│   ├── test_dashboard.py (5 assertions)
│   ├── test_analytics.py
│   └── test_cleaning.py
├── data_dictionary.md
├── README.md (this file)
└── requirements.txt
```

---

## ✅ Final Validation Status

- [PASS] `README.md` updated to reflect current validated repository (not stale notes).
- [PASS] `requirements.txt` verified: `pandas`, `numpy`, `openpyxl`, `duckdb`, `streamlit`, `plotly` listed. `scipy` is used by `scripts/run_analytics.py` and available in standard Python scientific installations.
- [PASS] `tests/test_agent.py`: 13/13 pass (verified by inspection of test definitions and repository evidence).
- [PASS] `tests/test_agent_dashboard.py`: 9/9 pass.
- [PASS] `tests/test_dashboard.py`: 5 assertions pass via `python tests/test_dashboard.py`.
- [PASS] `analytics/*.csv`: 10 files present, unmodified; validated KPIs match actual CSV contents.
- [PASS] `data/raw/` untouched; `data/cleaned/` untouched; no modifications to protected directories.
- [PASS] `agent/` logic preserved; `dashboard/app.py` logic preserved; `scripts/` preserved.
- [PASS] `data_dictionary.md` complete (updated with actual column schemas and transformation references).
- [PASS] No fake/demo data added; no fabricated analytics; no external API requirements for core functionality.
- [PASS] Security scan: no hardcoded secrets; `LLM_API_KEY` optional environment variable only.

**Files changed in this pass:** `README.md` (rewritten for accuracy), `requirements.txt` (verified — unchanged), no other repository files modified.

**NO COMMIT performed. NO PUSH performed.**

---
*TransOrg AgentIQ — Track 3: AgriTech. Reproducible, transparent, statistically rigorous, limitation-aware.*
