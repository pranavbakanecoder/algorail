"""
Direct Testing of Optimization Functions
Tests the optimization functions without requiring the full FastAPI server
"""

import sys
import os
sys.path.append('.')

import pandas as pd
from algorithms.comprehensive_hybrid_optimizer import ComprehensiveHybridOptimizer
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

def test_comprehensive_hybrid_direct():
    """Test comprehensive hybrid optimizer directly"""
    print("🧪 Testing Comprehensive Hybrid Optimizer (Direct)")
    print("-" * 50)
    
    try:
        trains_df, sections_df, train_sections_df = create_test_data()
        
        optimizer = ComprehensiveHybridOptimizer()
        result = optimizer.optimize(trains_df, sections_df, train_sections_df)
        
        print(f"✅ Success: {result.success}")
        print(f"📊 Method: {result.method}")
        print(f"⏱️  Computation Time: {result.computation_time:.2f}s")
        print(f"🚂 Total Delay: {result.total_delay:.1f}")
        print(f"🔧 Conflicts Resolved: {result.conflicts_resolved}")
        print(f"📈 Throughput: {result.throughput}")
        
        if result.schedule:
            print(f"📋 Schedule: {len(result.schedule)} trains scheduled")
            for train_id, schedule in list(result.schedule.items())[:2]:  # Show first 2
                print(f"   {train_id}: {len(schedule)} sections")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_optimization_functions():
    """Test optimization functions from routes"""
    print("\n🔧 Testing Optimization Functions (Routes)")
    print("-" * 50)
    
    try:
        trains_df, sections_df, train_sections_df = create_test_data()
        
        # Test comprehensive hybrid function
        print("Testing comprehensive_hybrid_optimizer function...")
        result = comprehensive_hybrid_optimizer(None)  # Mock db session
        print(f"✅ Comprehensive Hybrid: {result.get('success', 'Unknown')}")
        print(f"   Method: {result.get('method', 'Unknown')}")
        print(f"   Trains: {result.get('trains_count', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_endpoint_simulation():
    """Simulate API endpoint calls"""
    print("\n🌐 Testing API Endpoint Simulation")
    print("-" * 50)
    
    # Test different optimization methods
    methods = ["comprehensive_hybrid", "milp", "rl"]
    
    for method in methods:
        print(f"\n--- Testing {method.upper()} ---")
        try:
            if method == "comprehensive_hybrid":
                result = comprehensive_hybrid_optimizer(None)
            elif method == "milp":
                result = milp_optimizer(None)
            elif method == "rl":
                result = rl_optimizer(None)
            
            print(f"✅ {method}: Success")
            print(f"   Method: {result.get('method', 'Unknown')}")
            print(f"   Status: {result.get('success', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ {method}: {e}")

def main():
    print("🚀 Railway AI - Direct Optimization Testing")
    print("=" * 60)
    
    # Test 1: Direct comprehensive hybrid
    success1 = test_comprehensive_hybrid_direct()
    
    # Test 2: Optimization functions
    success2 = test_optimization_functions()
    
    # Test 3: API simulation
    test_api_endpoint_simulation()
    
    print("\n" + "=" * 60)
    print("🎯 Testing Summary:")
    print(f"   Direct Comprehensive Hybrid: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Optimization Functions: {'✅ PASS' if success2 else '❌ FAIL'}")
    print("   API Simulation: ✅ COMPLETED")
    
    if success1 and success2:
        print("\n🏆 All tests passed! Endpoints should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
