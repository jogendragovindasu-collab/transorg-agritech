# Executive Dashboard Design
## TransOrg AgentIQ Datathon - Track 3: AgriTech

**Created:** 2026-09-12  
**Status:** Design Complete — Implementation Pending  
**Technology:** Streamlit + Plotly + Pandas  
**Entry Point:** `dashboard/app.py`

---

## 1. DASHBOARD OBJECTIVE

Build an **executive supply-chain intelligence dashboard** that transforms messy agricultural data into actionable business insights, demonstrating:

1. **Data Rescue Impact** — Quantifiable cleaning value
2. **Risk Detection** — Price/MSP vulnerability, logistics bottlenecks
3. **Analytical Rigor** — Transparent limitations, statistical methods
4. **Decision Support** — Action-oriented insights, not just charts

### Competitive Differentiation

**Most Teams:**
- Clean data + basic KPIs + pretty charts + chatbot

**Our Dashboard:**
- Shows measurable cleaning impact (before/after transformations)
- Business-oriented KPI hierarchy (Price Vulnerability Matrix, Supply Concentration)
- Explicit limitation disclosure (weather-to-mandi unsupported)
- Statistical rigor (p90 long-transit, correlation p-values)
- Actionable insights with supporting evidence

---

## 2. TARGET USERS

- **Agricultural Policymakers** — MSP effectiveness, price crash trends
- **Mandi Administrators** — Performance benchmarking, logistics hotspots
- **Supply Chain Managers** — Transit bottlenecks, warehouse efficiency
- **Data Scientists / Judges** — Data quality transparency, methodology validation

---

## 3. KEY BUSINESS QUESTIONS

| Question | Dashboard Answer |
|---|---|
| Are farmers getting MSP? | 40.34% price crash rate; Wheat/Cotton/Sugarcane vulnerable |
| Which mandis need intervention? | 3 high-volume mandis with 35-44% crash rates |
| Where are logistics bottlenecks? | Warehouse-level transit analysis (p90 method) |
| How does weather affect supply? | Date-level correlation: rainfall -0.048 (p=0.58, non-significant) |
| How much data was rescued? | 5,143 valid quantities from 25,750 arrivals (20,607 unresolvable units) |

---

## 4. PAGE STRUCTURE

### Page 1: Executive Overview
- Top 6 KPI cards
- Executive insights (from `executive_insights.csv`)
- Business story summary
- Quick filters (date range, crop)

### Page 2: Supply & Mandi Intelligence
- Daily arrival trends
- Supply concentration (top mandis, crop distribution)
- Mandi performance explorer (table + filters)
- Mandi ranking (volume, price performance, crash rate)

### Page 3: Price & MSP Risk
- Price crash rate (40.34%)
- Modal Price vs MSP comparison
- Price Vulnerability Matrix (volume × crash rate scatter)
- Crop-level risk table
- Mandi-level risk table

### Page 4: Logistics Intelligence
- Transit KPIs (avg, median, p90 threshold)
- Warehouse performance table
- Long-transit rate by warehouse
- Distance vs transit relationship
- Methodology note (p90 definition)

### Page 5: Weather & Arrivals
- Date-level weather trends (rainfall, temperature, humidity)
- Synchronized weather-arrival visualization
- Correlation statistics with p-values
- **Limitation notice:** Weather-to-mandi unsupported

### Page 6: Data Rescue Impact
- Before/after row counts
- Transformation examples (units, currency, IDs)
- Duplicate removal summary
- Negative value detection
- Unresolved data transparency
- Validation checksum verification

---

## 5. KPI HIERARCHY

### Tier 1: Critical Business Metrics (Hero Cards)
1. **Total Arrivals** — 1,300,773 quintals
2. **Price Crash Rate** — 40.34% (HIGH SEVERITY)
3. **Average Modal Price** — Rs. 3,793
4. **Average MSP** — Rs. 3,711
5. **Active Mandis** — 57
6. **Average Transit** — 12.94 hours

### Tier 2: Strategic Insights
- Supply concentration: Top 5 mandis = 10.3%
- Crop concentration: Top 3 crops = 46.8%
- Vulnerable crops: Wheat (41.6%), Cotton (40.1%), Sugarcane (39.0%)
- Vulnerable mandis: 3 high-volume mandis with 35-44% crash rates

### Tier 3: Operational Metrics
- Median transit: 13.0 hours
- P90 long-transit threshold: 21.7 hours
- Avg distance: 628 km
- Valid data rates by dataset

---

## 6. CHART SPECIFICATIONS

### 6.1 Daily Arrivals Trend
- **Type:** Line chart (Plotly)
- **X-axis:** Date
- **Y-axis:** Daily arrivals (quintals)
- **Layers:** Optional 7-day moving average
- **Filters:** Crop, date range
- **Interaction:** Hover shows exact date + value
- **Insight annotations:** Mark unusual high/low periods if detected

### 6.2 Supply Concentration (Mandis)
- **Type:** Horizontal bar chart
- **Data:** Top 10 mandis by arrival volume
- **Color:** Semantic (top 5 highlighted)
- **Tooltip:** Mandi name, district, volume, % of total
- **Accompanying stat:** "Top 5 = X% of total"

### 6.3 Crop Distribution
- **Type:** Pie or donut chart
- **Data:** 6 canonical crops
- **Tooltip:** Crop, volume, percentage
- **Note:** "Unresolved crops excluded" (separate stat)

### 6.4 Modal Price vs MSP Comparison
- **Type:** Grouped bar chart (by crop)
- **Bars:** Modal price (blue), MSP (orange)
- **Reference line:** Parity line
- **Tooltip:** Crop, modal, MSP, gap, gap %
- **Highlight:** Crops below MSP

### 6.5 Price Vulnerability Matrix
- **Type:** Scatter plot (Plotly)
- **X-axis:** Total arrivals (quintals)
- **Y-axis:** Price crash rate (%)
- **Points:** Crops or Mandis (selectable)
- **Size:** Number of price records
- **Color:** Severity (red for high crash + high volume)
- **Quadrants:** Annotate HIGH VOLUME + HIGH CRASH
- **Tooltip:** Entity name, arrivals, crash rate, crash count

### 6.6 Warehouse Transit Performance
- **Type:** Table with conditional formatting
- **Columns:** Warehouse, trip count, avg transit, median transit, p75, p90, long-transit rate
- **Sort:** By median transit (descending)
- **Highlight:** Rows > overall median × 1.5

### 6.7 Weather-Arrival Correlation
- **Type:** Dual-axis line chart
- **Primary Y-axis:** Total arrivals
- **Secondary Y-axis:** Total rainfall
- **X-axis:** Date
- **Layers:** Temperature as optional overlay
- **Stats box:** Correlation coefficients + p-values
- **Note:** "Date-level analysis only"

### 6.8 Data Rescue Before/After
- **Type:** Side-by-side comparison cards
- **Sections:** Arrivals, Price, Transport, Weather
- **Metrics:** Raw count, valid count, excluded count, exclusion %
- **Visual:** Progress bar or comparison bar

---

## 7. FILTERS & INTERACTIONS

### Global Filters (Sidebar)
- **Date Range:** Slider (min/max from data)
- **Crop:** Multi-select dropdown (canonical crops only)
- **State:** Dropdown (with "All")
- **District:** Dropdown (filtered by state)
- **Mandi:** Searchable dropdown
- **Reset Button:** Clear all filters

### Page-Specific Filters
- Page 2: Crop + Mandi
- Page 3: Crop + Date
- Page 4: Warehouse
- Page 5: Date range (synchronized weather + arrivals)

### Interactions
- **Hover tooltips:** Rich contextual data
- **Click-to-filter:** Click crop in pie → filter other charts
- **Expandable sections:** Methodology, limitations
- **Downloadable data:** Export filtered table as CSV

---

## 8. BUSINESS INSIGHTS (from `executive_insights.csv`)

Display top 5-7 insights in dedicated cards on Overview page:

**Format:**
```
[CATEGORY] Title
Metric: X
Implication: Y
Supporting Data: Z
```

**Example:**
```
[PRICE] Wheat shows elevated price vulnerability
Crash Rate: 41.6%
Implication: High-volume crop with frequent below-MSP trading
Supporting: 225,921 qtl arrivals, 440 crash instances
```

**Severity Coding:**
- High → Red badge
- Medium → Yellow badge
- Low → Blue badge
- Informational → Gray badge

---

## 9. ACTION-ORIENTED RECOMMENDATIONS

Provide recommendations **derived from analytics**, not invented:

| Finding | Recommendation |
|---|---|
| 40.34% overall crash rate | Monitor MSP compliance; investigate modal price determinants |
| 3 vulnerable mandis | Focus intervention resources on high-volume crash-prone mandis |
| Wheat/Cotton/Sugarcane risk | Prioritize price monitoring for these crops |
| Warehouse transit variability | Investigate logistics practices at high-transit warehouses |
| 80% unresolvable quantity units | Improve data collection protocols for arrival records |

---

## 10. DATA SOURCES

### Primary Sources (Analytics Outputs)
1. `analytics/mandi_kpis.csv` — Mandi-level performance
2. `analytics/crop_kpis.csv` — Crop-level metrics
3. `analytics/daily_kpis.csv` — Time-series data
4. `analytics/price_msp_analysis.csv` — Price records
5. `analytics/transport_kpis.csv` — Overall transport
6. `analytics/warehouse_kpis.csv` — Warehouse performance
7. `analytics/weather_daily.csv` — Daily weather
8. `analytics/weather_arrival_analysis.csv` — Weather-arrival correlation
9. `analytics/executive_insights.csv` — Business insights
10. `analytics/data_quality_summary.csv` — Cleaning audit

### Secondary Sources (For Validation/Context)
- `docs/audit/cleaning_audit_summary.json` — Step 5 audit
- `reports/ANALYTICS_VALIDATION_REPORT.txt` — Validation stats

### NOT Used
- `data/raw/*` — Never accessed by dashboard
- `data/cleaned/*` — Not accessed (use analytics layer)

---

## 11. EMPTY / ERROR STATES

### No Data After Filters
```
📊 No data matches the selected filters.
Try adjusting your filter criteria or resetting filters.
```

### Missing Analytics File
```
⚠️ Required analytics file not found: {filename}
Please run: python scripts/run_analytics.py
```

### Insufficient Data for Chart
```
ℹ️ Insufficient data to display this visualization.
Minimum {N} records required.
```

---

## 12. RESPONSIVE BEHAVIOR

- **Desktop (>1200px):** 3-column KPI grid, side-by-side charts
- **Tablet (768-1200px):** 2-column KPI grid, stacked charts
- **Mobile (<768px):** Single column (Streamlit default)

### Chart Adaptations
- Large scatter plots → tables on mobile
- Multi-axis charts → simplified single-axis
- Wide tables → horizontal scroll

---

## 13. VISUAL DESIGN SYSTEM

### Colors (Semantic)
- **Primary:** `#1f77b4` (blue) — Neutral data
- **Success:** `#2ca02c` (green) — Positive indicators
- **Warning:** `#ff7f0e` (orange) — Moderate risk
- **Danger:** `#d62728` (red) — High risk, price crash
- **Neutral:** `#7f7f7f` (gray) — Secondary info

### Typography
- **Headers:** 24-32px, bold
- **KPI Numbers:** 36-48px, bold
- **KPI Labels:** 14px, normal
- **Body:** 14-16px, normal
- **Footnotes:** 12px, italic

### Spacing
- Section padding: 2rem
- Card padding: 1.5rem
- Chart margins: Auto (Plotly default)

### Components
- **KPI Cards:** White background, subtle shadow, rounded corners
- **Insight Cards:** Colored left border (severity), white bg
- **Tables:** Striped rows, sortable headers, conditional formatting
- **Charts:** Clean grid, minimal decoration, readable axes

---

## 14. METHODOLOGY SECTION (Expandable)

Include on Overview page, collapsible by default:

**Title:** "Data & Methodology"

**Content:**
- **Data Flow:** Raw → Cleaned → Analytics → Dashboard
- **Cleaning:** 5 datasets, 342 mandi IDs normalized, 36 crop variants mapped
- **Analytics:** 10 KPI tables, 10 executive insights
- **Limitations:**
  - Weather-to-mandi: Unsupported (date-level only)
  - Unresolved crops: 13 variants, 1,158 records excluded
  - Quantity units: 20,607 unresolvable records excluded
  - Transport delay: Statistical p90 method (no business threshold)
- **Reproducibility:** `python scripts/run_analytics.py`

---

## 15. TECHNICAL SPECIFICATIONS

### Technology Stack
- **Framework:** Streamlit 1.28+
- **Plotting:** Plotly Express + Plotly Graph Objects
- **Data:** Pandas 2.0+
- **Utilities:** NumPy, SciPy (already installed)

### Performance
- **Caching:** Use `@st.cache_data` for analytics loading
- **Lazy Loading:** Load page-specific data on page switch
- **No Re-computation:** Never recalculate KPIs (use analytics outputs)

### File Structure
```
dashboard/
├── app.py (main entry point, navigation)
├── pages/
│   ├── 1_Executive_Overview.py
│   ├── 2_Supply_Mandi.py
│   ├── 3_Price_Risk.py
│   ├── 4_Logistics.py
│   ├── 5_Weather_Arrivals.py
│   └── 6_Data_Rescue.py
├── components/
│   ├── kpi_cards.py
│   ├── insight_cards.py
│   ├── charts.py
│   └── tables.py
└── utils/
    ├── data_loader.py
    ├── filters.py
    └── formatters.py
```

### Entry Command
```bash
streamlit run dashboard/app.py
```

### Port
Default: `8501` (Streamlit default)

---

## 16. VALIDATION CHECKLIST

Before completion, verify:

- [ ] Dashboard reads analytics outputs (not raw/cleaned data)
- [ ] All KPI values match analytics validation report
- [ ] No KPI logic duplicated/reimplemented incorrectly
- [ ] Filters work on expected columns
- [ ] No unsupported weather-to-mandi claims
- [ ] No fake real-time claims
- [ ] Limitations explicitly stated
- [ ] Data rescue impact visible
- [ ] Executive insights supported by data
- [ ] No fabricated recommendations
- [ ] Error states handled gracefully
- [ ] Tests pass (`tests/test_dashboard_data.py`)
- [ ] `data/raw/` untouched
- [ ] Step 5/6 outputs unchanged

---

## 17. TESTING REQUIREMENTS

Create: `tests/test_dashboard_data.py`

**Test Cases:**
1. All analytics files load without error
2. Required columns exist in each file
3. KPI values are numeric and non-negative where expected
4. Filter columns exist
5. Dashboard data matches analytics validation report
6. No modification of analytics files by dashboard
7. Executive insights CSV loads correctly
8. Data quality summary loads correctly

---

## 18. DASHBOARD VALIDATION REPORT

Create: `reports/DASHBOARD_VALIDATION_REPORT.txt`

**Contents:**
- Dashboard pages implemented
- KPIs displayed with sources
- Charts created
- Filters implemented
- Insights displayed
- Data rescue visualization implemented
- Files consumed
- Test results
- Known limitations
- Reproducibility command

---

## 19. COMPETITIVE EDGE SUMMARY

**What Makes This Dashboard Different:**

1. **Data Rescue Transparency** — Shows before/after cleaning impact quantitatively
2. **Business-First KPIs** — Price Vulnerability Matrix, Supply Concentration
3. **Statistical Rigor** — P90 long-transit, correlation p-values, explicit limitations
4. **Action-Oriented Insights** — Not just "price fell" but "Wheat vulnerable: 41.6% crash rate, 225k qtl"
5. **Analytical Honesty** — Weather-to-mandi unsupported (explicitly stated)
6. **Judge-Friendly Architecture** — Clean separation: raw → cleaned → analytics → dashboard

**Differentiation from "Basic KPI Dashboard":**
- Most teams: Show price chart
- Our dashboard: Show Price Vulnerability Matrix with volume × crash rate quadrants

**Differentiation from "Pretty Charts Dashboard":**
- Most teams: Hide messy data work
- Our dashboard: Dedicated "Data Rescue Impact" page showing transformations

---

## 20. NEXT STEPS (POST-DASHBOARD)

After dashboard validation:
1. Review dashboard validation report
2. Verify all charts render correctly
3. Test filters and interactions
4. Confirm data source integrity
5. Update main README
6. **STOP** — Do not build AI agent until explicitly instructed

---

**END OF DASHBOARD DESIGN DOCUMENT**
