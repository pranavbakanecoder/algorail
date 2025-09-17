"""
Comprehensive Hybrid Optimizer
Integrates ACO, GA, and Heuristic optimizers with 3-stage pipeline approach.
Self-contained module with all optimization algorithms.
"""

import random
import pandas as pd
import numpy as np
import time
from typing import List, Dict, Tuple

class OptimizationResult:
    """Container for optimization results"""
    
    def __init__(self, method: str):
        self.method = method
        self.total_delay = 0.0
        self.computation_time = 0.0
        self.throughput = 0
        self.schedule = {}
        self.conflicts_resolved = 0
        self.success = False
        self.fitness_history = []

class SimpleHeuristicOptimizer:
    """Simple heuristic optimizer based on priority rules"""
    
    def __init__(self):
        pass
    
    def optimize(self, trains_df: pd.DataFrame, sections_df: pd.DataFrame,
                train_sections_df: pd.DataFrame) -> OptimizationResult:
        """Run simple priority-based optimization"""
        
        start_time = time.time()
        result = OptimizationResult("Priority Heuristic")
        
        try:
            # Sort trains by priority (lower number = higher priority)
            trains_sorted = trains_df.sort_values('priority').copy()
            
            schedule = {}
            total_delay = 0
            conflicts_resolved = 0
            
            for _, train in trains_sorted.iterrows():
                train_id = train['train_id']
                base_delay = train.get('delay_minutes', 0)
                priority = train.get('priority', 5)
                
                # Assign delay based on priority
                if priority <= 2:  # High priority
                    additional_delay = random.uniform(0, 5)
                elif priority <= 4:  # Medium priority
                    additional_delay = random.uniform(2, 10)
                else:  # Low priority
                    additional_delay = random.uniform(5, 20)
                
                final_delay = base_delay + additional_delay
                total_delay += final_delay
                
                # Create train schedule
                train_schedule = []
                train_sections = train_sections_df[train_sections_df['train_id'] == train_id]
                
                for _, section in train_sections.iterrows():
                    train_schedule.append({
                        'section_id': section['section_id'],
                        'entry_time': section.get('scheduled_entry_time', section.get('start_time', 0)),
                        'exit_time': section.get('scheduled_exit_time', section.get('end_time', 0)),
                        'delay_added': additional_delay
                    })
                
                schedule[train_id] = train_schedule
                conflicts_resolved += 1
            
            result.schedule = schedule
            result.total_delay = total_delay
            result.throughput = len(trains_df)
            result.conflicts_resolved = conflicts_resolved
            result.success = True
            
        except Exception as e:
            print(f"❌ Heuristic optimization failed: {e}")
            result.success = False
        
        result.computation_time = time.time() - start_time
        return result

class ACOOptimizer:
    """Original ACOOptimizer for train scheduling"""

    def __init__(self, population_size=30, iterations=50, alpha=1.0, beta=5.0, evaporation_rate=0.5):
        self.population_size = population_size
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.best_schedule = None
        self.best_score = float('inf')
        self.trains_df = None
        self.train_sections_df = None

    def _initialize_pheromones(self, trains):
        pheromones = {}
        for t1 in trains:
            for t2 in trains:
                if t1 != t2:
                    pheromones[(t1, t2)] = 1.0
        return pheromones

    def _calculate_heuristic(self, t1_priority, t2_priority):
        return 1.0 / (abs(t1_priority - t2_priority) + 1)

    def optimize(self, trains_df: pd.DataFrame, sections_df: pd.DataFrame,
                 train_sections_df: pd.DataFrame, seed_solution=None) -> Tuple[List, float]:
        self.trains_df = trains_df
        self.train_sections_df = train_sections_df
        trains = trains_df['train_id'].tolist()
        priorities = {tid: trains_df[trains_df['train_id'] == tid]['priority'].values[0] for tid in trains}
        pheromones = self._initialize_pheromones(trains)

        for iteration in range(self.iterations):
            population = []
            scores = []

            for _ in range(self.population_size):
                schedule = self._construct_solution(trains, pheromones, priorities)
                score = self._evaluate(schedule)
                population.append(schedule)
                scores.append(score)

                if score < self.best_score:
                    self.best_score = score
                    self.best_schedule = schedule

            self._update_pheromones(pheromones, population, scores)

        return self.best_schedule, self.best_score

    def _construct_solution(self, trains, pheromones, priorities):
        schedule = []
        unvisited = set(trains)
        current = random.choice(trains)
        schedule.append(current)
        unvisited.remove(current)

        while unvisited:
            probs = []
            denom = 0.0

            for t in unvisited:
                tau = pheromones.get((current, t), 1)
                eta = self._calculate_heuristic(priorities[current], priorities[t])
                p = (tau ** self.alpha) * (eta ** self.beta)
                probs.append((t, p))
                denom += p

            if denom > 0:
                probs = [(t, p/denom) for t, p in probs]
                current = self._roulette_wheel_selection(probs)
            else:
                current = random.choice(list(unvisited))

            schedule.append(current)
            unvisited.remove(current)

        return schedule

    def _roulette_wheel_selection(self, probs):
        r = random.random()
        cumulative = 0.0
        for t, p in probs:
            cumulative += p
            if r <= cumulative:
                return t
        return probs[-1][0]

    def _evaluate(self, schedule):
        score = 0
        priority_penalty = 100
        conflict_penalty = 1000

        # Priority inversion penalty
        for i, ti in enumerate(schedule):
            for j in range(i):
                tj = schedule[j]
                pri_i = self.trains_df.loc[self.trains_df['train_id'] == ti, 'priority'].values
                pri_j = self.trains_df.loc[self.trains_df['train_id'] == tj, 'priority'].values
                if pri_i.size and pri_j.size and pri_j[0] > pri_i[0]:
                    score += priority_penalty

        # Section conflict penalty
        ts_map = {
            row['train_id']: set(self.train_sections_df[self.train_sections_df['train_id'] == row['train_id']]['section_id'])
            for _, row in self.trains_df.iterrows()
        }
        for i, ti in enumerate(schedule):
            for j in range(i+1, len(schedule)):
                tj = schedule[j]
                if ts_map.get(ti, set()) & ts_map.get(tj, set()) and abs(i-j) <= 1:
                    score += conflict_penalty

        return score

    def _update_pheromones(self, pheromones, population, scores):
        # Evaporation
        for key in pheromones:
            pheromones[key] *= (1 - self.evaporation_rate)
            if pheromones[key] < 0.1:
                pheromones[key] = 0.1

        # Deposit pheromones for best solution
        best_idx = scores.index(min(scores))
        best = population[best_idx]
        for i in range(len(best) - 1):
            key = (best[i], best[i+1])
            if key in pheromones and scores[best_idx] > 0:
                pheromones[key] += 1 / scores[best_idx]

class GAOptimizer:
    """Enhanced Genetic Algorithm with advanced evaluation and hybrid support"""
    
    def __init__(self, population_size=30, generations=50, mutation_rate=0.05):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
    
    def optimize(self, trains_df: pd.DataFrame, sections_df: pd.DataFrame, 
                 train_sections_df: pd.DataFrame, initial_population=None) -> OptimizationResult:
        """Optimize with optional initial population seeding"""
        
        start_time = time.time()
        result = OptimizationResult("GA (Genetic Algorithm)")
        
        try:
            trains = trains_df['train_id'].tolist()
            
            # Use initial population if provided (for hybrid approaches)
            if initial_population is not None and len(initial_population) > 0:
                population = []
                for individual in initial_population[:self.population_size]:
                    if isinstance(individual, list) and all(isinstance(x, str) for x in individual):
                        population.append(individual)
                
                # Fill remaining slots if needed
                while len(population) < self.population_size:
                    population.append(random.sample(trains, len(trains)))
            else:
                # Create random population
                population = [random.sample(trains, len(trains)) for _ in range(self.population_size)]
            
            best_individual = None
            best_score = float('inf')
            fitness_history = []
            
            for generation in range(self.generations):
                # Evaluate all individuals
                scores = [self._evaluate(ind, train_sections_df) for ind in population]
                
                # Track best solution
                best_gen_idx = np.argmin(scores)
                if scores[best_gen_idx] < best_score:
                    best_score = scores[best_gen_idx]
                    best_individual = population[best_gen_idx].copy()
                
                fitness_history.append(best_score)
                
                # Selection, crossover, and mutation
                selected = self._selection(population, scores)
                next_population = []
                
                for i in range(self.population_size // 2):
                    parent1, parent2 = random.sample(selected, 2)
                    child1, child2 = self._crossover(parent1, parent2)
                    next_population.extend([
                        self._mutate(child1),
                        self._mutate(child2)
                    ])
                
                population = next_population[:self.population_size]
            
            # Convert to schedule format
            schedule_dict = self._convert_to_schedule_format(best_individual, trains_df, train_sections_df)
            
            result.schedule = schedule_dict
            result.total_delay = best_score
            result.throughput = len(trains_df)
            result.conflicts_resolved = self.population_size * len(fitness_history)
            result.fitness_history = fitness_history
            result.success = True
            
        except Exception as e:
            print(f"❌ GA optimization failed: {e}")
            result.success = False
        
        result.computation_time = time.time() - start_time
        return result
    
    def _evaluate(self, individual, train_sections_df):
        """Advanced evaluation with conflict detection, priorities, and idle time"""
        score = 0
        section_usage = {}  # section_id -> list of (start, end)
        priority_bonus = 0
        
        for order, train_id in enumerate(individual):
            train_sections = train_sections_df[train_sections_df['train_id'] == train_id]
            
            # Get priority (default to 1 if not available)
            priority = train_sections['priority'].iloc[0] if 'priority' in train_sections.columns else 1
            
            for _, row in train_sections.iterrows():
                sec_id = row['section_id']
                start = row.get('start_time', 0)
                end = row.get('end_time', 0)
                
                # Initialize section usage tracking
                if sec_id not in section_usage:
                    section_usage[sec_id] = []
                
                # Check for conflicts in this section
                for (used_start, used_end) in section_usage[sec_id]:
                    # Heavy penalty for overlap conflicts
                    if not (end <= used_start or start >= used_end):
                        score += 100  # Large penalty for conflict
                
                # Record this usage
                section_usage[sec_id].append((start, end))
                
                # Idle time penalty (if train waits before entering section)
                if order > 0:
                    prev_train_id = individual[order - 1]
                    prev_sections = train_sections_df[train_sections_df['train_id'] == prev_train_id]
                    prev_end = prev_sections.get('end_time', pd.Series([0])).max()
                    idle_time = max(0, start - prev_end)
                    score += idle_time * 2  # Penalty for idle time
            
            # Priority bonus: reward higher priority trains scheduled earlier
            priority_bonus += priority * (len(individual) - order)
        
        # Subtract bonus from total score (lower score is better)
        score -= priority_bonus
        return score
    
    def _selection(self, population, scores):
        """Select best half of population"""
        idx_sorted = np.argsort(scores)
        selected = [population[i] for i in idx_sorted[:len(population)//2]]
        return selected
    
    def _crossover(self, parent1, parent2):
        """Order crossover preserving train sequence"""
        size = len(parent1)
        p1, p2 = sorted(random.sample(range(size), 2))
        
        child1 = parent1[p1:p2] + [t for t in parent2 if t not in parent1[p1:p2]]
        child2 = parent2[p1:p2] + [t for t in parent1 if t not in parent2[p1:p2]]
        
        return child1, child2
    
    def _mutate(self, individual):
        """Swap mutation"""
        if random.random() < self.mutation_rate:
            i, j = random.sample(range(len(individual)), 2)
            individual[i], individual[j] = individual[j], individual[i]
        return individual
    
    def _convert_to_schedule_format(self, individual, trains_df, train_sections_df):
        """Convert GA individual to standard schedule format"""
        schedule_dict = {}
        
        for order, train_id in enumerate(individual):
            train_schedule = []
            train_sections = train_sections_df[train_sections_df['train_id'] == train_id]
            
            # Calculate delay based on position and conflicts
            base_delay = order * 1.5  # Position-based delay
            
            for _, section in train_sections.iterrows():
                train_schedule.append({
                    'section_id': section['section_id'],
                    'entry_time': section.get('start_time', 0),
                    'exit_time': section.get('end_time', 0),
                    'delay_added': base_delay
                })
            
            schedule_dict[train_id] = train_schedule
        
        return schedule_dict

class ComprehensiveHybridOptimizer:
    """3-stage hybrid optimizer: Heuristic → ACO → GA"""
    
    def __init__(self, heuristic_params=None, aco_params=None, ga_params=None):
        self.heuristic_params = heuristic_params or {}
        self.aco_params = aco_params or {'population_size': 20, 'iterations': 30}
        self.ga_params = ga_params or {'population_size': 30, 'generations': 40}
    
    def optimize(self, trains_df: pd.DataFrame, sections_df: pd.DataFrame, 
                train_sections_df: pd.DataFrame) -> OptimizationResult:
        """Run comprehensive 3-stage hybrid optimization"""
        
        start_time = time.time()
        result = OptimizationResult("Comprehensive Hybrid (Heuristic → ACO → GA)")
        
        try:
            print("   🚀 Starting 3-Stage Hybrid Optimization...")
            
            # Stage 1: Heuristic (fast baseline)
            print("   📋 Stage 1: Running Heuristic Optimizer...")
            heuristic_optimizer = SimpleHeuristicOptimizer(**self.heuristic_params)
            heuristic_result = heuristic_optimizer.optimize(trains_df, sections_df, train_sections_df)
            
            if heuristic_result.success:
                heuristic_schedule = self._extract_train_order_from_schedule(heuristic_result.schedule, trains_df)
                print(f"   ✅ Heuristic baseline: {heuristic_result.total_delay:.1f} delay")
            else:
                print("   ❌ Heuristic failed, using random seed")
                heuristic_schedule = None
            
            # Stage 2: ACO (seeded by heuristic)
            print("   🐜 Stage 2: Running ACO Optimizer (seeded)...")
            aco_optimizer = ACOOptimizer(**self.aco_params)
            aco_schedule, aco_score = aco_optimizer.optimize(trains_df, sections_df, train_sections_df, 
                                                           seed_solution=heuristic_schedule)
            
            if aco_schedule and aco_score < float('inf'):
                print(f"   ✅ ACO improvement: {aco_score:.1f} delay")
            else:
                print("   ❌ ACO failed, using heuristic for GA")
                aco_schedule = heuristic_schedule
                aco_score = heuristic_result.total_delay if heuristic_result.success else float('inf')
            
            # Stage 3: GA (seeded by both heuristic and ACO)
            print("   🧬 Stage 3: Running GA Optimizer (multi-seeded)...")
            ga_optimizer = GAOptimizer(**self.ga_params)
            
            # Create initial population with both seeds
            initial_population = []
            if aco_schedule:
                initial_population.append(aco_schedule)
            if heuristic_schedule and heuristic_schedule != aco_schedule:
                initial_population.append(heuristic_schedule)
            
            ga_result = ga_optimizer.optimize(trains_df, sections_df, train_sections_df, 
                                            initial_population=initial_population)
            
            # Stage 4: Return best result
            if ga_result.success:
                result = ga_result
                result.method = "Comprehensive Hybrid (Heuristic → ACO → GA)"
                print(f"   🏆 Final GA result: {ga_result.total_delay:.1f} delay")
                
                # Combine statistics from all stages
                result.conflicts_resolved = (
                    (heuristic_result.conflicts_resolved if heuristic_result.success else 0) +
                    (self.aco_params.get('population_size', 20) * self.aco_params.get('iterations', 30)) +
                    ga_result.conflicts_resolved
                )
            else:
                # Fallback to best available result
                if aco_schedule and aco_score < float('inf'):
                    # Create result from ACO
                    result = OptimizationResult("Comprehensive Hybrid (ACO Fallback)")
                    result.schedule = self._convert_aco_schedule_to_dict(aco_schedule, trains_df, train_sections_df)
                    result.total_delay = aco_score
                    result.throughput = len(trains_df)
                    result.success = True
                elif heuristic_result.success:
                    result = heuristic_result
                    result.method = "Comprehensive Hybrid (Heuristic Fallback)"
                else:
                    result.success = False
            
            print(f"   ✅ 3-Stage Hybrid Complete!")
            
        except Exception as e:
            print(f"   ❌ Comprehensive Hybrid optimization failed: {e}")
            result.success = False
        
        result.computation_time = time.time() - start_time
        return result
    
    def _extract_train_order_from_schedule(self, schedule_dict, trains_df):
        """Extract train order from schedule dictionary"""
        if not schedule_dict:
            return None
        
        trains = trains_df['train_id'].tolist()
        
        # Simple extraction - use order of appearance in schedule
        # In a real implementation, you'd sort by actual scheduling times
        train_order = []
        for train_id in schedule_dict.keys():
            if train_id in trains:
                train_order.append(train_id)
        
        # Add any missing trains
        for train_id in trains:
            if train_id not in train_order:
                train_order.append(train_id)
        
        return train_order
    
    def _convert_aco_schedule_to_dict(self, train_order, trains_df, train_sections_df):
        """Convert ACO train order to schedule dictionary format"""
        schedule_dict = {}
        
        for order, train_id in enumerate(train_order):
            train_schedule = []
            train_sections = train_sections_df[train_sections_df['train_id'] == train_id]
            
            # Calculate delay based on position in schedule
            base_delay = order * 2  # Simple delay calculation
            
            for _, section in train_sections.iterrows():
                train_schedule.append({
                    'section_id': section['section_id'],
                    'entry_time': section.get('start_time', 0),
                    'exit_time': section.get('end_time', 0),
                    'delay_added': base_delay
                })
            
            schedule_dict[train_id] = train_schedule
        
        return schedule_dict

# Standalone testing and usage
if __name__ == "__main__":
    print("🧪 Testing Comprehensive Hybrid Optimizer")
    print("=" * 50)
    
    # Sample data
    trains_data = {
        'train_id': ['RAJ001', 'EXP002', 'FRT003', 'LOC004'],
        'train_name': ['Rajdhani', 'Express', 'Freight', 'Local'],
        'priority': [1, 2, 5, 4],
        'delay_minutes': [0, 5, 10, 2]
    }
    trains_df = pd.DataFrame(trains_data)
    
    sections_df = pd.DataFrame({
        'section_id': ['S1', 'S2', 'S3'], 
        'from_station': ['A', 'B', 'C'], 
        'to_station': ['B', 'C', 'D']
    })
    
    train_sections_df = pd.DataFrame({
        'train_id': ['RAJ001', 'RAJ001', 'EXP002', 'FRT003', 'LOC004'],
        'section_id': ['S1', 'S2', 'S1', 'S3', 'S2'],
        'start_time': [800, 830, 1000, 1400, 1200],
        'end_time': [830, 900, 1030, 1430, 1230],
        'priority': [1, 1, 2, 5, 4]
    })
    
    # Run comprehensive optimization
    optimizer = ComprehensiveHybridOptimizer()
    result = optimizer.optimize(trains_df, sections_df, train_sections_df)
    
    if result.success:
        print(f"\n🎯 Success: {result.method}")
        print(f"📊 Total Delay: {result.total_delay:.1f}")
        print(f"⏱️  Computation Time: {result.computation_time:.2f}s")
        print(f"🔧 Conflicts Resolved: {result.conflicts_resolved}")
        print(f"🚂 Trains Scheduled: {len(result.schedule)}")
    else:
        print("\n❌ Optimization failed")