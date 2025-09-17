"""
Endpoint Testing Without Database Dependency
Tests optimization logic without requiring database connection
"""

import sys
import os
sys.path.append('.')

import pandas as pd
from algorithms.comprehensive_hybrid_optimizer import ComprehensiveHybridOptimizer

def create_test_data():
    """Create comprehensive test data"""
    trains_data = {
        'train_id': ['T001', 'T002', 'T003', 'T004', 'T005'],
        'train_name': ['Rajdhani Express', 'Shatabdi Express', 'Passenger Train', 'Freight Train', 'Local Train'],
        'train_type': ['Rajdhani', 'Express', 'Passenger', 'Freight', 'Local'],
        'priority': [1, 2, 4, 6, 5],
        'delay_minutes': [0, 5, 10, 15, 8],
        'scheduled_start_time': ['08:00', '09:30', '11:00', '14:00', '16:00'],
        'max_speed_kmph': [130, 110, 80, 60, 70]
    }
    
    sections_data = {
        'section_id': ['S001', 'S002', 'S003', 'S004'],
        'from_station': ['DEL', 'GZB', 'AGR', 'BPL'],
        'to_station': ['GZB', 'AGR', 'BPL', 'MUM'],
        'length_km': [50, 80, 120, 200],
        'max_trains_allowed': [3, 2, 4, 3],
        'track_type': ['Double', 'Single', 'Double', 'Double']
    }
    
    train_sections_data = {
        'train_id': ['T001', 'T001', 'T002', 'T003', 'T004', 'T005'],
        'section_id': ['S001', 'S002', 'S001', 'S001', 'S003', 'S002'],
        'scheduled_entry_time': ['08:00', '08:45', '09:30', '11:00', '14:00', '16:00'],
        'scheduled_exit_time': ['08:30', '09:15', '10:00', '11:30', '15:00', '16:30'],
        'start_time': [800, 845, 930, 1100, 1400, 1600],
        'end_time': [830, 915, 1000, 1130, 1500, 1630],
        'priority': [1, 1, 2, 4, 6, 5]
    }
    
    return (
        pd.DataFrame(trains_data),
        pd.DataFrame(sections_data), 
        pd.DataFrame(train_sections_data)
    )

def test_comprehensive_hybrid_performance():
    """Test comprehensive hybrid optimizer performance"""
    print("🧪 Testing Comprehensive Hybrid Optimizer Performance")
    print("-" * 60)
    
    trains_df, sections_df, train_sections_df = create_test_data()
    
    # Test with different parameter configurations
    configs = [
        {"name": "Fast", "aco_params": {"population_size": 10, "iterations": 10}, "ga_params": {"population_size": 15, "generations": 15}},
        {"name": "Balanced", "aco_params": {"population_size": 20, "iterations": 20}, "ga_params": {"population_size": 25, "generations": 25}},
        {"name": "Thorough", "aco_params": {"population_size": 30, "iterations": 30}, "ga_params": {"population_size": 40, "generations": 40}}
    ]
    
    results = []
    
    for config in configs:
        print(f"\n--- Testing {config['name']} Configuration ---")
        
        try:
            optimizer = ComprehensiveHybridOptimizer(
                aco_params=config['aco_params'],
                ga_params=config['ga_params']
            )
            
            result = optimizer.optimize(trains_df, sections_df, train_sections_df)
            
            if result.success:
                print(f"✅ Success: {result.method}")
                print(f"   Computation Time: {result.computation_time:.2f}s")
                print(f"   Total Delay: {result.total_delay:.1f}")
                print(f"   Conflicts Resolved: {result.conflicts_resolved}")
                print(f"   Throughput: {result.throughput}")
                
                results.append({
                    'config': config['name'],
                    'success': True,
                    'time': result.computation_time,
                    'delay': result.total_delay,
                    'conflicts': result.conflicts_resolved
                })
            else:
                print(f"❌ Failed: {result.method}")
                results.append({
                    'config': config['name'],
                    'success': False,
                    'time': 0,
                    'delay': float('inf'),
                    'conflicts': 0
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'config': config['name'],
                'success': False,
                'time': 0,
                'delay': float('inf'),
                'conflicts': 0
            })
    
    return results

def test_optimization_consistency():
    """Test optimization consistency across multiple runs"""
    print("\n🔄 Testing Optimization Consistency")
    print("-" * 60)
    
    trains_df, sections_df, train_sections_df = create_test_data()
    optimizer = ComprehensiveHybridOptimizer()
    
    runs = 3
    results = []
    
    for i in range(runs):
        print(f"\n--- Run {i+1}/{runs} ---")
        
        try:
            result = optimizer.optimize(trains_df, sections_df, train_sections_df)
            
            if result.success:
                print(f"✅ Success: {result.total_delay:.1f} delay, {result.computation_time:.2f}s")
                results.append({
                    'run': i+1,
                    'success': True,
                    'delay': result.total_delay,
                    'time': result.computation_time
                })
            else:
                print(f"❌ Failed")
                results.append({
                    'run': i+1,
                    'success': False,
                    'delay': float('inf'),
                    'time': 0
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'run': i+1,
                'success': False,
                'delay': float('inf'),
                'time': 0
            })
    
    return results

def test_schedule_format():
    """Test schedule format and structure"""
    print("\n📋 Testing Schedule Format")
    print("-" * 60)
    
    trains_df, sections_df, train_sections_df = create_test_data()
    optimizer = ComprehensiveHybridOptimizer()
    
    try:
        result = optimizer.optimize(trains_df, sections_df, train_sections_df)
        
        if result.success and result.schedule:
            print(f"✅ Schedule generated successfully")
            print(f"   Trains scheduled: {len(result.schedule)}")
            
            # Check schedule structure
            for train_id, schedule in result.schedule.items():
                print(f"   {train_id}: {len(schedule)} sections")
                for section in schedule[:2]:  # Show first 2 sections
                    print(f"     - {section['section_id']}: {section['entry_time']}-{section['exit_time']}")
            
            return True
        else:
            print(f"❌ No schedule generated")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Railway AI - Comprehensive Endpoint Testing")
    print("=" * 70)
    
    # Test 1: Performance with different configurations
    perf_results = test_comprehensive_hybrid_performance()
    
    # Test 2: Consistency across multiple runs
    consistency_results = test_optimization_consistency()
    
    # Test 3: Schedule format
    format_success = test_schedule_format()
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 Testing Summary")
    print("=" * 70)
    
    print("\n📊 Performance Results:")
    for result in perf_results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"   {result['config']}: {status} ({result['time']:.2f}s, {result['delay']:.1f} delay)")
    
    print("\n🔄 Consistency Results:")
    successful_runs = [r for r in consistency_results if r['success']]
    if successful_runs:
        avg_delay = sum(r['delay'] for r in successful_runs) / len(successful_runs)
        avg_time = sum(r['time'] for r in successful_runs) / len(successful_runs)
        print(f"   Successful runs: {len(successful_runs)}/{len(consistency_results)}")
        print(f"   Average delay: {avg_delay:.1f}")
        print(f"   Average time: {avg_time:.2f}s")
    else:
        print("   ❌ No successful runs")
    
    print(f"\n📋 Schedule Format: {'✅ PASS' if format_success else '❌ FAIL'}")
    
    # Overall assessment
    all_perf_passed = all(r['success'] for r in perf_results)
    any_consistency = len(successful_runs) > 0
    
    if all_perf_passed and any_consistency and format_success:
        print("\n🏆 All tests passed! The comprehensive hybrid optimizer is working correctly.")
        print("   The endpoints should work once database connection is properly configured.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()
