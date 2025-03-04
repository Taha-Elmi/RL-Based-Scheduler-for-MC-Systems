import enum
import random
from math import lcm
from rl_agent import RLAgent
import numpy as np


class CriticalityLevel(enum.Enum):
    HIGH = enum.auto()
    LOW = enum.auto()


class System:
    _instance = None

    def __init__(self):
        self.rl_agent = None
        self.tasks = []
        self.jobs = []
        self.ready_queue = []
        self.criticality_level = CriticalityLevel.LOW
        self.utilization = {}
        self.vdf = 0
        self.n_mode_change = 0
        self.n_dropped_jobs = 0
        self.hyper_period = 0
        self.time = 0

    def add_task(self, task):
        self.tasks.append(task)
        self.hyper_period = lcm(*[task.period for task in self.tasks])
        self.rl_agent = RLAgent(len(self.tasks))

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

    def release_job(self, task):
        new_job = Job(task)
        task.number_of_jobs += 1
        self.jobs.append(new_job)
        self.ready_queue.append(new_job)
        print(f'a job from task {task.id} has been released')

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

    def check_high_criticality_conditions(self):
        for job in self.ready_queue:
            if job.task.criticality_level == CriticalityLevel.HIGH and job.execution_time > job.task.wcet[self.criticality_level]:
                return True
        return False

    def switch_mode_to_high(self):
        self.criticality_level = CriticalityLevel.HIGH
        for job in self.ready_queue[:]:
            if job.task.criticality_level == CriticalityLevel.LOW:
                print(f'a job from task {job.task.id} has been dropped.')
                self.ready_queue.remove(job)
                self.n_dropped_jobs += 1
        self.n_mode_change += 1

    def update_wcet_with_rl(self):
        state = self.calculate_qos_state()
        state_idx = np.digitize(state, self.rl_agent.states) - 1
        action = self.rl_agent.select_action(state_idx)

        if action == "increase":
            for task in self.tasks:
                if task.criticality_level == CriticalityLevel.HIGH:
                    task.adaptive_wcet = min(task.adaptive_wcet * 1.1, task.wcet[CriticalityLevel.HIGH])

        elif action == "decrease":
            for task in self.tasks:
                if task.criticality_level == CriticalityLevel.HIGH:
                    task.adaptive_wcet = max(task.adaptive_wcet * 0.9, task.wcet[CriticalityLevel.LOW])

        reward = self.compute_reward()
        next_state_idx = np.digitize(self.calculate_qos_state(), self.rl_agent.states) - 1
        self.rl_agent.update_q_table(state_idx, self.rl_agent.actions.index(action), reward, next_state_idx)

    def calculate_qos_state(self):
        # Define QoS as the ratio of scheduled LC tasks to max possible LC tasks
        scheduled_lc_tasks = sum(1 for job in self.jobs if job.task.criticality_level == CriticalityLevel.LOW)
        max_lc_tasks = len([t for t in self.tasks if t.criticality_level == CriticalityLevel.LOW])
        return scheduled_lc_tasks / max_lc_tasks if max_lc_tasks > 0 else 1.0

    def compute_reward(self):
        # Reward function based on mode switches and QoS
        mode_switch_penalty = -10 if self.criticality_level == CriticalityLevel.HIGH else 0
        qos_reward = self.calculate_qos_state() * 10
        return qos_reward + mode_switch_penalty

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
        low_wcet = self.task.wcet[CriticalityLevel.LOW]
        high_wcet = self.task.wcet[CriticalityLevel.HIGH]

        if random.random() < 0.8:
            base_execution_time = random.uniform(low_wcet * 0.8, low_wcet)
        else:
            base_execution_time = random.uniform(low_wcet, high_wcet)

        return base_execution_time * Job.execution_time_coefficient

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
