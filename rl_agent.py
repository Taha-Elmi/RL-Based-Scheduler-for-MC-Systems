import numpy as np
import random


class RLAgent:
    def __init__(self, num_tasks):
        self.states = np.linspace(0.1, 1.0, num=10)  # QoS states
        self.actions = ["increase", "decrease", "stable"]  # Modify C_LO
        self.q_table = np.zeros((len(self.states), len(self.actions)))
        self.learning_rate = 0.5
        self.discount_factor = 0.9
        self.epsilon = 0.01  # Exploration-exploitation balance

    def select_action(self, state_index):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        return self.actions[np.argmax(self.q_table[state_index])]

    def update_q_table(self, state_idx, action_idx, reward, next_state_idx):
        current_q = self.q_table[state_idx, action_idx]
        max_future_q = np.max(self.q_table[next_state_idx])
        self.q_table[state_idx, action_idx] = current_q + self.learning_rate * (
            reward + self.discount_factor * max_future_q - current_q
        )
