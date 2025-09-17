"""
Test suite for train optimization algorithms
Validates algorithm performance and correctness
"""
import numpy as np
import sys
import os
import pandas as pd
import unittest
from datetime import datetime
import unittest
from algorithms.milp_optimizer import MILPOptimizer
from algorithms.realtime_optimizer import RealtimeOptimizer
from algorithms.comprehensive_hybrid_optimizer import ComprehensiveHybridOptimizer

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.priority_engine import PriorityEngine
from algorithms.train_optimizer import TrainOptimizer, SimpleHeuristicOptimizer, GeneticAlgorithmOptimizer

class TestPriorityEngine(unittest.TestCase):
    """Test cases for Priority Engine"""
    
    def setUp(self):
        self.priority_engine = PriorityEngine()
    
    def test_train_type_priority(self):
        """Test basic train type priority assignment"""
        
        rajdhani = {'train_type': 'Rajdhani', 'scheduled_start_time': '12:00', 'delay_minutes': 0}
        freight = {'train_type': 'Freight', 'scheduled_start_time': '12:00', 'delay_minutes': 0}
        
        rajdhani_priority = self.priority_engine.get_train_priority(rajdhani)
        freight_priority = self.priority_engine.get_train_priority(freight)
        
        # Rajdhani should have higher priority (lower number)
        self.assertLess(rajdhani_priority, freight_priority)
        
        print(f"✅ Priority Test: Rajdhani ({rajdhani_priority:.2f}) > Freight ({freight_priority:.2f})")
    
    def test_conflict_resolution(self):
        """Test conflict resolution between two trains"""
        
        train_a = {
            'train_id': 'RAJ001',
            'train_type': 'Rajdhani',
            'scheduled_start_time': '08:00',
            'delay_minutes': 0
        }
        
        train_b = {
            'train_id': 'FRT001',
            'train_type': 'Freight', 
            'scheduled_start_time': '08:00',
            'delay_minutes': 0
        }
        
        winner = self.priority_engine.resolve_conflict(train_a, train_b)
        self.assertEqual(winner, 'RAJ001')
        
        print(f"✅ Conflict Resolution: {winner} wins (as expected)")
    
    def test_time_based_priority(self):
        """Test time-based priority adjustments"""
        
        peak_train = {'train_type': 'Express', 'scheduled_start_time': '08:00', 'delay_minutes': 0}
        night_train = {'train_type': 'Express', 'scheduled_start_time': '02:00', 'delay_minutes': 0}
        
        peak_priority = self.priority_engine.get_train_priority(peak_train)
        night_priority = self.priority_engine.get_train_priority(night_train)
        
        # Peak hour trains should have slightly higher priority
        self.assertLess(peak_priority, night_priority)
        
        print(f"✅ Time Priority: Peak ({peak_priority:.2f}) > Night ({night_priority:.2f})")

class TestOptimizationAlgorithms(unittest.TestCase):
    """Test cases for optimization algorithms"""
    
    def setUp(self):
        # Create sample data
        self.trains_df = pd.DataFrame({
            'train_id': ['RAJ001', 'EXP002', 'PASS003', 'FRT004'],
            'train_name': ['Rajdhani Express', 'Shatabdi Express', 'Passenger', 'Goods Train'],
            'train_type': ['Rajdhani', 'Express', 'Passenger', 'Freight'],
            'priority': [1, 3, 4, 6],
            'delay_minutes': [0, 5, 2, 15],
            'scheduled_start_time': ['08:00', '09:30', '11:00', '14:00'],
            'max_speed_kmph': [130, 110, 80, 60],
            'origin_station': ['DEL', 'DEL', 'GZB', 'GZB'],
            'destination_station': ['MUM', 'AGR', 'DEL', 'MUM']
        })
        
        self.sections_df = pd.DataFrame({
            'section_id': ['S001', 'S002', 'S003', 'S004'],
            'from_station': ['DEL', 'GZB', 'AGR', 'BPL'],
            'to_station': ['GZB', 'AGR', 'BPL', 'MUM'],
            'length_km': [50, 80, 120, 200],
            'max_trains_allowed': [3, 2, 4, 3],
            'track_type': ['Double', 'Single', 'Double', 'Double']
        })
        
        self.train_sections_df = pd.DataFrame({
            'train_id': ['RAJ001', 'RAJ001', 'EXP002', 'PASS003', 'FRT004'],
            'section_id': ['S001', 'S002', 'S001', 'S001', 'S003'],
            'scheduled_entry_time': ['08:00', '08:45', '09:30', '11:00', '14:00'],
            'scheduled_exit_time': ['08:30', '09:15', '10:00', '11:30', '15:00']
        })
    
    def test_heuristic_optimizer(self):
        """Test heuristic optimization algorithm"""
        
        optimizer = SimpleHeuristicOptimizer()
        result = optimizer.optimize(self.trains_df, self.sections_df, self.train_sections_df)
        
        self.assertTrue(result.success)
        self.assertGreater(result.throughput, 0)
        self.assertGreater(len(result.schedule), 0)
        
        print(f"✅ Heuristic Optimizer: {result.total_delay:.1f} min delay, {result.throughput} trains")
    
    def test_genetic_algorithm(self):
        """Test genetic algorithm optimizer"""
        
        # Use smaller parameters for faster testing
        optimizer = GeneticAlgorithmOptimizer(population_size=10, generations=5)
        result = optimizer.optimize(self.trains_df, self.sections_df, self.train_sections_df)
        
        self.assertTrue(result.success)
        self.assertGreater(result.throughput, 0)
        self.assertGreater(len(result.fitness_history), 0)
        
        print(f"✅ Genetic Algorithm: {result.total_delay:.1f} min delay, {len(result.fitness_history)} generations")
    
    def test_full_optimization_pipeline(self):
        """Test complete optimization pipeline"""
        
        optimizer = TrainOptimizer()
        results = optimizer.run_all_optimizations(self.trains_df, self.sections_df, self.train_sections_df)
        
        self.assertGreater(len(results), 0)
        
        # Check that at least one method succeeded
        successful_results = [r for r in results if r.success]
        self.assertGreater(len(successful_results), 0)
        
        # Get best result
        best_result = optimizer.get_best_result(results)
        self.assertIsNotNone(best_result)
        
        print(f"✅ Full Pipeline: Best method = {best_result.method}")
        print(f"   Total delay: {best_result.total_delay:.1f} minutes")
        print(f"   Computation time: {best_result.computation_time:.2f} seconds")

class TestDataValidation(unittest.TestCase):
    """Test data validation and integrity"""
    
    def test_data_loading(self):
        """Test that CSV files can be loaded properly"""
        
        try:
            # Try to load CSV files if they exist
            if os.path.exists("../data/trains.csv"):
                trains = pd.read_csv("../data/trains.csv")
                self.assertGreater(len(trains), 0)
                print(f"✅ Data Loading: {len(trains)} trains loaded")
            else:
                print("⚠️  CSV files not found, skipping data loading test")
                
        except Exception as e:
            self.fail(f"Data loading failed: {e}")
    
    def test_schema_validation(self):
        """Test data schema validation"""
        
        # Test with sample data
        sample_trains = pd.DataFrame({
            'train_id': ['T001'],
            'train_name': ['Test Train'],
            'train_type': ['Express'],
            'priority': [3],
            'scheduled_start_time': ['12:00'],
            'delay_minutes': [0]
        })
        
        required_cols = {'train_id', 'train_type', 'scheduled_start_time'}
        actual_cols = set(sample_trains.columns)
        
        self.assertTrue(required_cols.issubset(actual_cols))
        print("✅ Schema Validation: Required columns present")

def run_performance_benchmark():
    """Run performance benchmark on algorithms"""
    
    print("\n🚀 Performance Benchmark")
    print("-" * 50)
    
    # Create larger dataset for benchmarking
    np.random.seed(42)
    n_trains = 20
    
    train_types = ['Rajdhani', 'Express', 'Passenger', 'Freight', 'Local']
    
    benchmark_trains = pd.DataFrame({
        'train_id': [f'T{i:03d}' for i in range(n_trains)],
        'train_name': [f'Train {i}' for i in range(n_trains)],
        'train_type': [np.random.choice(train_types) for _ in range(n_trains)],
        'priority': np.random.randint(1, 7, n_trains),
        'delay_minutes': np.random.randint(0, 30, n_trains),
        'scheduled_start_time': [f'{8 + i%12:02d}:00' for i in range(n_trains)]
    })
    
    benchmark_sections = pd.DataFrame({
        'section_id': [f'S{i:03d}' for i in range(10)],
        'from_station': [f'STN{i}' for i in range(10)],
        'to_station': [f'STN{i+1}' for i in range(10)],
        'length_km': np.random.randint(20, 200, 10),
        'max_trains_allowed': np.random.randint(2, 5, 10)
    })
    
    benchmark_train_sections = pd.DataFrame({
        'train_id': np.random.choice(benchmark_trains['train_id'], 50),
        'section_id': np.random.choice(benchmark_sections['section_id'], 50),
        'scheduled_entry_time': [f'{8 + i%16:02d}:{i%60:02d}' for i in range(50)],
        'scheduled_exit_time': [f'{9 + i%16:02d}:{i%60:02d}' for i in range(50)]
    })
    
    # Run benchmark
    optimizer = TrainOptimizer()
    results = optimizer.run_all_optimizations(benchmark_trains, benchmark_sections, benchmark_train_sections)
    
    print(f"\n📊 Benchmark Results ({n_trains} trains):")
    for result in results:
        if result.success:
            print(f"   {result.method}: {result.computation_time:.3f}s, {result.total_delay:.1f} min delay")

if __name__ == '__main__':
    print("🧪 Railway AI - Algorithm Test Suite")
    print("=" * 60)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmark
    run_performance_benchmark()
    
    print("\n✅ All tests completed!")


class TestExtendedAlgorithms(unittest.TestCase):

    def setUp(self):
        # Initialize data samples
        self.trains = pd.DataFrame({'train_id': ['T1', 'T2', 'T3'], 'priority': [1, 2, 2]})
        self.sections = pd.DataFrame({'section_id': ['S1']})
        self.train_sections = pd.DataFrame({
            'train_id': ['T1', 'T2', 'T3'],
            'section_id': ['S1', 'S1', 'S1'],
            'scheduled_entry_time': ['08:00', '08:10', '08:20']
        })

    def test_milp_optimizer(self):
        milp = MILPOptimizer()
        schedule = milp.optimize(self.trains, self.sections, self.train_sections)
        self.assertIsNotNone(schedule)
        self.assertTrue(all(isinstance(v, list) for v in schedule.values()))

    def test_comprehensive_hybrid_optimizer(self):
        comprehensive = ComprehensiveHybridOptimizer()
        result = comprehensive.optimize(self.trains, self.sections, self.train_sections)
        self.assertTrue(result.success)
        self.assertIsInstance(result.schedule, dict)
        self.assertIsInstance(result.total_delay, (int, float))

    def test_realtime_optimizer(self):
        realtime = RealtimeOptimizer()
        disrupted_trains = realtime.simulate_delay(self.trains, 'T2', 5)
        results = realtime.reoptimize(disrupted_trains, self.sections, self.train_sections)
        self.assertTrue(len(results) > 0)

if __name__ == '__main__':
    unittest.main()
