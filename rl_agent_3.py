import numpy as np


class WCET_AdaptiveAgent:
    def __init__(self, min_diff=-0.2, max_diff=1.0, step=0.1, learning_rate=0.1, discount_factor=0.9):
        self.min_diff = min_diff
        self.max_diff = max_diff
        self.step = step
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

        # Generate states based on the difference from the basic WCET
        self.states = [round(x, 1) for x in np.arange(min_diff, max_diff + step, step)]

        # Define actions (-0.1, 0, 0.1) with constraints on first and last state
        self.actions = {state: [-step, 0, step] for state in self.states}
        self.actions[min_diff] = [0, step]  # First state: No decrease
        self.actions[max_diff] = [-step, 0]  # Last state: No increase

        # Initialize Q-table
        self.q_table = {(state, action): 0.0 for state in self.states for action in self.actions[state]}

    def select_action(self, state, epsilon=0.1):
        """ Choose action using an epsilon-greedy policy. """
        if np.random.rand() < epsilon:
            return np.random.choice(self.actions[state])
        return max(self.actions[state], key=lambda a: self.q_table[(state, a)])

    def update_q_table(self, state, action, reward):
        """ Update the Q-table using the Q-learning update rule. """
        next_state = round(state + action, 1)
        next_state = min(max(next_state, self.min_diff), self.max_diff)  # Ensure within bounds

        current_q = self.q_table[(state, action)]
        max_next_q = max([self.q_table[(next_state, a)] for a in self.actions[next_state]])

        self.q_table[(state, action)] = current_q + self.learning_rate * (
                    reward + self.discount_factor * max_next_q - current_q)
