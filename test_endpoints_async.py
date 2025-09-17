"""
Async Endpoint Testing Script
Tests the FastAPI endpoints with proper async handling
"""

import asyncio
import sys
import os
sys.path.append('.')

import pandas as pd
from backend.app.routes.optimization import comprehensive_hybrid_optimizer, milp_optimizer, rl_optimizer

def create_test_data():
    """Create test data for optimization"""
    trains_data = {
        'train_id': ['T001', 'T002', 'T003', 'T004'],
        'train_name': ['Rajdhani Express', 'Shatabdi Express', 'Passenger Train', 'Freight Train'],
        'train_type': ['Rajdhani', 'Express', 'Passenger', 'Freight'],
        'priority': [1, 2, 4, 6],
        'delay_minutes': [0, 5, 10, 15],
        'scheduled_start_time': ['08:00', '09:30', '11:00', '14:00'],
        'max_speed_kmph': [130, 110, 80, 60]
    }
    
    sections_data = {
        'section_id': ['S001', 'S002', 'S003'],
        'from_station': ['DEL', 'GZB', 'AGR'],
        'to_station': ['GZB', 'AGR', 'BPL'],
        'length_km': [50, 80, 120],
        'max_trains_allowed': [3, 2, 4],
        'track_type': ['Double', 'Single', 'Double']
    }
    
    train_sections_data = {
        'train_id': ['T001', 'T001', 'T002', 'T003', 'T004'],
        'section_id': ['S001', 'S002', 'S001', 'S001', 'S003'],
        'scheduled_entry_time': ['08:00', '08:45', '09:30', '11:00', '14:00'],
        'scheduled_exit_time': ['08:30', '09:15', '10:00', '11:30', '15:00'],
        'start_time': [800, 845, 930, 1100, 1400],
        'end_time': [830, 915, 1000, 1130, 1500],
        'priority': [1, 1, 2, 4, 6]
    }
    
    return (
        pd.DataFrame(trains_data),
        pd.DataFrame(sections_data), 
        pd.DataFrame(train_sections_data)
    )

async def test_optimization_functions():
    """Test optimization functions with proper async handling"""
    print("🔧 Testing Optimization Functions (Async)")
    print("-" * 50)
    
    try:
        # Test comprehensive hybrid function
        print("Testing comprehensive_hybrid_optimizer function...")
        result = await comprehensive_hybrid_optimizer(None)  # Mock db session
        print(f"✅ Comprehensive Hybrid: {result.get('success', 'Unknown')}")
        print(f"   Method: {result.get('method', 'Unknown')}")
        print(f"   Trains: {result.get('trains_count', 'Unknown')}")
        print(f"   Total Delay: {result.get('total_delay', 'Unknown')}")
        print(f"   Computation Time: {result.get('computation_time', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_all_optimization_methods():
    """Test all optimization methods"""
    print("\n🌐 Testing All Optimization Methods")
    print("-" * 50)
    
    methods = [
        ("comprehensive_hybrid", comprehensive_hybrid_optimizer),
        ("milp", milp_optimizer),
        ("rl", rl_optimizer)
    ]
    
    results = {}
    
    for method_name, method_func in methods:
        print(f"\n--- Testing {method_name.upper()} ---")
        try:
            result = await method_func(None)  # Mock db session
            results[method_name] = True
            
            print(f"✅ {method_name}: Success")
            print(f"   Method: {result.get('method', 'Unknown')}")
            print(f"   Success: {result.get('success', 'Unknown')}")
            print(f"   Trains: {result.get('trains_count', 'Unknown')}")
            
            if 'total_delay' in result:
                print(f"   Total Delay: {result.get('total_delay', 'Unknown')}")
            if 'computation_time' in result:
                print(f"   Computation Time: {result.get('computation_time', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ {method_name}: {e}")
            results[method_name] = False
    
    return results

async def main():
    print("🚀 Railway AI - Async Endpoint Testing")
    print("=" * 60)
    
    # Test optimization functions
    success1 = await test_optimization_functions()
    
    # Test all methods
    results = await test_all_optimization_methods()
    
    print("\n" + "=" * 60)
    print("🎯 Testing Summary:")
    print(f"   Optimization Functions: {'✅ PASS' if success1 else '❌ FAIL'}")
    
    print("\n📊 Method Results:")
    for method, success in results.items():
        print(f"   {method}: {'✅ PASS' if success else '❌ FAIL'}")
    
    all_passed = success1 and all(results.values())
    
    if all_passed:
        print("\n🏆 All tests passed! Endpoints are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
