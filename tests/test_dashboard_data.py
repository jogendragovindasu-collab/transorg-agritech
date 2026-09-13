#!/usr/bin/env python3
"""
Test that dashboard loads analytics data correctly.
Tests data source integrity without modifying analytics outputs.
"""

import pandas as pd
from pathlib import Path

def test_analytics_files_load():
    analytics_dir = Path('analytics')
    required_files = [
        'mandi_kpis.csv', 'crop_kpis.csv', 'daily_kpis.csv',
        'price_msp_analysis.csv', 'transport_kpis.csv',
        'warehouse_kpis.csv', 'executive_insights.csv',
        'weather_daily.csv', 'weather_arrival_analysis.csv',
        'data_quality_summary.csv'
    ]
    for f in required_files:
        assert (analytics_dir / f).exists(), f"Missing: analytics/{f}"
        # Check can load
        df = pd.read_csv(analytics_dir / f)
        print(f"  [PASS] {f}: {len(df)} rows loaded")

if __name__ == '__main__':
    print("Testing dashboard data sources...")
    test_analytics_files_load()
    print("\nAll analytics files load correctly.")
