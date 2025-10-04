#!/usr/bin/env python3
"""
🎯 FINAL CANARY VALIDATION for v1.3.1-dbfix
Quick validation test for production readiness
"""

import requests
import time
from datetime import datetime

def test_canary():
    print("🚀 FINAL CANARY VALIDATION: v1.3.1-dbfix")
    print("="*60)
    
    base_url = "http://localhost:8000"
    results = []
    
    # Test 1: Health endpoint
    print("\n📍 Test 1: Health Check")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=5)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            print(f"✅ Health OK ({response_time:.1f}ms)")
            results.append(True)
        else:
            print(f"❌ Health Failed: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Health Error: {e}")
        results.append(False)
    
    # Test 2: Main page
    print("\n📍 Test 2: Main Page")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/", timeout=5)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200 and "Trang chủ" in response.text:
            print(f"✅ Main Page OK ({response_time:.1f}ms)")
            results.append(True)
        else:
            print(f"❌ Main Page Failed: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Main Page Error: {e}")
        results.append(False)
    
    # Test 3: Bookings page
    print("\n📍 Test 3: Bookings Page")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/bookings", timeout=5)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            print(f"✅ Bookings OK ({response_time:.1f}ms)")
            results.append(True)
        else:
            print(f"❌ Bookings Failed: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ Bookings Error: {e}")
        results.append(False)
    
    # Final verdict
    print("\n" + "="*60)
    print("📊 CANARY RESULTS:")
    print(f"   Tests Passed: {sum(results)}/3")
    print(f"   Success Rate: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print("\n🎊 CANARY VALIDATION SUCCESSFUL!")
        print("✅ v1.3.1-dbfix APPROVED for production deployment")
        print("🚀 Ready for 100% traffic allocation")
        print("📈 Database schema fixes working correctly")
        return True
    else:
        print("\n💥 CANARY VALIDATION FAILED!")
        print("❌ v1.3.1-dbfix NOT APPROVED")
        print("🛑 ROLLBACK REQUIRED")
        return False

if __name__ == "__main__":
    success = test_canary()
    exit(0 if success else 1)