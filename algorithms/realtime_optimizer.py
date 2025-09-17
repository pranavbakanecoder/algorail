import copy
from algorithms.comprehensive_hybrid_optimizer import ComprehensiveHybridOptimizer

class RealtimeOptimizer:
    def __init__(self):
        self.comprehensive_optimizer = ComprehensiveHybridOptimizer()

    def simulate_delay(self, trains_df, train_id, delay_minutes):
        # Copy data to avoid mutation
        disrupted_trains = copy.deepcopy(trains_df)
        mask = disrupted_trains['train_id'] == train_id
        disrupted_trains.loc[mask, 'delay_minutes'] += delay_minutes
        return disrupted_trains

    def reoptimize(self, disrupted_trains_df, sections_df, train_sections_df):
        # Run comprehensive hybrid optimizer for speed and accuracy
        return self.comprehensive_optimizer.optimize(disrupted_trains_df, sections_df, train_sections_df)
    
    def reoptimize_with_config(self, disrupted_trains_df, sections_df, train_sections_df, 
                              aco_params=None, ga_params=None):
        # Run comprehensive hybrid optimizer with custom parameters
        optimizer = ComprehensiveHybridOptimizer(
            aco_params=aco_params or {},
            ga_params=ga_params or {}
        )
        return optimizer.optimize(disrupted_trains_df, sections_df, train_sections_df)
