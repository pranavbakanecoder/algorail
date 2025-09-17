"""
HTTP Endpoint Testing Script
Tests the FastAPI endpoints via HTTP requests
"""

import requests
import json
import time

def test_endpoint(base_url, endpoint, method="GET", params=None):
    """Test a single endpoint"""
    url = f"{base_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        
        print(f"✅ {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Success: {data.get('data', {}).get('success', 'Unknown')}")
                print(f"   Method: {data.get('data', {}).get('method', 'Unknown')}")
                print(f"   Trains: {data.get('data', {}).get('trains_count', 'Unknown')}")
                if 'total_delay' in data.get('data', {}):
                    print(f"   Total Delay: {data.get('data', {}).get('total_delay', 'Unknown')}")
                if 'computation_time' in data.get('data', {}):
                    print(f"   Computation Time: {data.get('data', {}).get('computation_time', 'Unknown')}")
            except Exception as e:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Error: {response.text[:200]}")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {endpoint}")
        print(f"   Error: {e}")
        return False

def main():
    print("🚀 Railway AI - HTTP Endpoint Testing")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
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
    
    results = {}
    
    for method in optimization_methods:
        print(f"\n--- Testing {method.upper()} ---")
        success = test_endpoint(base_url, "/optimize/", params={"method": method})
        results[method] = success
        
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
    
    other_results = {}
    
    for endpoint, method in other_endpoints:
        success = test_endpoint(base_url, endpoint, method)
        other_results[endpoint] = success
        if success:
            print(f"✅ {endpoint} working")
        else:
            print(f"❌ {endpoint} failed")
    
    print("\n🎯 Testing Complete!")
    print("=" * 50)
    
    print("\n📊 Optimization Results:")
    for method, success in results.items():
        print(f"   {method}: {'✅ PASS' if success else '❌ FAIL'}")
    
    print("\n📊 Other Endpoints:")
    for endpoint, success in other_results.items():
        print(f"   {endpoint}: {'✅ PASS' if success else '❌ FAIL'}")
    
    all_optimization_passed = all(results.values())
    all_other_passed = all(other_results.values())
    
    if all_optimization_passed:
        print("\n🏆 All optimization endpoints working correctly!")
    else:
        print("\n⚠️  Some optimization endpoints failed.")
    
    if all_other_passed:
        print("🏆 All other endpoints working correctly!")
    else:
        print("⚠️  Some other endpoints failed.")

if __name__ == "__main__":
    main()
