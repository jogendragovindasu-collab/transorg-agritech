"""
TransOrg AgentIQ Datathon - Track 3: AgriTech
Data Loading Utilities for Dashboard

Loads analytics outputs with caching
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import json

ANALYTICS_DIR = Path('analytics')
AUDIT_DIR = Path('docs/audit')

@st.cache_data
def load_mandi_kpis():
    """Load mandi-level KPIs"""
    try:
        return pd.read_csv(ANALYTICS_DIR / 'mandi_kpis.csv')
    except FileNotFoundError:
        st.error("❌ mandi_kpis.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_crop_kpis():
    """Load crop-level KPIs"""
    try:
        return pd.read_csv(ANALYTICS_DIR / 'crop_kpis.csv')
    except FileNotFoundError:
        st.error("❌ crop_kpis.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_daily_kpis():
    """Load daily time-series KPIs"""
    try:
        df = pd.read_csv(ANALYTICS_DIR / 'daily_kpis.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("❌ daily_kpis.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_price_analysis():
    """Load price-MSP analysis records"""
    try:
        df = pd.read_csv(ANALYTICS_DIR / 'price_msp_analysis.csv')
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("❌ price_msp_analysis.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_transport_kpis():
    """Load transport KPIs"""
    try:
        return pd.read_csv(ANALYTICS_DIR / 'transport_kpis.csv')
    except FileNotFoundError:
        st.error("❌ transport_kpis.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_warehouse_kpis():
    """Load warehouse KPIs"""
    try:
        return pd.read_csv(ANALYTICS_DIR / 'warehouse_kpis.csv')
    except FileNotFoundError:
        st.error("❌ warehouse_kpis.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_weather_daily():
    """Load daily weather data"""
    try:
        df = pd.read_csv(ANALYTICS_DIR / 'weather_daily.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("❌ weather_daily.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_weather_arrival_analysis():
    """Load weather-arrival correlation analysis"""
    try:
        df = pd.read_csv(ANALYTICS_DIR / 'weather_arrival_analysis.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("❌ weather_arrival_analysis.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_executive_insights():
    """Load executive insights"""
    try:
        return pd.read_csv(ANALYTICS_DIR / 'executive_insights.csv')
    except FileNotFoundError:
        st.error("❌ executive_insights.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_data_quality_summary():
    """Load data quality summary"""
    try:
        return pd.read_csv(ANALYTICS_DIR / 'data_quality_summary.csv')
    except FileNotFoundError:
        st.error("❌ data_quality_summary.csv not found. Run: python scripts/run_analytics.py")
        return None

@st.cache_data
def load_cleaning_audit():
    """Load cleaning audit summary"""
    try:
        with open(AUDIT_DIR / 'cleaning_audit_summary.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning("⚠️ cleaning_audit_summary.json not found")
        return None

def get_overall_kpis():
    """Calculate overall KPIs from validated analytics outputs.
    Uses analytics/*.csv directly with deterministic aggregation.
    Source mapping for each KPI:
      - total_arrivals_qtl: analytics/crop_kpis.csv -> total_arrivals_qtl.sum()
      - price_crash_rate: analytics/price_msp_analysis.csv -> price_below_msp_flag.mean()
      - avg_modal_price: analytics/price_msp_analysis.csv -> modal_price.mean()
      - avg_msp: analytics/price_msp_analysis.csv -> msp.mean()
      - active_mandis: analytics/mandi_kpis.csv -> count(arrival_record_count > 0)
      - avg_transit_hours: analytics/transport_kpis.csv -> avg_transit_hours (row 1)
      - median_transit_hours: analytics/transport_kpis.csv -> median_transit_hours (row 1)
    """
    crop_kpis = load_crop_kpis()
    price_analysis = load_price_analysis()
    transport_kpis = load_transport_kpis()
    mandi_kpis = load_mandi_kpis()

    if price_analysis is None or transport_kpis is None or mandi_kpis is None:
        return None

    # Price KPIs from price_msp_analysis.csv (validated Step 6 analytics output, 6472 records)
    price_crash_rate = price_analysis['price_below_msp_flag'].mean() * 100 if 'price_below_msp_flag' in price_analysis.columns else 0.0
    avg_modal_price = price_analysis['modal_price'].mean()
    avg_msp = price_analysis['msp'].mean()

    # Supply from crop_kpis.csv
    total_arrivals = crop_kpis['total_arrivals_qtl'].sum() if crop_kpis is not None else 0.0
    active_mandis = len(mandi_kpis[mandi_kpis['arrival_record_count'] > 0]) if mandi_kpis is not None else 0

    # Transport from transport_kpis.csv (statistical p90 = 21.7h)
    avg_transit_hours = transport_kpis.iloc[0]['avg_transit_hours'] if len(transport_kpis) > 0 else 0.0
    median_transit_hours = transport_kpis.iloc[0]['median_transit_hours'] if len(transport_kpis) > 0 else 0.0

    return {
        'total_arrivals_qtl': float(total_arrivals),
        'price_crash_rate': float(price_crash_rate),
        'avg_modal_price': float(avg_modal_price),
        'avg_msp': float(avg_msp),
        'active_mandis': int(active_mandis),
        'avg_transit_hours': float(avg_transit_hours),
        'median_transit_hours': float(median_transit_hours),
    }
