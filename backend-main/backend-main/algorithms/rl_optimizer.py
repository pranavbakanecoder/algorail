import pandas as pd
import random

class TrainEnv:
    def __init__(self, trains_df, train_sections_df):
        self.trains = trains_df['train_id'].tolist()
        self.sections = train_sections_df['section_id'].unique().tolist()
        self.state = self.reset()

    def reset(self):
        self.unassigned_trains = set(self.trains)
        self.schedule = []
        return tuple(self.unassigned_trains)

    def step(self, train_id):
        self.unassigned_trains.remove(train_id)
        self.schedule.append(train_id)
        reward = -len(self.schedule)  # Negative reward to encourage shorter schedule
        done = len(self.unassigned_trains) == 0
        return tuple(self.unassigned_trains), reward, done

class RLAgent:
    def __init__(self, trains_df, train_sections_df, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.env = TrainEnv(trains_df, train_sections_df)
        self.q_table = dict()  # state: {action: q-value}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        actions = list(state)
        if random.random() < self.epsilon or state not in self.q_table:
            return random.choice(actions)
        return max(self.q_table[state], key=self.q_table[state].get)

    def update_q(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in state}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0 for a in next_state}
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values()) if next_state else 0
        self.q_table[state][action] = old_value + self.alpha * (reward + self.gamma * next_max - old_value)

    def train(self, episodes=100):
        best_schedule = []
        best_score = float('inf')
        for ep in range(episodes):
            state = self.env.reset()
            total_reward = 0
            while True:
                action = self.choose_action(state)
                next_state, reward, done = self.env.step(action)
                self.update_q(state, action, reward, next_state)
                state = next_state
                total_reward += reward
                if done:
                    break
            if total_reward < best_score:
                best_score = total_reward
                best_schedule = list(self.env.schedule)
        return best_schedule, best_score

def run_rl_optimizer(trains_df, sections_df, train_sections_df):
    agent = RLAgent(trains_df, train_sections_df)
    schedule, score = agent.train(episodes=100)
    return schedule, score
