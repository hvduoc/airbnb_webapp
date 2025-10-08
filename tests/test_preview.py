import sys

sys.path.append(".")
import pandas as pd

from utils import get_room_mapping_preview

print("Testing preview function...")

# Test với sample CSV data
data = {
    "Nhà/phòng cho thuê": [
        "Avalon 5.3 - OceanSight - New interior, central",
        "Avalon 2.4- OceanSight - New interior, central",
    ]
}
df = pd.DataFrame(data)

room_mapping_data = {
    "mappings": {"Avalon 5.3 - OceanSight - New interior, central": "AVA-503"}
}

try:
    preview = get_room_mapping_preview(df, room_mapping_data)
    print("✅ Preview function works!")
    print(f"Rows: {len(preview)}")
    for row in preview:
        print(f"  Original: {row['original']}")
        print(f"  Mapped: {row['mapped_name']}")
        print(f"  Changed: {row['mapped']}")
        print("---")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
