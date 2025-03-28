import enum
import random
from math import lcm
from rl_agent_3 import WCET_AdaptiveAgent


class CriticalityLevel(enum.Enum):
    HIGH = enum.auto()
    LOW = enum.auto()


class System:
    _instance = None

    def __init__(self):
        self.tasks = []
        self.jobs = []
        self.ready_queue = []
        self.criticality_level = CriticalityLevel.LOW
        self.utilization = {}
        self.vdf = 0
        self.n_mode_change = 0
        self.n_dropped_jobs = 0
        self.mode_change_history = []
        self.dropped_jobs_history = []
        self.time_history = []
        self.hyper_period = 0
        self.time = 0

        self.dropped_jobs_percentage_history = []
        self.hyper_period_history = []

        self.rl_agent = WCET_AdaptiveAgent(min_diff=-0.2, max_diff=1.0, step=0.1)

    def add_task(self, task):
        self.tasks.append(task)
        self.hyper_period = lcm(*[task.period for task in self.tasks])
        # self.rl_agent = RLAgent(len(self.tasks))

    def calculate_utilization(self):
        for task_criticality_level in CriticalityLevel:
            for system_criticality_level in CriticalityLevel:
                if system_criticality_level == CriticalityLevel.HIGH and task_criticality_level == CriticalityLevel.LOW:
                    continue
                u = 0
                for task in self.tasks:
                    if task.criticality_level == task_criticality_level:
                        u += task.wcet[system_criticality_level] / task.period
                self.utilization[(task_criticality_level, system_criticality_level)] = u

    def update_vdf(self):
        self.vdf = (self.utilization[(CriticalityLevel.HIGH, CriticalityLevel.LOW)] /
                    (1 - self.utilization[(CriticalityLevel.LOW, CriticalityLevel.LOW)]))

    def setup(self):
        self.jobs.clear()
        self.calculate_utilization()
        self.update_vdf()

    def release_job(self, task):
        new_job = Job(task)
        task.number_of_jobs += 1
        self.jobs.append(new_job)
        self.ready_queue.append(new_job)
        # print(f'a job from task {task.id} has been released')

    def schedule(self):
        def deadline_and_criticality_sort_function(j1: Job, j2: Job) -> int:
            a = j1.get_deadline()
            b = j2.get_deadline()
            if a < b:
                return -1
            elif a == b:
                if j1.task.criticality_level == j2.task.criticality_level:
                    return 0
                if j1.task.criticality_level == CriticalityLevel.HIGH:
                    return -1
                return 1
            else:
                return 1

        from functools import cmp_to_key
        self.ready_queue.sort(key=cmp_to_key(deadline_and_criticality_sort_function))

    def check_expired_jobs(self):
        for job in self.ready_queue:
            if job.get_deadline() <= self.time:
                self.ready_queue.remove(job)
                self.n_dropped_jobs += 1
                # print(f'a jon from task {job.task.id} has been dropped.')

    def generate_new_jobs(self):
        for task in self.tasks:
            if self.time % task.period == 0:
                if self.criticality_level == CriticalityLevel.LOW or task.criticality_level == CriticalityLevel.HIGH:
                    self.release_job(task)
                else:
                    self.n_dropped_jobs += 1

    def step(self):
        if self.criticality_level == CriticalityLevel.HIGH and self.check_low_criticality_conditions():
            self.switch_mode_to_low()

        self.check_expired_jobs()

        if self.time % self.hyper_period == 0:
            self.update_graph()
            # self.update_wcet_with_rl()
            self.setup()

        self.generate_new_jobs()

        self.schedule()

        if len(self.ready_queue) > 0:
            self.ready_queue[0].execute()

        if self.criticality_level == CriticalityLevel.LOW and self.check_high_criticality_conditions():
            self.switch_mode_to_high()

        self.time += 1

    def check_low_criticality_conditions(self):
        for job in self.ready_queue:
            if job.task.criticality_level == CriticalityLevel.HIGH:
                return False
        return True

    def switch_mode_to_low(self):
        self.criticality_level = CriticalityLevel.LOW
        # print(f'system has switched to {self.criticality_level}')

    def check_high_criticality_conditions(self):
        for job in self.ready_queue:
            if job.task.criticality_level == CriticalityLevel.HIGH and job.execution_time > job.task.wcet[self.criticality_level]:
                return True
        return False

    def switch_mode_to_high(self):
        self.criticality_level = CriticalityLevel.HIGH
        for job in self.ready_queue[:]:
            if job.task.criticality_level == CriticalityLevel.LOW:
                # print(f'a job from task {job.task.id} has been dropped.')
                self.ready_queue.remove(job)
                self.n_dropped_jobs += 1
        self.n_mode_change += 1
        # print(f'system has switched to {self.criticality_level}')

    def update_graph(self):
        """Update the graph data for real-time plotting."""
        # self.mode_change_history.append(self.n_mode_change)
        # self.dropped_jobs_history.append(self.n_dropped_jobs / len(self.jobs))
        # self.time_history = list(range(len(self.dropped_jobs_history)))

        total_jobs = len(self.jobs)
        drop_percentage = (self.n_dropped_jobs / total_jobs) * 100 if total_jobs > 0 else 0
        self.dropped_jobs_percentage_history.append(drop_percentage)
        self.hyper_period_history.append(len(self.hyper_period_history))

        self.n_mode_change = 0
        self.n_dropped_jobs = 0

    def update_wcet_with_rl(self):
        if self.rl_agent.last_state is None:
            self.rl_agent.last_state = 0.0
            return

        reward = (len([j for j in self.jobs if j.task.criticality_level == CriticalityLevel.LOW and j.is_done]) /
                  len([j for j in self.jobs if j.task.criticality_level == CriticalityLevel.LOW]) if self.jobs else 0)

        # print(f'state: {self.rl_agent.last_state}')
        # print(f'action: {self.rl_agent.last_action}')
        # print(f'reward: {reward}')
        # print(f'new_state: {new_state}')
        # print('q_table:')
        # for k, v in self.rl_agent.q_table.items():
        #     print(f'{k}: {v}')
        # input('--------------------------------------------------------------')

        self.rl_agent.update_q_table(self.rl_agent.last_state, self.rl_agent.last_action, reward)

        new_state = self.rl_agent.last_state + self.rl_agent.last_action
        action = self.rl_agent.select_action(new_state)

        for task in self.tasks:
            if task.criticality_level == CriticalityLevel.HIGH:
                task.wcet[CriticalityLevel.LOW] += action

        self.rl_agent.last_state = new_state
        self.rl_agent.last_action = action

    @staticmethod
    def get_instance():
        if System._instance is None:
            System._instance = System()
        return System._instance


class Task:
    counter = 1

    def __init__(self, id, period, low_wcet, high_wcet, criticality_level):
        # self.id = Task.counter
        self.id = id
        self.period = period
        self.wcet = {CriticalityLevel.LOW: low_wcet, CriticalityLevel.HIGH: high_wcet}
        self.basic_low_wcet = low_wcet
        self.aet = 0
        self.number_of_jobs = 0
        self.criticality_level = criticality_level

        Task.counter += 1


class Job:
    execution_time_coefficient = 1.0

    def __init__(self, task: Task):
        self.task = task
        self.release_time = System.get_instance().time
        self.execution_time = 0
        self.is_done = False

    def generate_random_execution_time(self):
        low_wcet = self.task.basic_low_wcet
        high_wcet = self.task.wcet[CriticalityLevel.HIGH]

        if random.random() < 0.9:
            base_execution_time = random.uniform(low_wcet * 0.8, low_wcet)
        else:
            base_execution_time = min(random.uniform(low_wcet, low_wcet * 1.1), high_wcet)

        return base_execution_time + Job.execution_time_coefficient

    def get_deadline(self):
        if System.get_instance().criticality_level == CriticalityLevel.HIGH or self.task.criticality_level == CriticalityLevel.LOW:
            return self.release_time + self.task.period
        else:
            return self.release_time + (System.get_instance().vdf * self.task.period)

    def execute(self):
        self.execution_time += 1
        if self.execution_time > self.generate_random_execution_time():
            self.is_done = True
            System.get_instance().ready_queue.remove(self)

    def __repr__(self):
        return f'[task_id: {self.task.id}, deadline: {self.get_deadline()}, wcet: {self.task.wcet}, execution_time: {self.execution_time}]\n'


class QLearningAgent:
    def __init__(self, alpha=0.5, gamma=0, epsilon=0.1):
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = {}  # Q-values for state-action pairs
        self.actions = [-1, 0, 1]  # Decrease, Do Nothing, Increase WCET
        self.last_state = None
        self.last_action = 0

    def get_state(self, jobs):
        low_critical_jobs = [j for j in jobs if j.task.criticality_level == CriticalityLevel.LOW]
        if len(low_critical_jobs) == 0:
            return 0.0
        return round(len([j for j in low_critical_jobs if j.is_done]) / len(low_critical_jobs), 2)

    def choose_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in self.actions}

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)

        max_q = max(self.q_table[state].values())
        best_actions = [a for a, q in self.q_table[state].items() if q == max_q]

        if 0 in best_actions:
            return 0  # Prioritize "do nothing" if tied
        return random.choice(best_actions)

    def update_q(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in self.actions}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0 for a in self.actions}

        max_next_q = max(self.q_table[next_state].values())
        self.q_table[state][action] += self.alpha * (reward + self.gamma * max_next_q - self.q_table[state][action])
