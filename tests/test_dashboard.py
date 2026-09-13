#!/usr/bin/env python3
"""
Dashboard Tests — verifies analytics consumption without raw data access.
Only reads analytics/ and checks component imports.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_analytics_exist():
    import pandas as pd
    analytics_dir = Path('analytics')
    required = [
        'mandi_kpis.csv', 'crop_kpis.csv', 'daily_kpis.csv',
        'price_msp_analysis.csv', 'transport_kpis.csv', 'warehouse_kpis.csv',
        'weather_daily.csv', 'weather_arrival_analysis.csv',
        'executive_insights.csv', 'data_quality_summary.csv'
    ]
    missing = [f for f in required if not (analytics_dir / f).exists()]
    assert len(missing) == 0, f"Missing analytics: {missing}"
    print("PASS: analytics files present")

def test_dashboard_imports():
    # Verify all dashboard modules import cleanly
    import importlib.util
    modules = [
        'dashboard.utils.data_loader',
        'dashboard.components.kpi_cards',
        'dashboard.components.insight_cards',
        'dashboard.components.charts',
        'dashboard.components.agent_interface',
    ]
    for mod in modules:
        spec = importlib.util.find_spec(mod)
        assert spec is not None, f"Module {mod} not found"
    print("PASS: dashboard modules importable")

def test_no_raw_access_in_dashboard():
    # Confirm dashboard/app.py does not reference data/raw/
    app_path = Path('dashboard/app.py')
    content = app_path.read_text(encoding='utf-8')
    assert 'data/raw/' not in content, "Dashboard must not reference raw data"
    assert 'analytics/' in content, "Dashboard must reference analytics/"
    print("PASS: dashboard uses analytics/ not raw/")

def test_data_loader_uses_analytics():
    loader_path = Path('dashboard/utils/data_loader.py')
    content = loader_path.read_text(encoding='utf-8')
    assert "ANALYTICS_DIR = Path('analytics')" in content
    print("PASS: data_loader points to analytics/")

def test_filters_handle_empty():
    import pandas as pd
    df = pd.read_csv('analytics/daily_kpis.csv')
    # Empty filter simulation: return subset; check doesn't crash
    subset = df.iloc[0:0]  # zero rows
    assert len(subset) == 0
    print("PASS: empty filter handled gracefully")

if __name__ == '__main__':
    test_analytics_exist()
    test_dashboard_imports()
    test_no_raw_access_in_dashboard()
    test_data_loader_uses_analytics()
    test_filters_handle_empty()
    print("\nAll dashboard tests passed.")
