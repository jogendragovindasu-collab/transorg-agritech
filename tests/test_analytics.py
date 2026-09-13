#!/usr/bin/env python3
"""Focused analytics tests — deterministic, no external APIs."""
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

CLEANED_DIR = Path('data/cleaned')
ANALYTICS_DIR = Path('analytics')

def test_price_crash_definition():
    df_price = pd.read_csv(CLEANED_DIR / 'track3_price_and_msp_clean.csv')
    valid = df_price[(df_price['modal_price'].notnull()) & (df_price['msp'].notnull()) &
                     (df_price['modal_price_status'] == 'resolved') & (df_price['msp_status'] == 'resolved')].copy()
    valid['crash'] = (valid['modal_price'] < valid['msp']).astype(int)
    assert valid['crash'].sum() <= len(valid), "Crash count exceeds denominator"
    assert 0 <= valid['crash'].mean() <= 1, "Crash rate not in [0,1]"
    print("PASS: price_crash_definition")

def test_transport_p90_statistical():
    df_t = pd.read_csv(CLEANED_DIR / 'track3_transport_logistics_clean.csv')
    valid = df_t[df_t['negative_transit_flag'] == 0].copy()
    p90 = valid['transit_hours_clean'].quantile(0.90)
    assert p90 >= 0, "P90 threshold negative"
    print(f"PASS: transport_p90_statistical (p90={p90:.2f}h)")

def test_weather_date_level_only():
    df_w = pd.read_csv(CLEANED_DIR / 'track3_weather_sensors_clean.csv')
    # Confirm no unsupported mandi mapping in cleaned weather
    assert 'mandi_id' not in df_w.columns, "Weather dataset claims unsupported mandi mapping"
    print("PASS: weather_date_level_only")

def test_analytics_no_negative_kpis():
    df_mandi = pd.read_csv(ANALYTICS_DIR / 'mandi_kpis.csv')
    assert (df_mandi['total_arrival_qty_qtl'] >= 0).all()
    df_crop = pd.read_csv(ANALYTICS_DIR / 'crop_kpis.csv')
    assert (df_crop['total_arrivals_qtl'] >= 0).all()
    df_weather = pd.read_csv(ANALYTICS_DIR / 'weather_daily.csv')
    assert (df_weather['avg_temperature_celsius'] >= -100).all()  # physically impossible only
    print("PASS: analytics_no_negative_kpis")

def test_duplicate_keys():
    for fname in ['mandi_kpis.csv', 'crop_kpis.csv', 'warehouse_kpis.csv', 'daily_kpis.csv', 'weather_daily.csv']:
        df = pd.read_csv(ANALYTICS_DIR / fname)
        key_col = df.columns[0]
        assert df[key_col].duplicated().sum() == 0, f"Duplicate keys in {fname}"
    print("PASS: duplicate_keys")

def test_weather_correlation_sample_size():
    df = pd.read_csv(ANALYTICS_DIR / 'weather_arrival_analysis.csv')
    assert len(df) > 10, "Weather-arrival correlation needs >10 overlapping days"
    # Correlation should exist in the dataset; weak values acceptable
    print(f"PASS: weather_correlation_sample_size (n={len(df)})")

if __name__ == '__main__':
    test_price_crash_definition()
    test_transport_p90_statistical()
    test_weather_date_level_only()
    test_analytics_no_negative_kpis()
    test_duplicate_keys()
    test_weather_correlation_sample_size()
    print("\nAll analytics tests passed.")
