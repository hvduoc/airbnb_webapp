import requests

print("Testing CSV preview API endpoint...")

# Prepare test data
csv_content = """Nhà/phòng cho thuê,Check-in,Check-out,Số đêm,Khách,Tình trạng,Thu nhập tổng,Phí dọn dẹp
"Avalon 5.3 - OceanSight - New interior, central",2024-01-01,2024-01-03,2,2,Confirmed,2000000,200000
"Avalon 2.4- OceanSight - New interior, central",2024-01-05,2024-01-07,2,2,Confirmed,1800000,200000"""

room_mapping = {
    "mappings": {"Avalon 5.3 - OceanSight - New interior, central": "AVA-503"}
}

# Test data for API
test_data = {"csv_content": csv_content, "room_mapping": room_mapping}

try:
    response = requests.post(
        "http://127.0.0.1:8004/api/csv/preview-json", json=test_data, timeout=10
    )

    print(f"Response status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("✅ API works!")
        print(f"Preview rows: {len(result.get('preview', []))}")
        for row in result.get("preview", [])[:3]:  # Show first 3
            print(
                f"  {row['original']} -> {row['mapped_name']} (changed: {row['mapped']})"
            )
    else:
        print(f"❌ API failed: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback

    traceback.print_exc()
