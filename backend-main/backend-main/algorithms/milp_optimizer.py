import pulp
import pandas as pd

class MILPOptimizer:
    def __init__(self, max_block_time=10, time_limit=30):
        self.max_block_time = max_block_time
        self.time_limit = time_limit  # solver time limit in seconds

    def _time_to_minutes(self, time_str):
        h, m = map(int, time_str.split(':'))
        return h * 60 + m

    def optimize(self, trains_df, sections_df, train_sections_df):
        # Limit data size for testing speed
        trains_df = trains_df.head(10)
        sections_df = sections_df.head(50)
        train_sections_df = train_sections_df[train_sections_df['train_id'].isin(trains_df['train_id'])]

        model = pulp.LpProblem("Train_Scheduling_Optimization", pulp.LpMinimize)
        trains = trains_df['train_id'].tolist()
        sections = sections_df['section_id'].tolist()

        schedule_vars = {}
        for _, row in train_sections_df.iterrows():
            var_name = f"start_{row['train_id']}_{row['section_id']}"
            schedule_vars[(row['train_id'], row['section_id'])] = pulp.LpVariable(var_name, lowBound=0)

        total_delay_vars = []
        for (train_id, section_id), var in schedule_vars.items():
            scheduled_str = train_sections_df[
                (train_sections_df['train_id'] == train_id) &
                (train_sections_df['section_id'] == section_id)
            ]['scheduled_entry_time'].values[0]
            scheduled_time = self._time_to_minutes(scheduled_str)

            delay_var = pulp.LpVariable(f"delay_{train_id}_{section_id}", lowBound=0)
            model += delay_var >= var - scheduled_time
            model += delay_var >= 0
            total_delay_vars.append(delay_var)

        model += pulp.lpSum(total_delay_vars), "Minimize_Total_Delay"

        M = 1e5

        # Conflict constraints: no two trains on same section at the same time
        for section in sections:
            trains_on_section = train_sections_df[train_sections_df['section_id'] == section]['train_id'].unique()
            for i in range(len(trains_on_section)):
                for j in range(i+1, len(trains_on_section)):
                    t1, t2 = trains_on_section[i], trains_on_section[j]
                    s1 = schedule_vars[(t1, section)]
                    s2 = schedule_vars[(t2, section)]
                    b = pulp.LpVariable(f"order_{t1}_{t2}_{section}", cat='Binary')
                    model += s1 + self.max_block_time <= s2 + M * (1 - b)
                    model += s2 + self.max_block_time <= s1 + M * b

        # Junction constraints example
        junction_sections = sections_df[sections_df['junction_flag'] == 1]['section_id'].tolist()
        for junction in junction_sections:
            trains_on_junction = train_sections_df[train_sections_df['section_id'] == junction]['train_id'].unique()
            for i in range(len(trains_on_junction)):
                for j in range(i+1, len(trains_on_junction)):
                    t1, t2 = trains_on_junction[i], trains_on_junction[j]
                    s1 = schedule_vars[(t1, junction)]
                    s2 = schedule_vars[(t2, junction)]
                    b = pulp.LpVariable(f"junction_order_{t1}_{t2}_{junction}", cat='Binary')
                    model += s1 + self.max_block_time <= s2 + M * (1 - b)
                    model += s2 + self.max_block_time <= s1 + M * b

        # Enforce train priorities (higher priority trains depart earlier)
        priority_map = {tid: self._get_priority_score(trains_df, tid) for tid in trains}
        for section in sections:
            trains_on_section = train_sections_df[train_sections_df['section_id'] == section]['train_id'].unique()
            for t1 in trains_on_section:
                for t2 in trains_on_section:
                    if t1 == t2:
                        continue
                    if priority_map.get(t1, 5.0) < priority_map.get(t2, 5.0):
                        s1 = schedule_vars[(t1, section)]
                        s2 = schedule_vars[(t2, section)]
                        model += s1 <= s2

        solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=self.time_limit)
        status = model.solve(solver)

        if status != pulp.LpStatusOptimal:
            print("No optimal solution found within time limit.")
            return None

        schedule = {}
        for (train_id, section_id), var in schedule_vars.items():
            start_time = pulp.value(var)
            schedule.setdefault(train_id, []).append({
                'section_id': section_id,
                'start_time': start_time
            })

        return schedule

    def _get_priority_score(self, trains_df, train_id):
        train_row = trains_df[trains_df['train_id'] == train_id]
        if not train_row.empty:
            return float(train_row['priority'].values[0])
        return 5.0  # default priority
