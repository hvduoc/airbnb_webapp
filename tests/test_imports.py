import sys
sys.path.append('.')

print("Testing imports...")

try:
    from services.upload_service import UploadService
    print("✅ UploadService import OK")
except Exception as e:
    print(f"❌ UploadService import failed: {e}")

try:
    from utils import update_room_mapping
    print("✅ update_room_mapping import OK")
except Exception as e:
    print(f"❌ update_room_mapping import failed: {e}")

try:
    from models import Booking, Property, Building, Channel
    print("✅ Models import OK")
except Exception as e:
    print(f"❌ Models import failed: {e}")

try:
    import pandas as pd
    print("✅ Pandas import OK")
except Exception as e:
    print(f"❌ Pandas import failed: {e}")

print("Testing basic functionality...")

try:
    # Test room mapping function
    from utils import update_room_mapping
    test_mapping = {'mappings': {'test': 'mapped'}}
    update_room_mapping(test_mapping)
    print("✅ Room mapping function works")
except Exception as e:
    print(f"❌ Room mapping failed: {e}")
    import traceback
    traceback.print_exc()

print("All tests done.")