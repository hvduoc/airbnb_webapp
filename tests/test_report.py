#!/usr/bin/env python3
"""Test script để debug báo cáo"""

import traceback
from datetime import date

try:
    from main import compute_monthly_report

    print("🔍 Testing compute_monthly_report...")

    # Test với dữ liệu nhỏ
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    group_by = "property"

    print(f"Parameters: start={start_date}, end={end_date}, group_by={group_by}")

    result = compute_monthly_report(start_date, end_date, group_by)

    print(f"✅ Success! Result keys: {list(result.keys())}")
    print(f"📊 Total rows: {len(result.get('rows', []))}")
    print(f"💰 Totals: {result.get('total', {})}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n📋 Full traceback:")
    traceback.print_exc()
