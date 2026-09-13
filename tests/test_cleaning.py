#!/usr/bin/env python3
"""
Tests for TransOrg AgriTech cleaning transformations.
Run with: python tests/test_cleaning.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import re
from run_cleaning import (
    extract_and_convert_quantity, extract_and_convert_distance,
    clean_price, convert_temperature_to_celsius, convert_rainfall_to_mm,
    normalize_mandi_id
)


def test_quantity_conversions():
    # Qtl unchanged
    assert extract_and_convert_quantity("415.88 qtl") == (415.88, 'qtl', 'resolved')
    # KG -> 0.01
    assert extract_and_convert_quantity("36,654.0 KG")[0] == 36654.0 * 0.01
    assert extract_and_convert_quantity("36,654.0 KG")[2] == 'resolved'
    # Tonne/MT -> 10.0
    val = extract_and_convert_quantity("100 T")
    assert val == (1000.0, 'T', 'resolved')
    # Tonne variant
    assert extract_and_convert_quantity("500 MT") == (5000.0, 'MT', 'resolved')
    # Negative -> NaN + negative flag
    val_neg = extract_and_convert_quantity("-50 KG")
    assert val_neg[0] != val_neg[0]  # NaN check
    assert val_neg[2] == 'negative'
    print("  [PASS] quantity conversions (qtl, kg, tonne, mt, negative)")


def test_distance_conversions():
    # KM unchanged
    val_km = extract_and_convert_distance("316.5 KM")
    assert val_km == (316.5, 'KM', 'resolved')
    # Miles -> km
    val_miles = extract_and_convert_distance("100 miles")
    assert abs(val_miles[0] - 160.934) < 0.001
    assert val_miles[1] == 'miles'
    # No unit
    val_no_unit = extract_and_convert_distance("250")
    assert val_no_unit[0] == 250.0
    print("  [PASS] distance conversions (km, miles, no_unit)")


def test_temperature_celsius():
    # Celsius embedded
    assert convert_temperature_to_celsius("30.5°C", None) == (30.5, 'embedded_celsius')
    # Fahrenheit to Celsius
    f_result = convert_temperature_to_celsius(77, "F")
    assert abs(f_result[0] - 25.0) < 0.1
    assert f_result[1] == 'fahrenheit'
    # Negative temp
    assert convert_temperature_to_celsius(-5, "C") == (-5.0, 'celsius')
    print("  [PASS] temperature conversions (celsius, fahrenheit, embedded)")


def test_rainfall_mm():
    # MM unchanged
    assert convert_rainfall_to_mm(25, "mm") == (25.0, 'mm')
    # Inches -> mm
    val_in = convert_rainfall_to_mm(2.5, "in")
    assert abs(val_in[0] - 63.5) < 0.01
    # Negative rainfall -> NaN + negative (returns 2-tuple: value, status)
    val_neg = convert_rainfall_to_mm(-10, "mm")
    assert val_neg[1] == 'negative'
    print("  [PASS] rainfall conversions (mm, inches, negative)")


def test_price_cleaning():
    assert clean_price("₹1200") == (1200.0, 'resolved')
    # Price with Rs. and decimals (string cleaning applies replacement chain)
    assert clean_price("Rs. 850.50")[0] == 850.5
    assert clean_price("1,250") == (1250.0, 'resolved')
    # Empty strings
    assert clean_price("")[1] == 'empty'
    print("  [PASS] price cleaning (currency symbols, commas)")


def test_mandi_id_normalization():
    # Canonical
    assert normalize_mandi_id("MANDI001")[0] == "MANDI001"
    # With hyphen
    assert normalize_mandi_id("MANDI-054")[0] == "MANDI054"
    # Underscore
    assert normalize_mandi_id("mandi_049")[0] == "MANDI049"
    # Numeric only
    assert normalize_mandi_id("056")[0] == "MANDI056"
    # Unresolvable
    assert normalize_mandi_id("UNKNOWN_ID")[1] == 'unknown'
    print("  [PASS] mandi ID normalization (canonical, hyphen, underscore, numeric)")


def test_negative_value_policy():
    # Negative quantity should NOT return zero
    val = extract_and_convert_quantity("-100 Qtl")
    assert val[0] != 0  # Must NOT be zero (should be NaN)
    assert val[2] == 'negative'
    # Negative rainfall should NOT return zero (2-tuple: value, status)
    val_rain = convert_rainfall_to_mm(-5, "mm")
    assert val_rain[1] == 'negative'
    assert val_rain[0] != 0
    print("  [PASS] negative value policy (not converted to zero)")


if __name__ == '__main__':
    print("Running cleaning transformation tests...")
    test_quantity_conversions()
    test_distance_conversions()
    test_temperature_celsius()
    test_rainfall_mm()
    test_price_cleaning()
    test_mandi_id_normalization()
    test_negative_value_policy()
    print("\nAll tests passed.")
