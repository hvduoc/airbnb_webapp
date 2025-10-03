import sys

sys.path.append('.')

print("Testing UploadService offline...")

try:
    # Test database connection first
    from db import get_session_context
    print("✅ Database imports OK")
    
    # Test with session
    with get_session_context() as session:
        print("✅ Database session OK")
        
        # Test service initialization
        from services.upload_service import UploadService
        service = UploadService(session)
        print("✅ UploadService initialization OK")
        
        # Test room mapping data format
        room_mapping_data = {
            'mappings': {
                'Avalon 5.3 - OceanSight - New interior, central': 'AVA-503'
            }
        }
        
        # Try update_room_mapping function
        from utils import update_room_mapping
        update_room_mapping(room_mapping_data)
        print("✅ Room mapping update OK")
        
    print("All offline tests passed!")
    
except Exception as e:
    print(f"❌ Error in offline test: {e}")
    import traceback
    traceback.print_exc()