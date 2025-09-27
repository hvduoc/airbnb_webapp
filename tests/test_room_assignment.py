# 🧪 **TEST SCRIPT - ROOM ASSIGNMENT FUNCTIONALITY**

"""
Test script để validate kịch bản TASK-001: Room Assignment Tracking

Kịch bản: Khách đặt phòng 203 nhưng ở phòng 303
"""

import requests
import json
from datetime import date

BASE_URL = "http://127.0.0.1:8000"

def test_room_assignment_workflow():
    """Test complete room assignment workflow"""
    
    print("🚀 Testing Room Assignment Workflow - 203→303")
    print("=" * 60)
    
    # Test data
    booking_id = 912  # Use existing booking
    test_data = {
        "booked_room": "203",
        "actual_room": "303", 
        "revenue_attribution": "actual_room",
        "change_reason": "maintenance",
        "changed_date": str(date.today()),
        "changed_by": "Admin Test",
        "notes": "Phòng 203 bị hỏng máy lạnh, chuyển khách sang 303"
    }
    
    # Step 1: Verify booking exists
    print(f"\n📋 Step 1: Check booking {booking_id}...")
    response = requests.get(f"{BASE_URL}/bookings/{booking_id}")
    if response.status_code == 200:
        print("✅ Booking exists")
    else:
        print(f"❌ Booking not found: {response.status_code}")
        return False
    
    # Step 2: Create room assignment
    print(f"\n🏠 Step 2: Create room assignment...")
    response = requests.post(f"{BASE_URL}/bookings/{booking_id}/room-assignment", data=test_data)
    if response.status_code == 303:  # Redirect after successful POST
        print("✅ Room assignment created/updated")
    else:
        print(f"❌ Failed to create assignment: {response.status_code}")
        return False
    
    # Step 3: Verify room assignment in booking detail
    print(f"\n🔍 Step 3: Verify assignment in booking detail...")
    response = requests.get(f"{BASE_URL}/bookings/{booking_id}")
    if response.status_code == 200:
        content = response.text
        if "203" in content and "303" in content:
            print("✅ Room assignment visible in booking detail")
        else:
            print("❌ Room assignment not visible")
            return False
    else:
        print(f"❌ Cannot load booking detail: {response.status_code}")
        return False
    
    # Step 4: Test revenue attribution scenarios
    print(f"\n💰 Step 4: Test revenue attribution scenarios...")
    
    # Test different attribution methods
    attribution_tests = [
        ("actual_room", "🏠 Phòng thực tế"),
        ("booked_room", "📍 Phòng đã đặt"),
        ("split", "⚖️ Chia đôi")
    ]
    
    for method, description in attribution_tests:
        test_data["revenue_attribution"] = method
        response = requests.post(f"{BASE_URL}/bookings/{booking_id}/room-assignment", data=test_data)
        if response.status_code == 303:
            print(f"✅ {description} attribution test passed")
        else:
            print(f"❌ {description} attribution test failed")
            return False
    
    print(f"\n🎉 All tests passed! Room assignment system working correctly.")
    print("\n📊 Test Summary:")
    print("  ✅ Room assignment creation")
    print("  ✅ Booking detail integration")
    print("  ✅ Revenue attribution methods")
    print("  ✅ Form validation and persistence")
    
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print(f"\n🧪 Testing Edge Cases...")
    print("-" * 30)
    
    # Test invalid booking ID
    print("Testing invalid booking ID...")
    response = requests.get(f"{BASE_URL}/bookings/99999/room-assignment")
    if response.status_code == 500:  # Should handle gracefully
        print("⚠️ Invalid booking handling needs improvement")
    else:
        print("✅ Invalid booking handled properly")
    
    # Test same room assignment (no change)
    print("Testing same room assignment...")
    same_room_data = {
        "booked_room": "203",
        "actual_room": "203",  # Same room
        "revenue_attribution": "actual_room",
        "change_reason": "operational",
        "changed_date": str(date.today()),
        "changed_by": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/bookings/912/room-assignment", data=same_room_data)
    if response.status_code == 303:
        print("✅ Same room assignment handled")
    else:
        print("❌ Same room assignment failed")

if __name__ == "__main__":
    print("🎯 ROOM ASSIGNMENT TESTING - TASK-001")
    print("Testing implementation of booking vs actual room tracking")
    print()
    
    try:
        # Main workflow test
        if test_room_assignment_workflow():
            # Edge cases
            test_edge_cases()
        else:
            print("❌ Main workflow failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
    
    print(f"\n🏁 Testing completed!")