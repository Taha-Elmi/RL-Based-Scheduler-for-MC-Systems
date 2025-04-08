import numpy as np


class TDLearningAgent:
    def __init__(self, min_diff, max_diff, step=0.1, learning_rate=0.1, discount_factor=0):
        self.min_diff = min_diff
        self.max_diff = max_diff
        self.step = step
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        # Generate states based on the difference from the basic WCET
        self.states = [round(x, 1) for x in np.arange(min_diff, max_diff + step, step)]
        self.values = {s: 0.0 for s in self.states}

        # Define actions (-0.1, 0, 0.1) with constraints on first and last state
        self.actions = {state: [-step, 0, step] for state in self.states}
        self.actions[min_diff] = [0, step]  # First state: No decrease
        self.actions[max_diff] = [-step, 0]  # Last state: No increase

        # Store the last state and action until the reward comes out
        self.last_state = None
        self.last_action = 0

    def calculate_reward(self, jobs):
        from models import CriticalityLevel
        (len([j for j in jobs if j.task.criticality_level == CriticalityLevel.LOW and j.is_done]) /
         len([j for j in jobs if j.task.criticality_level == CriticalityLevel.LOW]) if jobs else 0)

    def select_action(self, state, epsilon=0.1):
        """ Choose action using an epsilon-greedy policy. """
        if np.random.rand() < epsilon:
            return np.random.choice(self.actions[state])
        return max(self.actions[state], key=lambda a: self.values[round(state + a, 1)])

    def update_values(self, state, reward):
        """ Update values using the TD-learning update rule. """
        self.values[state] += self.learning_rate * (reward - self.values[state])
