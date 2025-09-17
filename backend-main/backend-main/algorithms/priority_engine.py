"""
Priority Engine for Train Traffic Optimization
Handles train priority decisions based on Indian Railways classification
"""
import pandas as pd
from typing import Dict

class PriorityEngine:
    """Handles train priority and precedence decisions"""
    
    def __init__(self):
        # Indian Railways Priority Matrix
        self.train_type_priority = {
            'Rajdhani': 1,       # Highest priority
            'Shatabdi': 1,      
            'Vande Bharat': 1,
            'Duronto': 2,
            'Express': 3,
            'Mail': 3,
            'Superfast': 3,
            'Passenger': 4,
            'Local': 5,
            'Freight': 6,        # Lowest priority
            'MEMU': 5,
            'DEMU': 5
        }
        
        # Time-based priority adjustments
        self.time_multipliers = {
            'peak_hours': 0.8,       # Higher priority during peak
            'night_hours': 1.2,      # Lower priority at night
            'normal_hours': 1.0
        }
    
    def get_train_priority(self, train_info: Dict) -> float:
        """Calculate final priority score for a train"""
        
        base_priority = self.train_type_priority.get(train_info.get('train_type', 'Passenger'), 4)
        
        # Add custom priority if specified
        if 'priority' in train_info:
            base_priority = min(base_priority, train_info['priority'])
        
        # Time-based adjustment
        scheduled_time = train_info.get('scheduled_start_time', '12:00')
        time_factor = self._get_time_factor(scheduled_time)
        
        # Delay penalty (delayed trains get slightly lower priority)
        delay_penalty = min(train_info.get('delay_minutes', 0) * 0.01, 0.5)
        
        final_priority = base_priority * time_factor + delay_penalty
        
        return final_priority
    
    def _get_time_factor(self, time_str: str) -> float:
        """Get time-based priority multiplier"""
        try:
            hour = int(time_str.split(':')[0])
            
            # Peak hours: 7-10 AM, 5-8 PM
            if (7 <= hour <= 10) or (17 <= hour <= 20):
                return self.time_multipliers['peak_hours']
            # Night hours: 11 PM - 5 AM
            elif hour >= 23 or hour <= 5:
                return self.time_multipliers['night_hours']
            else:
                return self.time_multipliers['normal_hours']
                
        except:
            return 1.0
    
    def resolve_conflict(self, train_a: Dict, train_b: Dict) -> str:
        """Decide which train gets priority in a conflict"""
        
        priority_a = self.get_train_priority(train_a)
        priority_b = self.get_train_priority(train_b)
        
        # Lower number = higher priority
        if priority_a < priority_b:
            return train_a['train_id']
        elif priority_b < priority_a:
            return train_b['train_id']
        else:
            # Equal priority - use scheduled time as tiebreaker
            time_a = train_a.get('scheduled_start_time', '12:00')
            time_b = train_b.get('scheduled_start_time', '12:00')
            
            if time_a <= time_b:
                return train_a['train_id']
            else:
                return train_b['train_id']
    
    def get_priority_explanation(self, train_info: Dict) -> str:
        """Get human-readable explanation of priority decision"""
        
        train_type = train_info.get('train_type', 'Unknown')
        base_priority = self.train_type_priority.get(train_type, 4)
        delay = train_info.get('delay_minutes', 0)
        
        explanation = f"Train Type: {train_type} (Priority Level {base_priority})"
        
        if delay > 0:
            explanation += f" | Delayed by {delay} minutes"
        
        scheduled_time = train_info.get('scheduled_start_time', '12:00')
        hour = int(scheduled_time.split(':')[0])
        
        if (7 <= hour <= 10) or (17 <= hour <= 20):
            explanation += " | Peak hours - Higher priority"
        elif hour >= 23 or hour <= 5:
            explanation += " | Night hours - Lower priority"
        
        return explanation
    
    def create_priority_matrix(self, trains_df: pd.DataFrame) -> pd.DataFrame:
        """Create a priority matrix for all trains"""
        
        priority_data = []
        
        for _, train in trains_df.iterrows():
            train_dict = train.to_dict()
            priority_score = self.get_train_priority(train_dict)
            explanation = self.get_priority_explanation(train_dict)
            
            priority_data.append({
                'train_id': train['train_id'],
                'train_name': train.get('train_name', 'Unknown'),
                'train_type': train.get('train_type', 'Unknown'),
                'priority_score': priority_score,
                'explanation': explanation,
                'scheduled_time': train.get('scheduled_start_time', '12:00'),
                'delay_minutes': train.get('delay_minutes', 0)
            })
        
        priority_df = pd.DataFrame(priority_data)
        priority_df = priority_df.sort_values('priority_score')
        priority_df['rank'] = range(1, len(priority_df) + 1)
        
        return priority_df


# Sample test run (can be removed or commented out when integrating)
if __name__ == "__main__":
    engine = PriorityEngine()

    train_1 = {
        'train_id': 'RAJ001',
        'train_name': 'Rajdhani Express',
        'train_type': 'Rajdhani',
        'scheduled_start_time': '08:00',
        'delay_minutes': 0
    }

    train_2 = {
        'train_id': 'FRT001', 
        'train_name': 'Freight Train',
        'train_type': 'Freight',
        'scheduled_start_time': '10:00',
        'delay_minutes': 15
    }

    print("🧪 Testing Priority Engine")
    print("-" * 40)

    priority_1 = engine.get_train_priority(train_1)
    priority_2 = engine.get_train_priority(train_2)

    print(f"Train 1 ({train_1['train_name']}): Priority = {priority_1:.2f}")
    print(f"Train 2 ({train_2['train_name']}): Priority = {priority_2:.2f}")

    winner = engine.resolve_conflict(train_1, train_2)
    print(f"\n🏆 Conflict Resolution: {winner} gets priority")

    print("\n📝 Explanations:")
    print(f"Train 1: {engine.get_priority_explanation(train_1)}")
    print(f"Train 2: {engine.get_priority_explanation(train_2)}")
