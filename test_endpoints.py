"""
Endpoint Testing Script for Railway AI
Tests all optimization endpoints after comprehensive hybrid integration
"""

import requests
import json
import time
import sys

def test_endpoint(base_url, endpoint, method="GET", params=None, data=None):
    """Test a single endpoint"""
    url = f"{base_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text}")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {e}")
        return False

def main():
    print("🚀 Railway AI - Endpoint Testing")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Test server health
    print("\n📡 Testing Server Health...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure the server is running with: uvicorn backend.app.main:app --reload")
        return
    
    # Test optimization endpoints
    print("\n🔧 Testing Optimization Endpoints...")
    
    optimization_methods = [
        "comprehensive_hybrid",
        "milp", 
        "rl"
    ]
    
    for method in optimization_methods:
        print(f"\n--- Testing {method.upper()} Optimizer ---")
        success = test_endpoint(base_url, "/optimize/", params={"method": method})
        
        if success:
            print(f"✅ {method} endpoint working")
        else:
            print(f"❌ {method} endpoint failed")
    
    # Test other endpoints
    print("\n📊 Testing Other Endpoints...")
    
    other_endpoints = [
        ("/stations/", "GET"),
        ("/sections/", "GET"), 
        ("/trains/", "GET"),
        ("/train_sections/", "GET"),
        ("/live-trains/", "GET"),
        ("/conflict-alerts/", "GET")
    ]
    
    for endpoint, method in other_endpoints:
        success = test_endpoint(base_url, endpoint, method)
        if success:
            print(f"✅ {endpoint} working")
        else:
            print(f"❌ {endpoint} failed")
    
    print("\n🎯 Testing Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
